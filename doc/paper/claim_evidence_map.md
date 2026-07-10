# Claim–evidence map — the five pre-registrations

Companion table for the pivoted manuscript
([paper_v2_outline.md](paper_v2_outline.md)). For every claim the
paper is allowed to make, this file names the pre-registered
hypothesis that grounds it, the verdict, the key numbers, and where
the evidence lives (document section, runner script, freeze/results
commits). **Nothing here re-runs, re-judges, or re-tunes anything**:
verdicts and numbers are quoted verbatim from the executed plans, and
pre-registered results are strictly separated from post-hoc
interpretation (final section).

Provenance discipline: each plan's implementation was frozen in a
commit **before** its results were read (freeze SHA precedes results
SHA in git history for #2, #3, #4; #1's plan was fixed at 332b1d2 and
its results recorded at 088bc8e).

| # | Plan (doc) | Runner | Freeze / provenance |
|---|---|---|---|
| 1 | [experiment_plan_paderborn.md](../preregistrations/experiment_plan_paderborn.md) | `python -m tests.paderborn.exp_paderborn_full` | plan fixed 332b1d2 · results 088bc8e |
| 2 | [experiment_plan_paderborn2.md](../preregistrations/experiment_plan_paderborn2.md) | `python -m tests.paderborn.exp_paderborn2` | impl frozen 8ea1a9d before results |
| 3 | [experiment_plan_paderborn3.md](../preregistrations/experiment_plan_paderborn3.md) | `python -m tests.paderborn.exp_paderborn3` | impl frozen c61f061 before results |
| 4 | [experiment_plan_ims.md](../preregistrations/experiment_plan_ims.md) | `python -m tests.ims.exp_ims` | impl frozen b387a4f before results |
| 5 | [experiment_plan_hydraulic.md](../preregistrations/experiment_plan_hydraulic.md) | `python -m tests.hydraulic.exp_hydraulic_prereg` | plan frozen 2f78443 · impl frozen 7c6d054 before results |

---

## Pillar 1 — Shareable severity geometry (cross-sectional)

**Manuscript claim**: *the geometry representing physical damage
depth can be shared across bearing individuals of the same
specification.*

| Item | Content |
|---|---|
| Pre-registered hypothesis | #1 H1 — physical severity ordering on the real-pitting ladders, per operating condition, with kill condition (adjacent pair reversed, CI excluding 0, in ≥2 of 4 conditions) |
| Verdict | **SUPPORTED** — 12 of 12 condition × adjacent-pair tests ordered (inner 8/8, outer 4/4), **zero reversals** |
| Key numbers | Spearman ρ(extent, per-bearing median margin) = **+0.845 inner / +0.866 outer**; adjacent-group CIs exclude 0; KB24 (combined, extent 3) deepest at +92.7 |
| Disclosed noise floor | extent-1 medians span −0.2 (KI14) to +17.2 (KI04) — the ladder stands on group medians, not on every individual |
| Scope (registered wording) | cross-sectional, same-spec, cross-bearing; **not** a longitudinal same-bearing degradation track |
| Evidence | experiment_plan_paderborn.md §5-H1 |

## Pillar 2 — Widening the population support fails (cross-sectional)

**Manuscript claim**: *healthy between-individual variation must not
be absorbed as thickness of the shared normal support: FAR barely
improves and shallow damage is swallowed.*

| Item | Content |
|---|---|
| Pre-registered hypotheses | #1 H3 (flat pooled support transfers designed FAR to unseen healthy bearings); #2 candidates A (global floor), B (component-conditional floor), C (condition-conditional floor), D (hierarchical population envelope) |
| Verdicts | #1 H3 **KILLED** by its own kill condition; #2 **A/B/C/D all KILLED** |
| Key numbers | #1: unseen-bearing FAR mean **42.06%** (folds 66.37/0.00/59.80%) vs 4% kill bar; construction curve 99.96 → 98.63 → 66.37% (1→2→4 bearings). #2 (FAR mean / det_all / extent-1 absorption): A 43.1% / 81.5% / 11.9%; B 42.9% / 68.1% / **41.1%** + one ordering pair lost (7/8); C 46.9% / 74.7% / 22.4%; D 44.8% / 63.5% / 35.5% |
| What was rejected (registered wording) | the flat pooled-support **implementation** and its widened variants — not population normality in principle; the healthy population's between-bearing tolerance layer is unrepresented |
| Evidence | experiment_plan_paderborn.md §5-H3; experiment_plan_paderborn2.md §8 |

## Pillar 3 — Healthy commissioning restores the alarm origin (cross-sectional)

**Manuscript claim**: *two scalars per unit — the median and IQR of
its own clean likelihood, from ~64 s of healthy commissioning —
recover the designed false-alarm rate on unseen healthy bearings at
zero severity cost.* Role-bounded: **healthy admission calibration,
never the failure alarm** (see Pillar 4).

| Item | Content |
|---|---|
| Pre-registered hypotheses | #2 E (one-scalar commissioning offset); #3 E0–E4 (alarm-side-only candidates on a fixed severity geometry) |
| Verdicts | #2 E **INCONCLUSIVE, direction strongly positive** (FAR 43.1% → 14.1%, missed the < 2% bar); #3 **E0 KILLED** (16.15%), **E1 ladder flat** — registered diagnostic fired: the offset *model*, not sample size, is binding (15.3% at 1 recording → 14.75% at 12), **E2 KILLED** (13.77%/12.43%), **E3 SUPPORTED**, **E4 SUPPORTED** |
| Key numbers | E3: unseen-healthy FAR **0.10%** (n=4 recordings/condition; ~64 s total) / 0.29% (n=8) — below the 2% pass bar **and below the designed 0.5% rate**; E4: 0.88% (n=4) / 0.13% (n=8) |
| Severity audit | **bit-identical** to shared-geometry reference by construction, verified: H1 12/12 (inner 8/8 ρ+0.85, outer 4/4 ρ+0.87), det_all 81.5%, severity-side extent-1 absorption 11.9% |
| Registered standing limitation | cross-sectional data cannot test a commissioned unit's damage phase under its own scale — the question #4 was registered to answer |
| Evidence | experiment_plan_paderborn2.md §8-E; experiment_plan_paderborn3.md §7 |

## Pillar 4 — Longitudinal degradation needs the unit's own history

**Manuscript claim (positive half)**: *a margin built from the unit's
own early normal life is statistically progressive on real
run-to-failure degradation, with useful lead and high persistence.*

**Manuscript claim (negative half, the bound on Pillar 3)**:
*cross-sectional calibration success does not imply longitudinal
detection validity — the fleet E3 calibration reused as the failure
alarm is 11–14% of life late, or silent.*

| Item | Content |
|---|---|
| Pre-registered hypotheses | #4 H1L (statistical progressiveness: EOL-vs-healthy CI, occupancy Spearman, Q5-vs-Q1 deepening), H2L (sustained onset + healthy-phase FAR, paired), H3L (E3 scale-compression risk, kill at >1% of life delay on ≥2 of 3), H4L (same-shaft controls, no kill), M (milling, descriptive) |
| Verdicts | **H1L SUPPORTED 3/3**; **H2L supported at 1/3 failures** (split below); **H3L KILLED 3/3 — the headline**; H4L finding; M descriptive |
| H1L numbers | occupancy ρ **+0.90 / +1.00 / +0.95** (t1-B3 / t1-B4 / t2-B1); EOL-vs-healthy CIs [+20.1,+26.4] / [+56.6,+58.7] / [+390.8,+519.2] IQR; t2-B1 reaches +463 IQR at end of life |
| H2L numbers | sustained onset on all 3 failed bearings; **leads 74–148 h**; **persistence 93.5–99.6%**; healthy-phase FAR 6.92% / 1.08% / 1.52% |
| H2L split (post-execution, presentational; registered verdict stands) | H2L-a early persistent detection: supported 3/3 · H2L-b design-rate healthy FAR from self-reference: **NOT universally supported** — t1-B3's 6.92% (13.8× design) is a genuine healthy false-alarm rate, occupancy-verified, not early onset |
| H3L numbers | E3 fleet margin delays sustained onset **+13.96% of life** (t1-B3), **misses onset entirely** (t1-B4), delays **+11.18% of life** (t2-B1). Disclosed design note: the statistic bundles reference-geometry mismatch and personal-scale compression; decomposition is future work |
| H4L numbers | every same-shaft control shows late-life sustained onset at high persistence (t2 controls: onset 71–79% of life, persistence 97–100%, healthy FAR 0.1–3.9%) — read as shared-shaft vibration transmission; grounds the detection-vs-localization scope split |
| M numbers | ρ(margin, flank wear VB) **median +0.38** over 14 cases; 11/14 positive (up to +0.92), two near zero, one strongly negative (case 12, −0.82) — reported without smoothing |
| Evidence | experiment_plan_ims.md §4 (results), §5 (interpretive refinement, logged) |

## Pillar 1 extension — graded severity on a second machine class (#5)

**Manuscript claim**: *the graded-severity geometry extends beyond
bearings: on a cyclic hydraulic rig, physical degradation grade maps
to ordered, CI-separated severity margins for the targets the
fault-agnostic vocabulary can observe — and the margin can order
severity even at stages the alarm cannot yet detect.*

Disclosure carried with the claim (registered in #5 §0): #5 is a
**registered confirmatory validation**, not a blind pre-registration —
the post-freeze exploration had observed related quantities; the
registered-novel elements are the single fixed vocabulary, five fresh
split seeds, ordering statistics with CIs, and the pass/kill rules.

| Item | Content |
|---|---|
| Pre-registered hypotheses | #5 H1H (cooler ordering, primary), H2H (valve margin ordering — the open question), H3H (leak ordering + FAR-drift coverage), H4H (accumulator observability limit, descriptive) |
| Verdicts | **H1H SUPPORTED** (5/5 on all three criteria); **H2H SUPPORTED** (ρ +0.890…+0.925, CIs excluding 0, 5/5); **H3H KILLED by its registered kill** (severe-stage detection < 50% on 3/5 seeds); H4H expectation held 5/5 |
| Key numbers | cooler det 100%/100% on every seed, med(3%) > med(20%) CI-separated; valve margins ordered on every seed while mild stages sit at floor-level detection (0.6–2.8%) — severity/alarm decoupling on timing geometry; leak healthy FAR 1.02–3.06% (2–6× design, coverage finding confirmed) |
| Honest bounds | cooler healthy FAR at design on only 1/5 seeds (0.51–5.61%, worst seed = BIC K-collapse); the exploration's single-split leak detection (82/91%) did not survive registered splits |
| Scope (registered §4) | within-asset, single rig — no cross-individual transfer, no longitudinal claim, no localization, no RUL |
| Evidence | experiment_plan_hydraulic.md §7 |

---

## Failure and limitation registry (all retained in the manuscript)

Everything below appears in the paper — as results, bounds, or
limitations — never silently dropped.

| Item | Where it lives | Manuscript placement |
|---|---|---|
| #1 H2 killed on purity (62.5% < 70%), with the disclosed confound (66% of frames out-of-support, so regime assignment is extrapolation) | experiment_plan_paderborn.md §5-H2 | §4 (cross-sectional validation), stated with confound |
| #1 H3 / #2 A–D: support widening fails; B loses an ordering pair and absorbs 41% of extent-1 | plans #1 §5, #2 §8 | §4 — a load-bearing negative result, not a footnote |
| #2 E missed its own pass bar (14.1% ≫ 2%) — INCONCLUSIVE, not supported | plan #2 §8 | §4 — kept as the step that motivated #3 |
| #3 E1 ladder flat: the scalar-offset model, not sample size, was binding | plan #3 §7 | §4 — the registered diagnostic |
| #4 H2L-b: t1-B3 healthy FAR 6.92% (13.8× design) — self-reference does not guarantee probability calibration | plan #4 §4/§5 | §5 + §7 Limitations |
| #4 H3L killed 3/3: fleet E3 as failure alarm late or silent | plan #4 §4 | §5 — a central result of the paper |
| #4 H4L: same-shaft controls show late-life onsets — NOT deleted as false alarms; read as system-level vibration transmission | plan #4 §4/§5 | §5 finding + §7 (localization unvalidated) |
| Milling heterogeneity (median ρ +0.38; one case −0.82) | plan #4 §4-M | §5 auxiliary/descriptive + §7 |
| Fault localization: which bearing/component is the source — never claimed, separate spatial-inference task | plan #4 §5 | §7 Limitations / future work |
| Test 3 (IMS) registered descriptive-only; its B4 control at 16.2% healthy FAR disclosed as-is | plan #4 §1/§4 | §5, descriptive |
| Test-rig scope: one rig per corpus, small failed-bearing counts (3 primary), same-spec bearings | plans #1–#4 | §7 Limitations |
| Commissioned unit's damage phase under its own scale on longitudinal **fleet** data — untested | plan #3 §7 / principles doc | §7 / future work |
| Production commissioning API not implemented; production defaults unchanged by all four plans | every plan's §1 | §7 — no unimplemented feature is claimed as a result |
| No RUL prediction anywhere (registered directive, #4 A1; #5 §4) | plan #4 A1, plan #5 §4 | scope statement in §1 and §5 |
| #5 H3H killed: leak severe-stage detection < 50% on 3/5 seeds — the exploration's single-split 82/91% overstated it | plan #5 §7 | §4 — split fragility as a registered finding |
| #5 cooler healthy FAR at design on 1/5 seeds only (0.51–5.61%; worst = BIC K-collapse) | plan #5 §7 | §4 + §7 Limitations (recurring healthy-FAR gap, with #4 t1-B3) |
| #5 accumulator: registered observability limit confirmed 5/5 (representation property, not detector claim) | plan #5 §7 | §7 Limitations |
| #5 is a registered confirmatory validation, not blind (exploration preceded it) | plan #5 §0 | disclosed wherever #5 is cited |

## Pre-registered vs post-hoc — the ledger

Pre-registered verdicts (quotable as confirmatory evidence): #1 H1,
H2, H3, H5; #2 A–E; #3 E0–E4 with the E1-ladder diagnostic; #4 H1L,
H2L, H3L, H4L, M; #5 H1H–H4H (with the §0 disclosure: registered
confirmatory validation — the exploration preceded it, so #5's
previously-observed quantities are protocol-fixed replications, while
the valve margin ordering and the leak kill are new findings).
Post-hoc / interpretive material (quotable only as
interpretation, and labeled as such in the manuscript):

- #1 §6 post-hoc analyses (component-conditional floor, hard-partition
  refutation, regime-semantics measurement) and §7 conceptual model
  (healthy envelope, three meanings of "regime") — motivated #2's
  candidates; carried **no evidential weight** there, and #2 §8-B
  showed why (the post-hoc component-floor optimism did not survive
  the registered protocol).
- #4 §5 interpretive refinement (H2L-a/b split; H3L restated as
  "cross-sectional calibration success does not imply longitudinal
  detection validity"; H4L detection-vs-localization semantics) —
  logged post-execution, verdicts and numbers unchanged.
- [nsad_deployment_principles.md](../preregistrations/nsad_deployment_principles.md) —
  the synthesis document; every sentence there is traceable to a
  registered verdict above.
