# Pre-registered plan #5 — graded physical severity on a cyclic hydraulic rig

**Status: EXECUTED — results and verdicts in §7.** H1H cooler
SUPPORTED (100% detection, ordering + CI + ρ on 5/5 seeds; healthy-FAR
split variability disclosed); H2H valve SUPPORTED — the margin orders
valve severity (ρ +0.89…+0.93, 5/5) even where mild-stage detection is
absent; **H3H leak KILLED by its registered kill condition**
(severe-stage detection < 50% on 3/5 seeds — the single-split
exploration's 82/91% did not survive registered splits) while its
ordering statistics held; H4H accumulator observability-limit
expectation held 5/5. §§0–6 untouched since registration (plan frozen
at 2f78443, runner frozen at 7c6d054, both before any result was
read). Originally written 2026-07-10, committed
before the runner (`tests/hydraulic/exp_hydraulic_prereg.py`) was
implemented; the runner was committed before any result was read;
results are appended below §6, nothing above §7 edited afterward —
the discipline of plans #1–#4.

Successor-in-spirit to the post-freeze exploration
[hydraulic_exploration.md](../explorations/hydraulic_exploration.md),
whose closing line proposed exactly this: *"the hydraulic rig as a
second physical-label severity benchmark with pre-registered
hypotheses (margin↔stage ordering, target-conditional normality,
granularity, FAR-drift-as-coverage)."*

## 0. Relationship to the exploration (full disclosure)

The exploration already observed detection rates and median margins on
this dataset, including at the vocabulary fixed below. **This plan is
therefore a registered confirmatory validation, not a blind
pre-registration**, and the paper must cite it as such. What is
genuinely fixed-in-advance and previously uncomputed:

1. **One vocabulary for all four targets** (the exploration reported a
   granularity ladder; a per-target best pick would be
   damage-informed feature selection and is forbidden here);
2. **five fresh split seeds** (the exploration used seed 0; all
   registered splits differ from it);
3. **ordering statistics with uncertainty** — Spearman ρ and bootstrap
   CIs on adjacent-stage median differences, never computed in the
   exploration;
4. **pass/kill conditions** fixed before the run.

What this plan adds to the paper if supported: the severity-geometry
claim (Paderborn #1, vibration bearings) extended to a **second
machine class** — a cyclic hydraulic rig with heterogeneous sensors —
against **graded physical degradation labels**, within one asset
(per-asset mode). This is a within-asset severity validation; it tests
no cross-individual transfer (single rig — that axis belongs to #1–#3)
and nothing longitudinal (no run-to-failure — that axis belongs to #4).

**Data**: Condition Monitoring of Hydraulic Systems (ZeMA; Helwig,
Pignanelli & Schuetze 2015), UCI id 447, CC BY 4.0; 2205 constant
60-second load cycles, 17 sensors at 1/10/100 Hz; component conditions
varied on a grid — cooler efficiency 100/20/3%, valve switching
behavior 100/90/80/73%, internal pump leakage 0/1/2, accumulator
pre-charge 130/115/100/90 bar — plus a stable-conditions flag.
Obtained via the Machine-Learning-FGA/Hydraulic-systems GitHub mirror
(files identical to the UCI archive); `HYDRAULIC/` is gitignored.

## 1. Fixed protocol (frozen before implementation)

- **Vocabulary (identical for all targets, all hypotheses)**:
  `phase12shape`, d = 272 — the promoted two-layer cycle vocabulary
  (12-bin normalized-phase magnitude profile + generic timing features
  `peak_pos` / `trough_pos` / `rise_time` / `settle_time`, per sensor;
  `lambda3_detector.features.extractor.extract_cycle_phase_features`).
  Fault-agnostic: nothing aligned to any component; the circular-shift
  mechanism behind the timing features is unit-tested
  (`tests/core/test_cycle_phase.py`).
- **Detector**: the frozen support-floor path, UNCHANGED — z-norm on
  the fit split → PCA 90% variance (the d > 16 guardrail) → GMM with
  BIC auto-K (full covariance) → nested out-of-sample 0.5% likelihood
  floor. Margin = (floor − ll) / |fit-side IQR|; margin > 0 = outside
  the floor. Identical mechanics to the exploration
  (`tests/hydraulic/exp_hydraulic.build_floor`), reused by import.
- **Normality per target** (the structural fact of this rig: only 10
  of 2205 cycles are all-nominal): normal = cycles with the TARGET
  component nominal and stable flag 0; the other three components vary
  freely inside the normal set — operating conditions the regime layer
  must absorb. Degraded = cycles at each labeled stage of the target
  (same stability filter). `tests/hydraulic/hydraulic_datasets.target_split`,
  unchanged.
- **Splits**: per seed, a permutation of the normal set; first 60% =
  fit, rest = healthy holdout. **Seeds fixed: {1, 2, 3, 4, 5}** (the
  exploration's seed 0 is deliberately excluded). Every quantity is
  reported per seed.
- **Decision rule over seeds (fixed)**: a pass criterion HOLDS if it
  is satisfied on ≥ 4 of 5 seeds; a kill event FIRES if it occurs on
  ≥ 2 of 5 seeds.
- **Statistics (fixed)**: Spearman ρ computed over pooled per-cycle
  (stage rank, margin) pairs of the degraded cycles; adjacent-stage
  median-difference CIs by percentile bootstrap, 10,000 resamples.
- **Pairing law**: every FAR is reported with detection from the same
  run; every detection with its FAR. (Standing rule of #1–#4.)
- **Legitimacy**: component-condition labels are used only to (a)
  define target-nominal construction sets (operational metadata, as
  Paderborn's operating-condition labels) and (b) final scoring. No
  quantity is tuned against degraded outcomes; no constant of the
  detector or vocabulary may be revised after the first run.
- Production defaults unchanged regardless of outcome.

## 2. Hypotheses (pass / kill fixed before execution)

**H1H — cooler: graded-severity ordering (primary).** Construction on
cooler-nominal cycles; stages 20% (mild), 3% (severe).
*Pass*: (a) detection ≥ 95% at both stages; (b) median margin ordered
med(3%) > med(20%) > 0 with the adjacent-stage bootstrap CI excluding
0; (c) Spearman ρ(stage rank, margin) > 0 — each holding on ≥ 4/5
seeds. Held-out healthy FAR reported paired, with distance to the
designed 0.5% rate.
*Kill*: ordering reversed (med(3%) < med(20%)) with CI excluding 0 on
≥ 2/5 seeds, or detection < 95% at either stage on ≥ 2/5 seeds.

**H2H — valve: timing-severity margin ordering (the open question).**
The exploration measured valve *detection* at this vocabulary
(severe-only) but never its margins. Stages 90/80/73%.
*Pass*: (a) Spearman ρ > 0; (b) med(73%) − med(90%) bootstrap CI
excluding 0 from above; (c) detection at the severe stage (73%)
≥ 50% — each on ≥ 4/5 seeds. Registered expectation, disclosed: the
mild stages (90/80%) are likely near or below the floor at
cycle-summary granularity (the granularity limitation); their low
detection does NOT kill.
*Kill*: detection(73%) < 50% on ≥ 2/5 seeds, or med(73%) < med(90%)
with CI excluding 0 on ≥ 2/5 seeds.

**H3H — leak: profile-severity ordering + FAR-drift as coverage
measurement.** Stages 1 (weak), 2 (severe).
*Pass*: (a) detection ≥ 50% at both stages; (b) med(2) > med(1) with
CI excluding 0; (c) ρ > 0 — each on ≥ 4/5 seeds.
*Registered coverage measurement (not a kill)*: the held-out healthy
FAR for the leak-nominal pool is expected to drift above design
(exploration: 3.6–4.1% across every vocabulary — normal-pool
heterogeneity beyond the fitted structure). It is reported paired and
as-is; if it instead lands ≤ 2× design, that contradicts the
exploration's coverage finding and is reported prominently either way.
*Kill*: ordering reversed with CI excluding 0 on ≥ 2/5 seeds, or
detection(stage 2) < 50% on ≥ 2/5 seeds.

**H4H — accumulator: registered observability limit (descriptive, no
kill).** Registered expectation: detection < 50% at every stage and
median margins ≤ 0 at this granularity — the exploration's
"representation-level observability limit of this sensor set" claim,
now on the record before the run. If instead any stage reaches ≥ 50%
detection on ≥ 4/5 seeds, the limit claim is withdrawn and the
detection reported. Either way: descriptive, reported in full.

## 3. Primary evaluations

1. Per target × seed: held-out healthy FAR paired with per-stage
   detection and median margin (IQR units) — one table, all seeds.
2. Ordering statistics per target × seed: Spearman ρ; adjacent-stage
   median differences with bootstrap 95% CIs.
3. Verdicts per hypothesis against §2, with the ≥ 4/5 / ≥ 2/5 rule.
4. Audit: one vocabulary, one detector configuration, zero constants
   changed; confirmed in the results section.

## 4. What this plan may NOT claim (fixed)

- No cross-individual transfer (single rig).
- No longitudinal/degradation-progression claim (condition grid, not
  run-to-failure).
- No fault localization (the four targets are *defined* by the label
  grid; nothing is inferred about spatial source).
- No RUL.
- No claim that the vocabulary is optimal — it is the promoted
  fault-agnostic default, fixed for comparability.

## 5. Execution discipline

Plan committed (this document, §§0–6) → runner
`tests/hydraulic/exp_hydraulic_prereg.py` implemented and committed
**before any result is read** → single run
(`python -m tests.hydraulic.exp_hydraulic_prereg`) → results appended
as §7, nothing above edited → verdicts SUPPORTED / KILLED /
INCONCLUSIVE per hypothesis. Post-hoc analyses, if any, in a separate
marked section.

## 6. Registered interpretation map (fixed before the run)

| Outcome | Reading in the paper |
|---|---|
| H1H supported | The graded-severity geometry claim extends to a second machine class against physical labels — within-asset, registered statistics |
| H1H killed | The cooler exploration result does not survive registered statistics/splits; the severity-geometry claim stays bearings-only |
| H2H supported | The timing vocabulary carries valve severity ordering in the margin even where mild-stage detection is absent — severity and alarm decoupled again |
| H2H killed | Valve severity is not represented at this granularity; granularity limitation stands unsoftened |
| H3H supported + FAR drift confirmed | Ordering and coverage are separate properties: the margin can order severity while the healthy pool outruns the fitted support — the #1 H3 lesson, within-asset |
| H4H expectation held | Observability limit registered and confirmed; reported as a limitation of the sensor set/granularity, not a detector property |

---

## 7. Execution results (run 2026-07-10; nothing above this section edited after the run)

Implementation: `tests/hydraulic/exp_hydraulic_prereg.py`, frozen at
7c6d054 before these results were read (plan frozen at 2f78443).
Command: `python -m tests.hydraulic.exp_hydraulic_prereg`. Vocabulary
phase12shape d=272; seeds {1–5}; 10,000-resample bootstrap CIs.

### Per-target × per-seed table (FAR always paired with detection)

**cooler** (stages 20% → 3%):

| seed | K | healthy FAR | det 20% / 3% | med 20% / 3% (IQR) | ρ | adj CI (3%−20%) |
|---|---|---:|---|---|---:|---|
| 1 | 2 | 0.51% | 100.0% / 100.0% | +2140.5 / +2559.9 | +0.488 | [+344.9, +493.8] |
| 2 | 2 | 1.02% | 100.0% / 100.0% | +953.3 / +4463.1 | +0.866 | [+3445.4, +3569.2] |
| 3 | 2 | 2.04% | 100.0% / 100.0% | +1124.2 / +1777.2 | +0.862 | [+624.6, +679.0] |
| 4 | 1 | 5.61% | 100.0% / 100.0% | +468.8 / +1799.4 | +0.866 | [+1249.3, +1441.9] |
| 5 | 2 | 1.02% | 100.0% / 100.0% | +2162.5 / +9150.6 | +0.866 | [+6906.9, +7056.8] |

**valve** (stages 90% → 80% → 73%):

| seed | K | healthy FAR | det 90/80/73% | med 90/80/73% (IQR) | ρ | adj CIs |
|---|---|---:|---|---|---:|---|
| 1 | 1 | 0.68% | 2.2% / 1.4% / 100.0% | −10.2 / −5.9 / +9.4 | +0.925 | [+4.0,+4.6] [+14.7,+15.8] |
| 2 | 1 | 3.38% | 2.8% / 79.7% / 100.0% | −2.7 / +1.0 / +12.6 | +0.915 | [+3.4,+3.9] [+11.3,+11.9] |
| 3 | 1 | 0.68% | 1.4% / 0.6% / 4.7% | −14.9 / −12.6 / −3.8 | +0.890 | [+2.1,+2.6] [+8.4,+9.0] |
| 4 | 1 | 0.00% | 1.4% / 0.8% / 79.7% | −6.9 / −5.3 / +1.2 | +0.891 | [+1.4,+1.8] [+6.2,+6.7] |
| 5 | 1 | 0.68% | 1.4% / 1.1% / 96.7% | −9.9 / −6.9 / +4.5 | +0.906 | [+2.7,+3.3] [+10.9,+11.9] |

**leak** (stages 1 → 2):

| seed | K | healthy FAR | det 1 / 2 | med 1 / 2 (IQR) | ρ | adj CI (2−1) |
|---|---|---:|---|---|---:|---|
| 1 | 3 | 2.04% | 45.2% / 77.3% | −0.3 / +2.1 | +0.456 | [+1.8, +2.9] |
| 2 | 1 | 3.06% | 22.3% / 25.2% | −2.9 / −2.9 | +0.030 | [−0.2, +0.2] |
| 3 | 3 | 1.02% | 51.0% / 81.0% | +0.1 / +4.3 | +0.386 | [+3.5, +4.9] |
| 4 | 2 | 2.55% | 23.5% / 45.6% | −3.1 / −0.5 | +0.162 | [+2.2, +3.2] |
| 5 | 3 | 2.04% | 16.0% / 27.1% | −5.5 / −2.6 | +0.388 | [+2.3, +3.2] |

**accumulator** (stages 115 → 100 → 90 bar): healthy FAR 0.00–3.47%;
detection 16.0–26.7% at every stage on every seed; medians −25.0 …
−2.1 (all ≤ 0, near-identical across stages); ρ +0.029 … +0.074; all
adjacent CIs straddle 0.

### Verdicts (against §2; pass ≥ 4/5 seeds, kill ≥ 2/5 seeds)

- **H1H — SUPPORTED.** Detection ≥ 95% at both stages: 5/5. Ordering
  med(3%) > med(20%) > 0 with adjacent CI excluding 0: 5/5. ρ > 0:
  5/5. Reversal kill fired 0/5. **Disclosed with it (registered
  reporting duty)**: held-out healthy FAR reaches design on 1 of 5
  seeds only (0.51 / 1.02 / 2.04 / 5.61 / 1.02%; median 1.02% vs
  designed 0.5%); the worst seed (5.61%, 11× design) is the one where
  BIC collapsed to K = 1. Healthy FAR at design rate from a single
  split is not automatic — the IMS H2L-b lesson recurring on a second
  rig.
- **H2H — SUPPORTED (the registered open question, answered).** ρ > 0:
  5/5 (+0.890 … +0.925). med(73%) > med(90%) with CI excluding 0: 5/5.
  Severe-stage detection ≥ 50%: 4/5. Kill conditions fired 0/5 (the
  seed-3 detection drop, 4.7%, occurs on 1 seed — below the ≥ 2/5 kill
  bar — and is disclosed as split sensitivity). The registered
  expectation held: mild stages (90/80%) sit at floor-level detection
  (0.6–2.8%, one seed-2 exception at 79.7%) **while the margin orders
  all three stages on every seed** — severity representation and alarm
  decision decoupled again, this time on timing geometry.
- **H3H — KILLED, by its registered kill condition.** Severe-stage
  detection < 50% on 3 of 5 seeds (25.2 / 45.6 / 27.1%) — ≥ 2/5, kill
  fires. For completeness under the pairing law: the ordering
  statistics largely held (ordered + CI 4/5; ρ > 0 5/5, though weakly,
  +0.03 … +0.46), and no reversal occurred. **The single-split
  exploration's 82/91% leak detection did not survive registered
  multi-seed splits** — precisely the fragility this plan's split
  protocol existed to expose. Registered coverage measurement: healthy
  FAR 2.04 / 3.06 / 1.02 / 2.55 / 2.04% (2–6× design) — the FAR-drift
  coverage finding confirmed on fresh splits (exploration: 3.6–4.1%).
- **H4H — expectation held, 5/5.** Detection < 50% and median ≤ 0 at
  every stage on every seed; ρ ≈ 0. The observability limit of this
  sensor set at cycle-summary granularity is now a registered,
  confirmed negative — a property of the representation, not a
  detector failure claim.

Audit (§3-4): one vocabulary, one detector configuration, zero
constants changed between targets or seeds.

### Reading

The graded-severity geometry claim extends to a second machine class
under registered statistics: on a cyclic hydraulic rig, physical
degradation grade maps to ordered, CI-separated severity margins for
the two targets whose faults the fault-agnostic vocabulary can see
(cooler: magnitude profile; valve: timing geometry) — with valve
showing the sharpest form of the paper's role separation, ordering
present in the margin at stages the alarm cannot yet detect. The two
negatives are equally load-bearing: leak detection is split-fragile at
this granularity (H3H killed — a single lucky split had overstated
it), and the accumulator is confirmed unobservable at this sensor
set/granularity. Healthy-FAR-at-design remains the recurring honest
gap across rigs (#4 t1-B3; cooler seed 4 here).

### Standing limitations

- Single rig: no cross-individual claim; condition grid, not
  run-to-failure: no longitudinal claim (registered scope, §4).
- Registered confirmatory validation, not a blind pre-registration
  (§0): cooler/accumulator outcomes confirm exploration observations
  under fixed protocol; the valve margin ordering and the leak kill
  are the genuinely new findings.
- Healthy FAR split variability (cooler 0.51–5.61%) is disclosed but
  unexplained beyond the K-collapse correlate; per-split floor
  stability is future work.
- Production defaults unchanged.
