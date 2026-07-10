"""Promotion tests: vibration adapter (§13.9).

The package implementation must be numerically identical to the
versions the pre-registered runs froze (Paderborn #1–#3 helpers and
the IMS #4 sample-rate-generic form)."""

import numpy as np

from lambda3_detector.adapters import vibration_features
from lambda3_detector.adapters.vibration import (band_energies,
                                                 spectral_entropy)


def test_identical_to_ims_frozen_implementation():
    from tests.ims.ims_datasets import vib_features as frozen
    rng = np.random.default_rng(0)
    for fs in (20_480.0, 64_000.0, 250.0):
        frame = rng.normal(size=4096)
        np.testing.assert_allclose(
            vibration_features(frame, fs), frozen(frame, fs), rtol=1e-12)


def test_identical_to_paderborn_frozen_helpers():
    from tests.paderborn.paderborn_datasets import (ENV_BANDS, VIB_BANDS,
                                                    _band_energies,
                                                    _spectral_entropy)
    rng = np.random.default_rng(1)
    x = rng.normal(size=16_000)
    np.testing.assert_allclose(
        band_energies(x, 64_000.0, VIB_BANDS),
        _band_energies(x, 64_000.0, VIB_BANDS), rtol=1e-12)
    assert spectral_entropy(x) == _spectral_entropy(x)


def test_dimension_contract():
    rng = np.random.default_rng(2)
    assert vibration_features(rng.normal(size=5120), 20_480.0).shape == (20,)
