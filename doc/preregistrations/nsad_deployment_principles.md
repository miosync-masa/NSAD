# NSAD deployment principles — what the pre-registrations decided

Synthesis of the pre-registered arc (all executed, all pushed). The
principles below were fixed by #1–#4; #5 (added later, by logged
amendment) extends the shared-geometry leg cross-domain without
altering any of them:

| # | Plan | Verdict chain |
|---|---|---|
| 1 | [experiment_plan_paderborn.md](experiment_plan_paderborn.md) | H1 severity ordering SUPPORTED 12/12; H3 flat fleet support KILLED |
| 2 | [experiment_plan_paderborn2.md](experiment_plan_paderborn2.md) | support-widening (B/C/D) KILLED — swallows shallow damage; E commissioning inconclusive-positive |
| 3 | [experiment_plan_paderborn3.md](experiment_plan_paderborn3.md) | E3 location+scale SUPPORTED — design FAR from ~64 s of healthy commissioning, zero severity cost |
| 4 | [experiment_plan_ims.md](experiment_plan_ims.md) | H1L longitudinal progressiveness SUPPORTED 3/3; **H3L fleet-E3-as-failure-alarm KILLED 3/3** (11–14% of life late, or silent) |
| 5 | [experiment_plan_hydraulic.md](experiment_plan_hydraulic.md) | registered confirmatory: H1H cooler + H2H valve severity ordering SUPPORTED on a second machine class (margins ordered even below the alarm floor); H3H leak KILLED by its registered detection criterion; H4H observability limit confirmed |

## The symmetric result

Measured from both the success and the refutation side:

```
Shareable:        the damage-severity geometry (the ruler)
Not shareable:    the alarm's baseline history
Calibratable:     healthy false alarms (median + IQR, ~64 s)
Breaks if forced: the same calibration applied to failure alarms
Detectable:       system-level anomaly progression (persistent,
                  progressive, with 74–148 h lead)
Not localizable:  the source bearing/component — a separate
                  spatial-inference task, not a detector property
```

## The four results, one line each

1. **#1** — Physical damage severity is representable in a geometry
   that transfers across bearing identities.
2. **#2** — The healthy population must not be absorbed by widening
   the shared support: shallow damage goes with it.
3. **#3** — Healthy false alarms are fixed by per-unit
   location–scale commissioning: two scalars from ~64 seconds,
   severity untouched.
4. **#4** — That same fleet calibration must not serve as the failure
   alarm: in the damage phase it is 11–14% of life late, or silent.
   The failure alarm belongs to the unit's own accumulated history.

## Central sentences (fixed for the next manuscript)

> Physical damage severity was represented by a transferable
> geometry, but deployable alarm decisions required asset-specific
> temporal reference. Population-support expansion obscured shallow
> damage, while fleet location–scale calibration corrected healthy
> false alarms but delayed or suppressed longitudinal fault
> detection.

> Cross-sectional calibration success does not imply longitudinal
> detection validity.

Shortest form: **Share the ruler; personalize the baseline and the
history.**

## The three-layer deployment shape

```
Factory-shared (fleet prior)
├─ structural adapter (fault-agnostic vocabulary)
├─ shared structural geometry
├─ severity_margin (non-saturating, cross-unit comparable)
└─ three-state semantics

Commissioning of a new unit (admission)
├─ healthy median + healthy IQR (~64 s of healthy operation)
├─ initial FAR verification / normality admission
└─ E3's bounded role: healthy bridge, NEVER the failure alarm

In service (asset posterior)
├─ accumulate the unit's own normal history
├─ per-asset longitudinal baseline
├─ monitor occupancy / distribution deepening / persistence
└─ failure alarms from self-history, not fleet calibration
```

The handoff is *fleet prior → asset posterior*: a new unit becomes
operational immediately on a short commissioning, and alarm authority
migrates to the unit's own history as it accumulates.

## Consequences for the next manuscript

- The center of gravity is machine condition monitoring / PHM; the
  univariate corpus material is supporting evidence, not the stage.
- Every claim above carries a pre-registered run with frozen
  implementation commits on both sides (freeze SHA < results SHA in
  git history for #2, #3, #4).
- Known open items, registered where they arose: FAR at design rate
  from self-reference is not automatic (IMS t1-B3, 6.92%);
  geometry-mismatch vs scale-compression decomposition in H3L;
  fault localization as a separate spatial-inference layer;
  commissioned-unit damage-phase behavior under its own scale on
  longitudinal fleet data.
