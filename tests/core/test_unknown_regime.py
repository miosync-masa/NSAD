"""Unknown-regime detection (RegimeAwareDetector) のユニットテスト。

思想: 「わからないときは、未知の身体レジームとして報告する」
  - clean 学習データに存在しない分布の frame は unknown_mask=True / state=2
  - 既知レジーム内の frame は unknown を出さない (false-unknown 率 ≈ unknown_ll_percentile %)
  - 'score'/'binary' (NAB 互換出力) は unknown 検出の影響を受けない
"""

import numpy as np
import pytest

from lambda3_detector.regime import RegimeAwareDetector


@pytest.fixture(scope='module')
def two_regime_with_novel():
    """2 つの正常レジーム + 学習から除外された未知分布セグメント。

    - regime A: N(0, 1)   2000 frames
    - regime B: N(6, 1)   2000 frames
    - novel   : N(30, 0.5) 300 frames — anomaly_mask で学習から除外。
      GMM はこの分布を一切見ないので、predict 時に「未知レジーム」となるべき。
    """
    rng = np.random.default_rng(0)
    regime_a = rng.normal(0.0, 1.0, 2000)
    regime_b = rng.normal(6.0, 1.0, 2000)
    novel = rng.normal(30.0, 0.5, 300)
    events = np.concatenate([regime_a, regime_b, novel])
    mask = np.zeros(len(events), dtype=bool)
    mask[4000:] = True  # novel segment を post-mortem tag として除外
    det = RegimeAwareDetector(K='auto')
    result = det.fit_predict(events, mask)
    return det, result


def test_novel_segment_is_reported_unknown(two_regime_with_novel):
    _, result = two_regime_with_novel
    unknown_rate_novel = result['unknown_mask'][4000:].mean()
    assert unknown_rate_novel > 0.9, (
        f"novel segment should be reported as unknown regime, "
        f"got rate {unknown_rate_novel:.3f}"
    )


def test_known_regimes_stay_quiet(two_regime_with_novel):
    _, result = two_regime_with_novel
    # mask_margin=50 が novel 直前 50 frame を学習から除外するため、
    # 判定対象は margin 手前まで。
    unknown_rate_clean = result['unknown_mask'][:3950].mean()
    assert unknown_rate_clean < 0.02, (
        f"false-unknown rate on known regimes should be ~unknown_ll_percentile%, "
        f"got {unknown_rate_clean:.3f}"
    )


def test_state_semantics(two_regime_with_novel):
    _, result = two_regime_with_novel
    state = result['state']
    binary = result['binary']
    unknown = result['unknown_mask']
    # state=2 ⇔ unknown (unknown は binary に優先)
    assert np.array_equal(state == 2, unknown)
    # unknown でない frame では state == binary
    assert np.array_equal(state[~unknown], binary[~unknown])
    assert set(np.unique(state)).issubset({0, 1, 2})


def test_nab_compatible_outputs_untouched(two_regime_with_novel):
    _, result = two_regime_with_novel
    # binary は score の閾値 1.0 のみから決まる (unknown は混入しない)
    assert np.array_equal(
        result['binary'], (result['score'] >= 1.0).astype(np.int32)
    )


def test_diagnostic_outputs_well_formed(two_regime_with_novel):
    det, result = two_regime_with_novel
    n = len(result['score'])
    assert result['log_likelihood'].shape == (n,)
    assert result['regime_confidence'].shape == (n,)
    assert np.isfinite(result['ll_floor'])
    assert det.ll_floor == result['ll_floor']
    conf = result['regime_confidence']
    assert conf.min() >= 0.0 and conf.max() <= 1.0 + 1e-9
    # novel segment の尤度は floor を大きく割る
    assert np.median(result['log_likelihood'][4000:]) < result['ll_floor']
