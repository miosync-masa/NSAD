"""UCI/ZeMA 'Condition Monitoring of Hydraulic Systems' loader.

Physical test rig (Helwig, Pignanelli, Schuetze 2015): a hydraulic
circuit driven in constant 60-second load cycles while the condition of
four components is varied over a grid — cooler efficiency (100/20/3%),
valve switching behavior (100/90/80/73%), internal pump leakage
(0/1/2), accumulator pre-charge (130/115/100/90 bar) — plus a
stable-conditions flag. 2205 cycles, 17 sensors at 1/10/100 Hz.
CC BY 4.0. Obtained from the Machine-Learning-FGA/Hydraulic-systems
mirror of the UCI archive (data identical; UCI id 447).

Layout expected under HYDRAULIC/ (gitignored):
    PS1..PS6.txt EPS1.txt FS1.txt FS2.txt TS1..TS4.txt VS1.txt
    CE.txt CP.txt SE.txt profile.txt

Frame convention: ONE FRAME PER CYCLE — each 60 s cycle is summarized
by the per-cycle mean of each sensor, giving a (2205, 17) stream in
cycle order. This is deliberately the crudest honest summary (no
transient/shape features); whatever it cannot see is reported as a
finding, not hidden.

Key structural fact (measured here, drives the experiment design):
only 10 of 2205 cycles have ALL components nominal, because the rig
varies components simultaneously. "Normal" must therefore be defined
per target component: cycles where the TARGET is nominal — with the
other components' states treated as operating conditions to be
absorbed by the regime layer — exactly the regime-resolved
normal-structure setting.
"""

from __future__ import annotations

import os

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'HYDRAULIC')
CACHE = os.path.join(DATA_DIR, 'cycle_means.npz')

SENSORS = ['PS1', 'PS2', 'PS3', 'PS4', 'PS5', 'PS6', 'EPS1',
           'FS1', 'FS2', 'TS1', 'TS2', 'TS3', 'TS4', 'VS1',
           'CE', 'CP', 'SE']

PROFILE_COLS = ['cooler', 'valve', 'leak', 'accumulator', 'stable']
NOMINAL = {'cooler': 100.0, 'valve': 100.0, 'leak': 0.0,
           'accumulator': 130.0}
# degradation stages ordered mild -> severe
STAGES = {
    'cooler': [20.0, 3.0],
    'valve': [90.0, 80.0, 73.0],
    'leak': [1.0, 2.0],
    'accumulator': [115.0, 100.0, 90.0],
}


def load_cycle_means(force: bool = False, features: str = 'mean'):
    """Per-cycle summary frames.

    features='mean'    -> X (2205, 17): per-cycle mean of each sensor.
    features='meanstd' -> X (2205, 34): mean AND within-cycle std of
        each sensor — std is a generic dispersion summary (fault-
        agnostic; NOT a valve-specific transient feature), the smallest
        step up in within-cycle granularity.
    """
    if os.path.exists(CACHE) and not force:
        z = np.load(CACHE)
        means, stds, segs = z['X'], z['S'], z['G']
        pbins, pshape, profile = z['PB'], z['PH'], z['profile']
    else:
        import pandas as pd
        from lambda3_detector.features.extractor import \
            extract_cycle_phase_features
        mcols, scols, gcols, pbcols, phcols = [], [], [], [], []
        for name in SENSORS:
            m = pd.read_csv(os.path.join(DATA_DIR, f'{name}.txt'),
                            sep='\t', header=None,
                            dtype=np.float64).to_numpy()
            mcols.append(m.mean(axis=1))
            scols.append(m.std(axis=1))
            # 6 equal within-cycle segments (phase-resolved means):
            # fault-agnostic granularity, no alignment to any component
            seg = m.reshape(m.shape[0], 6, -1).mean(axis=2)
            gcols.append(seg)
            # cycle-phase features (lambda3_detector.features.extractor):
            # 12-bin phase profile + timing vocabulary — the information
            # |FFT| discards (tests/core/test_cycle_phase.py)
            f = extract_cycle_phase_features(m, n_bins=12)
            pbcols.append(f['phase_mean'])
            phcols.append(np.column_stack([
                f['peak_pos'], f['trough_pos'],
                f['rise_time'], f['settle_time']]))
        means, stds = np.column_stack(mcols), np.column_stack(scols)
        segs = np.hstack(gcols)
        pbins, pshape = np.hstack(pbcols), np.hstack(phcols)
        profile = np.loadtxt(os.path.join(DATA_DIR, 'profile.txt'))
        np.savez_compressed(CACHE, X=means, S=stds, G=segs,
                            PB=pbins, PH=pshape, profile=profile)
    if features == 'mean':
        return means, profile
    if features == 'meanstd':
        return np.hstack([means, stds]), profile
    if features == 'seg6':
        return segs, profile
    if features == 'phase12':
        return pbins, profile
    if features == 'shape':
        return pshape, profile
    if features == 'phase12shape':
        return np.hstack([pbins, pshape]), profile
    raise ValueError(features)


def target_split(target: str, stable_only: bool = True):
    """Normal/degraded index sets for one target component.

    normal   : target at nominal (other components ARE allowed to vary —
               they are operating conditions, i.e. regimes)
    degraded : dict stage-value -> indices (same stability filter)
    """
    _, profile = load_cycle_means()
    col = PROFILE_COLS.index(target)
    stable = (profile[:, 4] == 0) if stable_only else np.ones(
        len(profile), dtype=bool)
    normal = np.where((profile[:, col] == NOMINAL[target]) & stable)[0]
    degraded = {s: np.where((profile[:, col] == s) & stable)[0]
                for s in STAGES[target]}
    return normal, degraded
