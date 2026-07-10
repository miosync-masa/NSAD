"""Mode-change probe — doc/preregistrations/experiment_plan_multivariate.md §9 Step 2 (H3).

Question: does the GLOBAL joint reconstruction residual (V2) false-alarm
at operating-mode changes that are part of NORMAL operation?

Setup: 2-channel coupled synthetic. Load alternates between two plateaus
(mode A: c≈0.3, mode B: c≈0.7) with instantaneous switches — a realistic
load step. Temperature follows the coupling with first-order lag (thermal
inertia), so each switch produces a normal transient. Mode changes occur
in BOTH the calibration span and the test span; all data is normal (no
anomaly anywhere). Any flag is a false alarm.

Report: FP rate within ±TRANSIENT_MARGIN frames of a transition vs
elsewhere. Both outcomes are informative:
  - transition FP >> steady FP → V2 (global residual) is mode-change
    fragile → motivates V3 (regime-conditioned, H3);
  - transition FP ≈ steady FP → global residual already absorbs mode
    changes; the regime layer is not needed on this axis (report honestly).

Also runs the same data through V3 (RegimeAwareDetector, K='auto',
calibrate_combined) for a first side-by-side.

Usage::
    python -m tests.probes.exp_mode_change_probe
"""

from __future__ import annotations

import numpy as np

from lambda3_detector.regime import RegimeAwareDetector
from lambda3_detector.streaming import StreamingReconstructionScorer

N_CAL = 4000
N_TEST = 4000
MODE_LEN = 800          # frames per plateau
TAU_T = 25.0            # thermal lag (frames) for the temperature response
NOISE_C = 0.02
NOISE_T = 0.4
TRANSIENT_MARGIN = 60   # frames around a transition counted as "transition"


def make_series(rng):
    n = N_CAL + N_TEST
    # load: alternating plateaus with instantaneous switches
    mode = (np.arange(n) // MODE_LEN) % 2
    c_target = np.where(mode == 0, 0.3, 0.7)
    c = c_target + NOISE_C * rng.normal(size=n)
    # temperature: first-order response to the load (thermal inertia)
    T = np.zeros(n)
    T[0] = 20.0 + 40.0 * c[0]
    for t in range(1, n):
        T_ss = 20.0 + 40.0 * c[t]
        T[t] = T[t - 1] + (T_ss - T[t - 1]) / TAU_T
    T = T + NOISE_T * rng.normal(size=n)
    X = np.column_stack([c, T])
    transitions = [t for t in range(1, n) if mode[t] != mode[t - 1]]
    return X, transitions


def classify_frames(n, transitions):
    near = np.zeros(n, dtype=bool)
    for tr in transitions:
        near[max(0, tr - TRANSIENT_MARGIN):tr + TRANSIENT_MARGIN + 1] = True
    return near


def main():
    rng = np.random.default_rng(7)
    X, transitions = make_series(rng)
    cal = X[:N_CAL]
    mu, sd = cal.mean(axis=0), cal.std(axis=0) + 1e-12
    Xz = (X - mu) / sd

    near = classify_frames(len(X), transitions)
    test_idx = np.arange(N_CAL, len(X))
    test_near = near[test_idx]
    n_trans_test = sum(1 for tr in transitions if tr >= N_CAL)

    print("=" * 78)
    print("MODE-CHANGE PROBE (H3) — all data normal; every flag is a false alarm")
    print(f"  plateaus of {MODE_LEN} frames, thermal lag tau={TAU_T}, "
          f"{n_trans_test} transitions in test span")
    print("=" * 78)

    # --- V2: global joint reconstruction residual -----------------------
    s = StreamingReconstructionScorer(n_components=5, delay_window=20)
    s.calibrate(Xz[:N_CAL])
    ratios = np.array([s.score(Xz, t) / (s.threshold + 1e-12)
                       for t in test_idx])
    flags = ratios >= 1.0

    fp_near = flags[test_near].mean()
    fp_steady = flags[~test_near].mean()
    per_trans = sum(
        flags[(test_idx >= tr - TRANSIENT_MARGIN)
              & (test_idx <= tr + TRANSIENT_MARGIN)].any()
        for tr in transitions if tr >= N_CAL
    )
    print(f"\nV2 (global residual):")
    print(f"  FP rate near transitions (±{TRANSIENT_MARGIN}): {fp_near:7.2%}")
    print(f"  FP rate in steady operation:                 {fp_steady:7.2%}")
    print(f"  transitions with >=1 false alarm:            "
          f"{per_trans}/{n_trans_test}")

    # --- V3: regime-conditioned (Tier 2, no anomaly anywhere) -----------
    det = RegimeAwareDetector(K='auto', calibrate_combined=True)
    result = det.fit_predict(Xz, np.zeros(len(X), dtype=bool))
    v3_flags = result['binary'].astype(bool)[test_idx]
    v3_unknown = result['unknown_mask'][test_idx]
    print(f"\nV3 (regime-conditioned, K_eff={result['K_eff']}, "
          f"calibrated):")
    print(f"  FP rate near transitions (±{TRANSIENT_MARGIN}): "
          f"{v3_flags[test_near].mean():7.2%}")
    print(f"  FP rate in steady operation:                 "
          f"{v3_flags[~test_near].mean():7.2%}")
    print(f"  unknown-rate near transitions:               "
          f"{v3_unknown[test_near].mean():7.2%}")
    print(f"  unknown-rate steady:                         "
          f"{v3_unknown[~test_near].mean():7.2%}")

    print("\nVerdict:")
    if fp_near > max(3 * fp_steady, 0.02):
        print("  V2 global residual IS mode-change fragile "
              f"({fp_near:.1%} vs {fp_steady:.1%}) -> motivates V3 (H3).")
    else:
        print("  V2 global residual absorbs mode changes "
              f"({fp_near:.1%} vs {fp_steady:.1%}) -> regime layer not "
              "needed on this axis (report honestly).")


if __name__ == "__main__":
    main()
