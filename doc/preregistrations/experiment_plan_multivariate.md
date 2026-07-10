# Lambda³-NSAD — Experiment Plan: Multivariate / Contextual-Anomaly Extension

Working plan for the EAAI submission's multivariate arm. Sits beside
`abstract.md`, `architecture.md`, `future_work.md`, `scoreboard.md`.

**One-line thesis.** Marginal-flag-gated single-channel detection
*structurally* misses **contextual anomalies** (each channel in its own
normal range, but the *joint* structure broken). Regime × correlation-residual
structure catches them **without learning anomaly shapes** — extending C2
(temporal geometry expansion) from univariate to *temporal + relational*
geometry, and lifting the framework from point anomalies to contextual
anomalies (Chandola et al. 2009 taxonomy).

**Parsimony note (a strength, state it).** V2–V4 below require almost **no
new detector code**: the reconstruction scorer already accepts `(n, d)`,
GMM already clusters multivariate, the unknown-regime channel and kernel
scorer already exist. The extension is mostly *feeding `d>1` through
existing machinery* + rigorous evaluation. New work concentrates in
evaluation harness and ablation, not in the detector.

---

## 1. Hypotheses and pre-registered decision rules

| ID | Hypothesis | Confirmed if | Kill / rethink if |
|---|---|---|---|
| **H1** | Contextual anomalies are structurally invisible to marginal-gated single-channel detection but visible to joint structure | On **contextual-labeled** anomalies, V2/V3 catch ≫ V0 (V0 ≈ chance), while on **univariate-labeled** anomalies V2/V3 ≈ V0 (no regression from going multivariate) | V0 already catches contextual anomalies (thesis void), **or** V2/V3 regress badly on univariate anomalies (multivariate machinery not free) |
| **H2** | The correlation term itself carries the detection, not just extra features | `full` covariance ≫ `diagonal` covariance on contextual anomalies | `diagonal` ties `full` → the coupling is not what fires; claim unsupported |
| **H3** | Regime-conditioning is needed under multi-modal operation | V3 (regime-conditioned residual) removes the false alarms that V2 (global residual) emits at operating-mode changes | V2 already clean across mode changes → regime layer unnecessary for this axis (report honestly, drop it) |

**Falsifiability discipline.** No variant is claimed until the mechanism
probe (Step 1) fires on the 2-channel synthetic. Run before believing.

---

## 2. The variant ladder (the experimental spine)

Escalating structure. Each step isolates one mechanism. This ladder is
*also* the Introduction narrative: start from the reader's naive solution,
show where it breaks, escalate.

| Variant | What it is | Handles | New code |
|---|---|---|---|
| **V0** | Per-channel independent NNNU + late-fusion rule ("temp alarms → check current"), i.e. alarm rationalization | Univariate anomalies only. **Cannot** fire when marginals stay in-range | Fusion rule (small; = `MultiChannelDiagnostics` core) |
| **V1** | Manual-regime buckets: bucket by a *known* conditioning channel (e.g. current), per-bucket 1-D threshold | Conditional anomalies **when the conditioning axis is known** (motor: current = load) | Small helper |
| **V2** | Multivariate reconstruction residual: existing `StreamingReconstructionScorer` with `d>1`; SVD subspace over joint delay-embedding; residual fires on coordination break | Linear cross-channel coupling, unknown direction (symmetric) | **None** (`d>1` already supported) |
| **V3** | Regime-conditioned multivariate residual: Tier-2 `RegimeAwareDetector` with `d>1`, **full-covariance** GMM regimes, residual computed within regime | + multi-modal operation (startup / steady / shutdown) without mode-change false alarms | Config + z-norm + verification |
| **V4** | Full joint GMM + **unknown-regime channel** (ll-floor) + kernel scorer, all multivariate | + unknown coupling structure (high-d, unknown causal axis) and **nonlinear** coupling; coordination break exits the fitted support → `state=2` | **None** (channel + kernel scorer exist) |

**Three-layer coupling coverage** (feed all 6 scorers multivariate):
linear correlation → reconstruction (V2); piecewise-linear → regime (V3);
nonlinear → kernel (V4). Roles partition cleanly.

**Design guardrails (do not violate — NNNU honesty):**
- Detection layer may be joint; **diagnosis layer stays a per-channel /
  per-scorer contribution decomposition** so "which channel broke the
  ellipse" is recoverable. Keep the detection/diagnosis separation from
  `future_work.md §2.2` — only the *detection* internals go joint.
- Per-channel z-normalization **first**, always (Mode B2: 6-order scale
  gaps otherwise let one channel eat the subspace).
- Do **not** blindly full-joint high-d. Use the **known correlation graph**
  (which sensors the plant co-instruments because they are known to couple)
  to build residual features on small subsets. Curse of dimensionality:
  full-cov params grow as d²; fine at 4–8, not at 52.

---

## 3. Datasets

| Role | Dataset | ch | Why | Access |
|---|---|---:|---|---|
| **Mechanism probe** | Synthetic 2-ch (current↔temperature): correlated normal + injected coordination break at (low current, high temp) | 2 | Existence proof + the left/right figure; both marginals in-range | self-generated |
| **Contextual + regime, primary** | **TEP** (Tennessee Eastman Process) | ~52 (use coupled subset ≤8) | Causally coupled process variables; **operating modes = regimes**; faults propagate cross-variable → genuine contextual anomalies | Harvard Dataverse |
| **Real physical, multivariate** | **SKAB** (Skoltech Anomaly Benchmark, water-pump testbed) | **8** | Real rig, correlated sensors, physical-origin labeled faults (cavitation, imbalance, reduced motor power) manifesting across coupled sensors | Kaggle |
| **Single-channel anchor** | **NAB** (already done) | 1 | Continuity with the univariate results in `scoreboard.md`; shows the extension is additive | GitHub |
| **Diagnosis-layer demo** | Synthetic 4-ch motor (vib / temp / strain / current) | 4 | `MultiChannelDiagnostics` fault-mode inference (flag-combination → fault mode) | self-generated |
| *(optional)* | UCI Hydraulic Systems / CMAPSS | multi | Mechanical / condition-monitoring alternative if a motor framing is preferred over process | UCI / NASA |

**Avoid as headline: SWaT / WADI / SMD.** Their anomalies are predominantly
*univariate* (single-channel), single-channel methods tend to win on them,
and much of SWaT is detectable from one feature — validating a
*multivariate-coupling* thesis there invites the reviewer to say "single-
channel is enough here." May appear only as a secondary/known-limitation
mention, never as the demonstration. Likewise SMAP/MSL: each entity is
effectively one sensor + one-hot commands → no coupling to test.

**TEP honesty.** TEP is a *simulation* — but a two-decade-standard,
community-accepted public benchmark, distinct from bespoke synthetic data.
State this and pair it with **SKAB (real rig)** so "real-physical evidence"
(SKAB) and "coupled-process + operating-mode evidence" (TEP) are covered
by different sources.

---

## 4. Critical evaluation design — contextual vs univariate stratification

**This is the reviewer-proofing move. Do not report a single averaged F1
over all anomalies.**

For every labeled anomaly/event, tag it:

- **Univariate** — visible in at least one channel's *marginal* range
  (some channel leaves its own normal band).
- **Contextual** — all channels' marginals stay in-range; only the *joint*
  configuration is out of normal structure.

Tagging procedure (disclosed, reproducible): per-channel marginal
normal band = clean-data quantile interval; an event is *univariate* if any
channel exits its band during the window, else *contextual*. Report the
split counts per dataset.

**The proof table** (the paper's novelty made empirical):

|  | Univariate anomalies | Contextual anomalies |
|---|---|---|
| V0 (single-channel + fusion) | catches (≈ parity) | **structurally misses** |
| V2 / V3 (joint structure) | ≈ V0 (no regression) | **catches** |

If this pattern holds → contribution is proven on the *right subset*, and
the SWaT-style objection ("single-channel is enough") is pre-empted:
*we concede parity on univariate anomalies and claim the gain precisely
where single-channel cannot go.*

---

## 5. Metrics (consistent with `scoreboard.md` industrial framing)

- **Window catch rate** (share of labeled windows with ≥1 flag) and
  **FP per 10k out-of-window frames**, at **self-calibrated, label-free**
  operating points. Primary.
- **Unknown-channel (`state=2`) catch / FP reported separately** — the
  thesis is that the *support boundary* detects the coordination break, so
  the unknown channel is a first-class result, not a fallback.
- **Per-channel contribution decomposition** at each flagged frame
  (diagnosis-layer interpretability: which channel drove the residual).
- Per-file / per-fault-type breakdown for TEP (fault modes differ sharply).
- Deterministic (`random_state=0`), single frozen configuration across all
  files of a dataset; no per-dataset tuning.

---

## 6. Ablations (isolation logic — each isolates one claim)

| Ablation | Isolates | Expected |
|---|---|---|
| V0 → V2 (scorers held constant) | effect of **joint structure** alone | V2 gains only on contextual anomalies |
| V2 → V3 | effect of **regime-conditioning** under multi-modal operation | V3 removes mode-change false alarms (tests H3) |
| `diagonal` vs `tied` vs `full` covariance | whether the **correlation term** does the work | `full` ≫ `diagonal` on contextual (tests H2) |
| reconstruction (linear) vs kernel (nonlinear) | linear vs nonlinear coupling | kernel adds catch only where coupling is nonlinear |
| per-channel z-norm on vs off | scale-domination (Mode B2) | off → one channel eats the subspace |
| joint-all-d vs known-graph subsets | curse of dimensionality vs domain-graph features | subsets ≥ full-joint at high d, and are interpretable |

---

## 7. Legitimacy rule (carried over unchanged from `scoreboard.md §1`)

- Anomaly labels used **only** for (i) training exclusion from normal-
  structure construction and (ii) final scoring. Never as positive
  examples, shape templates, or threshold targets.
- TEP: exclude fault segments when building normal structure; use fault-
  free (Fault 0) for calibration. SKAB: use the authors' train (normal) /
  test split. NAB: as already done.
- No anomaly-shape learning. Single frozen config. No per-dataset tuning.
- Regime labels may use full-series information (as in current Tier 2) but
  **never anomaly frames** — keep the causal caveat explicit.

---

## 8. Risks specific to the multivariate extension

| Risk | Mitigation |
|---|---|
| Linear subspace misses nonlinear coupling | escalate to kernel scorer (V4); report which datasets need it |
| Direction of conditioning unknown | prefer **symmetric** subspace residual (reconstruction) over regression `r = temp − f(current)`; regression fixes a causal direction the sensing may not justify |
| Full-cov GMM under-determined at high d | known-correlation-graph subsets, not blind full-joint; cap joint dimension |
| Diagnosis blur when detection goes joint | recover cause via per-channel contribution decomposition (§5) |
| TEP = simulation | pair with real SKAB; state the ideal-vs-available contrast as in `abstract.md §4` |
| Mode-change false alarms (global residual) | regime-conditioned residual (V3); this is exactly what H3 tests |

---

## 9. Execution order (hand-off to 環, each step independently committable)

1. **Mechanism probe.** Existing `StreamingReconstructionScorer`, 2-ch
   synthetic (correlated normal + one coordination-break point). Confirm
   residual fires while both marginals stay in-range. *Gate: if this does
   not fire, stop and reconsider the feature — do not proceed.*
2. **Mode-change probe.** Same 2-ch, add an operating-mode change in the
   normal segment. Does the **global** residual (V2) false-alarm at the
   mode change? If yes → motivates V3.
3. **SKAB `d=8` via existing reconstruction scorer (V2).** First real-data
   multivariate check. Report catch / FP and the univariate/contextual
   split.
4. **V3 on SKAB + TEP.** Wrap in Tier-2 `RegimeAwareDetector`, `d>1`,
   `covariance_type=full`, per-channel z-norm. Verify unknown channel
   (`state=2`) fires on contextual breaks.
5. **Stratify + proof table (§4).** Tag every anomaly univariate/contextual;
   build the V0-vs-V2/V3 contrast. This is the figure/table the paper turns on.
6. **Ablations (§6).** Covariance type first (H2), then regime (H3), then
   kernel, then z-norm.
7. **Diagnosis demo.** 4-ch motor synthetic → `MultiChannelDiagnostics`
   fault-mode inference (flag-combination → fault mode).

---

## 10. Deliverables → paper mapping

| Output | Paper slot |
|---|---|
| Fig: naive late-fusion misses vs joint catches (synthetic → confirmed on TEP/SKAB) | Introduction hook + Results headline |
| Table: univariate vs contextual stratified catch (§4) | Results — the novelty proof |
| Table: covariance ablation `diagonal`/`tied`/`full` (H2) | Ablation |
| Fig: per-channel contribution decomposition | Discussion — AI-ready interpretation payload |
| SKAB real-rig result + TEP coupled-process result | Evaluation — real + coupled evidence pair |
| Framing: "contextual anomaly handled by structure expansion, not shape learning" | positions C2 as a contextual-anomaly contribution (Chandola taxonomy) |

**Nociception:** one sentence only, as in `abstract.md` — multi-channel
coordination break = "unfamiliar body state." Do not build on it.

---

## 11. AMENDMENTS (post-execution; original text above unchanged)

Pre-registered decision rules were applied as written. Changes and
verdicts, in the open:

### A1. Tagging rule refined (pre-reg change, approved)

The §4 rule "univariate if any channel exits its band" is statistically
broken for long events: with a [0.5%, 99.5%] band, ~1% of frames of a
*fully normal* window sit outside by construction. Refined rule
(implemented in `tests/probes/test_contextual_mechanism.py`,
`tests/multivariate/contextual_stratify.py`, `tests/multivariate/benchmark_tep.py`): a channel
counts as exited only **beyond chance** — out-of-band fraction > 2× the
nominal tail mass, or a sustained run (≥5 consecutive frames). This
change makes the SKAB finding *stronger*: zero contextual windows under
a rule that resists chance-level mislabeling.

### A2. H1 verdicts per dataset

| Dataset | Verdict |
|---|---|
| Synthetic (anti-phase probe) | **Confirmed**: V0 flag rate at matched-phase control level (blind); joint residual 100% of core frames at 1.3% normal flag rate |
| SKAB (real rig) | **No contextual events exist** (34/34 univariate; flow exits band in 31/34). Finding, not failure |
| TEP-Braatz | **No contextual events**; faults propagate to sustained marginal band exit within ~2 samples (median lead −1). "Contextual" is a *phase*, and in TEP that phase is ~6 minutes |

Cross-dataset finding (pillar ③): **pure contextual anomalies are rare
in public benchmarks** — physical faults propagate to marginals within
minutes. To be connected to the benchmark-transparency literature
(Wu & Keogh; Wenig et al.) as a methodological contribution.

### A3. Baseline audit (the MSPC reckoning)

Our joint reconstruction scorer at `delay_window=1` **is** PCA-SPE
(identity verified: `tests/probes/test_mspc_sanity.py`, corr > 0.99). Against
the calibrated MSPC standard (PCA-SPE / Hotelling T² / SPE∨T²,
Chiang-Russell-Braatz) under the identical label-free threshold family:

- TEP: v2 66.3%@2.04 FAR vs SPE 65.4%@2.01 vs SPE∨T² 67.2%@2.45 — parity.
- SKAB: T² 94.1% catch @ ~120 FP/10k floor vs v2/unknown 100% @ ~223–253
  floor — edge trades, no decisive win.

**The FP-efficiency headline ("joint needs 6.5×/4–30× less FP budget
than marginal detection") is retracted**: it compared calibrated joint
statistics against an *uncalibrated* OR-of-channels — the same
multiple-comparison inflation fixed by `calibrate_combined` in the
univariate work. Against properly calibrated MSPC, no FP-efficiency
claim survives. What survives: the NNNU skeleton contains classical
MSPC as a zero-new-code special case.

### A4. The unknown channel positioning (the spine)

On single-mode TEP, the reduced-space unknown channel degenerates
**exactly** to Hotelling T² (BIC selects K=1). On multimode data it
does not: the two SKAB windows T² misses at q=0.999 are both K_eff=3
files, and the multi-regime unknown catches both; on the synthetic
ghost state (coupling-consistent forbidden middle between operating
modes) the global T² rates the fault *more normal than average* while
the multi-regime support boundary catches >80% of it
(`tests/probes/test_regime_ghost_state.py`).

> **Hotelling T² is the K=1 special case of the unknown channel.** The
> contribution is not the statistic — it is the regime-resolved,
> full-space, three-state, self-calibrating generalization that spans
> univariate NAB to 52-variable TEP on one frozen configuration.

### A5. H2 outcome (synthetic-only per amendment; strong form falsified)

Pre-registered kill condition fired: at BIC-matched policy, diagonal
ties full (both 100% on the anti-phase break). Characterization
(`tests/probes/test_h2_covariance.py`): full = 100% at every K∈[1,5]; diag =
0% at K=1, 100% at K≥2. Correlation orientation is everything at
minimal complexity; one extra axis-aligned component substitutes for
it. Implication: what matters is capturing the **support geometry** of
normality, by whichever parametrization — the support-boundary framing
absorbs H2.

### A6. Strategy (directed)

The multivariate arm is **not** a standalone paper. It folds into the
main NSAD EAAI paper as a generality + honest-benchmarking section.
The paper's spine (three pillars):

1. **Unknown channel** — three-state density-support detection,
   frozen-default, NAB 85%@0.56% → SKAB 100%@382/10k → TEP (=T² at K=1;
   exceeds it on multimode data). MSPC's in-model statistics do not
   have this channel as first-class three-state semantics.
2. **Label-free self-calibration + one frozen config across scales** —
   1ch NAB → 8ch SKAB → 52-var TEP with no per-dataset tuning; MSPC
   practice tunes per process.
3. **Honest benchmark finding** — contextual anomalies are rare in
   public benchmarks; per-file-sweep and uncalibrated-OR protocol
   pitfalls quantified (+25–59 pts; multiple-comparison inflation).

MSPC is treated head-on in Related Work; "joint SPE FP-efficiency" is
never a headline. Regime layer: supporting role with the ghost-state
demonstration and the 2/2 SKAB multimode recovery as evidence.

### A7. The real duel — Yu-Qin FGMM-Bayes and OC-SVM (outcome: b, with two deltas)

The ghost-state result of A4 beat single-model T² — the baseline Yu &
Qin (AIChE J. 54(7):1811, 2008) already superseded with FGMM + a
Bayesian-inference probability index. The duel against the actual
lineage was run with a disclosed reconstruction (paper paywalled; both
plausible readings implemented — posterior-weighted χ² BIP and
min-Mahalanobis — evaluated against the stronger;
`tests/baselines/fgmm_bayes.py`, `tests/multivariate/exp_support_duel.py`).

**Outcome (b) — detection parity.** On the ghost, every GMM-family
index catches 100%; on SKAB, FGMM-BIP matches the unknown channel
(100%@266 vs 100%@253 per 10k). The multimode advantage over T²
(A4's SKAB 2/2) belongs to the multimode-GMM lineage as a whole, not to
the density floor specifically. Per the pre-committed guardrail, all
detector-superiority claims versus multimode-GMM monitoring are
dropped; the ghost figure remains captioned "vs single-model T²".

**Two honest deltas survive the duel:**

1. **Severity saturation.** BIP ∈ [0,1] saturates in deep inter-mode
   valleys: ghost margin +0.0 calibration-IQR above threshold
   (detection is numerically marginal), vs +30.3 for the raw density
   floor and +42.7 for min-Mahalanobis. Probability-saturating indices
   lose severity gradation — required for graded self-preservation
   signals (nociception Levels) — while unnormalized density/distance
   scores retain it.
2. **OC-SVM valley blindness — a zero-tuning-regime finding.** At the
   frozen standard config (RBF, ν=0.05, gamma='scale'), OC-SVM misses
   the ghost entirely (0% detection) while catching all marginal SKAB
   faults; its SKAB FP floors are also higher (337–348 vs 253 per 10k).
   Stated explicitly: this is config-dependent — a tuned bandwidth may
   see the valley. The comparison is default-vs-default deliberately,
   because the framework's entire claim is zero-tuning operation;
   per-rig tuning is exactly the practice being avoided. The finding is
   about the zero-tuning regime, not a handicapped opponent.

### A8. Deployability — the diag light path (parity measured, then cost)

H2's falsification (A5) implies the surviving pillar needs no full
covariance. Parity of the diag-GMM support floor
(`tests/multivariate/exp_deployability.py`): ghost diag = full (100%, same FP); TEP
reduced-space diag = full (K_eff=1, 55.3% @ 0.81% FAR); SKAB diag
33/34 @ 176 FP/10k vs full 34/34 @ 253 — a one-window trade at lower
FP, disclosed. Measured inference cost at d=52, K=3: **diag-GMM 468
FLOPs/frame, 1.26 KB parameters, zero matrix operations, 325 ns/frame**
vs full-GMM 8,580 / 33 KB / 1,122 ns and OC-SVM 18,094 / 35 KB /
10,340 ns. Honesty constraints stated: BIP inference is the same
O(K·d²) family as full-covariance likelihood (Bayes only normalizes the
same K Gaussian evaluations); our BIC×K training is likely heavier than
Figueiredo-Jain (offline, once, not claimed). Pillar ② gains measured
edge-class frugality: the support floor that ties the field runs
matrix-free at microcontroller-class cost.

### A9. The worked downstream consumer (the castle) + final reframe

`tests/probes/test_downstream_policy.py`: a small rule-based policy consumes
the interpretation payload — three-state channel, per-scorer
attribution, and the non-saturating unknown margin *including its
trajectory* — and emits per-episode graded actions on a bimodal rig:

| Event | Payload signature | Action |
|---|---|---|
| fast transient (in-support spike) | state=1, fast-group dominant | L1 transient check |
| slow leak (gradual support egress) | state=2, onset 0.65 IQR/frame | L1 schedule maintenance |
| shallow ghost (abrupt egress) | state=2, onset 3.4, depth ~5 IQR | L2 reduce & investigate |
| deep ghost (valley center) | state=2, onset 8.2, depth ~42 IQR | L3 stop & escalate |

Asserted contrasts: (i) FGMM-BIP (fair z-space fit) saturates at ~1.0
on both ghosts (|Δ| < 0.02) — a BIP-driven policy is **structurally
forced** to give the shallow and the deep ghost the same action, while
the non-saturating margin separates them 8.3× and the frozen policy
(DEEP=10 IQR) crosses the L2/L3 line between them; (ii) *how* the
process left normal structure is readable from the margin trajectory
alone (leak 0.65 vs ghosts 3.4/8.2 IQR/frame, 5-frame smoothed) — no
extra detector machinery. Quiet on ≥97% of normal frames. Structural
defaults frozen; only rig geometry was designed.

**Final reframe (directed).** Pillars restated: ① non-saturating,
decomposable, regime-attributed interpretation payload (now
demonstrated, not just measured); ② edge-class deployability
(desktop-measured wall-clock, platform-independent counts, on-device
future work); ③ honest benchmarking. Detection parity with the
MSPC/GMM lineage is presented as **expected by construction** (T² =
K=1 special case; SPE = reconstruction) — the paper claims no SOTA
detector and is an engineering-applications paper. **Nociception
positioning updated** (openly): from a single guarded sentence to the
Discussion's empirical design rationale for non-saturating severity —
the restriction was set when the evidence was poetic; the duel made it
measured (+0.0 vs +30.3 IQR), and the consumer made it demonstrated.
Pain that cannot grade cannot prioritize.

### A10. Frozen-config transfer test — pillar ② gets its contrast

The missing half of pillar ② ("we transfer" was demonstrated; "they
don't" was not). `tests/multivariate/exp_frozen_transfer.py`: each method fixes its
operating point on a fit split; realized clean flag rate on held-out
frames vs each method's own designed rate, across 2ch → 8ch → 52ch:

| Method (realized FAR / detection at the transferred point) | rig2 (d=2) | SKAB (d=8) | TEP (d=52) |
|---|---|---|---|
| ours (0.5% floor, designed 0.5%) | 1.06% / 100% | 0.33% / 57.8% | 0.00% / **58.1%** |
| OC-SVM, γ frozen once (designed 5%) | 5.19% / 100% | **21.9% (×4.4)** / 80.6% | **100% (×20, collapse)** / 100%* |
| OC-SVM, γ='scale' re-derived (designed 5%) | 5.12% / 100% | 4.60% / 68.0% | **23.5% (×4.7)** / 88.1% |
| OC-SVM + our mechanism ('frozen+cleanq') | 5.62% / 94.0% | 4.53% / 68.3% | 0.00% / **0.0%** |

\* 100% FAR = flags everything; its "detection" is vacuous.

**The two 0.00%s, distinguished (the kill criterion applied to
ourselves).** A silent detector transfers its FAR trivially — that is
exactly how the hybrid row was killed (FAR 0.00%, detection 0.0%). Our
own d=52 realized FAR is also 0.00%, so the same check must apply: at
that transferred operating point our detection is **58.1% of fault
frames** (same run, same table). FAR semantics AND score validity
transfer together for the density floor; the hybrid transfers only the
threshold over a bandwidth-dead score. The two-axis decomposition of
A10.1 closes on ourselves.

**Mechanism, stated once**: our operating point is a percentile of the
detector's own clean-score distribution — its meaning ("flag x% of
clean") is dimension-, scale-, and shape-invariant, i.e. the threshold
semantics are generated internally from the clean structure rather than
supplied externally. An RBF bandwidth enters as exp(−γ‖x−y‖²), which
grows with dimension and scale: γ frozen at d=2 degenerates the kernel
at d=52 (100% FAR — everything flagged), and even per-dataset
re-derivation (γ='scale') drifts ×4.7 at d=52/n=300.

**Self-catch, disclosed (the third in-sample-bias occurrence)**: the
first run of this very test drifted our own method ×32 at d=52 — an
in-sample floor over an overfit 52-D density. The transfer property
holds only under two load-bearing protocol guardrails, now explicit:
out-of-sample floors (nested split) and high-d PCA reduction. The
percentile SEMANTICS transfer; the density estimate must be sane.

**Scope and language (pre-committed nails)**: deployability advantage,
not performance (a tuned OC-SVM out-catches Lambda³-R at matched NAB
points, scoreboard §2.3); the advantage's scope is OC-SVM-style
bandwidths and fixed control-limit MSPC — NOT Yu-Qin FGMM, whose
Figueiredo-Jain auto-K is equally self-adapting on this axis. Paper
language is fixed as: **"no per-dataset tuning — structural defaults,
frozen-config transfer demonstrated, adjustable if desired"** — never
"parameter-free" (already retracted once, LEDGER), never bare
"tuning-free". OC-SVM's ghost catch at its loose native ν=5% point is
noted; the duel's valley-blindness finding was at matched low-FAR
points and stands.


#### A10.1 Refinements (asymmetry, accommodation, and the principle)

**Claim weighting (asymmetric, pre-committed).** The transfer claim
stands on the frozen-γ structural collapse (×20, kernel saturation with
dimension — clean mechanism). The γ='scale' ×4.7 drift is auxiliary:
at d=52/n=300 it is confounded with the small-sample regime; a
sample-size contribution cannot be excluded. We say so first.

**Full accommodation (the hybrid row).** OC-SVM was granted our entire
operating-point mechanism (nested out-of-sample clean-percentile,
'frozen+cleanq'): at d=8 it rescues frozen-γ's FAR (21.9% → 4.5%, det
68.3%); at d=52 the FAR transfers (0.00%) **but detection is 0.0%** —
the percentile mechanism transfers threshold semantics for any score,
and cannot rescue a score the bandwidth has degenerated. Two
independent failure axes: threshold semantics vs score validity.
Conversely: even granting OC-SVM the per-dataset self-adaptation we
forgo (γ='scale'), its realized FAR drifts, while our zero-adaptation
point holds at design.

**Transferability design conditions (the guardrails, as principle).**
Operating-point transferability requires all three: (i) out-of-sample
threshold estimation — removing it broke US at ×32 (in-sample
percentile bias); (ii) dimensionality control of the density estimate
— a 52-D full covariance from 300 samples is not a sane density;
(iii) a score whose validity survives the transfer — the frozen
bandwidth fails exactly here (axis decomposed by the hybrid row). Each
condition has a measured counterexample in this repository. This is
not a caveat list; it is the design condition set for transferable
operating points, formulated with failure evidence.

**Positioning.** Pillar ② is the paper's one clean quantitative win —
"we transfer at design rate, the bandwidth collapses, with mechanism" —
and it exists on an axis (operating-point transferability) where
neither MSPC nor OC-SVM competes, the axis vacated by leaving the
detection contest. Pillar ① wins on semantics with detection parity;
pillar ③ is meta; pillar ② is the measured victory.
