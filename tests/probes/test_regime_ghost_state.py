"""Phase C — the regime layer's crisp demonstration: the ghost state.

A bimodal process (load plateaus at c≈0.3 and c≈0.7, temperature follows
with thermal lag) develops a fault that parks it at c≈0.5, T≈40 — the
"forbidden middle": coupling-consistent, both marginals mid-band, but an
operating point that NEVER occurs in steady normal operation (e.g. a
valve stuck at mid-travel).

Single-model statistics are structurally blind to it: the global
Gaussian's mean sits between the modes, so the ghost state has an
UNUSUALLY LOW Mahalanobis distance (T² sees it as the most normal point
in the file), and the global PCA line passes through it (SPE ≈ 0).
The multi-regime support boundary (GMM K='auto' by BIC + log-likelihood
floor — the unknown channel) sees it as outside every known regime.

This is the K=1-degeneration result from the MSPC audit, inverted into
a positive: Hotelling T² is the unknown channel's K=1 special case, and
the ghost state is exactly where the general case parts ways with it.
Positioning stays modest (multimode monitoring has GMM prior art); the
demonstration is that the NNNU skeleton exhibits this with zero new
machinery.
"""

import numpy as np
import pytest

from sklearn.mixture import GaussianMixture

from tests.baselines.mspc_baselines import MSPCModel

N_CAL = 4000
MODE_LEN = 800
TAU_T = 25.0
NOISE_C = 0.02
NOISE_T = 0.4
GHOST_START = 5200        # inside the test span, mid-plateau
GHOST_LEN = 200
LL_PERCENTILE = 0.5       # frozen unknown-floor default


def _make_series(rng, n=6000):
    mode = (np.arange(n) // MODE_LEN) % 2
    c_target = np.where(mode == 0, 0.3, 0.7).astype(np.float64)
    # ghost fault: stuck at mid-travel
    c_target[GHOST_START:GHOST_START + GHOST_LEN] = 0.5
    c = c_target + NOISE_C * rng.normal(size=n)
    T = np.zeros(n)
    T[0] = 20.0 + 40.0 * c[0]
    for t in range(1, n):
        T_ss = 20.0 + 40.0 * c[t]
        T[t] = T[t - 1] + (T_ss - T[t - 1]) / TAU_T
    T = T + NOISE_T * rng.normal(size=n)
    X = np.column_stack([c, T])
    core = slice(GHOST_START + 50, GHOST_START + GHOST_LEN)  # settled ghost
    return X, core


@pytest.fixture(scope='module')
def rig():
    rng = np.random.default_rng(11)
    X, core = _make_series(rng)
    cal = X[:N_CAL]
    mu, sd = cal.mean(axis=0), cal.std(axis=0) + 1e-12
    Xz = (X - mu) / sd
    return X, Xz, core


def _fit_gmm(train, K):
    return GaussianMixture(n_components=K, covariance_type='full',
                           random_state=0, reg_covar=1e-6,
                           max_iter=200).fit(train)


def _fit_gmm_auto(train, K_max=5, min_frames=50):
    best, best_bic, k_eff = None, float('inf'), 1
    for K in range(1, K_max + 1):
        g = _fit_gmm(train, K)
        if np.bincount(g.predict(train), minlength=K).min() < min_frames:
            continue
        b = g.bic(train)
        if b < best_bic:
            best, best_bic, k_eff = g, b, K
    return best, k_eff


def test_ghost_is_contextual(rig):
    """Both marginals stay mid-band during the ghost (chance-level rule)."""
    X, _, core = rig
    cal = X[:N_CAL]
    lo = np.quantile(cal, 0.005, axis=0)
    hi = np.quantile(cal, 0.995, axis=0)
    seg = X[core]
    for ch in (0, 1):
        out = (seg[:, ch] < lo[ch]) | (seg[:, ch] > hi[ch])
        assert out.mean() <= 0.02, f"ghost leaves marginal band on ch{ch}"


def test_global_t2_blind_even_sees_ghost_as_normal(rig):
    """Global single-Gaussian T² assigns the ghost BELOW-median distance:
    single-model MSPC is not merely weak here, it is inverted."""
    _, Xz, core = rig
    g1 = _fit_gmm(Xz[:N_CAL], 1)
    nll = -g1.score_samples(Xz)              # monotone in global T²
    floor = float(np.quantile(-g1.score_samples(Xz[:N_CAL]), 0.995))
    assert (nll[core] > floor).mean() < 0.05, \
        "global single-Gaussian unexpectedly flags the ghost"
    assert np.median(nll[core]) < np.median(nll[:N_CAL]), \
        "ghost should look MORE normal than average to the global model"


def test_global_spe_blind(rig):
    """Global PCA SPE ≈ 0 on the ghost (it lies on the global line)."""
    _, Xz, core = rig
    m = MSPCModel().fit(Xz[:N_CAL])
    spe = m.spe(Xz)
    tau = float(np.quantile(m.spe(Xz[:N_CAL]), 0.995))
    assert (spe[core] > tau).mean() < 0.05, \
        "global SPE unexpectedly flags the ghost"


def test_multiregime_unknown_catches_ghost(rig):
    """The multi-regime support boundary flags the ghost; BIC picks K>=2."""
    _, Xz, core = rig
    gmm, k_eff = _fit_gmm_auto(Xz[:N_CAL])
    assert k_eff >= 2, f"BIC failed to find the modes (K_eff={k_eff})"
    ll_cal = gmm.score_samples(Xz[:N_CAL])
    floor = float(np.percentile(ll_cal, LL_PERCENTILE))
    unknown = gmm.score_samples(Xz) < floor
    assert unknown[core].mean() > 0.8, (
        f"multi-regime unknown channel caught only "
        f"{unknown[core].mean():.0%} of ghost frames"
    )
    # specificity: quiet on normal frames outside the ghost
    normal = np.ones(len(Xz), dtype=bool)
    normal[GHOST_START - 100:GHOST_START + GHOST_LEN + 100] = False
    normal[:N_CAL] = False
    assert unknown[normal].mean() < 0.03
