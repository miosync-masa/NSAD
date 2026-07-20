# Pre-registered plan #6 — is the support-widening dilemma a property of the *formulation* or of *our density model*?

**Status: EXECUTED — results and verdicts in §8.** K4 anchor passed at
exact integer counts (run valid). **H1c SUPPORTED 4/4 — no model
admits any feasible shared clean-tail boundary; K1 does not fire; the
formulation-level claim is licensed.** **H2 SUPPORTED 4/4 — E3
recovers unseen-healthy FAR under every score family (0.10–0.34%);
the density model is an interchangeable component of the role
separation.** **H3 first half KILLED — K3 fires**: severity ordering
(12/12) held only for the likelihood deficit (M1); SPE/T²/combined
margins broke the extent ladder (4/8 inner) — severity geometry is a
property of *the likelihood deficit*, not of unsquashed scores in
general, and §2.7-1 is bounded accordingly. H3's M4 half supported in
the starkest form: BIP saturates at raw median 1.0000 at every extent
on real damage. H1a/H1b reported per model as registered (M3 sits on
the *other* horn of the dilemma: designed FAR transfers at 0.21% but
paired with 23% detection and 87% extent-1 absorption). §§0–7
untouched since registration (plan frozen at dd264cc, implementation
at 8beb325, both before any result was read). Originally written
2026-07-14; nothing above §8 edited after the freeze commit.

Predecessors: [experiment_plan_paderborn.md](experiment_plan_paderborn.md)
(#1, severity + cross-bearing FAR),
[experiment_plan_paderborn2.md](experiment_plan_paderborn2.md)
(#2, widening candidates A–D killed; E inconclusive-positive),
[experiment_plan_paderborn3.md](experiment_plan_paderborn3.md)
(#3, E3 location+scale commissioning supported).
Multivariate identity/parity evidence:
[experiment_plan_multivariate.md](experiment_plan_multivariate.md)
(#M, PCA-SPE and Hotelling T² established as identity-tested special
cases of the detector; FGMM-BIP saturation measured on the ghost
probe).

---

## 0. Purpose

Plans #1–#3 measured a dilemma on the Paderborn corpus: a flat pooled
support does not transfer its designed FAR to unseen healthy bearings
(42% FAR), every registered widening candidate failed (FAR barely
moves, extent-1 absorption rises to 41.1%), and a two-scalar
alarm-side commissioning recovers the designed rate at bit-identical
severity.

**Every one of those numbers was measured on one density model** — the
GMM support floor. The manuscript currently claims a
*formulation-level* result ("pooled one-class monitoring collapses
individuality and damage"), but the evidence licenses only a
*detector-level* one ("our GMM support floor collapses them"). A
reviewer is entitled to ask whether the dilemma is a weakness of our
density estimator rather than a property of the pooled one-class
formulation itself.

This plan asks exactly that question, and registers the answer that
would force us to *weaken* our own central claim.

> **Q1 (dilemma).** Does the support-widening dilemma reproduce under
> density models we did not design — PCA-SPE, Hotelling T², and their
> calibrated combination — on the same corpus, splits, and registered
> criteria? And, decisively: does **any** single shared clean-tail
> boundary exist, for **any** of these models, that admits unseen
> healthy bearings while retaining shallow damage?
>
> **Q2 (role separation).** Does two-scalar commissioning (median +
> IQR of the model's *own* clean score) recover unseen-healthy FAR
> under those same models, at unchanged severity?
>
> **Q3 (severity carrier).** Does the *non-saturation* property that
> distinguishes an unsquashed deficit from a probability-type index —
> measured on the synthetic ghost probe (BIP +0.0 IQR vs density floor
> +30.3) — reproduce on real physical damage with known extent?

Q1 and Q2 decide whether the paper's contribution is a **method** or a
**formulation**. Q3 decides whether the severity claim is a property
of the score's *form* (unsquashed) or of *our particular* score.

**Anchor vs prospective (disclosure, fixed here).** The M1 (GMM) cells
and the E3-on-M1 cell are **replication anchors**: their outcomes were
measured in #2/#3 and are known (candidate A: fold FARs 68.8/0.0/60.5%,
mean 43.1%; E3: 0.10% at bit-identical severity). They serve as the K4
sanity gate, and no verdict about them is claimed as new. The
**prospectively registered** outcomes — for which no measurement of any
kind has been performed — are: PCA-SPE (M2), Hotelling T² (M3), the
calibrated combined MSPC statistic (M5), all candidates and the
feasibility audit under each, and the FGMM-BIP severity contrast (M4)
on physical damage. This is the same honesty form as #5's
confirmatory disclosure, scoped along the model axis.

---

## 1. Fixed elements (unchanged, non-negotiable)

Everything below is inherited verbatim from plans #1–#3. Nothing is
re-tuned for this plan; if a density model needs a hyperparameter this
plan cannot set in a principled, damage-blind way, that model is
reported as inapplicable rather than tuned.

- **Corpus**: Paderborn KAt, d = 27 adapter
  (`tests/paderborn/paderborn_datasets.py`), 40,944 frames, 32 bearings,
  4 operating conditions. No fault-frequency alignment, no feature
  selection by damage labels, no adapter modification.
- **Splits**: by recording; healthy holdout by bearing (the same
  rotating folds over K001–K006 as #1 H3 and #2). Recordings 1–4 of an
  unseen bearing are the commissioning reserve; 5–20 are the evaluation
  set. **Identical frame sets to #2** — candidate A under M1 must
  reproduce #2's row as the sanity anchor (see K4 for the exact-count
  criterion). If it does not, the run is void and no verdict is issued.
- **Legitimacy rule**: damage labels only for final scoring and for
  the §3.8 feasibility *existence* evaluation (disclosed there);
  operating-condition labels are permissible operational metadata;
  bearing identity of construction units is permissible commissioning
  metadata; **no quantity may be tuned against damage outcomes**, for
  *any* model, including the baselines, and **no deployment threshold
  is ever selected using damage labels**. Every threshold in this plan
  is a percentile of the model's own clean-score distribution on a
  nested out-of-sample slice of construction data (the C.11 guardrail —
  its violation is what produced the ×32 drift on record).
- **Repository defaults remain unchanged** regardless of outcome.

---

## 2. Design: models × calibration candidates

### 2.1 Density models under test

Each model produces a scalar frame score `s(x)`, oriented so that
**larger means more abnormal** (§2.3-i), on the **shared fitted
geometry** built from healthy construction bearings only. All models
are fitted on the identical construction frames with **one shared PCA
fit per fold**; where they act differs and is fixed here:

- the GMM (M1), Hotelling T² (M3), and FGMM (M4) operate in the
  **retained-score space** of that shared PCA fit;
- **PCA-SPE (M2) is the squared prediction error in the discarded
  residual space of the original standardized d = 27 vector** — SPE is
  never computed from an already PCA-reduced input.

| ID | Model | Score `s(x)` | Provenance |
|---|---|---|---|
| **M1** | GMM support floor (current) | `ℓ_floor − ℓ(x)` (unsquashed log-likelihood deficit; retained-score space) | the released detector; reference values from #1–#3 (**anchor**) |
| **M2** | PCA-SPE (Q statistic) | squared prediction error in the residual space of the original standardized d = 27 vector | identity-tested vs the detector's reconstruction scorer, corr > 0.99 (`tests/probes/test_mspc_sanity.py`) — textbook MSPC (Jackson & Mudholkar, 1979) |
| **M3** | Hotelling T² | Mahalanobis distance in the retained-score space of the same shared PCA fit | the unknown channel at K = 1 (C.3) — textbook MSPC (Hotelling, 1947) |
| **M4** | FGMM-BIP | Bayesian inference probability index (probability-type, bounded) | the multimode-GMM lineage (Yu & Qin, 2008); our reconstruction, per the A.4 implementation disclosure |
| **M5** | calibrated combined MSPC | `r(x) = max( T²/τ_T², SPE/τ_SPE )`, recalibrated: `s(x) = r(x) / Q_0.995(r_clean)` on the nested clean slice (the A.10 multiple-comparison control applied to the SPE∨T² disjunction) | the strongest practical MSPC comparator expressible under the shared protocol |

M2, M3, and M5 are **state-of-the-art established features for this
task**, not straw men: they are the textbook standard of multivariate
condition monitoring, M2/M3 are already inside our own detector as
identity-tested special cases, and M5 is their calibrated disjunction —
the standard practical deployment of the pair. M4 is included because
it is the *closest published relative* of our method (multimode GMM)
and because it is the one score here whose form is
**probability-type and bounded** — it is the Q3 contrast, not a
competitor.

**Disclosure, stated in advance:** even M5 under this shared protocol
is *not* the strongest possible MSPC practice (which re-derives control
limits per process, uses contribution plots, and often per-condition
models). This plan does not claim to have optimised the baselines
beyond the shared protocol. What it claims to test is a **structural
property under a fixed common protocol**. Where a candidate is
inapplicable to a model, it is reported as N/A, never approximated.

### 2.2 Calibration candidates

Re-expressed from #2 so that each is well-defined for **any** scalar
score, not only for a mixture likelihood:

| ID | Candidate | Definition (model-agnostic) |
|---|---|---|
| **A** | flat pooled threshold (control) | single threshold = `Q_0.995(s_clean)` on the nested out-of-sample construction slice (the 0.5% designed clean tail; §2.3-ii) |
| **B** | component-conditional threshold | per-mixture-component thresholds — **defined only for M1/M4** (their own components); reported N/A for M2/M3/M5 (they have no components), and this asymmetry is itself reported, not patched |
| **C** | condition-conditional threshold | one shared geometry; the threshold (only) conditions on the known operating condition |
| **D** | hierarchical population envelope | identical in structure to #2's D: per-(construction-bearing × condition) cell thresholds on the nested slice; per condition, the unseen bearing receives the **loosest** threshold across construction bearings (min-union in likelihood orientation; for the one-sided abnormality scores of this plan, the loosest threshold is the **max**; §2.3-v) |
| **E3** | **two-scalar commissioning** | standardize `s` by the *unseen unit's own* clean median and IQR, estimated from its 4 healthy commissioning recordings (~64 s), then map onto the reference scale — the §2.4 affine transform, applied to whichever score the model emits (§2.3-iii) |

A–D are the widening family (they move the *support*). E3 is the
alarm-side family (it moves the *decision variable*, and by
construction cannot touch the geometry).

Cells: 5 models × 5 candidates, minus the three N/A cells (B under
M2/M3/M5) = **22 registered runs**.

### 2.3 Mathematical conventions (registered; the implementation may not deviate)

i. **Orientation.** Every score is oriented so larger = more abnormal:
   M1 `ℓ_floor − ℓ(x)`; M2 SPE; M3 T²; M4 BIP; M5 the calibrated
   max-ratio. M4's orientation is verified at run start (median on the
   nested clean slice must be below the median on known damaged
   frames); if reversed, it is negated, and the check is reported.

ii. **Thresholds.** Candidate A's threshold is the 99.5th percentile
   of `s` on the nested out-of-sample construction slice (designed
   clean tail 0.5%). All conditional candidates (B/C/D) use the same
   percentile rule within their cells, with the #2 small-cell
   fallbacks (≥ 50 frames for B/C cells, ≥ 20 for D cells; fallback to
   the global threshold). For M1 this reproduces the #2 floor exactly
   (threshold ≡ 0 in deficit orientation). For M5 the recalibration
   makes candidate A's threshold identically 1; the implementation
   asserts `|threshold_A_M5 − 1| < 1e-9` (a built-in detector of
   double-calibration or slice mix-ups).

iii. **E3.** For unseen unit i: `b̂ᵢ` = median and `ŝᵢ` = IQR of the
   unit's own clean `s` on commissioning recordings 1–4, with the
   zero-IQR guard `ŝᵢ ← max(ŝᵢ, 1e-12)`. Reference location/scale are
   the median and IQR of `s` on the nested clean slice. The alarm
   evaluates `s_ref(x) = med_ref + iqr_ref · (s(x) − b̂ᵢ)/ŝᵢ` against
   candidate A's threshold. The severity side is the untransformed
   `s`; its bit-identity to candidate A's severity output is asserted
   per model (evaluation 6).

iv. **H3 dynamic range.** At the registered 0.5% clean-tail operating
   point (never at a detection-matched point — that would be oracle
   matching): margin(extent) = (median `s` at that extent −
   candidate-A threshold) / max(clean IQR, 1e-12), on the inner
   ladder, per model — **with the unnormalized raw medians reported
   alongside** (guarding against degenerate clean IQRs for the bounded
   M4 score). Detection at the same operating point is reported from
   the same run.

v. **Hierarchical envelope direction.** #2's D takes, per condition,
   the loosest per-bearing floor (minimum in likelihood orientation).
   In this plan's one-sided abnormality orientation the loosest
   threshold is the **maximum** across construction bearings. Same
   candidate, orientation made explicit.

vi. **Feasibility sweep variable.** Fold geometries are independently
   fitted, so raw score values are not comparable across folds. The
   sweep variable is the **clean-tail quantile q**: for model m and
   fold f, `θ_mf(q) = Q_q(clean nested scores of m, f)`; FAR and
   absorption are evaluated per fold at `θ_mf(q)` and averaged across
   folds at fixed q (§3.8). A raw shared numeric threshold is never
   swept across folds.

---

## 3. Primary evaluations (identical to #2 unless stated, per cell)

For every (model, candidate) cell, on the identical evaluation frames:

1. **Unseen-healthy FAR** (rotating folds over K001–K006), **always
   paired with detection over all damaged frames from the same run** —
   the pairing law applies to every table, for baselines as strictly
   as for us. FARs are reported per fold with integer flagged counts
   and denominators, plus the fold mean.
2. **Extent-1 absorption**: fraction of shallowest-extent real-damage
   frames falling inside the healthy envelope (the swallowing metric).
   Reported as (a) the **fold mean** (each fold's geometry scores the
   damaged frames; the primary quantity for this plan's cross-fold
   claims) and (b) the **legacy primary-fold value** (direct
   comparability with #2).
3. **Severity ordering (H1)**: the 12/12 per-condition adjacent-pair
   test on the inner (8) and outer (4) real-pitting ladders, re-run on
   *that model's* score (primary-fold geometry, as in #1/#2; bootstrap
   seed fixed in the implementation before the freeze).
4. **Spearman ρ**(fact-sheet extent, per-bearing median score),
   reported per model with its n (6 inner bearings / 3 outer bearings).
5. **Severity dynamic range (Q3)**: per §2.3-iv, at the registered
   0.5% clean-tail operating point, with detection from the same run —
   the physical-data analogue of the ghost-probe saturation
   measurement (+0.0 vs +30.3 IQR).
6. **Severity invariance audit under E3**: the severity side must be
   **bit-identical** to that model's candidate-A severity output —
   verified per model, not assumed (mechanism 3 predicts it for any
   affine alarm-side transform of any score).
7. **Audit**: no fault labels, no defect-frequency bands, no
   damage-informed adjustment anywhere, in any cell, for any model.
8. **All-threshold feasibility audit (per model; the H1c quantity).**
   Sweep the common clean-tail quantile q per §2.3-vi. For each q:
   `FAR̄_m(q) = (1/3) Σ_f FAR_mf(θ_mf(q))` and
   `Abs̄_m(q) = (1/3) Σ_f Abs_mf(θ_mf(q))`. Report, per model: whether
   `∃q: FAR̄_m(q) < 2% ∧ Abs̄_m(q) < 50%`; the frontier (minimum
   Abs̄ subject to FAR̄ < 2%, and minimum FAR̄ subject to Abs̄ < 50%);
   and **per-fold feasibility flags** (whether the same conjunction is
   achievable within each fold alone). Damage labels are used only to
   *evaluate the existence* of a feasible boundary — an oracle
   existence audit, disclosed as such — never to choose a deployment
   threshold.

---

## 4. Hypotheses and pass conditions (fixed before execution)

**H1 — the dilemma is model-invariant.** Split into three registered
sub-hypotheses; only H1c controls the formulation-level verdict.

- **H1a — native boundary transfer (descriptive strength).** For each
  of M1, M2, M3, M5: candidate A's mean unseen-healthy FAR is ≥ 10×
  the designed rate. Reported per model; a model falling short of the
  10× magnitude is reported as such and weakens the *strength*
  narrative, but does not by itself kill the formulation-level claim.
- **H1b — tested adaptations fail.** For each of M1, M2, M3, M5: no
  widening candidate (B/C/D, where applicable) reduces mean FAR below
  10% without raising fold-mean extent-1 absorption above that model's
  candidate-A value. Reported per model as a registered
  sub-hypothesis.
- **H1c — shared-boundary infeasibility (the controlling verdict).**
  For **each** of M1, M2, M3, M5, the feasibility audit of §3.8 finds
  **no** q with `FAR̄(q) < 2% ∧ Abs̄(q) < 50%`.

*H1 is supported — licensing the formulation-level claim — when H1c
holds for all four models. H1a/H1b are reported alongside as strength
and adaptation evidence; their partial failure adjusts wording, not
the license.*

**H2 — role separation is model-invariant.**
For **each** of M1, M2, M3, M5: candidate E3 reduces mean
unseen-healthy FAR below the 2% pass bar of #3, **and** the severity
audit (evaluation 6) is bit-identical for that model.

*Supported if it holds for all four. This licenses the claim that the
three-layer deployment principle is a property of the formulation, and
that the density model is an interchangeable component.*

**H3 — non-saturation is a property of the score's form.**
On the inner extent ladder, at the registered 0.5% clean-tail
operating point (§2.3-iv): the unsquashed scores (M1, M2, M3, M5)
yield a strictly increasing median margin across extents 1→2→3 with a
dynamic range > 5 clean-IQR between extent 1 and extent 3, whereas the
probability-type index (M4) yields a range < 1 clean-IQR at that same
registered operating point (i.e. it detects but cannot grade), with
detection from the same run reported for every model.

*Supported if both halves hold. This moves the ghost-probe saturation
finding from a synthetic probe to real physical damage of known
extent.*

---

## 5. Kill conditions (fixed before execution — these are the ones that cost us)

- **K1 (kills the formulation-level claim; fires on H1c only).** If
  the feasibility audit finds, for **any** of M1/M2/M3/M5, a
  clean-tail quantile q with `FAR̄(q) < 2% ∧ Abs̄(q) < 50%`, then the
  manuscript's central proposition is **demoted from formulation-level
  to detector-level** throughout, and the model admitting the feasible
  boundary is reported as the counterexample, by name, in the main
  text. The abstract sentence *"conventional pooled one-class
  monitoring collapses..."* would be rewritten to name our detector
  specifically. (Failures of H1a's 10× magnitude or of H1b's
  adaptation criteria adjust scope wording but do not, alone, fire
  K1.)

- **K2 (kills the interchangeability claim).** If E3 fails to recover
  FAR under M2, M3, or M5, then role separation is **reported as a
  property of the likelihood-based formulation only**, not of pooled
  one-class monitoring generally, and §2.4/§6.2 are re-scoped
  accordingly. We do not get to say "the density model is an
  interchangeable component."

- **K3 (kills the severity-form claim).** If M2/M3/M5 fail to preserve
  severity ordering (H1 12/12), then severity geometry is a property
  of *the likelihood deficit*, not of unsquashed scores in general,
  and §2.7-1 is bounded to say so. (Note: this outcome would be a
  *stronger* result for our method and a *weaker* one for the paper's
  thesis. It is registered as a kill precisely because it is the
  outcome we would be tempted to celebrate.)

- **K4 (voids the run).** Candidate A under M1 must reproduce #2's
  anchor row **exactly at the integer level**: per fold, the flagged
  frame count and the evaluation-frame denominator must equal the
  values produced by #2's own candidate-A implementation run in the
  same process on the same folds (and the resulting percentages must
  round to #2's published 68.8/0.0/60.5%). If integer equality fails,
  the run is void; no verdict issues. (Fallback tolerance of ≤ 0.05
  percentage points applies only if an integer comparison is
  structurally impossible, which is not expected.)

---

## 6. What this plan decides (stated before seeing the numbers)

| Outcome | Consequence for the manuscript |
|---|---|
| H1c + H2 supported | The contribution is a **formulation-level result**: no single shared clean-tail boundary reconciles unseen-healthy admission with shallow-damage retention under GMM, PCA-SPE, Hotelling T², or calibrated combined MSPC — and the three-layer resolution holds across all of them. The density model is an interchangeable component; the paper's claim is about pooled one-class monitoring, not about Lambda³-NSAD. **This also constitutes the comparison against state-of-the-art established features that MSSP's ML guidelines require** — not as a superiority claim, but as a measurement of a *shared structural limit* and a *shared remedy*. |
| H1c supported, H2 killed | The dilemma is universal; the remedy is ours. Weaker, still publishable, and honestly reported. |
| H1c killed (K1) | The central proposition is demoted to a detector-level finding, and the counterexample model is named in the abstract. |
| H3 supported | The severity/alarm role separation is grounded in the *form* of the score (unsquashed vs bounded), measured on real damage — the mechanism-1 obligation discharged on physical data rather than a probe. |
| H3 killed | Mechanism 1's non-saturation argument is bounded to the synthetic probe and reported as such (K3 wording where ordering itself fails). |

**No outcome of this plan changes any number already reported in
§4–§5 of the manuscript.** The registered verdicts of #1–#5 stand as
executed. This plan can only change the *scope* of what those numbers
are claimed to show.

---

## 7. Reporting discipline

- Every FAR is reported with the detection from the same run — for the
  baselines too. A silent baseline is not a good baseline.
- Baseline underperformance is never reported as our advantage. If
  M2/M3/M5 do worse, the disclosure of §2.1 (they are not optimised
  MSPC practice) is repeated **in the same table caption**, not buried.
- The N/A cells (B under M2/M3/M5) are printed as N/A. They are a fact
  about what a component-free model can express, and they are
  discussed, not filled.
- Fold-mean and legacy primary-fold absorption are both printed;
  per-fold feasibility flags are printed; no conclusion is drawn from
  a single fold alone.
- Verdicts are written against §4/§5 verbatim, with no post-hoc
  criteria. Any post-hoc observation goes in a separately marked
  subsection carrying no evidential weight (the #2 §8-B precedent).

---

## 8. Execution results

*(To be completed after execution. Nothing above this line may be
edited after the freeze commit. Freeze SHA precedes results SHA in the
repository history.)*

Implementation: `tests/paderborn/exp_density_invariance.py` (to be
committed and frozen before results are read).
Command: `python -m tests.paderborn.exp_density_invariance`.

### Implementation notes (binding on the implementation, part of the registration)

- Reuse `exp_paderborn2.py`'s fold logic, frame sets, and constants
  **unchanged** (`SharedGeometry`, `FOLDS`, `_rec_index`,
  `COMMISSION_MAX_IDX`, ladders, `EXTENT1_REAL`); the frozen #2 runner
  file is not modified. The nested floor-slice indices are re-derived
  by the byte-identical deterministic procedure (same seed-0 shuffle),
  and the re-derivation is verified by exact equality of the
  reconstructed `floor_ll` with `SharedGeometry.floor_ll`.
- Scores follow §2.1/§2.3 exactly: M2 = `pca.spe(z(X))` on the
  standardized d = 27 vector; M3 = `pca.t2(z(X))`; M1/M4 in the
  retained-score space of the same `pca` object; M5 per §2.1 with the
  threshold-≡-1 assertion.
- All thresholds, τ's, reference statistics, and E3 statistics come
  from the same nested out-of-sample slice and the same percentile
  rule (never in-sample: the C.11 guardrail).
- E3 for every model standardizes **that model's own clean score**
  (median, IQR, zero-IQR guard) from the unseen unit's commissioning
  recordings 1–4. For M2/M3/M5 the score is one-sided and
  non-negative; the transform is still affine and the
  severity-invariance prediction is unchanged.
- M4 (FGMM-BIP) reuses the A.4 reconstruction verbatim (`FGMMBayes`,
  BIC over K, seed 0); no re-tuning; orientation assertion per
  §2.3-i.
- The feasibility sweep implements §2.3-vi / §3.8 with a fine
  registered q-grid (2001 uniform points on (0,1) plus a refinement
  ladder approaching 1), evaluated by sorted-score binary search;
  monotonicity of FAR̄ and Abs̄ in q is checked and reported.
- Bootstrap seed for the ladder CIs: 7 (matching #2's evaluation
  seed); N_BOOT = 800.
- Emit machine-readable results into `paper_results/`:
  `density_invariance.csv` (one row per cell: fold FARs with integer
  counts, fold-mean FAR, det_all fold-mean + primary, absorption
  fold-mean + legacy primary, ordering, ρ; N/A cells explicit),
  `density_feasibility.csv` (per model: existence flag, frontier
  values, per-fold flags), `density_severity.csv` (per model ×
  extent: margin in clean-IQR, raw median, detection at the
  registered point). These are not added to `manifest.json`
  verification at run time; registration of the executed numbers into
  the manifest is a separate post-§8 step.

### Results (run 2026-07-14; §§0–7 and the implementation notes above unchanged after the freeze commits)

Plan frozen at dd264cc; implementation frozen at 8beb325; both precede
this results commit. Command: `python -m
tests.paderborn.exp_density_invariance`. Machine-readable outputs:
`paper_results/density_invariance.csv`, `density_feasibility.csv`,
`density_severity.csv`.

**K4 anchor — PASSED at exact integer counts (run valid).** M1×A per
fold: 1408/2048, 0/2048, 1240/2048 — identical to #2's CandA run
in-process, and rounding to the published 68.8/0.0/60.5%. M4
orientation check: clean median 0.4620 < damaged median 1.0000 → sign
+1 (no negation needed). All fold geometries K=5; FGMM K=5. M1
A-threshold ≡ 0 and M5 A-threshold ≡ 1 assertions passed.

**Cell table (fold-mean FAR / det_all / extent-1 absorption; legacy
primary-fold absorption in parentheses; B = N/A for component-free
models):**

| Model | A | B | C | D | E3 |
|---|---|---|---|---|---|
| M1 GMM deficit | 43.10% / 53.7% / 41.4% (11.9%) | 42.85% / 52.5% / 50.0% (41.1%) | 46.86% / 68.4% / 28.8% (22.4%) | 44.78% / 63.7% / 33.9% (35.5%) | **0.10%** / 53.7% / 41.4% (11.9%) |
| M2 PCA-SPE | 5.21% / 44.7% / 63.9% (62.3%) | N/A | 10.24% / 45.9% / 53.2% (54.9%) | 6.98% / 41.8% / 61.1% (63.4%) | **0.16%** / 44.7% / 63.9% (62.3%) |
| M3 Hotelling T² | 0.21% / 23.3% / 87.2% (73.8%) | N/A | 0.26% / 21.6% / 87.4% (83.0%) | 0.08% / 16.5% / 91.7% (91.0%) | **0.33%** / 23.3% / 87.2% (73.8%) |
| M4 FGMM-BIP | 44.87% / 53.7% / 42.4% (18.4%) | 48.91% / 65.1% / 39.7% (39.4%) | 50.42% / 70.3% / 27.8% (22.6%) | 47.74% / 67.9% / 30.7% (30.3%) | **0.00%** / 53.7% / 42.4% (18.4%) |
| M5 combined MSPC | 3.39% / 39.9% / 70.2% (70.7%) | N/A | 6.59% / 39.9% / 64.4% (62.5%) | 4.38% / 35.7% / 72.1% (71.7%) | **0.34%** / 39.9% / 70.2% (70.7%) |

Disclosure repeated with the table (per §7): M2/M3/M5 under this
shared protocol are not optimised MSPC practice; underperformance is
never claimed as our advantage.

**Feasibility audit (§3.8; the H1c quantity):**

| Model | Feasible q exists? | min Abs̄ s.t. FAR̄<2% | min FAR̄ s.t. Abs̄<50% | per-fold flags |
|---|---|---|---|---|
| M1 | **no** | — (FAR̄<2% unreachable) | 22.2% | T/F/F |
| M2 | **no** | 76.0% | 8.8% | F/F/T |
| M3 | **no** | 77.8% | 20.5% | F/T/F |
| M4 | **no** | — (FAR̄<2% unreachable) | 24.4% | T/F/F |
| M5 | **no** | 77.2% | 8.4% | F/T/T |

FAR̄ and Abs̄ monotone in q for every model (checked). Single folds
occasionally admit a feasible point (the per-fold flags) — never the
fold mean, which is exactly why the fold-mean judgment was registered.

**Severity ladder and H3 margins (primary fold; registered 0.5%
clean-tail point; margins in clean-IQR with detection from the same
run; raw medians in the CSV):**

| Model | inner ordered | outer ordered | ρ inner/outer | extent 1→2→3 margins | detection |
|---|---|---|---|---|---|
| M1 | **8/8** | **4/4** | +0.85 / +0.87 | +10.3 / +19.1 / +21.4 | 84/100/100% |
| M2 | 4/8 | 3/4 | +0.78 / +0.00 | −0.1 / +21.8 / +11.9 | 47/99/95% |
| M3 | 4/8 | 4/4 | +0.78 / +0.87 | −1.2 / +1.6 / +1.2 | 39/67/60% |
| M4 | 3/8 | 3/4 | +0.48 / +0.50 | +0.0 / +0.0 / +0.0 (raw medians 1.0000/1.0000/1.0000) | 77/100/100% |
| M5 | 4/8 | 3/4 | +0.78 / +0.00 | −0.9 / +13.5 / +6.7 | 35/94/86% |

E3 severity-invariance audit (evaluation 6): bit-identical per model,
asserted in-run.

### Verdicts (against §4/§5 verbatim)

- **H1a (descriptive, per model):** M1 ✓ (43.10% ≥ 5%), M2 ✓ (5.21%),
  M3 ✗ (0.21%), M5 ✗ (3.39%). M3's low native FAR is reported with its
  registered pairing: detection 23.3% and extent-1 absorption 87.2% —
  the T² boundary admits unseen healthy units by being nearly blind to
  shallow damage. It sits on the *other horn* of the dilemma, not
  outside it.
- **H1b (adaptations, per model):** holds for M1 and M3; fails by its
  letter for M2 (D: 6.98% < 10% at absorption 61.1% < A's 63.9%) and
  M5 (C: 6.59% < 10% at absorption 64.4% < A's 70.2%) — in both cases
  the "success" is a sub-10% FAR bought at >60% shallow-damage
  absorption under a candidate whose control was already absorbing
  >60%. Reported as registered; scope wording adjusted, license
  unaffected (H1c controls).
- **H1c — SUPPORTED 4/4. K1 does not fire.** No single shared
  clean-tail boundary achieves FAR̄ < 2% ∧ Abs̄ < 50% for any of M1,
  M2, M3, M5 (nor, descriptively, M4). **The formulation-level claim
  is licensed**: on this corpus, under likelihood, residual,
  Mahalanobis, and calibrated combined statistics alike, healthy
  individuality and shallow damage compete for the same pooled scalar
  boundary — the models differ only in which horn of the dilemma they
  sit on.
- **H2 — SUPPORTED 4/4 (and M4 descriptively).** E3 recovers
  unseen-healthy FAR under every score family: M1 0.10%, M2 0.16%,
  M3 0.33%, M5 0.34% (M4 0.00%), each paired with its family's
  unchanged fold-mean damage detection (det_all 53.7 / 44.7 / 23.3 /
  39.9 / 53.7%, per the cell table) and each at bit-identical
  severity. *(Presentational pairing added post-results-commit per the
  standing FAR-with-detection rule; no number or verdict changed.)*
  **The density model is an interchangeable component of the
  three-layer role separation**; the remedy is a property of the
  formulation, not of the likelihood.
- **H3 — first half KILLED; K3 FIRES.** Only M1 satisfies the
  registered unsquashed-ladder condition (strictly increasing,
  range 11.1 IQR > 5). M2/M3/M5 margins break the extent ladder
  (extent-2 > extent-3 for M2/M5; M3 compresses to a 2.8-IQR band)
  and their per-condition ordering falls to 4/8 inner. Per K3's
  registered wording: **severity geometry is a property of the
  likelihood deficit, not of unsquashed scores in general** — §2.7-1
  is bounded accordingly (non-saturation is necessary but not
  sufficient; the score must also resolve the damage displacement,
  which the full-density deficit does and the residual/Mahalanobis
  projections do not, on this corpus). The registered note stands:
  this is a stronger result for our method and a weaker one for the
  thesis, which is exactly why it was registered as a kill. **H3's M4
  half is supported in its starkest form**: BIP saturates at raw
  median 1.0000 at every extent — on real physical damage, the
  probability-type index detects (77–100%) but cannot grade at all.

### Reading

The dilemma is a property of the formulation; the remedy is a property
of the formulation; the *ruler* is a property of the score. Five score
families, one shared protocol, one registered feasibility question —
and no pooled scalar boundary reconciles unseen-healthy admission with
shallow-damage retention under any of them, while two commissioning
scalars fix the alarm under all of them. What does *not* generalize is
the severity ladder: the unsquashed *form* is necessary (M4's
saturation shows what is lost without it) but only the likelihood
deficit on the fitted support carried physical extent ordering. The
manuscript's claims move accordingly: the conflation claim and the
role separation are stated at formulation level with #6 as license;
mechanism 1 is bounded to the likelihood deficit; and the MSSP
established-features comparison is discharged as a measured shared
structural limit and a shared remedy — with no superiority claim
anywhere.

### Standing limitations

- M2/M3/M5 are the shared-protocol expressions of MSPC statistics,
  not optimised MSPC practice (per-process control limits,
  contribution plots, per-condition models remain untested here).
- The feasibility audit is an oracle *existence* measurement (damage
  labels evaluate the frontier; no deployment threshold is chosen
  from it).
- Single-fold feasible points exist for every model; conclusions rest
  on fold means as registered.
- H1b's 10%/absorption criterion proved loose against controls that
  already absorb >60%; reported as registered, superseded by H1c.
- Production defaults unchanged.
