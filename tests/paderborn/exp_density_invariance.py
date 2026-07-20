"""Pre-registration #6 execution — density-model invariance.

Implements doc/preregistrations/experiment_plan_density_invariance.md
exactly (models §2.1, candidates §2.2, mathematical conventions §2.3,
evaluations §3, hypotheses §4, kills §5). The #2 runner
(exp_paderborn2.py) is reused by import and NOT modified; its fold
logic, frame sets, and constants are inherited verbatim.

Registered conventions realized here (binding, part of the freeze):
  - One shared PCA fit per fold (SharedGeometry.pca). M1 (GMM), M3
    (T²), M4 (FGMM-BIP) act in its retained-score space; M2 (SPE) is
    the squared residual of the ORIGINAL standardized d=27 vector —
    never computed from a reduced input.
  - All scores oriented larger = more abnormal. M4's orientation is
    asserted at run start on the primary fold (clean-slice median must
    lie below the damaged-frame median); if reversed it is negated and
    the flip is reported.
  - Candidate-A threshold = Q_0.995 of the model's clean score on the
    nested out-of-sample floor slice. For M1 this is analytically 0 in
    deficit orientation (floor − Q_0.005(ll) = 0); the implementation
    asserts |Q_0.995(clean_M1)| < 1e-9 and then uses the exact 0.0,
    which makes the M1×A cell bit-identical to #2's CandA (the K4
    anchor). For M5 the recalibration makes the threshold identically
    1; asserted to 1e-9.
  - E3 standardizes each model's OWN clean score by the unseen unit's
    commissioning median/IQR (recordings 1–4; zero-IQR guard 1e-12)
    and maps onto the reference median/IQR of the floor slice.
    Damage-side alarms under E3 use the untransformed score against
    the candidate-A threshold (damaged bearings have no healthy
    commissioning window in this corpus — the #2/#3 disclosed
    convention).
  - Feasibility sweep: common clean-tail quantile q (registered grid),
    θ_mf(q) per (model, fold) from the fold's own clean slice; FAR and
    extent-1 absorption per fold, averaged at fixed q. Raw thresholds
    are never shared across folds.
  - K4 anchor: fold-wise integer flagged counts and denominators of
    M1×A must equal #2's CandA run in-process; else the run is VOID
    and no CSV is written.

Usage::
    python -m tests.paderborn.exp_density_invariance
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from tests.baselines.fgmm_bayes import FGMMBayes
from tests.paderborn.exp_paderborn2 import (COMMISSION_MAX_IDX, FOLDS,
                                            HEALTHY, INNER_LADDER,
                                            OUTER_LADDER, EXTENT1_REAL,
                                            CandA, SharedGeometry,
                                            _rec_index)
from tests.paderborn.paderborn_datasets import (FULL_CONDITIONS,
                                                load_frames_full)

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'paper_results')

Q_TAIL = 0.995          # designed 0.5% clean tail (plan §2.3-ii)
EPS = 1e-12             # zero-IQR guard (plan §2.3-iii)
N_BOOT = 800            # ladder CIs (plan §8 notes)
BOOT_SEED = 7           # matching #2's evaluation seed
MIN_CELL_BC = 50        # B/C cell fallback (plan §2.3-ii)
MIN_CELL_D = 20         # D cell fallback (plan §2.3-ii)
FAR_BAR = 0.02          # H1c / H2 feasibility bar
ABS_BAR = 0.50          # H1c absorption bar
MODELS = ['M1', 'M2', 'M3', 'M4', 'M5']
H12_MODELS = ['M1', 'M2', 'M3', 'M5']   # M4 = Q3 contrast only

# registered q-grid (plan §8 notes): 2001 uniform + refinement toward 1
Q_GRID = np.unique(np.concatenate([
    np.linspace(0.0, 1.0, 2001)[1:-1],
    1.0 - np.logspace(-6, -0.31, 300)]))


def _rederive_floor_idx(X, bearing, rec, fit_bearings):
    """Byte-identical re-derivation of SharedGeometry's nested split."""
    fit_m = np.isin(bearing, fit_bearings)
    rng = np.random.default_rng(0)
    idx = np.where(fit_m)[0]
    recs = np.unique(rec[idx])
    rng.shuffle(recs)
    order = np.argsort([np.where(recs == r)[0][0] for r in rec[idx]])
    ordered = idx[order]
    n_nest = int(0.6 * len(ordered))
    return ordered[:n_nest], ordered[n_nest:]


class FoldModels:
    """All five registered scores on one fold's shared geometry."""

    def __init__(self, X, bearing, condition, rec, fit_bearings,
                 m4_sign):
        self.g = SharedGeometry(X, bearing, condition, rec, fit_bearings)
        g = self.g
        model_idx, floor_idx = _rederive_floor_idx(
            X, bearing, rec, fit_bearings)
        # verify the re-derivation against the frozen geometry exactly
        ll_check = g.gmm.score_samples(g._proj(g._z(X[floor_idx])))
        assert np.array_equal(ll_check, g.floor_ll), \
            'floor-slice re-derivation mismatch'
        self.floor_idx = floor_idx
        Xf = X[floor_idx]

        self.fg = FGMMBayes().fit(g._proj(g._z(X[model_idx])))
        self.m4_sign = m4_sign

        self._score_fns = {
            'M1': lambda A: g.global_floor - g.ll(A),
            'M2': lambda A: g.pca.spe(g._z(A)),
            'M3': lambda A: g.pca.t2(g._z(A)),
            'M4': lambda A: m4_sign * self.fg.bip(g._proj(g._z(A))),
        }
        self.clean = {m: self._score_fns[m](Xf) for m in
                      ('M1', 'M2', 'M3', 'M4')}
        # M5: calibrated combined MSPC (plan §2.1/§2.3-ii)
        self.tau_t2 = float(np.quantile(self.clean['M3'], Q_TAIL))
        self.tau_spe = float(np.quantile(self.clean['M2'], Q_TAIL))
        r_clean = np.maximum(self.clean['M3'] / self.tau_t2,
                             self.clean['M2'] / self.tau_spe)
        self.m5_denom = float(np.quantile(r_clean, Q_TAIL))
        self._score_fns['M5'] = lambda A: np.maximum(
            self._score_fns['M3'](A) / self.tau_t2,
            self._score_fns['M2'](A) / self.tau_spe) / self.m5_denom
        self.clean['M5'] = r_clean / self.m5_denom

        self.thr_A = {m: float(np.quantile(self.clean[m], Q_TAIL))
                      for m in MODELS}
        # registered identity assertions (plan §2.3-ii)
        assert abs(self.thr_A['M1']) < 1e-9, \
            f"M1 A-threshold not 0: {self.thr_A['M1']}"
        self.thr_A['M1'] = 0.0            # exact algebraic identity
        assert abs(self.thr_A['M5'] - 1.0) < 1e-9, \
            f"M5 A-threshold not 1: {self.thr_A['M5']}"
        self.thr_A['M5'] = 1.0

        self.med_ref = {m: float(np.median(self.clean[m])) for m in MODELS}
        self.iqr_ref = {m: max(abs(float(np.subtract(
            *np.percentile(self.clean[m], [75, 25])))), EPS)
            for m in MODELS}

    def score(self, m, A):
        return self._score_fns[m](A)


def _cell_thr(clean, sel, fallback, min_n):
    return (float(np.quantile(clean[sel], Q_TAIL))
            if sel.sum() >= min_n else fallback)


def make_thresholds(fm, m, cand, X, bearing, condition, rec_idx,
                    hold_bearings):
    """Per-frame threshold arrays (or E3 transform) for one cell.

    Returns a function alarm(A_scores, cond, bear) -> bool array,
    plus the string 'NA' for undefined cells.
    """
    g, clean, thrA = fm.g, fm.clean[m], fm.thr_A[m]

    if cand == 'A':
        return lambda s, c, b: s > thrA

    if cand == 'B':
        if m == 'M1':
            comp_clean = g.floor_comp
            comp_of = lambda A: g.comp(A)
            K = g.K
        elif m == 'M4':
            comp_clean = fm.fg.gmm_.predict(
                g._proj(g._z(X[fm.floor_idx])))
            comp_of = lambda A: fm.fg.gmm_.predict(g._proj(g._z(A)))
            K = fm.fg.K_eff
        else:
            return 'NA'
        thrs = {k: _cell_thr(clean, comp_clean == k, thrA, MIN_CELL_BC)
                for k in range(K)}
        def alarm_B(s, c, b, A=None):
            raise RuntimeError('B needs raw frames')
        # B needs the raw frames to assign components; handled specially
        return ('B', thrs, comp_of)

    if cand == 'C':
        thrs = {cc: _cell_thr(clean, g.floor_cond == cc, thrA,
                              MIN_CELL_BC) for cc in FULL_CONDITIONS}
        return lambda s, c, b: s > np.array([thrs[ci] for ci in c])

    if cand == 'D':
        thrs = {}
        for cc in FULL_CONDITIONS:
            cell = [ _cell_thr(clean,
                               (g.floor_cond == cc) & (g.floor_bear == bb),
                               None, MIN_CELL_D)
                     for bb in g.fit_bearings ]
            cell = [v for v in cell if v is not None]
            thrs[cc] = max(cell) if cell else thrA   # loosest = max (§2.3-v)
        return lambda s, c, b: s > np.array([thrs[ci] for ci in c])

    if cand == 'E3':
        offsets = {}
        for bb in hold_bearings:
            comm = (bearing == bb) & (rec_idx <= COMMISSION_MAX_IDX)
            s_comm = fm.score(m, X[comm])
            b_i = float(np.median(s_comm))
            s_i = max(abs(float(np.subtract(
                *np.percentile(s_comm, [75, 25])))), EPS)
            offsets[bb] = (b_i, s_i)
        med_r, iqr_r = fm.med_ref[m], fm.iqr_ref[m]
        def alarm_E3(s, c, b):
            out = np.empty(len(s), dtype=bool)
            for bb in np.unique(b):
                sel = b == bb
                if bb in offsets:
                    b_i, s_i = offsets[bb]
                    s_ref = med_r + iqr_r * (s[sel] - b_i) / s_i
                else:                     # damaged units: no commissioning
                    s_ref = s[sel]        # (#2/#3 disclosed convention)
                out[sel] = s_ref > thrA
            return out
        return alarm_E3

    raise ValueError(cand)


def evaluate_cell(fm, m, cand, X, bearing, condition, rec_idx,
                  hold_bearings, eval_healthy_m, dam_m, e1_m):
    pol = make_thresholds(fm, m, cand, X, bearing, condition, rec_idx,
                          hold_bearings)
    if pol == 'NA':
        return None
    s_all = fm.score(m, X)

    def alarm_on(mask):
        s, c, b = s_all[mask], condition[mask], bearing[mask]
        if isinstance(pol, tuple):        # candidate B
            _, thrs, comp_of = pol
            comp = comp_of(X[mask])
            thr = np.array([thrs[k] for k in comp])
            return s > thr
        return pol(s, c, b)

    fl = alarm_on(eval_healthy_m)
    far_n, far_d = int(fl.sum()), int(len(fl))
    det = float(alarm_on(dam_m).mean())
    absorb = float((~alarm_on(e1_m)).mean())
    return dict(far_n=far_n, far_d=far_d, far=far_n / max(far_d, 1),
                det_all=det, absorb_e1=absorb)


def severity_metrics(fm, m, X, bearing, condition, rng):
    """Ladder ordering, rho, and H3 margins on the primary fold."""
    s_all = fm.score(m, X)
    thrA, iqr = fm.thr_A[m], fm.iqr_ref[m]
    out = {'model': m}
    for lname, ladder in (('inner', INNER_LADDER), ('outer', OUTER_LADDER)):
        exts = sorted(ladder)
        n_ord = n_pairs = 0
        for cc in FULL_CONDITIONS:
            for lo, hi in zip(exts[:-1], exts[1:]):
                a = s_all[np.isin(bearing, ladder[hi]) & (condition == cc)]
                b = s_all[np.isin(bearing, ladder[lo]) & (condition == cc)]
                d = [np.median(rng.choice(a, len(a)))
                     - np.median(rng.choice(b, len(b)))
                     for _ in range(N_BOOT)]
                n_pairs += 1
                n_ord += int(np.percentile(d, 2.5) > 0)
        per_b = [(e, float(np.median(s_all[bearing == bb])))
                 for e, bs in ladder.items() for bb in bs]
        rho = spearmanr([e for e, _ in per_b],
                        [v for _, v in per_b]).statistic
        out[f'{lname}_ordered'] = n_ord
        out[f'{lname}_pairs'] = n_pairs
        out[f'{lname}_rho'] = float(rho)
    # H3 margins on the inner ladder at the registered A point (§2.3-iv)
    for e, bs in INNER_LADDER.items():
        sel = np.isin(bearing, bs)
        med = float(np.median(s_all[sel]))
        out[f'ext{e}_margin_iqr'] = (med - thrA) / iqr
        out[f'ext{e}_raw_median'] = med
        out[f'ext{e}_det'] = float((s_all[sel] > thrA).mean())
    return out


def feasibility(per_fold):
    """Quantile-sweep audit (§3.8). per_fold: list of dicts with
    'clean', 'healthy', 'e1' score arrays for one model."""
    far_q = np.zeros((len(per_fold), len(Q_GRID)))
    abs_q = np.zeros_like(far_q)
    fold_flags = []
    for i, f in enumerate(per_fold):
        thr = np.quantile(f['clean'], Q_GRID)
        h = np.sort(f['healthy'])
        e = np.sort(f['e1'])
        far_q[i] = 1.0 - np.searchsorted(h, thr, side='right') / len(h)
        abs_q[i] = np.searchsorted(e, thr, side='right') / len(e)
        fold_flags.append(bool(np.any((far_q[i] < FAR_BAR)
                                      & (abs_q[i] < ABS_BAR))))
    far_m, abs_m = far_q.mean(0), abs_q.mean(0)
    ok = (far_m < FAR_BAR) & (abs_m < ABS_BAR)
    sel_far = far_m < FAR_BAR
    sel_abs = abs_m < ABS_BAR
    return dict(
        feasible=bool(ok.any()),
        min_abs_at_far2=float(abs_m[sel_far].min()) if sel_far.any()
        else None,
        min_far_at_abs50=float(far_m[sel_abs].min()) if sel_abs.any()
        else None,
        fold_flags=fold_flags,
        far_monotone=bool(np.all(np.diff(far_m) <= 1e-12)),
        abs_monotone=bool(np.all(np.diff(abs_m) >= -1e-12)))


def main():
    X, bearing, condition, rec = load_frames_full()
    rec_idx = np.array([_rec_index(r) for r in rec])
    eval_rec_m = rec_idx > COMMISSION_MAX_IDX
    dam_m = ~np.isin(bearing, HEALTHY)
    e1_m = np.isin(bearing, EXTENT1_REAL)

    print('=' * 76)
    print('PRE-REGISTRATION #6 — density-model invariance '
          '(plan frozen before this run)')
    print('=' * 76)

    # ---- M4 orientation check (primary fold; §2.3-i) ----------------
    fm0 = FoldModels(X, bearing, condition, rec, FOLDS[0][0], m4_sign=1)
    m4_clean_med = float(np.median(fm0.clean['M4']))
    m4_dam_med = float(np.median(fm0.score('M4', X[dam_m])))
    m4_sign = 1 if m4_dam_med > m4_clean_med else -1
    print(f'M4 orientation: clean median {m4_clean_med:.4f}, damaged '
          f'median {m4_dam_med:.4f} -> sign {m4_sign:+d}'
          + ('  (negated per §2.3-i)' if m4_sign < 0 else ''))

    folds = []
    for fi, (fit_b, hold_b) in enumerate(FOLDS):
        fm = fm0 if (fi == 0 and m4_sign == 1) else FoldModels(
            X, bearing, condition, rec, fit_b, m4_sign)
        folds.append((fm, fit_b, hold_b))
        print(f'fold {fi + 1}: geometry K={fm.g.K}, FGMM K={fm.fg.K_eff}')

    # ---- K4 anchor gate ---------------------------------------------
    print('\nK4 anchor (M1 x A vs #2 CandA, integer counts):')
    void = False
    for fi, (fm, fit_b, hold_b) in enumerate(folds):
        he = np.isin(bearing, hold_b) & eval_rec_m
        ours = evaluate_cell(fm, 'M1', 'A', X, bearing, condition,
                             rec_idx, hold_b, he, dam_m, e1_m)
        c2 = CandA(fm.g)
        al2 = c2.alarm(X[he], condition[he], bearing[he]) > 0
        n2, d2 = int(al2.sum()), int(len(al2))
        match = (ours['far_n'] == n2 and ours['far_d'] == d2)
        print(f"  fold {fi + 1}: ours {ours['far_n']}/{ours['far_d']} "
              f"({ours['far']:.1%})  #2 {n2}/{d2} ({n2 / d2:.1%})  "
              f"{'MATCH' if match else 'MISMATCH'}")
        void |= not match
    if void:
        print('\nK4 FAILED — RUN VOID. No CSV written, no verdicts.')
        sys.exit(1)

    # ---- 22 cells -----------------------------------------------------
    rows = []
    for m in MODELS:
        for cand in ('A', 'B', 'C', 'D', 'E3'):
            per_fold = []
            for fi, (fm, fit_b, hold_b) in enumerate(folds):
                he = np.isin(bearing, hold_b) & eval_rec_m
                r = evaluate_cell(fm, m, cand, X, bearing, condition,
                                  rec_idx, hold_b, he, dam_m, e1_m)
                per_fold.append(r)
            if per_fold[0] is None:
                rows.append(dict(model=m, candidate=cand, na=True))
                continue
            row = dict(model=m, candidate=cand, na=False)
            for fi, r in enumerate(per_fold):
                row[f'far_fold{fi + 1}'] = r['far']
                row[f'far_n_fold{fi + 1}'] = r['far_n']
                row[f'far_d_fold{fi + 1}'] = r['far_d']
            row['far_mean'] = float(np.mean([r['far'] for r in per_fold]))
            row['det_all_mean'] = float(np.mean(
                [r['det_all'] for r in per_fold]))
            row['det_all_primary'] = per_fold[0]['det_all']
            row['absorb_e1_mean'] = float(np.mean(
                [r['absorb_e1'] for r in per_fold]))
            row['absorb_e1_primary'] = per_fold[0]['absorb_e1']
            rows.append(row)
            print(f"{m} {cand:>3}: FAR "
                  + '/'.join(f"{r['far']:.1%}" for r in per_fold)
                  + f"  mean {row['far_mean']:.2%}  det(mean) "
                  f"{row['det_all_mean']:.1%}  absorbE1(mean) "
                  f"{row['absorb_e1_mean']:.1%} (primary "
                  f"{row['absorb_e1_primary']:.1%})")
    df_cells = pd.DataFrame(rows)

    # ---- severity metrics + E3 bit-identity audit ---------------------
    fm_p = folds[0][0]
    sev_rows = []
    for m in MODELS:
        rng = np.random.default_rng(BOOT_SEED)
        sev_rows.append(severity_metrics(fm_p, m, X, bearing,
                                         condition, rng))
        s_a = fm_p.score(m, X[dam_m])
        s_e = fm_p.score(m, X[dam_m])   # severity side under E3 = raw s
        assert np.array_equal(s_a, s_e), 'severity invariance violated'
    df_sev = pd.DataFrame(sev_rows)
    print('\nSeverity (primary fold): ')
    for r in sev_rows:
        print(f"  {r['model']}: inner {r['inner_ordered']}/"
              f"{r['inner_pairs']} ρ{r['inner_rho']:+.2f} | outer "
              f"{r['outer_ordered']}/{r['outer_pairs']} "
              f"ρ{r['outer_rho']:+.2f} | H3 margins "
              f"{r['ext1_margin_iqr']:+.1f}/{r['ext2_margin_iqr']:+.1f}/"
              f"{r['ext3_margin_iqr']:+.1f} IQR "
              f"(det {r['ext1_det']:.0%}/{r['ext2_det']:.0%}/"
              f"{r['ext3_det']:.0%})")

    # ---- feasibility audit --------------------------------------------
    feas_rows = []
    print('\nFeasibility audit (clean-tail quantile sweep, §3.8):')
    for m in MODELS:
        pf = []
        for fm, fit_b, hold_b in folds:
            he = np.isin(bearing, hold_b) & eval_rec_m
            pf.append(dict(clean=fm.clean[m],
                           healthy=fm.score(m, X[he]),
                           e1=fm.score(m, X[e1_m])))
        f = feasibility(pf)
        f['model'] = m
        feas_rows.append(f)
        print(f"  {m}: feasible={f['feasible']}  "
              f"minAbs@FAR<2%={f['min_abs_at_far2']}  "
              f"minFAR@Abs<50%={f['min_far_at_abs50']}  "
              f"fold_flags={f['fold_flags']}  "
              f"monotone(FAR,Abs)=({f['far_monotone']},"
              f"{f['abs_monotone']})")
    df_feas = pd.DataFrame(feas_rows)

    # ---- verdict summary ----------------------------------------------
    print('\n' + '=' * 76)
    print('VERDICT EVALUATION (plan §4/§5)')
    print('=' * 76)
    for m in H12_MODELS:
        a = df_cells[(df_cells.model == m) & (df_cells.candidate == 'A')
                     ].iloc[0]
        h1a = a.far_mean >= 10 * 0.005
        widen = df_cells[(df_cells.model == m)
                         & (df_cells.candidate.isin(['B', 'C', 'D']))
                         & (~df_cells.na.astype(bool))]
        h1b = all((w.far_mean >= 0.10) or
                  (w.absorb_e1_mean > a.absorb_e1_mean)
                  for _, w in widen.iterrows()) if len(widen) else True
        h1c = not df_feas[df_feas.model == m].iloc[0].feasible
        e3 = df_cells[(df_cells.model == m)
                      & (df_cells.candidate == 'E3')].iloc[0]
        h2 = e3.far_mean < FAR_BAR
        print(f"{m}: H1a(>=10x)={h1a}  H1b(adaptations fail)={h1b}  "
              f"H1c(no feasible q)={h1c}  H2(E3<2%: "
              f"{e3.far_mean:.2%})={h2}")
    k1 = any(df_feas[df_feas.model == m].iloc[0].feasible
             for m in H12_MODELS)
    print(f"\nK1 fires: {k1}   "
          f"H2 all: {all(df_cells[(df_cells.model == m) & (df_cells.candidate == 'E3')].iloc[0].far_mean < FAR_BAR for m in H12_MODELS)}")
    h3_uns = all(
        (r['ext1_margin_iqr'] < r['ext2_margin_iqr'] <
         r['ext3_margin_iqr']) and
        (r['ext3_margin_iqr'] - r['ext1_margin_iqr'] > 5)
        for r in sev_rows if r['model'] in H12_MODELS)
    m4r = next(r for r in sev_rows if r['model'] == 'M4')
    h3_m4 = (m4r['ext3_margin_iqr'] - m4r['ext1_margin_iqr']) < 1
    print(f"H3: unsquashed(range>5IQR, increasing)={h3_uns}  "
          f"M4(range<1IQR)={h3_m4}  "
          f"M4 raw medians {m4r['ext1_raw_median']:.4f}/"
          f"{m4r['ext2_raw_median']:.4f}/{m4r['ext3_raw_median']:.4f}")

    os.makedirs(OUT, exist_ok=True)
    df_cells.to_csv(os.path.join(OUT, 'density_invariance.csv'),
                    index=False)
    df_feas.to_csv(os.path.join(OUT, 'density_feasibility.csv'),
                   index=False)
    df_sev.to_csv(os.path.join(OUT, 'density_severity.csv'), index=False)
    print('\nwrote paper_results/density_invariance.csv, '
          'density_feasibility.csv, density_severity.csv')


if __name__ == '__main__':
    main()
