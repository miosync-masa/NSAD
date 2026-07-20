# Lambda³-NSAD — Manuscript Draft (v2, engineering pivot)

Target venue: **Mechanical Systems and Signal Processing (MSSP)**;
submission main field: **[A] Signal processing in machine/system
health monitoring**. Fallbacks: EAAI, Reliability Engineering & System
Safety. Working title (primary candidate, see abstract.md §1):

> Share the Geometry, Commission the Individual: Separating Healthy
> Individuality from Damage Severity in Normal-Structure Machine
> Condition Monitoring

Status: **complete v2 draft — §1 through §8 plus Appendices A–E;
internal review (v2.1) incorporated**: mechanism claims bounded to
their tested conditions (§2.7-1/5/6), the commissioning algebra
written in likelihood space (§2.4, §6.2), geometry transfer separated
from cross-domain principle replication (§4.5, §8), the H3L causal
attribution bounded to the complete fleet-transfer mechanism (§5.4,
§6.2), the bit-identical severity audit scoped (§4.4), and statistical
inference units fixed (§4.1) with a post-hoc recording-level
cluster-bootstrap audit (Appendix A.11 — all three H1 adjacent-pair
orderings survive). Final consistency sweep (v2.2) applied: abstract
subject, deficit/vocabulary/observability wording, §6.2 scope, and
Appendix C formal alignment. **Pre-registration #6 executed and
integrated (v2.3)**: the dilemma and the commissioning remedy are
formulation-level (no feasible shared boundary under PCA-SPE,
Hotelling T², or calibrated combined MSPC; E3 recovers FAR under all
of them), and the severity ladder is bounded to the likelihood
deficit (registered kill K3) — §4.6.
This draft supersedes the v1 manuscript (EAAI-framed, NAB/SKAB/TEP-
centered; preserved verbatim in git history). Per the migration plan
in [paper_v2_outline.md](paper_v2_outline.md), the v1 evidence
material is folded in below as Appendices A–D with numbers and tables
unchanged; v1's introduction, robotics motivation, and discussion
framing are not carried (superseded by the pivot). Every number in
§3–§5 is a pre-registered value quoted from the executed plans
([claim_evidence_map.md](claim_evidence_map.md) is the audit trail;
the machine-readable snapshot `paper_results/` reproduces all of them,
manifest verification 16/16). Citations appear as (Author, Year)
placeholders; the bibliography is assembled at submission time.

Figures (generated: `python -m tests.figures.export_paper_results` →
`python -m tests.figures.make_paper_v2_figures`; appendix set:
`python -m tests.figures.make_figures`):

| Manuscript figure | File (doc/figures/) | Section |
|---|---|---|
| Figure 1 | v2_fig1_severity_ladder | §4.2 |
| Figure 2 | v2_fig2_dilemma | §4.3 |
| Figure 3 | v2_fig5_hydraulic | §4.5 |
| Figure 4 | v2_fig3_ims_longitudinal | §5.4 |
| Figure 5 | v2_fig4_deployment | §6.1 |
| Figure C1 (pipeline) | fig1_pipeline | Appendix C |
| Figure B1 (ghost state) | fig2_ghost_support | Appendix B |
| Figure B2 (frozen transfer) | fig4_frozen_transfer | Appendix B |
| Figure D1 (worked consumer) | fig3_policy_margin | Appendix D |
| Figure D2 (Mode A/B) | fig5_mode_ab | Appendix D |

Writing rules in force for this manuscript (binding):

- Language: "no per-dataset tuning — structural defaults, adjustable
  if desired"; never "parameter-free", never bare "tuning-free".
- Labels: never "no anomaly labels" — "no anomaly-shape learning";
  anomaly annotations are exclusion masks (data hygiene, not
  supervision); operating-condition and component-condition labels
  are operational metadata.
- **Pairing rule (§2.7)**: every results subsection in §4–§5 opens
  with a one-sentence back-reference to its §2.7 mechanism, and every
  results figure caption pairs the measurement with its one-line why.
- FAR is never reported without detection from the same run.
- Six registered plans, all executed, freeze SHA preceding results
  SHA; the collective is "six registered experiments, including one
  explicitly disclosed confirmatory validation" — #5 always carries
  that disclosure, and #6's GMM cells always carry the
  replication-anchor disclosure (its prospective content is the
  PCA-SPE / T² / combined-MSPC / FGMM-BIP results).
- No RUL prediction, no fault-localization claim, no detection-
  accuracy comparison against supervised fault classifiers (different
  question; §1.2), no detector-superiority claim over calibrated MSPC
  or the multimode-GMM lineage (Appendix B).
- The three central sentences (§6.3) are fixed wording.

---

## Abstract

Conventional pooled one-class monitoring — a single shared normal
support with a single alarm score — collapses two different sources
of deviation in machine condition monitoring into one outlier
score: normal variation between healthy individuals of identical
specification, and change caused by physical damage. A narrow
normal support then raises false alarms on unseen healthy units,
while a widened support absorbs shallow damage. We address the
resulting deployment question — how to admit healthy individuality
without losing damage severity or degradation progression — through
six registered experiments, including one explicitly disclosed
confirmatory validation following exploration, on physical machine
corpora, under one frozen detector configuration, with
implementations committed before results were read. First, on the Paderborn corpus, the
physical extent of real accelerated-lifetime damage was
order-preserved on a shared severity margin across bearing
individuals (12/12 ordered condition-pairs, zero reversals,
Spearman ρ +0.85/+0.87). Second, widening the shared support to
cover unseen healthy units failed by pre-registered criteria: false
alarms barely improved while up to 41% of shallowest-damage frames
were absorbed. Third, two scalars per unit — the median and
interquartile range of its own clean likelihood, estimated from
about 64 seconds of healthy commissioning — restored the designed
false-alarm rate on unseen healthy bearings (0.10%) while leaving
the separately reported shared-severity output unchanged by
construction. Fourth, on NASA IMS run-to-failure data, margins
referenced to each unit's own early life were statistically
progressive on all three failed bearings (alarm-occupancy
ρ ≥ +0.90, lead times 74–148 h, persistence 93.5–99.6%), whereas
reusing the fleet commissioning calibration as the failure alarm
was 11–14% of life late, or silent. Fifth, a registered
confirmatory validation replicated the graded-severity ordering
principle on a second machine class — a cyclic hydraulic rig
(cooler and valve margins ordered with confidence intervals on all
registered splits; the leak target failed its registered detection
criterion and is reported as such). Sixth, the dilemma and its
commissioning remedy proved formulation-level rather than
detector-level: under PCA squared prediction error, Hotelling T², and
a calibrated combined MSPC statistic on the same registered folds, no
shared clean-tail boundary reconciled unseen-healthy admission with
shallow-damage retention (at a 2% false-alarm ceiling the cheapest
absorption of shallowest damage was 76–78% under those three
statistics; under the likelihood deficit itself the ceiling was
unreachable), while the same two-scalar commissioning recovered the
designed rate under every score family (0.10–0.34%, at each family's
unchanged damage detection) — and only the
likelihood deficit carried the physical extent ladder, a registered
kill we report against our own thesis. The resulting deployment
principle — share the severity geometry, commission the individual,
and monitor degradation against its own history — separates
transferable damage severity from asset-specific alarm calibration.
Generic benchmarks (NAB, SKAB, Tennessee Eastman) are retained as
breadth checks in the appendix; fault localization is explicitly
out of scope.

## 1. Introduction

### 1.1 The conflation problem

Conventional pooled one-class monitoring — a single shared normal
support with a single alarm score — is trained on normal operating
data and alarms on departure from it. In fleet deployment this
formulation meets a fact it does not represent: **healthy individuals
of identical specification differ**. Same-type bearings differ in
run-in history, manufacturing tolerance, mounting, lubrication and
surface state; their vibration signatures differ accordingly, and
none of that difference is damage. The pooled outlier score collapses
this between-individual variation and damage-induced change into one
number, and the deployment consequence is a dilemma that, in this
paper's tested formulation, could not be escaped by support widening
alone. Keep the normal support narrow — one unit's data, or a small
pool — and unseen healthy units false-alarm: on the Paderborn corpus,
a support constructed from four healthy bearings flags **42%** of two
unseen healthy bearings' frames (mean over rotating folds, §4.3), two
orders of magnitude above the designed 0.5% rate. Widen the support to
absorb the healthy population, and shallow damage goes with it: under
the widened-support candidates of §4.3, the fraction of
shallowest-extent real-damage frames absorbed into the healthy
envelope rises from 11.9% to as much as **41.1%**, detection drops,
and one severity-ordering pair is lost. Both horns of the dilemma are
*measured* in this paper, under pre-registered criteria, not argued —
and the dilemma is not an artifact of our density model: a registered
feasibility audit under PCA squared prediction error, Hotelling T²,
and a calibrated combined MSPC statistic, on the same folds, found no
shared clean-tail boundary achieving both unseen-healthy admission
and shallow-damage retention for any score family (§4.6). The
negative claim remains bounded: none of the tested shared-support
widening strategies resolved it (§4.3, §4.6); we do not claim that no
hierarchical or individual-effect normality model could.

The question this paper answers:

> How can a deployable alarm design handle distinct-but-same-spec
> healthy individuals without losing physical damage severity and
> longitudinal degradation progression?

### 1.2 Position in the landscape

This work sits beside, not against, the established signal-processing
tradition of bearing diagnostics. Envelope analysis and the
fault-frequency tradition (Randall & Antoni, 2011; Antoni, 2006),
spectral kurtosis and kurtogram-based band selection (Antoni, 2007),
and cyclostationary analysis (Antoni, 2009) encode *fault-specific
physics* — defect frequencies, resonance bands, cyclic modulation — a
priori, and are the right tools when the fault class is known and the
question is its signature. Deep-learning PHM answers a related
supervised question: convolutional and recurrent fault classifiers
trained and evaluated on CWRU and Paderborn data (Lessmeier et al.,
2016; Zhang et al., 2020), and transfer-learning variants that adapt
classifiers across operating conditions or machines, learn *which
known fault* a signal shows from labeled fault examples. Bayesian
degradation modeling (the Gebraeel et al., 2005 lineage) fits
stochastic wear processes for prognosis.

Because the Paderborn corpus is a standard supervised-diagnosis
benchmark, we state the differentiation first, in our own voice:
**supervised fault classifiers answer "which known fault is this?"
from labeled fault examples; this paper answers a different question —
"how do we separate normal individuality from damage, and grade the
damage, without ever learning a fault shape?"** The methods consume
different information (fault labels versus healthy data only) and
produce different outputs (a class posterior versus a severity margin
plus a calibrated alarm). No detection-accuracy comparison against
fault classifiers is claimed or owed, in either direction. Envelope
analysis is the complementary contrast on the signal side: it builds
fault physics into the representation, where our feature vocabulary
deliberately does not — §2.7 mechanism 2 states what that choice
pays (mild valve stages, the accumulator observability limit) and
what it buys (fault-agnostic vocabularies governed by one
qualification law across fault types, components, and machine
classes, with no fault-frequency input to maintain).

Three further literatures ground specific components and are engaged
where they act. One-class novelty detection (Schölkopf et al., 2001;
Tax & Duin, 2004; mixture models since Bishop, 1994) is the ancestry
of the normal-structure core; the support-widening failure of §4.3 is
a measured boundary of that family's naive fleet extension.
Multivariate statistical process control and its multimode-GMM
lineage (Yu & Qin, 2008) share two of our statistics — the detector
contains PCA-SPE and Hotelling T² as identity-tested special cases —
and Appendix B carries the full head-on account, including detection
parity, which we do not contest. Pre-registration #6 engages that
lineage experimentally rather than by citation: it re-runs the
fleet-transfer question under PCA-SPE, T², and their calibrated
combination on a shared protocol, and measures the support-widening
dilemma and its commissioning remedy on those statistics directly
(§4.6) — a shared structural limit and a shared remedy, not a
superiority claim. Benchmark-transparency work in
time-series anomaly detection (Wu & Keogh, 2022; Schmidl et al.,
2022) motivated the evaluation discipline of Appendix A. Condition
monitoring practice (Jardine et al., 2006; Randall, 2011) supplies
the deployment vocabulary — commissioning, admission, per-asset
baselines — that §6 turns into a measured principle.

### 1.3 The answer, previewed

Six registered experiments (hypotheses and kill conditions fixed
before execution; implementations frozen in commits before results
were read; freeze SHA precedes results SHA in the repository history;
#5 is an explicitly disclosed confirmatory validation following
exploration, and #6's GMM cells are disclosed replication anchors)
decompose the dilemma into three layers with different owners:

- **Shared across the fleet**: the fault-agnostic feature vocabulary,
  the structural geometry, and the **severity margin** — a common
  ruler that reads physical damage depth. On Paderborn's real
  accelerated-lifetime damage it order-preserves physical extent
  across bearing individuals (12/12 ordered condition-pairs, zero
  reversals, Spearman ρ +0.845/+0.866; §4.2). Separately, a
  registered confirmatory validation replicated the ordering
  *principle* — the same margin construction, not the same fitted
  geometry — on a second machine class, a cyclic hydraulic rig with
  graded degradation labels (§4.5).
- **Calibrated per individual at commissioning**: the **alarm
  origin**. Two scalars — the median and IQR of the unit's own clean
  score, estimated from ~64 s of healthy operation — restore the
  designed false-alarm rate on unseen healthy bearings (0.10%) while
  leaving the severity side bit-identical (§4.4) — and the mechanism
  is model-invariant: the same transform recovers the designed rate
  under PCA-SPE, Hotelling T², and combined MSPC scores alike
  (0.16–0.34%, §4.6). This is healthy admission calibration, and it
  is role-bounded: never the failure alarm.
- **Referenced to the individual's own history in service**: the
  **failure alarm**. On NASA IMS run-to-failure data, margins built
  from each unit's own early life are statistically progressive on
  all three failed bearings, with 74–148 h of lead at 93.5–99.6%
  persistence (§5.2–5.3) — whereas the fleet commissioning
  calibration reused as the failure alarm is 11–14% of life late, or
  silent (§5.4). Cross-sectional calibration success does not imply
  longitudinal detection validity.

In one sentence: **share the geometry, commission the individual, and
monitor degradation against its own history.**

### 1.4 Contributions

**Methodological (signal & statistics)** — each item carries its §2.7
mechanism, stated mathematically or physically, not only measured:

1. A normal-structure monitoring framework that separates the
   *transferable severity geometry* from *asset-specific calibration*
   and the *asset's longitudinal reference* — deciding which parts of
   learned normality are fleet property and which are individual
   property, a question the generic one-class formulation does not
   pose.
2. The severity margin and the alarm decision designed as **distinct
   statistical objects**: an unbounded, unsquashed log-likelihood
   deficit on a
   shared geometry (ordinal, cross-unit comparable, non-saturating)
   versus a FAR-controlled decision variable (individual). Every
   pre-registered failure in this paper is a measurement of what
   happens when one object is forced to do the other's job.
3. The location–scale algebra of commissioning, written once and read
   twice (§6.2): the same affine transform that aligns healthy
   quantiles across units — fixing admission FAR — necessarily
   divides the fault's likelihood displacement by the unit's healthy
   scale, a mechanism consistent with the late-or-silent failure
   alarm; the registered experiment measures the failure of the
   complete fleet-transfer mechanism and does not isolate the scale
   term from reference-geometry mismatch.
4. A registered evaluation discipline: six registered plans with
   kill conditions, FAR always paired with detection, failures
   retained as load-bearing results, and a machine-readable results
   snapshot whose key statistics are verified against the registered
   numbers.

**Engineering (measured on physical corpora)**:

1. Cross-sectional order preservation of real damage extent across
   bearing individuals: 12/12 ordered condition-pairs, zero
   reversals, ρ +0.845/+0.866 (§4.2).
2. Recovery of unseen-healthy-individual FAR by two-scalar
   commissioning: 0.10% from ~64 s, below the designed 0.5% rate, at
   bit-identical severity (§4.4).
3. Run-to-failure lead of 74–148 h at 93.5–99.6% persistence with
   statistically progressive margins on all three primary IMS failed
   bearings, from each unit's own early life (§5.2–5.3).
4. Measured delay/silence of fleet-style healthy calibration reused
   as a failure alarm: +11–14% of life, or silent (§5.4) — a negative
   result that, to our knowledge, is rarely measured at all.
5. Cross-domain replication of the graded-severity ordering principle
   on a cyclic hydraulic rig, with its failures reported: the leak
   target killed by its registered detection criterion, the
   accumulator consistent with an observability limit at this
   granularity (§4.5).
6. A semantic separation of detection and localization grounded in
   the same-shaft control finding (§5.5).
7. Formulation-level invariance of the dilemma and its remedy,
   measured (#6, §4.6): no shared clean-tail boundary is feasible
   under GMM-deficit, PCA-SPE, Hotelling T², or calibrated combined
   MSPC scores, while two-scalar commissioning recovers designed FAR
   under all of them — and, reported against our own thesis, the
   physical extent ladder survived only on the likelihood deficit
   (registered kill K3).

### 1.5 Scope

The claims are bounded as plainly as they are made. This paper claims
**anomaly detection** — has the machine system departed from its
normal structure — and does **not** claim fault localization: §5.5
shows same-shaft control bearings alarming on a neighbor's failure,
because a vibration sensor observes the mechanical system (shaft,
housing, load path), not only the component beneath it. Attributing
the departure to a source is a separate spatial-inference task, named
as future work. No remaining-useful-life prediction appears anywhere
(a registered directive). Pre-registration #5 is a **registered
confirmatory validation** — the exploration preceded it, disclosed in
the plan itself and wherever #5 is cited (§4.5). The generic
benchmarks (NAB, SKAB, TEP) are retained as breadth checks:
*generic benchmark results are retained as breadth checks; the
primary evidence comes from cross-sectional physical-damage
validation and longitudinal run-to-failure evaluation* (§3,
Appendices A–B).

The remainder of the paper: §2 the method and the six signal-level
mechanisms; §3 the breadth checks, briefly; §4 cross-sectional
validation (Paderborn #1–#3, hydraulic #5); §5 longitudinal
validation (IMS #4); §6 the deployment principle and the mechanistic
closure of its central boundary; §7 limitations; §8 conclusion.
Appendix A: evaluation protocol and univariate-corpus results.
Appendix B: the multivariate arm and MSPC head-on account. Appendix
C: architecture detail and formal definitions. Appendix D: the worked
downstream consumer and failure taxonomy. Appendix E: the
pre-registration documents.

## 2. Method

The detector core is the released normal-structure implementation,
frozen throughout: no constant, threshold, or feature was changed for
any experiment in this paper. This section gives the layers in
deployment order and then the signal-level rationale (§2.7); formal
definitions, the scorer bank, and the complete frozen-constant table
are in Appendix C.

### 2.1 Fault-agnostic structural adapter

Raw sensor streams enter through a modality-aware, fault-independent
feature vocabulary — the *adapter*. The qualification law, fixed
before the first pre-registration: **nothing in an adapter may be
aligned to a fault frequency, a component identity, or any
damage-specific structure.** The vibration vocabulary used on
Paderborn and IMS is, per channel: log RMS; 12 log-spaced band
energies from 20 Hz to 0.8 × Nyquist; spectral entropy; and 6 generic
envelope band energies (|Hilbert| spectrum, 5–1000 Hz, log-spaced) —
expressed sample-rate-independently, so the identical construction
serves 64 kHz (Paderborn, d = 27 with current and slow channels) and
20.48 kHz (IMS, d = 20 per channel). The cyclic-machinery vocabulary
used on the hydraulic rig adds a normalized-phase magnitude profile
(12 bin means) and a generic timing vocabulary (peak/trough position,
rise/settle time) per sensor — carrying the within-cycle information
that magnitude spectra provably discard (§2.7, mechanism 2). No
envelope band targets a bearing defect frequency; no timing feature
knows which component it watches.

### 2.2 Shared severity geometry and the support margin

Normality is described, not learned against faults: construction data
(healthy operation only) is z-normalized, reduced by PCA retaining
90% variance when d > 16 (a density-sanity guardrail), and modeled by
a Gaussian mixture with BIC-selected component count. The *support
floor* is the 0.5th percentile of the mixture log-likelihood on a
**nested out-of-sample** slice of construction data — never on the
fitting frames (Appendix B measures the ×32 drift when this rule is
violated). The **severity margin** of a frame x is

```
m(x) = ( ℓ_floor − ℓ(x) ) / IQR_clean
```

— the log-likelihood deficit below the clean support floor, in units
of the clean distribution's interquartile range. m(x) > 0 means
outside described normality; the magnitude is an unbounded,
unsquashed, cross-unit-comparable severity reading, not a probability
and not a metric distance — the conditions under which it carries
ordinal severity are stated and tested per §2.7, mechanism 1.

### 2.3 Role separation: severity margin vs alarm decision

The margin plays two roles in naive deployments, and this paper's
central design choice is to refuse the overload. The
**severity_margin** is the ordinal damage-depth ruler: computed on
the *shared* geometry, common scale across units and operating
conditions, read for ordering, grading, and trend. The **alarm
decision** is a FAR-controlled binary: its operating point belongs to
the individual asset. Every pre-registered failure in §4–§5 is a
measurement of what happens when one object does the other's job —
support widening moves the severity geometry to fix an alarm problem
(§4.3); fleet calibration reuses an admission alarm as a failure
alarm (§5.4).

### 2.4 Commissioning calibration (healthy admission)

A new unit i is admitted by estimating two scalars from a short
healthy commissioning window: the location b̂ᵢ (median) and scale ŝᵢ
(IQR) of *its own* clean log-likelihood ℓ(x) under the shared
geometry. The calibration acts entirely in likelihood space — the E3
mechanism, exactly as implemented:

```
zᵢ(x)      = ( ℓ(x) − b̂ᵢ ) / ŝᵢ          standardize by the unit's own
                                          clean location and scale
ℓᵢ→ref(x)  = b_ref + s_ref · zᵢ(x)        map onto the reference scale
aᵢ(x)      = ( ℓ_floor − ℓᵢ→ref(x) ) / s_ref     commissioned alarm score
```

where b_ref and s_ref are the median and IQR of the reference clean
log-likelihood (the floor-estimation slice of §2.2). The commissioned
alarm score aᵢ is a **different statistical object from the shared
severity margin** m(x) = (ℓ_floor − ℓ(x))/IQR_clean of §2.2: the
affine map is applied only inside aᵢ, and m is never transformed —
which is why §4.4's registered audit finds the severity side
bit-identical *by construction*. The mechanism is role-bounded by
§5.4's registered kill: healthy admission calibration, never the
failure alarm. §6.2 reads this one transform twice.

### 2.5 Per-asset longitudinal reference

In service, the failure alarm is referenced to the unit's own
accumulated normal history. On run-to-failure data the registered
construction is the unit's first 20% of life (model part 60%, floor
part the later 40%, out-of-sample in time); the registered readouts
are: **sustained onset** — the first snapshot index from which ≥3
consecutive snapshots have median frame margin > 0; **lead time** —
time from sustained onset to end of test; **alarm occupancy** — the
fraction of frames with margin > 0 per life quintile;
**distributional deepening** — bootstrap CIs on
end-of-life-versus-healthy and Q5-versus-Q1 median differences;
**persistence** — the fraction of post-onset snapshots with positive
median margin. Raw-margin regressions (self-healing, debris
migration, lubrication changes) are expected physical behavior;
progression is claimed statistically, not pointwise (a pre-registered
amendment logged before execution).

### 2.6 Detector core

The three-state output semantics (normal-in-regime /
deviation-in-regime / outside known normal structure), the six causal
scorers, per-regime robust thresholds, OR-fusion calibration, and the
single frozen configuration are inherited unchanged from the released
implementation and are specified in Appendix C, including the
complete constant table. All six pre-registrations run the identical
support-floor path (#6 additionally scores registered comparator
statistics on the same shared geometry, fitted once per fold);
production defaults were changed by none of them.

### 2.7 Signal-level rationale — six mechanisms, and the pairing rule

This venue's review standard asks *why* a result holds, next to the
result. This subsection states the six mechanisms once; the **pairing
rule** then binds the rest of the paper: every results subsection in
§4–§5 opens with a one-sentence back-reference to its mechanism, and
every results figure caption pairs the measurement with its one-line
why. The map is fixed here:

| Mechanism | Consumed by |
|---|---|
| 1 margin–severity ordinality (empirical condition) | §4.2, §4.5, §5.2, §4.6 |
| 2 fault-agnostic vocabulary | §4.2, §4.5 |
| 3 location–scale algebra | §4.4, §5.4, §6.2, §4.6 |
| 4 cross-sectional vs longitudinal objects | §4.3, §4.6, §5.4, §6.2 |
| 5 system-level observability (propagation) | §5.5 |
| 6 observability limit | §4.5 |

**Mechanism 1 — why the margin *can* preserve severity, and when.**
The margin is an *unsquashed likelihood deficit*, not a metric
distance: log-likelihood differences satisfy no triangle inequality,
and for a multimodal density (a GMM among them) ℓ(x) is not monotone
in displacement — moving away from one mode toward another can raise
it, and a physical degradation path may bend or re-approach the
fitted support in feature space. What the construction guarantees is
narrower and is what ordinal severity actually needs: no
probability-type squashing is applied, so the deficit never saturates
beyond the alarm boundary and remains free to keep discriminating.
Along a degradation path γ(s), ordinal severity is retained when the
feature map resolves the relevant physical degree of freedom and the
fitted log-likelihood decreases over the observed range,

```
d/ds ℓ( φ(γ(s)) ) < 0 .
```

Whether this condition holds is empirical, and §4–§5 test it on
physical damage and run-to-failure trajectories: it held on the
Paderborn extent ladders at group level (12/12, §4.2), on the
hydraulic cooler and valve stages (§4.5), and statistically along the
IMS degradations (§5.2) — and the same sections report where it did
not (the identity-noise floor, the leak kill, the accumulator).
Non-saturation is the design property; monotonicity over the observed
trajectories is the measured result, not an assumption. **And #6
sharpens the boundary with a registered kill reported against our own
thesis (§4.6): non-saturation is necessary but not sufficient.**
Under the identical protocol, unsquashed residual and Mahalanobis
scores (SPE, T², their calibrated combination) failed to carry the
extent ladder (4/8 inner pairs ordered; extent-2 margins exceeding
extent-3), while the full-density likelihood deficit carried it
completely (8/8 + 4/4) — severity geometry, as measured on this
corpus, is a property of the likelihood deficit on the fitted
support, not of unsquashed scores in general. The probability-type
converse also lands on physical data: BIP saturates at raw median
1.0000 at every damage extent (§4.6; Appendix B's ghost-probe
contrast, reproduced on real damage).

**Mechanism 2 — why the vocabulary is fault-agnostic, and what that
costs.** Log-spaced band energies, spectral entropy, and generic
envelope bands span the spectral axes on which mechanical damage
expresses, without encoding whose damage: no defect frequency enters,
so the same vocabulary serves inner-race pitting, roller wear, cooler
degradation, and faults nobody enumerated. The cyclic timing
vocabulary carries a mechanism proof: the magnitude spectrum |FFT| is
*exactly invariant* under circular shift, so a valve switching lag —
a circular shift within the machine cycle — is invisible to every
magnitude feature, while normalized-phase timing features move
monotonically with the lag (unit-tested:
`tests/core/test_cycle_phase.py`). The cost is stated with the
choice: fault-specific representations (envelope analysis at defect
frequencies) will out-resolve a generic vocabulary on their target
fault, and faults whose physical degree of freedom the generic
features do not span remain unobservable (mechanism 6). The purchase
is fault-agnostic vocabularies governed by one qualification law
across fault types, components, and machine classes, maintained
without fault-frequency engineering.

**Mechanism 3 — what location–scale calibration changes, and what it
cannot.** The E3 transform zᵢ(x) = (ℓ(x) − b̂ᵢ)/ŝᵢ (§2.4) is affine
in the unit's clean log-likelihood. An affine map relocates and
rescales the *decision variable* aᵢ; it cannot re-shape the geometry
that produced ℓ, so severity ordering, computed on the shared
geometry, is untouched by construction (§4.4's audit: bit-identical).
The same algebra bounds the mechanism: dividing by the unit's healthy
scale ŝᵢ necessarily divides any likelihood displacement Δℓ — a
fault's included — by the same factor. A unit whose healthy
likelihood is naturally dispersed (large ŝᵢ) gets a well-calibrated
healthy phase and a fault signal compressed by exactly the factor
that calibrated it: a mechanism *consistent with* delayed or missed
onset. §5.4 measures the failure of the complete fleet-transfer
mechanism (which this compression is one part of); §6.2 states
precisely what is derived and what is measured.

**Mechanism 4 — cross-sectional and longitudinal are different
statistical objects.** Admission FAR is a *population-quantile
alignment* problem: make the healthy quantiles of unit i land on the
design rate under the fleet reference. Failure alarming is a
*within-asset temporal displacement* problem: detect when unit i's
present departs from unit i's own past. The first is solved by
aligning distributions across units at one time; the second requires
a reference along time within one unit. No amount of success at the
first implies the second — and the pair (#3 supported, #4 H3L killed)
is the measured proof (§4.4, §5.4).

**Mechanism 5 — why single-sensor detection cannot claim
localization.** A vibration transducer measures the response of the
assembled mechanical system: excitation at one bearing propagates
through shaft, housing, and load path to every mount. Departure from
normal structure is therefore a *system-level* observable, and a
single-sensor detector is epistemically entitled to claim only it.
Attributing the departure to a component requires spatial inversion —
arrival order, amplitude ratios, phase relationships across sensors —
which this detector does not perform. §5.5's control-bearing onsets
are *consistent with* this propagation mechanism (alternative
system-level explanations such as common load drift are not
excluded); what they demonstrate regardless of cause is the
identifiability boundary itself: the present measurements do not
identify the source component.

**Mechanism 6 — the observability limit, defined.** Let P₀ and P₁ be
the distributions of the raw signal under normal operation and under
a fault mode, and φ_g the feature map at granularity g. If the
pushforward distributions coincide,

```
P₀ ∘ φ_g⁻¹ = P₁ ∘ φ_g⁻¹ ,
```

no detector operating only on φ_g can distinguish the fault from
normal operation — the direction that is information-theoretically
exact. The converse is qualified, not claimed as an equivalence:
sufficiently separated pushforward distributions make detection
*possible*, subject to finite-sample estimation and thresholding.
Fault information can be destroyed at the representation — averaged
out by cycle summaries, cancelled in magnitude spectra (mechanism 2's
circular-shift case), below sensor resolution. The accumulator target
of §4.5 is the operational demonstration: invariant detection ≈ 20%
and flat margins across every registered granularity, behavior
consistent with a representation-level limit, not a detector failure.
The honest fix is a feature vocabulary whose pushforward separates
the fault, never a threshold.

## 3. Generic qualification (breadth checks)

Before the engineering validations, the identical frozen
configuration was qualified on three public benchmarks. We state the
framing sentence once and abide by it: *we do not present these as
leaderboard targets; generic benchmark results are retained as
breadth checks; the primary evidence comes from cross-sectional
physical-damage validation and longitudinal run-to-failure
evaluation.*

| Corpus | Role | Result (label-free operating points) |
|---|---|---|
| NAB, 52 labeled univariate series | generic time-series qualification | support-boundary channel alone 85.0% of labeled windows @ 0.56% FP; combined three-state 96.3% @ 303/10k |
| SKAB, 8-sensor water-circulation testbed | multivariate anomaly qualification | 100% (34/34) @ 382 FP/10k |
| TEP, 52-variable process | process/regime qualification | BIC selects K = 1, at which the support floor *is* Hotelling T² |

One identity is worth a sentence in the main text because it speaks
this venue's language: the detector *contains* the classical
statistics — its reconstruction scorer at unit delay is PCA squared
prediction error and its support floor at K = 1 is Hotelling's T²,
both verified as identities, not analogies — so detection parity with
calibrated MSPC is the design working as intended, and no superiority
over that lineage is claimed anywhere. Protocols, baselines
(including where they win), the protocol-inflation audit, and the
full multivariate arm are Appendices A and B.

## 4. Cross-sectional engineering validation (Paderborn #1–#3, hydraulic #5)

### 4.1 Corpus and ground truth

The Paderborn KAt corpus (Lessmeier et al., 2016) provides what the
severity question needs: **real damage of known physical extent on
distinct physical bearings of one specification**. Six healthy
bearings (K001–K006; run-in 1–19 h except K001 > 50 h); real
accelerated-lifetime damage with fact-sheet extents — inner-ring
fatigue pitting spanning extents 1→2→3 (KI04/KI14/KI17/KI21 → KI18 →
KI16), outer-ring extents 1→2 (KA04/KA22 → KA16), plus indentation,
combined-damage, and twelve artificially damaged bearings; four
operating conditions per bearing (speed, torque, radial force
varied); 20 recordings × 4 s each per setting. Under the d = 27
adapter: 32 bearings, **40,944 frames** (3 non-finite frames dropped,
1 malformed recording skipped — both logged). All experiments are
pre-registered: plan #1 (severity, regimes, cross-bearing FAR), #2
(support-widening candidates vs commissioning), #3 (alarm-side
calibration ladder). Splits are by recording, healthy holdout by
bearing (rotating folds); damage labels are used only for final
scoring.

**Statistical inference units (binding for every result in §4–§5).**
So that no interval is read beyond its support, the independence and
generalization unit of each result family is fixed here:

| Result family | Independence / generalization unit |
|---|---|
| Paderborn severity (§4.2) | the **bearing** is the individual unit — inner ladder: 6 bearings, outer ladder: 3 bearings; the four prespecified operating conditions are repeated measurements within bearing |
| Paderborn FAR (§4.3–§4.4) | the **held-out bearing** is the generalization unit (rotating folds over 6 healthy bearings); frame-level FARs are conditional estimates within each held-out bearing |
| IMS (§5) | a **case series of 3 primary failed bearings** (plus one descriptive test); no population effect size is implied |
| Hydraulic (§4.5) | a **single rig**; the five registered seeds measure split robustness, not five independent rigs |

The registered bootstrap CIs resample **frames**. Frames within a
recording are not independent replicates, so those intervals are
conditional on the observed bearings and recordings: they quantify
estimation noise of the group medians under the fitted model, not
bearing-population variability. A post-hoc recording-level
cluster-bootstrap sensitivity audit — not pre-registered, and kept
separate from every registered number — is reported in Appendix A.11.

### 4.2 Shared severity geometry (#1 H1)

*Tested per mechanisms 1–2: an unsquashed likelihood deficit over a
fault-agnostic vocabulary can retain ordinal separation when the
represented damage trajectory moves progressively away from the
fitted healthy distribution — whether it does, across individuals and
above the identity-noise floor, is exactly what this registered test
measures.* The registered test: on the real-pitting ladders, per
operating condition, adjacent extents ordered with bootstrap 95% CIs
on median differences; kill if any adjacent pair reverses with CI
excluding zero in ≥2 of 4 conditions.

**Result — supported, 12 of 12.** All condition × adjacent-pair tests
ordered (inner 8/8, outer 4/4), **zero reversals**; pooled Spearman
ρ(extent, per-bearing median margin) = **+0.845** (inner; six
bearings) / **+0.866** (outer; three bearings, four prespecified
operating conditions — reported with its n, not as a population
estimate); adjacent-group CIs exclude zero
([+8.4, +9.3] and [+1.9, +2.8] IQR inner; [+12.8, +16.7] outer). The
combined-damage bearing of extent 3 (KB24) shows the deepest margin
of all (+92.7). Figure 1 shows both ladders with every bearing
labeled.

The identity-noise floor is disclosed with the claim: extent-1
per-bearing medians span −0.2 (KI14) to +17.2 (KI04) — individual
bearings overlap across extent labels, and the ladder stands on group
medians, not on every individual. The scope is registered wording:
this is a cross-sectional, same-spec, cross-bearing severity
validation, not a longitudinal degradation track (§5 supplies that
axis). Two registered negatives from the same plan are reported here
rather than hidden. H2 (operating conditions recoverable as mixture
regimes at multi-bearing scale) was **killed on purity** — 62.5%
against a 70% kill bar — with its confound disclosed: purity was
measured on frames of which 66% lay outside the fitted support, where
regime assignment is extrapolation by the formulation's own logic
(Appendix C.3). And the same plan's H3 anticipated §4.3: the flat
pooled support does not transfer its designed FAR to unseen healthy
bearings.

*Figure 1 caption (fixed): Median severity margin versus fact-sheet
damage extent, inner and outer real-pitting ladders. Dots:
per-bearing medians; line: per-extent group median; shaded band:
range of the six healthy bearings' per-bearing medians under the same
primary model. This is a group-level ordering result, not an
individual-stage classifier (KI14 lies inside the healthy band).
Measured: 12/12 ordered pairs, ρ +0.845 (six inner bearings) /
+0.866 (three outer bearings), zero reversals. Why tested: an
unsquashed likelihood deficit can retain ordinal separation when the
represented damage trajectory moves progressively away from the
fitted healthy distribution (§2.7-1/2); whether it does, above the
identity-noise floor, is the registered measurement.*

### 4.3 Support expansion fails (#1 H3, #2 A–D)

*Expected from mechanism 4: unseen-healthy FAR is a
population-quantile alignment problem; thickening the shared support
attacks it by moving the severity geometry instead, so any FAR gained
must be paid in absorbed shallow damage.* The registered candidates:
A, the flat pooled floor (control); B, component-conditional floors;
C, known-condition conditional floors; D, a hierarchical
between-bearing population envelope. Kill conditions included: FAR
improvement purchased with severity ordering, or majority absorption
of extent-1 damage.

**Result — all four killed.** The flat support flags 42.06% of
unseen-healthy frames (fold FARs 66.37/0.00/59.80%; construction-size
curve 99.96 → 98.63 → 66.37% for 1→2→4 bearings — monotone, nowhere
near design). The widened candidates barely move the mean FAR
(42.9–46.9% vs 43.1%) while extent-1 absorption rises from 11.9% to
**41.1%** (B), 22.4% (C), 35.5% (D), detection over all damaged
frames falls from 81.5% to as low as 63.5%, and B loses an inner
ordering pair (7/8). Every number sits in Figure 2 with its
FAR–absorption pairing; the kill conditions did exactly the job they
were registered for. What was rejected is registered wording: the
flat pooled-support *implementation* and its widened variants — not
population normality in principle; the healthy population's
between-bearing tolerance layer is real and unrepresented, and
absorbing it into support thickness is the wrong representation.

*Figure 2 caption (fixed): Unseen-healthy FAR (log) versus
extent-1-damage absorption. A is the flat-support control; B–D are
the widening candidates (all killed); E/E3 are the commissioning
family (alarm-side only). Measured: A–D cluster at 42–47% FAR with
absorption up to 41.1%; E/E3 move FAR to 14.1% → 0.10%. Note: the
E/E3 vertical coordinates denote the unchanged shared-severity output
(bit-identical by construction); commissioned damage-phase alarm
performance was not evaluated in this cross-sectional corpus. Why:
widening attacks a quantile-alignment problem by deforming the
severity geometry (§2.7-4), while an affine alarm-side transform
cannot touch the geometry at all (§2.7-3).*

### 4.4 Two-scalar commissioning (#2 E → #3 E3)

*Expected from mechanism 3: if healthy individuality is a
location–scale difference in the unit's clean likelihood rather than
a different damage geometry, an affine alarm-side correction should
recover the designed FAR — and provably cannot alter severity.* Plan
#2's candidate E (one scalar, the unit's median offset, from 4
healthy recordings) moved unseen-healthy FAR 43.1% → 14.1% at zero
severity cost and was registered INCONCLUSIVE-positive (it missed its
< 2% pass bar). Plan #3 fixed the hypothesis space for the residual:
offset model, condition dependence, dispersion, sample size — each a
registered candidate on the alarm side only, with the severity audit
as a standing disqualifier.

**Result — the model, not the sample size, was binding; location +
scale closes the gap.** The registered E1 ladder is flat: one scalar
per unit gives 15.33% FAR at 1 commissioning recording and 14.75% at
12 — the registered diagnostic fired, sample size was never the
constraint. E2 (condition-resolved offsets with shrinkage) barely
helps (13.77/12.43%): the mechanism is not condition dependence of
the center. **E3 — standardizing each unit's likelihood by its own
commissioning median and IQR — reaches 0.10% mean unseen-healthy FAR
at n = 4 recordings per condition (~64 s of healthy operation
total), below the 2% pass bar and below the designed 0.5% rate
itself**; E4 (a conservative bootstrap tail) is supported at larger
windows (0.13% at n = 8). The severity audit passes exactly: H1
12/12 (inner 8/8 ρ +0.85, outer 4/4 ρ +0.87), detection 81.5%,
severity-side extent-1 absorption 11.9% — **bit-identical** to the
shared-geometry reference, as mechanism 3 requires by construction,
now verified rather than assumed. Stated precisely: commissioning
restored unseen-healthy admission FAR while leaving the *separately
reported* shared-severity output bit-identical by construction — an
architecture audit, not a sensitivity result. The cross-sectional
experiment did not, and could not, test the damage-phase alarm of a
commissioned damaged unit: damaged bearings in this corpus have no
healthy commissioning window (§5.4 and §7 take up exactly that
question).

The role bound is stated in the same breath as the win: this is
healthy commissioning — admission calibration for a new unit's alarm
origin. Plan #3 registered its own open flank ("a loose per-unit
scale estimated at commissioning could compress later damage margins
on the alarm side"), and plan #4 was registered to attack it. §5.4
reports the outcome; §6.2 derives it.

### 4.5 Cross-domain graded severity (hydraulic rig, #5)

*Expected from mechanisms 1, 2, and 6: on a second machine class, the
margin can order graded physical degradation for every target whose
degree of freedom the fault-agnostic vocabulary spans — and should
fail, informatively, where it does not; whether it does is the
empirical condition of mechanism 1, tested here.* The scope of the
claim is fixed before the results: Paderborn (§4.2) demonstrated
**geometry transfer** — one shared fitted geometry preserving
group-level ordering across same-spec bearing individuals. This
section demonstrates something categorically different: the same
*margin construction* (a different adapter, a different fitted model,
a single rig, target-conditional normal sets) reproducing graded
ordering on another machine class — **a cross-domain replication of
the ordering principle, not transfer of a common fitted geometry**,
and margin values are not comparable across domains (Paderborn's
ladders live at tens of IQR; the cooler's at thousands). Disclosure
second, registered in the plan itself: #5 is a **registered
confirmatory validation, not a blind pre-registration** — a
post-freeze exploration preceded it; the registered-novel elements
are one fixed vocabulary for all targets (no per-target feature
selection), five fresh split seeds, ordering statistics with
bootstrap CIs, and pass/kill rules. The rig: UCI 447 (ZeMA; Helwig et al., 2015), 2205
constant 60-s load cycles, 17 sensors, four components varied on a
grid — cooler efficiency 100/20/3%, valve switching 100/90/80/73%,
pump leakage 0/1/2, accumulator pre-charge 130–90 bar. Normality is
target-conditional (only 10 of 2205 cycles are all-nominal): the
other components vary freely *inside* the normal set — operating
conditions the regime layer must absorb.

**Results (Figure 3).** **H1H cooler — supported 5/5**: detection
100% at both degradation stages on every seed; median margins ordered
med(3%) > med(20%) > 0 with adjacent CIs excluding zero on every
seed; ρ +0.49…+0.87. Disclosed with it (a registered reporting duty):
held-out healthy FAR reaches design on 1 of 5 seeds only
(0.51/1.02/2.04/5.61/1.02%; the worst seed coincides with a BIC
collapse to K = 1) — healthy FAR at design from a single split is not
automatic, the same honest gap §5.3 meets on IMS. **H2H valve —
supported, and the registered open question answered**: the margin
orders all three stages on every seed (ρ +0.890…+0.925, severe-mild
CIs excluding zero) *while individual alarm detection at the mild
stages remains low* (0.6–2.8%, one seed's 80%-stage exception at
79.7%) — the ordering is read from label-based group comparison, not
from per-cycle alarms, and it is the severity/alarm role separation
of §2.3 reproduced on timing geometry: below-floor group medians
retained ordinal stage information. **H3H
leak — KILLED by its registered kill condition**: severe-stage
detection < 50% on 3 of 5 seeds (25.2/45.6/27.1%); the preceding
exploration's single-split 82/91% did not survive registered splits —
precisely the fragility the five-seed protocol existed to expose. Its
ordering statistics largely held (ordered + CI on 4/5 seeds; ρ > 0 on
5/5, weakly), and the registered coverage measurement confirmed the
FAR-drift finding (healthy FAR 1.02–3.06%, 2–6× design). **H4H
accumulator — the registered observability-limit expectation held
5/5**: detection 16–27% with flat, sub-floor margins at every stage
on every seed and ρ ≈ 0 — behavior consistent with a
representation-level observability limit at this sensor set and cycle
granularity (mechanism 6): invariant across every registered
granularity, rescued by none of them.

*Figure 3 caption (fixed): Per-stage margin distributions across the
five registered splits, cooler (magnitude profile; symlog vertical
axis) and valve (cycle-phase/timing geometry). Dot: split median;
bar: p25–p75; detection annotated as the mean over the five splits.
Measured: cooler 100%/100% detection with CI-separated ordered
margins; valve margins ordered on every split (ρ +0.89…+0.93) —
below-floor group medians retained ordinal stage information via
label-based group comparison, while individual alarm detection at
mild stages remained low. Why tested: an unsquashed likelihood
deficit can retain ordinal separation where the vocabulary spans the
fault's degree of freedom (§2.7-1/2); ordering without detection is
the severity/alarm role separation, and the absent targets mark the
representation's span, not the detector's threshold (§2.7-6).*

### 4.6 Density-model invariance (#6)

*Expected from mechanisms 1, 3, and 4: if the support-widening
dilemma (§4.3) and its commissioning remedy (§4.4) are properties of
the pooled one-class formulation, they must survive replacing the
likelihood with the one-class statistics MSPC practice would reach
for; if they are artifacts of the GMM floor, a residual or
Mahalanobis boundary should escape them.* Pre-registration #6 re-ran
the #2 protocol — same folds, frame sets, thresholds-from-nested-slice
rule, and candidates — under five score families on one shared PCA
geometry per fold: M1, the likelihood deficit (the #2 anchor); M2,
PCA-SPE computed from the residual of the standardized d = 27 vector;
M3, Hotelling T² in the retained-score space; M4, FGMM-BIP (the A.4
probability-type comparator, run as a contrast, outside the
hypothesis pass-set); M5, calibrated combined MSPC,
max(T²/τ_T², SPE/τ_SPE) recalibrated on the same nested slice.
Disclosed in the registration and repeated here: M1 and E3-on-M1 are
replication anchors already measured in #2/#3 — they also gate run
validity, and the gate passed at exact fold-level flagged-frame
integer counts against #2 (1408/2048, 0/2048, 1240/2048); the
prospective content is M2/M3/M5 and M4-on-physical-damage. All #6
cell statistics are fold means (the registered basis); §4.3's figures
are primary-fold, and the corresponding legacy values replicate
(extent-1 absorption 11.9%, candidate-B 41.1%). M2/M3/M5 under this
shared protocol are shared-protocol expressions of MSPC statistics,
not optimised MSPC practice (§7); their underperformance is never
claimed as an advantage.

**The dilemma is formulation-level (H1c supported 4/4; the registered
kill K1 stays silent).** The primary judgment swept the entire
clean-tail quantile axis per model — the threshold read per fold at
each quantile q from that fold's nested clean slice, FAR and extent-1
absorption fold-averaged, both monotone in q as checked — and asked
whether *any* shared boundary achieves fold-mean FAR < 2% with
fold-mean absorption < 50%. **None exists, for any of M1, M2, M3, or
M5** (nor, descriptively, M4). At the FAR < 2% ceiling, minimum
absorption is 76.0% (M2), 77.8% (M3), 77.2% (M5), and the ceiling is
unreachable for M1/M4; holding absorption < 50% forces FAR to
8.4–24.4%. The families differ only in which horn they occupy: M3's
native designed-tail boundary posts 0.21% FAR — paired, per the
standing rule, with 23.3% detection over damaged frames and 87.2%
extent-1 absorption. The T² boundary admits unseen healthy units by
being nearly blind to shallow damage; it sits on the *other horn* of
the dilemma, not outside it. Two registered sub-criteria fell by
their letter and are reported: the descriptive ≥ 10×-design native
FAR (H1a) replicates on M1 (43.10%) and M2 (5.21%) but not M3/M5
(0.21/3.39%), and the adaptation criterion (H1b) is met by M2-D and
M5-C only in the degenerate sense of sub-10% FAR bought at > 60%
absorption against controls already absorbing > 60%. Single folds
occasionally admit a feasible point; the fold mean — the registered
basis — never does.

**The remedy is formulation-level (H2 supported 4/4).** Two
commissioning scalars per unseen unit — median and IQR of *that
model's own clean score* over the same four recordings — restore
designed unseen-healthy admission under every family: 0.10% (M1),
0.16% (M2), 0.33% (M3), 0.34% (M5), and 0.00% for M4 descriptively —
each paired with its family's unchanged damage detection (fold-mean
det_all 53.7 / 44.7 / 23.3 / 39.9 / 53.7% over damaged frames: the
transform moves the alarm origin, not the damage-side response) and
at bit-identical shared severity, asserted in-run. The density
model is an interchangeable component of the three-layer role
separation (§6): the remedy is a property of the formulation, not of
the likelihood.

**The severity ladder is not (H3's first half killed; the registered
kill K3 fires, reported against our own thesis).** Only the
likelihood deficit satisfies the registered unsquashed-ladder
condition: strictly increasing extent medians spanning 11.1 clean-IQR
with per-condition ordering 8/8 + 4/4 (ρ +0.85/+0.87). M2 and M5
break the extent ladder (extent 2 > extent 3: +21.8 vs +11.9 and
+13.5 vs +6.7 IQR), M3 compresses it into a 2.8-IQR band
(−1.2/+1.6/+1.2), and per-condition inner ordering falls to 4/8 for
all three. M4 completes the contrast in its starkest form: BIP
saturates at raw median 1.0000 at every damage extent — on real
physical damage the probability-type index detects (77–100%) but
cannot grade at all. Per the registered kill wording: severity
geometry is a property of the likelihood deficit on the fitted
support, not of unsquashed scores in general, and §2.7-1 is bounded
accordingly. A stronger result for the method, a weaker one for the
thesis — which is exactly why it was registered as a kill.

The claim ledger moves accordingly: the conflation claim (§1.1) and
the role separation (§2.3–2.5) are stated at formulation level with
#6 as license; mechanism 1 is bounded to the likelihood deficit; and
the comparison with established statistics is discharged as a
measured shared structural limit plus a shared remedy, with no
superiority claim anywhere (Appendix B's parity stance stands).

## 5. Longitudinal engineering validation (NASA IMS #4)

### 5.1 Corpus and registered protocol

The IMS run-to-failure corpus (IMS Center, University of Cincinnati;
NASA Prognostics Data Repository) supplies the axis Paderborn cannot:
**the same physical bearings degrading to failure over weeks**. Four
bearings per shaft at constant 2000 rpm; 1-s vibration snapshots
every ~10 min. Test 1 (2156 snapshots, 828 h): failures at bearing 3
(inner race) and bearing 4 (roller). Test 2 (984 snapshots, 164 h):
failure at bearing 1 (outer race). Test 3 is registered
descriptive-only (labeling less certain; 6324 snapshots). The
registered protocol (plan #4, amended before execution to statistical
rather than pointwise progressiveness): per-asset mode — each
bearing's model from its own first 20% of life; healthy-phase
evaluation window 20–50%; end-of-life the final 5%; the §2.5 readouts
verbatim; the milling dataset as a registered descriptive arm. The
registered directive: this is not an RUL study, and no RUL estimate
appears.

### 5.2 Statistical progressiveness (H1L)

*Expected from mechanism 1: real degradation should deepen the
own-history margin statistically — occupancy rising, distributions
deepening — even where raw margins temporarily recover (self-healing,
debris migration).* **Result — supported 3/3, no kill.** All three
primary failed bearings pass all three registered tests:
alarm-occupancy Spearman over life quintiles **+0.90 / +1.00 /
+0.95** (t1-B3 / t1-B4 / t2-B1); end-of-life-versus-healthy CIs
excluding zero ([+20.1, +26.4] / [+56.6, +58.7] / [+390.8, +519.2]
IQR); Q5-versus-Q1 deepening likewise. End-of-life margins reach
+463 IQR (t2-B1) — amplitudes ordered like the physical stories. The
descriptive test-3 failed bearing shows the same pattern (ρ +0.97).

### 5.3 Lead time, persistence, and the healthy-FAR miss (H2L)

Sustained onset exists on every failed bearing: onsets at 85.0 /
69.0 / 54.6% of life, **lead times 79 / 148 / 74 h**, persistence
**93.5 / 98.2 / 99.6%**. The registered verdict is supported at 1 of
3 failures, and the split reading (logged post-execution;
presentational, verdicts unchanged) makes the two halves explicit:
early persistent detection is supported 3/3, while **design-rate
healthy FAR from self-reference is not universally supported** —
t1-B3's healthy-window FAR is **6.92%**, 13.8× the 0.5% design, and
it is a genuine false-alarm rate (its early-quintile occupancies are
1–2%, so this is not early onset). In the tested architecture,
successful longitudinal alarming required an asset-specific
historical reference; ownership of that history does not by itself
guarantee probability calibration. The same gap appeared on the
hydraulic rig (§4.5,
cooler seed 4); it is carried to §7 as a limitation, not smoothed.

### 5.4 Fleet calibration fails in the damage phase (H3L)

*Tested per mechanisms 3 and 4: the E3 transform aligns healthy
quantiles across units — and necessarily divides the unit's
likelihood displacement by its healthy scale, a mechanism consistent
with late or missed onset when an admission mechanism is applied to a
temporal-displacement problem.* The registered comparison:
per-asset margin versus the E3 fleet margin (reference bearing's
geometry and floor, target bearing standardized by the location/IQR
of its own construction window — the #3 mechanism verbatim); kill if
standardization delays onset by more than 1% of life on ≥2 of 3
failed bearings.

**Result — killed 3 of 3; the registered headline.** The E3 fleet
margin delays sustained onset by **+13.96% of life** (t1-B3),
**misses onset entirely** (t1-B4), and delays by **+11.18% of life**
(t2-B1). Figure 4 overlays both margins on all three bearings: the
fleet-calibrated trajectory tracks the healthy phase faithfully —
that is what it was fit to do — and stays below its floor while the
per-asset margin climbs through onset into triple-digit IQR
territory. A disclosed design note from the plan: the H3L statistic
bundles reference-geometry mismatch and personal-scale compression
(both parts of the registered E3 fleet mechanism); decomposing them
is future work. The conclusion is the paper's central proposition,
registered wording: **cross-sectional calibration success does not
imply longitudinal detection validity.** E3 is not killed as a
mechanism — its role is bounded: healthy commissioning, never the
failure alarm.

*Figure 4 caption (fixed): Per-snapshot median margin over life
(symlog vertical axis), per-asset reference (blue) versus the E3
fleet-calibrated alarm margin (red), three failed bearings. Sustained
onset = first index from which three consecutive snapshots have
positive median margin (it does not imply permanent positivity
afterward). Measured: leads 79/148/74 h at 93.5–99.6% persistence
per-asset; E3 +14.0% late / silent / +11.2% late. Why (mechanism):
the affine standardization that aligns healthy quantiles necessarily
divides likelihood displacement by the unit's healthy scale
(§2.7-3) — consistent with the measured delays; the registered
comparison evaluates the complete fleet-transfer mechanism (reference
geometry + standardization) and does not isolate scale compression
from reference-geometry mismatch (§2.7-4, §6.2).*

### 5.5 Same-shaft controls (H4L): detection is system-level

*Tested per mechanism 5: sensors observe the machine system, so a
neighbor's failure can surface in a control bearing's own margin.*
Registered as a finding with no kill: every same-shaft
control bearing shows a late-life sustained onset with high
persistence (test-2 controls: onsets at 71–79% of life, persistence
97–100%, at healthy FARs of 0.1–3.9%). These responses are
*consistent with* vibration transmission through shaft, housing, and
load path from the failing neighbor; alternative system-level
explanations (common load drift, rig-level change) are not excluded,
and no causal propagation claim is made. What they demonstrate
regardless of cause is that single-sensor responses do not identify
the source component. These onsets are not deleted as false alarms
and not claimed as detections of the control bearings' own state:
they are the measured reason this paper separates **anomaly
detection**
(the machine system departed from normal structure — claimed) from
**fault localization** (which component is the source — not claimed,
a separate spatial-inference task). Test 3's B4 control (16.2%
healthy FAR, onset at 32% of life) is disclosed as-is; test 3's data
quality is why it was registered descriptive.

### 5.6 Milling (registered descriptive arm)

Against a continuous physical severity variable — flank wear VB on
the NASA milling dataset — the margin's per-case Spearman correlation
has **median ρ +0.38 over 14 cases**: 11 of 14 positive (up to
+0.92), two near zero, one strongly negative (case 12, −0.82).
Reported without smoothing: the margin tracks continuous wear in
most but not all cutting conditions, auxiliary evidence for the
severity geometry on a third physical setup, claimed at descriptive
strength only.

## 6. The deployment principle

### 6.1 Three layers, each licensed and bounded by registered results

Figure 5 assembles the paper. Every layer carries the pre-registered
result that licenses it *and* the pre-registered failure that forbids
its neighbor's job:

```
Factory-shared (fleet-level shared model)
├─ fault-agnostic structural adapter
├─ shared structural geometry
├─ severity_margin — unsquashed, cross-unit comparable
│    licensed by:  #1 H1 (12/12, ρ +0.845/+0.866), #5 H1H/H2H
└─   bounded by:   #2 B–D — the geometry must NOT be widened
                   to absorb healthy individuality

Commissioning of a new unit (admission)
├─ healthy median b̂ᵢ + IQR ŝᵢ from ~64 s of healthy operation
├─ alarm location + scale, per asset
│    licensed by:  #3 E3 (FAR 0.10%, severity bit-identical
│                  by construction)
└─   bounded by:   #4 H3L — admission calibration only; not
                   used as the failure alarm

In service (asset-specific longitudinal reference)
├─ accumulate the unit's own normal history
├─ sustained onset · occupancy · deepening · persistence
│    licensed by:  #4 H1L/H2L-a (leads 74–148 h, persistence
│                  93.5–99.6%)
└─   bounded by:   #4 H2L-b — self-reference does not guarantee
                   probability calibration (t1-B3, 6.92%)
```

The severity margin and the alarm score remain distinct deliverables
end to end: the margin is read for grading and trend on the common
scale; alarms are decided against individual references. The handoff
is fleet-level shared model → asset-specific longitudinal reference:
a new unit is operational immediately after a ~64 s commissioning,
and alarm authority migrates to its own accumulated history as it
forms.

*Figure 5 caption (fixed): The three-layer deployment shape. Each
layer names the registered result that licenses it and the registered
failure that bounds its neighbor — the principle is built from both
sides of the evidence.*

### 6.2 Closing the H3L boundary mechanistically

The intellectual center of the paper is not that commissioning worked
cross-sectionally and failed longitudinally — two measurements — but
that one transform explains the shape of both. Write the
standardization once, in likelihood space (§2.4):

```
zᵢ(x) = ( ℓ(x) − b̂ᵢ ) / ŝᵢ
```

**Read it cross-sectionally.** Across healthy units i, the clean
log-likelihood distributions differ in location and scale — and in
the tested Paderborn setting, the residual healthy-individual
transfer error was adequately represented by exactly those two
differences (the #3 E1 ladder showed one scalar insufficient and
sample size irrelevant; adding ŝᵢ closed the gap to 0.10%). The affine map sends every unit's healthy quantiles
onto the reference quantiles, so the designed tail rate transfers:
admission FAR 0.10% on unseen bearings (§4.4). And because the map
acts only inside the commissioned alarm score aᵢ — never on the
shared margin m — the severity ordering is untouched by construction:
the audit's bit-identity is algebra, not luck. And the algebra never
reads ℓ's internals: #6 replayed the same two-scalar commissioning on
residual (PCA-SPE), Mahalanobis (T²), and calibrated combined-MSPC
scores, and the admission repair replicated under every one
(0.16–0.34% at bit-identical severity, §4.6) — the density model is
an interchangeable component of the transform, measured, not assumed.

**Read it longitudinally.** Fix unit i and let damage grow a
likelihood displacement Δℓ(t) below the unit's healthy level. The
commissioned alarm sees Δℓ(t)/ŝᵢ: the same division that aligned the
healthy quantiles compresses the fault signal, and a unit with
naturally dispersed clean likelihood — large ŝᵢ — received the best
healthy calibration and the most compressed fault signal, by the same
factor. This much is derived: the compression is an analytic property
of the affine map, and it provides a mechanism *consistent with* the
onset criterion being crossed late or never. What is measured is the
failure of the **complete** registered fleet-transfer mechanism —
reference geometry plus location–scale standardization — at +13.96%
of life late, silent, and +11.18% late (§5.4); the registered design
note stands: the experiment does not isolate scale compression from
reference-geometry mismatch, and that decomposition is future work
(§7). One transform; two statistical objects (population-quantile
alignment versus within-asset temporal displacement, §2.7-4); the
mechanism is derived, the combined failure is measured, and the
boundary between the two is stated rather than blurred.

H2L-b folds in as the same lesson's self-reference form: an
own-history floor fixes the *reference* — displacement is measured
against the right past — but the floor's realized tail rate is still
an estimate from finite clean data, and t1-B3's 6.92% (with the
hydraulic cooler's 0.51–5.61% split spread) shows probability
calibration is not conferred by ownership of the history. Reference
correctness and rate calibration are separate properties; this paper
validates the first and reports the second honestly as open.

### 6.3 Central sentences (fixed)

> **Share the geometry, commission the individual, and monitor
> degradation against its own history.**

> Physical damage extent was represented on a geometry transferable
> across same-spec bearing individuals, whereas valid failure
> alarming in the tested architecture required an asset-specific
> longitudinal reference.

> Cross-sectional calibration success does not imply longitudinal
> detection validity.

## 7. Limitations

1. **Fault localization is unvalidated** — and same-shaft propagation
   (§5.5) means single-sensor attribution is not merely future work
   but presently unavailable: the detector reports system-level
   departure only.
2. **Test rigs and sample sizes**: one rig per corpus; three primary
   failed bearings on IMS; same-spec bearing populations; the
   hydraulic rig is a single asset (no cross-individual axis there).
   The registered kill thresholds were set for exactly these sizes.
3. **Healthy FAR at design rate from self-reference is not
   automatic**: t1-B3 at 6.92% (13.8× design); hydraulic cooler at
   design on 1 of 5 splits (0.51–5.61%, worst under a BIC K-collapse).
   Reference correctness and rate calibration are separate properties
   (§6.2).
4. **Milling heterogeneity**: median ρ +0.38 with one strongly
   negative case; the descriptive arm does not support a uniform
   continuous-wear claim.
5. **Hydraulic negatives**: leak detection is split-fragile at cycle
   granularity (H3H killed by its registered criterion); the
   accumulator behaves consistently with an observability limit at
   this sensor set/granularity
   (mechanism 6); #5 as a whole is a registered confirmatory
   validation, not blind — carried wherever it is cited.
6. **The H3L statistic bundles** reference-geometry mismatch with
   personal-scale compression; §6.2's derivation isolates the scale
   term analytically, but the experimental decomposition is future
   work.
7. **No production commissioning API is claimed**: the commissioning
   bridge exists as a role-bounded library module; repository
   production defaults were changed by none of the six
   pre-registrations. A commissioned unit's damage phase under its
   own scale on longitudinal *fleet* data remains untested.
8. **#6's comparators are shared-protocol expressions of MSPC
   statistics, not optimised MSPC practice**: per-process control
   limits, contribution plots, and per-condition models remain
   untested; their underperformance under this protocol is never
   claimed as an advantage.
9. **The #6 feasibility audit is an oracle *existence* measurement on
   fold means**: damage labels evaluate the frontier only — no
   deployment threshold is selected from them — and single folds
   occasionally admit feasible points that the registered fold-mean
   judgment does not.
10. **The severity ladder is likelihood-deficit-specific** (#6's K3,
    fired against our own thesis): residual, Mahalanobis, and
    combined-MSPC scores did not carry the physical extent ladder on
    this corpus, and the probability-type index saturated; §2.7-1's
    scope is bounded to the likelihood deficit on the fitted support.

## 8. Conclusion

Six registered experiments on physical machine corpora — one an
explicitly disclosed confirmatory validation, one a model-invariance
test whose GMM cells are disclosed replication anchors — under one
frozen detector configuration, measured both sides of a question
conventional pooled one-class monitoring leaves implicit: what part
of learned normality is fleet property, and what part is individual
property.
The symmetric result, from success and refutation alike: a shared
fitted geometry preserved group-level physical-damage ordering across
same-spec bearing individuals (12/12 ordered condition-pairs, zero
reversals, ρ +0.845/+0.866), and the ordering principle — the same
margin construction, separately fitted — was replicated on a second
machine class in registered confirmatory form (cooler and valve
margins ordered on every registered split, the valve ordering
standing below the alarm floor) — while the
alarm does not transfer: widening the shared support to absorb
healthy individuality swallows up to 41% of the shallowest damage;
two scalars of healthy commissioning restore designed admission FAR
(0.10%) at provably untouched severity; and that same calibration,
reused as a failure alarm, is 11–14% of life late or silent, while
margins referenced to each unit's own early life detect degradation
progressively (occupancy ρ ≥ +0.90) with 74–148 h of lead at
93.5–99.6% persistence. The mechanisms are stated with the
measurements: an unsquashed likelihood deficit retained ordinal
severity over the observed degradation trajectories; an affine
calibration aligns healthy quantiles and, by the same algebra,
compresses fault displacement — a mechanism consistent with the
measured lateness, though the registered comparison does not isolate
it from reference-geometry mismatch; single-sensor measurements do
not identify the source component where vibration propagates;
observability is a property of the feature map's span. And the
boundary between formulation and score is measured rather than
assumed: the pooled-boundary dilemma and its two-scalar remedy
replicated under residual, Mahalanobis, and calibrated combined-MSPC
statistics alike — no shared clean-tail boundary reconciles
unseen-healthy admission with shallow-damage retention under any of
them, while commissioning restores designed admission under all of
them (0.10–0.34%) — whereas the physical severity ladder survived
only on the likelihood deficit, a registered kill reported against
our own thesis. Failures are
retained as load-bearing results — the
killed support-widening family, the killed fleet-alarm reuse, the
killed leak target, the healthy-FAR misses, the accumulator's
observability limit, the severity ladder's failure to generalize
beyond the likelihood deficit — because the deployment principle is built from both
sides: **share the geometry, commission the individual, and monitor
degradation against its own history.**

---
## Appendix A — Evaluation protocol and univariate-corpus results

Folded in from the v1 manuscript with numbers and tables unchanged
(cross-references renumbered; provenance in the header). Role in the
pivoted paper: the breadth-check protocol behind §3's NAB row, and
the evaluation-methodology contributions (the legitimacy rule, the
three disclosed protocols, and the protocol-inflation audit) that
§4–§5 inherit — FAR/detection pairing and self-calibrated operating
points were developed here and applied unchanged to the engineering
validations.

### A.0 Protocol overview

The protocol section carries an unusual share of this paper's
contribution, because two of our findings are about evaluation itself.
The rules below were fixed before the results of the results appendices and are
applied to our own method and to every baseline identically.

### A.1 Corpora and input conventions

Three public corpora and two synthetic probes are used, spanning three
orders of magnitude in dimensionality under the single frozen
configuration of C.12.

- **NAB** (Lavin & Ahmad, 2015): 52 labeled univariate series across
  six categories (plus five unlabeled series retained for corpus-level
  scoring), with official anomaly windows. Univariate convention
  (C.6); the first 15% of each series is probationary, as in
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
  Appendix B and Appendix D). Their generators are frozen and published; their
  geometry, never the detector configuration, is what was designed.

### A.2 The legitimacy rule

Test anomaly labels are used for exactly two things:
(1) **training exclusion** — labeled incident windows, dilated by the
±50-frame margin of C.12, are removed from normal-structure
construction; and (2) **final scoring**. Nothing else. Every threshold,
calibration constant, and score transform is derived from normal
structure alone, per C.4. The canonical statement of Section
3.1 applies verbatim: annotations act only as exclusion masks for
constructing uncontaminated normal structure — never as positive
anomaly examples, anomaly-shape templates, or threshold-selection
targets. In the ideal industrial setting, normal structure would be
built from separate clean operating logs and labels would be needed for
evaluation only; the public corpora mix incidents into their series and
provide no such logs, so exclusion is how clean normality is obtained.
This is data hygiene, not supervision — and A.9 measures how
much of everyone's performance it accounts for.

### A.3 Three disclosed protocols

Three evaluation protocols follow from the rule, and they answer
different questions; conflating them is precisely the inflation
mechanism quantified in A.10.

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
official leaderboard figures; A.10 measures the inflation on
every method we run. P3 is the official-style protocol, disclosed for
transparency in two variants: an *anchored* transform (a fixed monotone
map of each method's native decision boundary, usable online) and a
retrospective per-file min-max normalization (which consumes the file's
full score range — future information — and is marked as such).

### A.4 Baselines and fairness stance

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
zero-tuning regime is the claim under test: default-against-default is
the fair comparison for that claim, self-calibration opportunities are
granted to baselines wherever the mechanism transfers (clean-quantile
operating points, A.9; the full-accommodation transfer row,
Appendix B), and findings that depend on a baseline's frozen
configuration are labeled as such where they occur.

### A.5 Metric discipline

Two rules apply to every table in the results appendices. First, operating points
are stated with their provenance (designed rate, realized rate, or
oracle) so that no self-calibrated number sits silently beside an
oracle number. Second, **a false-alarm rate is never reported without
its paired detection figure from the same run**: a detector that flags
nothing transfers its false-alarm rate trivially, so a low realized FAR
is only evidence of a working operating point when the same row shows
the signal survived. Appendix B shows a case where this pairing is the
entire distinction between a working transfer and a dead one — the
check was developed against a baseline and then applied to ourselves.

### A.6 Reproducibility

Every run is deterministic (fixed mixture seed, no stochastic
augmentation); the full constant set is the one table in C.12
and is identical across all experiments; all corpora are public; all
harnesses, baselines, probes, and identity tests ship in the released
implementation, and each results table in the results appendices names the script
that regenerates it.

### A.7 Self-calibrated detection: the three channels

Protocol P1 on NAB, all 52 labeled files, one frozen configuration
(`tests/nab/benchmark_nab_selfcal.py`):

| Channel | Meaning | Catch | FP/10k |
|---|---|---:|---:|
| alarm (state 1) | deviation inside a known regime | 89.7% (96/107) | 247 |
| **unknown (state 2)** | **outside known normal structure** | **85.0% (91/107)** | **56** |
| **combined (state ≠ 0)** | either | **96.3% (103/107)** | 303 |

The middle row is the thesis of Appendix C made empirical. The unknown
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

### A.8 The effect of regime structure, isolated

Tier 0 and Tier 2 share the identical scorer bank (C.12), so
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
(A.7). In within-file separability (protocol P2, diagnostic),
the same substitution moves the corpus weighted mean from 58.55 to
72.02 (+13.47), with gains in every category. Regime structure, not
scorer complexity, accounts for the improvement: the scorers are the
same code in both tiers.

### A.9 Baselines under the same rule

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
and A.3 is what keeps that statement precise.

### A.10 The protocol audit

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
statistic itself (the `τ_k` of C.9): false positives fall
1087 → 266 per 10k at a cost of 2.8 catch points
(`tests/core/test_combined_calibration.py`). Both artifacts were found by
auditing our own pipeline; both corrections are part of the released
configuration.



### A.11 Post-hoc statistical audit: recording-level cluster bootstrap (not pre-registered)

The registered H1 confidence intervals resample frames, and frames
within a 4-s recording are not independent replicates (§4.1's
inference-units table). This audit — run after the internal review,
**not pre-registered, and kept out of every registered verification**
— re-estimates the adjacent-pair median differences of §4.2 by
resampling *recordings* (the finest defensible cluster: bearing-level
resampling is degenerate for the single-bearing extent groups, and
the bearing remains the generalization unit). Same primary model,
audit seed 42, 2000 resamples
(`python -m tests.figures.statistical_units_audit` →
`paper_results/statistical_audit.csv`):

| Ladder pair | Bearings (lo→hi) | Recordings (lo→hi) | Frame-bootstrap 95% CI (audit seed) | Recording-cluster 95% CI | Ordered under cluster? |
|---|---|---|---|---|---|
| inner 1→2 | 4→1 | 320→80 | [+8.4, +9.3] | [+7.5, +10.5] | yes |
| inner 2→3 | 1→1 | 80→80 | [+1.9, +2.8] | [+0.8, +3.9] | yes |
| outer 1→2 | 2→1 | 160→80 | [+12.9, +16.5] | [+9.5, +20.4] | yes |

The cluster intervals are wider, as they must be — recordings carry
the within-bearing dependence the frame bootstrap ignores — and **all
three adjacent-pair orderings survive the coarser resampling unit**
(every cluster CI excludes zero). The registered frame-bootstrap
numbers stand as reported, with their §4.1 conditional
interpretation; this audit is a sensitivity check on the resampling
unit, not a revision of any registered value.

## Appendix B — The multivariate arm and the MSPC account

Folded in from the v1 manuscript with numbers and tables unchanged.
Role in the pivoted paper: the SKAB/TEP breadth rows of §3, the
identity tests behind §3's parity statement, and the measured
saturation contrast that §2.7 (mechanism 1) cites. No detection
superiority over calibrated MSPC or the multimode-GMM lineage is
claimed anywhere in this appendix — parity is the design working as
intended.

### B.0 Relation to MSPC and the multimode-GMM lineage

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
experiments confirm it: in a direct comparison (Appendix B, with the
implementation disclosure of A.4), FGMM-BIP reaches detection
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
the unnormalized density floor retains ~+30 — Appendix D converts this
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
transfer (Appendix B), where MSPC practice re-derives control limits
per process. We also disclose the reverse trade: our BIC-based
component selection retrains over a grid of K and is heavier at
training time than Figueiredo–Jain. Finally, on interpretability, MSPC
attributes alarms through contribution plots (Kourti & MacGregor, 1996;
Alcalá & Qin, 2009); the per-scorer, per-regime attribution of Section
4 plays that role for a heterogeneous scorer bank, with the deviation
axis (jump, drift, trajectory, reconstruction) named rather than
recovered from loadings.


### B.1 Generality across scales

**Identities and parity, stated first.** The reconstruction scorer at
unit delay reproduces PCA-SPE (correlation > 0.99,
`tests/probes/test_mspc_sanity.py`), and on the single-mode Tennessee Eastman
process BIC selects K = 1, at which the unknown channel *is* Hotelling
T² — the special-case remark of C.3, observed in the wild. At
matched false-alarm rates under the same label-free threshold family,
our variants are at parity with calibrated SPE / T² / SPE∨T² on TEP
(±2 points) and SKAB (edge trades). One earlier internal claim — that
joint detection needs a 6.5× smaller false-positive budget than
per-channel detection — is retracted here: it compared a calibrated
joint statistic against an uncalibrated OR of channels, i.e. exactly
the A.10 artifact. The corrected comparison is parity.

**The unknown channel across scales** (the result that repeats):

| Data | d | Unknown-channel result |
|---|---:|---|
| NAB | 1→5 | 85.0% catch @ 0.56% FP (A.7) |
| SKAB | 8 | 100% (34/34) @ 382 FP/10k — including both windows T² misses (the two files where BIC finds three regimes) |
| TEP | 52 | degenerates exactly to T² (K = 1 selected) |
| Ghost probe | 2 | catches > 80% of a fault that global T² rates *more normal than average* |

The last row is the structural case (`tests/probes/test_regime_ghost_state.py`,
Figure B1): a bimodal process with a fault frozen between the modes. The
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
of the FGMM-BIP index (A.4), detection is at parity: every
GMM-family index catches the ghost fault at 100%, and on SKAB, FGMM-BIP
scores 100% @ 266 FP/10k against the unknown channel's 100% @ 253. The
multimode advantage over single-model T² belongs to the whole lineage.
Two deltas survive. First, severity: BIP's margin beyond its own alarm
boundary on the deep ghost is +0.0 IQR — detection numerically marginal
— against +30.3 for the raw density floor; the probability-type index evaluated here
saturates exactly where grading is needed (Appendix D makes this
operational). Second, the frozen-configuration OC-SVM is valley-blind
(0% ghost detection at matched low-FAR points; SKAB FP floors 337–348
vs 253) — a zero-tuning-regime finding, config-dependent as disclosed
in A.4.

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
Figure B2).
Each method fixes its operating point on a fit split of clean data;
we report the realized flag rate on held-out clean frames against the
method's own designed rate, with detection at that same transferred
point (A.5):

| Method (realized FAR / detection) | rig (d=2) | SKAB (d=8) | TEP (d=52) |
|---|---|---|---|
| ours (0.5% floor, designed 0.5%) | 1.06% / 100% | 0.33% / 57.8% | 0.00% / **58.1%** |
| OC-SVM, γ frozen once (designed 5%) | 5.19% / 100% | **21.9%** / 80.6% | **100% (collapse)** / 100%† |
| OC-SVM, γ re-derived per dataset | 5.12% / 100% | 4.60% / 68.0% | **23.5% (×4.7)** / 88.1% |
| OC-SVM + our mechanism (hybrid) | 5.62% / 94.0% | 4.53% / 68.3% | 0.00% / **0.0%** |

† 100% FAR flags everything; its "detection" is vacuous.

The mechanism is the one stated in C.6: a percentile of the
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
kills the hybrid row, so the A.5 pairing rule applies to us: at
that transferred point our detection is 58.1% of fault frames — same
run, same table. A silent detector transfers FAR trivially; a valid one
transfers FAR and signal together.

**Self-catch, disclosed.** The first run of this test drifted *our*
realized rate ×32 at d = 52 — an in-sample floor over an overfit
52-dimensional density, the third occurrence of in-sample percentile
bias in this project. The C.11 guardrails are load-bearing, and
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
matched points (A.9).

### B.7 Ablations and self-tests

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
diagonal light path of Appendix B can match the full floor. We report
the falsification rather than the hypothesis because the corrected
attribution is the useful engineering fact.



## Appendix C — Formal problem statement and architecture detail

Folded in from the v1 manuscript (definitions, scorer bank, and the
frozen constant table are the released implementation §2 summarizes).
The v1 text below retains its own motivating vocabulary in places
("unattended operation", "onboard"); those constraints originated the
frozen-configuration and self-calibration requirements that the
engineering validations of §4–§5 then tested on physical corpora.

### C.0 Formal problem statement

### C.1 Setting and data hygiene

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

### C.2 Normal structure

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
(quantified in A.10). `D̃_t` is a ratio, unbounded above, and
monotone in every scorer: it is a severity, not a probability.

### C.3 The three-state output

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
P_t = ( state_t,  r_t,  D̃_t,  { s_j/T_{r_t,j} }_j,  ℓ_floor − ℓ(φ_t),  P(R_{r_t}|φ_t) )
```

— state, regime, calibrated severity, per-scorer attribution, support
margin (positive outside the support, matching the severity margin's
sign convention throughout), and assignment confidence. The problem this paper addresses is
the construction of `S` and the delivery of `P_t`, causally and
onboard; any downstream decision logic is a consumer of `P_t`
(Appendix D exhibits one). This also fixes what "AI-ready" means in
this paper, narrowly: the output is the structured causal payload
`P_t`, not a scalar anomaly score, so downstream rule-based or learned
policies receive state, regime, attribution, confidence, and severity
without reconstructing detector internals.

**Remark (classical special cases).** With `K = 1` and a Gaussian
density, the state-2 rule is a Hotelling T² control chart; with a
delay window of one frame, the reconstruction scorer in the bank of
Appendix C is PCA squared prediction error. Both reductions are
verified as identities in Appendix B — the formulation contains the
classical statistics rather than competing with them.

### C.4 Constraints as formal requirements

The four application-class constraints of the v1 framing (unattended operation, onboard computation, worlds exceeding commissioning data, graded incident response) appear in this
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
   anomalous examples; anomaly shapes never enter estimation, and
   annotations enter only as exclusion masks for data hygiene (C.1)
   and at final evaluation.
4. **Non-saturating severity** — both severities (`D̃_t` and the
   support margin) are unbounded ratios or differences, monotone in
   the underlying scores; no component maps severity through a
   probability-type squashing that saturates beyond the alarm boundary.

Requirements 1–3 restrict how `S` may be built; requirement 4
restricts what may be reported. Appendix C gives the concrete
architecture; Appendix A states the evaluation protocol that keeps the
same discipline at measurement time.

### C.5 The architecture: overview

This section instantiates the tuple `S` of Definition 1; Figure C1
sketches the pipeline. The
architecture is one system with two input conventions and two
operational modes; nothing in it is specific to any evaluation corpus,
and every constant introduced below is a structural default, frozen
across all experiments in this paper and adjustable if desired.
Corpus-specific matters (which convention applies where, how
construction data is obtained) belong to the protocol and are stated
once, in Appendix A.

### C.6 Input conventions and normalization

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

### C.7 The scorer bank

Six causal scorers watch six structural axes of the normalized stream.
Each obeys the same contract: it is calibrated on construction data,
scores frame `t` from `events[:t+1]` only, and owns a threshold set by
the same robust percentile rule (C.8), so that the ratio
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
the results appendices reports the measured consequence, and multivariate-aware
trend scorers are future work.

### C.8 Regime layer and per-regime thresholds

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

### C.9 Fused deviation and its calibration

Per frame, the fused deviation is the OR vote of Definition 3:
`D_t = max_j s_j(t)/T_{r_t,j}`. As C.2 states, an OR over six
~1% tails flags clean data at up to ~6%, so the fused statistic is
calibrated against its own clean distribution: `τ_k` is the same
trimmed percentile applied to `D` on construction frames of regime `k`,
and the reported severity is `D̃_t = D_t/τ_{r_t}`. The per-scorer
thresholds retain their role as cross-scorer scale alignment; `τ_k`
restores the designed clean flag rate to the fusion. The measured
effect of this one constant is reported in A.10.

### C.10 The unknown channel and state assembly

The support floor `ℓ_floor` is the 0.5th percentile of the mixture
log-likelihood on a nested held-out slice of construction data (the
out-of-sample rule of C.11). At inference, a frame with
`ℓ(φ_t) < ℓ_floor` is outside known normal structure: it is reported as
`state 2` with severity `ℓ_floor − ℓ(φ_t)` (an unbounded difference —
requirement 4), taking priority over the in-regime verdict exactly as
C.3 prescribes. Otherwise `state = 1[D̃_t ≥ 1]`. The channel
costs nothing new: it reuses the mixture already fitted for the regime
layer, evaluated once per frame.

### C.11 Estimation guardrails and the light path

Two guardrails govern how the floor is estimated when model capacity is
high relative to the construction sample, and both are transferability
design conditions in the sense of Appendix B — each is backed by a
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

For microcontroller-class budgets, a **light path** evaluates the
same support-floor semantics with diagonal covariance: per frame, `K·d`
squared standardized distances and a log-sum-exp — no matrix products,
no stored covariance factors. At `d = 52` this is 468 floating-point
operations and 1.26 KB of parameters per frame (platform-independent
counts; wall-clock figures in the results appendices are desktop-measured, and
on-device measurement is future work). Appendix B reports where the
light path matches the full-covariance floor and where it does not.

### C.12 Operational modes and the frozen configuration

Two modes share the identical scorer bank:

- **Tier 0 (streaming baseline)** calibrates every scorer on the head
  segment of the stream and OR-votes thereafter, with no regime layer,
  no fusion calibration, and no unknown channel. It exists in this
  paper as the controlled ablation: identical scorers, no structured
  normality.
- **Tier 2 (regime-aware)** is the full system of C.6–C.11 and
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
| Exclusion mask margin | ±50 frames | hygiene dilation (Appendix A) |
| Jump / gradual scales | {5, 20, 50, 200} / {50, 200, 500} | scorer time scales |
| Delay width / rank | 20 / ≤ 5 | embedding geometry |
| PCA guardrail | d ≳ 16, 90% variance | density sanity at scale |

These are structural defaults in the sense of C.4: they encode
what jumps, drifts, and regimes *are*, not what any particular dataset
looks like. None was changed for any corpus, dimension, or scale in
this paper; all are adjustable if a deployment desires.



## Appendix D — Worked downstream consumer and failure taxonomy

Folded in from the v1 manuscript with numbers unchanged. Role in the
pivoted paper: qualification of the payload semantics — the
three-state output and non-saturating margin that §2.2–§2.3 rely on —
including the four-event graded-action demonstration and the measured
policy-level consequence of probability saturation (the §2.7
mechanism-1 contrast made operational).

### D.0 Overview

This section reads the system's outputs the way a consumer would — its
failures first, then a demonstration that the interpretation payload of
C.3 is sufficient, by itself, to drive graded action.

### D.1 Failure as structural feedback

Per-file separability on the univariate corpus is sharply bimodal
(Figure D2): files where clean construction data covers the operating
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
producing silent zeros — the 85% catch of A.7 includes exactly
such files — so the failure of the normality description is itself
reported, per frame, in-band. What remains honestly weak is *in-regime*
detection on Mode B files: the unknown channel says "outside my
description", not "here is the anomaly type". For the unattended
setting, this is the designed division of labor: an
explicit report of departure from described normality is the input a
protective policy can act on; a silent zero is not.

### D.2 From payload to graded action: a worked consumer

The claim "AI-ready interpretation layer" owes the reader a consumer.
We provide the smallest honest one: a rule-based policy, roughly thirty
lines (`tests/probes/test_downstream_policy.py`), deliberately containing no
learning and no detector machinery of its own — if the policy is
trivial, whatever it achieves is attributable to the payload it
consumes. The policy sees only C.3's `P_t`: the state channel,
per-scorer attribution, and the unnormalized support margin with its
own trajectory.

**Rig.** A two-channel bimodal process (commanded load switching
between two plateaus, temperature relaxing toward a load-dependent
setpoint, plus slow ambient wander), with four embedded events of
distinct ground-truth character: **E1**, a four-frame in-support
temperature transient; **E2**, a slow leak ramping the temperature out
of the support over ~90 frames; **E3**, the process stuck *between* the
two modes at a shallow valley position; **E4**, stuck at the valley
center — the ghost geometry of Appendix B. Per A.1, the rig's
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
constants are structural defaults in the C.12 sense — a depth
that separates "outside" from "deep inside the forbidden region", a
slope that separates creep from step — not values fitted to the rig.

**Result.** All four events receive their intended distinct actions,
and the policy is quiet on ≥97% of normal frames (Figure D1):

| Event | Ground truth | Payload signature | Action |
|---|---|---|---|
| E1 | in-support transient | state 1, fast-scorer attribution | transient check |
| E2 | slow leak | state 2, onset 0.65 IQR/frame | schedule maintenance |
| E3 | shallow ghost | state 2, abrupt onset (3.4–8.2 IQR/frame), depth ≈ 5 IQR | reduce & investigate |
| E4 | deep ghost | state 2, abrupt onset, depth ≈ 42 IQR | **stop & escalate** |

Three payload properties do the work, and each maps to a deployment
requirement. The state channel plus attribution separates E1's
transient from E2's wear pattern (interpretability of the deviation
axis). The margin *trajectory* separates E2 from E3 — gradual versus
abrupt egress, read off the payload with no additional detector. And
the margin's *depth* separates E3 from E4 — the graded-response
requirement made concrete.

**The saturation contrast, made operational.** On the same run, the
FGMM-BIP index (A.4) saturates on both ghosts: median > 0.99 on
each, separated by less than 0.02 — while the unnormalized margins
differ by more than a factor of three and straddle the 10-IQR default
from opposite sides. The consequence is not a score-quality nuance but
a policy-level impossibility: any policy driven by the saturated index
must give E3 and E4 the same action, and this is asserted, not argued —
the test suite verifies that the BIP-driven variant of the same policy
collapses the two actions while the margin-driven one separates them.
Both indices detect both ghosts; detection was never the question. A
severity that cannot grade cannot prioritize, and prioritization is
what a graded protective ladder requires.

### D.3 What the demonstration does and does not show

It shows that the payload of C.3 carries enough information —
state, attribution, margin, and margin trajectory — for a trivial
consumer to emit four correctly ranked protective actions on events of
four distinct characters, and that one of those distinctions is
structurally unavailable to the probability-saturating index we
evaluate. It does not
show a validated protective system: the rig is synthetic, the events
are four, the policy constants — though structural — have two of them,
and no closed-loop consequence (did stopping help?) is evaluated.
Closed-loop evaluation on physical platforms is future work
(future work; §7 of the main text), and the division of labor stands as designed: this paper's
subject is the observation layer; the consumer exists to prove the
interface carries what a policy needs.



## Appendix E — Pre-registration documents

The six plans are part of the released repository
(`doc/preregistrations/`); each was written with hypotheses and kill
conditions fixed before execution, and each implementation was frozen
in a commit before its results were read (freeze SHA precedes results
SHA in the repository history).

| # | Plan (doc/preregistrations/) | Runner | Freeze / provenance | Verdict chain |
|---|---|---|---|---|
| 1 | experiment_plan_paderborn.md | `python -m tests.paderborn.exp_paderborn_full` | plan fixed 332b1d2 · results 088bc8e | H1 supported 12/12; H2 killed on purity (confound disclosed); H3 killed by its kill condition |
| 2 | experiment_plan_paderborn2.md | `python -m tests.paderborn.exp_paderborn2` | impl frozen 8ea1a9d | A–D killed (support widening); E inconclusive-positive |
| 3 | experiment_plan_paderborn3.md | `python -m tests.paderborn.exp_paderborn3` | impl frozen c61f061 | E3 supported (FAR 0.10%, severity bit-identical); E0/E2 killed; E1 ladder flat |
| 4 | experiment_plan_ims.md | `python -m tests.ims.exp_ims` | impl frozen b387a4f | H1L supported 3/3; H2L split (one healthy-FAR miss); H3L killed 3/3; H4L finding; milling descriptive |
| 5 | experiment_plan_hydraulic.md | `python -m tests.hydraulic.exp_hydraulic_prereg` | plan 2f78443 · impl 7c6d054 | H1H/H2H supported; H3H killed; H4H limit confirmed (registered confirmatory) |
| 6 | experiment_plan_density_invariance.md | `python -m tests.paderborn.exp_density_invariance` | plan dd264cc · impl 8beb325 · results 3b75342 | H1c supported 4/4 (K1 silent); H2 supported 4/4; H3 first half killed — K3 fires (ladder is likelihood-deficit-specific); K4 anchor exact |

Reproducibility: all corpora are public; every run is deterministic;
the machine-readable snapshot `paper_results/` (generated by
`python -m tests.figures.export_paper_results`) reproduces the
registered statistics — manifest verification 16/16 — and the
main-text figures are rendered from that snapshot alone
(`python -m tests.figures.make_paper_v2_figures`). #6 additionally
emits `density_invariance.csv`, `density_feasibility.csv`, and
`density_severity.csv` into the same snapshot directory directly from
its frozen runner (not part of the 16/16 manifest verification, which
covers the #1–#5 export pipeline).
