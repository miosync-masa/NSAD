"""NSAD on the Paderborn bearing subset — vibration-adapter exploration.

Questions (post-freeze, exploratory; §13 adapter view):
  Q1  Does BIC discover the operating conditions as regimes?
      (two conditions in the subset — expect K_eff ≈ 2, and regime
      labels should align with the condition tag on held-out normal)
  Q2  Does the frozen support-floor path detect bearing damage through
      the fault-agnostic vibration vocabulary, per condition?
  Q3  FAR on held-out healthy recordings, paired with detection
      (the §5.5 rule), splits BY RECORDING (frames within a 4 s
      recording are correlated — a frame-level split would leak).

Frozen path throughout: z-norm on fit, PCA 90% (d=27 > 16 guardrail),
GMM BIC auto-K full-cov, nested out-of-sample 0.5% floor. No
per-dataset tuning.

Usage::
    python -m tests.paderborn.exp_paderborn
"""

from __future__ import annotations

import numpy as np

from tests.hydraulic.exp_hydraulic import build_floor
from tests.paderborn.paderborn_datasets import CONDITIONS, load_frames

SPLIT_FRAC = 0.6


def main():
    X, bearing, condition, rec = load_frames()
    print("=" * 72)
    print("PADERBORN SUBSET — frozen support-floor path, vibration "
          f"adapter d={X.shape[1]}")
    print("  normal = K001 (single healthy bearing; within-bearing "
          "holdout, disclosed)")
    print("=" * 72)

    normal = bearing == 'K001'
    recs = np.unique(rec[normal])
    rng = np.random.default_rng(0)
    rng.shuffle(recs)
    n_fit = int(SPLIT_FRAC * len(recs))
    fit_recs, hold_recs = set(recs[:n_fit]), set(recs[n_fit:])
    fit_m = normal & np.isin(rec, list(fit_recs))
    hold_m = normal & np.isin(rec, list(hold_recs))

    mu, sd = X[fit_m].mean(0), X[fit_m].std(0) + 1e-12
    z = lambda A: (A - mu) / sd

    margin, k = build_floor(z(X[fit_m]))
    print(f"\nQ1 — regimes: BIC selected K = {k} "
          f"({len(CONDITIONS)} operating conditions in the data)")

    m_hold = margin(z(X[hold_m]))
    far = float((m_hold > 0).mean())
    print(f"\nQ3 — held-out healthy (by recording, {len(hold_recs)} recs, "
          f"{hold_m.sum()} frames): FAR {far:6.2%} (designed 0.5%)")

    print("\nQ2 — detection per damaged bearing per condition "
          "(FAR above is the pair):")
    for b in ('KA01', 'KI01'):
        for c in CONDITIONS:
            m = (bearing == b) & (condition == c)
            mm = margin(z(X[m]))
            print(f"  {b} ({'outer' if b == 'KA01' else 'inner'} ring, "
                  f"artificial) @ {c}: det {(mm > 0).mean():6.1%}   "
                  f"median margin {np.median(mm):8.1f} IQR   "
                  f"(n={m.sum()})")


if __name__ == '__main__':
    main()
