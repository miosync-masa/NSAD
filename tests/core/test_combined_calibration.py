"""combined-ratio calibration (calibrate_combined) のユニットテスト。

per-scorer percentile threshold の OR 投票は familywise フラグ率を
scorer 数分積み上げる (6 scorer × p99 → clean 上 ~6%)。
calibrate_combined=True は OR 出力の clean 分布から最終判定境界を
導出し直し、clean 上のフラグ率を ≈(100-percentile)% に回復する。
"""

import numpy as np
import pytest

from lambda3_detector.regime import RegimeAwareDetector, expand_anomaly_mask


@pytest.fixture(scope='module')
def two_regime_with_spikes():
    """2 正常レジーム + 大振幅スパイク異常 (mask 済み)。"""
    rng = np.random.default_rng(1)
    regime_a = rng.normal(0.0, 1.0, 3000)
    regime_b = rng.normal(6.0, 1.0, 3000)
    events = np.concatenate([regime_a, regime_b])
    mask = np.zeros(len(events), dtype=bool)
    spike_at = [1500, 4500]
    for i in spike_at:
        events[i:i + 5] += 15.0   # 正常構造から大きく逸脱するスパイク
        mask[i:i + 5] = True
    return events, mask, spike_at


def _run(events, mask, cal):
    det = RegimeAwareDetector(K='auto', calibrate_combined=cal)
    return det, det.fit_predict(events, mask)


def test_clean_flag_rate_reduced(two_regime_with_spikes):
    events, mask, _ = two_regime_with_spikes
    expanded = expand_anomaly_mask(mask, 50)
    _, r_off = _run(events, mask, cal=False)
    _, r_on = _run(events, mask, cal=True)
    rate_off = r_off['binary'].astype(bool)[~expanded].mean()
    rate_on = r_on['binary'].astype(bool)[~expanded].mean()
    # OR 積み上げ (>2%) → 校正後は percentile=99 相当の ~1% 台へ
    assert rate_off > 0.02, f"uncalibrated rate unexpectedly low: {rate_off:.3%}"
    assert rate_on < rate_off / 2, (
        f"calibration should at least halve clean flag rate "
        f"({rate_off:.3%} -> {rate_on:.3%})"
    )
    assert rate_on < 0.03


def test_large_deviations_still_caught(two_regime_with_spikes):
    events, mask, spike_at = two_regime_with_spikes
    _, r_on = _run(events, mask, cal=True)
    flags = r_on['binary'].astype(bool)
    for i in spike_at:
        assert flags[i:i + 5].any(), f"spike at {i} lost after calibration"


def test_tau_reported_and_sane(two_regime_with_spikes):
    events, mask, _ = two_regime_with_spikes
    det, r_on = _run(events, mask, cal=True)
    taus = r_on['combined_tau']
    assert set(taus.keys()) == set(range(r_on['K_eff']))
    for tau in taus.values():
        assert 1.0 <= tau < 20.0   # OR 積み上げ係数: 1 以上、常識的範囲
    # 校正は score の単調変換 (regime 内) — binary は score>=1 と一致
    assert np.array_equal(
        r_on['binary'], (r_on['score'] >= 1.0).astype(np.int32))


def test_default_behavior_unchanged(two_regime_with_spikes):
    events, mask, _ = two_regime_with_spikes
    _, r_off = _run(events, mask, cal=False)
    assert all(v == 1.0 for v in r_off['combined_tau'].values())
