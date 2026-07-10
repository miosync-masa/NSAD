"""NASA IMS run-to-failure bearing loader + Milling loader.

IMS Bearing Data Set (J. Lee, H. Qiu, G. Yu, J. Lin, and Rexnord
Technical Services; IMS Center, University of Cincinnati) and Milling
Data Set (A. Agogino, K. Goebel; BEST Lab, UC Berkeley), both from the
NASA Prognostics Data Repository, NASA Ames Research Center — used
with acknowledgment per the repository's request.

IMS layout under IMS/ (gitignored): 1st_test/ (2156 snapshots, 8
channels = 2 per bearing), 2nd_test/ (984 snapshots, 4 channels),
4th_test/txt/ (test 3 as shipped, 6324 snapshots, 4 channels). Each
snapshot file: 20480 rows (1 s @ 20.48 kHz), tab-separated columns,
filename = timestamp. Failures: test1 bearing 3 (inner race) and
bearing 4 (roller); test2 bearing 1 (outer race); test3 bearing 3
(reported; descriptive only per pre-registration).

Adapter: the fault-agnostic vibration vocabulary of
tests/paderborn/paderborn_datasets.py expressed sample-rate-independently
(pre-registered §1): per channel — log RMS, 12 log band energies
20 Hz → 0.8×Nyquist, spectral entropy, 6 envelope band energies
5 Hz → min(1000, 0.8×Nyquist). Frames: 0.25 s (5120 samples).
"""

from __future__ import annotations

import os
from datetime import datetime
from glob import glob

import numpy as np

from tests.paderborn.paderborn_datasets import _band_energies, _spectral_entropy

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'IMS')
MILL_MAT = os.path.join(os.path.dirname(__file__), '..', '..', 'MILLING',
                        'mill.mat')

FS = 20_480
FRAME = 5_120                     # 0.25 s

TESTS = {
    'test1': dict(subdir='1st_test', n_ch=8,
                  bearings={1: (0, 1), 2: (2, 3), 3: (4, 5), 4: (6, 7)},
                  failed=[3, 4]),
    'test2': dict(subdir='2nd_test', n_ch=4,
                  bearings={1: (0,), 2: (1,), 3: (2,), 4: (3,)},
                  failed=[1]),
    'test3': dict(subdir=os.path.join('4th_test', 'txt'), n_ch=4,
                  bearings={1: (0,), 2: (1,), 3: (2,), 4: (3,)},
                  failed=[3]),
}


def _vib_bands(fs):
    return np.logspace(np.log10(20), np.log10(0.8 * fs / 2), 13)


def _env_bands(fs):
    hi = min(1000.0, 0.8 * fs / 2)
    return np.logspace(np.log10(5), np.log10(hi), 7)


def vib_features(frame: np.ndarray, fs: float) -> np.ndarray:
    """d=20 per channel: the sample-rate-generic vibration vocabulary."""
    from scipy.signal import hilbert
    env = np.abs(hilbert(frame))
    feats = [np.log(np.sqrt((frame ** 2).mean()) + 1e-12)]
    feats.extend(_band_energies(frame, fs, _vib_bands(fs)))
    feats.append(_spectral_entropy(frame))
    feats.extend(_band_energies(env - env.mean(), fs, _env_bands(fs)))
    return np.array(feats, dtype=np.float64)


def _snap_time(name: str) -> float:
    """Filename timestamp -> hours since epoch."""
    return datetime.strptime(name, '%Y.%m.%d.%H.%M.%S').timestamp() / 3600


def load_ims_test(test: str, force: bool = False):
    """Returns (frames: {bearing: (n_snap*4, d)}, times_h: (n_snap,)).

    Snapshots sorted by timestamp; each contributes 4 frames in order.
    """
    cfg = TESTS[test]
    cache = os.path.join(DATA_DIR, f'{test}_frames.npz')
    if os.path.exists(cache) and not force:
        z = np.load(cache, allow_pickle=True)
        return ({b: z[f'b{b}'] for b in cfg['bearings']}, z['times'])
    import pandas as pd
    paths = sorted(glob(os.path.join(DATA_DIR, cfg['subdir'], '2*')))
    times, per_b = [], {b: [] for b in cfg['bearings']}
    n_frames = (20480 // FRAME)
    for p in paths:
        try:
            arr = pd.read_csv(p, sep=r'\s+', header=None,
                              dtype=np.float64).to_numpy()
        except Exception as e:            # noqa: BLE001
            print(f"  SKIP {os.path.basename(p)}: {type(e).__name__}")
            continue
        if arr.shape[0] < 20480 or arr.shape[1] != cfg['n_ch']:
            print(f"  SKIP {os.path.basename(p)}: shape {arr.shape}")
            continue
        times.append(_snap_time(os.path.basename(p)))
        for b, chans in cfg['bearings'].items():
            for i in range(n_frames):
                seg = arr[i * FRAME:(i + 1) * FRAME]
                per_b[b].append(np.concatenate(
                    [vib_features(seg[:, c], FS) for c in chans]))
    frames = {b: np.vstack(v) for b, v in per_b.items()}
    np.savez_compressed(cache, times=np.array(times),
                        **{f'b{b}': v for b, v in frames.items()})
    return frames, np.array(times)


# ---------------------------------------------------------------- milling
MILL_FS = 250.0
MILL_FRAME = 1000     # 4 s — declared framing for the descriptive M study


def load_milling():
    """Returns list of dicts: case, run, VB (nan if unrecorded),
    frames (9, 40) using vib_table + vib_spindle."""
    from scipy.io import loadmat
    d = loadmat(MILL_MAT, simplify_cells=True)['mill']
    out = []
    for r in d:
        sig = np.column_stack([r['vib_table'], r['vib_spindle']])
        if not np.isfinite(sig).all():
            continue
        fr = []
        for i in range(len(sig) // MILL_FRAME):
            seg = sig[i * MILL_FRAME:(i + 1) * MILL_FRAME]
            fr.append(np.concatenate(
                [vib_features(seg[:, c], MILL_FS) for c in (0, 1)]))
        vb = float(r['VB']) if np.ndim(r['VB']) == 0 else np.nan
        out.append(dict(case=int(r['case']), run=int(r['run']),
                        VB=vb, frames=np.vstack(fr)))
    return out
