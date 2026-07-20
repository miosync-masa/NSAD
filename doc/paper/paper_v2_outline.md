# Paper v2 outline — the engineering pivot

Target venue: **Mechanical Systems and Signal Processing (MSSP)**
(first choice; submission main field: **[A] Signal processing in
machine/system health monitoring**). Fallbacks: EAAI, Reliability
Engineering & System Safety — same manuscript spine, different section
weighting. This document is the working outline of the
pivoted manuscript — **now drafted**: [paper_draft.md](paper_draft.md)
is the complete v2 manuscript written to this outline (§1–§8 plus
Appendices A–E). The v1 draft's evidence material is folded into those
appendices with numbers unchanged; the v1 manuscript itself is
preserved verbatim in git history.
Concept, abstract, and contribution bullets: [abstract.md](abstract.md).
Claim–evidence correspondence: [claim_evidence_map.md](claim_evidence_map.md).

**Venue pivot rationale (logged 2026-07-10).** The paper's center is
no longer "a generic AI anomaly detector applied to engineering" but
*how healthy individuality, physical damage severity, alarm
calibration, and longitudinal degradation are separated as signal
structure in machine condition monitoring* — normal-structure signal
interpretation for machine health monitoring. That is MSSP's stated
scope (signal processing in machine/system health monitoring; time
series methods; uncertainty quantification; prognostics), and the
evidence base is theory + physical experiment, which MSSP explicitly
requests. Consequence for the writing (not for the evidence): the
mechanism of each result must be stated mathematically/physically, not
only measured — the §2.7 obligations below.
*Outline review incorporated (2026-07-10), four writing directives,
zero new experiments*: (1) §2.7 back-referenced from every Results
subsection and figure caption (pairing rule); (2) §3 hard-capped at
half a page; (3) §1 gains the MSSP-native competitive landscape with
the supervised-diagnosis differentiation stated first; (4) §6 closes
the H3L boundary mechanistically from §2.7-3/4 — success and failure
derived from the same affine equation.

**Integration-phase rules (binding).** No new detection features, no
new feature vocabulary, no new threshold tuning, no RUL extension, no
fault-localization extension, no production-default change, no change
to any pre-registered verdict or number. Post-hoc interpretation is
always separated from pre-registered results.
*Logged amendment (2026-07-10)*: the no-new-experiments rule was
lifted by explicit author authorization for exactly one addition —
pre-registration #5 (hydraulic graded severity), executed under the
full freeze discipline (plan 2f78443 → runner 7c6d054 → results) with
no new features (the promoted cycle-phase vocabulary, as released) and
no default changes. Everything else above stays binding.
*Logged amendment 2 (2026-07-14)*: the same rule was lifted a second
time by explicit author authorization for exactly one addition —
pre-registration #6 (density-model invariance of the support-widening
dilemma), executed under the full freeze discipline (plan dd264cc →
runner 8beb325 → results 3b75342) with no new features (comparator
statistics PCA-SPE / T² / FGMM-BIP reuse the released Appendix-B
implementations on the frozen #2 geometry; the calibrated combined
statistic is a registered evaluation construct, not a product change)
and no default changes. Manuscript effect: new §4.6, §2.7-1 scope
bound (K3), formulation-level wording licensed by H1c, "six registered
experiments". Everything else above stays binding.

---

## 1. The central problem

Conventional pooled one-class monitoring — a single shared normal
support with a single alarm score — collapses two different sources
of deviation into the same outlier score: **normal variation between
healthy individuals** of identical specification, and **change caused
by physical damage**. The consequence is a dilemma that support
widening alone did not escape in the tested formulation: a narrow normal support false-alarms on unseen healthy units
(Paderborn: 42% mean FAR on unseen healthy bearings under the flat
pooled support), while a widened support absorbs shallow damage
(extent-1 absorption 11.9% → up to 41.1% under the widened
candidates, with detection dropping and one severity-ordering pair
lost).

The paper's question:

> How can a deployable alarm design handle distinct-but-same-spec
> healthy individuals without losing physical damage severity and
> longitudinal degradation progression?

## 2. The answer in one paragraph (the deployment principle)

Share what is shareable, calibrate what is individual, and reference
what is historical:

- **Shared (fleet)**: the fault-agnostic adapter, the structural
  feature geometry, the severity-margin scale — the common ruler that
  reads damage ordering (pre-reg #1: inner 8/8, outer 4/4, zero
  reversals, ρ +0.845 / +0.866).
- **Per-individual (commissioning)**: the alarm origin — location and
  scale (median + IQR) of the unit's own clean likelihood, from ~64 s
  of healthy operation (pre-reg #3: unseen-healthy FAR 0.10%,
  severity bit-identical).
- **Per-history (in service)**: the longitudinal degradation
  reference — sustained onset, alarm occupancy, distributional
  deepening, persistence, built from the unit's own early life
  (pre-reg #4: occupancy ρ +0.90 / +1.00 / +0.95, lead 74–148 h,
  persistence 93.5–99.6%; the fleet calibration reused as the failure
  alarm is 11–14% of life late, or silent).

Central sentences (fixed):

> **Share the geometry, commission the individual, and monitor
> degradation against its own history.**

> Physical damage extent was represented on a geometry transferable
> across same-spec bearing individuals, whereas valid failure
> alarming in the tested architecture required an asset-specific
> longitudinal reference.

> Cross-sectional calibration success does not imply longitudinal
> detection validity.

## 3. Scope separations (stated in the manuscript, verbatim intent)

**Detection vs localization.** On IMS, non-failed same-shaft control
bearings also show late-life sustained onsets (onset 71–79% of life at
97–100% persistence for the test-2 controls) — each sensor observes
the machine system (shaft, housing, load path), not only the bearing
beneath it. The paper claims **anomaly detection** (has the machine
system departed from its normal structure somewhere), and explicitly
does **not** claim **fault localization** (which component is the
source). Localization is described as a separate spatial-inference
task and a limitation/future-work item; no new implementation or
experiment is added for it.

**Benchmarks vs primary evidence.** NAB / SKAB / TEP are retained but
demoted from primary evidence to qualification:

> Generic benchmark results are retained as breadth checks; the
> primary evidence comes from cross-sectional physical-damage
> validation and longitudinal run-to-failure evaluation.

Their in-paper roles: generic time-series qualification (NAB),
multivariate anomaly qualification (SKAB), process/regime
qualification (TEP) — confirmation that NSAD operates as a general
anomaly detector. Full configurations, complete result tables, and
baseline comparisons move to the Appendix.

**No-RUL / no-localization guardrails.** The paper never claims RUL
prediction (pre-reg #4 A1 directive), never claims source
identification, never presents E3 commissioning as a successful
failure detector (H3L killed 3/3), never hides the H2L healthy-FAR
miss (t1-B3, 6.92%), and never deletes the control-bearing onsets as
mere false alarms.

---

## 4. Section-by-section outline

### §1 Introduction
- The conflation problem: healthy individuality and damage collapse
  into one outlier score.
- The engineering dilemma: narrow support → false alarms on unseen
  healthy units; wide support → shallow damage absorbed. Both sides
  *measured* in this paper, not argued (pre-reg #1 H3, #2 B/C/D).
- **Competitive landscape, MSSP-native (mandatory).** Position the
  work inside the literatures MSSP readers live in, not the AI
  benchmark literature: envelope analysis and the fault-frequency
  tradition (Randall & Antoni line), spectral kurtosis,
  cyclostationary analysis, deep-learning PHM (CNN/LSTM fault
  classifiers on CWRU/Paderborn), transfer learning for bearing fault
  diagnosis, and Bayesian degradation modeling. The Paderborn corpus
  (Lessmeier et al. 2016) is a standard supervised-diagnosis
  benchmark, so the differentiation is stated first, in our own
  voice: **supervised fault classifiers answer "which known fault is
  this?" from labeled fault examples; this paper answers a different
  question — "how do we separate normal individuality from damage,
  and grade the damage, without ever learning a fault shape?"** No
  detection-accuracy comparison against fault classifiers is claimed
  or owed: the methods consume different information (fault labels vs
  healthy data only) and produce different outputs (class posterior
  vs severity margin + calibrated alarm). Envelope analysis is the
  complementary contrast on the signal side: it encodes fault-specific
  physics (defect frequencies) a priori; the fault-agnostic vocabulary
  deliberately does not, and §2.7-2 states what is paid and bought.
- The deployment question (§1 above) and the three-layer answer,
  previewed.
- Contribution summary: the methodological (signal/statistical)
  contribution / engineering contribution split (abstract.md §4).
- Scope nails: anomaly detection, not localization; no RUL; evidence
  is pre-registered with frozen implementations (freeze SHA precedes
  results SHA).

### §2 Method
- Fault-agnostic structural adapter (vibration vocabulary,
  sample-rate-independent construction; no fault-frequency
  alignment).
- Shared severity geometry and the support margin (non-saturating,
  cross-unit comparable).
- The role separation carried through the whole paper:
  **severity_margin** (ordinal damage-depth ruler, shared) vs
  **alarm decision** (FAR-controlled, individual) — two different
  statistical objects.
- Commissioning calibration: per-unit location + scale of clean
  likelihood (the E3 mechanism), role-bounded to healthy admission.
- Per-asset longitudinal reference: construction from the unit's own
  early life; sustained onset / occupancy / deepening / persistence
  as the degradation readouts.
- Detector core inherited unchanged from the released implementation
  (frozen defaults; pointer to Appendix for the architecture detail
  already drafted in v1 §3–§4).
- **§2.7 Signal-level rationale (MSSP writing obligations).** Six
  mechanisms the venue will demand stated mathematically/physically,
  each already grounded in an executed result — no new experiments,
  only exposition.
  **Pairing rule (binding).** §2.7 does not discharge the obligation
  by existing inside §2: MSSP's review axis "contribution to
  understanding the underlying physics/signal processing" is scored
  next to the results. Therefore every Results subsection in §4–§5
  **opens with one back-reference sentence** recalling its §2.7
  mechanism ("this is expected to hold because…"), and every results
  figure caption pairs the measurement with its one-line why. The
  mechanism map is fixed here: §4 severity ordering ↔ 2.7-1/2;
  §4 commissioning ↔ 2.7-3; §4 support-expansion failure ↔ 2.7-4
  (population-quantile side); §4 hydraulic ↔ 2.7-1/2/6; §5
  progressiveness ↔ 2.7-1; §5 H3L ↔ 2.7-3/4; §5 H4L ↔ 2.7-5.
  The six mechanisms:
  1. *Why the margin preserves severity*: the margin is an
     unnormalized log-likelihood distance below the clean support
     floor — an unsquashed likelihood deficit, not a metric distance
     and not monotone in general for multimodal densities; ordinal
     severity is retained when the feature map resolves the physical
     degree of freedom and the fitted log-likelihood decreases along
     the observed degradation path — an empirical condition, tested
     (evidence: #1 H1 ordering, #5 H1H/H2H; drafted per the v2.1
     internal review).
  2. *Why the vocabulary is fault-agnostic*: the qualification law
     (architecture §13.2) — log-spaced band energies, spectral
     entropy, generic envelope bands, cycle-phase profile + timing —
     nothing aligned to fault frequencies or component identities; the
     cycle-phase case carries its own mechanism proof (|FFT| is
     circular-shift invariant; the timing features move monotonically
     with lag — `tests/core/test_cycle_phase.py`).
  3. *What location–scale calibration changes and what it cannot*: an
     affine transform of the unit's clean log-likelihood — it moves
     the alarm origin and unit (decision variable) and provably leaves
     the shared geometry and margin untouched (severity audit
     bit-identical, #3); the same algebra explains the longitudinal
     failure — dividing by a unit's healthy IQR divides the absolute
     damage displacement with it (H3L: late or silent).
  4. *Cross-sectional vs longitudinal semantics*: admission FAR is a
     population-quantile alignment problem; failure alarming is a
     within-asset temporal-reference problem; the two are different
     statistical objects, and #3-success + #4-kill is the measured
     proof that solving one does not solve the other.
  5. *Why same-shaft propagation separates detection from
     localization*: a vibration sensor observes the response of the
     mechanical system (shaft, housing, load path), so departure from
     normal structure is a system-level observable; attributing it to
     a component requires spatial inversion (arrival order, amplitude
     ratios, phase) that a single-sensor detector does not perform
     (H4L controls).
  6. *Observability limit, defined*: a fault mode is observable at
     granularity g iff its physical degree of freedom displaces the
     feature map φ_g on the fitted support; the accumulator's
     invariance across every registered granularity (H4H, 5/5) is the
     operational demonstration — a representation property, not a
     detector property.

### §3 Generic qualification (short — **hard cap: half a page**)
- Length rule, fixed: MSSP readers largely do not know NAB, and the
  IT time-series benchmark world is outside their landscape — every
  paragraph spent here reads as misallocated pages. Half a page
  total: one summary table row per corpus + the framing sentence.
- Content: NAB (unknown channel 85% @ 0.56% FP; combined 96.3%),
  SKAB (100% @ 382/10k), TEP (K=1 degeneration to Hotelling T²;
  SPE/T² identities) — as breadth checks only, with the verbatim
  framing sentence of §3 above. The T²/SPE identities are the one
  detail worth a sentence here, because they speak MSSP's language
  (the detector contains the classical statistics as special cases).
- Everything else (protocol taxonomy, baselines, duel, transfer
  test, cost tables) → Appendix.

### §4 Cross-sectional engineering validation (Paderborn #1–#3)
- Corpus and ground truth: real accelerated-lifetime damage with
  known physical extent; six healthy individuals.
- **Shared severity** (#1 H1) [opens with §2.7-1/2 back-reference]:
  12/12 ordered pairs, zero reversals, ρ +0.845/+0.866;
  identity-noise floor disclosed.
- **Support expansion failure** (#1 H3, #2 A–D) [opens with §2.7-4
  back-reference, population-quantile side]: the FAR/absorption
  table; B's lost ordering pair; the registered kill conditions doing
  their job.
- **Two-scalar commissioning** (#2 E → #3 E3) [opens with §2.7-3
  back-reference — what the affine transform can move]: the E1-ladder
  diagnostic (model, not sample size); E3 at 0.10% FAR from ~64 s;
  severity audit bit-identical. Role bound stated immediately:
  healthy admission calibration, not a failure alarm.
- #1 H2 (condition-as-regime purity) reported killed, with its
  confound.
- **Cross-domain graded severity (#5, hydraulic rig)** [opens with
  §2.7-1/2/6 back-references] — closing
  subsection: the severity geometry read against graded physical
  labels on a second machine class (cooler 100% detection with
  CI-separated ordered margins on 5/5 splits; valve margins ordered,
  ρ +0.89…+0.93, at stages the alarm cannot yet detect — the
  severity/alarm role separation on timing geometry); the leak target
  killed by its registered detection criterion (split fragility the
  single-split exploration had masked); accumulator observability
  limit registered and confirmed. Cited with its §0 disclosure:
  registered confirmatory validation, not blind.

### §5 Longitudinal engineering validation (NASA IMS #4)
- Per-asset mode: construction on the unit's own first 20% of life.
- **Statistical progressiveness** (H1L 3/3) [opens with §2.7-1
  back-reference]: occupancy ρ, EOL deepening CIs, up to +463 IQR.
- **Lead time / persistence / healthy FAR** (H2L, split reading):
  74–148 h leads at 93.5–99.6% persistence; the t1-B3 6.92%
  healthy-FAR miss reported as a genuine miss.
- **Fleet calibration fails in the damage phase** (H3L killed 3/3)
  [opens with §2.7-3/4 back-reference — the same affine algebra,
  other consequence]: +13.96% / silent / +11.18% of life — the bound
  on §4's commissioning win; the bundling disclosure (geometry
  mismatch + scale compression).
- **Same-shaft control finding** (H4L) [opens with §2.7-5
  back-reference]: late-life onsets on non-failed bearings; the
  detection-vs-localization scope split.
- Milling as auxiliary/descriptive: margin vs continuous wear,
  median ρ +0.38, heterogeneity included.

### §6 Deployment principle
- The three-layer shape (fleet geometry → healthy admission
  commissioning → per-asset longitudinal monitoring), each layer
  carrying the pre-registered result that licenses it *and* the
  pre-registered failure that forbids its neighbor's job.
- Severity margin vs alarm score as distinct deliverables.
- **Closing the H3L boundary mechanistically (the paper's
  intellectual center — mandatory subsection).** Not "commissioning
  worked cross-sectionally and failed longitudinally" as two
  measurements, but **two consequences of the same equation**, via
  §2.7-3/4: write the likelihood standardization
  zᵢ = (ℓ − b̂ᵢ)/ŝᵢ once (the commissioned alarm score is
  aᵢ = (ℓ_floor − (b_ref + s_ref·zᵢ))/s_ref; the shared margin is a
  different object and is never transformed), and
  read it twice. Cross-sectionally, the affine map aligns healthy
  quantiles across units, so the admission FAR lands at design (#3,
  0.10%) while the shared geometry — and with it severity ordering —
  is untouched by construction (bit-identical audit). Longitudinally,
  the *same* division by the unit's healthy scale ŝᵢ divides the
  absolute damage displacement: a unit with a large healthy IQR has
  its fault growth compressed by exactly the factor that made its
  healthy phase well-calibrated — hence onset 11–14% of life late, or
  never (H3L 3/3). One transform; two statistical objects
  (population-quantile alignment vs within-asset temporal
  displacement); success on one axis and failure on the other are
  *derived*, not merely observed. Fold H2L-b in as the same lesson's
  self-reference form: an own-history floor fixes the reference, not
  the calibration (t1-B3's 6.92%). This subsection is what moves the
  paper from experiment report to contribution-to-understanding — the
  MSSP review axis the venue pivot was for.
- The handoff: a new unit is operational after short commissioning;
  alarm authority migrates to its own history as it accumulates.

### §7 Limitations
- Fault localization unvalidated (and same-shaft transmission means
  single-sensor attribution is not available).
- Test rigs: one rig per corpus; three primary failed bearings;
  same-spec populations.
- Healthy FAR at design rate from self-reference is not automatic
  (t1-B3).
- Milling heterogeneity (one strongly negative case).
- Production commissioning API not implemented; defaults unchanged.
- Commissioned unit's damage phase under its own scale on
  longitudinal fleet data — untested.

### §8 Conclusion
- The symmetric result, measured from success and refutation sides;
  the central sentences of §2 above.

### Appendix (migration from v1 draft)
| Appendix | Content | Source in v1 draft |
|---|---|---|
| A | NAB protocol, three-protocol taxonomy, self-calibrated results, baselines, protocol audit (+25–59 pt sweep inflation, OR multiple-comparison fix) | paper_draft.md §5, §6.1–6.4 |
| B | SKAB / TEP multivariate arm: identities, unknown-channel table, FGMM-BIP duel, light-path costs, frozen-config transfer | paper_draft.md §6.5–6.6 |
| C | Architecture detail and formal definitions beyond §2's needs | paper_draft.md §3–§4 |
| D | Worked downstream consumer + failure taxonomy (kept as qualification of the payload semantics) | paper_draft.md §7 |
| E | Pre-registration documents as supplementary material (plans #1–#5, verbatim, with freeze SHAs) | doc/preregistrations/experiment_plan_* |

---

## 5. Figures plan (no new experiments; regenerated from cached runs only)

Existing figures fig1–fig5 (NAB/multivariate) move with their
sections to the Appendix. Main-text figures are a two-stage build
(publication engineering, not research): (1)
`python -m tests.figures.export_paper_results` re-executes the #1–#5
pre-registered computations through the frozen runners (identical
seeds, splits, and evaluation order) into the machine-readable
snapshot `paper_results/` (CSV/NPZ + manifest.json with a
verification block against the registered numbers); (2)
`python -m tests.figures.make_paper_v2_figures` renders
doc/figures/v2_fig1–v2_fig5 from that snapshot ONLY — no dataset
access, no hand-typed numbers.
Caption rule, per the §2.7 pairing rule: every results figure caption
carries its one-line mechanism ("measured + why") alongside the
measurement:

1. Severity ladder: per-bearing median margin vs physical extent,
   per condition (Paderborn #1).
2. The dilemma panel: FAR vs extent-1 absorption for A–E candidates
   (#2/#3) — support widening vs commissioning, one picture.
3. IMS margin trajectories with sustained onset, occupancy per
   quintile, and the E3-vs-raw onset delay (#4).
4. The three-layer deployment schematic (fleet prior → commissioning
   → asset posterior).
5. Hydraulic graded severity (#5): per-stage margin distributions for
   cooler and valve across the five registered splits, detection
   paired.

## 6. What is NOT in this paper (fixed list)

- New detection features, new features, new threshold tuning.
- RUL prediction, in any form.
- Fault-source localization claims.
- E3 as a successful failure detector.
- Any change to production defaults or pre-registered numbers.
- NAB / SKAB / TEP as primary novelty.
- Post-hoc interpretation presented as pre-registered hypothesis.
