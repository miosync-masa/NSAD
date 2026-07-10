"""
NAB classical baselines — self-run under the SAME protocol as Lambda³-NSAD.

Purpose (paper, doc/paper/abstract.md §8 "Known review risks"):
  All Lambda³ comparisons so far rest on published NAB numbers. This script
  runs classical normal-only detectors through the exact same harness
  (same loader, same 5D feature expansion, same NAB Sweeper scoring, same
  probationary conventions) so that the paper can report author-run
  baselines and validate protocol comparability.

Baselines (all scikit-learn, single frozen configuration across all files):
  - ocsvm   : OneClassSVM(RBF, nu=0.05, gamma='scale')
  - iforest : IsolationForest(n_estimators=100, random_state=0)
  - lof     : LocalOutlierFactor(n_neighbors=20, novelty=True)

Two evaluation modes, mirroring the two Lambda³ tiers:
  - streaming  (Tier 0 analog): fit on the first 15% of each series
    (the NAB probationary period, = Lambda³-S calibration span), then score
    every frame with the frozen model. Strictly causal.
  - exclusion  (Tier 2 analog): fit on all frames outside the expanded
    anomaly windows (mask_margin=50, identical to RegimeAwareDetector),
    z-normalized by clean statistics. Semi-supervised anomaly-exclusion,
    same information budget as Lambda³-R.

Anomaly score fed to the NAB Sweeper: -decision_function / -score_samples
(higher = more anomalous). The Sweeper min-max normalizes per file, exactly
as for Lambda³ scores.

Training subsample cap: OneClassSVM is O(n^2)+ in training; training sets
larger than --max-train-samples (default 5000) are subsampled with a fixed
random_state=0. Disclosed in the paper as part of the frozen configuration.

Usage::
    python -m tests.nab.benchmark_nab_baselines --category realKnownCause
    python -m tests.nab.benchmark_nab_baselines --category realTraffic --detectors ocsvm
    python -m tests.nab.benchmark_nab_baselines --category all --modes streaming,exclusion
"""

from __future__ import annotations

import argparse
import time
from typing import Dict, List, Optional

import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

from lambda3_detector.regime import expand_anomaly_mask

from tests.nab.nab_datasets import iter_category
from tests.nab.nab_features import expand_to_5d
from tests.nab.nab_metrics import format_nab_score, score_all_profiles

CATEGORIES = [
    'realKnownCause', 'realAWSCloudwatch', 'realTraffic',
    'realAdExchange', 'artificialWithAnomaly', 'realTweets',
]

DETECTOR_NAMES = ['ocsvm', 'iforest', 'lof']

MODES = ['streaming', 'exclusion']

CALIBRATION_RATIO = 0.15   # = NAB probationary period = Lambda³-S calibration
MASK_MARGIN = 50           # = RegimeAwareDetector default


def make_detector(name: str, random_state: int = 0):
    """Single frozen configuration per detector — no per-dataset tuning."""
    if name == 'ocsvm':
        return OneClassSVM(kernel='rbf', nu=0.05, gamma='scale')
    if name == 'iforest':
        return IsolationForest(n_estimators=100, random_state=random_state)
    if name == 'lof':
        return LocalOutlierFactor(n_neighbors=20, novelty=True)
    raise ValueError(f"unknown detector {name!r}; valid: {DETECTOR_NAMES}")


def anomaly_score(model, X: np.ndarray) -> np.ndarray:
    """Continuous anomaly score, higher = more anomalous."""
    if hasattr(model, 'decision_function'):
        return -np.asarray(model.decision_function(X), dtype=np.float64)
    return -np.asarray(model.score_samples(X), dtype=np.float64)


def make_anomaly_mask(sample) -> np.ndarray:
    mask = np.zeros(sample.n, dtype=bool)
    for si, ei in sample.window_indices:
        mask[si:ei + 1] = True
    return mask


def _subsample(X: np.ndarray, max_n: int, random_state: int = 0) -> np.ndarray:
    if len(X) <= max_n:
        return X
    rng = np.random.default_rng(random_state)
    idx = rng.choice(len(X), size=max_n, replace=False)
    return X[np.sort(idx)]


def run_one(sample,
            detector_name: str,
            mode: str,
            n_features: int = 5,
            feature_window: int = 30,
            max_train_samples: int = 5000) -> Optional[Dict]:
    n_windows = len(sample.windows_ts)
    anomaly_mask = make_anomaly_mask(sample)
    if not anomaly_mask.any():
        return None

    if n_features == 1:
        X = np.asarray(sample.values, dtype=np.float64).reshape(-1, 1)
    elif n_features == 5:
        X = expand_to_5d(sample.values, window=feature_window)
    else:
        raise ValueError(f"unsupported n_features={n_features}")
    n = len(X)

    # --- training split, mirroring the Lambda³ tiers ---
    if mode == 'streaming':
        n_cal = max(int(n * CALIBRATION_RATIO), 20)
        train_idx = np.arange(n_cal)
    elif mode == 'exclusion':
        expanded = expand_anomaly_mask(anomaly_mask, MASK_MARGIN)
        train_idx = np.where(~expanded)[0]
        if len(train_idx) < 100:
            print(f"  {sample.name}: clean data too small "
                  f"({len(train_idx)} frames), skipping")
            return None
    else:
        raise ValueError(f"unknown mode {mode!r}; valid: {MODES}")

    # --- z-normalize with training statistics (same convention as Lambda³) ---
    mu = X[train_idx].mean(axis=0)
    sd = X[train_idx].std(axis=0) + 1e-10
    X_norm = (X - mu) / sd
    X_train = _subsample(X_norm[train_idx], max_train_samples)

    # --- fit + score ---
    model = make_detector(detector_name)
    t0 = time.perf_counter()
    model.fit(X_train)
    scores = anomaly_score(model, X_norm)
    t_run = time.perf_counter() - t0

    np.nan_to_num(scores, copy=False, nan=0.0, posinf=0.0, neginf=0.0)

    nab_scores = score_all_profiles(sample, scores)
    print(f"■ {sample.name}  n={n}  #windows={n_windows}  "
          f"train={len(X_train)}  t={t_run:.1f}s  "
          f"[{detector_name.upper()} / {mode}]")
    for prof, s in nab_scores.items():
        print(format_nab_score(s, f'{detector_name}-{mode}'))

    return {
        'name': sample.name,
        'n': sample.n,
        'n_windows': n_windows,
        't_run': t_run,
        'nab_scores': nab_scores,
    }


def _agg(rows: List[Dict]) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    rows = [r for r in rows if r is not None]
    if not rows:
        return out
    profiles = list(rows[0]['nab_scores'].keys())
    for prof in profiles:
        norms = [r['nab_scores'][prof].normalized for r in rows]
        out[prof] = {
            'mean': float(np.mean(norms)),
            'min': float(np.min(norms)),
            'max': float(np.max(norms)),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--category', default='realKnownCause',
                    help=f"NAB category, or 'all' for {CATEGORIES}")
    ap.add_argument('--windows-file', default='combined_windows.json')
    ap.add_argument('--features', type=int, default=5, choices=[1, 5])
    ap.add_argument('--feature-window', type=int, default=30)
    ap.add_argument('--detectors', default='all',
                    help=f"comma-separated subset of {DETECTOR_NAMES}, or 'all'")
    ap.add_argument('--modes', default='streaming,exclusion',
                    help=f"comma-separated subset of {MODES}")
    ap.add_argument('--max-train-samples', type=int, default=5000,
                    help='training subsample cap (OneClassSVM scalability; '
                         'fixed random_state=0)')
    args = ap.parse_args()

    if args.detectors.strip().lower() == 'all':
        detectors = list(DETECTOR_NAMES)
    else:
        detectors = [d.strip() for d in args.detectors.split(',') if d.strip()]
        for d in detectors:
            if d not in DETECTOR_NAMES:
                ap.error(f"unknown detector {d!r}; valid: {DETECTOR_NAMES}")

    modes = [m.strip() for m in args.modes.split(',') if m.strip()]
    for m in modes:
        if m not in MODES:
            ap.error(f"unknown mode {m!r}; valid: {MODES}")

    categories = (
        CATEGORIES if args.category.strip().lower() == 'all'
        else [args.category]
    )

    print("=" * 110)
    print(f"NAB CLASSICAL BASELINES  categories={categories}  "
          f"detectors={detectors}  modes={modes}  "
          f"features={args.features}  max_train={args.max_train_samples}")
    print("=" * 110)

    # results[(detector, mode)][category] = (rows, agg)
    summary: Dict = {}
    for category in categories:
        samples = list(iter_category(category, windows_file=args.windows_file))
        for det in detectors:
            for mode in modes:
                print(f"\n--- category={category}  detector={det}  mode={mode} ---")
                rows = []
                for sample in samples:
                    r = run_one(
                        sample, det, mode,
                        n_features=args.features,
                        feature_window=args.feature_window,
                        max_train_samples=args.max_train_samples,
                    )
                    if r is not None:
                        rows.append(r)
                agg = _agg(rows)
                summary[(det, mode, category)] = (len(rows), agg)

    print("\n" + "=" * 110)
    print("SUMMARY (3-profile mean per detector x mode x category)")
    print("=" * 110)
    print(f"  {'detector':<9} {'mode':<11} {'category':<24} {'files':>5} "
          f"{'3-prof mean':>12}")
    print("-" * 110)
    weighted: Dict = {}
    for (det, mode, category), (n_files, agg) in sorted(summary.items()):
        if not agg:
            continue
        three_prof = float(np.mean([agg[p]['mean'] for p in agg]))
        print(f"  {det:<9} {mode:<11} {category:<24} {n_files:>5} "
              f"{three_prof:>12.2f}")
        weighted.setdefault((det, mode), []).append((n_files, three_prof))

    if len(categories) > 1:
        print("-" * 110)
        for (det, mode), pairs in sorted(weighted.items()):
            total = sum(nf for nf, _ in pairs)
            wmean = sum(nf * v for nf, v in pairs) / total
            print(f"  {det:<9} {mode:<11} {'WEIGHTED':<24} {total:>5} "
                  f"{wmean:>12.2f}")


if __name__ == "__main__":
    main()
