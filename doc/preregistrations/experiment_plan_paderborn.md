# Pre-registered plan — Paderborn full-dataset validation

**Status: EXECUTED — results in §5.** H1 supported (12/12
condition-pair tests ordered); H2 killed on purity (confound noted);
H3 killed exactly as its kill condition anticipated — the prominent
finding. Sections 0–4 are untouched since pre-registration (verified
against commit 332b1d2). §5's numbers and verdicts are from the run
(commit 088bc8e); one interpretive paragraph in §5-H3 and the §6
readings were refined after conceptual review (marked inline; original
phrasing preserved in git history). §7 adds the conceptual model; the
follow-up pre-registration is
[experiment_plan_paderborn2.md](experiment_plan_paderborn2.md).

**Original status: PRE-REGISTERED, data not yet transferred.** Fixed before the
full dataset arrives (transfer: GitHub Release assets on this repo).
The subset exploration ([paderborn_exploration.md](../explorations/paderborn_exploration.md))
was exploratory; this document converts its open questions into
hypotheses with kill conditions, per the discipline of
[experiment_plan_multivariate.md](experiment_plan_multivariate.md).
Written 2026-07-10, before any full-dataset measurement.

## 0. Ground truth (from the official fact sheets, fixed here)

Healthy (Table 7): K001–K006 (6 bearings; K001 has >50 h run-in,
K002–K006 have 1–19 h).

Artificial damage (Table 4, all single-point): outer ring KA01(EDM,1),
KA03(engraver,2), KA05(engraver,1), KA06(engraver,2), KA07(drill,1),
KA08(drill,2), KA09(drill,2); inner ring KI01(EDM,1), KI03(engraver,1),
KI05(engraver,1), KI07(engraver,2), KI08(engraver,2).

Real damage from accelerated lifetime tests (Table 5):

| Ladder | Bearings (damage, extent) |
|---|---|
| Outer, fatigue pitting | KA04(1), KA22(1), **KA16(2)** |
| Outer, indentation | KA15(1), KA30(1) |
| Inner, fatigue pitting | KI04(1), KI14(1), KI17(1), KI21(1), **KI18(2)**, **KI16(3)** |
| Combined | KB23(in+out, 2), KB24(in+out, 3), KB27(out+in indent, 1) |

**The severity ladders for H1**: inner-ring real fatigue pitting spans
extents 1→2→3 (KI04/14/17/21 → KI18 → KI16); outer spans 1→2
(KA04/22 → KA16); combined spans 1→2→3 (KB27 → KB23 → KB24, mixed
damage types, secondary evidence only).

Four operating conditions per bearing (N15_M07_F10, N09_M07_F10,
N15_M01_F10, N15_M07_F04): speed 1500/900 rpm, torque 0.7/0.1 Nm,
radial force 1000/400 N. 20 recordings × 4 s each per setting.

## 1. Confound identified in the subset run (drives the design)

K001/KA01/KI01 are **different physical bearings**: the subset's
out-of-support judgment mixes (damage) + (bearing identity) +
(mounting/recording variation). The full dataset separates these:
healthy identity variation is measured across K001–K006, and detection
claims must survive it.

## 2. Hypotheses (fixed, with kill conditions)

**H1 — physical severity ordering (the core claim).** On the
inner-ring real-pitting ladder, the median support margin of damaged
frames is strictly ordered by damage extent: median(KI16, ext.3) >
median(KI18, ext.2) > median(extent-1 group), per operating condition,
with Spearman ρ(extent, per-bearing median margin) > 0 and bootstrap
95% CI on each pairwise median difference excluding 0.
*Kill*: any adjacent pair reversed with CI excluding 0, in ≥2 of 4
operating conditions → H1 falsified for real damage; report as the
severity claim's physical limit. *Note*: extent-1 bearings differ as
individuals; their spread is reported as the identity-noise floor
against which the ladder must stand.

**H2 — condition-as-regime at K=4.** With healthy construction data
spanning all four operating conditions, BIC selects K ≥ 4 and the
regime↔condition assignment purity on held-out healthy recordings is
> 90%. *Kill*: purity < 70% or BIC collapses conditions (K ≤ 2) →
the subset's 100%-purity result does not generalize; report.

**H3 — cross-bearing healthy coverage (the FAR fix).** Construction
on {4 healthy bearings}, holdout = {2 unseen healthy bearings}
(rotating folds over K001–K006): realized FAR on unseen-bearing frames
falls below 2% (vs the subset's within-bearing 4.3% at designed 0.5%),
and decreases monotonically as construction bearings go 1→2→4.
*Kill*: FAR on unseen healthy bearings stays > 4% at 4 construction
bearings → healthy bearing identity is NOT absorbable as regime
variation at this feature granularity; the deployability story for
per-asset monitoring changes materially (fleet-level normality needs
per-unit calibration) — report prominently, not as a footnote.

**H4 — FAR/detection pairing (protocol law, §5.5).** Every FAR in
every table is paired with detection from the same run. Not a
hypothesis — a standing rule; listed so its violation is auditable.

**H5 — artificial vs real (secondary, descriptive).** Same-ring
comparisons (e.g., KA01 artificial vs KA04 real, both outer extent 1):
report margin distributions side by side. No directional claim
pre-committed; whatever the geometry says.

## 3. Protocol (frozen)

Adapter: `tests/paderborn/paderborn_datasets.py` d=27 vocabulary, UNCHANGED from
the subset run (qualification law: no fault-frequency alignment).
Detector: the frozen support-floor path, UNCHANGED. Splits: always by
recording; healthy holdout additionally by bearing (H3). No constant
of any kind may be revised after the first full-dataset run; feature
changes would require a new pre-registration section, logged.

## 4. Data transfer note

Official server / Zenodo / Kaggle / HuggingFace / Google Drive bulk
paths are unavailable from this environment (Drive MCP returns file
content base64-inline through the conversation — unusable at GB
scale). Fixed path: rar assets on a GitHub Release of this repository
(≤2 GB per asset; split archives where needed), downloaded directly
and extracted locally (p7zip installed; rar4/5 support verified on
first asset). Priority order if uploaded incrementally: K002–K006 →
KI04/KI18/KI16 → KA04/KA22/KA16 → remainder.

## 5. Results (run 2026-07-10; 32 bearings, 40,944 frames, d=27; 3 non-finite frames dropped, 1 malformed recording skipped — both logged)

Primary model: fit K001–K004, unseen healthy K005/K006. **Its unseen-
healthy FAR is 66.37%** (see H3) — so, by our own pairing law, the
absolute detection percentages under this model are NOT deployment
numbers; what survives the miscalibrated operating point is the margin
ORDERING (median differences), which is what H1 tests.

### H1 — SUPPORTED (the core claim, both ladders)

Pooled: inner Spearman ρ(extent, per-bearing median) = **+0.845**,
adjacent-group CIs [+8.4,+9.3] and [+1.9,+2.8] IQR; outer ρ = +0.866,
CI [+12.8,+16.7]. Per the pre-registered per-condition wording:
**12 of 12 condition × adjacent-pair tests ordered** (inner 8/8, outer
4/4), zero reversals — the kill condition is nowhere near triggered.
Real fatigue-pitting extent maps to monotonically deeper support
margins under all four operating conditions.

Identity-noise floor, disclosed: extent-1 medians span −0.2 (KI14) to
+17.2 (KI04) — individual bearings overlap across extent labels; the
ladder stands on group medians, not on every individual. KB24
(combined damage, extent 3) shows the deepest margin of all (+92.7),
consistent with severity.

Scope of what H1 proved, stated precisely: this is a
**cross-sectional, same-spec, cross-bearing severity validation**
(same bearing type, same rig, same measurement chain, same four
operating conditions, damage position/type/extent known) — not a
longitudinal same-bearing degradation track; a longitudinal test is
the stronger future validation and does not invalidate this one. H1
verified damage-severity ordering within operating conditions; it did
not verify that each damaged frame was matched against the GMM
component semantically corresponding to its condition (see §6a — at
multi-bearing scale the components do not carry that meaning). Central
sentence: *the physical ordering of real bearing damage was preserved
in the support margin across all operating conditions, despite
substantial between-bearing healthy variability.*

### H2 — KILLED on purity, with a confound

BIC selected K = 5 (≥ 4: acceptable), but regime↔condition purity on
unseen healthy is **62.5% < 70%**. Confound, noted rather than argued
away: purity was measured on frames of which 66% are outside the
fitted support (H3), where regime assignment is extrapolation by the
formulation's own §3.3 logic. The subset's 100% purity (same-bearing
holdout) remains valid; cross-bearing purity is not currently
measurable independently of H3's failure.

### H3 — KILLED, exactly as the kill condition anticipated (the finding)

Unseen-bearing FAR: 66.37% / 0.00% / 59.80% across rotating folds
(mean 42.06% ≫ 4% kill threshold); construction-size curve 99.96% →
98.63% → 66.37% (1→2→4 bearings) — monotone improvement, nowhere near
design rate.

**What H3 rejected is an implementation hypothesis — that the current
flat pooled GMM with a global support floor transfers its designed FAR
to unseen healthy bearings — not population-level normality in
principle.** All six bearings are healthy by the official fact sheets;
flagging 66% of K005/K006's frames therefore does not mean those
bearings are anomalous — it means the current normal support
under-represents the healthy population's **normal tolerance layer**
(between-bearing variation: run-in history, manufacturing tolerance,
mounting, lubrication and surface state; see §7). The deployability
reading today: per-asset monitoring (construction data from the same
unit; subset FAR 4.3%) is the **currently validated** mode, and
fleet-level normality requires a representation of the between-bearing
tolerance layer — the subject of the follow-up pre-registration
([experiment_plan_paderborn2.md](experiment_plan_paderborn2.md)).
Simply widening thresholds is not that representation: it risks
swallowing mild damage into the healthy buffer. *(Wording of this
paragraph refined after conceptual review; verdict, numbers, and kill
status unchanged — original phrasing in commit 088bc8e.)*

Post-hoc observation (flagged as such, not pre-registered): the folds
are strongly asymmetric — unseen K001/K002 score 0.00% FAR under a
K003–K006 model, while K005/K006 sit far outside a K001–K004 model.
Bearing individuality is directional; K001's much longer run-in
(>50 h vs 1–19 h) is a candidate physical explanation for span
differences, untested here.

### H5 — descriptive

At the same nominal extent (1), artificial damage is more visible than
real pitting: inner KI01 (EDM) median +45.5 vs real +9.5…+17.2 (and
KI14 at −0.2); outer KA01 +17.5 vs KA04 +15.8 / KA22 +4.0. Weakest
detections cluster in artificial drilling/engraver damages (KA07/KA08,
KI05/KI07: 9–50% under this model). No directional claim was
pre-committed; these are the distributions.

### Reading

The severity thesis survived its hardest test to date (real damage,
physical extents, all conditions, zero reversals), while the
transferability thesis met a real limit: operating conditions are
absorbable structure (within-bearing: subset 100% purity), bearing
individuality is not — at this vocabulary. Both facts are now
measured, and the second one was caught by a kill condition we wrote
before seeing the data.

## 6. Post-hoc analyses (NOT pre-registered; prompted by the conceptual question "regimes are operating modes — shouldn't damaged/healthy be paired within the same condition?")

Three measurements, all on the primary fit (K001–K004):

**(a) Do the discovered regimes mean operating modes at multi-bearing
scale? NO.** Component→condition map of the K=5 mixture: three
components map to N15_M01_F10, none to N15_M07_F10; regime↔condition
purity is 42.3% on damaged frames and 37.5% on unseen healthy — the
labels do not mean conditions for anyone. At single-bearing scale the
same machinery gave 100% purity. **Bearing identity competes with
operating condition for mixture capacity** (and the frozen K ≤ 5 cap
sits far below the true 4-condition × 4-bearing structure). This is
H3's failure seen from the regime side.

**(b) Component-conditional support floor helps.** Keeping the pooled
structure but setting the unknown floor per mixture component (the
unknown-channel analogue of the architecture's per-regime scorer
thresholds): unseen FAR 66.4% → 51.2%, and the inner ladder's
separation widens (10.3/19.1/21.4 → 17.9/43.9/49.1 IQR) with ordering
intact. Naming rule, per (a): because the components do NOT carry
operating-condition semantics at multi-bearing scale, this is a
**component-conditional support floor** — it may not be called an
operating-regime-conditional floor until the semantic correspondence
is verified. Direction is right (consistency with the per-component
scorer thresholds), coverage is not solved (FAR 51%): candidate B of
the follow-up pre-registration, not a default change.

**(c) What the backfire actually refuted: the hard partition.**
Separate per-condition models and floors (condition labels are
operational metadata, not anomaly labels — legitimacy intact): unseen
FAR improves to 42.0% **but H1's ordering is destroyed in every
condition** (extent-3 medians fall to or below extent-1). The failure
is attributable to the partition, not to using condition metadata:
splitting the geometry re-defines the distance scale per condition
(destroying the margins' common severity scale), leaves ~500-frame
floors (quantile noise), and makes within-condition variance
identity-dominated. Refuted: *split the geometry by condition*.
Remaining candidate: *shared geometry with conditional calibration*
(floor/tail only) — candidate C of the follow-up pre-registration.

**Net reading**: at single-asset scale, semantic operating regime,
latent mixture component, and calibration unit coincided (subset:
100% purity); at multi-bearing scale they come apart (§7 separates
the three). The correct candidate direction is shared severity
geometry with conditional calibration; the between-bearing tolerance
layer itself (§7) is what remains unrepresented. All numbers here are
post-hoc and exploratory; any promotion to defaults goes through the
new pre-registration
([experiment_plan_paderborn2.md](experiment_plan_paderborn2.md)).

## 7. Conceptual model: the healthy population envelope (normal tolerance layer)

Added after §5/§6; interprets, does not alter, the verdicts.

**Fixed facts.** The six healthy bearings K001–K006 differ in run-in
history (K001 >50 h; K002–K006 1–19 h), and both healthy and damaged
bearings were measured under the same four operating conditions. The
differences among healthy bearings therefore are not operating-
condition effects; they are **normal between-bearing variation** —
run-in history, manufacturing tolerance, surface and lubrication
state, mounting, unit-specific vibration/current signatures. Since the
fact sheets certify all six as healthy, this variation is not anomaly:
it is the volatility — the normal buffer — of a same-spec healthy
population. Normal structure is not one thin line; it is a
multidimensional **healthy envelope per operating condition**.

**Decomposition (conceptual, not yet a fitted model):**

```
x(i, c, t) = μ(c) + b(i) + ε(i, c, t) + δ(i, c, t)

μ(c)  operating-condition normal center
b(i)  between-bearing healthy offset          (normal tolerance layer)
ε     within-bearing normal fluctuation
δ     damage displacement                     (zero when healthy)
```

NSAD's target is δ, never b(i). H1 shows δ's ordering survives b(i)
(group medians beat the identity-noise floor); H3 shows the current
flat pooled support conflates b(i) with δ for unseen units.

**Three meanings of "regime", now separated:**

1. **semantic operating regime** — the physical operating mode
   (speed / torque / load);
2. **latent mixture component** — the cluster the GMM builds from
   observed geometry;
3. **calibration unit** — the unit that owns a threshold or support
   floor.

At single-asset scale the three coincided (subset: 100% purity). At
multi-bearing scale they come apart: components split along
condition × identity (§6a), so component-conditional calibration
(§6b) is not yet operating-regime-conditional, and hard partitioning
by known condition (§6c) sacrifices the shared severity scale.

**Architecture hypothesis for the follow-up** (pre-registered in
[experiment_plan_paderborn2.md](experiment_plan_paderborn2.md)):
represent normal structure hierarchically — condition effect +
between-bearing tolerance + within-bearing fluctuation — sharing the
d=27 adapter, feature geometry, severity-margin scale, NSAD core, and
three-state semantics, while conditioning only normal centers, healthy
buffers, floors, and alarm operating points. Separate the two roles
one margin currently plays: a **severity_margin** (non-saturating
distance on the shared geometry, the ordinal severity scale held
common across conditions) and a **calibrated_alarm_score** (tail
probability under condition + population + unit variation, the
FAR-controlling decision variable). One margin should not carry both
jobs.

**The two pillars of this validation:**

1. *The physical severity of real damage was preserved as support-
   margin ordering under cross-sectional, cross-bearing conditions.*
2. *A healthy population carries non-negligible between-bearing
   variability, and the current flat pooled-support model could not
   represent that normal buffer.*

> Normal operating conditions form structured regimes within an
> asset, while healthy population variability forms an additional
> tolerance layer that must not be mistaken for damage.

In one sentence: **the severity geometry transferred; the current
population alarm calibration did not.**
