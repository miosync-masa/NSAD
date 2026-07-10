"""Pre-registration #3 execution — asset-specific alarm calibration.

Implements doc/preregistrations/experiment_plan_paderborn3.md. Every candidate operates
on the ALARM side of the same shared geometry (reused verbatim from
tests/paderborn/exp_paderborn2.SharedGeometry); the severity margin is the
shared global-floor margin for all candidates by construction, and the
severity-side audit (H1 12/12, Spearman rho) is computed once on that
shared margin and reported as the standing qualification.

Registered frame conventions (§1 of the plan):
  commissioning reserve = recordings 1-12 per (bearing, condition)
  FAR eval set          = recordings 13-20 of unseen bearings,
                          identical for every candidate/ladder point
  damaged units carry NO commissioning (no healthy period exists in
  this cross-sectional data): their alarm sits at the uncommissioned
  shared floor — det_all and alarm-side absorption are therefore
  common to the E-family, disclosed.

Candidates (all alarm-side only):
  E0  per-unit global scalar offset, commissioning = 4 recordings/cond
  E1  E0's ladder: 1 / 2 / 4 / 8 / 12 recordings per condition
  E2  condition-specific offsets shrunk toward the unit scalar,
      w_c = n_c / (n_c + 128)  (n0 fixed in the pre-registration)
  E3  location + scale: unit ll standardized by commissioning
      median/IQR, mapped to the reference scale, global floor
  E4  E3 + conservative per-unit tail: floor_i = lower bootstrap 95%
      confidence bound of the 0.5% quantile of the unit's
      standardized commissioning ll (1000 resamples)

Declared before execution (lengths unspecified by the plan for E2-E4):
E2/E3/E4 run at BOTH 4 recordings (E0 comparability) and 8 recordings
(the pass-bar cost ceiling).

Usage::
    python -m tests.paderborn.exp_paderborn3
"""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from tests.paderborn.exp_paderborn2 import (FOLDS, HEALTHY, INNER_LADDER,
                                  OUTER_LADDER, N_BOOT, SharedGeometry,
                                  _boot_ci, _rec_index)
from tests.paderborn.paderborn_datasets import FULL_CONDITIONS, load_frames_full

COMMISSION_RESERVE = 12      # recordings 1-12
EVAL_MIN_IDX = 13            # FAR eval on recordings 13-20
Q = 0.005
N0_SHRINK = 128              # fixed in the pre-registration
LADDER = [1, 2, 4, 8, 12]
EXTENT1_REAL = ['KI04', 'KI14', 'KI17', 'KI21', 'KA04', 'KA22',
                'KA15', 'KA30', 'KB27']


def _comm_mask(bearing, rec_idx, b, n_rec):
    return (bearing == b) & (rec_idx <= n_rec)


class AlarmE0:
    """Per-unit global scalar offset (the #2 mechanism)."""

    def __init__(self, g, X, bearing, condition, rec_idx, hold_b,
                 n_rec=4):
        self.g = g
        self.n_rec = n_rec
        med_ref = float(np.median(g.floor_ll))
        self.off = {}
        for b in hold_b:
            m = _comm_mask(bearing, rec_idx, b, n_rec)
            self.off[b] = float(np.median(g.ll(X[m]))) - med_ref

    def margin(self, A, cond, bear):
        ll = self.g.ll(A)
        off = np.array([self.off.get(b, 0.0) for b in bear])
        return (self.g.global_floor + off - ll) / self.g.iqr


class AlarmE2:
    """Condition-specific offsets shrunk toward the unit scalar."""

    def __init__(self, g, X, bearing, condition, rec_idx, hold_b,
                 n_rec=4):
        self.g = g
        self.n_rec = n_rec
        med_ref = float(np.median(g.floor_ll))
        med_ref_c = {c: float(np.median(g.floor_ll[g.floor_cond == c]))
                     for c in FULL_CONDITIONS}
        self.off = {}
        for b in hold_b:
            m = _comm_mask(bearing, rec_idx, b, n_rec)
            g_off = float(np.median(g.ll(X[m]))) - med_ref
            for c in FULL_CONDITIONS:
                mc = m & (condition == c)
                n_c = int(mc.sum())
                if n_c:
                    raw = float(np.median(g.ll(X[mc]))) - med_ref_c[c]
                    w = n_c / (n_c + N0_SHRINK)
                    self.off[(b, c)] = w * raw + (1 - w) * g_off
                else:
                    self.off[(b, c)] = g_off

    def margin(self, A, cond, bear):
        ll = self.g.ll(A)
        off = np.array([self.off.get((b, c), 0.0)
                        for b, c in zip(bear, cond)])
        return (self.g.global_floor + off - ll) / self.g.iqr


class AlarmE3:
    """Location + scale standardization to the reference scale."""

    def __init__(self, g, X, bearing, condition, rec_idx, hold_b,
                 n_rec=4):
        self.g = g
        self.n_rec = n_rec
        self.med_ref = float(np.median(g.floor_ll))
        self.iqr_ref = g.iqr
        self.loc, self.scl = {}, {}
        for b in hold_b:
            m = _comm_mask(bearing, rec_idx, b, n_rec)
            ll = g.ll(X[m])
            self.loc[b] = float(np.median(ll))
            self.scl[b] = (abs(float(np.subtract(
                *np.percentile(ll, [75, 25])))) + 1e-12)

    def _std_ll(self, A, bear):
        ll = self.g.ll(A)
        loc = np.array([self.loc.get(b, self.med_ref) for b in bear])
        scl = np.array([self.scl.get(b, self.iqr_ref) for b in bear])
        return (ll - loc) / scl * self.iqr_ref + self.med_ref

    def margin(self, A, cond, bear):
        return (self.g.global_floor - self._std_ll(A, bear)) / self.iqr_ref


class AlarmE4(AlarmE3):
    """E3 + conservative per-unit tail floor (bootstrap lower CB)."""

    def __init__(self, g, X, bearing, condition, rec_idx, hold_b,
                 n_rec=4, n_boot=1000, seed=11):
        super().__init__(g, X, bearing, condition, rec_idx, hold_b,
                         n_rec=n_rec)
        rng = np.random.default_rng(seed)
        self.floor_i = {}
        for b in hold_b:
            m = _comm_mask(bearing, rec_idx, b, n_rec)
            llb = self._std_ll(X[m], bearing[m])
            qs = [np.quantile(rng.choice(llb, len(llb)), Q)
                  for _ in range(n_boot)]
            self.floor_i[b] = float(np.percentile(qs, 5))   # lower CB

    def margin(self, A, cond, bear):
        llp = self._std_ll(A, bear)
        fl = np.array([self.floor_i.get(b, self.g.global_floor)
                       for b in bear])
        return (fl - llp) / self.iqr_ref


def severity_audit(g, X, bearing, condition):
    """H1 on the shared severity margin (common to ALL candidates)."""
    sev = lambda A: (g.global_floor - g.ll(A)) / g.iqr
    rng = np.random.default_rng(7)
    out = {}
    for name, ladder in (('inner', INNER_LADDER), ('outer', OUTER_LADDER)):
        exts = sorted(ladder)
        n_ord, n_pairs = 0, 0
        for c in FULL_CONDITIONS:
            for lo, hi in zip(exts[:-1], exts[1:]):
                a = sev(X[np.isin(bearing, ladder[hi]) & (condition == c)])
                b = sev(X[np.isin(bearing, ladder[lo]) & (condition == c)])
                ci = _boot_ci(a, b, rng)
                n_pairs += 1
                n_ord += int(ci[0] > 0)
        per_b = [(e, float(np.median(sev(X[bearing == b_]))))
                 for e, bs in ladder.items() for b_ in bs]
        rho = spearmanr([e for e, _ in per_b],
                        [v for _, v in per_b]).statistic
        out[name] = (n_ord, n_pairs, float(rho))
    return out


def main():
    X, bearing, condition, rec = load_frames_full()
    rec_idx = np.array([_rec_index(r) for r in rec])
    eval_m = rec_idx >= EVAL_MIN_IDX

    print("=" * 76)
    print("PRE-REGISTRATION #3 — asset-specific alarm calibration "
          "(doc/preregistrations/experiment_plan_paderborn3.md)")
    print(f"  commissioning reserve: recordings 1-{COMMISSION_RESERVE}; "
          f"FAR eval: recordings {EVAL_MIN_IDX}-20 (identical for all)")
    print("=" * 76)

    # ---- severity audit (shared margin; the standing qualification)
    g0 = SharedGeometry(X, bearing, condition, rec, FOLDS[0][0])
    aud = severity_audit(g0, X, bearing, condition)
    dam_m = ~np.isin(bearing, HEALTHY)
    sev0 = (g0.global_floor - g0.ll(X[dam_m])) / g0.iqr
    e1_m = np.isin(bearing, EXTENT1_REAL)
    sev_e1 = (g0.global_floor - g0.ll(X[e1_m])) / g0.iqr
    print(f"\nSeverity audit (shared margin, common to every candidate):")
    print(f"  inner {aud['inner'][0]}/{aud['inner'][1]} "
          f"ρ{aud['inner'][2]:+.2f}   outer {aud['outer'][0]}/"
          f"{aud['outer'][1]} ρ{aud['outer'][2]:+.2f}")
    print(f"  det_all {float((sev0 > 0).mean()):.1%}   "
          f"severity-side E1 absorption {float((sev_e1 <= 0).mean()):.1%}"
          f"   (E-family alarm side for damaged units = same, "
          "no commissioning exists — disclosed)")

    # ---- FAR per fold for each candidate configuration
    configs = ([(f'E0/E1 scalar n={n}', AlarmE0, {'n_rec': n})
                for n in LADDER]
               + [(f'E2 shrunk-cond n={n}', AlarmE2, {'n_rec': n})
                  for n in (4, 8)]
               + [(f'E3 loc+scale n={n}', AlarmE3, {'n_rec': n})
                  for n in (4, 8)]
               + [(f'E4 +cons.tail n={n}', AlarmE4, {'n_rec': n})
                  for n in (4, 8)])

    results = {name: [] for name, _, _ in configs}
    for fit_b, hold_b in FOLDS:
        g = SharedGeometry(X, bearing, condition, rec, fit_b)
        he = np.isin(bearing, hold_b) & eval_m
        for name, cls, kw in configs:
            cand = cls(g, X, bearing, condition, rec_idx, hold_b, **kw)
            mm = cand.margin(X[he], condition[he], bearing[he])
            results[name].append(float((mm > 0).mean()))

    print(f"\n{'configuration':<24} {'FAR fold1':>10} {'fold2':>8} "
          f"{'fold3':>8} {'mean':>8}")
    for name, _, _ in configs:
        f = results[name]
        print(f"{name:<24} {f[0]:>10.2%} {f[1]:>8.2%} {f[2]:>8.2%} "
              f"{np.mean(f):>8.2%}")


if __name__ == '__main__':
    main()
