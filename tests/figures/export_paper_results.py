"""Publication build step — machine-readable results snapshot.

Re-executes the five pre-registered computations by importing the
frozen runners' components (no runner file is modified; no constant,
seed, split, or evaluation changes anywhere) and writes the results
that the runners print to stdout into paper_results/ as CSV/NPZ, plus
a manifest.json that records provenance and verifies key exported
statistics against the registered numbers in the plan documents.

This is a build step, not an experiment: every number here is the
deterministic output of the already-registered computation.

Outputs (paper_results/):
    paderborn_severity.csv          #1 per-bearing x condition margins
    paderborn_support_candidates.csv#2 candidates A-E full table
    paderborn_commissioning.csv     #3 E0-E4 ladder/fold FAR table
    ims_trajectories.npz            #4 per-snapshot median-margin
                                    trajectories (+ E3 fleet variant)
    ims_summary.csv                 #4 per-bearing summary table
    milling_wear.csv                #4-M per-run margin vs VB + rho
    hydraulic_seed_stage.csv        #5 per target x seed x stage
    hydraulic_seed_summary.csv      #5 per target x seed (FAR, rho, CIs)
    manifest.json                   provenance + verification block

Usage::
    python -m tests.figures.export_paper_results             # all
    python -m tests.figures.export_paper_results hydraulic   # subset
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'paper_results')

# ------------------------------------------------------------------ registry
# Ground-truth labels fixed in experiment_plan_paderborn.md §0.
PADERBORN_META = {
    # bearing: (ring, extent, damage kind)
    **{b: ('healthy', 0, 'healthy') for b in
       ['K001', 'K002', 'K003', 'K004', 'K005', 'K006']},
    'KA01': ('outer', 1, 'artificial EDM'),
    'KA03': ('outer', 2, 'artificial engraver'),
    'KA05': ('outer', 1, 'artificial engraver'),
    'KA06': ('outer', 2, 'artificial engraver'),
    'KA07': ('outer', 1, 'artificial drill'),
    'KA08': ('outer', 2, 'artificial drill'),
    'KA09': ('outer', 2, 'artificial drill'),
    'KI01': ('inner', 1, 'artificial EDM'),
    'KI03': ('inner', 1, 'artificial engraver'),
    'KI05': ('inner', 1, 'artificial engraver'),
    'KI07': ('inner', 2, 'artificial engraver'),
    'KI08': ('inner', 2, 'artificial engraver'),
    'KA04': ('outer', 1, 'real fatigue pitting'),
    'KA22': ('outer', 1, 'real fatigue pitting'),
    'KA16': ('outer', 2, 'real fatigue pitting'),
    'KA15': ('outer', 1, 'real indentation'),
    'KA30': ('outer', 1, 'real indentation'),
    'KI04': ('inner', 1, 'real fatigue pitting'),
    'KI14': ('inner', 1, 'real fatigue pitting'),
    'KI17': ('inner', 1, 'real fatigue pitting'),
    'KI21': ('inner', 1, 'real fatigue pitting'),
    'KI18': ('inner', 2, 'real fatigue pitting'),
    'KI16': ('inner', 3, 'real fatigue pitting'),
    'KB23': ('combined', 2, 'real combined'),
    'KB24': ('combined', 3, 'real combined'),
    'KB27': ('combined', 1, 'real combined+indentation'),
}

# Registered reference values (plan documents; verification targets).
REGISTERED = {
    'paderborn1_inner_rho': (+0.845, 'experiment_plan_paderborn.md §5-H1'),
    'paderborn1_outer_rho': (+0.866, 'experiment_plan_paderborn.md §5-H1'),
    'paderborn2_far_mean_A': (0.431, 'experiment_plan_paderborn2.md §8'),
    'paderborn2_far_mean_E': (0.141, 'experiment_plan_paderborn2.md §8'),
    'paderborn2_absorb_B': (0.411, 'experiment_plan_paderborn2.md §8'),
    'paderborn3_E3n4_far_mean': (0.0010, 'experiment_plan_paderborn3.md §7'),
    'ims_t1B3_lead_h': (79.0, 'experiment_plan_ims.md §4'),
    'ims_t1B4_lead_h': (148.0, 'experiment_plan_ims.md §4'),
    'ims_t2B1_lead_h': (74.0, 'experiment_plan_ims.md §4'),
    'ims_t1B3_rho_occ': (+0.90, 'experiment_plan_ims.md §4'),
    'ims_t1B4_rho_occ': (+1.00, 'experiment_plan_ims.md §4'),
    'ims_t2B1_rho_occ': (+0.95, 'experiment_plan_ims.md §4'),
    'ims_h3l_delay_t1B3_pct': (+13.96, 'experiment_plan_ims.md §4'),
    'ims_h3l_delay_t2B1_pct': (+11.18, 'experiment_plan_ims.md §4'),
    'hydraulic_cooler_far_seed1': (0.0051,
                                   'experiment_plan_hydraulic.md §7'),
    'hydraulic_valve_rho_seed1': (+0.925,
                                  'experiment_plan_hydraulic.md §7'),
}

_verification = {}


def _verify(key, exported, atol):
    ref, src = REGISTERED[key]
    ok = bool(abs(exported - ref) <= atol)
    _verification[key] = dict(registered=ref, exported=float(exported),
                              atol=atol, match=ok, source=src)
    if not ok:
        print(f"  !! VERIFY MISMATCH {key}: exported {exported} vs "
              f"registered {ref} ({src})")


# ------------------------------------------------------------- Paderborn #1
def export_paderborn1():
    from tests.paderborn.exp_paderborn_full import _fit_primary
    from tests.paderborn.paderborn_datasets import (FULL_CONDITIONS,
                                                    load_frames_full)
    from scipy.stats import spearmanr
    X, bearing, condition, rec = load_frames_full()
    z, margin, k, hold_m = _fit_primary(
        X, bearing, rec, ['K001', 'K002', 'K003', 'K004'],
        ['K005', 'K006'])
    rows = []
    for b in sorted(set(bearing)):
        ring, ext, kind = PADERBORN_META[b]
        for c in ['all'] + FULL_CONDITIONS:
            m = (bearing == b) if c == 'all' else \
                ((bearing == b) & (condition == c))
            mg = margin(z(X[m]))
            rows.append(dict(bearing=b, ring=ring, extent=ext,
                             damage_kind=kind, condition=c,
                             median_margin=float(np.median(mg)),
                             detection=float((mg > 0).mean()),
                             q25=float(np.percentile(mg, 25)),
                             q75=float(np.percentile(mg, 75)),
                             n_frames=int(m.sum())))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, 'paderborn_severity.csv'), index=False)
    # verification: Spearman on the real-pitting ladders (pooled medians)
    for name, sel in (('inner', ['KI04', 'KI14', 'KI17', 'KI21', 'KI18',
                                 'KI16']),
                      ('outer', ['KA04', 'KA22', 'KA16'])):
        sub = df[(df.bearing.isin(sel)) & (df.condition == 'all')]
        rho = spearmanr(sub.extent, sub.median_margin).statistic
        _verify(f'paderborn1_{name}_rho', rho, atol=0.02)
    print(f"  paderborn_severity.csv: {len(df)} rows (K={k})")


# ------------------------------------------------------------- Paderborn #2
def export_paderborn2():
    from tests.paderborn.exp_paderborn2 import (CANDIDATES, FOLDS,
                                                SharedGeometry, _rec_index,
                                                COMMISSION_MAX_IDX, evaluate)
    from tests.paderborn.paderborn_datasets import load_frames_full
    X, bearing, condition, rec = load_frames_full()
    rec_idx = np.array([_rec_index(r) for r in rec])
    eval_rec_m = rec_idx > COMMISSION_MAX_IDX

    fold_fars = {C.name: [] for C in CANDIDATES}
    for fit_b, hold_b in FOLDS:                      # mirrors main()
        g = SharedGeometry(X, bearing, condition, rec, fit_b)
        hold_eval = np.isin(bearing, hold_b) & eval_rec_m
        for C in CANDIDATES:
            cand = C(g, X=X, bearing=bearing, condition=condition,
                     rec=rec, hold_bearings=hold_b)
            al = cand.alarm(X[hold_eval], condition[hold_eval],
                            bearing[hold_eval])
            fold_fars[C.name].append(float((al > 0).mean()))

    fit_b, hold_b = FOLDS[0]
    g = SharedGeometry(X, bearing, condition, rec, fit_b)
    hold_eval = np.isin(bearing, hold_b) & eval_rec_m
    rows = []
    for C in CANDIDATES:
        rng = np.random.default_rng(7)               # mirrors main()
        cand = C(g, X=X, bearing=bearing, condition=condition, rec=rec,
                 hold_bearings=hold_b)
        r = evaluate(cand, X, bearing, condition, rec, hold_eval, rng)
        i, o = r['ladders']['inner'], r['ladders']['outer']
        ff = fold_fars[C.name]
        rows.append(dict(
            candidate=C.name, far_fold1=ff[0], far_fold2=ff[1],
            far_fold3=ff[2], far_mean=float(np.mean(ff)),
            det_all=r['det_all'], absorb_e1=r['absorb_e1'],
            inner_ordered=i[0], inner_pairs=i[1], inner_rho=i[2],
            outer_ordered=o[0], outer_pairs=o[1], outer_rho=o[2],
            scale_ratio=r['scale_ratio']))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, 'paderborn_support_candidates.csv'),
              index=False)
    _verify('paderborn2_far_mean_A',
            float(df[df.candidate.str.startswith('A')].far_mean.iloc[0]),
            atol=0.01)
    _verify('paderborn2_far_mean_E',
            float(df[df.candidate.str.startswith('E')].far_mean.iloc[0]),
            atol=0.01)
    _verify('paderborn2_absorb_B',
            float(df[df.candidate.str.startswith('B')].absorb_e1.iloc[0]),
            atol=0.01)
    print(f"  paderborn_support_candidates.csv: {len(df)} rows")


# ------------------------------------------------------------- Paderborn #3
def export_paderborn3():
    from tests.paderborn.exp_paderborn2 import FOLDS, SharedGeometry, \
        _rec_index
    from tests.paderborn.exp_paderborn3 import (AlarmE0, AlarmE2, AlarmE3,
                                                AlarmE4, EVAL_MIN_IDX,
                                                LADDER, severity_audit)
    from tests.paderborn.paderborn_datasets import load_frames_full
    X, bearing, condition, rec = load_frames_full()
    rec_idx = np.array([_rec_index(r) for r in rec])
    eval_m = rec_idx >= EVAL_MIN_IDX

    g0 = SharedGeometry(X, bearing, condition, rec, FOLDS[0][0])
    audit = severity_audit(g0, X, bearing, condition)

    configs = ([(f'E0/E1 scalar n={n}', AlarmE0, {'n_rec': n})
                for n in LADDER]
               + [(f'E2 shrunk-cond n={n}', AlarmE2, {'n_rec': n})
                  for n in (4, 8)]
               + [(f'E3 loc+scale n={n}', AlarmE3, {'n_rec': n})
                  for n in (4, 8)]
               + [(f'E4 +cons.tail n={n}', AlarmE4, {'n_rec': n})
                  for n in (4, 8)])
    results = {name: [] for name, _, _ in configs}
    for fit_b, hold_b in FOLDS:                      # mirrors main()
        g = SharedGeometry(X, bearing, condition, rec, fit_b)
        he = np.isin(bearing, hold_b) & eval_m
        for name, cls, kw in configs:
            cand = cls(g, X, bearing, condition, rec_idx, hold_b, **kw)
            mm = cand.margin(X[he], condition[he], bearing[he])
            results[name].append(float((mm > 0).mean()))
    rows = [dict(configuration=name, far_fold1=f[0], far_fold2=f[1],
                 far_fold3=f[2], far_mean=float(np.mean(f)))
            for name, f in results.items()]
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, 'paderborn_commissioning.csv'),
              index=False)
    _verify('paderborn3_E3n4_far_mean',
            float(df[df.configuration == 'E3 loc+scale n=4']
                  .far_mean.iloc[0]), atol=0.002)
    print(f"  paderborn_commissioning.csv: {len(df)} rows "
          f"(severity audit: inner {audit['inner'][0]}/"
          f"{audit['inner'][1]} ρ{audit['inner'][2]:+.2f}, outer "
          f"{audit['outer'][0]}/{audit['outer'][1]} "
          f"ρ{audit['outer'][2]:+.2f})")
    return dict(severity_audit=audit)


# -------------------------------------------------------------------- IMS #4
def export_ims():
    from tests.ims.exp_ims import (TESTS, N_PER_SNAP, run_bearing,
                                   snap_medians, sustained_onset)
    from tests.ims.ims_datasets import load_ims_test
    rng = np.random.default_rng(3)                   # mirrors main()
    npz, rows = {}, []
    for test in ('test1', 'test2', 'test3'):         # exact main() order
        cfg = TESTS[test]
        frames, times = load_ims_test(test)
        n_snap = len(times)
        npz[f'times_{test}'] = times
        results = {b: run_bearing(test, b, frames[b], times, rng)
                   for b in cfg['bearings']}
        ref_b = min(b for b in cfg['bearings'] if b not in cfg['failed'])
        for b in cfg['bearings']:
            r = results[b]
            npz[f'med_{test}_b{b}'] = r['med']
            npz[f'ncon_{test}_b{b}'] = np.array(r['model'].n_con)
            row = dict(
                test=test, bearing=b,
                role='failed' if b in cfg['failed'] else 'control',
                primary=test != 'test3', K=r['model'].K,
                n_snap=n_snap, n_construct=r['model'].n_con,
                healthy_far=r['far'],
                onset_idx=r['onset'],
                onset_pct=(100 * r['onset'] / n_snap
                           if r['onset'] is not None else None),
                lead_h=r['lead_h'], persistence=r['persist'],
                rho_occ=r['rho_occ'] if b in cfg['failed'] else None,
                occ_q1=r['occ'][0], occ_q2=r['occ'][1], occ_q3=r['occ'][2],
                occ_q4=r['occ'][3], occ_q5=r['occ'][4],
                ci_eol_lo=float(r['ci_eol'][0]),
                ci_eol_hi=float(r['ci_eol'][1]),
                ci_q_lo=float(r['ci_q'][0]), ci_q_hi=float(r['ci_q'][1]),
                eol_med=r['eol_med'], healthy_med=r['healthy_med'],
                e3_onset_pct=None, e3_delay_pct=None)
            if b in cfg['failed'] and test != 'test3':
                # E3 fleet margin under the reference geometry —
                # verbatim re-computation of exp_ims.h3l, additionally
                # keeping the trajectory for the figure (h3l returns
                # only the onset index; no rng is consumed).
                ref_model = results[ref_b]['model']
                n_con = ref_model.n_con
                ll_t = ref_model.ll(frames[b])
                con_ll = ll_t[:n_con * N_PER_SNAP]
                comm = con_ll[int(0.6 * len(con_ll)):]
                loc = float(np.median(comm))
                iqr = (abs(float(np.subtract(
                    *np.percentile(comm, [75, 25])))) + 1e-12)
                med_ref = float(np.median(ref_model.floor_ll))
                ll_std = (ll_t - loc) / iqr * ref_model.iqr + med_ref
                marg = (ref_model.floor - ll_std) / ref_model.iqr
                med_e3 = snap_medians(marg, n_snap)
                onset_e3 = sustained_onset(med_e3, n_con)
                npz[f'e3med_{test}_b{b}'] = med_e3
                row['e3_onset_pct'] = (100 * onset_e3 / n_snap
                                       if onset_e3 is not None else None)
                row['e3_delay_pct'] = (
                    (onset_e3 - r['onset']) / n_snap * 100
                    if onset_e3 is not None and r['onset'] is not None
                    else None)
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, 'ims_summary.csv'), index=False)
    np.savez_compressed(os.path.join(OUT, 'ims_trajectories.npz'), **npz)

    def _cell(test, b, col):
        return df[(df.test == test) & (df.bearing == b)][col].iloc[0]
    _verify('ims_t1B3_lead_h', _cell('test1', 3, 'lead_h'), atol=1.0)
    _verify('ims_t1B4_lead_h', _cell('test1', 4, 'lead_h'), atol=1.0)
    _verify('ims_t2B1_lead_h', _cell('test2', 1, 'lead_h'), atol=1.0)
    _verify('ims_t1B3_rho_occ', _cell('test1', 3, 'rho_occ'), atol=0.005)
    _verify('ims_t1B4_rho_occ', _cell('test1', 4, 'rho_occ'), atol=0.005)
    _verify('ims_t2B1_rho_occ', _cell('test2', 1, 'rho_occ'), atol=0.005)
    _verify('ims_h3l_delay_t1B3_pct', _cell('test1', 3, 'e3_delay_pct'),
            atol=0.05)
    _verify('ims_h3l_delay_t2B1_pct', _cell('test2', 1, 'e3_delay_pct'),
            atol=0.05)
    assert _cell('test1', 4, 'e3_onset_pct') is None or \
        np.isnan(_cell('test1', 4, 'e3_onset_pct')), \
        't1-B4 E3 silence expected (registered)'
    print(f"  ims_summary.csv: {len(df)} rows; ims_trajectories.npz: "
          f"{len(npz)} arrays")


# -------------------------------------------------------------- Milling (M)
def export_milling():
    from tests.multivariate.exp_deployability import _fit_auto
    from tests.baselines.mspc_baselines import MSPCModel
    from tests.ims.exp_ims import Q
    from tests.ims.ims_datasets import load_milling
    from scipy.stats import spearmanr
    runs = load_milling()                            # mirrors exp_ims main()
    rows = []
    for c in sorted(set(r['case'] for r in runs)):
        rs = sorted([r for r in runs if r['case'] == c],
                    key=lambda r: r['run'])
        if len(rs) < 6:
            continue
        con = np.vstack([r['frames'] for r in rs[:3]])
        mu, sd = con.mean(0), con.std(0) + 1e-12
        z = lambda A: (A - mu) / sd
        pca = MSPCModel().fit(z(con))
        proj = lambda A: pca._scores_resid(z(A))[0]
        g, k = _fit_auto(proj(con), 'full')
        ll_con = g.score_samples(proj(con))
        floor = float(np.quantile(ll_con, Q))
        iqr = abs(float(np.subtract(
            *np.percentile(ll_con, [75, 25])))) + 1e-12
        vb, mg = [], []
        for r in rs:
            if not np.isfinite(r['VB']):
                continue
            m = float(np.median((floor - g.score_samples(
                proj(r['frames']))) / iqr))
            vb.append(r['VB'])
            mg.append(m)
            rows.append(dict(case=c, run=r['run'], VB=r['VB'],
                             median_margin=m, rho_case=None))
        if len(vb) >= 5:
            rho = float(spearmanr(vb, mg).statistic)
            for row in rows:
                if row['case'] == c:
                    row['rho_case'] = rho
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, 'milling_wear.csv'), index=False)
    med_rho = float(np.median(df.groupby('case').rho_case.first()
                              .dropna()))
    print(f"  milling_wear.csv: {len(df)} rows "
          f"(median case ρ {med_rho:+.2f})")


# ------------------------------------------------------------- Hydraulic #5
def export_hydraulic():
    from tests.hydraulic.exp_hydraulic_prereg import (FEATURES, SEEDS,
                                                      boot_ci_severe_vs_mild,
                                                      run_target_seed)
    from tests.hydraulic.hydraulic_datasets import STAGES, load_cycle_means
    X, _ = load_cycle_means(features=FEATURES)
    stage_rows, sum_rows = [], []
    for target in STAGES:                            # mirrors main() order
        for seed in SEEDS:
            r = run_target_seed(target, X, seed)
            for rank, stage in enumerate(STAGES[target]):
                s = r['stages'][stage]
                m = s['m']
                stage_rows.append(dict(
                    target=target, seed=seed, stage=stage,
                    stage_rank=rank + 1, det=s['det'], median=s['med'],
                    p5=float(np.percentile(m, 5)),
                    p25=float(np.percentile(m, 25)),
                    p75=float(np.percentile(m, 75)),
                    p95=float(np.percentile(m, 95)), n_cycles=s['n']))
            row = dict(target=target, seed=seed, K=r['K'],
                       healthy_far=r['far'], rho=r['rho'])
            for i, (lo, hi) in enumerate(r['adj_ci']):
                row[f'adj_ci{i + 1}_lo'] = lo
                row[f'adj_ci{i + 1}_hi'] = hi
            if len(STAGES[target]) == 3:
                lo, hi = boot_ci_severe_vs_mild(r, target)
                row['severe_vs_mild_ci_lo'] = lo
                row['severe_vs_mild_ci_hi'] = hi
            sum_rows.append(row)
    pd.DataFrame(stage_rows).to_csv(
        os.path.join(OUT, 'hydraulic_seed_stage.csv'), index=False)
    dfs = pd.DataFrame(sum_rows)
    dfs.to_csv(os.path.join(OUT, 'hydraulic_seed_summary.csv'),
               index=False)
    _verify('hydraulic_cooler_far_seed1',
            float(dfs[(dfs.target == 'cooler') & (dfs.seed == 1)]
                  .healthy_far.iloc[0]), atol=0.002)
    _verify('hydraulic_valve_rho_seed1',
            float(dfs[(dfs.target == 'valve') & (dfs.seed == 1)]
                  .rho.iloc[0]), atol=0.005)
    print(f"  hydraulic_seed_stage.csv: {len(stage_rows)} rows; "
          f"hydraulic_seed_summary.csv: {len(sum_rows)} rows")


# ------------------------------------------------------------------ manifest
FROZEN = {
    'paderborn1': dict(plan='doc/preregistrations/experiment_plan_paderborn.md',
                       runner='tests/paderborn/exp_paderborn_full.py',
                       freeze='plan 332b1d2, results 088bc8e'),
    'paderborn2': dict(plan='doc/preregistrations/experiment_plan_paderborn2.md',
                       runner='tests/paderborn/exp_paderborn2.py',
                       freeze='impl 8ea1a9d before results'),
    'paderborn3': dict(plan='doc/preregistrations/experiment_plan_paderborn3.md',
                       runner='tests/paderborn/exp_paderborn3.py',
                       freeze='impl c61f061 before results'),
    'ims': dict(plan='doc/preregistrations/experiment_plan_ims.md',
                runner='tests/ims/exp_ims.py',
                freeze='impl b387a4f before results'),
    'hydraulic': dict(plan='doc/preregistrations/experiment_plan_hydraulic.md',
                      runner='tests/hydraulic/exp_hydraulic_prereg.py',
                      freeze='plan 2f78443, impl 7c6d054 before results'),
}


def write_manifest():
    # merge verification entries from a previous (subset) export so
    # partial re-runs never silently drop other sections' checks
    prev = os.path.join(OUT, 'manifest.json')
    if os.path.exists(prev):
        with open(prev) as fh:
            for k, v in json.load(fh).get('verification', {}).items():
                _verification.setdefault(k, v)
    head = subprocess.run(['git', 'rev-parse', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()
    files = {}
    for f in sorted(os.listdir(OUT)):
        if f == 'manifest.json':
            continue
        p = os.path.join(OUT, f)
        entry = dict(bytes=os.path.getsize(p))
        if f.endswith('.csv'):
            entry['rows'] = int(len(pd.read_csv(p)))
        files[f] = entry
    manifest = dict(
        purpose=('machine-readable snapshot of the five pre-registered '
                 'results for manuscript figures/tables; a build step, '
                 'not an experiment — computations re-executed by '
                 'importing the frozen runners with identical seeds, '
                 'splits, and evaluation order'),
        generator='tests/figures/export_paper_results.py',
        export_commit=head,
        provenance=FROZEN,
        datasets=dict(
            PADERBORN='KAt Data Center (CC BY-NC 4.0) via GitHub Release pu-bearing-data',
            IMS='NASA Prognostics Data Repository dataset 4 (IMS, Univ. of Cincinnati)',
            MILLING='NASA Prognostics Data Repository dataset 3 (BEST Lab, UC Berkeley)',
            HYDRAULIC='UCI id 447 (ZeMA, CC BY 4.0) via Machine-Learning-FGA mirror'),
        files=files,
        verification=_verification,
        verification_all_match=all(v['match']
                                   for v in _verification.values()),
    )
    with open(os.path.join(OUT, 'manifest.json'), 'w') as fh:
        json.dump(manifest, fh, indent=2)
    n_ok = sum(v['match'] for v in _verification.values())
    print(f"  manifest.json: {len(files)} files, verification "
          f"{n_ok}/{len(_verification)} matched")


SECTIONS = dict(paderborn1=export_paderborn1, paderborn2=export_paderborn2,
                paderborn3=export_paderborn3, ims=export_ims,
                milling=export_milling, hydraulic=export_hydraulic)


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    wanted = argv or list(SECTIONS)
    print(f"exporting paper_results/ sections: {wanted}")
    for name in wanted:
        print(f"[{name}]")
        SECTIONS[name]()
    write_manifest()


if __name__ == '__main__':
    main(sys.argv[1:])
