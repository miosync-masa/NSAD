"""Self-check: our joint reconstruction scorer at delay_window=1 IS the
MSPC SPE (Q) statistic — same subspace-residual construction. The audit
comparison is only meaningful if this identity holds numerically."""

import numpy as np

from lambda3_detector.streaming import StreamingReconstructionScorer
from tests.baselines.mspc_baselines import MSPCModel


def test_recon_w1_is_spe():
    rng = np.random.default_rng(3)
    # correlated 6-channel normal data
    B = rng.normal(size=(6, 3))
    train = rng.normal(size=(400, 3)) @ B.T + 0.1 * rng.normal(size=(400, 6))
    test = rng.normal(size=(200, 3)) @ B.T + 0.1 * rng.normal(size=(200, 6))
    test[50:60] += rng.normal(size=(10, 6)) * 2.0   # some off-structure frames

    m = MSPCModel(variance_target=0.9, max_components=5).fit(train)
    spe = np.sqrt(m.spe(test))          # residual NORM (scorer convention)

    s = StreamingReconstructionScorer(n_components=m.k, delay_window=1)
    s.calibrate(train)
    recon = np.array([s.score(test, t) for t in range(len(test))])

    corr = np.corrcoef(spe, recon)[0, 1]
    assert corr > 0.99, f"recon(W=1) should be the SPE statistic, corr={corr:.4f}"
