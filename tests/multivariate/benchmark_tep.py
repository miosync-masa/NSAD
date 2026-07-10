"""TEP benchmark — the contextual proof on the coupled-process standard.

doc/preregistrations/experiment_plan_multivariate.md §3/§9. TEP provides what NAB/SKAB
cannot: a separate clean normal-regime log (d00), i.e. the IDEAL
industrial setting — normal structure is built with no exclusion masks
and no labels of any kind. Faults activate at sample 160 of each 960-
sample test file.

Variants (identical training data = d00 only):
  v0j  per-channel jump ratios + OR fusion (rate-type marginal detection)
  v0z  per-channel |z| + OR fusion (level-type marginal detection — the
       industrial standard alarm limit; score = max over 52 channels).
       Both marginal baselines are reported so that neither rate- nor
       level-type marginal detection is a straw man.
  v2   joint reconstruction residual with delay_window=1 — at d=52 a
       delay-20 embedding would be 1040-dim against 500 calibration
       samples (under-sampled; §2 guardrail against blind high-d), so the
       joint structure is the spatial SVD subspace: the classic PCA
       SPE/Q-statistic, which is exactly our reconstruction scorer at W=1.

Contextual is a PHASE, not a per-fault binary: after onset the control
system propagates every TEP fault into dozens of marginal band exits, so
whole-window tagging marks everything univariate. The §4 question
becomes temporal: does the joint residual fire BEFORE any marginal
leaves its band? The lead-time analysis measures exactly that.

Thresholds (train-only, out-of-sample): scorers are calibrated on the
first 350 samples of d00; per-variant threshold = q-quantile of the score
on the held-out last 150 samples of d00. No test data, no labels.

Metrics (TEP convention adapted to ours):
  FAR        flag rate on fault-free frames: all of d00_te + the
             pre-fault head (0..159) of every fault file
  detection  per-fault: fraction of fault-active frames flagged
  delay      frames from fault onset (160) to first flag

Stratification (§4, refined rule): marginal bands from d00; a fault is
*univariate* if any channel exits its band beyond chance during the
fault segment, else *contextual*.

Usage::
    python -m tests.multivariate.benchmark_tep
"""

from __future__ import annotations

import numpy as np

from lambda3_detector.streaming import (
    StreamingJumpScorer,
    StreamingReconstructionScorer,
)

from tests.baselines.mspc_baselines import MSPCModel, ReducedUnknown
from tests.multivariate.tep_datasets import (
    FAULT_START,
    iter_faults,
    load_test,
    load_train_normal,
)

SPLIT = 350            # d00: first 350 = scorer calibration, last 150 = threshold
BAND = (0.005, 0.995)
NOMINAL_TAIL = 0.01
QS = (0.99, 0.999)


def _znorm(train: np.ndarray):
    mu = train.mean(axis=0)
    sd = train.std(axis=0) + 1e-12
    return lambda X: (X - mu) / sd


def build_v0(train_z: np.ndarray):
    """Return score_fn(X_z) -> (n,) max-over-channels jump ratio."""
    scorers = []
    for ch in range(train_z.shape[1]):
        s = StreamingJumpScorer(percentile=99.0)
        s.calibrate(train_z[:SPLIT, ch:ch + 1])
        scorers.append(s)

    def score_fn(Xz: np.ndarray) -> np.ndarray:
        n = len(Xz)
        out = np.zeros(n)
        for ch, s in enumerate(scorers):
            x1 = Xz[:, ch:ch + 1]
            thr = s.threshold + 1e-12
            r = np.array([s.score(x1, t) / thr for t in range(n)])
            out = np.maximum(out, r)
        return out
    return score_fn


def build_v0z(train_z: np.ndarray):
    """Marginal level detector: max |z| over channels (z from d00 stats).
    train_z is already z-normalized, so the score is simply max |·|."""
    def score_fn(Xz: np.ndarray) -> np.ndarray:
        return np.abs(Xz).max(axis=1)
    return score_fn


def build_v2(train_z: np.ndarray):
    s = StreamingReconstructionScorer(n_components=5, delay_window=1)
    s.calibrate(train_z[:SPLIT])
    thr = s.threshold + 1e-12

    def score_fn(Xz: np.ndarray) -> np.ndarray:
        return np.array([s.score(Xz, t) / thr for t in range(len(Xz))])
    return score_fn


def main():
    train = load_train_normal()
    z = _znorm(train)
    train_z = z(train)

    # --- stratification: marginal bands from ALL of d00 ------------------
    lo = np.quantile(train, BAND[0], axis=0)
    hi = np.quantile(train, BAND[1], axis=0)
    tags = {}
    culprit_n = {}
    for sample in iter_faults():
        seg = sample.values[FAULT_START:]
        culprits = []
        for ch in range(seg.shape[1]):
            out = (seg[:, ch] < lo[ch]) | (seg[:, ch] > hi[ch])
            run = longest = 0
            for o in out:
                run = run + 1 if o else 0
                longest = max(longest, run)
            if out.mean() > 2 * NOMINAL_TAIL or longest >= 5:
                culprits.append(ch)
        tags[sample.fault_id] = 'univariate' if culprits else 'contextual'
        culprit_n[sample.fault_id] = len(culprits)

    ctx = sorted(f for f, t in tags.items() if t == 'contextual')
    uni = sorted(f for f, t in tags.items() if t == 'univariate')
    print("=" * 100)
    print(f"TEP stratification (bands from d00): "
          f"univariate={len(uni)} {uni}")
    print(f"{'':38}contextual={len(ctx)} {ctx}")
    print("=" * 100)

    # --- scores -----------------------------------------------------------
    # audit baselines: MSPC standard (PCA-SPE / Hotelling T², Chiang-
    # Russell-Braatz) + the reduced-space unknown channel (Phase B)
    mspc = MSPCModel().fit(train_z[:SPLIT])
    unk = ReducedUnknown().fit(train_z[:SPLIT])
    print(f"MSPC subspace: k={mspc.k} components; "
          f"ReducedUnknown: K_eff={unk.K_eff}")
    builders = {
        'v0j': build_v0,
        'v0z': build_v0z,
        'v2': build_v2,
        'spe': lambda tz: (lambda Xz: mspc.spe(Xz)),
        't2': lambda tz: (lambda Xz: mspc.t2(Xz)),
        'unknown': lambda tz: (lambda Xz: unk.score(Xz)),
    }
    score_fns = {v: b(train_z) for v, b in builders.items()}
    d00_scores = {v: fn(train_z)[SPLIT:] for v, fn in score_fns.items()}

    d00te = load_test(0)
    test_scores = {v: {} for v in builders}
    for v, fn in score_fns.items():
        test_scores[v][0] = fn(z(d00te.values))
        for sample in iter_faults():
            test_scores[v][sample.fault_id] = fn(z(sample.values))

    # --- audit curve: detection vs FAR over the q grid --------------------
    # spe_or_t2 = calibrated OR (each statistic against its own clean
    # quantile — no multiple-comparison free pass)
    q_grid = [0.95, 0.98, 0.99, 0.995, 0.999]
    print("\nAUDIT CURVES — mean detection % over 21 faults @ FAR % "
          "(train-only cleanq thresholds)")
    print(f"  {'variant':<10}" + "".join(f"   q={q:<6}" for q in q_grid))
    curve_variants = list(builders) + ['spe_or_t2']
    for v in curve_variants:
        cells = []
        for q in q_grid:
            if v == 'spe_or_t2':
                tau_s = float(np.quantile(d00_scores['spe'], q))
                tau_t = float(np.quantile(d00_scores['t2'], q))
                flag = lambda f: (test_scores['spe'][f] > tau_s) | \
                                 (test_scores['t2'][f] > tau_t)
            else:
                tau = float(np.quantile(d00_scores[v], q))
                flag = lambda f: test_scores[v][f] > tau
            far_parts = [flag(0)]
            far_parts += [flag(f)[:FAULT_START] for f in range(1, 22)]
            far = np.concatenate(far_parts).mean()
            det = np.mean([flag(f)[FAULT_START:].mean()
                           for f in range(1, 22)])
            cells.append(f" {100*det:5.1f}@{100*far:<4.2f}")
        print(f"  {v:<10}" + "".join(cells))

    # --- evaluation at train-only cleanq thresholds -----------------------
    for q in QS:
        print(f"\n--- operating point: q={q} on held-out d00 scores "
              f"(train-only) ---")
        print(f"  {'variant':<6} {'FAR %':>7} "
              f"{'det% (univariate)':>19} {'det% (contextual)':>19} "
              f"{'ctx faults detected':>21}")
        for v in builders:
            tau = float(np.quantile(d00_scores[v], q))
            # FAR: d00_te + pre-fault heads
            far_frames = [test_scores[v][0] > tau]
            for f in range(1, 22):
                far_frames.append(test_scores[v][f][:FAULT_START] > tau)
            far = np.concatenate(far_frames).mean()
            det = {f: (test_scores[v][f][FAULT_START:] > tau).mean()
                   for f in range(1, 22)}
            det_uni = np.mean([det[f] for f in uni]) if uni else float('nan')
            det_ctx = np.mean([det[f] for f in ctx]) if ctx else float('nan')
            ctx_detail = "  ".join(
                f"f{f}:{det[f]:.0%}" for f in ctx) if ctx else "—"
            print(f"  {v:<6} {100*far:>7.2f} {100*det_uni:>18.1f}% "
                  f"{100*det_ctx:>18.1f}% {ctx_detail:>21}")

    # --- per-fault detail + lead-time analysis at q=0.99 ------------------
    # Contextual phase = frames after onset where NO channel has yet left
    # its marginal band (sustained, >=3 consecutive). If v2 fires inside
    # that phase, the fault was detected while every marginal was still
    # in-range — the contextual thesis as a lead-time statement.
    q = 0.99
    print(f"\nPer-fault detail at q={q} "
          f"(first-flag delays in frames after onset; lead = v0z - v2):")
    print(f"  {'fault':>7} {'tag':>5} {'v0z det%':>9} {'v2 det%':>8} "
          f"{'t_marginal':>11} {'t_v2':>6} {'lead':>6}")
    taus = {v: float(np.quantile(d00_scores[v], q)) for v in builders}
    leads = []
    for f in range(1, 22):
        det = {v: (test_scores[v][f][FAULT_START:] > taus[v]).mean()
               for v in builders}
        # first sustained marginal band exit (any channel, >=3 consecutive)
        seg = load_test(f).values[FAULT_START:]
        out_any = ((seg < lo) | (seg > hi))
        sus = out_any & np.roll(out_any, 1, axis=0) & np.roll(out_any, 2, axis=0)
        sus[:2] = False
        rows = np.where(sus.any(axis=1))[0]
        t_marg = int(rows[0]) if len(rows) else -1
        flags2 = test_scores['v2'][f][FAULT_START:] > taus['v2']
        t_v2 = int(np.argmax(flags2)) if flags2.any() else -1
        lead = (t_marg - t_v2) if (t_marg >= 0 and t_v2 >= 0) else None
        if lead is not None:
            leads.append(lead)
        lead_s = f"{lead:+d}" if lead is not None else "—"
        print(f"  {f:>7} {tags[f][:3]:>5} {det['v0z']:>9.1%} "
              f"{det['v2']:>8.1%} {t_marg:>11} {t_v2:>6} {lead_s:>6}")
    if leads:
        leads = np.array(leads)
        print(f"\n  lead time (marginal band exit − v2 first flag): "
              f"median {np.median(leads):+.0f} frames, "
              f"v2 earlier in {(leads > 0).sum()}/{len(leads)} faults "
              f"(1 frame = 3 min)")


if __name__ == "__main__":
    main()
