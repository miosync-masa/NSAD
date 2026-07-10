"""Step 4 — deployability: the diag-GMM light path, parity first, then cost.

H2's falsification (support geometry is capturable with diag+K) implies
the surviving pillar — support-boundary detection — has a matrix-free
O(K·d) inference path. The lost pillar (within-mode correlation for
contextual detection) was the only consumer of full covariance, and real
data contained no contextual events, so the light path gives up nothing
that survived.

Discipline: parity is MEASURED before any cost claim; costs are reported
as measured wall-clock (median of repeats) beside the analytic counts —
never O-notation alone. Honesty notes baked in:
  - Yu-Qin BIP inference is the same O(K·d²) family as our full-cov ll
    ("we're lighter" holds ONLY for the diag path);
  - our BIC×K training runs EM K_max times — likely HEAVIER than
    Figueiredo-Jain; training is offline, disclosed, not claimed.

Usage::
    python -m tests.multivariate.exp_deployability
"""

from __future__ import annotations

import time

import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.svm import OneClassSVM

from tests.baselines.mspc_baselines import MSPCModel
from tests.probes.test_regime_ghost_state import (
    GHOST_LEN, GHOST_START, N_CAL, _make_series,
)

LL_Q = 0.995     # frozen 0.5% floor


def _fit_auto(train, cov, K_max=5, min_frames=50, rs=0):
    best, best_bic, k_eff = None, float('inf'), 1
    for K in range(1, K_max + 1):
        g = GaussianMixture(n_components=K, covariance_type=cov,
                            random_state=rs, reg_covar=1e-6,
                            max_iter=200).fit(train)
        if np.bincount(g.predict(train), minlength=K).min() < min_frames:
            continue
        b = g.bic(train)
        if b < best_bic:
            best, best_bic, k_eff = g, b, K
    if best is None:
        best = GaussianMixture(n_components=1, covariance_type=cov,
                               random_state=rs, reg_covar=1e-6).fit(train)
        k_eff = 1
    return best, k_eff


def parity_ghost():
    rng = np.random.default_rng(11)
    X, core = _make_series(rng)
    cal = X[:N_CAL]
    Xz = (X - cal.mean(0)) / (cal.std(0) + 1e-12)
    print("\n[parity 1] ghost state (2ch):")
    for cov in ('full', 'diag'):
        g, k = _fit_auto(Xz[:N_CAL], cov)
        floor = float(np.quantile(-g.score_samples(Xz[:N_CAL]), LL_Q))
        s = -g.score_samples(Xz)
        det = (s[core] > floor).mean()
        normal = np.ones(len(Xz), bool)
        normal[:N_CAL] = False
        normal[GHOST_START - 100:GHOST_START + GHOST_LEN + 100] = False
        print(f"  {cov:<5} K_eff={k}  ghost det={det:6.1%}  "
              f"FP={(s[normal] > floor).mean():.2%}")


def parity_skab():
    from tests.nab.benchmark_nab_selfcal import aggregate, evaluate_flags
    from tests.multivariate.benchmark_skab import _clean_setup
    from tests.multivariate.skab_datasets import iter_all
    from lambda3_detector.regime import expand_anomaly_mask
    print("\n[parity 2] SKAB (8ch, 34 windows), unknown/nll channel, "
          "cleanq q=0.999:")
    for cov in ('full', 'diag'):
        rows = []
        for smp in iter_all():
            Xz, clean = _clean_setup(smp)
            g, _ = _fit_auto(clean, cov)
            s = -g.score_samples(Xz)
            expanded = expand_anomaly_mask(smp.anomaly.astype(bool), 50)
            tau = float(np.quantile(s[~expanded], 0.999))
            rows.append(evaluate_flags(smp, s > tau, int(0.15 * smp.n)))
        a = aggregate(rows)
        print(f"  {cov:<5} catch={a['catch']:5.1f}% ({a['windows']})  "
              f"fp/10k={a['fp_per_10k']:.0f}")


def parity_tep():
    from tests.multivariate.tep_datasets import FAULT_START, iter_faults, load_test, \
        load_train_normal
    print("\n[parity 3] TEP (52ch → PCA r, K by BIC), det%/FAR% at "
          "held-out q=0.999:")
    train = load_train_normal()
    z = lambda X: (X - train.mean(0)) / (train.std(0) + 1e-12)
    m = MSPCModel().fit(z(train)[:350])
    Ztr, _ = m._scores_resid(z(train))
    for cov in ('full', 'diag'):
        g, k = _fit_auto(Ztr[:350], cov)
        s_hold = -g.score_samples(Ztr[350:])
        tau = float(np.quantile(s_hold, 0.999))
        far_parts, dets = [], []
        for f in range(0, 22):
            Zt, _ = m._scores_resid(z(load_test(f).values))
            s = -g.score_samples(Zt)
            if f == 0:
                far_parts.append(s > tau)
            else:
                far_parts.append(s[:FAULT_START] > tau)
                dets.append((s[FAULT_START:] > tau).mean())
        print(f"  {cov:<5} K_eff={k}  det={100*np.mean(dets):5.1f}%  "
              f"FAR={100*np.concatenate(far_parts).mean():.2f}%")


def cost_table():
    print("\n[cost] inference per frame — analytic counts + measured "
          "wall-clock (median of 30 reps, 5000-frame batches)")
    print("  wall-clock is DESKTOP-MEASURED (x86, vectorized NumPy/BLAS);"
          " FLOPs and parameter memory are platform-independent.")
    print("  'MCU-class footprint' is an arithmetic estimate from those"
          " counts; on-device measurement is future work.")
    print(f"  {'model':<22} {'FLOPs/frame':>12} {'params (f32)':>13} "
          f"{'matrix ops':>10} {'ns/frame':>9}")
    rng = np.random.default_rng(0)

    def clock(fn, X, reps=30):
        ts = []
        for _ in range(reps):
            t0 = time.perf_counter()
            fn(X)
            ts.append(time.perf_counter() - t0)
        return 1e9 * np.median(ts) / len(X)

    for d, K, r in [(8, 3, 5), (52, 3, 20)]:
        train = rng.normal(size=(2000, d))
        train[:, 0] = train[:, 1] * 0.9 + 0.1 * train[:, 0]  # some corr
        X = rng.normal(size=(5000, d))

        gf = GaussianMixture(K, covariance_type='full', random_state=0,
                             reg_covar=1e-6).fit(train)
        gd = GaussianMixture(K, covariance_type='diag', random_state=0,
                             reg_covar=1e-6).fit(train)
        sp = MSPCModel(max_components=r).fit(train)
        oc = OneClassSVM(kernel='rbf', nu=0.05, gamma='scale').fit(train)
        n_sv = len(oc.support_vectors_)

        rows = [
            (f'full-GMM  d={d} K={K}', K * (d * d + 3 * d),
             K * (d * d + d) + K, 'yes',
             clock(gf.score_samples, X)),
            (f'diag-GMM  d={d} K={K}', K * 3 * d,
             K * 2 * d + K, 'no',
             clock(gd.score_samples, X)),
            (f'PCA-SPE   d={d} r={sp.k}', 2 * d * sp.k + 2 * d,
             d * sp.k + d, 'no',
             clock(sp.spe, X)),
            (f'OC-SVM    d={d} nSV={n_sv}', n_sv * (2 * d + 5),
             n_sv * d + n_sv, 'kernel',
             clock(oc.decision_function, X)),
        ]
        for name, flops, params, mat, ns in rows:
            print(f"  {name:<22} {flops:>12,} {4*params:>12,}B "
                  f"{mat:>10} {ns:>9,.0f}")
        print()
    print("  rolling stats (jump/drift scorers): O(1)/frame, "
          "few dozen bytes state — reference floor.")
    print("  NOTE: BIP inference = same O(K·d²) family as full-GMM ll "
          "(all K Gaussians evaluated; Bayes only normalizes).")
    print("  NOTE: BIC×K training runs EM K_max times — likely heavier "
          "than Figueiredo-Jain; offline, not claimed as an advantage.")


def main():
    parity_ghost()
    parity_skab()
    parity_tep()
    cost_table()


if __name__ == "__main__":
    main()
