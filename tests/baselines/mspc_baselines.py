"""MSPC (multivariate statistical process control) reference baselines.

The audit baselines demanded by honesty: PCA-SPE (Q statistic) and
Hotelling T² are THE textbook standard for TEP fault detection
(Chiang, Russell & Braatz). Any claim our variants make on TEP/SKAB
must survive comparison against these under the identical label-free
cleanq threshold family — otherwise it is a comparison against a straw
man. Note our joint reconstruction scorer at delay_window=1 IS the SPE
statistic (self-check in tests/probes/test_mspc_sanity.py); the NNNU skeleton
contains classical MSPC as a special case.

Also provides the high-d adaptation of the unknown channel (Phase B):
GMM (K='auto', full covariance) + log-likelihood floor fitted in the
PCA-reduced normal subspace — the support boundary of the described
normal structure, computable at d=52 without violating the full-cov
sample-size guardrail. Frozen defaults throughout; no per-dataset tuning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

try:
    from sklearn.mixture import GaussianMixture
except ImportError as e:      # pragma: no cover
    raise ImportError("mspc_baselines requires scikit-learn") from e

VARIANCE_TARGET = 0.90    # cumulative-variance rule for #components
MAX_COMPONENTS = 20       # cap (disclosed frozen default)


@dataclass
class MSPCModel:
    """PCA subspace with SPE (Q) and Hotelling T² statistics."""
    variance_target: float = VARIANCE_TARGET
    max_components: int = MAX_COMPONENTS
    mean_: Optional[np.ndarray] = field(default=None, repr=False)
    Vk_: Optional[np.ndarray] = field(default=None, repr=False)   # (k, d)
    var_: Optional[np.ndarray] = field(default=None, repr=False)  # (k,) score variances

    def fit(self, train: np.ndarray) -> 'MSPCModel':
        X = np.asarray(train, dtype=np.float64)
        n, d = X.shape
        self.mean_ = X.mean(axis=0)
        Xc = X - self.mean_
        _, s, Vt = np.linalg.svd(Xc, full_matrices=False)
        var = (s ** 2) / max(n - 1, 1)
        cum = np.cumsum(var) / var.sum()
        k = int(np.searchsorted(cum, self.variance_target) + 1)
        k = max(1, min(k, self.max_components, len(var) - 1))
        self.Vk_ = Vt[:k]
        self.var_ = var[:k] + 1e-12
        return self

    @property
    def k(self) -> int:
        return len(self.var_)

    def _scores_resid(self, X: np.ndarray):
        Xc = np.asarray(X, dtype=np.float64) - self.mean_
        scores = Xc @ self.Vk_.T                    # (n, k)
        resid = Xc - scores @ self.Vk_              # (n, d)
        return scores, resid

    def spe(self, X: np.ndarray) -> np.ndarray:
        """Q statistic: squared residual norm off the PCA subspace."""
        _, resid = self._scores_resid(X)
        return (resid ** 2).sum(axis=1)

    def t2(self, X: np.ndarray) -> np.ndarray:
        """Hotelling T²: Mahalanobis distance inside the subspace."""
        scores, _ = self._scores_resid(X)
        return ((scores ** 2) / self.var_).sum(axis=1)


@dataclass
class ReducedUnknown:
    """Unknown channel at high d: GMM + log-likelihood floor in the
    PCA-reduced normal subspace (mirrors RegimeAwareDetector's ll-floor,
    lambda3_detector/regime/regime_detector.py Step 8)."""
    K_max: int = 5
    min_frames_per_regime: int = 50
    random_state: int = 0
    model_: Optional[MSPCModel] = field(default=None, repr=False)
    gmm_: Optional[GaussianMixture] = field(default=None, repr=False)
    K_eff: int = 0

    def fit(self, train: np.ndarray) -> 'ReducedUnknown':
        self.model_ = MSPCModel().fit(train)
        Z, _ = self.model_._scores_resid(train)
        best_bic, best = float('inf'), None
        k_upper = min(self.K_max, max(1, len(Z) // self.min_frames_per_regime))
        for K in range(1, k_upper + 1):
            try:
                g = GaussianMixture(
                    n_components=K, covariance_type='full',
                    random_state=self.random_state, reg_covar=1e-6,
                    max_iter=200,
                ).fit(Z)
            except Exception:
                continue
            sizes = np.bincount(g.predict(Z), minlength=K)
            if sizes.min() < self.min_frames_per_regime:
                continue
            bic = g.bic(Z)
            if bic < best_bic:
                best_bic, best, self.K_eff = bic, g, K
        if best is None:
            best = GaussianMixture(
                n_components=1, covariance_type='full',
                random_state=self.random_state, reg_covar=1e-6,
            ).fit(Z)
            self.K_eff = 1
        self.gmm_ = best
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        """Higher = further outside known normal structure (= -loglik)."""
        Z, _ = self.model_._scores_resid(X)
        return -self.gmm_.score_samples(Z)
