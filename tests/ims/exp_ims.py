"""Pre-registration #4 execution — E3 longitudinal validity on IMS.

Implements doc/preregistrations/experiment_plan_ims.md (incl. amendment A1). NOT an
RUL study: the questions are early-healthy FAR, sustained onset, lead
time, alarm persistence, near-end margin, cross-bearing
reproducibility, and the H3L scale-compression risk.

Per-asset mode, temporal splits (no shuffling — deployment-faithful):
construction = first 20% of snapshots; model part = first 60% of
construction, floor part = last 40% (out-of-sample, later in time);
healthy window = 20–50% of life; end-of-life = final 5%; sustained
onset = 3 consecutive snapshots with median frame margin > 0.

H3L design (fixed here, before results): reference asset = the
lowest-index non-failed bearing of the same test (test1 → B1,
test2 → B2). (a) per-asset margin: the bearing's own geometry+floor.
(b) E3 fleet margin: the REFERENCE bearing's geometry and floor, with
the target bearing standardized by the location/IQR of its own
construction-window log-likelihood under that shared geometry (#3's
E3 mechanism verbatim). Onset delay (b)−(a) in % of life is the H3L
statistic.

Usage::
    python -m tests.ims.exp_ims
"""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from tests.multivariate.exp_deployability import _fit_auto
from tests.baselines.mspc_baselines import MSPCModel
from tests.ims.ims_datasets import TESTS, load_ims_test, load_milling

N_PER_SNAP = 4
Q = 0.005
N_BOOT = 800

CONSTRUCT_FRAC = 0.20
HEALTHY_LO, HEALTHY_HI = 0.20, 0.50
EOL_FRAC = 0.05
ONSET_RUN = 3


class AssetModel:
    """Frozen path on one bearing's own early life (temporal split)."""

    def __init__(self, frames, n_snap):
        n_con = int(CONSTRUCT_FRAC * n_snap)
        con = frames[:n_con * N_PER_SNAP]
        n_model = int(0.6 * len(con))
        model, floor_part = con[:n_model], con[n_model:]
        self.mu, self.sd = model.mean(0), model.std(0) + 1e-12
        z = lambda A: (A - self.mu) / self.sd
        self.pca = MSPCModel().fit(z(model))
        proj = lambda A: self.pca._scores_resid(z(A))[0]
        self.gmm, self.K = _fit_auto(proj(model), 'full')
        self.proj = proj
        self.floor_ll = self.gmm.score_samples(proj(floor_part))
        self.floor = float(np.quantile(self.floor_ll, Q))
        self.iqr = abs(float(np.subtract(
            *np.percentile(self.floor_ll, [75, 25])))) + 1e-12
        self.n_con = n_con

    def ll(self, A):
        return self.gmm.score_samples(self.proj(A))

    def margin(self, A):
        return (self.floor - self.ll(A)) / self.iqr


def snap_medians(margins, n_snap):
    return np.median(margins.reshape(n_snap, N_PER_SNAP), axis=1)


def sustained_onset(med, start):
    ok = med > 0
    for i in range(start, len(ok) - ONSET_RUN + 1):
        if ok[i:i + ONSET_RUN].all():
            return i
    return None


def _boot_diff(a, b, rng, n=N_BOOT):
    d = [np.median(rng.choice(a, len(a))) - np.median(rng.choice(b, len(b)))
         for _ in range(n)]
    return np.percentile(d, [2.5, 97.5])


def run_bearing(test, b, frames, times, rng, model=None):
    n_snap = len(times)
    m = model or AssetModel(frames, n_snap)
    marg = m.margin(frames)
    med = snap_medians(marg, n_snap)

    lo, hi = int(HEALTHY_LO * n_snap), int(HEALTHY_HI * n_snap)
    healthy_fr = marg[lo * N_PER_SNAP:hi * N_PER_SNAP]
    far = float((healthy_fr > 0).mean())

    onset = sustained_onset(med, m.n_con)
    lead_h = float(times[-1] - times[onset]) if onset is not None else None
    persist = (float((med[onset:] > 0).mean())
               if onset is not None else 0.0)

    # H1L quintiles over post-construction life
    qs = np.array_split(np.arange(m.n_con, n_snap), 5)
    occ = [float((med[q] > 0).mean()) for q in qs]
    rho_occ = spearmanr(np.arange(1, 6), occ).statistic

    eol_fr = marg[int((1 - EOL_FRAC) * n_snap) * N_PER_SNAP:]
    ci_eol = _boot_diff(eol_fr, healthy_fr, rng)
    q1_fr = marg[qs[0][0] * N_PER_SNAP:(qs[0][-1] + 1) * N_PER_SNAP]
    q5_fr = marg[qs[4][0] * N_PER_SNAP:(qs[4][-1] + 1) * N_PER_SNAP]
    ci_q = _boot_diff(q5_fr, q1_fr, rng)

    return dict(model=m, med=med, far=far, onset=onset, lead_h=lead_h,
                persist=persist, occ=occ, rho_occ=float(rho_occ),
                ci_eol=ci_eol, ci_q=ci_q,
                eol_med=float(np.median(eol_fr)),
                healthy_med=float(np.median(healthy_fr)))


def h3l(test, b_target, frames_t, ref_model, times, rng):
    """E3 fleet margin under the reference geometry; onset delay."""
    n_snap = len(times)
    n_con = ref_model.n_con  # same fraction; equal n_snap per test
    ll_t = ref_model.ll(frames_t)
    con_ll = ll_t[:n_con * N_PER_SNAP]
    # commissioning stats from the LATER 40% of the construction window
    comm = con_ll[int(0.6 * len(con_ll)):]
    loc, iqr = float(np.median(comm)), (abs(float(np.subtract(
        *np.percentile(comm, [75, 25])))) + 1e-12)
    med_ref = float(np.median(ref_model.floor_ll))
    ll_std = (ll_t - loc) / iqr * ref_model.iqr + med_ref
    marg = (ref_model.floor - ll_std) / ref_model.iqr
    med = snap_medians(marg, n_snap)
    return sustained_onset(med, n_con)


def main():
    rng = np.random.default_rng(3)
    print("=" * 76)
    print("PRE-REGISTRATION #4 — E3 longitudinal validity on IMS "
          "(doc/preregistrations/experiment_plan_ims.md, incl. A1)")
    print("=" * 76)

    h1_fail = h2_fail = h3_fail = 0
    for test in ('test1', 'test2', 'test3'):
        cfg = TESTS[test]
        tag = ' (descriptive)' if test == 'test3' else ''
        print(f"\n===== {test}{tag}: failed bearings {cfg['failed']} =====")
        frames, times = load_ims_test(test)
        n_snap = len(times)
        life_h = float(times[-1] - times[0])
        print(f"  {n_snap} snapshots, {life_h:.0f} h of life")

        results = {}
        for b in cfg['bearings']:
            results[b] = run_bearing(test, b, frames[b], times, rng)

        ref_b = min(b for b in cfg['bearings']
                    if b not in cfg['failed'])
        for b in cfg['bearings']:
            r = results[b]
            role = 'FAILED ' if b in cfg['failed'] else 'control'
            onset_pct = (100 * r['onset'] / n_snap
                         if r['onset'] is not None else None)
            print(f"  B{b} [{role}] K={r['model'].K}  "
                  f"healthy-FAR {r['far']:6.2%}  "
                  f"onset {'%.1f%% of life' % onset_pct if onset_pct is not None else '—':>15}  "
                  f"lead {'%.0f h' % r['lead_h'] if r['lead_h'] is not None else '—':>7}  "
                  f"persist {r['persist']:5.1%}")
            if b in cfg['failed']:
                print(f"      occupancy/quintile "
                      f"{['%.2f' % o for o in r['occ']]} "
                      f"ρ={r['rho_occ']:+.2f}   "
                      f"EOL-vs-healthy CI [{r['ci_eol'][0]:+.1f},"
                      f"{r['ci_eol'][1]:+.1f}]   "
                      f"Q5-vs-Q1 CI [{r['ci_q'][0]:+.1f},{r['ci_q'][1]:+.1f}]"
                      f"   EOL med {r['eol_med']:+.1f}")
                if test != 'test3':
                    a = (r['ci_eol'][0] > 0)
                    bq = (r['rho_occ'] > 0)
                    c = (r['ci_q'][0] > 0)
                    if not (a and bq and c):
                        h1_fail += 1
                    if r['onset'] is None or r['far'] > 0.05:
                        h2_fail += 1
                    onset_e3 = h3l(test, b, frames[b],
                                   results[ref_b]['model'], times, rng)
                    delay = ((onset_e3 - r['onset']) / n_snap * 100
                             if (onset_e3 is not None and
                                 r['onset'] is not None) else None)
                    print(f"      H3L (ref=B{ref_b}): E3 onset "
                          f"{'%.1f%% of life' % (100 * onset_e3 / n_snap) if onset_e3 is not None else 'NONE'}"
                          f"   delay vs per-asset "
                          f"{'%.2f%% of life' % delay if delay is not None else '—'}")
                    if delay is None or delay > 1.0:
                        h3_fail += 1

    print("\n===== primary-test kill counters (threshold: >=2 of 3) =====")
    print(f"  H1L failures: {h1_fail}   H2L failures: {h2_fail}   "
          f"H3L failures: {h3_fail}")

    # ---------------- M: milling (descriptive)
    print("\n===== M — milling margin vs flank wear VB (descriptive) =====")
    runs = load_milling()
    cases = sorted(set(r['case'] for r in runs))
    rhos = []
    for c in cases:
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
        iqr = abs(float(np.subtract(*np.percentile(ll_con, [75, 25])))) + 1e-12
        vb, mg = [], []
        for r in rs:
            if not np.isfinite(r['VB']):
                continue
            m = float(np.median((floor - g.score_samples(
                proj(r['frames']))) / iqr))
            vb.append(r['VB'])
            mg.append(m)
        if len(vb) >= 5:
            rho = spearmanr(vb, mg).statistic
            rhos.append(rho)
            print(f"  case {c:2d}: n={len(vb):2d} runs with VB   "
                  f"ρ(margin, VB) = {rho:+.2f}")
    if rhos:
        print(f"  median ρ over {len(rhos)} cases: "
              f"{np.median(rhos):+.2f}   (positive = margin tracks wear)")


if __name__ == '__main__':
    main()
