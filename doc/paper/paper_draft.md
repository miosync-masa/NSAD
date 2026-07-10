# Lambda³-NSAD — Manuscript Draft (v1 — superseded as the main line)

> **Pivot notice (2026-07-10).** The paper's center of gravity has
> moved from the generic-benchmark evidence below to the four
> pre-registered engineering validations (Paderborn #1–#3, NASA IMS
> #4). The v2 main line is [paper_v2_outline.md](paper_v2_outline.md)
> (concept: [abstract.md](abstract.md); claim–evidence map:
> [claim_evidence_map.md](claim_evidence_map.md)). **This draft is
> retained in full and unchanged below**: its §3–§4 (architecture),
> §5 (protocol), §6 (NAB/SKAB/TEP results), and §7 (worked consumer,
> failure taxonomy) are the designated Appendix source material of
> the v2 paper — generic time-series / multivariate / process
> qualification, no longer the primary novelty. No number, verdict,
> or default changed.

Target venue: **Engineering Applications of Artificial Intelligence (EAAI)**.
Working title (v1 candidate; v2 candidates are in abstract.md §1):

> Normal-Structure Anomaly Detection for AI-Ready Sensor Interpretation: A Regime-Resolved Lambda³ Architecture

Status: **complete first draft — §1 through §10.** Numbers come from
[scoreboard.md](scoreboard.md); the amendment record is
[experiment_plan_multivariate.md](../preregistrations/experiment_plan_multivariate.md);
the concept document is [abstract.md](abstract.md). Citations appear
as (Author, Year) placeholders; the bibliography is assembled and
verified against the primary sources at submission time. **Figures are
generated** (`python -m tests.figures.make_figures` → doc/figures/, PDF+PNG):
Fig. 1 pipeline (§4) · Fig. 2 ghost vs single-model T² (§6.5) ·
Fig. 3 worked-consumer margin trajectory (§7.2) · Fig. 4 frozen-config
transfer, FAR paired with detection (§6.5) · Fig. 5 Mode A/B
bimodality (§7.1). **Abstract drafted** (below). First review pass
applied (claim fore-grounding: early §1 summary, payload-subject
contribution bullet, narrow "AI-ready" definition in §3.3, §2.3
slimmed, §8.2 heading engineering-ized, §6 result map, saturation
claims narrowed to the measured instance, strengthened cost-table
footnote). Remaining for submission: title selection, bibliography,
venue formatting.

Writing rules in force for this manuscript (from the working docs, binding):

- Language: "no per-dataset tuning — structural defaults, adjustable if
  desired"; never "parameter-free", never bare "tuning-free".
- Labels: never "no anomaly labels" — "no anomaly-shape learning";
  anomaly-window annotations are exclusion masks (data hygiene, not
  supervision; canonical sentences in abstract.md §4.4).
- Costs: FLOPs/parameter counts are platform-independent; wall-clock is
  desktop-measured; on-device measurement is future work.
- Detection: no superiority claim over the multimode-GMM lineage
  (Yu & Qin 2008); parity is expected by construction and disclosed.
- The autonomous-platform setting is **motivation, not a validated
  claim**: every mention of a robot must explain exactly one design
  choice; no robot is measured in this paper; on-robot validation is
  future work. "Self-preservation" is defined in one sentence at first
  use and means onboard self-diagnosis, not an agentic survival
  objective. No pain or nervous-system analogies in the Introduction.

---

## Abstract

Autonomous and embedded systems need onboard, per-frame knowledge of
whether their sensor streams remain within known normal operation —
including recognition of operating states never seen during
commissioning — and a graded measure of departure, so that protective
responses can be proportionate. Anomaly-shape learning is poorly
matched to this setting: the failures that matter have no recorded
examples, and a scalar anomaly score does not carry the structure a
protective policy needs. We present Lambda³-NSAD, a normal-structure
interpretation layer motivated by these constraints. It makes normal
operating structure explicit — causal temporal features,
Gaussian-mixture regimes with BIC-selected complexity, per-regime
robust thresholds, and a likelihood support floor — and emits a
three-state, regime-attributed payload per frame: normal within a
known regime, deviation within a known regime, or outside known normal
structure, with non-saturating severity. Every operating point is a
percentile of the detector's own clean-score distribution;
anomaly-window annotations serve only as exclusion masks (no
anomaly-shape learning); and a single frozen configuration spans
univariate to 52-variable public corpora. The support-boundary channel
alone detects 85% of the Numenta Anomaly Benchmark's labeled windows
at a 0.56% false-positive rate, and the combined output reaches 96.3%.
The framework contains PCA squared prediction error and Hotelling T²
as identity-tested special cases, and we claim no detection
superiority over calibrated multivariate statistical process control
or multimode Gaussian-mixture monitoring. The contribution sits above
detection: the operating point transfers at its designed rate from 2
to 52 dimensions with detection retained, where a once-frozen kernel
bandwidth collapses to 100% false alarms; a matrix-free path evaluates
the support floor at 468 FLOPs per frame in 1.26 KB of parameters; and
a thirty-line rule-based policy converts the payload into four
correctly graded protective actions, one of which a
probability-saturating index provably cannot emit. On-platform
closed-loop validation is future work.

## 1. Introduction

Autonomous and embedded systems — field robots, mobile manipulators,
autonomous process equipment, and ultimately humanoid platforms —
operate on raw sensor streams: actuator currents, joint temperatures,
vibration channels, process variables. As autonomy increases, a growing
share of the responsibility for avoiding damage and incidents shifts
from human supervisors onto the platform itself. Throughout this paper
we use the term *self-preservation* in a restricted engineering sense:
an onboard self-diagnosis layer, in the tradition of functional safety
and condition monitoring, by which a platform recognizes that its
observed state has departed from its known normal operating envelope
and can act to avoid self-damage or a hazardous incident. This is
body-state monitoring — predictive maintenance applied by a machine to
its own body — not an agentic survival objective, and it implies no
resistance to external control or shutdown.

This paper contributes the observation half of that layer. We propose
Lambda³-NSAD, a normal-structure interpretation layer for streaming
sensor data. Rather than returning a binary anomaly flag or a scalar
score, the layer reports a causal payload per frame: whether the
current observation is normal within a known operating regime,
anomalous within a known regime, or outside the support of known
normality; which regime it belongs to; which structural scorer fired;
and how far the observation lies beyond the relevant boundary. The
goal is not to learn failure shapes, but to make clean normal
structure explicit enough that downstream onboard logic can act on
its departures. We claim no superior anomaly detector; the
contribution is a deployable interpretation layer that turns
normal-only structure into a regime-attributed, three-state,
severity-preserving signal for downstream action.

Observation precedes preservation. Before a platform can protect
itself, it must be able to answer, per frame and onboard, a question
that raw sensor values do not answer: is the current observation
(a) inside a known normal operating regime; (b) deviating within a
known regime — and if so, along which structural axis (abrupt jump,
gradual drift, trajectory change, reconstruction failure) and how
severely; or (c) outside every operating state the platform has ever
inhabited? Protective action is then a policy over that observation —
and Section 7 demonstrates one, a plain rule-based policy consuming
the payload.

The operating conditions of this application class impose four design
constraints, and each one maps to an architectural commitment in this
work. We state the mapping explicitly because the constraints are
requirements of the application class, not stylistic preferences.

1. **Unattended operation.** A deployed autonomous platform has no
   engineer alongside it to re-tune detector bandwidths or control
   limits for each new environment, body configuration, or sensor
   suite. The monitoring configuration must therefore transfer frozen,
   and every operating point must be self-calibrated from the
   platform's own clean operating data. This is why the framework
   performs no per-dataset tuning (structural defaults, adjustable if
   desired) and derives every threshold as a percentile of the
   detector's own clean-score distribution: a percentile's meaning —
   "flag x% of clean frames" — is invariant to the scale and
   dimensionality of the signal, so the operating point survives
   transfer where externally supplied bandwidths and fixed control
   limits do not (Section 6 quantifies this).
2. **Onboard computation.** The platform carries no data center;
   monitoring competes with control loops for a microcontroller-class
   budget. This is why the architecture includes a matrix-free light
   path — a diagonal-covariance support floor evaluated in hundreds of
   floating-point operations per frame with kilobyte-scale parameters —
   rather than assuming server-side inference (arithmetic costs are
   platform-independent; wall-clock figures reported later are
   desktop-measured, and on-device measurement is future work).
3. **The world exceeds the commissioning data.** A platform in the
   field will enter body states that were never present in its
   training or commissioning logs. A monitor that can only rank the
   current observation against known classes will silently assign such
   states to the nearest familiar pattern — a mislabel precisely where
   caution is most needed. This is why "outside known normal
   structure" is a first-class output state in this framework, decided
   by the support boundary of the described normality itself, rather
   than an implicit failure mode of a two-state detector.
4. **Incident avoidance is graded.** Protective responses on a real
   platform form a ladder — continue, de-rate, investigate, stop and
   make safe — so the severity signal must keep discriminating beyond
   the alarm boundary. This is why the framework reports an
   unnormalized deviation margin rather than a probability-type index:
   probability-like scores can saturate at their extremes exactly where
   grading is needed, and Section 7 demonstrates, on two out-of-support
   events of different depths, a graded policy that a measured
   saturating index provably collapses to a single action.

Given these constraints, the prevailing formulation — learn what
anomalies look like — is poorly matched to the application class. The
failure modes that matter most are the ones with no recorded examples;
collecting examples of physical failure is destructive and expensive;
and the platform's own body changes over its service life, invalidating
learned anomaly shapes. We therefore invert the formulation: make the
*normal* structure explicit, and detect departure from it. We call this
Normal-Structure Anomaly Detection (NSAD). No anomaly shape is ever
learned; anomaly-window annotations in public corpora are used only as
exclusion masks when constructing uncontaminated normal structure —
data hygiene, not supervision. In one sentence: we do not learn
anomalies; we clean normality.

The proposed architecture, Lambda³-NSAD, implements this formulation as
follows. A raw stream is expanded into a small causal
temporal-structural feature space (value, change, local deviation,
delay-embedded trajectory, low-rank reconstruction, kernel-space
deviation). Normality is structured into operating regimes by a
Gaussian mixture with BIC-selected complexity, and six streaming
scorers are thresholded per regime by robust percentiles of clean
scores, with an explicit multiple-comparison calibration of their OR
combination. A log-likelihood floor fitted on clean data defines the
support boundary and yields the third output state. The per-frame
interpretation payload — regime label, three-state classification,
per-scorer attribution, calibrated deviation ratio, and unnormalized
support margin — is designed to be consumed by downstream logic; we
demonstrate this with a worked rule-based consumer that emits four
graded actions from event type, egress signature, and margin depth.

The scope of the evidence must be stated as plainly as the motivation.
The autonomous-platform setting supplies the design constraints above;
it is not the evaluation target, and no robot is measured in this
paper. The empirical claims live on public corpora: the Numenta Anomaly
Benchmark (NAB), used strictly as a public corpus with official anomaly
labels — every operating point is derived without test labels and no
leaderboard comparison is made; the SKAB water-circulation testbed
(8 sensors); and the Tennessee Eastman process (52 variables).
On-robot validation is future work. We are equally plain about
detection performance: the framework *contains* the classical
multivariate statistics as special cases — its reconstruction scorer at
unit delay is PCA squared prediction error, and its unknown channel
with a single regime is Hotelling's T² (both identity-tested) — so
detection parity with the multivariate statistical process control and
multimode-GMM lineage is the design working as intended, not a finding
we contest. The contributions of this paper live above detection.

Specifically, this paper contributes:

- **A three-state, regime-attributed interpretation payload with
  non-saturating severity.** The support boundary of described
  normality is promoted to a first-class output state rather than
  treated as a failure of closed-world assignment — and that channel
  proves empirically useful as a detector in its own right (85% of
  NAB's labeled windows at a 0.56% false-positive rate by itself,
  fully self-calibrated; 100% of SKAB's; degenerating exactly to T²
  for unimodal operation and exceeding it under multimode operation).
  The payload's raw margin remains usable for graded downstream action
  beyond the alarm boundary — where the probability-type index we
  evaluate saturates — and a worked rule-based consumer converts the
  payload into four graded protective actions, including a distinction
  (shallow versus deep out-of-support states) that the saturated index
  cannot make.
- **Label-free self-calibration with one frozen configuration across
  scales, at edge-class cost.** The identical configuration runs on
  univariate NAB, 8-channel SKAB, and 52-variable TEP with no
  per-dataset tuning. In a frozen-configuration transfer test, the
  realized clean flag rate stays at its designed value (0.33–1.06%
  against a 0.5% design) from 2 to 52 dimensions with detection
  retained at the transferred operating point, while a kernel bandwidth
  frozen once collapses structurally (to 100% false alarms at 52
  dimensions) — and threshold semantics are shown to be independent of
  score validity, each with a measured counterexample. The
  matrix-free light path evaluates the support floor at 468 FLOPs per
  frame with 1.26 KB of parameters at d = 52.
- **Honest benchmarking as a methodological contribution.** All
  operating points are derived under a disclosed legitimacy rule (test
  labels used only for training exclusion and final scoring); per-file
  threshold sweeps are shown to inflate every method tested by 25–59
  points and are demoted to a separability diagnostic; OR-voting
  multiple-comparison inflation is quantified and corrected; and pure
  contextual anomalies are found to be rare in the public corpora used
  (a finding, reported with its tagging rule). Self-run one-class
  baselines under the identical harness provide the empirical context,
  including the operating points where they win.

The remainder of the paper is organized as follows. Section 2 positions
the work against time-series anomaly detection, one-class novelty
detection, and multivariate statistical process control, including a
direct account of what is and is not novel relative to the
multimode-GMM monitoring lineage. Section 3 formalizes NSAD. Section 4
describes the Lambda³-NSAD architecture and its calibration mechanics.
Section 5 defines the evaluation protocol and the legitimacy rule.
Section 6 reports results across the three corpora, the protocol
audits, and the frozen-configuration transfer test. Section 7 analyzes
failures as structural feedback and presents the worked downstream
consumer. Section 8 discusses the framework as an AI-ready
interpretation layer. Sections 9 and 10 give future work — including
on-robot validation — and conclusions.

---

## 2. Related Work

This work sits at the intersection of four bodies of literature:
streaming time-series anomaly detection and its benchmark practice;
one-class and novelty detection, including the classification literature
on rejection and open-set recognition; multivariate statistical process
monitoring, in particular its multimode Gaussian-mixture lineage; and
fault detection for autonomous platforms. The positioning throughout is
the one set in Section 1: unlike black-box anomaly classification, this
work builds the structured representation that is handed to downstream
AI, before any downstream model.

### 2.1 Time-series anomaly detection and benchmark practice

Streaming anomaly detection spans classical statistics to deep sequence
models. The Numenta Anomaly Benchmark (Lavin & Ahmad, 2015) established
a streaming evaluation setting and accompanies the HTM detector (Ahmad
et al., 2017); deep families include prediction-based recurrent models
(Malhotra et al., 2015), reconstruction-based autoencoders (Sakurada &
Yairi, 2014; Su et al., 2019), and are surveyed by Blázquez-García et
al. (2021) and, across shallow and deep methods, by Ruff et al. (2021).
Directly relevant to our protocol contributions is the
benchmark-transparency line: Wu & Keogh (2022) document that widely
used benchmarks admit trivial or flawed solutions, and the large-scale
evaluation of Schmidl et al. (2022) finds no method family dominant and
simple baselines persistently competitive. We continue this line from
the inside of a submission rather than as external critique: NAB is
used as a public corpus with official anomaly labels — not as a
leaderboard, and no published score is cited for comparison; all
baselines are re-run under the identical harness; per-file threshold
sweeps are shown to inflate every method we tested by 25–59 points and
are demoted to a separability diagnostic; and the multiple-comparison
inflation of OR-fused detector banks is quantified and corrected
(Section 6.4).

### 2.2 One-class learning, novelty detection, and the reject option

Learning from normal data only is the classical novelty-detection
setting: one-class SVMs (Schölkopf et al., 2001), support vector data
description (Tax & Duin, 2004), isolation forests (Liu et al., 2008),
local outlier factors (Breunig et al., 2000), and their deep
counterparts (Ruff et al., 2018). Mixture models in particular have
been used for novelty detection since Bishop (1994) and Roberts &
Tarassenko (1994), and are standard material in the surveys of Markou &
Singh (2003) and Pimentel et al. (2014). We therefore state the
novelty claim precisely: the contribution of this paper is not "a
Gaussian mixture for anomaly detection" but the architecture-level
combination — regime-resolved per-scorer thresholds, strictly causal
streaming operation, three-state output semantics with a first-class
unknown-structure channel, a single frozen configuration across scales,
and a controlled comparison (identical scorers with and without regime
structure) that isolates the effect of the regime layer itself
(+13.47 separability points; native false positives reduced from 2119
to 266 per 10k frames). Our self-run baselines also set the honest
context for this family: at matched label-free operating points a
one-class SVM with the same exclusion hygiene catches more NAB windows
than our combined channel (Section 6.3) — normality hygiene, not
detector choice, is the dominant single factor — while at its standard
frozen configuration the same detector is blind to inter-mode support
valleys (0% on the ghost-state probe of Section 6.5). We evaluate
default-against-default by design, because the unattended deployment
regime of Section 1 is the claim under test; a per-dataset-tuned
bandwidth may well recover the valley, and we say so.

The three-state output connects to a literature older than anomaly
detection: classification with a reject option (Chow, 1970) and, more
recently, open-set recognition (Scheirer et al., 2013; Bendale &
Boult, 2016), which formalize the failure of closed-world classifiers
on classes absent from training. The unknown channel transplants this
concern into streaming condition monitoring — the support boundary of
the described normality, fitted as a likelihood floor on clean data, is
promoted from a safeguard to a detector in its own right (by itself it
catches 85% of NAB's labeled windows at a 0.56% false-positive rate,
Section 6.1). On the calibration side, extreme-value approaches such as
SPOT (Siffer et al., 2017) likewise derive streaming thresholds without
labels; our operating points are percentiles of the detector's own
clean-score distribution, resolved per regime and additionally
calibrated for the multiple-comparison effect of OR fusion.

### 2.3 Multivariate statistical process monitoring and the multimode-GMM lineage

Multivariate monitoring of the Tennessee Eastman process is among the
most cultivated territories in process control. PCA-based squared
prediction error (Jackson & Mudholkar, 1979) and Hotelling's T²
(Hotelling, 1947) are the textbook standard (MacGregor & Kourti, 1995;
Chiang, Russell & Braatz, 2001; Qin, 2003), and the multimode extension
that this work most resembles must be credited by name: Yu & Qin (2008)
monitor multimode processes with finite Gaussian mixture models and a
Bayesian-inference probability index (BIP), with the component count
selected automatically by the Figueiredo–Jain algorithm, validated on
TEP; the lineage continues through Bayesian multimode monitoring (Ge &
Song, 2009), kernelized mixture variants, and later refinements (Jiang
et al., 2016).

We state our relationship to this lineage plainly, because two of our
statistics are its statistics. The joint reconstruction scorer at unit
delay is PCA squared prediction error, and the unknown channel with a
single regime is Hotelling's T² — both verified as identities in our
test suite, not asserted as analogies. It follows by construction that
detection parity with calibrated SPE/T², and with the multimode-GMM
lineage on multimode data, is the expected outcome, and our own
experiments confirm it: in a direct comparison (Section 6.5, with the
implementation disclosure of Section 5.4), FGMM-BIP reaches detection
parity with the unknown channel on the ghost-state probe and on SKAB
alike. The multimode advantage over single-model T²
therefore belongs to the whole lineage, and this paper claims no
detector superiority over it and no false-positive-efficiency advantage
over calibrated MSPC anywhere.

What this work adds sits above the shared statistics, and each item is
measured rather than argued. First, severity gradation: probability-type
indices can saturate at their extremes, and the reconstructed BIP index
does so in our setting — in deep inter-mode valleys its
margin over its own alarm boundary is +0.0 interquartile ranges where
the unnormalized density floor retains ~+30 — Section 7 converts this
into two different protective actions for two valley depths, which a
saturated index structurally cannot emit. Second, output semantics:
MSPC's in-model statistics have no first-class three-state
out-of-support channel; our alarm and unknown channels are demonstrably
non-redundant (96 and 91 of NAB's 107 windows respectively, 103 in
union), which no single fused index expresses. Third, cost: the
diagonal-covariance light path evaluates the same support floor
matrix-free at 468 FLOPs per frame and 1.26 KB of parameters at d = 52,
whereas full-covariance likelihoods and BIP inference share the
O(K·d²) family. Fourth, deployment: the identical frozen configuration
spans univariate NAB to 52-variable TEP with measured operating-point
transfer (Section 6.5), where MSPC practice re-derives control limits
per process. We also disclose the reverse trade: our BIC-based
component selection retrains over a grid of K and is heavier at
training time than Figueiredo–Jain. Finally, on interpretability, MSPC
attributes alarms through contribution plots (Kourti & MacGregor, 1996;
Alcalá & Qin, 2009); the per-scorer, per-regime attribution of Section
4 plays that role for a heterogeneous scorer bank, with the deviation
axis (jump, drift, trajectory, reconstruction) named rather than
recovered from loadings.

### 2.4 Fault detection for autonomous platforms

Onboard fault detection and diagnosis for robots is surveyed by
Khalastchi & Kalech (2018); the classical model-based route (Isermann,
2006) derives residuals from an explicit dynamic model of the platform.
The design constraints of Section 1 are the reasons this work takes the
data-driven route instead: an accurate dynamic model is exactly what an
evolving body and an unattended deployment cannot be assumed to keep,
whereas normal-structure description requires only the platform's own
clean operating data — and its unknown channel reports, rather than
mislabels, the states such a description has never covered. Condition
monitoring and condition-based maintenance provide the industrial
grounding for this normality-centric view (Jardine et al., 2006); this
paper's evaluation stays on that industrial ground (Section 5), and the
robotic setting remains what Section 1 declared it to be — the origin
of the constraints, not an evaluated claim.

## 3. Problem Formulation: Normal-Structure Anomaly Detection

### 3.1 Setting and data hygiene

A sensor stream delivers observations `x_t ∈ R^d` causally; at time `t`
only `x_{≤t}` is available. The system is given a body of *construction
data* assumed to reflect normal operation. In the ideal industrial
setting this is a separate clean operating log per operating condition.
In the public corpora used in this paper, no such separate log exists,
so construction data is obtained by exclusion: anomaly-window
annotations are used only as exclusion masks for constructing
uncontaminated normal structure. They are never used as positive
anomaly examples, anomaly-shape templates, or threshold-selection
targets. This use of labels is data hygiene, not supervision: no
component of the model defined below has access to what an anomaly
looks like.

### 3.2 Normal structure

**Definition 1 (normal structure).** The *normal structure* extracted
from construction data `N` is the tuple

```
S = ( φ,  {R_k}_{k=1..K},  {s_j}_{j=1..J},  {T_{k,j}},  {τ_k},  ℓ_floor )
```

where `φ` is a causal temporal-structural expansion `x_{≤t} → φ_t`;
`{R_k}` is a set of `K` *regimes*, the components of a probabilistic
model of `φ(N)` with density `p(φ)` and log-likelihood
`ℓ(φ) = log p(φ)`; `{s_j}` are `J` causal deviation scorers;
`T_{k,j}` is a robust percentile of the clean scores of scorer `j`
within regime `k`; `τ_k` is a per-regime calibration constant for the
fused score (Definition 3); and `ℓ_floor` is a lower percentile of
`ℓ` on clean data — the *support floor*. Every element of `S` is a
functional of construction data alone.

**Definition 2 (regime).** A *regime* is a normal operating state in
which identical raw sensor values carry different meaning. Formally,
regimes are the mixture components of the density model, and each frame
receives an assignment `r_t = argmax_k P(R_k | φ_t)`. The role of
regimes is semantic, not merely statistical: the same score value
`s_j(φ_t)` is compared against `T_{r_t, j}`, so what counts as
deviation is conditioned on where in normal operating space the system
currently is.

**Definition 3 (deviation).** The *deviation* of frame `t` is the
per-regime thresholded fusion of the scorer bank,

```
D_t = max_j  s_j(φ_{≤t}) / T_{r_t, j}          (raw OR fusion)
D̃_t = D_t / τ_{r_t}                            (calibrated deviation)
```

The max over `J` thresholded ratios is an OR vote, and an OR over `J`
statistics each set to an `α` tail rate flags clean data at up to `J·α`
— a multiple-comparison effect. The constant `τ_{r_t}` is therefore
itself a percentile of `D_t` on clean data within regime `r_t`, which
restores the designed clean flag rate to the fused statistic
(quantified in Section 6.4). `D̃_t` is a ratio, unbounded above, and
monotone in every scorer: it is a severity, not a probability.

### 3.3 The three-state output

The per-frame output is not a binary flag but a state

```
state_t = 2   if  ℓ(φ_t) < ℓ_floor         (outside known normal structure)
          1   elif  D̃_t ≥ 1                (deviation within a known regime)
          0   otherwise                     (normal within a known regime)
```

with the unknown test evaluated first: if the current frame is outside
the support of described normality, its regime assignment and scorer
thresholds are extrapolations, so no in-regime verdict is issued.
State 2 carries the unnormalized margin `ℓ_floor − ℓ(φ_t)` as its
severity; like `D̃_t` it is unbounded and non-saturating. The full
interpretation payload per frame is

```
P_t = ( state_t,  r_t,  D̃_t,  { s_j/T_{r_t,j} }_j,  ℓ(φ_t) − ℓ_floor,  P(R_{r_t}|φ_t) )
```

— state, regime, calibrated severity, per-scorer attribution, support
margin, and assignment confidence. The problem this paper addresses is
the construction of `S` and the delivery of `P_t`, causally and
onboard; any downstream decision logic is a consumer of `P_t`
(Section 7 exhibits one). This also fixes what "AI-ready" means in
this paper, narrowly: the output is the structured causal payload
`P_t`, not a scalar anomaly score, so downstream rule-based or learned
policies receive state, regime, attribution, confidence, and severity
without reconstructing detector internals.

**Remark (classical special cases).** With `K = 1` and a Gaussian
density, the state-2 rule is a Hotelling T² control chart; with a
delay window of one frame, the reconstruction scorer in the bank of
Section 4 is PCA squared prediction error. Both reductions are
verified as identities in Section 6.5 — the formulation contains the
classical statistics rather than competing with them.

### 3.4 Constraints as formal requirements

The four application-class constraints of Section 1 appear in this
formulation as verifiable properties, not as aspirations:

1. **Causality** — `φ`, every `s_j`, and the assignment `r_t` depend
   on `x_{≤t}` only; no element of `S` is revised by future data.
2. **Self-calibration** — every operating point in `S` (`T_{k,j}`,
   `τ_k`, `ℓ_floor`) is a percentile of the detector's own clean-score
   distribution. No externally supplied control limit or bandwidth
   enters; the percentile levels themselves are structural defaults,
   frozen across all experiments in this paper and adjustable if
   desired. There is no per-dataset tuning.
3. **No anomaly-shape learning** — no element of `S` is estimated from
   anomalous examples (Section 3.1); anomalies enter only at evaluation.
4. **Non-saturating severity** — both severities (`D̃_t` and the
   support margin) are unbounded ratios or differences, monotone in
   the underlying scores; no component maps severity through a
   probability-type squashing that saturates beyond the alarm boundary.

Requirements 1–3 restrict how `S` may be built; requirement 4
restricts what may be reported. Section 4 gives the concrete
architecture; Section 5 states the evaluation protocol that keeps the
same discipline at measurement time.

## 4. The Lambda³-NSAD Architecture

This section instantiates the tuple `S` of Definition 1; Figure 1
sketches the pipeline. The
architecture is one system with two input conventions and two
operational modes; nothing in it is specific to any evaluation corpus,
and every constant introduced below is a structural default, frozen
across all experiments in this paper and adjustable if desired.
Corpus-specific matters (which convention applies where, how
construction data is obtained) belong to the protocol and are stated
once, in Section 5.

### 4.1 Input conventions and normalization

The detector consumes a causal stream `events ∈ R^{n×d}`.

- **Multichannel convention.** When the platform exposes `d` physical
  channels (sensor suites, process variables), those channels *are* the
  feature space: `φ` is the identity on the current frame and the
  temporal structure is supplied by the scorers below.
- **Univariate convention.** A single channel is a compressed temporal
  object, not poor data. It is expanded causally into a small
  structural feature space — the raw value, a rolling mean, a rolling
  standard deviation, a second difference, and a rolling lag-1
  autocorrelation — so that level, scale, curvature, and local temporal
  dependence become separately observable axes. This is temporal
  geometry exposure, not feature inflation: five interpretable axes,
  no learned embedding.

Both conventions then pass through the same hygiene step: per-channel
z-normalization with mean and deviation estimated on construction data
only. Without it, channels of large physical scale dominate every
distance computed downstream; with it, all subsequent constants are
scale-free, which is one ingredient of the frozen-configuration claim.

### 4.2 The scorer bank

Six causal scorers watch six structural axes of the normalized stream.
Each obeys the same contract: it is calibrated on construction data,
scores frame `t` from `events[:t+1]` only, and owns a threshold set by
the same robust percentile rule (Section 4.3), so that the ratio
`s_j/T` is dimensionless and comparable across scorers.

Three scorers track scalar trend structure on the channel mean:

- **Jump** — multi-scale standardized increments: at windows
  `w ∈ {5, 20, 50, 200}`, the deviation of the current value from the
  trailing `w`-frame mean in trailing-σ units, each scale normalized by
  its own calibration percentile and the maximum taken. Detects abrupt
  level excursions at any of the four time scales.
- **Gradual** — causal Gaussian-weighted trends at windows
  `{50, 200, 500}`; the score is the sustained magnitude of the trend's
  frame-to-frame gradient. Detects slow directional ramps that never
  produce a single large increment.
- **Structural drift** — the distance of a trailing local mean
  (window 200) from the construction-data baseline. Detects
  displacement of the operating level itself.

Three scorers operate on the full joint space:

- **Reconstruction** — delay embedding of width 20, centered against
  the construction mean, projected onto the top singular subspace
  (rank ≤ 5) of the embedded construction data; the score is the
  residual norm. Detects departure from the low-rank temporal geometry
  that normal operation occupies — *position* outside the normal
  subspace.
- **Trajectory speed** — the standardized step length between
  consecutive delay-embedded vectors. Detects abrupt changes in how
  fast the state moves — *velocity*, the axis orthogonal to
  reconstruction's position.
- **Kernel** — the distance of the current frame to the kernel mean
  embedding of the construction set (polynomial kernel, degree 3).
  Detects deviations visible only through higher-order feature
  interactions.

One design limitation is disclosed here rather than discovered by the
reader: the three scalar-trend scorers collapse multichannel input to
the channel mean by construction, so with `d > 1` the alarm channel is
only partially multivariate, while the reconstruction, trajectory, and
kernel scorers — and the unknown channel below — are fully joint.
Section 6 reports the measured consequence, and multivariate-aware
trend scorers are future work.

### 4.3 Regime layer and per-regime thresholds

Normality is structured by a Gaussian mixture over the normalized
feature space, with full covariance and a deterministic fit. The
component count `K` is selected by BIC over `K ∈ {1, …, 5}`, subject to
a physical constraint: any candidate whose smallest component captures
fewer than 50 construction frames is rejected (a regime that cannot
supply its own threshold statistics is not a regime), with fallback to
`K = 1`. Regime assignment `r_t` is the maximum-posterior component.

Every `(regime, scorer)` pair then receives its own threshold: the
trimmed 99th percentile of the scorer's positive construction scores
within that regime — the top 1% of calibration scores are removed
before the percentile is taken. The trim exists because construction
data is cleaned, not certified: rare residual contamination in a small
regime would otherwise set that regime's threshold. This per-regime
table is what makes deviation regime-conditioned (Definition 2): the
same score is compared against different thresholds in different
operating states.

### 4.4 Fused deviation and its calibration

Per frame, the fused deviation is the OR vote of Definition 3:
`D_t = max_j s_j(t)/T_{r_t,j}`. As Section 3.2 states, an OR over six
~1% tails flags clean data at up to ~6%, so the fused statistic is
calibrated against its own clean distribution: `τ_k` is the same
trimmed percentile applied to `D` on construction frames of regime `k`,
and the reported severity is `D̃_t = D_t/τ_{r_t}`. The per-scorer
thresholds retain their role as cross-scorer scale alignment; `τ_k`
restores the designed clean flag rate to the fusion. The measured
effect of this one constant is reported in Section 6.4.

### 4.5 The unknown channel and state assembly

The support floor `ℓ_floor` is the 0.5th percentile of the mixture
log-likelihood on construction data. At inference, a frame with
`ℓ(φ_t) < ℓ_floor` is outside known normal structure: it is reported as
`state 2` with severity `ℓ_floor − ℓ(φ_t)` (an unbounded difference —
requirement 4), taking priority over the in-regime verdict exactly as
Section 3.3 prescribes. Otherwise `state = 1[D̃_t ≥ 1]`. The channel
costs nothing new: it reuses the mixture already fitted for the regime
layer, evaluated once per frame.

### 4.6 Estimation guardrails and the light path

Two guardrails govern how the floor is estimated when model capacity is
high relative to the construction sample, and both are transferability
design conditions in the sense of Section 6.5 — each is backed by a
measured failure of its absence, on our own method:

1. **Out-of-sample floors.** Percentile floors taken on the same frames
   the density model was fitted to inherit in-sample likelihood bias
   and silently destroy the designed flag rate (measured: a ×32 drift
   at `d = 52`). Floors are therefore estimated on a nested held-out
   slice of construction data, never on the fitting frames.
2. **Dimensionality control.** For `d ≳ 16`, the density model is
   fitted in a PCA subspace retaining 90% variance — a 52-dimensional
   full covariance estimated from a few hundred frames is not a sane
   density, and its floor is not a sane operating point.

For the onboard budget of Section 1, a **light path** evaluates the
same support-floor semantics with diagonal covariance: per frame, `K·d`
squared standardized distances and a log-sum-exp — no matrix products,
no stored covariance factors. At `d = 52` this is 468 floating-point
operations and 1.26 KB of parameters per frame (platform-independent
counts; wall-clock figures in Section 6 are desktop-measured, and
on-device measurement is future work). Section 6.5 reports where the
light path matches the full-covariance floor and where it does not.

### 4.7 Operational modes and the frozen configuration

Two modes share the identical scorer bank:

- **Tier 0 (streaming baseline)** calibrates every scorer on the head
  segment of the stream and OR-votes thereafter, with no regime layer,
  no fusion calibration, and no unknown channel. It exists in this
  paper as the controlled ablation: identical scorers, no structured
  normality.
- **Tier 2 (regime-aware)** is the full system of Sections 4.1–4.6 and
  the source of every headline result.

The complete constant set of the architecture is small enough to print,
and is the same in every experiment of this paper:

| Constant | Value | Role |
|---|---:|---|
| Scorer percentile | 99.0 | per-(regime, scorer) threshold level |
| Trim fraction | 0.01 | contamination robustness of thresholds |
| Fusion calibration | same rule as above | `τ_k` on the fused statistic |
| Unknown floor percentile | 0.5 | support-boundary level |
| `K` range / min regime size | 1–5 / 50 frames | BIC selection constraint |
| Exclusion mask margin | ±50 frames | hygiene dilation (Section 5) |
| Jump / gradual scales | {5, 20, 50, 200} / {50, 200, 500} | scorer time scales |
| Delay width / rank | 20 / ≤ 5 | embedding geometry |
| PCA guardrail | d ≳ 16, 90% variance | density sanity at scale |

These are structural defaults in the sense of Section 3.4: they encode
what jumps, drifts, and regimes *are*, not what any particular dataset
looks like. None was changed for any corpus, dimension, or scale in
this paper; all are adjustable if a deployment desires.

## 5. Evaluation Protocol

The protocol section carries an unusual share of this paper's
contribution, because two of our findings are about evaluation itself.
The rules below were fixed before the results of Section 6 and are
applied to our own method and to every baseline identically.

### 5.1 Corpora and input conventions

Three public corpora and two synthetic probes are used, spanning three
orders of magnitude in dimensionality under the single frozen
configuration of Section 4.7.

- **NAB** (Lavin & Ahmad, 2015): 52 labeled univariate series across
  six categories (plus five unlabeled series retained for corpus-level
  scoring), with official anomaly windows. Univariate convention
  (Section 4.1); the first 15% of each series is probationary, as in
  the benchmark's own convention. We state the framing sentence once
  and abide by it: *we do not present NAB as a leaderboard target, and
  we do not adopt fixed-global-threshold scoring as a design objective;
  NAB is used as a public corpus with official anomaly labels, and
  evaluated at operating points derived without test labels and without
  human threshold tuning.* No published detector score is cited for
  comparison anywhere in this paper.
- **SKAB** (Katser & Kozitsin, 2020): 34 labeled files from a physical
  water-circulation testbed, 8 sensors; multichannel convention.
- **TEP** (Downs & Vogel, 1993; the simulation datasets accompanying
  Chiang, Russell & Braatz, 2001): the Tennessee Eastman process,
  52 variables, 21 faults with a normal-operation training run;
  faults begin at a known sample index; multichannel convention.
- **Synthetic probes**: two controlled-geometry rigs answer mechanism
  questions the public corpora turn out not to pose — a coupling-break
  probe for pure contextual anomalies and a bimodal ghost-state probe
  for inter-mode support geometry (introduced with their experiments,
  Sections 6.5 and 7). Their generators are frozen and published; their
  geometry, never the detector configuration, is what was designed.

### 5.2 The legitimacy rule

Test anomaly labels are used for exactly two things:
(1) **training exclusion** — labeled incident windows, dilated by the
±50-frame margin of Section 4.7, are removed from normal-structure
construction; and (2) **final scoring**. Nothing else. Every threshold,
calibration constant, and score transform is derived from normal
structure alone, per Section 3.4. The canonical statement of Section
3.1 applies verbatim: annotations act only as exclusion masks for
constructing uncontaminated normal structure — never as positive
anomaly examples, anomaly-shape templates, or threshold-selection
targets. In the ideal industrial setting, normal structure would be
built from separate clean operating logs and labels would be needed for
evaluation only; the public corpora mix incidents into their series and
provide no such logs, so exclusion is how clean normality is obtained.
This is data hygiene, not supervision — and Section 6.3 measures how
much of everyone's performance it accounts for.

### 5.3 Three disclosed protocols

Three evaluation protocols follow from the rule, and they answer
different questions; conflating them is precisely the inflation
mechanism quantified in Section 6.4.

| Protocol | Operating point set by | Answers | Status |
|---|---|---|---|
| **P1 Self-calibrated** | the detector itself, from clean data | "what would deployment see?" | ★ headline; fully rule-compliant |
| P2 Per-file sweep | oracle sweep over each file's test labels | "does the score separate, per file?" | diagnostic only; never deployable |
| P3 Corpus single threshold | one global θ across the corpus | "do scores share a scale across files?" | transparency; we reject it as a design target |

P1 reports industrial quantities: **window catch rate** (share of
labeled windows containing at least one flag) and **false-positive
frames per 10k out-of-window frames**, probation excluded. P2 is
retained because within-file separability is a legitimate diagnostic of
score quality, but its numbers are inflated by construction — the
oracle threshold uses test labels — and must never be compared with
official leaderboard figures; Section 6.4 measures the inflation on
every method we run. P3 is the official-style protocol, disclosed for
transparency in two variants: an *anchored* transform (a fixed monotone
map of each method's native decision boundary, usable online) and a
retrospective per-file min-max normalization (which consumes the file's
full score range — future information — and is marked as such).

### 5.4 Baselines and fairness stance

All baselines are self-run under the identical harness, exclusion
hygiene, and metric definitions: one-class SVM (RBF, ν = 0.05),
isolation forest (100 trees), and local outlier factor (k = 20) on the
univariate corpus, each in a streaming mode (head-segment fit) and an
exclusion mode (granted the same clean training data we use); PCA-SPE,
Hotelling T², and their disjunction under the same label-free threshold
family on the multivariate corpora; and a reconstruction of the
FGMM-BIP index of Yu & Qin (2008) — the paper's description admits two
readings, both were implemented, and the stronger is reported. Each
baseline keeps a single frozen configuration, because the unattended
regime of Section 1 is the claim under test: default-against-default is
the fair comparison for that claim, self-calibration opportunities are
granted to baselines wherever the mechanism transfers (clean-quantile
operating points, Section 6.3; the full-accommodation transfer row,
Section 6.5), and findings that depend on a baseline's frozen
configuration are labeled as such where they occur.

### 5.5 Metric discipline

Two rules apply to every table in Section 6. First, operating points
are stated with their provenance (designed rate, realized rate, or
oracle) so that no self-calibrated number sits silently beside an
oracle number. Second, **a false-alarm rate is never reported without
its paired detection figure from the same run**: a detector that flags
nothing transfers its false-alarm rate trivially, so a low realized FAR
is only evidence of a working operating point when the same row shows
the signal survived. Section 6.5 shows a case where this pairing is the
entire distinction between a working transfer and a dead one — the
check was developed against a baseline and then applied to ourselves.

### 5.6 Reproducibility

Every run is deterministic (fixed mixture seed, no stochastic
augmentation); the full constant set is the one table in Section 4.7
and is identical across all experiments; all corpora are public; all
harnesses, baselines, probes, and identity tests ship in the released
implementation, and each results table in Section 6 names the script
that regenerates it.

## 6. Results

This section is organized around four empirical questions. **Q1** —
does the three-state channel detect useful departures from normal
structure? (Section 6.1). **Q2** — what does the regime layer add,
with scorers held fixed? (Section 6.2). **Q3** — how does the method
compare under identical label-free protocols, and what do the
protocols themselves do to the numbers? (Sections 6.3–6.4). **Q4** —
does the operating point transfer across scale, and at what cost?
(Section 6.5; ablations in 6.6). Every table names the released script
that regenerates it. Operating points carry their provenance per
Section 5.5; false-alarm rates are paired with detection from the same
run throughout.

### 6.1 Self-calibrated detection: the three channels

Protocol P1 on NAB, all 52 labeled files, one frozen configuration
(`tests/nab/benchmark_nab_selfcal.py`):

| Channel | Meaning | Catch | FP/10k |
|---|---|---:|---:|
| alarm (state 1) | deviation inside a known regime | 89.7% (96/107) | 247 |
| **unknown (state 2)** | **outside known normal structure** | **85.0% (91/107)** | **56** |
| **combined (state ≠ 0)** | either | **96.3% (103/107)** | 303 |

The middle row is the thesis of Section 3 made empirical. The unknown
channel is not an engineered detector: it is the 0.5th-percentile
support floor of the fitted normal structure, a frozen structural
default, evaluated on the mixture the regime layer already maintains.
By itself it catches 85% of the labeled windows at a 0.56%
false-positive rate — the lowest of any operating point we measured on
this corpus. If an anomaly is a departure from normal structure, the
support boundary of that structure is itself the detector; in-regime
deviation scoring adds catch on top of it (96.3% combined). The two
channels are complementary, not redundant — 96 and 91 windows
respectively, 103 in union — which no single fused index can express.

### 6.2 The effect of regime structure, isolated

Tier 0 and Tier 2 share the identical scorer bank (Section 4.7), so
their difference measures the regime layer alone. At the native
operating point (`D̃ ≥ 1`):

| Variant | Catch | FP/10k |
|---|---:|---:|
| Tier 0 (no regime structure), native | 99.1% (106/107) | 2119 |
| Tier 2, native, uncalibrated fusion | 97.2% (104/107) | 1087 |
| Tier 2 + fusion calibration `τ_k` | 94.4% (101/107) | 266 |
| Tier 2 + calibration + unknown-priority gating (alarm ch.) | 89.7% (96/107) | 247 |

Regime structuring and fusion calibration together cut the native
false-positive rate 8.6-fold (2119 → 247 per 10k) at a cost of nine
windows — and the combined three-state channel recovers to 103/107
(Section 6.1). In within-file separability (protocol P2, diagnostic),
the same substitution moves the corpus weighted mean from 58.55 to
72.02 (+13.47), with gains in every category. Regime structure, not
scorer complexity, accounts for the improvement: the scorers are the
same code in both tiers.

### 6.3 Baselines under the same rule

Protocol P1 with clean-quantile operating points grants every method
the identical self-calibration opportunity (per-file threshold at a
quantile of the score on clean frames;
`tests/nab/benchmark_nab_baselines.py`):

| Method | q=0.999: catch / FP/10k | q=0.9999: catch / FP/10k |
|---|---|---|
| Lambda³ (Tier 2, calibrated) | 59.8% / 15.5 | 39.3% / 4.0 |
| OC-SVM (exclusion) | **78.5% / 16.0** | 67.3% / 7.4 |
| iForest (exclusion) | 67.3% / 11.9 | 50.5% / 2.3 |
| iForest (streaming) | 63.6% / 9.9 | 37.4% / 1.6 |
| LOF (exclusion) | 64.5% / 12.1 | 43.9% / 3.5 |

Read plainly: at matched clean-quantile points, a one-class SVM given
the same exclusion hygiene catches more windows than our calibrated
alarm channel. We report this without qualification. Two further facts
give it its meaning. First, OC-SVM gains +18.7 points of catch from the
exclusion hygiene alone (versus its own streaming mode): the dominant
performance factor on this corpus is normality hygiene, not detector
choice — one-class methods are themselves normal-only learners, and the
family works. Second, under protocol P3 the picture inverts: with the
online-usable anchored transform, our calibrated ratio scores 33.40
while OC-SVM falls to 6.93 and LOF to 0.00, and the baselines recover
only under retrospective per-file min-max normalization (OC-SVM 53.46)
— which consumes the file's full score range and is not available in
deployment (`tests/nab/benchmark_nab_corpus.py`). The calibrated ratio is
the only score in this comparison whose scale means the same thing
across files. Neither method dominates; they win different protocols,
and Section 5.3 is what keeps that statement precise.

### 6.4 The protocol audit

Two evaluation artifacts were large enough to be findings.

**Per-file oracle sweeps.** Moving each method from protocol P3 to
protocol P2 — letting an oracle pick each file's best threshold from
test labels — inflates every method we run by +25 to +59 points
(e.g. OC-SVM exclusion 53.46 → 78.75; ours 33.40 → 72.15). This is why
P2 numbers are labeled a separability diagnostic and are never
comparable to official corpus-threshold leaderboard figures, ours
included.

**OR multiple-comparison inflation.** Six scorers, each thresholded at
its own ~1% tail and OR-voted, stack the family-wise clean flag rate
toward ~6% — the dominant source of the native-point false-positive
flood in the uncalibrated tier (1087/10k). The fix is not to tune
anything down but to measure the normal structure of the fusion
statistic itself (the `τ_k` of Section 4.4): false positives fall
1087 → 266 per 10k at a cost of 2.8 catch points
(`tests/core/test_combined_calibration.py`). Both artifacts were found by
auditing our own pipeline; both corrections are part of the released
configuration.

### 6.5 Generality across scales: the multivariate arm

**Identities and parity, stated first.** The reconstruction scorer at
unit delay reproduces PCA-SPE (correlation > 0.99,
`tests/probes/test_mspc_sanity.py`), and on the single-mode Tennessee Eastman
process BIC selects K = 1, at which the unknown channel *is* Hotelling
T² — the special-case remark of Section 3.3, observed in the wild. At
matched false-alarm rates under the same label-free threshold family,
our variants are at parity with calibrated SPE / T² / SPE∨T² on TEP
(±2 points) and SKAB (edge trades). One earlier internal claim — that
joint detection needs a 6.5× smaller false-positive budget than
per-channel detection — is retracted here: it compared a calibrated
joint statistic against an uncalibrated OR of channels, i.e. exactly
the Section 6.4 artifact. The corrected comparison is parity.

**The unknown channel across scales** (the result that repeats):

| Data | d | Unknown-channel result |
|---|---:|---|
| NAB | 1→5 | 85.0% catch @ 0.56% FP (Section 6.1) |
| SKAB | 8 | 100% (34/34) @ 382 FP/10k — including both windows T² misses (the two files where BIC finds three regimes) |
| TEP | 52 | degenerates exactly to T² (K = 1 selected) |
| Ghost probe | 2 | catches > 80% of a fault that global T² rates *more normal than average* |

The last row is the structural case (`tests/probes/test_regime_ghost_state.py`,
Figure 2): a bimodal process with a fault frozen between the modes. The
global covariance sees a point near the grand mean — its T² is *below*
the calibration median — while the multi-regime support boundary
reports the inter-mode valley as outside normality. T² is the K = 1 special
case of the unknown channel; multimode support geometry is what the
generalization buys.

**Contextual anomalies are rare in these corpora** — a finding, not a
shortfall (`tests/multivariate/contextual_stratify.py`). Under a beyond-chance
tagging rule (marginal band exit above 2× the nominal tail rate or a
≥5-frame run), SKAB has 0 of 34 contextual windows, and TEP faults
reach a sustained marginal band exit within about two samples of onset
(median lead −1). The mechanism exists — on a synthetic coupling break,
the joint residual flags 100% of break frames while per-channel
detection stays at its matched-phase background
(`tests/probes/test_contextual_mechanism.py`) — but public corpora barely pose
the pure-contextual case, which itself matters for how such benchmarks
are read.

**The duel** (`tests/multivariate/exp_support_duel.py`). Against our reconstruction
of the FGMM-BIP index (Section 5.4), detection is at parity: every
GMM-family index catches the ghost fault at 100%, and on SKAB, FGMM-BIP
scores 100% @ 266 FP/10k against the unknown channel's 100% @ 253. The
multimode advantage over single-model T² belongs to the whole lineage.
Two deltas survive. First, severity: BIP's margin beyond its own alarm
boundary on the deep ghost is +0.0 IQR — detection numerically marginal
— against +30.3 for the raw density floor; the probability-type index evaluated here
saturates exactly where grading is needed (Section 7 makes this
operational). Second, the frozen-configuration OC-SVM is valley-blind
(0% ghost detection at matched low-FAR points; SKAB FP floors 337–348
vs 253) — a zero-tuning-regime finding, config-dependent as disclosed
in Section 5.4.

**Cost of the light path** (`tests/multivariate/exp_deployability.py`). Detection
parity first: the diagonal floor matches the full-covariance floor on
the ghost probe (100%) and on reduced-space TEP (55.3% @ 0.81%), and
trades one SKAB window (33/34 @ 176 vs 34/34 @ 253, disclosed). At
d = 52, K = 3, per frame:

| Path | FLOPs | Parameters | Wall-clock* |
|---|---:|---:|---:|
| diag floor (light path) | 468 | 1.26 KB | 325 ns |
| full-covariance floor | 8,580 | 33 KB | 1,122 ns |
| OC-SVM decision function | 18,094 | 35 KB | 10,340 ns |

\* Wall-clock values are x86 desktop measurements only and are not
used as evidence of microcontroller latency; FLOP and parameter counts
are platform-independent, and on-device measurement is future work.
BIP inference shares full covariance's O(K·d²); our BIC-over-K
training is heavier than Figueiredo–Jain's single fit (offline,
disclosed).

**Frozen-configuration transfer** (`tests/multivariate/exp_frozen_transfer.py`,
Figure 4).
Each method fixes its operating point on a fit split of clean data;
we report the realized flag rate on held-out clean frames against the
method's own designed rate, with detection at that same transferred
point (Section 5.5):

| Method (realized FAR / detection) | rig (d=2) | SKAB (d=8) | TEP (d=52) |
|---|---|---|---|
| ours (0.5% floor, designed 0.5%) | 1.06% / 100% | 0.33% / 57.8% | 0.00% / **58.1%** |
| OC-SVM, γ frozen once (designed 5%) | 5.19% / 100% | **21.9%** / 80.6% | **100% (collapse)** / 100%† |
| OC-SVM, γ re-derived per dataset | 5.12% / 100% | 4.60% / 68.0% | **23.5% (×4.7)** / 88.1% |
| OC-SVM + our mechanism (hybrid) | 5.62% / 94.0% | 4.53% / 68.3% | 0.00% / **0.0%** |

† 100% FAR flags everything; its "detection" is vacuous.

The mechanism is the one stated in Section 4.1: a percentile of the
detector's own clean-score distribution means "flag x% of clean"
regardless of dimension or scale, whereas a bandwidth enters as
exp(−γ‖x−y‖²), which grows with both — γ frozen at d = 2 saturates the
kernel at d = 52 and everything becomes "far" (the load-bearing row).
The ×4.7 drift of the *re-derived* bandwidth is auxiliary evidence
only: at d = 52 with ~300 training frames it is confounded with the
small-sample regime, and we say so first. The hybrid row grants OC-SVM
our entire operating-point mechanism: it rescues the frozen bandwidth's
FAR at d = 8 (21.9% → 4.5%) — the percentile mechanism transfers
threshold semantics for *any* score — but at d = 52 the FAR "transfers"
(0.00%) over a score the bandwidth has already killed (detection 0.0%).
Threshold semantics and score validity are independent failure axes,
and no operating-point mechanism rescues a dead score.

**The two 0.00%s.** Our own d = 52 realized FAR is the same number that
kills the hybrid row, so the Section 5.5 pairing rule applies to us: at
that transferred point our detection is 58.1% of fault frames — same
run, same table. A silent detector transfers FAR trivially; a valid one
transfers FAR and signal together.

**Self-catch, disclosed.** The first run of this test drifted *our*
realized rate ×32 at d = 52 — an in-sample floor over an overfit
52-dimensional density, the third occurrence of in-sample percentile
bias in this project. The Section 4.6 guardrails are load-bearing, and
we generalize them as transferability design conditions: (i)
out-of-sample threshold estimation (its absence broke us, ×32), (ii)
dimensionality control of the density estimate (52-D full covariance
from ~300 frames), (iii) a score whose validity survives the transfer
(the frozen bandwidth fails here, decomposed by the hybrid row). Each
condition carries a measured counterexample. Scope, finally: this is a
deployability result about bandwidth-style and fixed-control-limit
operating points; it is not an advantage over the multimode-GMM
lineage, whose automatic order selection is equally self-adapting on
this axis, and a per-dataset-tuned OC-SVM still out-catches us at
matched points (Section 6.3).

### 6.6 Ablations and self-tests

**Threshold and order selection.** The released configuration (BIC over
K with the minimum-regime-size constraint; trimmed 99th-percentile
thresholds) was selected on development iterations of the univariate
corpus and then frozen; no per-corpus revisiting occurred. The trim
matters where construction data retains rare contamination in small
regimes; BIC-with-constraint matters because unconstrained likelihood
happily buys degenerate micro-regimes.

**Subtractive discipline.** A seventh scorer (FFT-based periodicity)
was implemented, measured at a net −1.10 points on the category where
it should have helped, and disabled; it ships in the codebase, off.

**Covariance ablation (a falsified hypothesis).** We pre-registered the
hypothesis that full covariance is what detects correlation-breaking
faults, with a kill condition. It died by that condition: on the
coupling-break probe, diagonal covariance detects 0% at K = 1 but 100%
at K ≥ 2 — one extra axis-aligned component substitutes for the
correlation structure (`tests/probes/test_h2_covariance.py`). What matters is
support geometry, not covariance parametrization; this is also why the
diagonal light path of Section 6.5 can match the full floor. We report
the falsification rather than the hypothesis because the corrected
attribution is the useful engineering fact.

## 7. Failure Analysis and the Worked Downstream Consumer

This section reads the system's outputs the way a consumer would — its
failures first, then a demonstration that the interpretation payload of
Section 3.3 is sufficient, by itself, to drive graded action.

### 7.1 Failure as structural feedback

Per-file separability on the univariate corpus is sharply bimodal
(Figure 5): files where clean construction data covers the operating
regimes reach 95+ separability with near-zero false positives (Mode A),
and files where the covered-normal-structure assumption is violated
fall to approximately zero (Mode B). We report the causes as a taxonomy
because they are structural and predictable, not stochastic:

| Type | Structural cause | Corpus example |
|---|---|---|
| B1 | missing normal regime — an operating state (e.g. seasonal) absent from construction data | ambient temperature series |
| B2 | scale distortion — six orders of magnitude crush the z-normalized geometry | disk-write-bytes series |
| B3 | drift beyond regime time scales | long social-media series |
| B4 | sparse windows in very long series — an evaluation-format mismatch, not a detection failure | 15k+ frame files |

Each type names the violated assumption, which is what makes the
taxonomy actionable: B1 calls for construction data spanning the
missing state, B2 for scale-aware preprocessing, B3 for a slower
structural layer (future work), B4 for episode-level scoring. The
three-state output changes what Mode B looks like in operation: frames
outside described normality surface on the unknown channel rather than
producing silent zeros — the 85% catch of Section 6.1 includes exactly
such files — so the failure of the normality description is itself
reported, per frame, in-band. What remains honestly weak is *in-regime*
detection on Mode B files: the unknown channel says "outside my
description", not "here is the anomaly type". For the unattended
setting of Section 1, this is the designed division of labor: an
explicit report of departure from described normality is the input a
protective policy can act on; a silent zero is not.

### 7.2 From payload to graded action: a worked consumer

The claim "AI-ready interpretation layer" owes the reader a consumer.
We provide the smallest honest one: a rule-based policy, roughly thirty
lines (`tests/probes/test_downstream_policy.py`), deliberately containing no
learning and no detector machinery of its own — if the policy is
trivial, whatever it achieves is attributable to the payload it
consumes. The policy sees only Section 3.3's `P_t`: the state channel,
per-scorer attribution, and the unnormalized support margin with its
own trajectory.

**Rig.** A two-channel bimodal process (commanded load switching
between two plateaus, temperature relaxing toward a load-dependent
setpoint, plus slow ambient wander), with four embedded events of
distinct ground-truth character: **E1**, a four-frame in-support
temperature transient; **E2**, a slow leak ramping the temperature out
of the support over ~90 frames; **E3**, the process stuck *between* the
two modes at a shallow valley position; **E4**, stuck at the valley
center — the ghost geometry of Section 6.5. Per Section 5.1, the rig's
geometry is the experimental design; the detector configuration is the
frozen one throughout.

**Policy.** Actions are assigned per episode (contiguous non-normal
run, ≤3-frame gaps bridged) — the unit a real consumer acts on. The
rules, in full: if the episode contains unknown-state frames, escalate
to *stop & escalate* when the smoothed support margin exceeds a depth
of 10 calibration-IQRs; otherwise read *how* the process left the
support from the margin's own onset slope — below 1 IQR/frame is
gradual egress (wear or leak: *schedule maintenance*), above it abrupt
(*reduce & investigate*). Episodes of in-regime deviation only are
routed by dominant-scorer attribution: majority slow-scorer episodes to
*schedule maintenance*, fast ones to *transient check*. The two
constants are structural defaults in the Section 4.7 sense — a depth
that separates "outside" from "deep inside the forbidden region", a
slope that separates creep from step — not values fitted to the rig.

**Result.** All four events receive their intended distinct actions,
and the policy is quiet on ≥97% of normal frames (Figure 3):

| Event | Ground truth | Payload signature | Action |
|---|---|---|---|
| E1 | in-support transient | state 1, fast-scorer attribution | transient check |
| E2 | slow leak | state 2, onset 0.65 IQR/frame | schedule maintenance |
| E3 | shallow ghost | state 2, abrupt onset (3.4–8.2 IQR/frame), depth ≈ 5 IQR | reduce & investigate |
| E4 | deep ghost | state 2, abrupt onset, depth ≈ 42 IQR | **stop & escalate** |

Three payload properties do the work, and each maps to a Section 1
requirement. The state channel plus attribution separates E1's
transient from E2's wear pattern (interpretability of the deviation
axis). The margin *trajectory* separates E2 from E3 — gradual versus
abrupt egress, read off the payload with no additional detector. And
the margin's *depth* separates E3 from E4 — the graded-response
requirement made concrete.

**The saturation contrast, made operational.** On the same run, the
FGMM-BIP index (Section 5.4) saturates on both ghosts: median > 0.99 on
each, separated by less than 0.02 — while the unnormalized margins
differ by more than a factor of three and straddle the 10-IQR default
from opposite sides. The consequence is not a score-quality nuance but
a policy-level impossibility: any policy driven by the saturated index
must give E3 and E4 the same action, and this is asserted, not argued —
the test suite verifies that the BIP-driven variant of the same policy
collapses the two actions while the margin-driven one separates them.
Both indices detect both ghosts; detection was never the question. A
severity that cannot grade cannot prioritize, and prioritization is
what the graded ladder of Section 1 requires.

### 7.3 What the demonstration does and does not show

It shows that the payload of Section 3.3 carries enough information —
state, attribution, margin, and margin trajectory — for a trivial
consumer to emit four correctly ranked protective actions on events of
four distinct characters, and that one of those distinctions is
structurally unavailable to the probability-saturating index we
evaluate. It does not
show a validated protective system: the rig is synthetic, the events
are four, the policy constants — though structural — have two of them,
and no closed-loop consequence (did stopping help?) is evaluated.
Closed-loop evaluation on physical platforms is future work
(Section 9), and the division of labor stands as designed: this paper's
subject is the observation layer; the consumer exists to prove the
interface carries what a policy needs.

## 8. Discussion

### 8.1 What the interpretation layer buys

The results support reading the framework not as a detector with
extras but as a front-end that converts raw streams into a
representation downstream logic can act on. In deployment terms, the
three channels have distinct operational readings, and Section 6
prices each. The unknown channel is the low-false-positive notify
channel (56/10k on the univariate corpus): it reports departure from
described normality, it needed no engineered detector, and its
operating point survives scale changes at design rate (Section 6.5).
The alarm channel is a monitoring signal (247/10k at the fully
self-calibrated point) — usable for attention direction and trend
review, and we state plainly that at that rate it is not a hard-stop
automation signal on its own. The combined channel is the coverage
reading (96.3% at 303/10k). A deployer who needs different rates moves
the two percentile levels of Section 4.7 — the semantics ("flag x% of
clean") move with them, which is what the transfer result licenses.

The same results discipline how the layer should be *compared*. On
detection, the honest summary of Sections 6.3 and 6.5 is: the
normality-based family works, a tuned one-class boundary out-catches
us at matched points on the univariate corpus, and the multimode-GMM
lineage reaches parity on everything we measured. The layer's case
rests on what sits above detection — the payload (Section 7.2), the
operating-point semantics (Section 6.5), the cost floor
(Section 6.5), and the protocol findings (Section 6.4) — and we
believe that is the correct division for an engineering-applications
venue: the statistics are classical; the architecture, calibration
discipline, and output semantics are where the engineering lives.

### 8.2 Severity-preserving protective signaling

The Section 1 definition of self-preservation was deliberately
restricted — onboard self-diagnosis, no agentic reading. Within that
restriction, one biological analogy earns its keep because it names a
measured design decision, and we confine it to this paragraph: a
protective signaling layer benefits from what nociception provides in
organisms — an interpretable cue that grades with severity and
distinguishes recognized stress from unrecognized state. The two
detection channels implement exactly this division — deviation within a
known regime is a recognized stress in a recognized operating state,
while support egress is a state the system has never inhabited — and
empirically the two are complementary, not redundant (96 and 91 of 107
windows, 103 in union; the unknown channel at the lowest false-positive
rate measured). The non-saturating severity requirement is where the
analogy becomes load-bearing: graded protective response — de-rate,
investigate, stop — needs a signal that keeps discriminating beyond the
alarm boundary, and Sections 6.5 and 7.2 measured precisely this
saturation in the index we evaluate (+0.0 IQR of margin
on a deep out-of-support fault) while the unnormalized margin retains
the gradation (~+30 IQR) that the four-action policy consumed. We
record the order of events honestly: the non-saturating margin was a
design choice, but its articulation as a protective-signaling rationale
followed the saturation measurements rather than preceding them. The
framing earned its place by evidence; we did not retrofit the
architecture to a philosophy.

### 8.3 Limitations

Six limitations bound the claims. (1) Mode B files: where normal
structure is unrepresented (B1–B3), in-regime detection remains weak;
the unknown channel reports the situation but does not diagnose it.
(2) The alarm channel's 2.5% native false-positive rate is a
monitoring-grade, not automation-grade, operating point. (3) At
matched clean-quantile operating points our catch does not beat a
tuned one-class baseline (Section 6.3); the contribution is the
interpretation layer, not raw catch. (4) The wall-clock figures are
desktop-measured; the microcontroller-class claim rests on
platform-independent FLOP and memory counts, and on-device
measurement is outstanding. (5) The frozen-transfer contrast's
auxiliary evidence (re-derived bandwidth, ×4.7) is confounded with
small-sample effects, as stated in Section 6.5; only the structural
collapse row is load-bearing. (6) No robot is measured in this paper:
the autonomous-platform setting motivated the constraints
(Section 1), and closing that loop is the first item below.

## 9. Future Work

Four lines of work follow directly from the paper's own gaps, in the
order the manuscript created them. First, physical-platform
validation: actuator-level streams (motor current, gearbox vibration,
joint temperature, torque) under the same frozen configuration, with
the light path measured on-device rather than arithmetically — the
Section 1 constraints were derived from this setting, and the
evidence should return to it. Second, closed-loop evaluation of the
protective policy: Section 7 shows the payload suffices for graded
action; whether acting on it improves outcomes (avoided damage,
reduced downtime) is a controlled-intervention question the
observation layer alone cannot answer. Third, the structural gaps
named by the failure taxonomy and the architecture's own disclosures:
a slower structural layer for B3 drift, episode-level scoring for B4,
multivariate-aware trend scorers for the Section 4.2 channel-mean
limitation, and multi-channel fault-mode attribution (which sensor
group left normality, not only that one did). Fourth, multimode
process corpora: the K = 1 degeneration on the single-mode Tennessee
Eastman process means the multimode unknown channel has been exercised
at scale only on the 8-sensor testbed and the synthetic probes;
public multimode process data would test the regime layer where it is
supposed to matter most.

## 10. Conclusion

We reframed anomaly detection as normal-structure interpretation:
instead of learning how systems fail, the framework makes normal
operating structure explicit — regimes, per-regime thresholds, and the
support boundary of the described normality — and reports, per frame
and causally, whether the system is inside that structure, deviating
within it and how, or outside it entirely. On public corpora from one
to fifty-two dimensions under a single frozen configuration, the
support boundary alone detected 85% of labeled anomaly windows at a
0.56% false-positive rate on the univariate corpus; the operating
point held its designed meaning across a 26-fold dimension change with
detection retained, where a frozen kernel bandwidth collapsed; and a
thirty-line policy converted the interpretation payload into four
correctly graded protective actions, one of which is structurally
unavailable to the probability-saturating severity index we evaluated. The classical
statistics of process monitoring are contained as special cases and
their lineage reaches detection parity with us wherever we measured;
the contribution is the layer above: three-state semantics,
self-calibrated transferable operating points at
microcontroller-class arithmetic cost, and an evaluation protocol
honest enough to be reused. For autonomous and embedded systems, this
is the observation half of self-preservation as Section 1 defined it —
knowing, onboard and per frame, whether the platform is inside its
described normal envelope, how far outside it has gone, and how fast
it left. The protective half — acting on that observation in closed
loop, on physical platforms — is the work this paper sets up.
