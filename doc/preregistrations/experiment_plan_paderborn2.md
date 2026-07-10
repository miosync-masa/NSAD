# Pre-registered plan #2 — hierarchical normal structure on the Paderborn healthy population

**Status: EXECUTED — results and verdicts in §8** (A/B/C/D KILLED,
E INCONCLUSIVE with strongly positive direction: FAR 43%→14% at zero
severity cost). §§0–7 untouched since pre-registration. Successor to
[experiment_plan_paderborn.md](experiment_plan_paderborn.md) (whose
§5–§7 record the executed validation and its conceptual model).
Written 2026-07-10, before any candidate below has been run under this
protocol. The post-hoc §6 measurements of the predecessor (component-
conditional floor: FAR 51.2%; hard partition: H1 destroyed) motivated
the candidate set but are exploratory and carry no evidential weight
here.

## 0. Purpose

Test whether the normal population envelope formed by the six healthy
bearings — the between-bearing **normal tolerance layer** of §7 of the
predecessor — can be represented **without swallowing damage
severity**. The target quantity is δ (damage displacement), never
b(i) (healthy between-bearing offset):

```
x(i, c, t) = μ(c) + b(i) + ε(i, c, t) + δ(i, c, t)
```

## 1. Fixed elements (unchanged, non-negotiable)

- Adapter: Paderborn d=27 vocabulary
  (`tests/paderborn/paderborn_datasets.py`), no fault-frequency alignment, no
  feature selection by damage labels, no modification.
- NSAD core, three-state semantics, severity-margin non-saturation.
- Splits: by recording, healthy holdout by bearing (rotating folds
  over K001–K006 as in H3 of the predecessor).
- Legitimacy rule: damage labels only for final scoring; operating-
  condition labels are permissible operational metadata; bearing
  identity of construction units is permissible commissioning
  metadata; NO quantity may be tuned against damage outcomes.
- Current repository defaults remain unchanged regardless of outcome;
  any promotion is a separate, logged decision after this plan runs.

## 2. Candidates

| ID | Description | Constraint |
|---|---|---|
| A | current global floor (baseline) | as executed |
| B | component-conditional support floor | pooled geometry; floors per mixture component |
| C | shared geometry + known-condition conditional floor/tail | **no per-condition models** — one shared geometry; only the floor (or tail calibration) conditions on the known operating condition |
| D | shared geometry + hierarchical between-bearing calibration | explicit b(i) layer estimated from construction bearings; unseen bearings receive the population-level buffer, not their own offsets |
| E | (optional) commissioning-style bearing offset correction | a short healthy commissioning window from the UNSEEN bearing may estimate its b(i) offset only — never damage-informed |

C exists because the predecessor's §6c refuted *splitting the
geometry*, not *using condition metadata*: the hard partition
destroyed the margins' common severity scale; C must keep the shared
scale by construction.

## 3. Primary evaluations

1. Unseen-healthy-bearing FAR (rotating folds), paired with detection
   from the same run — the pairing law applies to every table.
2. H1 preservation: the 12/12 per-condition adjacent-pair severity
   ordering on the real-pitting ladders, re-tested under each
   candidate.
3. Spearman ρ(extent, per-bearing median margin) not materially
   degraded (reference: +0.845 inner / +0.866 outer).
4. Extent-1 sensitivity: fraction of extent-1 real-damage frames
   outside the healthy envelope, reported per candidate (the
   swallowing metric).
5. Cross-condition comparability of the severity margin (one common
   ordinal scale; no per-condition rescaling artifacts).
6. Audit: no fault labels, no damage-frequency bands, no
   damage-specific adjustments anywhere in any candidate.

## 4. Pass candidates (fixed before execution)

- Unseen-healthy FAR < 2% (vs predecessor's 42% mean),
- H1 ordering 12/12 maintained,
- Spearman ρ not materially reduced,
- mild (extent-1) damage not absorbed wholesale into the healthy
  buffer (evaluation 4 does not collapse relative to A).

## 5. Kill conditions (fixed before execution)

- FAR improvement is achieved at the cost of severity ordering
  (any candidate that trades H1's 12/12 for FAR fails outright);
- the majority of extent-1 damage frames are absorbed into the
  healthy envelope;
- per-condition rescaling destroys the common margin scale
  (evaluation 5 fails);
- any candidate turns out to require damage-label-dependent
  adjustment (evaluation 6 fails) — disqualified, not tuned.

## 6. Output-role separation (architecture hypothesis under test)

Candidates D/E (and C where applicable) report two quantities per
frame instead of overloading one:

- `severity_margin` — non-saturating distance on the shared geometry;
  the ordinal severity scale, common across conditions;
- `calibrated_alarm_score` — tail-calibrated decision variable under
  condition + population + unit variation; the FAR-controlling output.

The hypothesis: severity comparison and alarm calibration are
different jobs, and the predecessor's H3/H1 tension is what happens
when one margin carries both.

## 7. Reporting discipline

Verbatim carry-overs from the predecessor: FAR/detection pairing on
every table; healthy variation is never called anomalous; detection
percentages under miscalibrated FAR are not deployment numbers;
post-hoc additions, if any, go into a separate marked section.

## 8. Execution results (run 2026-07-10; nothing above this section edited after the run)

Implementation: `tests/paderborn/exp_paderborn2.py` (committed at 8ea1a9d before
these results were read). Command: `python -m tests.paderborn.exp_paderborn2`.
40,944 frames, d=27, shared geometry K=5 on the primary fold; FAR for
every candidate evaluated on the identical frame set (recordings 5–20
of unseen bearings; 1–4 are the commissioning reserve). Sanity anchor:
candidate A's fold FARs (68.8/0.0/60.5%) reproduce the predecessor's
(66.4/0.0/59.8%) modulo the eval subset.

| Candidate | FAR (3 folds) | mean | det_all* | absorb-E1 | inner H1 | outer H1 | ρ (in/out) | scale ratio |
|---|---|---:|---:|---:|---|---|---|---:|
| A global floor | 68.8 / 0.0 / 60.5% | 43.1% | 81.5% | 11.9% | 8/8 | 4/4 | +0.85 / +0.87 | 1.58 |
| B component-conditional | 52.7 / 2.9 / 73.0% | 42.9% | 68.1% | **41.1%** | **7/8** | 4/4 | +0.85 / +0.87 | 1.31 |
| C condition-conditional | 49.8 / 25.5 / 65.3% | 46.9% | 74.7% | 22.4% | 8/8 | 4/4 | +0.85 / +0.87 | 1.58 |
| D hierarchical envelope | 46.9 / 25.0 / 62.4% | 44.8% | 63.5% | 35.5% | 8/8 | 4/4 | +0.85 / +0.87 | 1.58 |
| **E commissioning offset** | **15.5 / 0.0 / 26.8%** | **14.1%** | 81.5% | 11.9% | 8/8 | 4/4 | +0.85 / +0.87 | 1.58 |

\* det_all = detection over all damaged frames under the same run —
the pair for each FAR. Note how C/D's FAR "improvements" arrive with
detection drops (74.7 / 63.5% vs A's 81.5%): the pairing law showing
the trade.

### Verdicts (against the pre-registered §4 pass / §5 kill conditions)

- **A — KILLED as a fleet solution** (control; expected). Confirms the
  predecessor: flat pooled support does not transfer to unseen units.
- **B — KILLED, by kill condition 1+2.** Mean FAR essentially
  unchanged (42.9%), one inner ordering pair lost (7/8), and extent-1
  absorption jumps 11.9% → 41.1% — FAR non-improvement purchased with
  severity cost and mild-damage swallowing. The predecessor's post-hoc
  optimism about component floors does not survive the registered
  protocol (post-hoc §6b measured a different fold arrangement and no
  absorption metric — this is why post-hoc numbers carry no weight).
- **C — KILLED** (fails all pass criteria; no kill condition
  triggered, but mean FAR is *worse* than baseline — per-condition
  floors widened exactly where fold 2's previously-inside bearings
  lived — and absorption doubles to 22.4%).
- **D — KILLED as uncalibrated fleet transfer.** The population
  envelope (min-union over four construction bearings) still misses
  unseen units (mean 44.8%) while tripling extent-1 absorption
  (35.5%). Four bearings under-sample the population; widening
  envelopes swallows mild damage before covering unseen identity —
  the §5 kill mechanism, observed.
- **E — INCONCLUSIVE, direction strongly positive.** No kill condition
  triggered: H1 12/12 intact, ρ unchanged, absorption unchanged
  (severity side is untouched by design — role separation worked).
  FAR falls 43.1% → 14.1% (3.1×) with ONE scalar per unit estimated
  from 4 healthy recordings — but misses the pre-registered pass bar
  (< 2%), so it may not be declared SUPPORTED. Refinements (e.g.
  per-condition offsets, longer commissioning, scale as well as
  offset) are candidates for a pre-registration #3, not post-hoc
  tweaks here.

### Reading

The D-vs-E contrast answers the question they were built to separate:
**uncalibrated fleet transfer failed (D), while a short healthy
commissioning window recovered most of the loss (E) at zero severity
cost** — engineering value exactly as anticipated when the candidates
were defined ("D failing while E passes is a valid outcome").
E's residual FAR (14%) says one global offset per unit is not yet a
sufficient model of b(i); its zero-cost profile says the offset layer
is the right place to keep working. Role separation
(severity_margin vs calibrated alarm) did its job: every FAR
manipulation in B/C/D that touched the severity side paid for it
visibly, and E, which touched only the alarm side, paid nothing.

### Disclosed limitations

- E's damage-side commissioning cannot be simulated in this
  cross-sectional dataset (damaged bearings have no healthy period);
  E's damage metrics are therefore shared-geometry values (identical
  to A). In deployment, a unit commissioned healthy would carry its
  own offset into the damage phase; testing that requires
  longitudinal data.
- Compute: all candidates share the core cost; B/C/D add only floor
  lookups; E adds one median over 256 commissioning frames per unit.
- Production defaults unchanged; no promotion follows from this run
  alone (per §1).
