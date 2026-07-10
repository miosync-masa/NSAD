"""Paderborn FULL-dataset validation — pre-registered run.

Implements doc/preregistrations/experiment_plan_paderborn.md exactly (hypotheses and
kill conditions fixed before the data transfer). Adapter and detector
are UNCHANGED from the subset run (§3 of the plan).

  H1  physical severity ordering on the real-damage ladders
      (inner pitting extents 1/2/3; outer 1/2), Spearman + bootstrap
      CIs, extent-1 spread reported as the identity-noise floor
  H2  condition-as-regime with all four operating conditions
      (BIC K >= 4? purity > 90%?)
  H3  cross-bearing healthy FAR: rotating unseen-bearing folds +
      construction-size curve (1 -> 2 -> 4 bearings)
  H5  artificial vs real, same ring, extent 1 (descriptive)

Primary model: construct on K001-K004, hold out K005/K006 (healthy);
all damaged-bearing scoring uses the primary model. FAR and detection
are always read as a pair (§5.5).

Usage::
    python -m tests.paderborn.exp_paderborn_full
"""

from __future__ import annotations

import numpy as np

from tests.hydraulic.exp_hydraulic import build_floor
from tests.paderborn.paderborn_datasets import FULL_CONDITIONS, load_frames_full

HEALTHY = ['K001', 'K002', 'K003', 'K004', 'K005', 'K006']
INNER_LADDER = {1: ['KI04', 'KI14', 'KI17', 'KI21'],
                2: ['KI18'], 3: ['KI16']}
OUTER_LADDER = {1: ['KA04', 'KA22'], 2: ['KA16']}
ART_VS_REAL = [('outer ring', 'KA01', ['KA04', 'KA22']),
               ('inner ring', 'KI01', ['KI04', 'KI14', 'KI17', 'KI21'])]

SPLIT_SEED = 0
N_BOOT = 2000


def _fit_primary(X, bearing, rec, fit_bearings, hold_bearings):
    fit_m = np.isin(bearing, fit_bearings)
    hold_m = np.isin(bearing, hold_bearings)
    mu, sd = X[fit_m].mean(0), X[fit_m].std(0) + 1e-12
    z = lambda A: (A - mu) / sd
    # shuffle fit recordings so the nested floor split is not ordered
    rng = np.random.default_rng(SPLIT_SEED)
    fit_idx = np.where(fit_m)[0]
    recs = np.unique(rec[fit_idx])
    rng.shuffle(recs)
    order = np.argsort([np.where(recs == r)[0][0] for r in rec[fit_idx]])
    margin, k = build_floor(z(X[fit_idx[order]]))
    return z, margin, k, hold_m


def _boot_median_diff(a, b, rng, n=N_BOOT):
    """95% CI for median(a) - median(b) by frame bootstrap."""
    diffs = [np.median(rng.choice(a, len(a))) -
             np.median(rng.choice(b, len(b))) for _ in range(n)]
    return np.percentile(diffs, [2.5, 97.5])


def h3_cross_bearing(X, bearing, condition, rec):
    print("\n" + "=" * 72)
    print("H3 — cross-bearing healthy FAR (designed 0.5%; "
          "subset within-bearing was 4.30%)")
    folds = [(['K001', 'K002', 'K003', 'K004'], ['K005', 'K006']),
             (['K003', 'K004', 'K005', 'K006'], ['K001', 'K002']),
             (['K001', 'K002', 'K005', 'K006'], ['K003', 'K004'])]
    fars = []
    for fit_b, hold_b in folds:
        z, margin, k, hold_m = _fit_primary(X, bearing, rec, fit_b, hold_b)
        far = float((margin(z(X[hold_m])) > 0).mean())
        fars.append(far)
        print(f"  fit {fit_b} -> unseen {hold_b}: "
              f"FAR {far:6.2%}  (K={k}, n={hold_m.sum()})")
    print(f"  mean unseen-bearing FAR: {np.mean(fars):.2%}   "
          f"kill condition (>4% at 4 construction bearings): "
          f"{'TRIGGERED' if np.mean(fars) > 0.04 else 'not triggered'}")

    print("  construction-size curve (holdout fixed = K005/K006):")
    for fit_b in (['K001'], ['K001', 'K002'],
                  ['K001', 'K002', 'K003', 'K004']):
        z, margin, k, hold_m = _fit_primary(
            X, bearing, rec, fit_b, ['K005', 'K006'])
        far = float((margin(z(X[hold_m])) > 0).mean())
        print(f"    {len(fit_b)} bearing(s): FAR {far:6.2%}  (K={k})")


def main():
    X, bearing, condition, rec = load_frames_full()
    present = sorted(set(bearing))
    print("=" * 72)
    print(f"PADERBORN FULL — pre-registered run "
          f"(doc/preregistrations/experiment_plan_paderborn.md)")
    print(f"  bearings present: {len(present)}  frames: {len(X)}  "
          f"d={X.shape[1]}")
    print("=" * 72)

    # ---------------- primary model
    z, margin, k, hold_m = _fit_primary(
        X, bearing, rec, ['K001', 'K002', 'K003', 'K004'],
        ['K005', 'K006'])
    m_hold = margin(z(X[hold_m]))
    far = float((m_hold > 0).mean())
    print(f"\nPrimary model: fit K001-K004, unseen healthy K005/K006")
    print(f"  H2 — BIC K = {k} ({len(FULL_CONDITIONS)} operating "
          f"conditions in data)")
    print(f"  unseen-healthy FAR {far:6.2%} (designed 0.5%) — pair for "
          f"all detection below")

    # regime-condition purity (H2)
    from tests.baselines.mspc_baselines import MSPCModel
    from tests.multivariate.exp_deployability import _fit_auto
    fit_m = np.isin(bearing, ['K001', 'K002', 'K003', 'K004'])
    fitZ = z(X[fit_m])
    n_nest = int(0.6 * len(fitZ))
    mm = MSPCModel().fit(fitZ[:n_nest])
    proj = lambda A: mm._scores_resid(A)[0]
    g, _ = _fit_auto(proj(fitZ[:n_nest]), 'full')
    lab = g.predict(proj(z(X[hold_m])))
    cond_h = condition[hold_m]
    from collections import Counter
    purity = sum(max(Counter(cond_h[lab == kk]).values())
                 for kk in range(k) if (lab == kk).any()) / len(cond_h)
    print(f"  H2 — regime-condition purity on unseen healthy: "
          f"{purity:.1%}  (target >90%, kill <70%)")

    # ---------------- H1 severity ladders
    rng = np.random.default_rng(1)
    for name, ladder in (('inner ring, real fatigue pitting',
                          INNER_LADDER),
                         ('outer ring, real fatigue pitting',
                          OUTER_LADDER)):
        avail = {e: [b for b in bs if b in present]
                 for e, bs in ladder.items()}
        if not all(avail.values()):
            print(f"\nH1 [{name}]: missing bearings "
                  f"{ {e: bs for e, bs in ladder.items()} } — skipped")
            continue
        print(f"\nH1 — severity ladder [{name}]")
        group_frames = {}
        for e, bs in avail.items():
            meds = []
            for b in bs:
                m_b = margin(z(X[bearing == b]))
                meds.append(float(np.median(m_b)))
                print(f"  extent {e}  {b}: median margin {meds[-1]:8.1f}"
                      f"  det {(m_b > 0).mean():6.1%}"
                      f"  (n={(bearing == b).sum()})")
            group_frames[e] = np.concatenate(
                [margin(z(X[bearing == b])) for b in bs])
            if len(meds) > 1:
                print(f"           extent-{e} identity spread "
                      f"(median range): {min(meds):.1f} .. {max(meds):.1f}")
        exts = sorted(group_frames)
        from scipy.stats import spearmanr
        per_bearing = [(e, float(np.median(margin(z(X[bearing == b])))))
                       for e, bs in avail.items() for b in bs]
        rho = spearmanr([e for e, _ in per_bearing],
                        [m for _, m in per_bearing]).statistic
        print(f"  Spearman rho(extent, per-bearing median) = {rho:+.3f}")
        ok = True
        for lo, hi in zip(exts[:-1], exts[1:]):
            ci = _boot_median_diff(group_frames[hi], group_frames[lo], rng)
            verdict = 'ordered' if ci[0] > 0 else (
                'REVERSED' if ci[1] < 0 else 'not separated')
            ok &= ci[0] > 0
            print(f"  median(ext {hi}) - median(ext {lo}): "
                  f"95% CI [{ci[0]:+.1f}, {ci[1]:+.1f}] IQR — {verdict}")
        print(f"  H1 [{name}]: "
              f"{'SUPPORTED' if ok else 'NOT supported as ordered'}")

    # ---------------- H1 per-condition (the pre-registered wording)
    for name, ladder in (('inner ring, real fatigue pitting',
                          INNER_LADDER),
                         ('outer ring, real fatigue pitting',
                          OUTER_LADDER)):
        print(f"\nH1 per-condition [{name}] "
              f"(kill: reversed pair w/ CI excl. 0 in >=2 conditions)")
        exts = sorted(ladder)
        n_rev = {p: 0 for p in zip(exts[:-1], exts[1:])}
        for c in FULL_CONDITIONS:
            gf = {e: margin(z(X[np.isin(bearing, bs) & (condition == c)]))
                  for e, bs in ladder.items()}
            parts = []
            for lo, hi in zip(exts[:-1], exts[1:]):
                ci = _boot_median_diff(gf[hi], gf[lo], rng, n=800)
                v = ('ordered' if ci[0] > 0 else
                     'REVERSED' if ci[1] < 0 else 'flat')
                if ci[1] < 0:
                    n_rev[(lo, hi)] += 1
                parts.append(f"{lo}->{hi} {v} [{ci[0]:+.1f},{ci[1]:+.1f}]")
            print(f"  {c}: " + "; ".join(parts))
        killed = any(v >= 2 for v in n_rev.values())
        print(f"  kill condition: "
              f"{'TRIGGERED' if killed else 'not triggered'}")

    # ---------------- H5 artificial vs real (descriptive)
    print("\nH5 — artificial vs real, same ring, extent 1 (descriptive)")
    for ring, art, reals in ART_VS_REAL:
        if art not in present:
            continue
        m_art = margin(z(X[bearing == art]))
        print(f"  {ring}: artificial {art} median "
              f"{np.median(m_art):8.1f} IQR (det {(m_art>0).mean():5.1%})")
        for b in reals:
            if b not in present:
                continue
            m_r = margin(z(X[bearing == b]))
            print(f"  {ring}: real       {b} median "
                  f"{np.median(m_r):8.1f} IQR (det {(m_r>0).mean():5.1%})")

    # ---------------- overall detection summary (paired with FAR above)
    print("\nDetection summary, all damaged bearings (primary model):")
    damaged = [b for b in present if b not in HEALTHY]
    for b in damaged:
        m_b = margin(z(X[bearing == b]))
        print(f"  {b}: det {(m_b > 0).mean():6.1%}   "
              f"median margin {np.median(m_b):8.1f} IQR")

    # ---------------- H3
    h3_cross_bearing(X, bearing, condition, rec)


if __name__ == '__main__':
    main()
