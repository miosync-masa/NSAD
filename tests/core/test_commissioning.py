"""Promotion tests: per-unit healthy commissioning (E3, §13.9).

Faithfulness: the promoted implementation must equal the math the
pre-registered #3 run froze (tests/paderborn/exp_paderborn3.AlarmE3).
Property: a unit whose clean log-likelihood differs in location AND
scale is admitted at ~the designed rate after commissioning, while the
raw shared floor massively over-fires on it."""

import numpy as np
import pytest

from lambda3_detector.regime import commission_unit


def test_faithful_to_preregistered_e3_math():
    rng = np.random.default_rng(0)
    ref = rng.normal(-10, 2, size=4000)
    com = rng.normal(-25, 6, size=512)
    ll = rng.normal(-25, 6, size=1000)

    c = commission_unit(ref, com)
    got = c.standardize(ll)

    # the AlarmE3 formula, inline (exp_paderborn3, frozen at c61f061)
    iqr = lambda a: abs(float(np.subtract(*np.percentile(a, [75, 25]))))
    loc, scale = float(np.median(com)), iqr(com) + 1e-12
    med_ref, iqr_ref = float(np.median(ref)), iqr(ref) + 1e-12
    expected = (ll - loc) / scale * iqr_ref + med_ref
    np.testing.assert_allclose(got, expected, rtol=1e-12)

    floor = float(np.quantile(ref, 0.005))
    np.testing.assert_allclose(
        c.alarm_margin(ll, floor), (floor - expected) / iqr_ref,
        rtol=1e-12)


def test_commissioning_admits_shifted_and_scaled_unit():
    rng = np.random.default_rng(1)
    ref = rng.normal(-10, 2, size=8000)
    floor = float(np.quantile(ref, 0.005))

    # a healthy unit with different baseline location AND dispersion
    unit_clean = rng.normal(-30, 7, size=6000)
    com, fresh = unit_clean[:512], unit_clean[512:]

    raw_far = float((fresh < floor).mean())
    assert raw_far > 0.5            # the shared floor rejects the unit

    c = commission_unit(ref, com)
    far = float((c.alarm_margin(fresh, floor) > 0).mean())
    assert far == pytest.approx(0.005, abs=0.006)   # admitted at design


def test_role_boundary_documented():
    """The #4 boundary must ship with the code, not only the docs."""
    import lambda3_detector.regime.commissioning as m
    doc = (m.__doc__ or '') + (m.UnitCommissioning.alarm_margin.__doc__ or '')
    assert 'failure alarm' in doc and 'INVALID' in m.__doc__
