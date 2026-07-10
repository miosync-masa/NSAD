"""Phase D — H2 on synthetic only (pre-registration amendment), and the
honest characterization that replaced the original hypothesis.

Original H2: 'full covariance ≫ diagonal covariance on contextual
anomalies (the correlation term carries the detection)'. Pre-registered
kill condition: 'diagonal ties full → claim unsupported'.

Measured on the Step-1 anti-phase probe (unknown channel, ll-floor 0.5%):

    full : 100% detection at every K in 1..5
    diag : 0% at K=1, 100% at K>=2

Verdict — H2 strong form FALSIFIED at BIC-matched policy (both select
K=5 and tie at 100%); H2 weak form CONFIRMED at minimal complexity
(K=1: correlation orientation is all that separates 100% from 0%).
Mixture complexity and covariance orientation are *substitutes* for
representing correlated normal support: an axis-aligned mixture can
staircase-hug a correlated ridge given one extra component.

Implication for the paper: what matters is that the SUPPORT GEOMETRY of
normality is captured — by whichever parametrization — reinforcing the
support-boundary framing over any specific covariance structure. Real-
data H2 remains untestable (no contextual events in SKAB/TEP).
"""

import numpy as np
import pytest

from sklearn.mixture import GaussianMixture

from tests.probes.test_contextual_mechanism import N_CAL, _make_series

LL_PERCENTILE = 0.5


def _detection(Xz, core, covariance_type, K):
    g = GaussianMixture(n_components=K, covariance_type=covariance_type,
                        random_state=0, reg_covar=1e-6,
                        max_iter=200).fit(Xz[:N_CAL])
    floor = float(np.percentile(g.score_samples(Xz[:N_CAL]), LL_PERCENTILE))
    return (g.score_samples(Xz)[core] < floor).mean()


@pytest.fixture(scope='module')
def probe():
    rng = np.random.default_rng(42)
    X, core, _ = _make_series(rng)
    cal = X[:N_CAL]
    mu, sd = cal.mean(axis=0), cal.std(axis=0) + 1e-12
    return (X - mu) / sd, core


def test_h2_weak_form_correlation_carries_detection_at_k1(probe):
    """At minimal complexity the correlation term is everything."""
    Xz, core = probe
    assert _detection(Xz, core, 'full', 1) > 0.9
    assert _detection(Xz, core, 'diag', 1) < 0.05


def test_h2_strong_form_falsified_component_substitution(probe):
    """One extra axis-aligned component substitutes for correlation:
    the pre-registered kill condition for H2's strong form fires."""
    Xz, core = probe
    assert _detection(Xz, core, 'diag', 2) > 0.9
    # BIC-matched policy ties (both catch fully at their selected K)
    assert _detection(Xz, core, 'diag', 5) > 0.9
    assert _detection(Xz, core, 'full', 5) > 0.9
