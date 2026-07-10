"""Pre-registered #5 runner — graded physical severity on the hydraulic rig.

Implements doc/preregistrations/experiment_plan_hydraulic.md exactly
(protocol §1, hypotheses §2, evaluations §3). Registered confirmatory
validation: one fixed vocabulary (phase12shape, d=272) for all four
targets, five fixed split seeds {1..5} (the exploration's seed 0
excluded), Spearman + bootstrap-CI ordering statistics, pass/kill
decided by the >=4/5 (pass) / >=2/5 (kill) rule over seeds.

Detector mechanics are reused by import from the exploration runner
(tests/hydraulic/exp_hydraulic.build_floor) — the frozen support-floor
path, untouched: z-norm on fit split, PCA 90% for d>16, GMM BIC auto-K
full-cov, nested out-of-sample 0.5% likelihood floor; margin in
fit-side IQR units, margin > 0 = outside the floor.

Usage::
    python -m tests.hydraulic.exp_hydraulic_prereg
"""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from tests.hydraulic.exp_hydraulic import build_floor
from tests.hydraulic.hydraulic_datasets import (STAGES, load_cycle_means,
                                                target_split)

FEATURES = 'phase12shape'          # fixed, all targets (plan §1)
SEEDS = [1, 2, 3, 4, 5]            # fixed (plan §1); exploration seed 0 excluded
SPLIT_FRAC = 0.6                   # fixed (plan §1)
N_BOOT = 10_000                    # fixed (plan §1)
PASS_K, KILL_K = 4, 2              # >=4/5 pass, >=2/5 kill (plan §1)


def boot_median_diff_ci(a: np.ndarray, b: np.ndarray, rng) -> tuple:
    """Percentile-bootstrap 95% CI of median(b) - median(a)."""
    ra = np.median(rng.choice(a, (N_BOOT, len(a))), axis=1)
    rb = np.median(rng.choice(b, (N_BOOT, len(b))), axis=1)
    d = rb - ra
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def run_target_seed(target: str, X: np.ndarray, seed: int) -> dict:
    normal_idx, degraded = target_split(target)
    rng = np.random.default_rng(seed)
    idx = rng.permutation(normal_idx)
    n_fit = int(SPLIT_FRAC * len(idx))
    fit_idx, hold_idx = idx[:n_fit], idx[n_fit:]

    mu = X[fit_idx].mean(0)
    sd = X[fit_idx].std(0) + 1e-12
    z = lambda A: (A - mu) / sd

    margin, k = build_floor(z(X[fit_idx]))

    m_hold = margin(z(X[hold_idx]))
    res = {'far': float((m_hold > 0).mean()), 'K': k, 'stages': {}}

    ranks, margins = [], []
    for rank, stage in enumerate(STAGES[target]):
        m = margin(z(X[degraded[stage]]))
        res['stages'][stage] = {'det': float((m > 0).mean()),
                                'med': float(np.median(m)),
                                'n': len(m), 'm': m}
        ranks.append(np.full(len(m), rank))
        margins.append(m)
    res['rho'] = float(spearmanr(np.concatenate(ranks),
                                 np.concatenate(margins)).statistic)

    brng = np.random.default_rng(seed + 1000)
    stages = STAGES[target]
    res['adj_ci'] = [boot_median_diff_ci(res['stages'][stages[i]]['m'],
                                         res['stages'][stages[i + 1]]['m'],
                                         brng)
                     for i in range(len(stages) - 1)]
    return res


def tally(flags: list) -> str:
    n = sum(flags)
    return f"{n}/5 " + ("HOLDS" if n >= PASS_K else
                        "fails" if 5 - n >= KILL_K else "mixed")


def main():
    X, _ = load_cycle_means(features=FEATURES)
    print("=" * 76)
    print("PRE-REGISTRATION #5 — hydraulic rig, registered confirmatory run")
    print(f"  vocabulary {FEATURES} d={X.shape[1]}, seeds {SEEDS}, "
          f"split {SPLIT_FRAC}, bootstrap {N_BOOT}")
    print("=" * 76)

    results = {}
    for target in STAGES:
        results[target] = [run_target_seed(target, X, s) for s in SEEDS]
        stages = STAGES[target]
        print(f"\n[{target}]  stages {stages}")
        for s, r in zip(SEEDS, results[target]):
            det = " ".join(f"{r['stages'][st]['det']:6.1%}" for st in stages)
            med = " ".join(f"{r['stages'][st]['med']:+9.1f}" for st in stages)
            cis = " ".join(f"[{lo:+.1f},{hi:+.1f}]" for lo, hi in r['adj_ci'])
            print(f"  seed {s}: K={r['K']}  FAR {r['far']:6.2%}  "
                  f"det {det}  med {med}  rho {r['rho']:+.3f}  adjCI {cis}")

    # ---- verdict evaluation against plan §2 ------------------------------
    print("\n" + "=" * 76)
    print("VERDICT EVALUATION (plan §2; pass >=4/5 seeds, kill >=2/5 seeds)")
    print("=" * 76)

    def per_seed(target, fn):
        return [fn(r) for r in results[target]]

    # H1H cooler
    c = 'cooler'
    a = per_seed(c, lambda r: all(r['stages'][st]['det'] >= 0.95
                                  for st in STAGES[c]))
    b = per_seed(c, lambda r: (r['stages'][3.0]['med'] >
                               r['stages'][20.0]['med'] > 0)
                 and r['adj_ci'][0][0] > 0)
    d = per_seed(c, lambda r: r['rho'] > 0)
    rev = per_seed(c, lambda r: r['adj_ci'][0][1] < 0)
    print(f"H1H cooler: det>=95% both {tally(a)} | ordered+CI {tally(b)} | "
          f"rho>0 {tally(d)} | reversal-kill fired on {sum(rev)}/5")

    # H2H valve
    v = 'valve'
    a = per_seed(v, lambda r: r['rho'] > 0)
    b = per_seed(v, lambda r: (r['stages'][73.0]['med'] -
                               r['stages'][90.0]['med']) > 0)
    b_ci = per_seed(v, lambda r: boot_ci_severe_vs_mild(r, v)[0] > 0)
    cdet = per_seed(v, lambda r: r['stages'][73.0]['det'] >= 0.50)
    rev = per_seed(v, lambda r: boot_ci_severe_vs_mild(r, v)[1] < 0)
    print(f"H2H valve: rho>0 {tally(a)} | med(73)>med(90) {tally(b)} "
          f"| CI(73-90)>0 {tally(b_ci)} | det(73)>=50% {tally(cdet)} "
          f"| reversal-kill fired on {sum(rev)}/5")

    # H3H leak
    l = 'leak'
    a = per_seed(l, lambda r: all(r['stages'][st]['det'] >= 0.50
                                  for st in STAGES[l]))
    b = per_seed(l, lambda r: (r['stages'][2.0]['med'] >
                               r['stages'][1.0]['med'])
                 and r['adj_ci'][0][0] > 0)
    d = per_seed(l, lambda r: r['rho'] > 0)
    rev = per_seed(l, lambda r: r['adj_ci'][0][1] < 0)
    fars = [r['far'] for r in results[l]]
    print(f"H3H leak: det>=50% both {tally(a)} | ordered+CI {tally(b)} | "
          f"rho>0 {tally(d)} | reversal-kill fired on {sum(rev)}/5")
    print(f"H3H registered coverage measurement: healthy FAR per seed "
          f"{['%.2f%%' % (f * 100) for f in fars]} (design 0.5%)")

    # H4H accumulator (descriptive)
    ac = 'accumulator'
    lim = per_seed(ac, lambda r: all(r['stages'][st]['det'] < 0.50 and
                                     r['stages'][st]['med'] <= 0
                                     for st in STAGES[ac]))
    print(f"H4H accumulator: observability-limit expectation "
          f"(det<50% and med<=0, all stages) holds on {sum(lim)}/5 seeds")

    print("\nAudit: one vocabulary, one detector configuration, "
          "constants unchanged (plan §1).")


def boot_ci_severe_vs_mild(r: dict, target: str) -> tuple:
    """95% CI of med(severe) - med(mildest) for 3-stage targets (H2H)."""
    stages = STAGES[target]
    rng = np.random.default_rng(99)
    return boot_median_diff_ci(r['stages'][stages[0]]['m'],
                               r['stages'][stages[-1]]['m'], rng)


if __name__ == '__main__':
    main()
