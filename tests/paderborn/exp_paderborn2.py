"""Pre-registration #2 execution — hierarchical normal structure.

Implements doc/preregistrations/experiment_plan_paderborn2.md. Candidates A-E are floor
policies over ONE shared geometry (z-norm on fit healthy -> PCA 90% ->
GMM BIC auto-K, nested out-of-sample calibration part), so all five
share data, splits, scores, and evaluation functions by construction.
The d=27 adapter is untouched; no fault labels, fault frequencies, or
damage-specific features anywhere.

Shared split discipline:
  - rotating healthy folds as in the predecessor's H3;
  - primary fold (fit K001-K004 / unseen K005-K006) supplies all
    damage-side metrics;
  - recordings with index 1-4 per (bearing, condition) are the
    COMMISSIONING RESERVE: candidate E estimates unseen-bearing
    offsets there and NOTHING ELSE is evaluated there — unseen-healthy
    FAR for ALL candidates is measured on recordings 5-20 only, so
    every FAR is computed on the identical frame set.

Candidates (floor policies; severity_margin / alarm separated):
  A  global floor (baseline; reproduces the predecessor)
  B  component-conditional floor (per latent mixture component;
     components are NOT called operating regimes)
  C  known-condition conditional floor (shared geometry; ONLY the
     floor conditions on the operating-condition metadata)
  D  hierarchical between-bearing calibration: per-condition floor of
     the population envelope = min over construction bearings of the
     per-(bearing, condition) clean floor — condition effect and
     between-bearing layer separated, no unseen-bearing information
  E  commissioning offset: unseen bearing's healthy commissioning
     window (recordings 1-4) shifts the global floor by that unit's
     median clean-likelihood offset; damage-side severity is the
     shared-geometry margin (commissioning cannot be simulated for
     damaged bearings here — all their recordings are damaged;
     disclosed in the results)

Usage::
    python -m tests.paderborn.exp_paderborn2
"""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from tests.multivariate.exp_deployability import _fit_auto
from tests.baselines.mspc_baselines import MSPCModel
from tests.paderborn.paderborn_datasets import FULL_CONDITIONS, load_frames_full

HEALTHY = ['K001', 'K002', 'K003', 'K004', 'K005', 'K006']
FOLDS = [(['K001', 'K002', 'K003', 'K004'], ['K005', 'K006']),
         (['K003', 'K004', 'K005', 'K006'], ['K001', 'K002']),
         (['K001', 'K002', 'K005', 'K006'], ['K003', 'K004'])]
INNER_LADDER = {1: ['KI04', 'KI14', 'KI17', 'KI21'],
                2: ['KI18'], 3: ['KI16']}
OUTER_LADDER = {1: ['KA04', 'KA22'], 2: ['KA16']}
EXTENT1_REAL = ['KI04', 'KI14', 'KI17', 'KI21', 'KA04', 'KA22',
                'KA15', 'KA30', 'KB27']
Q = 0.005
N_BOOT = 800
COMMISSION_MAX_IDX = 4      # recordings 1-4 reserved for E


def _rec_index(rec_name: str) -> int:
    return int(rec_name.rsplit('_', 1)[1].split('.')[0])


class SharedGeometry:
    """One geometry per fold; every candidate reads its outputs."""

    def __init__(self, X, bearing, condition, rec, fit_bearings):
        self.fit_bearings = fit_bearings
        fit_m = np.isin(bearing, fit_bearings)
        self.mu = X[fit_m].mean(0)
        self.sd = X[fit_m].std(0) + 1e-12
        rng = np.random.default_rng(0)
        idx = np.where(fit_m)[0]
        recs = np.unique(rec[idx])
        rng.shuffle(recs)
        order = np.argsort([np.where(recs == r)[0][0] for r in rec[idx]])
        ordered = idx[order]
        n_nest = int(0.6 * len(ordered))
        model_idx, floor_idx = ordered[:n_nest], ordered[n_nest:]

        Zm = self._z(X[model_idx])
        self.pca = MSPCModel().fit(Zm)
        self.gmm, self.K = _fit_auto(self._proj(Zm), 'full')

        self.floor_ll = self.gmm.score_samples(self._proj(
            self._z(X[floor_idx])))
        self.floor_comp = self.gmm.predict(self._proj(
            self._z(X[floor_idx])))
        self.floor_cond = condition[floor_idx]
        self.floor_bear = bearing[floor_idx]
        self.iqr = abs(float(np.subtract(
            *np.percentile(self.floor_ll, [75, 25])))) + 1e-12
        self.global_floor = float(np.quantile(self.floor_ll, Q))

    def _z(self, A):
        return (A - self.mu) / self.sd

    def _proj(self, Z):
        return self.pca._scores_resid(Z)[0]

    def ll(self, A):
        return self.gmm.score_samples(self._proj(self._z(A)))

    def comp(self, A):
        return self.gmm.predict(self._proj(self._z(A)))


def _q_or_global(vals, fallback):
    return float(np.quantile(vals, Q)) if len(vals) >= 50 else fallback


class CandA:
    name = 'A global floor'
    calib_note = 'floor part only (shared)'

    def __init__(self, g: SharedGeometry, **kw):
        self.g = g

    def severity(self, A, cond, bear):
        return (self.g.global_floor - self.g.ll(A)) / self.g.iqr

    def alarm(self, A, cond, bear):
        return self.severity(A, cond, bear)


class CandB:
    name = 'B component-conditional floor'
    calib_note = 'floor part, per latent component'

    def __init__(self, g: SharedGeometry, **kw):
        self.g = g
        self.floors, self.iqrs = {}, {}
        for k in range(g.K):
            sel = g.floor_comp == k
            self.floors[k] = _q_or_global(g.floor_ll[sel], g.global_floor)
            self.iqrs[k] = (abs(float(np.subtract(*np.percentile(
                g.floor_ll[sel], [75, 25])))) + 1e-12
                if sel.sum() >= 50 else g.iqr)

    def severity(self, A, cond, bear):
        ll, comp = self.g.ll(A), self.g.comp(A)
        fl = np.array([self.floors[c] for c in comp])
        iq = np.array([self.iqrs[c] for c in comp])
        return (fl - ll) / iq

    alarm = severity


class CandC:
    name = 'C condition-conditional floor'
    calib_note = 'floor part, per known condition'

    def __init__(self, g: SharedGeometry, **kw):
        self.g = g
        self.floors = {c: _q_or_global(g.floor_ll[g.floor_cond == c],
                                       g.global_floor)
                       for c in FULL_CONDITIONS}

    def severity(self, A, cond, bear):
        ll = self.g.ll(A)
        fl = np.array([self.floors[c] for c in cond])
        return (fl - ll) / self.g.iqr          # shared IQR: common scale

    alarm = severity


class CandD:
    name = 'D hierarchical (population envelope)'
    calib_note = 'floor part, per (bearing x condition) cell, min-union'

    def __init__(self, g: SharedGeometry, **kw):
        self.g = g
        self.floors = {}
        for c in FULL_CONDITIONS:
            cell = []
            for b in g.fit_bearings:
                sel = (g.floor_cond == c) & (g.floor_bear == b)
                if sel.sum() >= 20:
                    cell.append(float(np.quantile(g.floor_ll[sel], Q)))
            self.floors[c] = min(cell) if cell else g.global_floor

    def severity(self, A, cond, bear):
        ll = self.g.ll(A)
        fl = np.array([self.floors[c] for c in cond])
        return (fl - ll) / self.g.iqr

    alarm = severity


class CandE:
    name = 'E commissioning offset'
    calib_note = 'floor part + 4 healthy recordings of the unseen unit'

    def __init__(self, g: SharedGeometry, X=None, bearing=None,
                 condition=None, rec=None, hold_bearings=None):
        self.g = g
        self.offsets = {}
        med_ref = float(np.median(g.floor_ll))
        for b in hold_bearings:
            comm = (bearing == b) & np.array(
                [_rec_index(r) <= COMMISSION_MAX_IDX for r in rec])
            self.offsets[b] = float(np.median(g.ll(X[comm]))) - med_ref

    def severity(self, A, cond, bear):
        # severity stays on the shared geometry (role separation)
        return (self.g.global_floor - self.g.ll(A)) / self.g.iqr

    def alarm(self, A, cond, bear):
        ll = self.g.ll(A)
        off = np.array([self.offsets.get(b, 0.0) for b in bear])
        return (self.g.global_floor + off - ll) / self.g.iqr


CANDIDATES = [CandA, CandB, CandC, CandD, CandE]


def _boot_ci(a, b, rng, n=N_BOOT):
    d = [np.median(rng.choice(a, len(a))) - np.median(rng.choice(b, len(b)))
         for _ in range(n)]
    return np.percentile(d, [2.5, 97.5])


def evaluate(cand, X, bearing, condition, rec, eval_healthy_m,
             rng) -> dict:
    out = {}
    # 1. unseen healthy FAR on the common eval set
    al = cand.alarm(X[eval_healthy_m], condition[eval_healthy_m],
                    bearing[eval_healthy_m])
    out['far'] = float((al > 0).mean())

    # damage-side (primary fold; all damaged frames)
    dam_m = ~np.isin(bearing, HEALTHY)
    al_d = cand.alarm(X[dam_m], condition[dam_m], bearing[dam_m])
    out['det_all'] = float((al_d > 0).mean())

    # 5. extent-1 real-damage absorption (alarm side)
    e1 = np.isin(bearing, EXTENT1_REAL)
    al_e1 = cand.alarm(X[e1], condition[e1], bearing[e1])
    out['absorb_e1'] = float((al_e1 <= 0).mean())

    # 2-4. H1 orderings on severity margin
    out['ladders'] = {}
    for lname, ladder in (('inner', INNER_LADDER), ('outer', OUTER_LADDER)):
        exts = sorted(ladder)
        n_ordered, n_pairs = 0, 0
        for c in FULL_CONDITIONS:
            for lo, hi in zip(exts[:-1], exts[1:]):
                a = cand.severity(
                    X[np.isin(bearing, ladder[hi]) & (condition == c)],
                    condition[np.isin(bearing, ladder[hi]) & (condition == c)],
                    bearing[np.isin(bearing, ladder[hi]) & (condition == c)])
                b = cand.severity(
                    X[np.isin(bearing, ladder[lo]) & (condition == c)],
                    condition[np.isin(bearing, ladder[lo]) & (condition == c)],
                    bearing[np.isin(bearing, ladder[lo]) & (condition == c)])
                ci = _boot_ci(a, b, rng)
                n_pairs += 1
                n_ordered += int(ci[0] > 0)
        per_b = []
        for e, bs in ladder.items():
            for b_ in bs:
                m = np.isin(bearing, [b_])
                per_b.append((e, float(np.median(
                    cand.severity(X[m], condition[m], bearing[m])))))
        rho = spearmanr([e for e, _ in per_b],
                        [v for _, v in per_b]).statistic
        out['ladders'][lname] = (n_ordered, n_pairs, float(rho))

    # 6. cross-condition scale comparability: per-condition IQR of the
    # severity margin on the clean calibration part (ratio max/min)
    g = cand.g
    iqrs = []
    # reconstruct calibration-part severity via stored floor_ll:
    # severity uses the candidate's own floors, so evaluate per cond
    for c in FULL_CONDITIONS:
        sel = g.floor_cond == c
        # approximate: severity of calibration frames = (floor-ll)/scale
        # computed through the candidate's alarm on stored ll is not
        # directly available; use per-condition IQR of margins on the
        # UNSEEN healthy eval set instead (same information, held out)
        selh = eval_healthy_m & (condition == c)
        sv = cand.severity(X[selh], condition[selh], bearing[selh])
        iqrs.append(abs(float(np.subtract(*np.percentile(sv, [75, 25])))))
    out['scale_ratio'] = max(iqrs) / (min(iqrs) + 1e-12)
    return out


def main():
    X, bearing, condition, rec = load_frames_full()
    rec_idx = np.array([_rec_index(r) for r in rec])
    eval_rec_m = rec_idx > COMMISSION_MAX_IDX   # common FAR eval set

    print("=" * 76)
    print("PRE-REGISTRATION #2 — hierarchical normal structure "
          "(doc/preregistrations/experiment_plan_paderborn2.md)")
    print(f"  frames {len(X)}  d={X.shape[1]}  "
          f"FAR eval set: recordings {COMMISSION_MAX_IDX + 1}-20 "
          "(identical for all candidates)")
    print("=" * 76)

    # -------- FAR across rotating folds, all candidates
    fold_fars = {C.name: [] for C in CANDIDATES}
    for fit_b, hold_b in FOLDS:
        g = SharedGeometry(X, bearing, condition, rec, fit_b)
        hold_eval = np.isin(bearing, hold_b) & eval_rec_m
        for C in CANDIDATES:
            cand = C(g, X=X, bearing=bearing, condition=condition,
                     rec=rec, hold_bearings=hold_b)
            al = cand.alarm(X[hold_eval], condition[hold_eval],
                            bearing[hold_eval])
            fold_fars[C.name].append(float((al > 0).mean()))

    # -------- full evaluation on the primary fold
    fit_b, hold_b = FOLDS[0]
    g = SharedGeometry(X, bearing, condition, rec, fit_b)
    print(f"\nprimary fold: fit {fit_b} -> unseen {hold_b}   "
          f"(shared geometry K={g.K})")
    hold_eval = np.isin(bearing, hold_b) & eval_rec_m

    rows = []
    for C in CANDIDATES:
        rng = np.random.default_rng(7)
        cand = C(g, X=X, bearing=bearing, condition=condition, rec=rec,
                 hold_bearings=hold_b)
        r = evaluate(cand, X, bearing, condition, rec, hold_eval, rng)
        r['name'] = C.name
        r['calib'] = C.calib_note
        r['far_folds'] = fold_fars[C.name]
        rows.append(r)

    print(f"\n{'candidate':<38} {'FAR(3 folds)':>22} {'det_all':>8} "
          f"{'absorbE1':>9} {'inner':>12} {'outer':>10} {'scale':>6}")
    for r in rows:
        ff = "/".join(f"{v:.1%}" for v in r['far_folds'])
        i = r['ladders']['inner']
        o = r['ladders']['outer']
        print(f"{r['name']:<38} {ff:>22} {r['det_all']:>8.1%} "
              f"{r['absorb_e1']:>9.1%} "
              f"{i[0]}/{i[1]} ρ{i[2]:+.2f}"
              f" {o[0]}/{o[1]} ρ{o[2]:+.2f} {r['scale_ratio']:>6.2f}")
    print("\ncalibration data per candidate:")
    for r in rows:
        print(f"  {r['name']:<38} {r['calib']}")


if __name__ == '__main__':
    main()
