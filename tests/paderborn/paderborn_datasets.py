"""Paderborn (KAt) bearing subset loader — vibration/acoustics adapter.

Data: Paderborn University Bearing Data Center (Lessmeier et al. 2016),
CC BY-NC 4.0, via the laiadc/PFM_Bearing_Fault_Detection GitHub mirror
(official server and Zenodo unreachable from this environment). The
mirror carries a SUBSET: K001 (healthy), KA01 (artificial outer-ring
damage), KI01 (artificial inner-ring damage), each under two operating
conditions (N09_M07_F10: 900 rpm / N15_M07_F10: 1500 rpm), 20
recordings of 4 s each. Channels: vibration_1 and two phase currents
at 64 kHz; force / speed / torque at 4 kHz; bearing temperature slow.

Subset limits, stated up front: ONE healthy bearing (no cross-bearing
healthy holdout — FAR is within-bearing across recordings), artificial
damages only, single damage extent (no severity grading), two of the
four official operating conditions.

Adapter (per §13.2 qualification law — fault-agnostic vocabulary):
each 4 s recording is split into 0.25 s frames; per frame:
  vibration : log RMS, 12 log-spaced band energies (20 Hz-25.6 kHz),
              spectral entropy, 6 envelope band energies (|Hilbert|
              spectrum, 0-1 kHz, log-spaced) — generic envelope
              structure, NOT aligned to any bearing fault frequency
  currents  : log RMS + spectral entropy per phase
  slow      : mean speed, torque, force
d = 27. Frames inherit the recording's (bearing, condition) labels.
"""

from __future__ import annotations

import os
from glob import glob

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'PADERBORN')
CACHE = os.path.join(DATA_DIR, 'frames.npz')

# Full-dataset layout (GitHub Release 'pu-bearing-data'): one flat dir
# per bearing under PADERBORN/full/, files named
# <condition>_<bearing>_<i>.mat with all four official conditions.
FULL_DIR = os.path.join(DATA_DIR, 'full')
FULL_CACHE = os.path.join(DATA_DIR, 'frames_full.npz')
FULL_CONDITIONS = ['N15_M07_F10', 'N09_M07_F10',
                   'N15_M01_F10', 'N15_M07_F04']

FS = 64_000
FRAME_S = 0.25
BEARINGS = ['K001', 'KA01', 'KI01']
CONDITIONS = ['N09', 'N15']

VIB_BANDS = np.logspace(np.log10(20), np.log10(25_600), 13)
ENV_BANDS = np.logspace(np.log10(5), np.log10(1_000), 7)


def _band_energies(x: np.ndarray, fs: float, edges: np.ndarray):
    spec = np.abs(np.fft.rfft(x)) ** 2
    freqs = np.fft.rfftfreq(len(x), 1.0 / fs)
    return np.array([np.log(spec[(freqs >= lo) & (freqs < hi)].sum() + 1e-12)
                     for lo, hi in zip(edges[:-1], edges[1:])])


def _spectral_entropy(x: np.ndarray):
    spec = np.abs(np.fft.rfft(x)) ** 2
    p = spec / (spec.sum() + 1e-12)
    return float(-(p * np.log(p + 1e-12)).sum())


def _frame_features(vib, cur1, cur2, speed, torque, force):
    from scipy.signal import hilbert
    env = np.abs(hilbert(vib))
    feats = [np.log(np.sqrt((vib ** 2).mean()) + 1e-12)]
    feats.extend(_band_energies(vib, FS, VIB_BANDS))
    feats.append(_spectral_entropy(vib))
    feats.extend(_band_energies(env - env.mean(), FS, ENV_BANDS))
    for c in (cur1, cur2):
        feats.append(np.log(np.sqrt((c ** 2).mean()) + 1e-12))
        feats.append(_spectral_entropy(c))
    feats.extend([speed.mean(), torque.mean(), force.mean()])
    return np.array(feats, dtype=np.float64)


def _load_recording(path: str):
    from scipy.io import loadmat
    m = loadmat(path, simplify_cells=True)
    key = [k for k in m if not k.startswith('__')][0]
    ch = {c['Name']: np.asarray(c['Data'], dtype=np.float64).ravel()
          for c in m[key]['Y']}
    return ch


def load_frames(force: bool = False):
    """Returns (X, bearing, condition, rec_id) — one row per frame."""
    if os.path.exists(CACHE) and not force:
        z = np.load(CACHE, allow_pickle=True)
        return z['X'], z['bearing'], z['condition'], z['rec']
    rows, bear, cond, rec = [], [], [], []
    n_frame = int(FRAME_S * FS)
    slow_ratio = 16  # 4 kHz channels
    for b in BEARINGS:
        for c in CONDITIONS:
            for path in sorted(glob(os.path.join(DATA_DIR, b, c, '*.mat'))):
                ch = _load_recording(path)
                vib = ch['vibration_1']
                n = (len(vib) // n_frame) * n_frame
                for i in range(0, n, n_frame):
                    s = slice(i, i + n_frame)
                    sl = slice(i // slow_ratio, (i + n_frame) // slow_ratio)
                    rows.append(_frame_features(
                        vib[s], ch['phase_current_1'][s],
                        ch['phase_current_2'][s], ch['speed'][sl],
                        ch['torque'][sl], ch['force'][sl]))
                    bear.append(b)
                    cond.append(c)
                    rec.append(os.path.basename(path))
    X = np.vstack(rows)
    bear, cond, rec = map(np.array, (bear, cond, rec))
    np.savez_compressed(CACHE, X=X, bearing=bear, condition=cond, rec=rec)
    return X, bear, cond, rec


def load_frames_full(force: bool = False):
    """Full-dataset frames: every bearing dir under PADERBORN/full/.

    Returns (X, bearing, condition, rec_id); condition is the full
    official code (e.g. 'N15_M07_F10'). Same d=27 adapter, unchanged
    (pre-registered protocol, doc/preregistrations/experiment_plan_paderborn.md §3).
    Incremental: re-run with force=True after adding bearing dirs.
    """
    def _finite_filter(X, bear, cond, rec):
        """Drop frames with non-finite features (a handful of full-set
        recordings have slow channels shorter than the vibration
        channel, leaving the last frame's slow slice empty -> NaN).
        Data hygiene of malformed frames, not a feature change."""
        ok = np.isfinite(X).all(axis=1)
        if not ok.all():
            print(f"  dropped {(~ok).sum()} non-finite frames "
                  f"of {len(ok)}")
        return X[ok], bear[ok], cond[ok], rec[ok]

    if os.path.exists(FULL_CACHE) and not force:
        z = np.load(FULL_CACHE, allow_pickle=True)
        return _finite_filter(z['X'], z['bearing'], z['condition'],
                              z['rec'])
    rows, bear, cond, rec = [], [], [], []
    n_frame = int(FRAME_S * FS)
    slow_ratio = 16
    bearings = sorted(d for d in os.listdir(FULL_DIR)
                      if os.path.isdir(os.path.join(FULL_DIR, d)))
    for b in bearings:
        for path in sorted(glob(os.path.join(FULL_DIR, b, '*.mat'))):
            base = os.path.basename(path)
            c = '_'.join(base.split('_')[:3])
            try:
                ch = _load_recording(path)
            except Exception as e:          # noqa: BLE001 — corrupt file
                print(f"  SKIP {base}: {type(e).__name__}")
                continue
            vib = ch['vibration_1']
            n = (len(vib) // n_frame) * n_frame
            for i in range(0, n, n_frame):
                s = slice(i, i + n_frame)
                sl = slice(i // slow_ratio, (i + n_frame) // slow_ratio)
                rows.append(_frame_features(
                    vib[s], ch['phase_current_1'][s],
                    ch['phase_current_2'][s], ch['speed'][sl],
                    ch['torque'][sl], ch['force'][sl]))
                bear.append(b)
                cond.append(c)
                rec.append(base)
    X = np.vstack(rows)
    bear, cond, rec = map(np.array, (bear, cond, rec))
    np.savez_compressed(FULL_CACHE, X=X, bearing=bear, condition=cond,
                        rec=rec)
    return _finite_filter(X, bear, cond, rec)
