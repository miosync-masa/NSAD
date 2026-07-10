"""Frozen-config transfer test — the missing half of pillar ②.

Claim under test (deployability, NOT performance): our operating point
is a percentile of the detector's OWN clean-score distribution, so its
MEANING ("flag x% of clean frames") is dimension-, scale-, and
shape-invariant — it transfers. An RBF OC-SVM's operating point does
not: γ enters as exp(−γ‖x−y‖²) where ‖x−y‖² grows with dimension and
scale, so a γ frozen at one scale degenerates at another, and ν places
a train-side geometric boundary whose realized FAR drifts with data.

Scope nails (pre-committed):
  - This is an advantage over OC-SVM-style bandwidths and fixed
    control-limit MSPC. It is NOT an advantage over Yu-Qin FGMM
    (Figueiredo-Jain auto-K is equally self-adapting on this axis).
  - Deployability, not performance: a per-dataset-tuned OC-SVM beats
    Lambda³-R at matched points on NAB (scoreboard §2.3, disclosed).
  - Language rule: "no per-dataset tuning; structural defaults;
    adjustable if desired" — never "parameter-free", never bare
    "tuning-free".

Protocol: per dataset (2ch rig → 8ch SKAB → 52ch TEP), split clean data
60/40 (fit / held-out). Each method fixes its operating point on the
fit part only; we report the REALIZED flag rate on held-out clean
frames against each method's own DESIGNED rate, plus detection at that
transferred point.

  ours          GMM (BIC auto-K, full cov) + 0.5% likelihood floor
                (designed clean flag rate: 0.5%)
  ocsvm_frozen  ν=0.05, γ = γ* frozen ONCE on the 2ch reference rig,
                native boundary df=0 (designed: ~5% on clean)
  ocsvm_scale   ν=0.05, γ='scale' re-derived per dataset — included to
                show γ CANNOT be fixed (sklearn recomputes it from the
                data precisely because a frozen γ does not transfer)

Result asymmetry (nail ①, pre-committed weighting): the load-bearing
claim is the FROZEN-γ total collapse (structural: γ fixed at d=2
saturates the kernel at d=52 → everything is "far" → 100% FAR). The
γ='scale' ×4.7 drift is AUXILIARY: at d=52 with n=300 it is confounded
with the small-sample regime and a sample-size contribution cannot be
excluded — stated here first, so no reviewer has to.

The accommodation row (nail ②): 'frozen+cleanq' grants OC-SVM our full
mechanism — the same nested out-of-sample clean-percentile operating
point. Confirmed decomposition: at d=8 the percentile threshold rescues
frozen-γ's FAR (21.9% → 4.5%); at d=52 the FAR "transfers" (0.00%) but
detection is 0.0% — the bandwidth has killed the SIGNAL, and no
operating-point mechanism can rescue a dead score. Threshold semantics
and score validity are independent failure axes.

The two 0.00%s (kill criterion self-applied): our d=52 realized FAR is
0.00% — the same number that killed the hybrid row. The distinction is
the detection column of the same run: ours detects 58.1% of fault
frames at that transferred point; the hybrid detects 0.0%. A silent
detector transfers FAR trivially; a valid one transfers FAR AND signal.
Always read the FAR and detection columns as a pair.

Honesty notes from the run:
  - rig2 ghost 100% for OC-SVM here is at its loose NATIVE nu=5% point;
    the duel's valley-blindness finding was at matched low-FAR (0.5%)
    operating points and stands as stated there.
  - 'ours' realized rates include quantile sampling noise (the 0.5%
    quantile of a few hundred floor frames is a handful of order
    statistics); drift factors of ~2 at small n are estimation noise,
    not calibration failure — reported as-is.
  - The two guardrails in _ours are load-bearing: without them the
    mechanism itself drifted 32x at d=52 (in-sample percentile bias,
    third occurrence in this project after the SKAB head-calibration
    and MSPC audits — floors must be out-of-sample whenever model
    capacity is high relative to n).

Usage::
    python -m tests.multivariate.exp_frozen_transfer
"""

from __future__ import annotations

import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.svm import OneClassSVM

from tests.multivariate.exp_deployability import _fit_auto

LL_Q = 0.995          # ours: 0.5% designed clean flag rate
NU = 0.05             # OC-SVM: 5% designed train outlier fraction
SPLIT_FRAC = 0.6


def _ours(fit, holdout, reduce_dims=16):
    """Percentile floor with the two protocol guardrails that make the
    transfer claim honest (both learned in earlier audits, disclosed):

    1. OUT-OF-SAMPLE floor: the floor percentile is taken on a nested
       held-out slice of the fit data, never on the frames the density
       model was fit to — in-sample percentile bias grows with model
       capacity / n and silently destroys the designed rate (measured:
       32x at d=52 with an in-sample floor).
    2. High-d reduction: for d > reduce_dims, densities are modeled in
       the PCA subspace (the §2 guardrail; a 52-D full covariance from
       ~300 samples is not a sane density estimate).
    """
    n_nest = int(0.6 * len(fit))
    model_part, floor_part = fit[:n_nest], fit[n_nest:]

    if fit.shape[1] > reduce_dims:
        from tests.baselines.mspc_baselines import MSPCModel
        m = MSPCModel().fit(model_part)
        proj = lambda A: m._scores_resid(A)[0]
    else:
        proj = lambda A: A

    g, k = _fit_auto(proj(model_part), 'full')
    floor = float(np.quantile(g.score_samples(proj(floor_part)),
                              1.0 - LL_Q))
    return ((g.score_samples(proj(holdout)) < floor).mean(),
            lambda A: g.score_samples(proj(A)) < floor, k)


def _ocsvm(fit, holdout, gamma):
    oc = OneClassSVM(kernel='rbf', nu=NU, gamma=gamma).fit(fit)
    return ((oc.decision_function(holdout) < 0).mean(),
            lambda A: oc.decision_function(A) < 0)


def _ocsvm_cleanq(fit, holdout, gamma):
    """OC-SVM granted OUR mechanism (nail ②, full accommodation): the
    same nested out-of-sample clean-percentile operating point, at its
    own designed 5% rate, on its own score. Pre-registered expectation:
    the percentile mechanism transfers the FAR for ANY score, but it
    cannot rescue a score the frozen bandwidth has degenerated —
    threshold semantics and score validity are separate failure axes."""
    n_nest = int(0.6 * len(fit))
    oc = OneClassSVM(kernel='rbf', nu=NU, gamma=gamma).fit(fit[:n_nest])
    score = lambda A: -oc.decision_function(A)
    tau = float(np.quantile(score(fit[n_nest:]), 1.0 - NU))
    return ((score(holdout) > tau).mean(),
            lambda A: score(A) > tau)


def gamma_scale(X):
    return 1.0 / (X.shape[1] * X.var())


def dataset_rig2():
    from tests.probes.test_regime_ghost_state import (
        GHOST_LEN, GHOST_START, N_CAL, _make_series)
    rng = np.random.default_rng(11)
    X, core = _make_series(rng)
    cal = X[:N_CAL]
    Xz = (X - cal.mean(0)) / (cal.std(0) + 1e-12)
    clean = Xz[:N_CAL]
    anomaly = Xz[core]
    return clean, [('ghost det%', anomaly)], 'rig2 (d=2)'


def dataset_skab():
    from tests.multivariate.skab_datasets import iter_all
    from tests.multivariate.benchmark_skab import _clean_setup
    cleans, anomalies = [], []
    for s in iter_all():
        Xz, clean = _clean_setup(s)
        cleans.append(clean)
        for (si, ei) in s.window_indices:
            anomalies.append(Xz[si:ei + 1])
    return (np.vstack(cleans),
            [('window frames det%', np.vstack(anomalies))], 'SKAB (d=8)')


def dataset_tep():
    from tests.multivariate.tep_datasets import FAULT_START, iter_faults, load_train_normal
    train = load_train_normal()
    z = lambda A: (A - train.mean(0)) / (train.std(0) + 1e-12)
    faults = np.vstack([z(s.values)[FAULT_START:] for s in iter_faults()])
    return z(train), [('fault frames det%', faults)], 'TEP (d=52)'


def main():
    datasets = [dataset_rig2(), dataset_skab(), dataset_tep()]

    # freeze gamma once, on the reference rig's fit part
    ref_clean = datasets[0][0]
    n_fit = int(SPLIT_FRAC * len(ref_clean))
    GAMMA_STAR = gamma_scale(ref_clean[:n_fit])

    print("=" * 96)
    print("FROZEN-CONFIG TRANSFER TEST — realized clean flag rate vs "
          "each method's designed rate")
    print(f"  gamma* frozen once on rig2 fit part: {GAMMA_STAR:.4f}")
    print("  deployability claim only; scope: OC-SVM bandwidths & fixed "
          "control limits (NOT Yu-Qin auto-K)")
    print("=" * 96)
    print(f"  {'dataset':<12} {'method':<14} {'designed':>9} "
          f"{'realized(held-out)':>19} {'detection':>22}")
    print("-" * 96)

    for clean, anomaly_sets, label in datasets:
        rng = np.random.default_rng(0)
        idx = rng.permutation(len(clean))
        n_fit = int(SPLIT_FRAC * len(clean))
        fit, hold = clean[idx[:n_fit]], clean[idx[n_fit:]]

        rows = []
        far, flag, k = _ours(fit, hold)
        rows.append((f'ours (K={k})', 1.0 - LL_Q, far, flag))
        far, flag = _ocsvm(fit, hold, GAMMA_STAR)
        rows.append(('ocsvm frozen', NU, far, flag))
        far, flag = _ocsvm(fit, hold, 'scale')
        rows.append(('ocsvm scale', NU, far, flag))
        far, flag = _ocsvm_cleanq(fit, hold, GAMMA_STAR)
        rows.append(('frozen+cleanq', NU, far, flag))

        for name, designed, realized, flag in rows:
            dets = "  ".join(
                f"{dn}: {flag(A).mean():5.1%}" for dn, A in anomaly_sets)
            drift = realized / designed if designed else float('inf')
            print(f"  {label:<12} {name:<14} {designed:>8.1%} "
                  f"{realized:>13.2%} (x{drift:4.1f}) {dets:>22}")
        print()


if __name__ == "__main__":
    main()
