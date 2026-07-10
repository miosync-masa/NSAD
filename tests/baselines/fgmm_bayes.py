"""FGMM-Bayes opponent — reconstruction of Yu & Qin (2008), AIChE J.
54(7):1811-1829: multimode monitoring with a finite Gaussian mixture and
a Bayesian-inference probability index, validated on TEP.

DISCLOSURE (reconstruction, not reproduction): the paper is paywalled;
secondary sources confirm the structure — posterior probabilities
P(k|x) of each sample belonging to each Gaussian component, combined
into an integrated global probabilistic index — but not the exact local
term. We therefore implement BOTH plausible readings and duel against
whichever is stronger on each rig (adversarial fairness):

  bip(X)       Σ_k P(k|x) · F_chi2_d(D²_k(x))   — posterior-weighted
               within-component Mahalanobis probability (the standard
               reconstruction used by follow-up papers; ∈ [0,1])
  min_maha(X)  min_k D²_k(x)                     — the alternative
               reading (pure nearest-component distance)

Component-count selection: Yu-Qin use Figueiredo-Jain (single-pass
pruning); we use BIC over K=1..K_max — a different selector with the
same goal. The duel tests the INDEX, not the selector. Note honestly:
BIC×K runs EM K_max times, so our TRAINING is likely heavier than F-J;
inference cost of BIP and of our raw mixture log-likelihood is the same
O(K·d²) family (both evaluate all K Gaussians; Bayes only normalizes).

The contrast under test: BIP/posterior indices normalize across
components; our unknown channel thresholds the UN-normalized mixture
density (support floor). The duel asks whether that difference matters
in inter-mode low-density valleys (ghost states) and on real multimode
data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy.stats import chi2
from sklearn.mixture import GaussianMixture


@dataclass
class FGMMBayes:
    K_max: int = 5
    min_frames_per_regime: int = 50
    random_state: int = 0
    gmm_: Optional[GaussianMixture] = field(default=None, repr=False)
    K_eff: int = 0
    d_: int = 0

    def fit(self, train: np.ndarray) -> 'FGMMBayes':
        X = np.asarray(train, dtype=np.float64)
        self.d_ = X.shape[1]
        best, best_bic = None, float('inf')
        k_upper = min(self.K_max,
                      max(1, len(X) // self.min_frames_per_regime))
        for K in range(1, k_upper + 1):
            try:
                g = GaussianMixture(
                    n_components=K, covariance_type='full',
                    random_state=self.random_state, reg_covar=1e-6,
                    max_iter=200,
                ).fit(X)
            except Exception:
                continue
            if np.bincount(g.predict(X), minlength=K).min() \
                    < self.min_frames_per_regime:
                continue
            b = g.bic(X)
            if b < best_bic:
                best, best_bic, self.K_eff = g, b, K
        if best is None:
            best = GaussianMixture(
                n_components=1, covariance_type='full',
                random_state=self.random_state, reg_covar=1e-6,
            ).fit(X)
            self.K_eff = 1
        self.gmm_ = best
        return self

    def _maha2(self, X: np.ndarray) -> np.ndarray:
        """(n, K) squared Mahalanobis distance to each component."""
        X = np.asarray(X, dtype=np.float64)
        out = np.zeros((len(X), self.gmm_.n_components))
        for k in range(self.gmm_.n_components):
            L = self.gmm_.precisions_cholesky_[k]      # (d, d), full cov
            y = (X - self.gmm_.means_[k]) @ L
            out[:, k] = (y ** 2).sum(axis=1)
        return out

    def bip(self, X: np.ndarray) -> np.ndarray:
        """Posterior-weighted within-component fault probability ∈ [0,1].
        Higher = more likely fault."""
        post = self.gmm_.predict_proba(X)
        pf = chi2.cdf(self._maha2(X), df=self.d_)
        return (post * pf).sum(axis=1)

    def min_maha(self, X: np.ndarray) -> np.ndarray:
        """Nearest-component squared Mahalanobis (higher = further)."""
        return self._maha2(X).min(axis=1)

    def nll(self, X: np.ndarray) -> np.ndarray:
        """Our contrast: un-normalized mixture density (support floor)."""
        return -self.gmm_.score_samples(X)
