"""Vibration/acoustics adapter — the fault-agnostic vibration vocabulary.

Promoted from the experiment path after validation on the Paderborn
cross-sectional arc (pre-registrations #1–#3) and the NASA IMS
run-to-failure arc (pre-registration #4); the implementation is
numerically identical to the version those pre-registered runs froze
(regression-tested in tests/core/test_vibration_adapter.py).

Vocabulary, expressed sample-rate-independently (per channel, d=20):
  - log RMS
  - 12 log-spaced band energies, 20 Hz → 0.8 × Nyquist
  - spectral entropy
  - 6 GENERIC envelope band energies (|Hilbert| spectrum),
    5 Hz → min(1 kHz, 0.8 × Nyquist)

Qualification law (architecture.md §13.2): nothing here is aligned to
any fault frequency (no BPFO/BPFI or fault-class structure) — the
vocabulary speaks about structure, never about faults.
"""

from __future__ import annotations

import numpy as np

__all__ = ['vibration_features', 'vibration_bands', 'envelope_bands',
           'spectral_entropy', 'band_energies']


def vibration_bands(fs: float) -> np.ndarray:
    """12 log-spaced band edges from 20 Hz to 0.8 x Nyquist."""
    return np.logspace(np.log10(20.0), np.log10(0.8 * fs / 2.0), 13)


def envelope_bands(fs: float) -> np.ndarray:
    """6 log-spaced envelope band edges, 5 Hz to min(1 kHz, 0.8 x Nyquist)."""
    hi = min(1000.0, 0.8 * fs / 2.0)
    return np.logspace(np.log10(5.0), np.log10(hi), 7)


def band_energies(x: np.ndarray, fs: float, edges: np.ndarray) -> np.ndarray:
    spec = np.abs(np.fft.rfft(x)) ** 2
    freqs = np.fft.rfftfreq(len(x), 1.0 / fs)
    return np.array([np.log(spec[(freqs >= lo) & (freqs < hi)].sum() + 1e-12)
                     for lo, hi in zip(edges[:-1], edges[1:])])


def spectral_entropy(x: np.ndarray) -> float:
    spec = np.abs(np.fft.rfft(x)) ** 2
    p = spec / (spec.sum() + 1e-12)
    return float(-(p * np.log(p + 1e-12)).sum())


def vibration_features(frame: np.ndarray, fs: float) -> np.ndarray:
    """d=20 per channel: the sample-rate-generic vibration vocabulary."""
    from scipy.signal import hilbert
    env = np.abs(hilbert(frame))
    feats = [np.log(np.sqrt((frame ** 2).mean()) + 1e-12)]
    feats.extend(band_energies(frame, fs, vibration_bands(fs)))
    feats.append(spectral_entropy(frame))
    feats.extend(band_energies(env - env.mean(), fs, envelope_bands(fs)))
    return np.array(feats, dtype=np.float64)
