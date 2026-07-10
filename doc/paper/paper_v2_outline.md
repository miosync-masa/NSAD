# Paper v2 outline — the engineering pivot

Target venue: **Engineering Applications of Artificial Intelligence
(EAAI)** (first choice). This document is the working outline of the
pivoted manuscript. It supersedes the v1 draft
([paper_draft.md](paper_draft.md)) **as the main line only**: the v1
draft is complete, its numbers are unchanged, and its NAB / SKAB / TEP
material becomes the Appendix of this paper (migration plan below).
Concept, abstract, and contribution bullets: [abstract.md](abstract.md).
Claim–evidence correspondence: [claim_evidence_map.md](claim_evidence_map.md).

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

---

## 1. The central problem

Generic one-class anomaly detection collapses two different sources
of deviation into the same outlier score: **normal variation between
healthy individuals** of identical specification, and **change caused
by physical damage**. The consequence is a dilemma with no tuning
escape: a narrow normal support false-alarms on unseen healthy units
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

> Physical damage severity was represented by a transferable
> geometry, whereas deployable failure alarms required an
> asset-specific longitudinal reference.

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
- The deployment question (§1 above) and the three-layer answer,
  previewed.
- Contribution summary: the AI contribution / engineering
  contribution split (abstract.md §4).
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

### §3 Generic qualification (short)
- One compact subsection summarizing NAB (unknown channel 85% @
  0.56% FP; combined 96.3%), SKAB (100% @ 382/10k), TEP (K=1
  degeneration to Hotelling T²; SPE/T² identities) — as breadth
  checks only, with the verbatim framing sentence of §3 above.
- Everything else (protocol taxonomy, baselines, duel, transfer
  test, cost tables) → Appendix.

### §4 Cross-sectional engineering validation (Paderborn #1–#3)
- Corpus and ground truth: real accelerated-lifetime damage with
  known physical extent; six healthy individuals.
- **Shared severity** (#1 H1): 12/12 ordered pairs, zero reversals,
  ρ +0.845/+0.866; identity-noise floor disclosed.
- **Support expansion failure** (#1 H3, #2 A–D): the FAR/absorption
  table; B's lost ordering pair; the registered kill conditions doing
  their job.
- **Two-scalar commissioning** (#2 E → #3 E3): the E1-ladder
  diagnostic (model, not sample size); E3 at 0.10% FAR from ~64 s;
  severity audit bit-identical. Role bound stated immediately:
  healthy admission calibration, not a failure alarm.
- #1 H2 (condition-as-regime purity) reported killed, with its
  confound.
- **Cross-domain graded severity (#5, hydraulic rig)** — closing
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
- **Statistical progressiveness** (H1L 3/3): occupancy ρ, EOL
  deepening CIs, up to +463 IQR.
- **Lead time / persistence / healthy FAR** (H2L, split reading):
  74–148 h leads at 93.5–99.6% persistence; the t1-B3 6.92%
  healthy-FAR miss reported as a genuine miss.
- **Fleet calibration fails in the damage phase** (H3L killed 3/3):
  +13.96% / silent / +11.18% of life — the bound on §4's
  commissioning win; the bundling disclosure (geometry mismatch +
  scale compression).
- **Same-shaft control finding** (H4L): late-life onsets on
  non-failed bearings; the detection-vs-localization scope split.
- Milling as auxiliary/descriptive: margin vs continuous wear,
  median ρ +0.38, heterogeneity included.

### §6 Deployment principle
- The three-layer shape (fleet geometry → healthy admission
  commissioning → per-asset longitudinal monitoring), each layer
  carrying the pre-registered result that licenses it *and* the
  pre-registered failure that forbids its neighbor's job.
- Severity margin vs alarm score as distinct deliverables.
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
sections to the Appendix. Main-text figure candidates — all derivable
from the already-executed #1–#4 runs' outputs, no new measurement:

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
