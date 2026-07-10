"""NSAD on a physical hydraulic rig (UCI 447) — exploratory experiment.

Question: does the frozen support-floor path (the paper's §4.6
configuration, untouched) detect component degradation on a real
multi-component rig, and — the severity question — does the
NON-SATURATING margin grade the labeled degradation STAGES
monotonically? This dataset is the first one available to us where
severity ground truth is graded (valve 90/80/73%, accumulator
115/100/90 bar, ...), i.e. where the severity-gradation claim can be
tested against physical labels rather than rig geometry.

Design (per target component, four experiments):
  normal    = cycles with the TARGET component nominal, stable flag 0;
              the other three components vary freely inside this set —
              they are operating conditions, and the regime layer must
              absorb them (this is the 'same value, different meaning'
              setting on real hardware).
  degraded  = cycles at each labeled degradation stage of the target.
  detector  = per-cycle-mean frames (d=17), z-normed on the fit split,
              PCA (90% var, the d>16 guardrail), GMM (BIC auto-K,
              full cov), nested OUT-OF-SAMPLE 0.5% likelihood floor —
              identical to tests/multivariate/exp_frozen_transfer._ours. No
              per-dataset tuning anywhere.
  report    = realized FAR on held-out normal cycles (paired with
              detection, per the §5.5 rule), detection %% per stage,
              and the median margin (in fit-side IQR units) per stage
              with a monotonicity verdict.

Honesty notes, pre-committed:
  - cycle-mean features are the crudest summary; faults that live in
    within-cycle transients (valve switching lag is the candidate) may
    be invisible at this granularity — if so, that is reported as a
    granularity finding, not smoothed over.
  - 'normal' for target X includes cycles where OTHER components are
    heavily degraded; detecting X's degradation against that
    background is the point, but it makes these four experiments
    non-comparable to single-fault benchmarks.

Usage::
    python -m tests.hydraulic.exp_hydraulic
"""

from __future__ import annotations

import numpy as np

from tests.multivariate.exp_deployability import _fit_auto
from tests.hydraulic.hydraulic_datasets import (STAGES, load_cycle_means,
                                      target_split)

LL_Q = 0.995          # designed clean flag rate 0.5% (frozen default)
SPLIT_FRAC = 0.6
REDUCE_DIMS = 16      # the §4.6 guardrail: PCA when d > 16


def build_floor(fit):
    """exp_frozen_transfer._ours, returning margin in fit-IQR units."""
    n_nest = int(0.6 * len(fit))
    model_part, floor_part = fit[:n_nest], fit[n_nest:]

    if fit.shape[1] > REDUCE_DIMS:
        from tests.baselines.mspc_baselines import MSPCModel
        m = MSPCModel().fit(model_part)
        proj = lambda A: m._scores_resid(A)[0]
    else:
        proj = lambda A: A

    g, k = _fit_auto(proj(model_part), 'full')
    ll_floor_part = g.score_samples(proj(floor_part))
    floor = float(np.quantile(ll_floor_part, 1.0 - LL_Q))
    iqr = float(np.subtract(*np.percentile(ll_floor_part, [75, 25]))) + 1e-12
    margin = lambda A: (floor - g.score_samples(proj(A))) / abs(iqr)
    return margin, k


def run_target(target: str, X, rng, label=''):
    normal_idx, degraded = target_split(target)
    idx = rng.permutation(normal_idx)
    n_fit = int(SPLIT_FRAC * len(idx))
    fit_idx, hold_idx = idx[:n_fit], idx[n_fit:]

    mu = X[fit_idx].mean(0)
    sd = X[fit_idx].std(0) + 1e-12
    z = lambda A: (A - mu) / sd

    margin, k = build_floor(z(X[fit_idx]))

    m_hold = margin(z(X[hold_idx]))
    far = float((m_hold > 0).mean())

    print(f"\n[{target}{label}]  normal={len(normal_idx)} cycles "
          f"(fit {n_fit} / holdout {len(hold_idx)}), K={k}")
    print(f"  held-out normal:   FAR {far:6.2%}  (designed 0.5%)")

    meds = []
    for stage in STAGES[target]:
        di = degraded[stage]
        if len(di) == 0:
            print(f"  stage {stage:>5g}: no stable cycles")
            continue
        m = margin(z(X[di]))
        det = float((m > 0).mean())
        med = float(np.median(m))
        meds.append(med)
        print(f"  stage {stage:>5g}: det {det:6.1%}   "
              f"median margin {med:8.1f} IQR   (n={len(di)})")
    mono = all(meds[i] < meds[i + 1] for i in range(len(meds) - 1))
    detected = all(m > 0 for m in meds)
    verdict = ('YES' if mono else 'NO') if detected else \
        'VACUOUS (stages not detected at median)'
    print(f"  margin monotone with degradation: "
          f"{verdict}  {['%.1f' % m for m in meds]}")
    return far, meds, mono


def main():
    print("=" * 72)
    print("HYDRAULIC RIG (UCI 447) — frozen support-floor path")
    print("  normal per target = target-nominal cycles; other components")
    print("  vary inside 'normal' (operating conditions -> regimes)")
    print("=" * 72)
    for features, d in (('mean', 17), ('meanstd', 34), ('seg6', 102),
                        ('shape', 68), ('phase12shape', 272)):
        X, _ = load_cycle_means(features=features)
        print(f"\n----- features: per-cycle {features}  (d={d}) -----")
        for target in STAGES:
            rng = np.random.default_rng(0)
            run_target(target, X, rng, label=f' {features}')


if __name__ == '__main__':
    main()
