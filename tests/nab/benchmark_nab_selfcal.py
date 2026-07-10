"""
Self-calibrated operating-point evaluation — no test labels, no human threshold.

The legitimacy rule (paper core):
  Test anomaly labels are used ONLY for (i) training-data exclusion
  (disclosed semi-supervised anomaly-exclusion setting) and (ii) final
  scoring. Thresholds, transforms, and hyperparameters are derived from
  NORMAL STRUCTURE ONLY. NAB is used as a labeled public corpus to answer
  one question: does deviation-from-normal-structure detect the labeled
  anomalies at an operating point the detector derived by itself?

This is deliberately NOT the NAB score. Metrics are the industrial ones:
  - window catch rate : share of labeled anomaly windows containing >=1 flag
  - FP rate           : flagged frames outside any window, per 10k frames
  - flag rate         : total flagged share (sanity)
First 15% of each file (probationary period) is excluded from both.

Operating points (all label-free):
  native   : anchored score >= 0.5 (= combined ratio >= 1.0) — the
             detector's own OR-voting decision (Lambda³ methods only)
  cleanq   : per-file threshold = q-quantile of the combined score on
             clean frames (outside expanded anomaly windows, margin=50 —
             the same exclusion-only label use as training). Applicable
             to every method, giving baselines the same self-calibration
             opportunity. This is "sweeping on normal clean": the
             operating point comes from the normal-score distribution.

Reads the score caches produced by tests/nab/benchmark_nab_corpus.py.

Usage::
    python -m tests.nab.benchmark_nab_selfcal
    python -m tests.nab.benchmark_nab_selfcal --methods lambda3_tier2,lambda3_tier2_gated
    python -m tests.nab.benchmark_nab_selfcal --clean-q 0.999,0.9999
"""

from __future__ import annotations

import argparse
from typing import Dict, List, Optional

import numpy as np

from lambda3_detector.regime import expand_anomaly_mask

from tests.nab.benchmark_nab_corpus import (
    ALL_METHODS,
    CACHE_DIR_DEFAULT,
    anchored_transform,
    load_cache,
    make_anomaly_mask,
    _key,
)
from tests.nab.nab_datasets import iter_category

CATEGORIES = [
    'realKnownCause', 'realAWSCloudwatch', 'realTraffic',
    'realAdExchange', 'artificialWithAnomaly', 'realTweets',
]
MASK_MARGIN = 50


def evaluate_flags(sample, flags: np.ndarray, probation: int) -> Dict:
    """窓捕捉率と FP 率 (probation 以降のみ)。"""
    window_mask = make_anomaly_mask(sample)
    eval_mask = np.zeros(sample.n, dtype=bool)
    eval_mask[probation:] = True

    windows_total = 0
    windows_caught = 0
    for si, ei in sample.window_indices:
        if ei < probation:
            continue   # 窓全体が probation 内 → 評価対象外
        windows_total += 1
        if flags[max(si, probation):ei + 1].any():
            windows_caught += 1

    out_window = eval_mask & ~window_mask
    fp_frames = int((flags & out_window).sum())
    n_out = int(out_window.sum())
    n_eval = int(eval_mask.sum())
    return {
        'windows_total': windows_total,
        'windows_caught': windows_caught,
        'fp_frames': fp_frames,
        'n_out_window': n_out,
        'n_eval': n_eval,
        'flag_frames': int((flags & eval_mask).sum()),
    }


def flags_native(method: str, scores: np.ndarray) -> Optional[np.ndarray]:
    if not method.startswith('lambda3'):
        return None   # baselines have no ratio-1.0 semantics
    return anchored_transform(method, scores) >= 0.5


def flags_cleanq(sample, scores: np.ndarray, q: float) -> np.ndarray:
    """per-file 閾値 = clean frame 上の combined score の q-quantile。

    clean = expanded anomaly window (margin=50) の外。学習時と同じ
    「除外のみ」のラベル使用。閾値そのものは正常スコア分布だけで決まる。
    """
    expanded = expand_anomaly_mask(make_anomaly_mask(sample), MASK_MARGIN)
    clean_scores = scores[~expanded]
    if len(clean_scores) < 100:
        return np.zeros(sample.n, dtype=bool)
    tau = float(np.quantile(clean_scores, q))
    return scores > tau


def aggregate(rows: List[Dict]) -> Dict:
    wt = sum(r['windows_total'] for r in rows)
    wc = sum(r['windows_caught'] for r in rows)
    fp = sum(r['fp_frames'] for r in rows)
    no = sum(r['n_out_window'] for r in rows)
    return {
        'files': len(rows),
        'catch': 100.0 * wc / wt if wt else 0.0,
        'windows': f"{wc}/{wt}",
        'fp_per_10k': 1e4 * fp / no if no else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--methods', default='all')
    ap.add_argument('--cache-dir', default=CACHE_DIR_DEFAULT)
    ap.add_argument('--clean-q', default='0.999,0.9999',
                    help='comma-separated quantiles for cleanq operating points')
    args = ap.parse_args()

    if args.methods.strip().lower() == 'all':
        methods = list(ALL_METHODS)
    else:
        methods = [m.strip() for m in args.methods.split(',') if m.strip()]

    qs = [float(x) for x in args.clean_q.split(',') if x.strip()]

    samples = []
    for cat in CATEGORIES:
        samples.extend(iter_category(cat))

    print("=" * 100)
    print("SELF-CALIBRATED OPERATING POINTS — label-free thresholds, "
          "industrial metrics")
    print("  catch    = % of labeled anomaly windows containing >=1 flagged frame")
    print("  fp/10k   = flagged frames outside windows per 10k out-of-window frames")
    print("  native   = combined ratio >= 1.0 (Lambda³ only)")
    print(f"  cleanq   = per-file clean-score quantile threshold, q in {qs}")
    print("  (probationary first 15% excluded)")
    print("=" * 100)

    header = (f"  {'method':<22} {'op-point':<14} {'catch %':>8} "
              f"{'windows':>10} {'fp/10k':>8}")
    print(header)
    print("-" * 100)

    for method in methods:
        cache = load_cache(args.cache_dir, method)
        missing = [s for s in samples if _key(s.name) not in cache]
        if missing:
            print(f"  {method:<22} (skip — {len(missing)} files not cached)")
            continue

        ops = []
        if method.startswith('lambda3'):
            ops.append(('native', None))
        ops.extend((f'cleanq@{q}', q) for q in qs)

        for op_name, q in ops:
            rows = []
            per_cat: Dict[str, List[Dict]] = {}
            for s in samples:
                scores = cache[_key(s.name)]
                probation = int(0.15 * s.n)
                if q is None:
                    flags = flags_native(method, scores)
                else:
                    flags = flags_cleanq(s, scores, q)
                r = evaluate_flags(s, flags.astype(bool), probation)
                rows.append(r)
                per_cat.setdefault(s.name.split('/')[0], []).append(r)
            a = aggregate(rows)
            print(f"  {method:<22} {op_name:<14} {a['catch']:>8.1f} "
                  f"{a['windows']:>10} {a['fp_per_10k']:>8.1f}")
        print()


if __name__ == "__main__":
    main()
