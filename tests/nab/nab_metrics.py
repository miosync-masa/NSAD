"""
NAB 公式 Sweeper を用いた scoring wrapper。

NAB の `nab.sweeper.Sweeper` をオプティマイザとして使い、
detector の anomaly_score 列を 3 profile (standard / low FP / low FN) で評価する。

normalization:
    score_normalized = 100 * (best_raw - null_baseline) / (perfect - null_baseline)
    null_baseline = threshold=1.1 (=何も検出しない) 時の Sweeper score
    perfect       = #windows * tpWeight

Usage::
    from tests.nab.nab_metrics import score_all_profiles
    scores = score_all_profiles(sample, anomaly_scores)
    # scores = {'standard': NABScore, 'reward_low_FP_rate': ..., 'reward_low_FN_rate': ...}
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List

import numpy as np

# NAB をパッケージ root の ./NAB に置く想定 (tests/ から見ると ../NAB)
_NAB_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'NAB')
)
if _NAB_ROOT not in sys.path:
    sys.path.insert(0, _NAB_ROOT)

from nab.sweeper import Sweeper  # noqa: E402

_PROFILES_PATH = os.path.join(_NAB_ROOT, 'config', 'profiles.json')
_PROFILES_CACHE: Dict[str, Dict] = {}


def load_profiles() -> Dict[str, Dict]:
    if not _PROFILES_CACHE:
        with open(_PROFILES_PATH) as f:
            _PROFILES_CACHE.update(json.load(f))
    return _PROFILES_CACHE


@dataclass
class NABScore:
    profile: str
    best_threshold: float
    best_raw: float
    null_baseline: float
    perfect: float
    normalized: float        # 0=null detector, 100=perfect detector
    tp: int
    fp: int
    fn: int
    n_windows: int


def _normalize_to_unit(scores: np.ndarray) -> np.ndarray:
    s = np.asarray(scores, dtype=np.float64)
    finite = np.isfinite(s)
    if not finite.any():
        return np.zeros_like(s)
    lo, hi = float(np.min(s[finite])), float(np.max(s[finite]))
    if hi - lo < 1e-12:
        return np.zeros_like(s)
    out = np.where(finite, (s - lo) / (hi - lo), 0.0)
    return np.clip(out, 0.0, 1.0)


def score_with_sweeper(sample, anomaly_scores: np.ndarray,
                       profile_name: str = 'standard') -> NABScore:
    """1 file × 1 profile のスコア。

    Args:
        sample: NABSample (timestamps / windows_ts / name を参照)
        anomaly_scores: (n,) float. NaN は 0 に置換。range は自動で [0,1] に min-max。
        profile_name: 'standard' | 'reward_low_FP_rate' | 'reward_low_FN_rate'
    """
    profiles = load_profiles()
    cost = profiles[profile_name]['CostMatrix']
    sweeper = Sweeper(probationPercent=0.15, costMatrix=cost)

    scores01 = _normalize_to_unit(anomaly_scores)

    timestamps = sample.timestamps
    window_limits = [(s, e) for s, e in sample.windows_ts]

    anomaly_list = sweeper.calcSweepScore(
        timestamps, scores01.tolist(), window_limits, sample.name
    )
    threshold_scores = sweeper.calcScoreByThreshold(anomaly_list)
    # 最初の entry が threshold=1.1 (null baseline, 全 FN)
    null = threshold_scores[0]
    best = max(threshold_scores, key=lambda r: r.score)

    n_windows = len(sample.windows_ts)
    perfect = n_windows * cost['tpWeight']
    if perfect - null.score > 1e-12:
        normalized = 100.0 * (best.score - null.score) / (perfect - null.score)
    else:
        normalized = 0.0

    return NABScore(
        profile=profile_name,
        best_threshold=float(best.threshold),
        best_raw=float(best.score),
        null_baseline=float(null.score),
        perfect=float(perfect),
        normalized=float(normalized),
        tp=int(best.tp), fp=int(best.fp), fn=int(best.fn),
        n_windows=n_windows,
    )


def score_all_profiles(sample, anomaly_scores: np.ndarray
                       ) -> Dict[str, NABScore]:
    return {
        name: score_with_sweeper(sample, anomaly_scores, profile_name=name)
        for name in load_profiles().keys()
    }


def format_nab_score(s: NABScore, label: str = '') -> str:
    return (f"    {label:<24}  {s.profile:<22}  "
            f"raw={s.best_raw:+8.3f}  norm={s.normalized:+7.2f}  "
            f"thr={s.best_threshold:.3f}  TP={s.tp:3d} FP={s.fp:4d} FN={s.fn:3d}")


# ---------------------------------------------------------------------------
# Corpus-level (official-NAB-style) scoring
#
# score_with_sweeper() は「ファイルごとに最適閾値」を選ぶ。これは official NAB
# の手続き (コーパス全体で単一閾値を最適化し、その固定閾値で全ファイルを採点)
# と異なり、全手法のスコアを上振れさせる。published number との比較には
# corpus-level の単一閾値が必要。以下はその実装。
#
#   Total(θ) = Σ_f S_f(θ)   (S_f = Sweeper の per-file raw score、閾値 θ 共通)
#   θ*       = argmax_θ Total(θ)
#   norm     = 100 * (Total(θ*) - Σ null_f) / (Σ perfect_f - Σ null_f)
#
# per-file min-max 正規化 ([0,1] スケール) は score_with_sweeper と同一。
# 変更点は「閾値最適化の単位」のみ。
# ---------------------------------------------------------------------------


@dataclass
class ThresholdCurve:
    """1 file × 1 profile の threshold → score step 関数。"""
    name: str
    thresholds: np.ndarray   # ascending, 最後は 1.1 (null)
    scores: np.ndarray
    tp: np.ndarray
    fp: np.ndarray
    fn: np.ndarray
    null: float              # θ=1.1 (何も flag しない) の score
    perfect: float           # n_windows * tpWeight

    def at(self, theta: np.ndarray):
        """S_f(θ): θ 以上で最小の候補閾値の score (= flag set が一致)。"""
        idx = np.searchsorted(self.thresholds, theta, side='left')
        idx = np.clip(idx, 0, len(self.thresholds) - 1)
        return idx


@dataclass
class CorpusScore:
    profile: str
    best_threshold: float
    best_raw_total: float
    null_total: float
    perfect_total: float
    normalized: float
    tp: int
    fp: int
    fn: int
    n_files: int
    per_file_normalized: Dict[str, float]   # 各 file の θ* 固定時 normalized
                                            # (windowless file は含まない)


def sweep_threshold_curve(sample, anomaly_scores: np.ndarray,
                          profile_name: str = 'standard',
                          normalize: bool = True) -> ThresholdCurve:
    """1 file の threshold sweep curve (corpus-level 集計の材料)。

    Args:
        normalize: True で per-file min-max ([0,1])。False は呼び出し側が
            file 横断で比較可能な [0,1] スコア (anchored transform 等) を
            渡す場合 — per-file 情報を一切使わない大域単調変換。
    """
    profiles = load_profiles()
    cost = profiles[profile_name]['CostMatrix']
    sweeper = Sweeper(probationPercent=0.15, costMatrix=cost)

    if normalize:
        scores01 = _normalize_to_unit(anomaly_scores)
    else:
        scores01 = np.clip(
            np.nan_to_num(np.asarray(anomaly_scores, dtype=np.float64),
                          nan=0.0, posinf=1.0, neginf=0.0),
            0.0, 1.0,
        )
    anomaly_list = sweeper.calcSweepScore(
        sample.timestamps, scores01.tolist(),
        [(s, e) for s, e in sample.windows_ts], sample.name
    )
    threshold_scores = sweeper.calcScoreByThreshold(anomaly_list)

    thr = np.array([t.threshold for t in threshold_scores], dtype=np.float64)
    sc = np.array([t.score for t in threshold_scores], dtype=np.float64)
    tp = np.array([t.tp for t in threshold_scores], dtype=np.int64)
    fp = np.array([t.fp for t in threshold_scores], dtype=np.int64)
    fn = np.array([t.fn for t in threshold_scores], dtype=np.int64)

    order = np.argsort(thr)
    thr, sc, tp, fp, fn = thr[order], sc[order], tp[order], fp[order], fn[order]

    null = float(sc[-1])   # threshold=1.1 (max) = 何も flag しない
    perfect = len(sample.windows_ts) * cost['tpWeight']

    return ThresholdCurve(
        name=sample.name, thresholds=thr, scores=sc,
        tp=tp, fp=fp, fn=fn, null=null, perfect=float(perfect),
    )


def corpus_score(curves: List[ThresholdCurve],
                 profile_name: str = 'standard',
                 max_candidates: int = 200_000) -> CorpusScore:
    """全 file 共通の単一閾値 θ* で採点 (official NAB 方式)。

    候補 θ は全 curve の閾値の和集合。組合せ爆発防止に max_candidates で
    等間隔 subsample (curve は step 関数なので順位の粗い量子化にしかならない)。
    """
    union = np.unique(np.concatenate([c.thresholds for c in curves]))
    if len(union) > max_candidates:
        keep = np.linspace(0, len(union) - 1, max_candidates).astype(np.int64)
        union = np.unique(np.concatenate([union[keep], [1.1]]))

    total = np.zeros(len(union), dtype=np.float64)
    tp_t = np.zeros(len(union), dtype=np.int64)
    fp_t = np.zeros(len(union), dtype=np.int64)
    fn_t = np.zeros(len(union), dtype=np.int64)
    for c in curves:
        idx = c.at(union)
        total += c.scores[idx]
        tp_t += c.tp[idx]
        fp_t += c.fp[idx]
        fn_t += c.fn[idx]

    best_i = int(np.argmax(total))
    theta = float(union[best_i])
    null_total = float(sum(c.null for c in curves))
    perfect_total = float(sum(c.perfect for c in curves))
    if perfect_total - null_total > 1e-12:
        normalized = 100.0 * (total[best_i] - null_total) / (
            perfect_total - null_total)
    else:
        normalized = 0.0

    per_file: Dict[str, float] = {}
    theta_arr = np.array([theta])
    for c in curves:
        if c.perfect - c.null <= 1e-12:
            continue   # windowless file: per-file normalization undefined
        s_at = float(c.scores[c.at(theta_arr)[0]])
        per_file[c.name] = 100.0 * (s_at - c.null) / (c.perfect - c.null)

    return CorpusScore(
        profile=profile_name,
        best_threshold=theta,
        best_raw_total=float(total[best_i]),
        null_total=null_total,
        perfect_total=perfect_total,
        normalized=float(normalized),
        tp=int(tp_t[best_i]), fp=int(fp_t[best_i]), fn=int(fn_t[best_i]),
        n_files=len(curves),
        per_file_normalized=per_file,
    )


def corpus_score_at(curves: List[ThresholdCurve], theta: float,
                    profile_name: str = 'standard') -> CorpusScore:
    """固定の単一閾値 θ で採点 (閾値最適化なし)。

    detector の native operating point (例: Lambda³ の anchored 0.5 =
    ratio 1.0 = 実運用の binary 判定そのもの) を corpus-level で評価する。
    """
    theta_arr = np.array([theta])
    total = 0.0
    tp = fp = fn = 0
    per_file: Dict[str, float] = {}
    for c in curves:
        i = int(c.at(theta_arr)[0])
        total += float(c.scores[i])
        tp += int(c.tp[i])
        fp += int(c.fp[i])
        fn += int(c.fn[i])
        if c.perfect - c.null > 1e-12:
            per_file[c.name] = 100.0 * (float(c.scores[i]) - c.null) / (
                c.perfect - c.null)
    null_total = float(sum(c.null for c in curves))
    perfect_total = float(sum(c.perfect for c in curves))
    if perfect_total - null_total > 1e-12:
        normalized = 100.0 * (total - null_total) / (perfect_total - null_total)
    else:
        normalized = 0.0
    return CorpusScore(
        profile=profile_name,
        best_threshold=float(theta),
        best_raw_total=float(total),
        null_total=null_total,
        perfect_total=perfect_total,
        normalized=float(normalized),
        tp=tp, fp=fp, fn=fn,
        n_files=len(curves),
        per_file_normalized=per_file,
    )
