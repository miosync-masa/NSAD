"""SKAB benchmark — multivariate variants on the real pump rig.

doc/preregistrations/experiment_plan_multivariate.md §9 Steps 3-4.

Variants (frozen configs, no per-dataset tuning). ALL variants build
normal structure from the SAME training data — the exclusion-cleaned
frames (anomaly windows + margin removed; the semi-supervised
anomaly-exclusion setting, legitimacy rule §7) — so the ONLY difference
between v0 and v2 is marginal vs joint structure. This is the §6
"V0 → V2, scorers held constant" isolation:

  v0   Per-channel marginal detection + OR late-fusion (the naive
       multi-sensor solution): StreamingJumpScorer per channel,
       calibrated on clean frames, flag if ANY channel fires.
  v2   Joint delay-embedded reconstruction residual, d=8:
       StreamingReconstructionScorer calibrated on clean frames,
       per-channel z-norm from clean statistics.
  v3   Tier-2 RegimeAwareDetector on the 8 raw channels (the channels ARE
       the feature space; no expand_to_5d), K='auto', full-covariance GMM,
       calibrate_combined=True. Reports alarm / unknown / combined
       channels separately.

Protocol notes:
  - anomaly-free.csv is recorded at a different operating point than the
    labeled files (flow 125 vs 32 …), so per-file normal structure is the
    realistic protocol; the anomaly-free file is not used here.
  - First-15%-head calibration was tried and rejected: SKAB files start
    with a thermal warmup transient, so a head-only baseline mismatches
    later normal operation for every variant (V2 FP ≈ 85%); exclusion-
    cleaned calibration covers the operating envelope and matches V3's
    information budget.
  - Metrics identical to the NAB self-calibrated evaluation: window catch
    rate + FP per 10k out-of-window frames, probationary first 15%
    excluded (reuses tests/nab/benchmark_nab_selfcal.evaluate_flags).

Usage::
    python -m tests.multivariate.benchmark_skab
    python -m tests.multivariate.benchmark_skab --variants v2,v3 --group valve1
"""

from __future__ import annotations

import argparse
from typing import Dict, List

import numpy as np

from lambda3_detector.regime import RegimeAwareDetector, expand_anomaly_mask
from lambda3_detector.streaming import (
    StreamingJumpScorer,
    StreamingReconstructionScorer,
)

from tests.nab.benchmark_nab_selfcal import aggregate, evaluate_flags
from tests.multivariate.skab_datasets import GROUPS, iter_group

CAL_RATIO = 0.15        # probationary span for evaluation (as in NAB)
MASK_MARGIN = 50        # exclusion margin (= RegimeAwareDetector default)
VARIANTS = ['v0', 'v2', 'v3']


def _clean_setup(sample):
    """Shared training data for all variants: exclusion-cleaned frames,
    per-channel z-norm from clean statistics (guardrail)."""
    expanded = expand_anomaly_mask(sample.anomaly.astype(bool), MASK_MARGIN)
    X = sample.values
    clean_raw = X[~expanded]
    mu = clean_raw.mean(axis=0)
    sd = clean_raw.std(axis=0) + 1e-12
    Xz = (X - mu) / sd
    return Xz, Xz[~expanded]


def run_v0(sample) -> Dict[str, np.ndarray]:
    """Per-channel jump + OR fusion (naive multi-sensor baseline)."""
    Xz, clean = _clean_setup(sample)
    n = sample.n
    flags = np.zeros(n, dtype=bool)
    for ch in range(Xz.shape[1]):
        s = StreamingJumpScorer(percentile=99.0)
        s.calibrate(clean[:, ch:ch + 1])
        thr = s.threshold + 1e-12
        x1 = Xz[:, ch:ch + 1]
        ratios = np.array([s.score(x1, t) / thr for t in range(n)])
        flags |= ratios >= 1.0
    return {'alarm': flags}


def run_v2(sample) -> Dict[str, np.ndarray]:
    """Joint reconstruction residual, d=8, same training data as v0."""
    Xz, clean = _clean_setup(sample)
    n = sample.n
    s = StreamingReconstructionScorer(n_components=5, delay_window=20)
    s.calibrate(clean)
    thr = s.threshold + 1e-12
    ratios = np.array([s.score(Xz, t) / thr for t in range(n)])
    return {'alarm': ratios >= 1.0}


def run_v3(sample) -> Dict[str, np.ndarray]:
    """Tier-2 regime-aware on raw 8 channels, anomaly-exclusion setting."""
    det = RegimeAwareDetector(K='auto', calibrate_combined=True)
    mask = sample.anomaly.astype(bool)
    result = det.fit_predict(sample.values, mask)
    alarm = result['binary'].astype(bool)
    unknown = result['unknown_mask'].astype(bool)
    return {
        'alarm': alarm & ~unknown,      # state == 1
        'unknown': unknown,             # state == 2
        'combined': alarm | unknown,    # state != 0
        '_K_eff': result['K_eff'],
    }


RUNNERS = {'v0': run_v0, 'v2': run_v2, 'v3': run_v3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variants', default='v0,v2,v3')
    ap.add_argument('--group', default='all',
                    help=f"'all' or one of {GROUPS}")
    args = ap.parse_args()

    variants = [v.strip() for v in args.variants.split(',') if v.strip()]
    for v in variants:
        if v not in VARIANTS:
            ap.error(f"unknown variant {v!r}; valid: {VARIANTS}")
    groups = GROUPS if args.group == 'all' else [args.group]

    print("=" * 100)
    print(f"SKAB benchmark  groups={groups}  variants={variants}")
    print("  catch = % of labeled anomaly windows with >=1 flag; "
          "fp/10k = out-of-window flags per 10k frames")
    print("  probationary first 15% excluded; frozen configs; "
          "per-file normal structure")
    print("=" * 100)

    # rows[variant][channel] = list of per-file evaluate_flags dicts
    rows: Dict[str, Dict[str, List[dict]]] = {
        v: {} for v in variants
    }
    per_group: Dict[str, Dict[str, Dict[str, List[dict]]]] = {
        g: {v: {} for v in variants} for g in groups
    }
    k_effs: List[int] = []

    for g in groups:
        for sample in iter_group(g):
            probation = int(CAL_RATIO * sample.n)
            for v in variants:
                try:
                    out = RUNNERS[v](sample)
                except ValueError as e:
                    print(f"  {sample.name} [{v}]: SKIP ({e})")
                    continue
                if '_K_eff' in out:
                    k_effs.append(out.pop('_K_eff'))
                for channel, flags in out.items():
                    r = evaluate_flags(sample, flags, probation)
                    rows[v].setdefault(channel, []).append(r)
                    per_group[g][v].setdefault(channel, []).append(r)

    print(f"\n  {'variant':<10} {'channel':<10} {'group':<9} {'files':>5} "
          f"{'catch %':>8} {'windows':>9} {'fp/10k':>8}")
    print("-" * 100)
    for v in variants:
        for channel in rows[v]:
            for g in groups:
                rs = per_group[g][v].get(channel, [])
                if not rs:
                    continue
                a = aggregate(rs)
                print(f"  {v:<10} {channel:<10} {g:<9} {a['files']:>5} "
                      f"{a['catch']:>8.1f} {a['windows']:>9} "
                      f"{a['fp_per_10k']:>8.1f}")
            a = aggregate(rows[v][channel])
            print(f"  {v:<10} {channel:<10} {'ALL':<9} {a['files']:>5} "
                  f"{a['catch']:>8.1f} {a['windows']:>9} "
                  f"{a['fp_per_10k']:>8.1f}")
        print()
    if k_effs:
        vals, counts = np.unique(k_effs, return_counts=True)
        print(f"  v3 K_eff distribution: "
              + "  ".join(f"K={k}:{c}" for k, c in zip(vals, counts)))


if __name__ == "__main__":
    main()
