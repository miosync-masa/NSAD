# Results — Lambda³ Normal-Structure Anomaly Detection on the NAB corpus

NAB (Numenta Anomaly Benchmark) is used here as a **public corpus with
official anomaly labels** — not as a leaderboard. We make no ranking claims
against published detector scores. The question these experiments answer:

> Can deviation from mathematically structured normality detect the labeled
> anomalies, at operating points derived **without test labels and without
> human threshold tuning**?

**Corpus**: 52 files with anomaly windows across 6 categories (plus 5
windowless `artificialNoAnomaly` files cached for corpus-level scoring).
All runs use one frozen configuration; deterministic (`random_state=0`).

---

## 1. The legitimacy rule

Test anomaly labels are used ONLY for:

1. **Training exclusion** — removing labeled incident windows (+ margin)
   from normal-structure construction (the disclosed semi-supervised
   anomaly-exclusion setting), and
2. **Final scoring.**

Thresholds, calibrations, and transforms are derived from **normal
structure only**. In canonical form: *we use anomaly-window annotations
only as exclusion masks for constructing uncontaminated normal
structure — never as positive anomaly examples, anomaly-shape templates,
or threshold-selection targets.* This label use is **data hygiene, not
supervision**: ideally normal regimes would be built from separate clean
normal-operation logs, but NAB mixes normal and anomalous segments
within each series and provides no such logs, so incident windows are
excluded instead (the semi-supervised anomaly-exclusion setting).

Three evaluation protocols follow from this rule:

| Protocol | Threshold chosen by | Status |
|---|---|---|
| **Self-calibrated** (§2) | the detector itself, from clean data | ★ the headline — fully rule-compliant |
| Separability (§3) | per-file oracle sweep over test labels | diagnostic only — measures score separability, NOT deployable alarm quality |
| Corpus single threshold (§4) | one global θ optimized on the corpus | disclosed for transparency; we reject fixed-global-threshold ideology as a design target |

Per-file oracle sweeps inflate every method's score (+25 to +59 points
measured across our self-run baselines) and must never be compared with
official NAB leaderboard numbers, which are corpus-single-threshold. We
therefore cite no published detector scores anywhere in this document.

---

## 2. Self-calibrated operating points (★ headline)

Label-free; no per-dataset tuning (frozen structural defaults, adjustable). Metrics are industrial: **window catch rate**
(share of labeled windows containing ≥1 flag) and **FP frames per 10k
out-of-window frames**. Probationary first 15% excluded.
`python -m tests.nab.benchmark_nab_selfcal`.

### 2.1 The three-channel output (Tier 2, calibrated, K=auto)

| Channel | Meaning | Catch | FP/10k |
|---|---|---:|---:|
| alarm (`state=1`) | deviation inside a known normal regime | 89.7% (96/107) | 247 |
| **unknown-notify (`state=2`)** | **left the support of known normal structure** (GMM log-likelihood floor) | **85.0% (91/107)** | **56** |
| **combined (`state≠0`)** | either signal | **96.3% (103/107)** | 303 |

**The unknown-regime channel alone catches 85% of NAB's labeled anomaly
windows at a 0.56% false-positive rate** — with no per-dataset threshold
tuning (frozen structural default: 0.5th-percentile likelihood floor on
clean data; adjustable if desired).
This is the core thesis made empirical: if an anomaly is a departure from
normal structure, then the *support boundary of that structure* is itself
the detector. In-regime deviation scoring adds catch on top (→96.3%).

### 2.2 Calibration progression at the native operating point (ratio ≥ 1.0)

| Variant | Catch | FP/10k | Note |
|---|---:|---:|---|
| Tier 0 streaming, native | 99.1% (106/107) | 2119 | no regime structure |
| Tier 2, native (uncalibrated) | 97.2% (104/107) | 1087 | per-regime thresholds halve FP |
| Tier 2 + combined calibration | 94.4% (101/107) | 266 | OR multiple-comparison fix (§5) |
| Tier 2 + calibration + unknown gating (alarm ch.) | 89.7% (96/107) | 247 | abstains outside known structure |

Regime structuring and OR-output calibration together cut the native FP
rate **8.6×** (2119 → 247) at a cost of 9 windows out of 107 — and the
combined channel recovers to 103/107.

### 2.3 Clean-quantile operating points, incl. self-run baselines

"Sweep on normal": per-file threshold = q-quantile of the score on clean
frames (same exclusion-only label use as training). This gives classical
baselines the identical self-calibration opportunity:

| Method | q=0.999: catch / FP/10k | q=0.9999: catch / FP/10k |
|---|---|---|
| Lambda³-R (Tier 2, cal) | 59.8% / 15.5 | 39.3% / 4.0 |
| OC-SVM (exclusion) | **78.5% / 16.0** | 67.3% / 7.4 |
| iForest (streaming) | 63.6% / 9.9 | 37.4% / 1.6 |
| iForest (exclusion) | 67.3% / 11.9 | 50.5% / 2.3 |
| LOF (exclusion) | 64.5% / 12.1 | 43.9% / 3.5 |

Read honestly: at matched clean-quantile points, **OC-SVM with the same
anomaly-exclusion hygiene catches more windows than Lambda³-R**. One-class
methods are themselves normal-only learners, so this table supports the
broader thesis — *normality-based detection works as a family* — while
Lambda³'s specific contributions lie elsewhere: regime semantics, the
unknown-regime channel (no baseline has one; §2.1), cross-file score
comparability (§4), and interpretability. Note OC-SVM gains +18.7 points
of catch from the exclusion setting itself — more evidence that **the
performance source is normality hygiene, not detector choice**.

Baselines: `python -m tests.nab.benchmark_nab_baselines` /
`tests/nab/benchmark_nab_corpus.py` (OneClassSVM RBF ν=0.05, IsolationForest
100 trees, LOF k=20; single frozen configs; details in the scripts).

---

## 3. Separability (per-file sweep — diagnostic, not deployable)

The original harness numbers, retained as a **within-file separability
measure**: the per-file best-threshold NAB score answers "how well does
the continuous score separate anomaly windows from normal frames inside
each file", akin to an AUC-style diagnostic. These numbers must not be
compared to official NAB scores (different protocol).

| Category | Files | Tier 0 | Tier 2 | Δ |
|---|---:|---:|---:|---:|
| realTraffic | 7 | 69.01 | **81.40** | +12.39 |
| realKnownCause | 7 | 64.20 | **78.30** | +14.10 |
| realAWSCloudwatch | 16 | 58.53 | **77.54** | +19.01 |
| artificialWithAnomaly | 6 | 46.69 | **72.23** | +25.54 |
| realAdExchange | 6 | 56.33 | **64.46** | +8.13 |
| realTweets | 10 | 55.78 | **56.66** | +0.88 |
| **Weighted (52 files)** | **52** | **58.55** | **72.02** | **+13.47** |

Same six scorers in both tiers: the +13.47 separability improvement is
attributable to normal-regime structuring alone.

Per-file behavior is sharply bimodal (Mode A: 95+; Mode B: ~0) — see §6.

---

## 4. Corpus-level single threshold (transparency)

One global threshold per method/profile (the official-NAB-style protocol).
Disclosed for transparency; we do not adopt fixed-global-threshold scoring
as a design target. `python -m tests.nab.benchmark_nab_corpus --aggregate`.

| Method | anchored¹ | minmax² | per-file sweep (§3 protocol) |
|---|---:|---:|---:|
| Lambda³-R (Tier 2) | **33.40** | 26.72 | 72.15 |
| iForest (exclusion) | 27.87 | **43.71** | 70.93 |
| iForest (streaming) | 21.14 | 34.87 | 70.58 |
| OC-SVM (exclusion) | 6.93 | **53.46** | 78.75 |
| Lambda³-S (Tier 0) | 3.79 | 23.66 | 58.48 |
| OC-SVM (streaming) | 2.13 | 0.00 | 59.09 |
| LOF (either mode) | 0.00 | 21–41 | 62–69 |

¹ anchored: fixed monotone map of each method's native boundary to 0.5
(Lambda³ `r/(1+r)`; baselines `sigmoid(−df)`) — usable online, no
per-file information.
² minmax: per-file min-max before the global threshold — requires the
file's full score range, i.e. retrospective (future information).

Two observations: (a) per-file sweeps inflate everything by +25 to +59
points — the reason §3 is a diagnostic, not a claim; (b) under the only
online-deployable variant (anchored), **Lambda³-R leads all self-run
methods**: its ratio scale is the only score with cross-file meaning.
Baseline decision functions collapse without retrospective per-file
normalization.

---

## 5. The OR-voting multiple-comparison fix

Six scorers, each thresholded at trimmed-p99 and OR-voted, stack the
family-wise clean flag rate to ~6% (multiple comparisons) — the dominant
source of the native-point FP flood, an artifact of early per-file
tuning. Fix (`calibrate_combined=True`): measure the **normal structure
of the OR output itself** — per-regime τ_r = robust threshold of
`combined_clean = max_k raw_k/thr_{r,k}` on clean frames; final score =
`combined/τ_r`. Per-scorer thresholds keep aligning scorer scales; the
decision boundary derives from the clean distribution of the OR
statistic. Effect: clean flag rate ~6% → ~1–2%; corpus native FP
1087 → 266 per 10k at −2.8 points of catch (§2.2). Unit tests:
`tests/core/test_combined_calibration.py`.

---

## 6. Honest failure: Mode A / Mode B, now with an unknown-regime channel

Per-file separability is bimodal:

```
Mode A (normal regimes covered):    95+ separability, FP≈0 at per-file points
Mode B (normal structure broken):   ~0 separability — explicit failure
```

Mode B causes are structural and predictable:

| Type | Cause | Example |
|---|---|---|
| B1 | missing normal regime (seasonal/state absent from clean data) | ambient_temperature_system_failure |
| B2 | scale distortion (six orders of magnitude crush z-norm) | ec2_disk_write_bytes_c0d644 |
| B3 | long-term drift beyond regime scales | realTweets/PFE, UPS |
| B4 | sparse windows in long series (evaluation-format mismatch) | 15k+ frame files |

Since the three-state output landed, Mode B is no longer silence: frames
outside known normal structure surface on the **unknown channel**
(`state=2`), which by itself catches 85% of all windows (§2.1). "Says
I-don't-know when it doesn't know" is now a measured detection channel,
not only a philosophy.

---

## 7. Experimental progression (kept honest)

| Stage | Result | Lesson |
|---|---|---|
| Tier 0 streaming | separability 58.55 | 6 scorers + OR voting work zero-shot |
| Tier 2 v1–v6 (K, threshold methods) | separability 72.02 (v3: BIC + trimmed p99) | regime structure, not scorer count, drives separability (+13.47) |
| Self-run baselines under same harness | OC-SVM excl. 78.75 (per-file sweep) | per-file sweeps inflate everything → protocol audit |
| Corpus-level re-evaluation | all methods drop 25–59 pts | per-file-sweep numbers are separability diagnostics, never leaderboard claims |
| Native-point audit | Tier 2 FP 1087/10k | OR voting stacks 6× p99 tails — multiple-comparison inflation |
| `calibrate_combined` | FP 1087→266, catch −2.8 pts | calibrate the OR output's own normal structure |
| Unknown-regime channel | 85% catch @ 56 FP/10k, frozen default | the support boundary of normal structure is itself the detector |
| Three-state combined | 96.3% catch @ 303 FP/10k | alarm + unknown = deployable, label-free operating point |

---

## 8. Multivariate arm (SKAB / TEP) — audited results

Full protocol, hypotheses, and pre-registration amendments in
[experiment_plan_multivariate.md](../preregistrations/experiment_plan_multivariate.md)
(§11 Amendments). Summary of what survived the MSPC baseline audit:

**Identity & parity (stated plainly).** Our reconstruction scorer at
`delay_window=1` **is** PCA-SPE (`tests/probes/test_mspc_sanity.py`); at
matched FAR under the same label-free threshold family, our variants
are at parity with calibrated SPE / Hotelling T² / SPE∨T² on both TEP
(±2 pts) and SKAB (edge trades). An earlier "joint needs 6.5× less FP
budget than marginal detection" claim is **retracted** — it compared
calibrated joint statistics against an uncalibrated OR-of-channels
(multiple-comparison inflation, §5).

**The unknown channel across scales** (the result that repeats):

| Dataset | d | Unknown channel result |
|---|---:|---|
| NAB | 1 | 85.0% catch @ 0.56% FP, frozen default (§2.1) |
| SKAB (real rig) | 8 | 100% catch (34/34) @ 382 FP/10k; catches both windows T² misses (both K_eff=3 multimode files) |
| TEP-Braatz | 52 | degenerates **exactly** to Hotelling T² (BIC selects K=1 on the single-mode process) |
| Ghost-state synthetic | 2 | global T² rates the fault *more normal than average*; multi-regime support boundary catches >80% (`tests/probes/test_regime_ghost_state.py`) |

> **Hotelling T² is the K=1 special case of the unknown channel.** The
> contribution is the regime-resolved, full-space, three-state,
> self-calibrating generalization under one frozen configuration (1ch → 52
> variables), not the statistic.

**Contextual-anomaly finding.** Under the refined tagging rule
(beyond-chance band exit), SKAB has 0/34 contextual windows and TEP
faults reach a sustained marginal band exit within ~2 samples (median
lead −1): **pure contextual anomalies are rare in public benchmarks**.
The contextual existence proof is synthetic
(`tests/probes/test_contextual_mechanism.py`: joint residual 100% of break
frames while per-channel detection stays at matched-phase background).
H2 (covariance ablation): strong form falsified — one extra
axis-aligned component substitutes for correlation; support geometry,
not covariance parametrization, is what matters
(`tests/probes/test_h2_covariance.py`).

**The duel (Yu-Qin FGMM-Bayes / OC-SVM) — outcome: parity, two deltas.**
Against a disclosed reconstruction of Yu & Qin 2008 (both plausible
readings, stronger taken), detection is at **parity**: ghost 100% for
every GMM-family index; SKAB FGMM-BIP 100%@266 vs unknown 100%@253.
The multimode advantage over T² belongs to the multimode-GMM lineage,
and no detector superiority over it is claimed. Surviving deltas:
(i) BIP saturates in inter-mode valleys — ghost margin **+0.0 IQR**
(numerically marginal detection) vs **+30.3** (raw density floor) /
+42.7 (min-Mahalanobis): severity gradation for graded
self-preservation signals; (ii) OC-SVM at frozen standard config is
**valley-blind** (0% ghost detection; SKAB FP floors 337–348 vs 253).

**Deployability (measured, parity first).** diag-GMM support floor:
ghost = full (100%); TEP reduced-space = full (55.3%@0.81%); SKAB
33/34 @ 176 FP/10k vs full 34/34 @ 253 (one-window trade, disclosed).
Inference at d=52, K=3: **diag 468 FLOPs/frame, 1.26 KB, no matrix
ops, 325 ns/frame (desktop-measured; FLOPs/memory are
platform-independent — on-device measurement future work)** vs
full-GMM 8,580 / 33 KB / 1,122 ns vs OC-SVM 18,094 / 35 KB /
10,340 ns. BIP inference shares full-cov's O(K·d²); BIC×K training is
heavier than Figueiredo-Jain (offline, disclosed). OC-SVM's ghost
blindness is a zero-tuning-regime finding (default-vs-default by
design; disclosed as config-dependent).

**Frozen-config transfer** (`tests/multivariate/exp_frozen_transfer.py`): the
percentile operating point keeps its designed meaning across scales
(realized 0.33–1.06% vs designed 0.5%, d=2→52) with detection retained
(58.1% of TEP fault frames at the transferred point — the
silent-transfer check applied to ourselves), while a once-frozen
OC-SVM bandwidth collapses structurally (5.2%→21.9%→100% FAR — the
load-bearing claim; the re-derived-γ ×4.7 at d=52/n=300 is auxiliary,
confounded with small-sample, stated first). Full accommodation row:
OC-SVM granted our entire out-of-sample percentile mechanism — FAR
rescued at d=8 (21.9%→4.5%) but detection 0.0% at d=52 under a
perfectly transferred threshold: threshold semantics and score
validity are independent failure axes. Deployability advantage over
bandwidth/fixed-limit operating points only (not Yu-Qin auto-K).
Transferability design conditions, each with a measured
counterexample: out-of-sample thresholds (×32 our own drift),
dimensionality control, score validity.

**The worked downstream consumer** (`tests/probes/test_downstream_policy.py`):
a rule-based policy over the interpretation payload emits four graded
actions (transient check / schedule maintenance / reduce & investigate /
stop & escalate) from event type, egress signature (leak 0.65 vs ghost
3.4–8.2 IQR/frame onset), and non-saturating depth (5 vs 42 IQR) —
including the two ghost actions a BIP-driven policy provably collapses
(BIP saturated at ~1.0 on both). Quiet on ≥97% of normal frames.

Reproduce: `python -m tests.multivariate.benchmark_skab`, `python -m
tests.multivariate.benchmark_tep`, `python -m tests.multivariate.contextual_stratify`,
`python -m tests.multivariate.exp_support_duel`, `python -m tests.multivariate.exp_deployability`,
`python -m pytest tests/probes/test_downstream_policy.py`
(SKAB and TEP cloned per tests/multivariate/skab_datasets.py / tests/multivariate/tep_datasets.py).

---

## 9. Reproducibility

```bash
git clone https://github.com/miosync-masa/NSAD.git
cd NSAD
pip install .
git clone --depth 1 https://github.com/numenta/NAB.git NAB

# separability (per-file sweep) — Tier 0 / Tier 2
python -m tests.legacy.benchmark_nab_streaming --category realKnownCause   # etc.
python -m tests.legacy.benchmark_nab_regime    --category realKnownCause   # etc.

# corpus-level + self-calibrated evaluations (caches per-file scores)
python -m tests.nab.benchmark_nab_corpus --compute --methods all
python -m tests.nab.benchmark_nab_corpus --aggregate
python -m tests.nab.benchmark_nab_selfcal

# self-run classical baselines (per-category harness)
python -m tests.nab.benchmark_nab_baselines --category all
```

Deterministic: GMM `random_state=0`; separability weighted mean 72.02 ± 0.01.

---

## License & citation

MIT. See repository root.

```bibtex
@software{lambda3_nnnu_2026,
  title  = {Normal-Structure Anomaly Detection (Lambda³ NSAD): detecting deviation from mathematically structured normality without neural networks},
  author = {Iizumi, Masamichi},
  year   = {2026},
  url    = {https://github.com/miosync-masa/NSAD},
}
```
