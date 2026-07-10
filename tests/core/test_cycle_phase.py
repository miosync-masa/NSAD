"""Mechanism test: why frequency-magnitude features cannot see a
switching lag, and why cycle-phase features can.

A pure time lag inside a periodic cycle is a circular shift. The
amplitude spectrum |FFT| is exactly invariant under circular shifts —
the lag lives entirely in the (discarded) phase of the spectrum. So
the legacy frequency features (freq_peak, freq_energy, freq_centroid,
freq_entropy — all built from |FFT|) are structurally blind to it,
while the phase-profile features move monotonically with the lag.

This is the observability statement behind the hydraulic valve finding
(doc/explorations/hydraulic_exploration.md): fault = timing shift, features =
cycle-level magnitudes -> invisible, by mathematics rather than by bad
luck.
"""

import numpy as np
import pytest

from lambda3_detector.features.extractor import (
    Lambda3FeatureExtractor, extract_cycle_phase_features)


def _cycle(lag: int, n: int = 600) -> np.ndarray:
    """One 'switching' cycle: baseline, ramp up after the (lagged)
    switching instant, plateau, release. Lag shifts timing only."""
    x = np.zeros(n)
    a, b = 100 + lag, 250 + lag
    x[a:b] = np.linspace(0, 1, b - a)
    x[b:b + 200] = 1.0
    x[b + 200:] = np.linspace(1, 0, n - b - 200)
    return x


LAGS = [0, 20, 40, 80]


def test_fft_magnitude_blind_to_pure_circular_shift():
    base = _cycle(0)
    fx = Lambda3FeatureExtractor()
    f0 = fx._extract_frequency_features_from_path(base)
    for lag in LAGS[1:]:
        shifted = np.roll(base, lag)          # pure lag, exact
        f1 = fx._extract_frequency_features_from_path(shifted)
        for k in ('freq_peak', 'freq_peak_amp', 'freq_energy',
                  'freq_centroid', 'freq_entropy'):
            assert f1[k] == pytest.approx(f0[k], rel=1e-9), (k, lag)


def test_phase_features_move_monotonically_with_lag():
    rises, peaks = [], []
    for lag in LAGS:
        f = extract_cycle_phase_features(np.roll(_cycle(0), lag))
        rises.append(float(f['rise_time']))
        peaks.append(float(f['peak_pos']))
    assert all(rises[i] < rises[i + 1] for i in range(len(rises) - 1)), rises
    assert all(peaks[i] < peaks[i + 1] for i in range(len(peaks) - 1)), peaks


def test_phase_profile_separates_what_magnitude_collapses():
    base, shifted = _cycle(0), np.roll(_cycle(0), 40)
    pb = extract_cycle_phase_features(base)['phase_mean']
    ps = extract_cycle_phase_features(shifted)['phase_mean']
    assert np.abs(pb - ps).max() > 0.2      # profile clearly displaced


def test_batch_matches_single():
    X = np.stack([_cycle(0), np.roll(_cycle(0), 40)])
    fb = extract_cycle_phase_features(X)
    f0 = extract_cycle_phase_features(X[0])
    np.testing.assert_allclose(fb['phase_mean'][0], f0['phase_mean'])
    assert fb['rise_time'].shape == (2,)
