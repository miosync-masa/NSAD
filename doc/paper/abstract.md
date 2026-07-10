# Lambda³-NSAD — EAAI paper concept & abstract (v2, engineering pivot)

Working document for the journal submission. Target venue:
**Engineering Applications of Artificial Intelligence (EAAI)** (first
choice; alternates: Mechanical Systems and Signal Processing,
Reliability Engineering & System Safety — same manuscript spine,
different section weighting).

**This version supersedes the v1 concept** (NAB/SKAB/TEP-centered
"AI-ready sensor interpretation" framing; preserved verbatim in git
history and, as a drafted manuscript, in
[paper_draft.md](paper_draft.md), whose benchmark material becomes
this paper's Appendix). Outline:
[paper_v2_outline.md](paper_v2_outline.md). Claim–evidence
correspondence: [claim_evidence_map.md](claim_evidence_map.md).

---

## 1. Title candidates

**Primary (recommended):**

> Share the Geometry, Commission the Individual: Separating Healthy
> Individuality from Damage Severity in Deployable Bearing Anomaly
> Detection

**Alternative (conservative):**

> Transferable Damage-Severity Geometry with Asset-Specific Alarm
> Calibration: Pre-Registered Cross-Sectional and Longitudinal
> Validation of Normal-Structure Anomaly Detection

**Alternative (problem-first):**

> When Normal Individuals Differ: Why One-Class Support Widening
> Fails, and What Commissioning and Self-History Recover

## 2. Naming

Method name in the paper: **Lambda³-NSAD** (Normal-Structure Anomaly
Detection); released implementation Lambda³-NNNU, introduced once in
a supporting role, exactly as in v1.

## 3. Core claim (the central proposition)

> Generic one-class anomaly detection collapses normal variation
> between healthy individuals and damage-induced change into the same
> outlier score. Narrowing the normal support false-alarms on unseen
> healthy units; widening it absorbs shallow damage. We show, through
> five pre-registered experiments on physical machine data under one
> frozen detector configuration, that the resolution is a role
> separation: physical damage severity lives on a **transferable
> shared geometry** — order-preserving across bearing individuals and,
> in a registered confirmatory validation, across machine classes —
> the healthy alarm origin is a **per-individual commissioning
> quantity** (two scalars from ~64 s), and the failure alarm requires
> the **unit's own longitudinal history** — because cross-sectional
> calibration success does not imply longitudinal detection validity.

One-line form (fixed):

> **Share the geometry, commission the individual, and monitor
> degradation against its own history.**

Second fixed sentence:

> Physical damage severity was represented by a transferable
> geometry, whereas deployable failure alarms required an
> asset-specific longitudinal reference.

## 4. Contributions

Split deliberately into the AI contribution and the engineering
contribution, because EAAI reviews for both.

### AI contribution

- **A normal-structure anomaly framework that separates transferable
  severity geometry from asset-specific calibration and longitudinal
  reference.** The framework decides *which parts of learned
  normality are fleet property and which are individual property* —
  a question generic one-class formulations do not pose.
- **Severity margin and alarm decision designed as distinct
  statistical objects.** The severity margin is a non-saturating,
  cross-unit-comparable ordinal ruler; the alarm score is a
  FAR-controlled decision variable. Every pre-registered failure in
  this paper (#2 B/C/D, #4 H3L) is a measurement of what happens when
  one object is forced to do the other's job.
- **A deployment principle in place of support expansion**: shared
  geometry + per-individual commissioning + self-history reference,
  each layer licensed by a pre-registered success and bounded by a
  pre-registered failure of its neighbor.

### Engineering contribution

- **Cross-sectional order preservation of real damage extent** across
  bearing individuals: 12/12 ordered condition-pairs (inner 8/8,
  outer 4/4), zero reversals, Spearman ρ +0.845 / +0.866 (Paderborn,
  accelerated-lifetime damage).
- **Recovery of unseen-healthy-individual FAR by two-scalar
  commissioning**: median + IQR of the unit's own clean likelihood
  from ~64 s of healthy operation → FAR 0.10%, below the designed
  0.5% rate, at bit-identical severity.
- **Run-to-failure lead of 74–148 h at 93.5–99.6% persistence** with
  statistically progressive margins (occupancy ρ +0.90/+1.00/+0.95)
  on all three primary IMS failed bearings, from each unit's own
  early life.
- **Measured delay/silence of fleet-style healthy calibration reused
  as a failure alarm**: sustained onset +11–14% of life late on two
  bearings, silent on one — the negative result that bounds the
  commissioning win and, to our knowledge, is rarely measured at all.
- **A semantic separation of detection and localization** grounded in
  the same-shaft control finding: sensors observe the machine system;
  claiming the source bearing is a different inference task.
- **Cross-domain graded-severity extension (registered confirmatory
  validation, #5)**: on a cyclic hydraulic rig, cooler degradation
  grades map to 100%-detected, CI-separated ordered margins on 5/5
  registered splits, and valve margins order all three degradation
  stages (ρ +0.89…+0.93) even where mild-stage detection is absent —
  with the leak target killed by its own registered detection
  criterion and the accumulator's observability limit confirmed.

## 5. Abstract draft (~260 words)

> One-class anomaly detection for machine condition monitoring
> collapses two different sources of deviation — normal variation
> between healthy individuals of identical specification, and change
> caused by physical damage — into a single outlier score. A narrow
> normal support then raises false alarms on unseen healthy units,
> while a widened support absorbs shallow damage. We address the
> resulting deployment question — how to admit healthy individuality
> without losing damage severity or degradation progression — through
> five pre-registered experiments on physical machine corpora, under
> one frozen detector configuration, with implementations committed
> before results were read. First, on the Paderborn corpus, the
> physical extent of real accelerated-lifetime damage was
> order-preserved on a shared severity margin across bearing
> individuals (12/12 ordered condition-pairs, zero reversals,
> Spearman ρ +0.85/+0.87). Second, widening the shared support to
> cover unseen healthy units failed by pre-registered criteria: false
> alarms barely improved while up to 41% of shallowest-damage frames
> were absorbed. Third, two scalars per unit — the median and
> interquartile range of its own clean likelihood, estimated from
> about 64 seconds of healthy commissioning — restored the designed
> false-alarm rate on unseen healthy bearings (0.10%) at bit-identical
> severity. Fourth, on NASA IMS run-to-failure data, margins
> referenced to each unit's own early life were statistically
> progressive on all three failed bearings (alarm-occupancy
> ρ ≥ +0.90, lead times 74–148 h, persistence 93.5–99.6%), whereas
> reusing the fleet commissioning calibration as the failure alarm
> was 11–14% of life late, or silent. Fifth, a registered
> confirmatory validation on a cyclic hydraulic rig extended the
> graded-severity ordering to a second machine class (cooler and
> valve margins ordered with confidence intervals on all registered
> splits; the leak target failed its registered detection criterion
> and is reported as such). The resulting deployment
> principle — share the severity geometry, commission the individual,
> and monitor degradation against its own history — separates
> transferable damage severity from asset-specific alarm calibration.
> Generic benchmarks (NAB, SKAB, Tennessee Eastman) are retained as
> breadth checks in the appendix; fault localization is explicitly
> out of scope.

## 6. Contribution bullets (for the submission form / highlights)

- Real bearing-damage extent is order-preserved on a severity margin
  shared across healthy individuals (12/12 pairs, ρ +0.85/+0.87).
- Widening one-class normal support to cover unseen healthy units
  measurably absorbs shallow damage — a pre-registered negative
  result.
- ~64 s of healthy commissioning (two scalars: median + IQR of clean
  likelihood) restores designed false-alarm rate on unseen units at
  zero severity cost.
- Run-to-failure margins from a unit's own early life give 74–148 h
  lead at 93.5–99.6% persistence; fleet calibration reused as the
  failure alarm is 11–14% of life late or silent.
- Graded physical degradation on a cyclic hydraulic rig is
  order-preserved on the same margin (registered confirmatory
  validation; failures reported: leak killed, accumulator
  unobservable at this granularity).
- Deployment principle: share the geometry, commission the
  individual, monitor degradation against its own history; anomaly
  detection and fault localization are semantically separated.

## 7. Known review risks & mitigations

| Risk | Mitigation |
|---|---|
| "Only bearings / one rig per corpus" | Stated as a limitation up front; #5 extends the severity-geometry claim to a cyclic hydraulic rig (a second machine class, heterogeneous sensors) under registered statistics; the claim remains the role-separation principle, demonstrated end-to-end on the hardest public physical corpora available for it (known damage extent, graded degradation labels, run-to-failure); NAB/SKAB/TEP breadth checks retained in the appendix. |
| "#5 isn't a real pre-registration (exploration came first)" | Conceded in the plan itself (§0, full disclosure): it is a registered confirmatory validation. Its genuinely new elements — one fixed vocabulary, five fresh splits, CI/Spearman statistics, kill rules — produced one new positive (valve margin ordering) and one kill (leak split fragility) the exploration had missed, which is the argument for the protocol. |
| "Small n (3 failed bearings)" | Pre-registered kill thresholds were set for exactly this n; all verdicts quote them; no significance theater beyond registered CIs and Spearman tests. |
| "Commissioning idea is just normalization" | The E1 ladder is the answer: the *one-scalar* model was flat in sample size (registered diagnostic), and location+scale is validated against its own registered pass bar — then bounded by H3L, which shows where the same mechanism must not be used. The bound is as much the contribution as the win. |
| "Isn't the H3L result obvious?" | It is measured, pre-registered, and quantified (11–14% of life, or silence) — and its opposite (fleet calibration as a cheap failure alarm) is a live deployment temptation. Cross-sectional-success-⇏-longitudinal-validity is the paper's central proposition. |
| "Control bearings alarm too — your FAR is bad" | Reported as H4L finding, not hidden: same-shaft transmission means sensors observe the machine system. This grounds the detection/localization scope split; localization is declared unvalidated. |
| "Healthy FAR miss at t1-B3" | Disclosed in abstract-adjacent text and §5/§7: self-reference does not automatically give probability calibration (6.92% vs 0.5% design). |
| "Where is RUL?" | Explicitly out of scope by registered directive (#4 A1); the paper claims detection validity readouts (onset, occupancy, persistence, deepening), never remaining-life estimates. |
| "Milling result is weak" | Registered descriptive-only; median ρ +0.38 with 11/14 positive and one −0.82 reported without smoothing, as auxiliary evidence for continuous-wear tracking. |
| "Benchmark numbers no longer defended?" | They were never leaderboard claims (v1 legitimacy rule); they move to the appendix with their full protocol taxonomy intact. |
| "Post-hoc reinterpretation" | The ledger in claim_evidence_map.md separates registered verdicts from logged post-hoc refinements; #2 §8-B is cited as the in-house example of why post-hoc numbers carry no evidential weight. |

## 8. Limitations (for the honest paper — fixed list)

- Fault localization unvalidated; same-shaft propagation limits
  single-sensor attribution.
- One rig per corpus; three primary failed bearings; same-spec
  populations only.
- Healthy FAR at design rate from self-reference is not automatic
  (t1-B3: 6.92%).
- Milling wear tracking is heterogeneous across cutting conditions.
- Hydraulic (#5): leak detection is split-fragile at cycle-summary
  granularity (registered kill); accumulator unobservable at this
  sensor set; cooler healthy FAR at design on 1/5 splits only.
- Production commissioning API not implemented; repository defaults
  unchanged by all five pre-registrations.
- A commissioned unit's damage phase under its own scale on
  longitudinal fleet data remains untested.

## 9. Citation

```bibtex
@software{lambda3_nnnu_2026,
  title  = {Normal-Structure Anomaly Detection (Lambda³ NNNU): detecting deviation from mathematically structured normality without neural networks},
  author = {Iizumi, Masamichi},
  year   = {2026},
  url    = {https://github.com/miosync-masa/Lambda_inverse_problem},
  note   = {Based on Dr. Iizumi's Lambda³ Theory}
}
```
