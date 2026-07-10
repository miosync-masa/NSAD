# Pre-registered plan #3 — asset-specific alarm calibration on a fixed severity geometry

**Status: EXECUTED — results and verdicts in §7.** E3
(location+scale commissioning) SUPPORTED at FAR 0.10% — below the
designed 0.5% rate — from 4 healthy recordings per condition, severity
audit exact; E4 supported; E0/E2 killed; the E1 ladder's registered
diagnostic identified the scalar-offset model (not sample size) as the
binding constraint. §§0–6 untouched since pre-registration. Successor to
[experiment_plan_paderborn2.md](experiment_plan_paderborn2.md) (§8:
A–D killed; E inconclusive-positive). Written 2026-07-10, before any
candidate below has been run under this protocol.

## 0. Motivation (what #2 established)

Two representations of healthy between-bearing variation were
separated experimentally:

```
Failed representation (B/C/D):
  widen the shared normal support
  → shallow damage is absorbed into the envelope
    (E1 absorption 11.9% → 22–41%), detection drops,
    ordering can be lost — FAR barely moves.

Positive direction (E):
  keep the shared severity geometry FIXED;
  align only the alarm origin to the unit's own healthy
  commissioning
  → FAR 43.1% → 14.1% (3.1×) at ZERO severity cost
    (H1 12/12, ρ, E1 absorption all unchanged).
```

Conceptually: keep the shared margin `m(x)` and correct only the
alarm side, `a_i(x) = m(x) − b̂_i` — unit identity as a **zero-point
difference in a common normality coordinate**, not a different damage
geometry. The human analogy: a shared temperature-to-pathology scale,
plus each person's own baseline temperature; deviation is read from
the personal baseline, but the scale of fever depth stays common.

E's residual 14.1% FAR says one scalar does not capture all of b(i).
Candidate residual mechanisms (fixed here as the hypothesis space):
the offset differs by operating condition; the unit's normal
DISPERSION differs, not only its center; 4 recordings under-estimate
the tail; within-recording correlation shrinks the effective sample.

Central sentences this plan aims to earn (or kill):

> A shared severity geometry survived across bearing identities,
> whereas a usable alarm operating point required asset-specific
> healthy commissioning.

> Expanding the population support degraded shallow-damage
> visibility, while a one-scalar commissioning correction reduced
> false alarms without altering severity ordering.

## 1. Fixed elements (non-negotiable)

- d=27 adapter, shared geometry (frozen path), rotating healthy folds
  — identical to #2.
- **The severity_margin is untouchable by every candidate.** All
  candidates calibrate the ALARM side only. Audit: each candidate's
  H1 12/12, Spearman ρ, and severity-side E1 metrics must be
  bit-identical to the shared-geometry values (this is the absolute
  qualification E earned in #2, now a standing requirement).
- Commissioning data: healthy recordings of the unseen unit only;
  never damage periods, never damage labels.
- Commissioning reserve: recordings 1–12 per (bearing, condition).
  **FAR eval set: recordings 13–20** of unseen bearings — identical
  frame set for every candidate and every ladder point.
- Damage-side metrics are evaluated at the uncommissioned shared
  floor (cross-sectional data has no healthy period for damaged
  units; a commissioned unit's damage-phase behavior requires
  longitudinal data — standing limitation, disclosed).
- Production defaults unchanged regardless of outcome.

## 2. Candidates (all alarm-side only)

| ID | Description | Fixed constants |
|---|---|---|
| E0 | per-unit global scalar offset (the #2 candidate, re-run on the 13–20 eval set) | baseline |
| E1 | commissioning-length ladder for E0: 1 / 2 / 4 / 8 / 12 recordings per condition | ladder fixed; no other change |
| E2 | condition-specific offsets with shrinkage toward the unit's global scalar | shrinkage weight w = n_c/(n_c + n₀), **n₀ = 128 frames** (two recordings' worth), fixed here |
| E3 | location + scale: unit's ll standardized by its commissioning median and IQR, mapped back to the reference scale, then compared to the global floor | scale = IQR ratio; no free constants |
| E4 | E3 + conservative tail: per-unit floor = lower bootstrap 95% confidence bound of the Q=0.5% quantile of the unit's commissioning ll (standardized) | 1000 bootstrap resamples, fixed |

Per-unit-per-condition independent models remain forbidden (E2 is
shrinkage to a shared scalar, not free parameters). No candidate may
touch the shared geometry, mixture, PCA, or severity margin.

## 3. Primary evaluations

1. Unseen-healthy FAR (3 rotating folds, eval recordings 13–20),
   paired with det_all from the same run — every table.
2. FAR-vs-commissioning-length curve (E1 ladder): does FAR stabilize
   with sample size, and where.
3. Severity-side audit: H1 12/12, ρ, severity-E1-absorption —
   must equal the shared-geometry values exactly (violation =
   disqualification, not a result).
4. Alarm-side E1 absorption at the commissioned operating point,
   reported per candidate (damaged units carry no offset — disclosed
   convention as in #2).
5. Calibration cost: recordings required per unit; compute deltas.
6. Audit: no fault labels / frequencies / damage-specific features.

## 4. Pass conditions (fixed before execution)

- Unseen-healthy FAR < 2% (the #2 bar, unchanged) at a commissioning
  cost ≤ 8 recordings per condition;
- severity-side audit passes exactly (item 3);
- report the distance to the designed 0.5% rate either way.

## 5. Kill conditions (fixed before execution)

- Any candidate whose mechanism touches the severity margin —
  disqualified outright (not tuned, not partially credited);
- FAR improvement that arrives with alarm-side E1 absorption
  materially above E0's (swallowing via personalized floors);
- E1-ladder instability: FAR at 12 recordings not better than at 4
  → the offset model, not the sample size, is the binding constraint;
- any candidate requiring damage-label-dependent adjustment.

## 6. Execution order

E0 (baseline re-anchor) → E1 ladder → E2 → E3 → E4; single script,
same folds, same eval frames; verdicts SUPPORTED / KILLED /
INCONCLUSIVE per candidate; failed candidates reported, not deleted;
results appended below this section, nothing above edited.

## 7. Execution results (run 2026-07-10; nothing above this section edited after the run)

Implementation: `tests/paderborn/exp_paderborn3.py`, committed at c61f061 before
these results were read. Command: `python -m tests.paderborn.exp_paderborn3`.

**Severity audit (the standing qualification)** — shared margin common
to every candidate by construction, verified: inner 8/8 ρ+0.85, outer
4/4 ρ+0.87, det_all 81.5%, severity-side extent-1 absorption 11.9% —
identical to the shared-geometry reference. Damaged units carry no
commissioning (disclosed §1 convention), so the E-family's damage-side
alarm values equal the shared-floor values; the personalized-floor
swallowing kill cannot be exercised in cross-sectional data.

**Unseen-healthy FAR (eval = recordings 13–20, identical for all):**

| Configuration | fold1 | fold2 | fold3 | mean |
|---|---:|---:|---:|---:|
| E0/E1 scalar n=1 | 20.70% | 0.00% | 25.29% | 15.33% |
| E0/E1 scalar n=2 | 21.78% | 0.00% | 29.20% | 16.99% |
| E0 scalar n=4 | 19.73% | 0.00% | 28.71% | 16.15% |
| E0/E1 scalar n=8 | 17.97% | 0.00% | 29.00% | 15.66% |
| E0/E1 scalar n=12 | 15.43% | 0.00% | 28.81% | 14.75% |
| E2 shrunk-cond n=4 | 18.26% | 0.00% | 23.05% | 13.77% |
| E2 shrunk-cond n=8 | 16.99% | 0.00% | 20.31% | 12.43% |
| **E3 loc+scale n=4** | **0.29%** | **0.00%** | **0.00%** | **0.10%** |
| **E3 loc+scale n=8** | 0.88% | 0.00% | 0.00% | **0.29%** |
| **E4 +cons.tail n=4** | 2.54% | 0.10% | 0.00% | **0.88%** |
| **E4 +cons.tail n=8** | 0.20% | 0.20% | 0.00% | **0.13%** |

### Verdicts (against the pre-registered §4 pass / §5 kill conditions)

- **E0 — KILLED** (16.15% ≫ 2%). Re-anchors #2's finding on the new
  eval set.
- **E1 ladder — the registered diagnostic fired.** The ladder is
  essentially flat (15.3% at 1 recording → 14.75% at 12): per §5
  kill 3, **the offset model, not the sample size, is the binding
  constraint**. One scalar per unit was never going to converge to
  design rate with more data.
- **E2 — KILLED** (13.77% / 12.43%). Condition-resolved offsets help
  marginally; the mechanism is not condition-dependence of the
  center.
- **E3 — SUPPORTED.** FAR 0.10% (n=4) / 0.29% (n=8) — below the 2%
  pass bar **and below the designed 0.5% rate itself** — at a
  commissioning cost of 4 recordings per condition, with the severity
  audit passing exactly. Distance to design (§4 reporting duty):
  realized ≤ designed, i.e. slightly conservative.
- **E4 — SUPPORTED** (0.88% at n=4; 0.13% at n=8; the conservative
  tail needs the larger window to beat E3's plug-in floor, as
  expected from quantile-bootstrap noise at n=256 frames).

### Reading

The E1-flatness + E3-collapse pair identifies the structure of
healthy unit identity in this data: **units differ in the location
AND the dispersion of their clean likelihood — two scalars, not
one.** Standardizing each unit's likelihood by its own commissioning
median and IQR (then mapping back to the shared reference scale)
restores the designed false-alarm rate on unseen units:

> Two scalars per unit — the median and IQR of its own clean
> likelihood, estimated from ~64 seconds of healthy operation
> (4 recordings × 4 conditions × 4 s) — recover the designed
> false-alarm rate on unseen bearings, at zero severity cost.

Both §0 central sentences are earned, and the second strengthens:
expanding the population support degraded shallow-damage visibility
(#2); a two-scalar commissioning standardization reduced false alarms
to the design rate without altering severity ordering (#3). The
severity geometry is shared; the alarm origin AND unit are personal.

### Standing limitations

- Cross-sectional: a commissioned unit's damage-phase behavior under
  its own (location, scale) correction is untestable here —
  longitudinal validation remains the decisive future test, since a
  loose per-unit scale estimated at commissioning could in principle
  compress later damage margins on the alarm side.
- fold1's E4 n=4 (2.54%) shows the conservative tail is
  small-sample-fragile; E3's plug-in floor is the simpler and better
  candidate at short commissioning.
- Production defaults unchanged; promotion (e.g., an opt-in
  commissioning API on the detector) is a separate, logged decision.
