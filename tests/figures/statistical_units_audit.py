"""Post-hoc statistical audit — NOT pre-registered.

Recording-level cluster bootstrap for the Paderborn #1 H1
adjacent-pair median differences, run as a sensitivity analysis for
the manuscript's inference-units disclosure (internal review, M6).
The registered analyses bootstrap FRAMES; frames within a recording
are not independent replicates, so this audit resamples RECORDINGS
(the finest defensible cluster; bearing-level resampling is
degenerate for the single-bearing extent groups, and the bearing
remains the generalization unit, reported as n).

Nothing here re-judges any registered verdict: the registered
frame-bootstrap CIs stand as reported (conditional on the observed
bearings and recordings); this audit asks only whether the ordering
conclusions survive the coarser resampling unit.

Model and margins are the #1 primary model verbatim
(tests/paderborn/exp_paderborn_full._fit_primary: fit K001-K004).
Bootstrap seed 42 (distinct from every registered analysis), 2000
resamples.

Output: paper_results/statistical_audit.csv (post-hoc column
included; deliberately NOT added to manifest.json verification —
registered and post-hoc numbers are kept separate).

Usage::
    python -m tests.figures.statistical_units_audit
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from tests.paderborn.exp_paderborn_full import (INNER_LADDER, OUTER_LADDER,
                                                _fit_primary)
from tests.paderborn.paderborn_datasets import load_frames_full

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'paper_results')
N_BOOT = 2000
SEED = 42


def group_margins_by_recording(margin, z, X, bearing, rec, bearings):
    """dict recording-id -> margin array, for the given bearings."""
    m = np.isin(bearing, bearings)
    out = {}
    for r in np.unique(rec[m]):
        sel = m & (rec == r)
        out[r] = margin(z(X[sel]))
    return out


def ci_from_boot(diffs):
    return float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


def bootstrap_pair(g_lo, g_hi, rng):
    """(frame CI, cluster CI) for median(hi) - median(lo)."""
    fr_lo = np.concatenate(list(g_lo.values()))
    fr_hi = np.concatenate(list(g_hi.values()))
    frame_diffs = [
        np.median(rng.choice(fr_hi, len(fr_hi)))
        - np.median(rng.choice(fr_lo, len(fr_lo)))
        for _ in range(N_BOOT)]
    keys_lo, keys_hi = list(g_lo), list(g_hi)
    cluster_diffs = []
    for _ in range(N_BOOT):
        pick_lo = rng.choice(len(keys_lo), len(keys_lo))
        pick_hi = rng.choice(len(keys_hi), len(keys_hi))
        m_lo = np.median(np.concatenate([g_lo[keys_lo[i]] for i in pick_lo]))
        m_hi = np.median(np.concatenate([g_hi[keys_hi[i]] for i in pick_hi]))
        cluster_diffs.append(m_hi - m_lo)
    return ci_from_boot(frame_diffs), ci_from_boot(cluster_diffs), \
        len(fr_lo), len(fr_hi)


def main():
    X, bearing, condition, rec = load_frames_full()
    z, margin, k, _ = _fit_primary(
        X, bearing, rec, ['K001', 'K002', 'K003', 'K004'],
        ['K005', 'K006'])
    rng = np.random.default_rng(SEED)
    rows = []
    for ladder_name, ladder in (('inner', INNER_LADDER),
                                ('outer', OUTER_LADDER)):
        groups = {e: group_margins_by_recording(
            margin, z, X, bearing, rec, bs) for e, bs in ladder.items()}
        exts = sorted(ladder)
        for lo, hi in zip(exts[:-1], exts[1:]):
            (f_lo, f_hi), (c_lo, c_hi), n_lo, n_hi = bootstrap_pair(
                groups[lo], groups[hi], rng)
            rows.append(dict(
                ladder=ladder_name, pair=f'{lo}->{hi}',
                n_bearings_lo=len(ladder[lo]), n_bearings_hi=len(ladder[hi]),
                n_recordings_lo=len(groups[lo]),
                n_recordings_hi=len(groups[hi]),
                n_frames_lo=n_lo, n_frames_hi=n_hi,
                frame_ci_lo=f_lo, frame_ci_hi=f_hi,
                cluster_ci_lo=c_lo, cluster_ci_hi=c_hi,
                ordered_frame=f_lo > 0, ordered_cluster=c_lo > 0,
                provenance='post-hoc statistical audit (recording-level '
                           'cluster bootstrap), NOT pre-registered'))
            print(f"{ladder_name} {lo}->{hi}: frame CI "
                  f"[{f_lo:+.1f},{f_hi:+.1f}]  cluster CI "
                  f"[{c_lo:+.1f},{c_hi:+.1f}]  "
                  f"(bearings {len(ladder[lo])}->{len(ladder[hi])}, "
                  f"recordings {len(groups[lo])}->{len(groups[hi])})")
    df = pd.DataFrame(rows)
    os.makedirs(OUT, exist_ok=True)
    df.to_csv(os.path.join(OUT, 'statistical_audit.csv'), index=False)
    print(f"wrote paper_results/statistical_audit.csv "
          f"({len(df)} pairs; K={k}; seed {SEED}, {N_BOOT} resamples)")


if __name__ == '__main__':
    main()
