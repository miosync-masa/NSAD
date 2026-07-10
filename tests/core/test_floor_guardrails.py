"""Promotion tests: out-of-sample floor + dimensionality guardrail
(architecture.md §13.9). Defaults must remain byte-identical; the
opt-in path must reproduce the guardrail semantics validated in the
experiment path (in-sample percentile bias, measured ×32 at d=52)."""

import numpy as np
import pytest

from lambda3_detector.regime import RegimeAwareDetector


def _clean_stream(rng, n=900, d=24):
    """High-d, modest-n Gaussian stream — the overfit-prone regime
    where the in-sample floor bias is large."""
    A = rng.normal(size=(d, d)) * 0.3
    cov_root = np.eye(d) + A @ A.T * 0.05
    X = rng.normal(size=(n, d)) @ cov_root
    return X


def test_default_floor_is_in_sample_and_unchanged():
    rng = np.random.default_rng(0)
    X = _clean_stream(rng)
    mask = np.zeros(len(X), dtype=bool)
    det = RegimeAwareDetector(K=1, scorer_factories=[], mask_margin=0)
    r = det.fit_predict(X, mask)
    # default path: floor gmm IS the regime gmm, floor is the in-sample
    # percentile of clean ll — recomputed independently here
    clean = (X - det.clean_mu) / det.clean_sd
    expected = float(np.percentile(det.gmm.score_samples(clean), 0.5))
    assert r['ll_floor'] == pytest.approx(expected, rel=1e-12)
    assert det.floor_gmm is det.gmm
    assert r['floor_out_of_sample'] is False
    assert r['floor_dims'] == X.shape[1]


def test_out_of_sample_floor_reduces_false_unknowns_on_fresh_clean():
    """The promoted mechanism: on fresh clean data from the same
    process, the in-sample floor over-fires (its floor sits at the
    optimistic in-sample likelihood scale); the out-of-sample floor
    honors the designed rate far better."""
    rng = np.random.default_rng(1)
    X = _clean_stream(rng, n=900)
    fresh = _clean_stream(rng, n=900)      # same process, unseen
    mask = np.zeros(len(X), dtype=bool)

    rates = {}
    for name, kw in (('in', {}),
                     ('oos', dict(floor_holdout_fraction=0.4))):
        det = RegimeAwareDetector(K=1, scorer_factories=[],
                                  mask_margin=0, **kw)
        det.fit_predict(X, mask)
        Z = (fresh - det.clean_mu) / det.clean_sd
        if det.floor_pca is not None:
            Z = det.floor_pca.transform(Z)
        ll = det.floor_gmm.score_samples(Z)
        rates[name] = float((ll < det.ll_floor).mean())

    design = 0.005
    assert rates['in'] > 3 * design, (
        f"setup not overfit-prone enough: in-sample rate {rates['in']:.4f}")
    assert rates['oos'] < rates['in'] / 2, rates
    assert rates['oos'] < 4 * design, rates


def test_reduce_dims_guardrail_applies_only_above_threshold():
    rng = np.random.default_rng(2)
    X = _clean_stream(rng, n=900, d=24)
    mask = np.zeros(len(X), dtype=bool)
    det = RegimeAwareDetector(K=1, scorer_factories=[], mask_margin=0,
                              floor_holdout_fraction=0.4,
                              floor_reduce_dims=16)
    r = det.fit_predict(X, mask)
    assert det.floor_pca is not None
    assert r['floor_dims'] < 24
    assert r['floor_out_of_sample'] is True
    # regime layer untouched: regime gmm still lives in the original space
    assert det.gmm.means_.shape[1] == 24

    det2 = RegimeAwareDetector(K=1, scorer_factories=[], mask_margin=0,
                               floor_holdout_fraction=0.4,
                               floor_reduce_dims=64)
    r2 = det2.fit_predict(X, mask)
    assert det2.floor_pca is None and r2['floor_dims'] == 24


def test_invalid_fraction_rejected():
    with pytest.raises(ValueError):
        RegimeAwareDetector(floor_holdout_fraction=1.5)
