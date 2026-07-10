"""
NAB corpus-level re-evaluation — single global threshold (official-NAB style).

Motivation (doc/paper/abstract.md "Known review risks"):
  The per-file harness (tests/nab/nab_metrics.score_with_sweeper) picks the best
  threshold PER FILE. Official NAB optimizes ONE threshold over the whole
  corpus per detector/profile. Per-file optimization inflates every method's
  score and makes comparisons against published numbers protocol-mismatched.
  This script re-scores Lambda³ (Tier 0 / Tier 2) and the classical baselines
  under a corpus-level single threshold, from the same per-file anomaly-score
  arrays.

Design:
  Phase 1 (--compute): run detectors over the corpus, cache per-file anomaly
    score arrays to <cache-dir>/<method>.npz. Resumable (existing entries are
    skipped). Methods can be computed in parallel background jobs, one
    --methods subset each.
  Phase 2 (--aggregate): load caches, build per-file threshold curves, and
    report per profile:
      - corpus-level normalized score (single θ*)
      - per-file-optimal score (existing protocol) for reference
    with per-category breakdown at the fixed θ*.

  Windowless files (e.g. artificialNoAnomaly) are ALWAYS computed into the
  cache; --include-empty controls whether aggregation includes them (official
  NAB does: they contribute FP penalties only).

Methods:
  lambda3_tier0      Lambda³-S streaming (calibration 15%, 6 scorers)
  lambda3_tier2      Lambda³-R regime-aware (K=auto, trimmed_percentile)
  {ocsvm,iforest,lof}_{streaming,exclusion}   classical baselines
                     (same configs as tests/nab/benchmark_nab_baselines)

On detector failure for a file (e.g. clean-data-too-small), the method
falls back to an all-zero score array for that file (= null detector),
and the fallback is reported. Disclosed rather than skipped, so every
method is scored on the identical file set.

Usage::
    python -m tests.nab.benchmark_nab_corpus --compute --methods lambda3_tier2
    python -m tests.nab.benchmark_nab_corpus --compute --methods baselines
    python -m tests.nab.benchmark_nab_corpus --aggregate
    python -m tests.nab.benchmark_nab_corpus --aggregate --include-empty
"""

from __future__ import annotations

import argparse
import os
import time
from typing import Dict, List, Optional

import numpy as np

from tests.nab.nab_datasets import iter_category
from tests.nab.nab_features import expand_to_5d
from tests.nab.nab_metrics import (
    corpus_score,
    corpus_score_at,
    score_all_profiles,
    load_profiles,
    sweep_threshold_curve,
)

CATEGORIES = [
    'realKnownCause', 'realAWSCloudwatch', 'realTraffic',
    'realAdExchange', 'artificialWithAnomaly', 'realTweets',
]
EMPTY_CATEGORIES = ['artificialNoAnomaly']

LAMBDA3_METHODS = [
    'lambda3_tier0', 'lambda3_tier2', 'lambda3_tier2_gated',
    'lambda3_tier2_cal', 'lambda3_tier2_cal_gated',
]
BASELINE_METHODS = [
    'ocsvm_streaming', 'ocsvm_exclusion',
    'iforest_streaming', 'iforest_exclusion',
    'lof_streaming', 'lof_exclusion',
]
ALL_METHODS = LAMBDA3_METHODS + BASELINE_METHODS

CACHE_DIR_DEFAULT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'nab_score_cache')
)

FEATURE_WINDOW = 30


def _key(name: str) -> str:
    return name.replace('/', '__')


def load_corpus(include_empty: bool = True) -> List:
    samples = []
    for cat in CATEGORIES:
        samples.extend(iter_category(cat))
    if include_empty:
        for cat in EMPTY_CATEGORIES:
            try:
                samples.extend(iter_category(cat, include_empty=True))
            except Exception as e:
                print(f"  (skip {cat}: {e})")
    return samples


def make_anomaly_mask(sample) -> np.ndarray:
    mask = np.zeros(sample.n, dtype=bool)
    for si, ei in sample.window_indices:
        mask[si:ei + 1] = True
    return mask


# --- per-method score computation -----------------------------------------

def score_lambda3_tier0(sample, X) -> np.ndarray:
    from tests.legacy.benchmark_nab_streaming import make_detector
    det = make_detector()
    return np.asarray(det.fit_predict(X)['score'], dtype=np.float64)


def score_lambda3_tier2(sample, X) -> np.ndarray:
    from lambda3_detector.regime import RegimeAwareDetector
    det = RegimeAwareDetector(K='auto')
    mask = make_anomaly_mask(sample)
    return np.asarray(det.fit_predict(X, mask)['score'], dtype=np.float64)


def score_lambda3_tier2_gated(sample, X) -> np.ndarray:
    """Tier 2 + unknown-regime gating (「分からないときは棄権する」)。

    unknown_mask=True の frame (GMM log-likelihood が clean 下限未満 =
    既知の正常レジームの外) では逸脱スコアを 0 に落とす。per-regime
    threshold は未知レジームでは正常モデルの外挿であり信頼できない、
    という三値 state 出力の意味論を alarm チャネルに適用したもの。
    人間による閾値チューニングもラベル使用も一切ない自己校正判定。
    """
    from lambda3_detector.regime import RegimeAwareDetector
    det = RegimeAwareDetector(K='auto')
    mask = make_anomaly_mask(sample)
    result = det.fit_predict(X, mask)
    score = np.asarray(result['score'], dtype=np.float64)
    unknown = np.asarray(result['unknown_mask'], dtype=bool)
    return np.where(unknown, 0.0, score)


def score_baseline(sample, X, detector_name: str, mode: str) -> np.ndarray:
    from lambda3_detector.regime import expand_anomaly_mask
    from tests.nab.benchmark_nab_baselines import (
        CALIBRATION_RATIO, MASK_MARGIN, _subsample,
        anomaly_score, make_detector,
    )
    n = len(X)
    if mode == 'streaming':
        train_idx = np.arange(max(int(n * CALIBRATION_RATIO), 20))
    else:
        expanded = expand_anomaly_mask(make_anomaly_mask(sample), MASK_MARGIN)
        train_idx = np.where(~expanded)[0]
        if len(train_idx) < 100:
            raise ValueError(f"clean data too small ({len(train_idx)})")
    mu = X[train_idx].mean(axis=0)
    sd = X[train_idx].std(axis=0) + 1e-10
    X_norm = (X - mu) / sd
    model = make_detector(detector_name)
    model.fit(_subsample(X_norm[train_idx], 5000))
    s = anomaly_score(model, X_norm)
    np.nan_to_num(s, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    return s


def compute_scores(sample, method: str) -> np.ndarray:
    X = expand_to_5d(sample.values, window=FEATURE_WINDOW)
    if method == 'lambda3_tier0':
        return score_lambda3_tier0(sample, X)
    if method == 'lambda3_tier2':
        return score_lambda3_tier2(sample, X)
    if method == 'lambda3_tier2_gated':
        return score_lambda3_tier2_gated(sample, X)
    if method in ('lambda3_tier2_cal', 'lambda3_tier2_cal_gated'):
        # combined-ratio calibration (OR 出力の再校正)。1 回の fit から
        # cal / cal+gated の両スコアを生成 (multi-output、両 cache に保存)
        from lambda3_detector.regime import RegimeAwareDetector
        det = RegimeAwareDetector(K='auto', calibrate_combined=True)
        result = det.fit_predict(X, make_anomaly_mask(sample))
        score = np.asarray(result['score'], dtype=np.float64)
        unknown = np.asarray(result['unknown_mask'], dtype=bool)
        return {
            'lambda3_tier2_cal': score,
            'lambda3_tier2_cal_gated': np.where(unknown, 0.0, score),
        }
    det, mode = method.rsplit('_', 1)
    return score_baseline(sample, X, det, mode)


# --- anchored transforms ----------------------------------------------------
#
# per-file min-max は各 file のスコア scale に依存する (=Lambda³ の
# 「ratio 1.0 = flag」の絶対アンカーを壊す)。anchored transform は per-file
# 情報を一切使わない大域単調写像で、file 横断比較可能な [0,1] スコアを作る:
#
#   lambda3   : r / (1 + r)          — ratio 1.0 (=フラグ境界) → 常に 0.5
#   baselines : sigmoid(a)           — a = -decision_function、
#                                      学習済み境界 (df=0) → 常に 0.5
#
# corpus-level 単一閾値の評価において、この「絶対アンカーの有無」は
# 手法間の本質的な差 (cross-file comparability) を露出させる。

def anchored_transform(method: str, scores: np.ndarray) -> np.ndarray:
    s = np.asarray(scores, dtype=np.float64)
    if method.startswith('lambda3'):
        s = np.maximum(s, 0.0)
        return s / (1.0 + s)
    # baselines: cache には anomaly_score = -decision_function が入っている
    return 1.0 / (1.0 + np.exp(-np.clip(s, -60.0, 60.0)))


# --- cache -----------------------------------------------------------------

def cache_path(cache_dir: str, method: str) -> str:
    return os.path.join(cache_dir, f"{method}.npz")


def load_cache(cache_dir: str, method: str) -> Dict[str, np.ndarray]:
    path = cache_path(cache_dir, method)
    if not os.path.exists(path):
        return {}
    with np.load(path) as z:
        return {k: z[k] for k in z.files}


def save_cache(cache_dir: str, method: str, data: Dict[str, np.ndarray]):
    os.makedirs(cache_dir, exist_ok=True)
    np.savez_compressed(cache_path(cache_dir, method), **data)


# --- phases ----------------------------------------------------------------

def phase_compute(methods: List[str], cache_dir: str):
    samples = load_corpus(include_empty=True)
    print(f"corpus: {len(samples)} files "
          f"({sum(1 for s in samples if s.windows_ts)} with windows)")
    for method in methods:
        cache = load_cache(cache_dir, method)
        todo = [s for s in samples if _key(s.name) not in cache]
        print(f"\n=== {method}: {len(cache)} cached, {len(todo)} to compute ===")
        fallbacks = []
        sibling_caches: Dict[str, Dict[str, np.ndarray]] = {}
        for i, sample in enumerate(todo):
            t0 = time.perf_counter()
            try:
                scores = compute_scores(sample, method)
            except Exception as e:
                print(f"  [{i+1}/{len(todo)}] {sample.name}: "
                      f"FALLBACK to null scores ({e})")
                scores = np.zeros(sample.n, dtype=np.float64)
                fallbacks.append(sample.name)
            else:
                print(f"  [{i+1}/{len(todo)}] {sample.name}  n={sample.n}  "
                      f"t={time.perf_counter()-t0:.1f}s")
            if isinstance(scores, dict):
                # multi-output method: 1 回の fit から複数 cache に保存
                for m2, arr in scores.items():
                    if m2 == method:
                        cache[_key(sample.name)] = arr
                    else:
                        sib = sibling_caches.setdefault(
                            m2, load_cache(cache_dir, m2))
                        sib[_key(sample.name)] = arr
                        save_cache(cache_dir, m2, sib)
            else:
                cache[_key(sample.name)] = scores
            save_cache(cache_dir, method, cache)   # incremental (resumable)
        if fallbacks:
            print(f"  {method}: {len(fallbacks)} null-fallback files: {fallbacks}")
        print(f"=== {method}: done ({len(cache)} files cached) ===")


def phase_aggregate(methods: List[str], cache_dir: str, include_empty: bool):
    samples = load_corpus(include_empty=include_empty)
    profiles = list(load_profiles().keys())
    windowed = [s for s in samples if s.windows_ts]

    print("=" * 110)
    print(f"CORPUS-LEVEL RE-EVALUATION  files={len(samples)} "
          f"(windowed={len(windowed)}, include_empty={include_empty})")
    print("  corpus  = ONE threshold per (method, profile), official-NAB style")
    print("  perfile = best threshold PER FILE (previous harness), for reference")
    print("=" * 110)

    rows = []
    for method in methods:
        cache = load_cache(cache_dir, method)
        missing = [s.name for s in samples if _key(s.name) not in cache]
        if missing:
            print(f"\n{method}: SKIP — {len(missing)} files not cached "
                  f"(run --compute first): {missing[:3]}...")
            continue

        corpus_mm: Dict[str, float] = {}      # per-file min-max + global θ
        corpus_an: Dict[str, float] = {}      # anchored transform + global θ
        perfile_norm: Dict[str, float] = {}   # per-file optimal (old harness)
        per_file_at_theta: Dict[str, Dict[str, float]] = {}
        for prof in profiles:
            curves_mm = [
                sweep_threshold_curve(s, cache[_key(s.name)], prof)
                for s in samples
            ]
            cs_mm = corpus_score(curves_mm, prof)
            curves_an = [
                sweep_threshold_curve(
                    s, anchored_transform(method, cache[_key(s.name)]),
                    prof, normalize=False)
                for s in samples
            ]
            cs_an = corpus_score(curves_an, prof)
            corpus_mm[prof] = cs_mm.normalized
            corpus_an[prof] = cs_an.normalized
            per_file_at_theta[prof] = cs_an.per_file_normalized
            if method.startswith('lambda3'):
                # native operating point: anchored 0.5 = ratio 1.0 =
                # 実運用の binary OR-voting 判定そのもの (閾値最適化なし)
                cs_nat = corpus_score_at(curves_an, 0.5, prof)
                print(f"  {method:<20} {prof:<22} "
                      f"native@ratio1.0={cs_nat.normalized:6.2f} "
                      f"(TP={cs_nat.tp} FP={cs_nat.fp} FN={cs_nat.fn})")
            # reference: per-file-optimal mean over windowed files
            pf = [
                score_all_profiles(s, cache[_key(s.name)])[prof].normalized
                for s in windowed
            ]
            perfile_norm[prof] = float(np.mean(pf))
            print(f"  {method:<20} {prof:<22} "
                  f"anchored={cs_an.normalized:6.2f} "
                  f"(θ*={cs_an.best_threshold:.3f} TP={cs_an.tp} "
                  f"FP={cs_an.fp} FN={cs_an.fn})   "
                  f"minmax={cs_mm.normalized:6.2f}   "
                  f"perfile={perfile_norm[prof]:6.2f}")

        a3 = float(np.mean(list(corpus_an.values())))
        m3 = float(np.mean(list(corpus_mm.values())))
        p3 = float(np.mean(list(perfile_norm.values())))
        rows.append((method, a3, m3, p3, per_file_at_theta))
        print(f"  {method:<20} {'3-profile mean':<22} anchored={a3:6.2f}   "
              f"minmax={m3:6.2f}   perfile={p3:6.2f}\n")

    print("=" * 110)
    print("  corpus = single global threshold (official-NAB style)")
    print("  anchored: scale-free monotone map (lambda3: r/(1+r), "
          "baselines: sigmoid(-df)) — no per-file info")
    print("  minmax  : per-file min-max to [0,1] before global threshold")
    print("  perfile : best threshold per file (old harness, inflated)")
    print("-" * 110)
    print(f"  {'method':<20} {'corpus/anchored':>16} {'corpus/minmax':>16} "
          f"{'per-file-opt':>14}")
    print("-" * 110)
    for method, a3, m3, p3, _ in sorted(rows, key=lambda r: -r[1]):
        print(f"  {method:<20} {a3:>16.2f} {m3:>16.2f} {p3:>14.2f}")

    # per-category means at the fixed global threshold (standard profile)
    print("\nPer-category mean of per-file normalized at fixed anchored θ* "
          "(standard profile):")
    cats = sorted({s.name.split('/')[0] for s in windowed})
    header = "  " + f"{'method':<20}" + "".join(f"{c[:14]:>16}" for c in cats)
    print(header)
    for method, _, _, _, pft in rows:
        pf = pft.get('standard', {})
        cells = []
        for c in cats:
            vals = [v for k, v in pf.items() if k.startswith(c + '/')]
            cells.append(f"{np.mean(vals):>16.2f}" if vals else f"{'—':>16}")
        print(f"  {method:<20}" + "".join(cells))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--compute', action='store_true')
    ap.add_argument('--aggregate', action='store_true')
    ap.add_argument('--methods', default='all',
                    help=f"'all', 'baselines', 'lambda3', or comma-separated "
                         f"subset of {ALL_METHODS}")
    ap.add_argument('--cache-dir', default=CACHE_DIR_DEFAULT)
    ap.add_argument('--include-empty', action='store_true',
                    help='aggregate over windowless files too '
                         '(official NAB includes them; FP penalties only)')
    args = ap.parse_args()

    sel = args.methods.strip().lower()
    if sel == 'all':
        methods = list(ALL_METHODS)
    elif sel == 'baselines':
        methods = list(BASELINE_METHODS)
    elif sel == 'lambda3':
        methods = list(LAMBDA3_METHODS)
    else:
        methods = [m.strip() for m in args.methods.split(',') if m.strip()]
        for m in methods:
            if m not in ALL_METHODS:
                ap.error(f"unknown method {m!r}; valid: {ALL_METHODS}")

    if not args.compute and not args.aggregate:
        ap.error("specify --compute and/or --aggregate")
    if args.compute:
        phase_compute(methods, args.cache_dir)
    if args.aggregate:
        phase_aggregate(methods, args.cache_dir, args.include_empty)


if __name__ == "__main__":
    main()
