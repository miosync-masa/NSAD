# Lambda³ Architecture

System architecture and algorithmic details for the Lambda³ anomaly detection framework.

## 0. Notation

| Symbol | Meaning |
|---|---|
| `events` | input time series, shape `(n,)` or `(n, d)` |
| `n` | total number of time frames |
| `d` | feature dimension (default `d=5` via `expand_to_5d`) |
| `t` | current time index (0-based) |
| `events[:t+1]` | causal lookback only, `events[t+1:]` access is **strictly forbidden** in streaming mode |
| `anomaly_mask` | (Tier 2 only) `(n,) bool`, True at known anomaly frames |
| `cal_end` | end of calibration phase (Tier 0: 15% of n; Tier 2: not applicable) |
| `Λ` | Lambda³ structure tensor (background theory) |

---

## 1. System overview

Lambda³ provides **two complementary operational modes** sharing the **same six streaming scorers** as building blocks:

```
                                  ┌─────────────────────────────────────────┐
                                  │   6 Streaming Scorers (the core)        │
                                  │   ─────────────────────────────────     │
                                  │   • StreamingJumpScorer                 │
                                  │   • StreamingGradualScorer              │
                                  │   • StreamingStructuralDriftScorer      │
                                  │   • StreamingReconstructionScorer       │
                                  │   • StreamingKernelScorer               │
                                  │   • StreamingStructuralScorer           │
                                  │                                         │
                                  │   Each: calibrate() → score(events, t)  │
                                  │         + per-scorer threshold          │
                                  └─────────────────┬───────────────────────┘
                                                    │
                          ┌─────────────────────────┴─────────────────────────┐
                          │                                                   │
                          ▼                                                   ▼
            ┌──────────────────────────┐                      ┌────────────────────────────┐
            │  Tier 0: Streaming       │                      │  Tier 2: Regime-aware  ★   │
            │  Lambda3StreamingDetector│                      │  RegimeAwareDetector       │
            │                          │                      │                            │
            │  • Zero-shot             │                      │  • Semi-supervised         │
            │  • First 15% calibration │                      │  • GMM regime clustering   │
            │  • OR voting             │                      │  • Per-regime threshold    │
            │                          │                      │  • OR-output calibration   │
            │                          │                      │  • 3-state output          │
            │                          │                      │    (normal/deviation/      │
            │                          │                      │     unknown regime)        │
            └──────────────────────────┘                      └────────────────────────────┘
```

**Tier 0** (`lambda3_detector.streaming`) is fully online: it calibrates on the first 15% of each series and streams thereafter with **strict no-future-leakage**.

**Tier 2** (`lambda3_detector.regime`) is semi-supervised in the sense that **anomaly window labels are used only to exclude contaminated frames from training** — anomaly frames are never observed by the scorers or by the GMM. The system learns the structure of *normal* behavior.

Both modes use the same per-frame **OR-voting** integration of the six scorers.

---

## 2. The six streaming scorers

All scorers inherit from `StreamingScorer` (`lambda3_detector/streaming/base.py`):

```python
class StreamingScorer(ABC):
    def calibrate(self, events_cal: np.ndarray) -> None: ...
    def score(self, events: np.ndarray, t: int) -> float: ...
    @property
    def threshold(self) -> float: ...
    @property
    def name(self) -> str:
        return self.__class__.__name__
```

Contract:
- `calibrate()` consumes a calibration segment and fixes the baseline + threshold (idempotent: same input → same internal state, controlled by NumPy seeds).
- `score(events, t)` is **causal**: accesses only `events[:t+1]`. Returns a single non-negative float.
- `threshold` is the binary-decision cut after calibration. Comparison `raw_score > threshold` produces a binary flag.

For Tier-level OR voting, the **ratio** `raw_score / threshold` (clipped to ≥ 0) is used as the per-scorer-per-frame contribution.

**Multivariate caveat (measured on SKAB)**: jump / gradual / drift
scorers collapse `(n, d)` input to the channel mean (`events.mean(axis=1)`)
by design, discarding cross-channel information; reconstruction, kernel
and structural scorers operate on the full joint space. With d>1 raw
channels the alarm channel is therefore only partially multivariate —
one reason the SKAB v3 alarm channel is noisy (2219 FP/10k) while the
fully-joint unknown channel is not (382). Making the fast/slow scorers
multivariate-aware is future work.

### 2.1 `StreamingJumpScorer`

**Detects**: sudden value jumps at multiple temporal scales.

- **State**: per-scale threshold dict `{w: threshold_w}` for windows `w ∈ {5, 20, 50, 200}`.
- **Raw value at scale w**:
  ```
  μ_w(t) = mean(sig[t-w : t])     # past w frames, excluding current
  σ_w(t) = std (sig[t-w : t]) + ε
  z_w(t) = |sig[t] - μ_w(t)| / σ_w(t)
  ```
  where `sig` is `events.mean(axis=1)` if d≥2 else `events.ravel()`.

- **Calibration**: per-scale `threshold_w = percentile_99(positive z_w over calibration)`.
- **Score**: internally multi-scale normalized:
  ```
  score_jump(t) = max_w  z_w(t) / threshold_w
  ```
  Returned `self.threshold = 1.0` (external comparison `score > 1.0` ↔ any scale exceeded its own 99th percentile).

### 2.2 `StreamingGradualScorer`

**Detects**: sustained directional drift (slow ramps) at multiple temporal scales.

- **Causal Gaussian-weighted trend** at scale `w` (sigma = `w/3`):
  ```
  weights_w[i] = exp(-i² / 2σ²) for i = 0..w-1   # newest frame i=0
  trend_w(t)  = Σᵢ weights_w[i] × sig[t-i]      # normalized weights, post-trim
  ```

- **Sustained gradient at scale w**:
  ```
  grad_w(t)      = |trend_w(t) - trend_w(t-1)|
  sustained_w(t) = mean over τ in [t - w/4, t] of grad_w(τ)
  ```

- **Score**: `score_gradual(t) = max_w sustained_w(t)`. Scales = `{50, 200, 500}`.
- **Threshold**: single global `percentile_99` over calibration.

### 2.3 `StreamingStructuralDriftScorer`

**Detects**: slow shifts in the local mean away from the calibration baseline.

- **Cumulative state**: rolling sum (O(1) per frame).
- **Raw value**:
  ```
  local(t) = mean(sig[t - W + 1 : t + 1])   # W = local_window = 200
  raw(t)   = |local(t) - ref_mean|          # ref_mean = mean of calibration sig
  ```
  After detector-level z-normalization, `ref_mean ≈ 0`, so `raw ≈ |local|`.
- **Threshold**: `percentile_99` over calibration self-scores.

### 2.4 `StreamingReconstructionScorer`  (Lambda³ Λ paths streaming proxy)

**Detects**: deviation from the low-rank temporal structure of normal data. This is the streaming equivalent of Lambda³'s structure tensor reconstruction error.

- **Delay embedding** of width `W = 20`:
  ```
  z_t = [events[t], events[t-1], ..., events[t-W+1]] ∈ R^{W·d}
  ```
- **Calibration**:
  1. Build `Z_cal ∈ R^{(n_cal-W+1) × (W·d)}` from delay vectors.
  2. Compute mean `μ ∈ R^{W·d}`, center `Z_cal - μ`.
  3. SVD `Z_cal - μ = U Σ Vᵀ`. Keep `V_k ∈ R^{k × (W·d)}` with `k = min(5, W·d-1)`.
  4. Per-frame residual `r_t = || (z_t - μ) - V_kᵀ V_k (z_t - μ) ||`.
  5. `threshold = percentile_99(positive r_t over calibration)`.

- **Score**: `raw(t) = || (z_t - μ) - V_kᵀ V_k (z_t - μ) ||`. Returns 0 if `t < W-1`.

**Connection to Lambda³**: `V_k` is the streaming proxy for `paths_matrix` rows — the low-rank temporal subspace that "normal" data occupies. Anomalies leave this subspace.

### 2.5 `StreamingKernelScorer`  (Kernel Mean Embedding Distance)

**Detects**: deviation from the RKHS centroid of the calibration set.

- **Kernel**: polynomial `K(x, y) = (xᵀy + c)^degree` with `c = 1.0`, `degree = 3`. (RBF also supported.)
- **Z-normalization at scorer level** (to avoid float overflow for NAB's wide value ranges):
  ```
  μ_feat = events_cal.mean(axis=0)
  σ_feat = events_cal.std (axis=0) + ε
  x̃     = (x - μ_feat) / σ_feat
  ```
- **Calibration**:
  1. Compute `K_cal ∈ R^{n_cal × n_cal}` over normalized calibration.
  2. Store `mean_term = mean(K_cal)` (scalar) and the normalized calibration matrix.
  3. Per-frame distance to RKHS centroid `μ_φ`:
     ```
     d²(x̃_t) = K(x̃_t, x̃_t)
              - 2 × mean_i K(x̃_t, x̃_cal_i)
              + mean_term
     ```
  4. `threshold = percentile_99(positive √d² over calibration)`.

- **Score**: `raw(t) = √max(d²(x̃_t), 0)`. Cost per frame: `O(n_cal × d)`.

### 2.6 `StreamingStructuralScorer`  (delay-embedded trajectory speed)

**Detects**: abrupt changes in the trajectory speed within the delay-embedded subspace. Orthogonal axis to the reconstruction scorer: the latter measures *position*, this measures *velocity*.

- **Step distance** with `W = 20`:
  ```
  z_t       = [events[t], events[t-1], ..., events[t-W+1]]
  step(t)   = || z_t - z_{t-1} ||      (Euclidean)
  ```
- **Calibration**:
  ```
  μ_step = mean(step over calibration, positive only)
  σ_step = std (step over calibration, positive only) + ε
  z_t    = (step(t) - μ_step) / σ_step
  threshold = percentile_99(|z_t| over calibration)
  ```
- **Score**: `raw(t) = |step(t) - μ_step| / σ_step`.

### 2.7 (Disabled) `StreamingPeriodicScorer`

FFT-based period estimation + same-phase residual `|events[t] - events[t - P]|`. **Disabled by default** because:
- on realKnownCause it provides net −1.10 NAB points across 7 files (lost more than gained),
- the calibration phase rarely contains a full period for true seasonal signals (e.g., `ambient_temperature`),
- principled but requires adaptive online baseline (EWMA) which is out of scope for static calibration.

Retained in the codebase for future research.

---

## 3. Tier 0 — `Lambda3StreamingDetector` (zero-shot streaming)

**Module**: `lambda3_detector/streaming/detector.py`.

### 3.1 Workflow

```
Input: events (n, d), scorers = [s_1, ..., s_K]
Config: calibration_ratio = 0.15, normalize = True

Phase A — Pre-normalize (optional, default True):
  cal_end = max(min_calibration, int(n * calibration_ratio))    # default min_calibration = 50
  μ_pre   = events[:cal_end].mean(axis=0)
  σ_pre   = events[:cal_end].std (axis=0) + ε
  events_used = (events - μ_pre) / σ_pre

Phase B — Calibration:
  events_cal = events_used[:cal_end]
  for s in scorers:
      s.calibrate(events_cal)              # freeze baseline + threshold

Phase C — Streaming:
  combined = np.zeros(n)
  for t in range(n):
      if t < cal_end:
          combined[t] = 0                  # probationary period
          continue
      best_ratio = 0
      for s in scorers:
          raw   = s.score(events_used, t)  # uses events_used[:t+1] only
          thr   = s.threshold
          if thr > 0 and finite(thr):
              ratio = raw / (thr + ε)
              if ratio > best_ratio:
                  best_ratio = ratio
      combined[t] = best_ratio

binary = (combined >= 1.0).astype(int)
```

### 3.2 The OR-voting integration

For frame `t` (after `cal_end`):

```
combined(t) = max_k  raw_k(t) / threshold_k
flag(t)     = combined(t) >= 1.0
```

This is **Binary OR voting** with a single continuous score per frame:
- If **any** scorer's raw value exceeds its own calibration threshold → flag.
- The maximum ratio doubles as a continuous score consumable by NAB's `Sweeper` for threshold optimization.

No weight tuning. No soft-max. No learned combination.

### 3.3 No-future-leakage guarantee

- `calibration_ratio = 0.15` matches the NAB **probationary period** convention (no detection during the first 15% of each file).
- `s.score(events_used, t)` accesses only `events_used[:t+1]` by contract.
- `μ_pre`, `σ_pre` are computed from `events[:cal_end]` only — never seeing future frames.

### 3.4 Results

Tier 0 within-file separability (per-file sweep, diagnostic): weighted mean **58.55** over 52 files. At the native operating point (ratio ≥ 1.0, label-free): 99.1% window catch at 2119 FP per 10k frames — no regime structure to control the OR-voting family-wise flag rate. See `doc/paper/scoreboard.md §2–3`.

---

## 4. Tier 2 — `RegimeAwareDetector` (semi-supervised regime-aware)

**Module**: `lambda3_detector/regime/regime_detector.py`.

This is the **headline configuration**. The data flow is one-shot (fit + predict in a single pass), not strictly streaming, but inference at each frame still uses only causal scorer ratios over a pre-computed regime label. Its output is **three-state**: normal-in-regime / deviation-in-regime / unknown regime — the second channel comes from calibrated OR voting, the third from the support boundary of the fitted normal structure.

### 4.1 Workflow

```
Input: events (n, d), anomaly_mask (n,) bool
Config (FIX defaults):
  K = 'auto'                              (BIC over K ∈ [1, 5])
  K_max = 5
  mask_margin = 50
  min_frames_per_regime = 50
  threshold_method = 'trimmed_percentile' (top 1% removed before p99)
  trim_fraction = 0.01
  percentile = 99.0
  normalize = True

Step 1 — Anomaly mask expansion (fixed):
  expanded_mask = expand_anomaly_mask(anomaly_mask, mask_margin)
    # dilate True positions by ±mask_margin

Step 2 — Z-normalize using clean statistics:
  μ_clean = events[~expanded_mask].mean(axis=0)
  σ_clean = events[~expanded_mask].std (axis=0) + ε
  events_used = (events - μ_clean) / σ_clean
  clean = events_used[~expanded_mask]    # GMM training set

Step 3 — BIC-based K selection (lambda3_detector/regime/regime_detector.py: _fit_gmm_adaptive):
  K_phys_max = max(1, len(clean) // min_frames_per_regime)
  K_upper    = min(K_max, K_phys_max)
  for K in [1, 2, ..., K_upper]:
      gmm_K = GaussianMixture(K, covariance_type='full',
                              random_state=0, reg_covar=1e-6).fit(clean)
      labels = gmm_K.predict(clean)
      if min(bincount(labels)) >= min_frames_per_regime:
          bic[K] = gmm_K.bic(clean)
  K_eff = argmin(bic)                    # subject to min cluster size constraint
  gmm   = the corresponding fit
  # Fallback: K=1 if no K satisfies the constraint

Step 4 — Common scorer calibration:
  scorers = build_scorer_factories([SCORER_NAMES], percentile)
              # default: all 6 scorers (jump, gradual, drift, recon, kernel, struct)
  for s in scorers:
      s.calibrate(clean)                  # uses ALL clean frames (regime-agnostic)
  # Note: baseline computation uses pooled clean data; regime-awareness lives in
  # the per-regime thresholds in Step 6.

Step 5 — Pre-compute per-scorer score arrays over clean:
  for s in scorers:
      raw_clean_s = [s.score(clean, t) for t in range(len(clean))]

Step 6 — Per-(regime, scorer) threshold:
  labels_clean = gmm.predict(clean)
  for k in range(K_eff):
      mask_k = (labels_clean == k)
      n_k    = mask_k.sum()
      if n_k < min_frames_per_regime:
          threshold[k][s.name] = +∞     # mark regime unusable
          continue
      for s in scorers:
          scores_k = raw_clean_s[s.name][mask_k]
          positive = scores_k[scores_k > ε]
          threshold[k][s.name] = compute_robust_threshold(
              positive, method='trimmed_percentile',
              percentile=99.0, trim_fraction=0.01)
              # = percentile(positive[positive <= percentile(positive, 99)], 99)

Step 6b — Combined-ratio calibration (opt-in, calibrate_combined=True):
  # Six per-scorer p99 thresholds OR-voted stack the family-wise clean
  # flag rate to ~6% (multiple comparisons). Calibrate the OR statistic
  # against its own clean distribution:
  combined_clean(t) = max_s raw_clean_s(t) / threshold[label_clean(t)][s]
  for k in range(K_eff):
      τ[k] = compute_robust_threshold(combined_clean[labels_clean == k],
                                      method='trimmed_percentile', ...)
  # default (calibrate_combined=False): τ[k] = 1.0 (behavior unchanged)

Step 7 — Streaming inference (causal per frame):
  regimes = gmm.predict(events_used)     # batch predict, but each prediction is per-frame
  combined = np.zeros(n)
  for t in range(n):
      k = regimes[t]
      best_ratio = 0
      for s in scorers:
          raw = s.score(events_used, t)  # causal, uses events_used[:t+1] only
          thr = threshold[k][s.name]
          if thr > 0 and finite(thr):
              ratio = raw / (thr + ε)
              if ratio > best_ratio:
                  best_ratio = ratio
      combined[t] = best_ratio / τ[k]
  binary = (combined >= 1.0).astype(int)

Step 8 — Unknown-regime detection (three-state output):
  ll_clean  = gmm.score_samples(clean)
  ll_floor  = percentile(ll_clean, unknown_ll_percentile)   # default 0.5%
  ll        = gmm.score_samples(events_used)
  unknown   = ll < ll_floor          # outside the support of known normal structure
  state     = 2 where unknown, else binary   # 0 normal / 1 deviation / 2 unknown
  regime_confidence = gmm.predict_proba(events_used).max(axis=1)
  # 'score'/'binary' are NOT affected by unknown detection
```

### 4.2 Trimmed percentile threshold

For each `(regime k, scorer s)` pair, the threshold is the **trimmed 99th percentile**:

```
T_{k,s} = percentile(
              { x ∈ scores_{k,s}  |  x ≤ percentile(scores_{k,s}, 99) },
              99
          )
```

Implemented in `compute_robust_threshold(method='trimmed_percentile', percentile=99, trim_fraction=0.01)`:

```python
trim_cut = np.percentile(scores, 100 * (1 - trim_fraction))   # 99th percentile
trimmed  = scores[scores <= trim_cut]                          # bottom 99% remain
return float(np.percentile(trimmed, percentile))               # 99th percentile of those
```

The effective percentile is roughly the 98.01th of the full distribution. The trim removes **rare training contamination** (a few normal frames with extreme values, often in small regimes) without lowering the threshold across genuinely heavy-tailed distributions — see `doc/paper/scoreboard.md §5` for the comparison of methods.

### 4.3 BIC selection in detail

For each candidate K:
1. Fit `GaussianMixture(K, covariance_type='full', random_state=0)`.
2. Predict labels on `clean`.
3. Reject K if any cluster has < `min_frames_per_regime = 50` samples.
4. Otherwise record `bic[K] = gmm.bic(clean)`.

Choose `argmin bic[K]` among accepted K. Fallback to K=1 if no K passes.

`bic_per_K` is returned in the result dict for diagnostic inspection.

### 4.4 OR voting (regime-aware)

For frame `t`:

```
k_t         = gmm.predict(events_used[t:t+1])[0]
combined(t) = max_s  raw_s(t) / threshold[k_t][s.name]
flag(t)     = combined(t) >= 1.0
```

Identical OR-voting form as Tier 0, but threshold is now **regime-conditional**.

### 4.5a Combined-ratio calibration (multiple-comparison control)

Each of the six scorers holds its own trimmed-p99 threshold, so OR voting
flags a clean frame whenever **any** of six ~1% tails fires — a
family-wise clean flag rate of up to ~6%. `calibrate_combined=True`
measures the clean distribution of the OR statistic itself
(`combined_clean = max_s raw_s/thr_{k,s}`) and derives a per-regime τ_k
with the same robust threshold method. The final score is `combined/τ_k`,
restoring the clean flag rate to ≈(100−percentile)%. Per-scorer
thresholds keep serving as cross-scorer scale alignment. Measured effect
(corpus, native point): FP 1087 → 266 per 10k at −2.8 points of catch.
Unit tests: `tests/core/test_combined_calibration.py`.

### 4.5b Unknown-regime channel (three-state output)

Frames whose GMM log-likelihood falls below a floor fitted on clean data
(`unknown_ll_percentile=0.5`) are reported as `state=2` — "outside known
normal structure" — instead of being force-assigned to the nearest
regime. This is the support boundary of the fitted normal structure used
as a detector in its own right; on NAB it alone catches 85% of labeled
windows at 56 FP per 10k frames, with no threshold tuning
(`doc/paper/scoreboard.md §2.1`). The `state=1` alarm and `state=2` unknown
channels are complementary (96 and 91 of 107 windows; 103 in union).
Unit tests: `tests/core/test_unknown_regime.py`.

### 4.5 Semi-supervised, normal-label only

The anomaly window labels enter the system **exactly once**: in Step 1, to expand the exclusion mask. After that point:
- `events[expanded_mask]` is **never seen** by the GMM (regime structure is learned only from normal frames).
- `events[expanded_mask]` is **never seen** by scorers during calibration (Step 4).
- Anomaly score is computed on `events[expanded_mask]` at inference time (Step 7) but no anomaly-shape signal informs detection.

This matches the industrial workflow of "exclude post-mortem incident periods from baseline construction". The label use is **data hygiene, not supervision**: annotations act only as exclusion masks for constructing uncontaminated normal structure — never as positive anomaly examples, anomaly-shape templates, or threshold-selection targets. (NAB provides no separate clean normal-regime logs, so exclusion is the only way to obtain clean normality from its mixed series.)

### 4.6 Results

At fully self-calibrated operating points (no test labels, no human
threshold tuning): unknown channel 85.0% catch @ 56 FP/10k; combined
three-state channel 96.3% @ 303; calibrated alarm channel 89.7% @ 247.
Within-file separability (per-file sweep, diagnostic only — not
comparable to official NAB scores): weighted mean **72.02** vs Tier 0's
58.55 with the identical scorer set. See `doc/paper/scoreboard.md §1–3`.

### 4.7 Multivariate operation, unification identities, transferability

**Multivariate use.** Both tiers accept `(n, d)` input; for
condition-monitoring data the d raw channels ARE the feature space (no
`expand_to_5d`). Guardrails, each with a measured counterexample in this
repository: per-channel z-normalization first (scale domination
otherwise); PCA reduction of the density model for d ≳ 16 (a 52-D full
covariance from ~300 samples is not a sane density); **out-of-sample
floors** — percentile floors taken on frames the density model was fit
to drift silently (×32 measured at d=52: in-sample percentile bias).

**Unification identities (tested).** The skeleton contains classical
MSPC as special cases: the reconstruction scorer at `delay_window=1`
**is** PCA-SPE (Q statistic; `tests/probes/test_mspc_sanity.py`, corr>0.99),
and the unknown channel at K=1 **is** Hotelling T² (measured exactly on
single-mode TEP). Detection parity with the multimode-GMM lineage
(Yu & Qin 2008) is therefore expected by construction; the framework's
claims live above the statistics (three-state semantics, severity
gradation, transferable operating points).

**Operating-point transferability.** The percentile floor's meaning
("flag x% of clean") is dimension- and scale-invariant — it holds at
design rate from d=2 to d=52 (`tests/multivariate/exp_frozen_transfer.py`), where a
once-frozen RBF bandwidth collapses to 100% FAR. Design conditions
(each necessary, each with a measured counterexample): out-of-sample
threshold estimation, dimensionality control, and a score whose
validity survives the transfer. The diag-covariance light path delivers
the same support floor matrix-free (d=52: 468 FLOPs/frame, 1.26 KB,
desktop-measured 325 ns/frame; `tests/multivariate/exp_deployability.py`).

**Interpretation payload → actions.** The result dict is a consumable
payload: `tests/probes/test_downstream_policy.py` demonstrates a ~30-line
rule-based consumer emitting graded actions (transient check /
schedule maintenance / reduce & investigate / stop & escalate) from
the three-state channel, per-scorer attribution, and the
non-saturating unknown margin and its trajectory — including two
ghost-depth actions a probability-saturating index (FGMM-BIP)
provably collapses into one.

---

## 5. Anomaly mask handling

Two implementations in `lambda3_detector/regime/regime_detector.py`:

### 5.1 `expand_anomaly_mask(mask, margin)` — FIX default

```
for each True position idx in mask:
    out[max(0, idx - margin) : min(n, idx + margin + 1)] = True
```

Fixed `±margin` dilation (default 50 frames each side). Used by the FIX configuration.

### 5.2 `adaptive_anomaly_mask(events, mask, ...)` — opt-in experimental

Variance-based recovery detection with total-exclusion cap:

```
1. Compute baseline_std = std(events[~expand(mask, max_margin)])
2. For each anomaly window [s, e]:
   - Extend post-margin: walk t = e+1, e+2, ... until
       local_std(events[t-W/2 : t+W/2]) <= variance_ratio * baseline_std
     OR off >= max_margin (default 300). At least base_margin = 50.
   - Symmetric pre-margin walk.
3. Ensure base_margin lower bound (OR with expand_anomaly_mask).
4. If total exclusion > max_exclusion_ratio (default 0.4),
   shrink margin uniformly from base_margin down to 0 in steps of 5
   until under cap. Fallback: pure anomaly_mask.
```

**NAB experiment finding**: Adaptive mode produces identical NAB scores to fixed margin on all 6 categories. NAB anomaly windows are tight (variance returns within `base_margin = 50` frames), so extension does not trigger meaningfully, and the cap only activates for files with very dense windows (e.g., `realTraffic/speed_7578` with 4 windows) where it merely reverts to base_margin behavior.

Retained as opt-in (`margin_adaptive=True`) for domains with gradual recovery transients.

---

## 6. Threshold methods (per-regime)

Implemented in `compute_robust_threshold(scores, method=..., ...)`:

| Method | Formula | Separability¹ | Notes |
|---|---|---|---|
| `percentile` | `np.percentile(s, 99)` | 71.29 | baseline; sensitive to training-set extremes |
| **`trimmed_percentile`** | `percentile(s[s ≤ percentile(s, 99)], 99)` | **72.02** | **★ FIX** — removes rare contamination, preserves heavy tails |
| `iqr` | `Q3 + 3 × (Q3 - Q1)` | 66.88 | classical Tukey rule, too loose for NAB |
| `mad` | `median(s) + 2.5 × 1.4826 × MAD(s)` | 66.09 | most robust but too low; FP cascade |
| `capped` | `min(p99, 5 × p90)` | 70.69 | experimental adaptive; misfires on small regimes |

¹ per-file-sweep separability (diagnostic protocol; see `doc/paper/scoreboard.md §1`).

The FIX choice is **`trimmed_percentile`** with `trim_fraction = 0.01`. The same method is reused at the combined-ratio level when `calibrate_combined=True` (§4.5a). Empirical lessons in `doc/paper/scoreboard.md §7`.

---

## 7. Per-scorer ablation API

Module `lambda3_detector.regime` exports:

```python
SCORER_NAMES = ['jump', 'gradual', 'drift', 'recon', 'kernel', 'struct']
SCORER_FACTORIES: Dict[str, Callable[[float], Callable]]
build_scorer_factories(scorer_names: List[str], percentile: float) -> List[Callable]
```

CLI:

```bash
# leave-one-out (drop the kernel scorer)
python -m tests.legacy.benchmark_nab_regime --category realKnownCause --exclude-scorers kernel

# subset (use only jump and kernel)
python -m tests.legacy.benchmark_nab_regime --category realKnownCause --scorers jump,kernel

# automated leave-one-out + summary table
python -m tests.legacy.ablation_runner --category realKnownCause
python -m tests.legacy.ablation_runner --all-categories
```

The same `--scorers` / `--exclude-scorers` flags are available on `tests/legacy/benchmark_nab_streaming.py` for Tier 0 ablation, via a parallel `STREAMING_SCORER_FACTORIES` dict.

---

## 8. Module layout

```
lambda3_detector/
├── streaming/                                  # Tier 0 building blocks
│   ├── base.py                  StreamingScorer ABC
│   ├── jump_streaming.py        StreamingJumpScorer
│   ├── gradual_streaming.py     StreamingGradualScorer
│   ├── drift_streaming.py       StreamingStructuralDriftScorer
│   ├── reconstruction_streaming.py    StreamingReconstructionScorer
│   ├── kernel_streaming.py      StreamingKernelScorer
│   ├── structural_streaming.py  StreamingStructuralScorer
│   ├── periodic_streaming.py    StreamingPeriodicScorer (disabled)
│   └── detector.py              Lambda3StreamingDetector (Tier 0 OR voting)
│
├── regime/                                     # Tier 2
│   ├── regime_detector.py       RegimeAwareDetector
│   │                              + compute_robust_threshold
│   │                              + expand_anomaly_mask
│   │                              + adaptive_anomaly_mask
│   │                              + SCORER_NAMES, SCORER_FACTORIES
│   │                              + build_scorer_factories
│   └── __init__.py              public API exports
│
├── analysis/                                   # Lambda³ batch building blocks (offline)
│   ├── structure_tensor.py
│   ├── structure_tensor_sparse.py
│   ├── multiscale_jumps.py
│   ├── topology.py
│   └── ...
│
├── scorers/                                    # Batch scorers (offline)
├── core/                                       # JIT kernels, inverse problem solver
└── detector.py                  Lambda3ZeroShotDetector (batch offline mode)

tests/
├── benchmark_nab_streaming.py   Tier 0 CLI + STREAMING_SCORER_FACTORIES
├── benchmark_nab_regime.py      Tier 2 CLI  ★ recommended
├── benchmark_nab.py             Batch CLI
├── benchmark_nab_baselines.py   Self-run classical baselines (OC-SVM/iForest/LOF)
├── benchmark_nab_corpus.py      Corpus-level scoring: score caches, single-θ,
│                                anchored transform, native operating point
├── benchmark_nab_selfcal.py     Self-calibrated operating points (catch %, FP/10k)
├── ablation_runner.py           Per-scorer leave-one-out ablation
├── skab_datasets.py / benchmark_skab.py     SKAB (real pump rig, 8ch)
├── tep_datasets.py / benchmark_tep.py       TEP (Braatz standard, 52ch)
├── contextual_stratify.py       Univariate/contextual tagging + curves
├── mspc_baselines.py            PCA-SPE / Hotelling T2 + reduced unknown
├── fgmm_bayes.py                Yu-Qin FGMM-Bayes reconstruction (duel)
├── exp_support_duel.py          Ghost-state duel (raw-ll/BIP/minMaha/OCSVM)
├── exp_deployability.py         diag light path: parity + measured cost
├── exp_frozen_transfer.py       Frozen-config transfer test (pillar 2)
├── exp_mode_change_probe.py     H3 probe (mode-change false alarms)
├── test_unknown_regime.py       Unknown-regime channel unit tests
├── test_combined_calibration.py OR-output calibration unit tests
├── test_contextual_mechanism.py Contextual probe (GATE)
├── test_regime_ghost_state.py   Ghost state vs single-model T2/SPE
├── test_h2_covariance.py        H2 characterization (full vs diag)
├── test_mspc_sanity.py          recon(W=1) == SPE identity
├── test_downstream_policy.py    Worked downstream consumer (the demo)
├── nab_datasets.py              NABSample loader (CSV + combined_windows.json)
├── nab_features.py              expand_to_5d (5-D feature engineering)
└── nab_metrics.py               NAB Sweeper score + corpus-level scoring
                                 (sweep_threshold_curve / corpus_score / corpus_score_at)

doc/
├── README.md                    documentation index
├── architecture.md              this file
├── figures/                     generated manuscript figures
├── paper/                       manuscript line (v2 outline, abstract, claim–evidence
│                                map, v1 draft, benchmark scoreboard = Appendix)
├── preregistrations/            pre-registered plans #1–#4 + multivariate + synthesis
└── explorations/                post-freeze explorations (not in the paper)
```

---

## 9. Data flow (single-file Tier 2)

```
              NAB CSV               combined_windows.json
                 │                          │
                 ▼                          ▼
            nab_datasets.py ──────► NABSample
                 │                          │
                 ▼                          ▼
            expand_to_5d                anomaly_mask
            (events shape (n, 5))       (shape (n,) bool)
                 │                          │
                 └──────────┬───────────────┘
                            │
                            ▼
                ┌────────────────────────────────┐
                │  RegimeAwareDetector.fit_predict│
                │                                │
                │  Step 1: expand_anomaly_mask   │ ◄── mask_margin
                │  Step 2: z-normalize on clean  │
                │  Step 3: BIC K selection       │ ◄── K_max, min_frames_per_regime
                │  Step 4: scorer.calibrate(clean)│
                │  Step 5: precompute clean scores│
                │  Step 6: per-(regime, scorer)  │ ◄── threshold_method, trim_fraction
                │           threshold             │
                │  Step 6b: combined-ratio τ_k    │ ◄── calibrate_combined
                │  Step 7: per-frame OR voting    │
                │  Step 8: unknown-regime floor   │ ◄── unknown_ll_percentile
                └────────────────────────────────┘
                            │
                            ▼
                  result dict:
                  • score (n,)   continuous, >= 1.0 = flagged (τ-calibrated)
                  • binary (n,)  0/1
                  • state (n,)   0 normal / 1 deviation / 2 unknown regime
                  • unknown_mask (n,) bool — outside known normal structure
                  • log_likelihood (n,), ll_floor, regime_confidence (n,)
                  • per_scorer   dict[name -> (n,) raw]
                  • thresholds_per_regime, combined_tau
                  • regimes (n,) int
                  • K_eff
                  • bic_per_K
                  • cal_clean_frames
                            │
                            ▼
                  nab_metrics.score_all_profiles(sample, score)
                            │
                            ▼
                  3 NAB profiles (standard / reward_low_FP_rate / reward_low_FN_rate)
                  → 3-profile mean
```

---

## 10. Reproducibility

All randomness is controlled by `random_state=0` in `GaussianMixture`. Given the same `events` and `anomaly_mask`, all computations are deterministic up to BLAS-level floating-point reproducibility. Empirically, the weighted separability mean reproduces to `72.02 ± 0.01` across runs.

To reproduce end-to-end:

```bash
git clone https://github.com/miosync-masa/Lambda_inverse_problem.git
cd Lambda_inverse_problem && pip install .
git clone --depth 1 https://github.com/numenta/NAB.git NAB

# separability (per-file sweep, diagnostic)
for cat in realKnownCause realAWSCloudwatch realTraffic \
           realAdExchange artificialWithAnomaly realTweets; do
    python -m tests.legacy.benchmark_nab_regime --category $cat
done

# self-calibrated operating points + corpus-level scoring + baselines
python -m tests.nab.benchmark_nab_corpus --compute --methods all
python -m tests.nab.benchmark_nab_corpus --aggregate
python -m tests.nab.benchmark_nab_selfcal
python -m tests.nab.benchmark_nab_baselines --category all
```

Weights for the 52-file weighted mean: (7, 16, 7, 6, 6, 10).

---

## 11. Connection to Lambda³ theory (background)

The streaming/regime-aware modes inherit conceptual primitives from the original batch Lambda³ system:

| Lambda³ batch concept | Streaming proxy |
|---|---|
| **Structure tensor `Λ`** | `events_used` after z-normalization |
| **Path matrix `paths_matrix`** (low-rank decomposition) | `V_k` from SVD of delay-embedded `Z_cal` (StreamingReconstructionScorer) |
| **Multi-scale jumps `ΔΛC`** | per-scale z-score with windows `{5, 20, 50, 200}` (StreamingJumpScorer) |
| **Kernel space deviation** | RKHS centroid distance (StreamingKernelScorer) |
| **Path smoothness** | delay-embedded step distance (StreamingStructuralScorer) |
| **Tension scalar `ρT`** | sustained causal gradient at multiple scales (StreamingGradualScorer) |

Topological invariants (winding number `Q_Λ`, multi-entropy, jump consistency `J(Λ)`) are exclusive to the batch mode (`Lambda3ZeroShotDetector.analyze()`) and are not used in streaming/regime-aware modes. They provide deeper interpretability for post-hoc analysis but require full-series O(n_paths × n_events) optimization.

---

## 12. Key design properties

1. **No tuned weights.** The OR-voting maximum replaces all weighted-combination tuning.
2. **No anomaly-shape learning.** Anomaly labels in Tier 2 are used exclusively for training-data exclusion — never for thresholds (the legitimacy rule, `doc/paper/scoreboard.md §1`).
3. **Single frozen configuration.** One setting (`K='auto'`, `trimmed_percentile`, `mask_margin=50`, `unknown_ll_percentile=0.5`) applies to all 6 NAB categories; no per-dataset tuning, no test-label-derived thresholds.
4. **Strict causal contract** in `StreamingScorer.score(events, t)`. Tier 0 enforces no-future-leakage at the framework level; Tier 2 inherits the same property at scoring (only the GMM regime label uses information from the full series, but never anomaly frames).
5. **Family-wise flag-rate control.** `calibrate_combined` calibrates the OR statistic against its own clean distribution, fixing the multiple-comparison inflation of six OR-voted p99 tails (§4.5a).
6. **Three-state output.** Deviation-in-regime and unknown-regime are separate, complementary channels; the unknown channel is the support boundary of the fitted normal structure acting as a detector (§4.5b).
7. **Modular ablation.** Each scorer can be enabled/disabled via the `--scorers` / `--exclude-scorers` CLI flags or programmatically via `build_scorer_factories(scorer_names=...)`.
8. **Honest failure modes.** Mode B files (extreme scale, seasonal drift, sparse-window long series) surface on the unknown channel rather than as silent zeros or misleading mid-confidence scores; see `doc/paper/scoreboard.md §6`.
9. **MSPC unification.** Classical statistics are contained as special cases — recon@W=1 ≡ PCA-SPE, unknown@K=1 ≡ Hotelling T² (both tested); detection parity with the multimode-GMM lineage is by construction, and claims live above the statistics (§4.7).
10. **Transferable operating points.** The percentile floor's meaning is dimension/scale-invariant and holds at design rate d=2→52 under three design conditions (out-of-sample floors, dimensionality control, score validity), each with a measured counterexample; the diag light path runs matrix-free at edge-class cost (§4.7).
11. **Consumable payload.** The three-state output + attribution + non-saturating margin drive a demonstrated downstream policy with graded actions that saturating indices provably cannot emit (`tests/probes/test_downstream_policy.py`).

---

## 13. Adapter view: before → during → after

The current architecture can be generalized as a three-layer observation system:

```text
Input adapters (before)        Common NSAD core (during)       Consumers (after)
────────────────────────       ─────────────────────────       ─────────────────────────
Univariate expansion           Normal-structure construction   Protective policy
Cyclic phase structure         Regime decomposition            Margin-trajectory reading
Vibration / acoustics          Self-calibrated thresholds      Episode aggregation
Multivariate joint geometry    Support floor                   Forensic reconstruction
Abrupt-event structure         Three-state payload             Fault-mode attribution
Actuator command-response      Non-saturating margin           Maintenance escalation
```

The distinction is architectural rather than organizational.

* A **before-layer adapter** exposes structural degrees of freedom that are physically present in the sensor stream but would otherwise be destroyed by an inappropriate representation.
* The **during-layer core** constructs and evaluates normal structure without knowing the identity or shape of any fault.
* An **after-layer consumer** interprets episodes already exposed by the core; it may aggregate margins, select protective actions, or run a more expensive forensic analysis.

The common contract is:

```text
raw sensor stream
    → fault-agnostic structural vocabulary
    → normal-structure interpretation
    → state / attribution / confidence / severity
    → action or post-hoc diagnosis
```

### 13.1 Before layer: structural input adapters

An input adapter does not detect a named fault. It transforms a sensor stream so that physically meaningful variation remains observable to the common core.

The current two input conventions are the smallest existing adapter registry:

```text
univariate stream
    → causal five-axis temporal expansion
multichannel stream
    → normalized joint sensor space
```

They should therefore be understood as two concrete adapters, not as the final set of accepted input forms.

Candidate adapter families are:

| Sensor or mechanism class     | Structural vocabulary exposed before the core                                                |
| ----------------------------- | -------------------------------------------------------------------------------------------- |
| Univariate temporal stream    | value, local mean, local scale, curvature, autocorrelation                                   |
| Multivariate process          | joint geometry, reconstruction residual, trajectory speed, kernel interaction                |
| Cyclic machinery              | normalized phase profile, phase-local slopes, peak/trough position, rise time, settling time |
| Vibration or acoustics        | spectral magnitude, spectral entropy, band energy, envelope structure, resonance structure   |
| Abrupt events                 | multiscale jumps, local synchronization, event-local deviation                               |
| Degradation-sensitive streams | slow drift, cumulative displacement, pulsation or path-energy structure                      |
| Actuator systems              | command-response lag, tracking residual, current-torque relation, load-conditioned response  |

Adapter selection must be justified by the measurement process, not by anomaly labels or benchmark performance.

Examples:

```text
Valid:
A valve fault is expressed as switching delay inside a repeated cycle;
therefore a phase-preserving cyclic adapter is required.

Invalid:
The phase adapter obtained the highest AUC on this dataset;
therefore it is selected for this dataset.
```

The first statement exposes a known physical degree of freedom. The second performs dataset-specific model selection and violates the frozen normal-structure formulation.

### 13.2 Adapter qualification law

A module qualifies as a normal-structure input adapter only if it extends the four requirements of the core architecture.

#### 1. Causality

The adapter may use only information available at its declared output time.

For frame-level output, it must depend on `x_≤t` only. For cycle-level output, a completed cycle may be emitted after its endpoint, but no future cycle may be used. Any non-causal module must be classified explicitly as an after-layer forensic consumer rather than as a streaming adapter.

#### 2. Self-calibration

Normalization constants, structural baselines, phase references, frequency bands, and operating points must be derived from clean construction data or fixed physical definitions.

They must not be selected from test-fault performance.

#### 3. No anomaly-shape learning

An adapter may describe the structure of an observation, but it may not describe the identity of a fault.

> **The vocabulary may speak about structure; it may not speak about faults.**

Permitted vocabulary includes:

```text
late response
abrupt transition
slow displacement
spectral concentration
loss of coupling
phase-local shape change
tracking residual
```

Impermissible vocabulary includes features or alignment rules constructed specifically to recognize:

```text
valve fault class 2
cooler degradation stage
bearing outer-race fault
known leak waveform
```

Anomaly annotations may not determine adapter parameters, feature selection, phase alignment, or thresholds.

#### 4. Severity preservation

The adapter should not irreversibly squash or average away the physical degree of freedom that may later carry severity.

This does not require every adapter feature to be unbounded. It requires the representation as a whole to preserve an unsaturated path from physical departure to the common core's non-saturating margin.

The cyclic mechanism test demonstrates why this requirement is load-bearing:

```text
pure circular lag
    → |FFT|-derived frequency features remain invariant
    → rise time and peak position move monotonically with lag
```

A magnitude-only representation is therefore mathematically incapable of observing a pure timing fault. Conversely, timing-only features discard steady magnitude information required by cooler degradation. The qualified cyclic adapter retains both vocabularies:

```text
magnitude profile + timing vocabulary
```

### 13.3 During layer: the invariant NSAD core

Adapters do not replace the common core. Every qualified adapter must return a causal feature stream that enters the same normal-structure machinery:

```text
feature stream
    → normalization from construction data
    → regime model
    → per-regime scorer calibration
    → calibrated fusion
    → support floor
    → three-state payload
```

The core remains responsible for:

* construction of normal structure;
* BIC-resolved regimes;
* per-regime robust thresholds;
* multiple-comparison calibration;
* the first-class out-of-support state;
* assignment confidence;
* per-scorer attribution;
* non-saturating support margin.

The hydraulic cycle experiment is evidence for this separation: the detector and support-floor path remained frozen. Only the observation map changed so that the fault's physical degree of freedom became visible.

The architectural interpretation is therefore:

> The detector did not require retuning; the missing object was an observation map that preserved the fault's physical degree of freedom.

### 13.4 After layer: consumers and forensic analysis

Two previously grouped items belong after the common core rather than before it.

#### Margin-trajectory consumers

The support margin is produced by the core. Its slope, persistence, acceleration, and episode-level depth are interpreted by downstream consumers.

Examples include:

```text
gradual support egress
    → maintenance scheduling
abrupt shallow egress
    → reduce output and investigate
deep support egress
    → stop and escalate
```

The worked downstream policy is the existing reference consumer. Drift and pulsation features may be before-layer vocabulary, but margin-trajectory interpretation itself is an after-layer operation.

#### Forensic reconstruction

Topology, entropy, and inverse-problem reconstruction are not streaming input adapters.

They are high-cost diagnostic consumers invoked after an episode has been localized:

```text
state-2 episode detected
    → select episode and surrounding context
    → reconstruct latent event relations
    → inspect topological, entropic, or path-level changes
    → produce post-hoc fault-mode attribution
```

The intended placement is therefore:

```text
online:
    adapter → NSAD core → protective action

post-event:
    stored episode → topology / entropy / inverse problem → forensic diagnosis
```

The inverse-problem path may be non-causal and computationally expensive without weakening the streaming claim, because it is not part of the streaming decision path.

### 13.5 Adapter registry and evidence status

| Registry entry            | Existing implementation                                                              | Evidence status                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| Univariate temporal       | five-axis expansion                                                                  | Validated in the current manuscript                                                              |
| Multivariate process      | `streaming/`, `regime/`, reconstruction and joint-space scorers                      | Validated in the current manuscript                                                              |
| Cyclic machinery          | `extract_cycle_phase_features`, magnitude profile, timing vocabulary, mechanism test | Validated in post-freeze hydraulic exploration, then under pre-registration #5 (`doc/preregistrations/experiment_plan_hydraulic.md`: cooler + valve severity ordering supported on 5 registered splits; leak killed; accumulator limit confirmed) |
| Vibration / acoustics     | FFT magnitude, energy, centroid, spectral entropy; generic envelope band energies (`tests/paderborn/paderborn_datasets.py`) | Detection validated in post-freeze Paderborn subset exploration (100% detection under 100%-pure condition-regimes; FAR coverage caveat — `doc/explorations/paderborn_exploration.md`); resonance extraction unimplemented |
| Abrupt events             | `analysis/multiscale_jumps.py` and jump kernels                                      | Existing inventory; adapter-to-core integration not yet externally validated                     |
| Degradation structure     | drift detection, CUSUM-related logic, `pulsation_jit.py`                             | Existing inventory; distinct from downstream margin-trajectory reading                           |
| Actuator command-response | none yet                                                                             | Requires command, measured response, current/torque, and preferably load-state signals           |
| Forensic analysis         | topology, multi-entropy, inverse-problem reconstruction                              | Existing after-layer inventory; not part of the online path                                      |

Four registry entries currently have empirical support:

1. univariate temporal expansion;
2. direct multivariate process input;
3. cyclic magnitude-plus-timing structure;
4. vibration band/envelope structure (detection on the Paderborn
   subset; FAR coverage still open — single healthy bearing).

The remaining entries are inventory or requirements, not validated claims.

### 13.6 Hydraulic mechanism result

The cyclic adapter provides the first complete example of the adapter law.

A pure circular shift test establishes representation-level observability (`tests/core/test_cycle_phase.py`):

```text
legacy |FFT| features:
    peak frequency
    energy
    centroid
    spectral entropy
    → invariant to lag within numerical precision

phase-preserving features:
    peak position
    rise time
    → monotone with lag
```

The frozen detector was then evaluated on the physical hydraulic rig. Detection per degradation stage (mild → severe), with the adapter variant that produced each result named explicitly:

| Target      | Cycle summary (means, d=17) | Best qualified cyclic variant | Interpretation |
| ----------- | ----------------------: | ---------------------------------------------: | --------------------------------------------------------------- |
| Valve       | ~1% (invisible) | **timing vocabulary (d=68)**: 2.2% → 81.7% → 100%; margin −2.6 → +1.1 → +9.8 | timing fault recovered and graded by severity |
| Leak        | 54–57% | **profile + timing (d=272)**: 82% → 91%; margin +2.8 → +7.6 | phase-local shape added useful observability |
| Cooler      | 100% / 100% | **profile + timing (d=272)**: 100% / 100%; FAR 0.51%; margin +388 → +1490 | steady magnitude information preserved and design FAR recovered |
| Accumulator | ~20% | ~20% at every granularity tried | remaining sensor-set observability limit |

Disclosed dimensionality effect: in the combined d=272 representation the phase profile dilutes the timing signal for the mild and middle valve stages (1.9% / 11.9% / 100% vs the timing-only 2.2% / 81.7% / 100%) — the two vocabularies are complementary but their unweighted concatenation is not yet the final adapter form.

The ablation establishes complementarity:

```text
timing vocabulary alone
    → recovers valve timing
    → loses cooler steady-state information

magnitude profile alone
    → retains cooler information
    → loses valve lag

magnitude profile + timing vocabulary
    → preserves both physical degrees of freedom
```

This is not evidence that one adapter detects every component. It is evidence that a fault-independent structural adapter can expose complementary physical coordinates while leaving genuine sensor observability limits visible.

### 13.7 Relationship to the current manuscript

The current manuscript deliberately freezes a compact reference architecture. Its two input conventions are a two-entry reduction of the broader adapter registry described here.

The manuscript should not be retroactively expanded to claim the full registry. The clean connection for subsequent work is:

> The two input conventions evaluated here are instances of a broader adapter interface: fault-independent, modality-aware structural transforms may expose additional physical degrees of freedom while preserving the same normal-structure core and payload semantics.

The cyclic hydraulic experiment began as post-freeze exploration, outside the manuscript's evidence base. The path this section anticipated ("a subsequent paper in which adapter hypotheses, qualification tests, and external datasets are fixed in advance") was subsequently taken: pre-registration #5 (`doc/preregistrations/experiment_plan_hydraulic.md`) fixed the vocabulary, splits, statistics, and pass/kill conditions before its frozen run, and its results — including the leak kill the exploration's single split had masked — are now citable manuscript evidence, with the registered-confirmatory disclosure carried alongside.

### 13.8 Legacy inventory policy

Legacy Lambda³ modules are not automatically part of the production path, but neither are they historical debris.

They are classified as:

```text
validated adapter
candidate adapter inventory
common-core component
after-layer consumer
retired or falsified mechanism
```

A legacy module is promoted only when:

1. a sensor mechanism identifies a missing observable degree of freedom;
2. the module or a minimal derivative exposes that degree of freedom;
3. a mechanism test demonstrates the relevant invariance or sensitivity;
4. the module satisfies the adapter qualification law;
5. the common core remains frozen during external evaluation.

Under this view, legacy preservation is justified: the repository is an inventory of mathematical mechanisms, while the adapter registry controls which mechanisms are allowed into a deployed observation path.

### 13.9 Promotion log (§13.8 criteria applied)

Promotions from the experiment path into the production package. Each
entry met the five §13.8 criteria (observable degree of freedom /
exposing implementation / mechanism test / qualification law / core
frozen during external validation) before promotion; all are opt-in or
additive — **default behavior is byte-identical** (regression-tested).

| Promoted | Into | Validated by | Promotion tests |
|---|---|---|---|
| Cycle-phase vocabulary (`extract_cycle_phase_features`) | `features/extractor.py` | hydraulic valve recovery + circular-shift mechanism test | `tests/core/test_cycle_phase.py` |
| Out-of-sample floor + dimensionality guardrail (opt-in `floor_holdout_fraction` / `floor_reduce_dims`; unknown-channel density only — regime layer untouched) | `regime/regime_detector.py` | ×32 in-sample drift self-catch (frozen-transfer test); used by every subsequent validation (hydraulic, Paderborn #1–#3, IMS #4); paper §4.6 | `tests/core/test_floor_guardrails.py` |
| Vibration adapter vocabulary (`vibration_features`, fs-generic) | `adapters/vibration.py` | Paderborn #1–#3 + IMS #4 (four pre-registered runs) | `tests/core/test_vibration_adapter.py` (numerical identity with the frozen implementations) |
| Per-unit healthy commissioning (`commission_unit`, location+scale) **with its role boundary in the docstring** (healthy admission only — NEVER the failure alarm; #4 H3L: fleet margin 11–14% of life late or silent) | `regime/commissioning.py` | #3 SUPPORTED (FAR 0.10% at zero severity cost), bounded by #4 | `tests/core/test_commissioning.py` (incl. a test asserting the boundary is documented) |

Deferred (not yet earned): episode/occupancy consumer utilities
(after-layer, awaits its own validation arc); severity/alarm
dual-output API (a v2 design pass). Never promoted: evaluation-side
baselines, dataset loaders, pre-registration runners (evidence
artifacts).
