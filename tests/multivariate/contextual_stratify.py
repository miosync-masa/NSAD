"""Step 5 — univariate/contextual stratification + the proof table (H1).

doc/preregistrations/experiment_plan_multivariate.md §4/§9-5.

Tagging (refined rule from the Step-1 probe, tests/probes/test_contextual_mechanism):
  Per-channel marginal band = [0.5%, 99.5%] quantiles of the
  exclusion-cleaned frames of the same file. A labeled window is
  **univariate** if any channel exits its band *beyond chance*:
  out-of-band fraction > 2x the nominal tail mass (2%), or a sustained
  run of >=5 consecutive frames outside the band. Otherwise **contextual**.
  (The naive 'any frame exits' rule mis-tags long windows: ~1% of fully
  normal frames sit outside the band by construction.)

Proof table (H1): window catch per tag for
  v0          per-channel jump ratios, OR fusion (score = max over channels)
  v2          joint reconstruction ratio (d=8)
  v3_alarm    Tier-2 calibrated combined score
  v3_unknown  -log_likelihood under the fitted regime GMM (support boundary)
at FP-matched, label-free operating points: per-file threshold =
q-quantile of the score on clean frames (cleanq; exclusion-only label
use), q in {0.99, 0.999}. All variants share the same exclusion-cleaned
training data.

Usage::
    python -m tests.multivariate.contextual_stratify
"""

from __future__ import annotations

import numpy as np

from lambda3_detector.regime import RegimeAwareDetector, expand_anomaly_mask
from lambda3_detector.streaming import (
    StreamingJumpScorer,
    StreamingReconstructionScorer,
)

from tests.nab.benchmark_nab_selfcal import evaluate_flags
from tests.multivariate.benchmark_skab import MASK_MARGIN, _clean_setup
from tests.baselines.mspc_baselines import MSPCModel
from tests.multivariate.skab_datasets import iter_all

CAL_RATIO = 0.15
BAND = (0.005, 0.995)
NOMINAL_TAIL = (BAND[0] + (1.0 - BAND[1]))   # 0.01
QS = (0.99, 0.999)


def tag_window(sample, si: int, ei: int, lo, hi):
    """Return ('univariate', channels) or ('contextual', [])."""
    seg = sample.values[si:ei + 1]
    culprits = []
    for ch in range(seg.shape[1]):
        out = (seg[:, ch] < lo[ch]) | (seg[:, ch] > hi[ch])
        run, longest = 0, 0
        for o in out:
            run = run + 1 if o else 0
            longest = max(longest, run)
        if out.mean() > 2 * NOMINAL_TAIL or longest >= 5:
            culprits.append(ch)
    return ('univariate', culprits) if culprits else ('contextual', [])


def scores_v0(sample):
    Xz, clean = _clean_setup(sample)
    n = sample.n
    per_ch = np.zeros((Xz.shape[1], n))
    for ch in range(Xz.shape[1]):
        s = StreamingJumpScorer(percentile=99.0)
        s.calibrate(clean[:, ch:ch + 1])
        thr = s.threshold + 1e-12
        x1 = Xz[:, ch:ch + 1]
        per_ch[ch] = [s.score(x1, t) / thr for t in range(n)]
    return per_ch.max(axis=0)


def scores_v2(sample):
    Xz, clean = _clean_setup(sample)
    s = StreamingReconstructionScorer(n_components=5, delay_window=20)
    s.calibrate(clean)
    thr = s.threshold + 1e-12
    return np.array([s.score(Xz, t) / thr for t in range(sample.n)])


def scores_v3(sample):
    det = RegimeAwareDetector(K='auto', calibrate_combined=True)
    result = det.fit_predict(sample.values, sample.anomaly.astype(bool))
    return {
        'v3_alarm': np.asarray(result['score'], dtype=np.float64),
        'v3_unknown': -np.asarray(result['log_likelihood'], dtype=np.float64),
    }


def main():
    samples = list(iter_all())

    # ---- tagging --------------------------------------------------------
    windows = []       # (sample_idx, si, ei, tag, culprits)
    for i, s in enumerate(samples):
        expanded = expand_anomaly_mask(s.anomaly.astype(bool), MASK_MARGIN)
        clean_raw = s.values[~expanded]
        lo = np.quantile(clean_raw, BAND[0], axis=0)
        hi = np.quantile(clean_raw, BAND[1], axis=0)
        for (si, ei) in s.window_indices:
            tag, culprits = tag_window(s, si, ei, lo, hi)
            windows.append((i, si, ei, tag, culprits))

    n_uni = sum(1 for w in windows if w[3] == 'univariate')
    n_ctx = len(windows) - n_uni
    print("=" * 100)
    print(f"STRATIFICATION (refined rule): {len(windows)} windows -> "
          f"univariate={n_uni}, contextual={n_ctx}")
    from collections import Counter
    culprit_counts = Counter(
        ch for w in windows for ch in w[4]
    )
    from tests.multivariate.skab_datasets import SENSOR_COLUMNS
    print("  univariate culprit channels: " + "  ".join(
        f"{SENSOR_COLUMNS[ch]}:{c}" for ch, c in culprit_counts.most_common()))
    for tag in ('contextual',):
        names = [samples[w[0]].name for w in windows if w[3] == tag]
        print(f"  {tag} windows: {names}")
    print("=" * 100)

    # ---- scores ----------------------------------------------------------
    all_scores = {}
    for i, s in enumerate(samples):
        entry = {'v0': scores_v0(s), 'v2': scores_v2(s)}
        entry.update(scores_v3(s))
        # MSPC audit baselines (Chiang-Russell-Braatz standard), per-file
        # PCA on the same exclusion-cleaned frames
        Xz, clean = _clean_setup(s)
        m = MSPCModel().fit(clean)
        entry['spe'] = m.spe(Xz)
        entry['t2'] = m.t2(Xz)
        # support-detector duel opponents (same clean frames, full d=8)
        from sklearn.svm import OneClassSVM
        from tests.baselines.fgmm_bayes import FGMMBayes
        fg = FGMMBayes().fit(clean)
        entry['fgmm_bip'] = fg.bip(Xz)
        entry['fgmm_minmaha'] = fg.min_maha(Xz)
        oc = OneClassSVM(kernel='rbf', nu=0.05, gamma='scale').fit(clean)
        entry['ocsvm'] = -oc.decision_function(Xz)
        all_scores[i] = entry

    variants = ['v0', 'spe', 't2', 'fgmm_bip', 'fgmm_minmaha', 'ocsvm',
                'v2', 'v3_alarm', 'v3_unknown']

    # ---- proof table at cleanq operating points --------------------------
    print(f"\nPROOF TABLE — catch by stratum at cleanq operating points "
          f"(label-free thresholds)")
    print(f"  {'variant':<12} {'q':>6} {'univariate':>16} {'contextual':>16} "
          f"{'fp/10k':>8}")
    print("-" * 100)
    for v in variants:
        for q in QS:
            caught = {'univariate': 0, 'contextual': 0}
            total = {'univariate': 0, 'contextual': 0}
            fp_rows = []
            for i, s in enumerate(samples):
                sc = all_scores[i][v]
                expanded = expand_anomaly_mask(
                    s.anomaly.astype(bool), MASK_MARGIN)
                tau = float(np.quantile(sc[~expanded], q))
                flags = sc > tau
                probation = int(CAL_RATIO * s.n)
                fp_rows.append(evaluate_flags(s, flags, probation))
                for (j, si, ei, tag, _) in windows:
                    if j != i or ei < probation:
                        continue
                    total[tag] += 1
                    if flags[max(si, probation):ei + 1].any():
                        caught[tag] += 1
            fp = 1e4 * sum(r['fp_frames'] for r in fp_rows) / \
                sum(r['n_out_window'] for r in fp_rows)
            uni = (f"{100*caught['univariate']/total['univariate']:5.1f}% "
                   f"({caught['univariate']}/{total['univariate']})"
                   if total['univariate'] else "  —")
            ctx = (f"{100*caught['contextual']/total['contextual']:5.1f}% "
                   f"({caught['contextual']}/{total['contextual']})"
                   if total['contextual'] else "  —")
            print(f"  {v:<12} {q:>6} {uni:>16} {ctx:>16} {fp:>8.1f}")
        print()

    # ---- catch-vs-FP curves (ROC-style, label-free threshold family) ----
    # The realized FP differs across variants at the same q (different score
    # tail shapes), so single-q rows are not FP-matched. Sweeping q traces a
    # catch-vs-FP curve; thresholds remain per-file clean quantiles
    # (label-free) — q is a global curve parameter, FP is measured post hoc.
    q_grid = [0.90, 0.95, 0.98, 0.99, 0.995, 0.998, 0.999, 0.9995]
    print("\nCATCH-vs-FP CURVES (all 34 windows; per-file cleanq thresholds)")
    print(f"  {'variant':<12}" + "".join(f"  q={q:<7}" for q in q_grid))
    for v in variants:
        catches, fps = [], []
        for q in q_grid:
            caught_n = 0
            fp_rows = []
            for i, s in enumerate(samples):
                sc = all_scores[i][v]
                expanded = expand_anomaly_mask(
                    s.anomaly.astype(bool), MASK_MARGIN)
                tau = float(np.quantile(sc[~expanded], q))
                flags = sc > tau
                probation = int(CAL_RATIO * s.n)
                fp_rows.append(evaluate_flags(s, flags, probation))
                for (j, si, ei, tag, _) in windows:
                    if j != i or ei < probation:
                        continue
                    if flags[max(si, probation):ei + 1].any():
                        caught_n += 1
            fp = 1e4 * sum(r['fp_frames'] for r in fp_rows) / \
                sum(r['n_out_window'] for r in fp_rows)
            catches.append(100.0 * caught_n / len(windows))
            fps.append(fp)
        print(f"  {v:<12}" + "".join(
            f"  {c:5.1f}%@{f:<6.0f}" for c, f in zip(catches, fps)))


if __name__ == "__main__":
    main()
