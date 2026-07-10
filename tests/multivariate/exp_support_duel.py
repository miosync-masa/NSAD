"""The support-detector duel — ghost rig.

Contestants, all fit on the same bimodal calibration data, all
thresholded by the same label-free clean-quantile family (99.5% of
calibration scores = the frozen 0.5% floor):

  raw_ll     ours: un-normalized mixture log-likelihood floor
  bip        Yu-Qin reconstruction: posterior-weighted chi2 probability
  min_maha   alternative reading: nearest-component Mahalanobis
  ocsvm      nonparametric support boundary (RBF OC-SVM, nu=0.05,
             frozen config from benchmark_nab_baselines)

Question: in the inter-mode low-density valley (the ghost state), does
the un-normalized density floor see something the posterior-normalized
index does not? Both outcomes are pre-committed
(doc/preregistrations/experiment_plan_multivariate.md guardrails).

Fairness note (OC-SVM): its valley blindness here is CONFIG-DEPENDENT —
a tuned bandwidth may well see the valley. The comparison is
default-vs-default deliberately: the framework's entire claim is
zero-tuning operation, so the fair regime for every contestant is its
standard frozen configuration. Tuning OC-SVM per rig is exactly the
practice the framework exists to avoid. Stated explicitly so the
result is read as a zero-tuning-regime finding, not a handicap.

Usage::
    python -m tests.multivariate.exp_support_duel
"""

from __future__ import annotations

import numpy as np
from sklearn.svm import OneClassSVM

from tests.baselines.fgmm_bayes import FGMMBayes
from tests.probes.test_regime_ghost_state import (
    GHOST_LEN, GHOST_START, N_CAL, _make_series,
)

Q = 0.995      # = frozen 0.5% floor, cleanq family


def main():
    rng = np.random.default_rng(11)
    X, core = _make_series(rng)
    cal = X[:N_CAL]
    mu, sd = cal.mean(axis=0), cal.std(axis=0) + 1e-12
    Xz = (X - mu) / sd

    fg = FGMMBayes().fit(Xz[:N_CAL])
    oc = OneClassSVM(kernel='rbf', nu=0.05, gamma='scale').fit(Xz[:N_CAL])

    scores = {
        'raw_ll': fg.nll(Xz),
        'bip': fg.bip(Xz),
        'min_maha': fg.min_maha(Xz),
        'ocsvm': -oc.decision_function(Xz),
    }

    normal = np.ones(len(Xz), dtype=bool)
    normal[:N_CAL] = False
    normal[GHOST_START - 100:GHOST_START + GHOST_LEN + 100] = False

    print("=" * 78)
    print(f"SUPPORT-DETECTOR DUEL — ghost state (K_eff={fg.K_eff}), "
          f"thresholds = {Q:.1%} clean quantile")
    print("=" * 78)
    print(f"  {'contestant':<10} {'ghost-core det%':>16} "
          f"{'FP% (normal test)':>18} {'ghost margin*':>14}")
    for name, sc in scores.items():
        tau = float(np.quantile(sc[:N_CAL], Q))
        det = (sc[core] > tau).mean()
        fp = (sc[normal] > tau).mean()
        # margin: how far past the threshold the ghost median sits,
        # in units of the calibration IQR (severity gradation check)
        iqr = np.subtract(*np.percentile(sc[:N_CAL], [75, 25])) + 1e-12
        margin = (np.median(sc[core]) - tau) / iqr
        print(f"  {name:<10} {100*det:>15.1f}% {100*fp:>17.2f}% "
              f"{margin:>+14.1f}")
    print("\n* margin = (ghost median − threshold) / calibration IQR;")
    print("  saturating indices (bip ∈ [0,1]) lose severity gradation "
          "even when detection ties.")


if __name__ == "__main__":
    main()
