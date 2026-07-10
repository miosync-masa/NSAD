# Pre-registered plan #4 — longitudinal validation on run-to-failure bearings (NASA IMS)

**Status: EXECUTED — results and verdicts in §4.** H1L SUPPORTED 3/3
(progressive margins on real run-to-failure); H2L supported at 1/3
failures (one healthy-FAR miss disclosed); **H3L KILLED 3/3 — the E3
fleet margin is 11–14% of life late, or silent, at failure**; H4L
same-shaft transmission finding; milling median ρ +0.38. §§1–3+A1
untouched since registration. Written
2026-07-10, before the data transfer and before any implementation is
run. Successor to
[experiment_plan_paderborn3.md](experiment_plan_paderborn3.md), whose
§7 left one registered standing limitation: cross-sectional data
cannot test the damage phase of a commissioned unit — in particular
the risk that a personal scale estimated at commissioning compresses
later damage margins. Run-to-failure data is the missing class; this
plan tests it.

**Data**: IMS Bearing Data Set (J. Lee, H. Qiu, G. Yu, J. Lin, and
Rexnord Technical Services, IMS Center, University of Cincinnati),
NASA Prognostics Data Repository, NASA Ames. Four bearings on one
shaft, constant 2000 rpm, run to failure over weeks; vibration
snapshots (1 s @ 20 kHz) every ~10 minutes. Test 1: 8 channels (2 per
bearing), failures at bearing 3 (inner race) and bearing 4 (roller).
Test 2: 4 channels, failure at bearing 1 (outer race). Test 3:
reported failure at bearing 3. **Tests 1 and 2 are primary; test 3 is
descriptive only** (its labeling is less certain in the literature).
Secondary set: Milling Data Set (A. Agogino, K. Goebel, BEST Lab, UC
Berkeley), same repository — progressive flank wear VB as a
CONTINUOUS physical severity ground truth; descriptive only.
We acknowledge the NASA Prognostics Data Repository and the data
donators per the repository's request.

## 1. Fixed protocol (before download)

- **Frames**: each 1 s snapshot → four 0.25 s frames (the Paderborn
  FRAME_S, unchanged).
- **Adapter**: the existing fault-agnostic vibration vocabulary,
  expressed sample-rate-independently (the same construction rule as
  Paderborn's, where 25.6 kHz = 0.8 × Nyquist at 64 kHz): per
  channel — log RMS; 12 log-spaced band energies from 20 Hz to
  0.8 × Nyquist (= 8 kHz at 20 kHz sampling); spectral entropy; 6
  generic envelope band energies (5–1000 Hz, unchanged). d = 20 per
  channel; bearings with two channels concatenate (d = 40). No
  fault-frequency alignment, no channels beyond vibration (IMS has
  none — a data-availability fact, not a feature change).
- **Detector**: the frozen support-floor path (z-norm → PCA 90% for
  d > 16 → GMM BIC auto-K → nested out-of-sample 0.5% floor),
  unchanged. **Per-asset mode**: construction data is the unit's own
  early life — the deployment mode validated in #2.
- **Life windows** (fractions of each test's snapshot count, fixed):
  construction = first 20%; healthy-phase evaluation window =
  20–50% (assumed healthy; if onset is detected inside it, the
  healthy-FAR interpretation is conditioned and disclosed);
  end-of-life phase = final 5%.
- **Sustained onset** (fixed definition): the first snapshot index
  from which ≥3 consecutive snapshots have median frame margin > 0;
  lead time = time from sustained onset to end of test.
- Per-bearing models: each bearing's detector sees only its own
  channel(s). One model per bearing per test.
- Production defaults unchanged regardless of outcome.

## 2. Hypotheses (kill conditions fixed)

**H1L — statistical progressiveness of the margin (the longitudinal
severity claim).** *(Amended pre-execution, A1 below — pointwise
monotonicity removed.)* For each failed bearing (test1-B3, test1-B4,
test2-B1), over the post-construction life divided into five equal
quintiles:
  (a) the end-of-life median severity margin exceeds the
      healthy-phase median (bootstrap 95% CI on the difference
      excluding 0);
  (b) **alarm occupancy** (fraction of frames with margin > 0 per
      quintile) increases toward failure: Spearman
      ρ(quintile index, occupancy) > 0;
  (c) distributional deepening: the final quintile's median margin
      exceeds the first post-construction quintile's (bootstrap CI
      excluding 0).
Temporary regressions of the raw margin (self-healing, debris
migration, lubrication changes) are expected physical behavior and do
NOT count against H1L.
*Kill*: (a), (b) or (c) fails for ≥2 of the 3 failed bearings.

**H2L — lead time and healthy-phase FAR (paired).** Sustained onset
exists and precedes end of test for each failed bearing; report lead
time in hours and as fraction of life. Healthy-phase FAR (20–50%
window) reported per bearing, paired with the onset/detection column.
*Kill*: no sustained onset before end of test for ≥2 of 3 failed
bearings, or healthy-phase FAR > 10 × design (i.e. > 5%) on ≥2 of 3
failed bearings' own channels (with the contamination caveat above).

**H3L — the scale-compression risk (#3's open question).** Compare
sustained-onset index under (a) the raw unit floor and (b) the
E3-style location+scale-standardized margin, both calibrated on the
same construction window.
*Kill*: standardization delays onset by more than 1% of life on ≥2 of
3 failed bearings — the risk is real; report prominently either way.

**H4L — same-shaft controls (no kill; the pair for H1L).** Non-failed
bearings' FAR over post-construction life, reported per bearing.
Elevated control FAR is reported as a finding (shared-shaft vibration
transmission is physically plausible), never silently excluded.

**M — Milling (descriptive, registered).** Per case: construction on
the first 3 runs; severity margin per run; Spearman ρ(margin, VB)
over runs with recorded wear. No kill; the question is whether the
margin tracks a continuous physical wear variable.

## 3. Execution discipline

Download → inspect layout → loader (`tests/ims/ims_datasets.py`) + runner
(`tests/ims/exp_ims.py`) → **implementation freeze-commit before reading
any result** → single run → results appended below §3, nothing above
edited → verdicts SUPPORTED / KILLED / INCONCLUSIVE. FAR always
paired with detection/lead-time from the same run. Post-hoc analyses,
if any, in a separate marked section.

## A1 — Pre-execution amendment (logged 2026-07-10, before download inspection and before any implementation run)

Directive: this plan verifies **E3's longitudinal validity only,
under the frozen configuration** — it is NOT an RUL-prediction study,
and no RUL estimation appears anywhere in it. Primary evaluations are
fixed as: early-healthy FAR; first sustained alarm time; lead time to
failure; **alarm persistence rate** (occupancy after onset); near-end
severity margin; cross-bearing reproducibility.

H1L's original "positive margin trend over the final 30%" was a
pointwise-monotonicity criterion and has been replaced (above) with
**statistical progressiveness**: real damage signals can temporarily
recover (spall smoothing/self-healing, debris migration, lubrication
state), so pointwise monotonicity is physically wrong as a kill.
Progressiveness is instead measured as: later-life distributions
deepen (quintile medians, CI), alarm occupancy rises toward failure
(Spearman over quintiles), and sustained-departure episodes lengthen
— reported descriptively alongside the registered (a)/(b)/(c) tests.
No other hypothesis, constant, or kill condition was changed; the
amendment precedes data inspection.

## 4. Execution results (run 2026-07-10; nothing above this section edited after the run)

Implementation: `tests/ims/ims_datasets.py` + `tests/ims/exp_ims.py`, frozen at
b387a4f before these results were read. Command:
`python -m tests.ims.exp_ims`. Tests 1/2 primary (3 failed bearings),
test 3 descriptive; 2156 / 984 / 6324 snapshots (828 / 164 / 1073 h).

### Per-bearing table (FAR always paired with onset/lead/persistence)

| Test | Bearing | healthy-FAR (20–50%) | sustained onset | lead | persistence | occupancy ρ | EOL-vs-healthy CI | Q5-vs-Q1 CI |
|---|---|---:|---:|---:|---:|---:|---|---|
| 1 | B3 **failed** (inner) | 6.92% | 85.0% of life | 79 h | 93.5% | +0.90 | [+20.1, +26.4] | [+8.6, +10.4] |
| 1 | B4 **failed** (roller) | 1.08% | 69.0% | 148 h | 98.2% | +1.00 | [+56.6, +58.7] | [+54.3, +55.3] |
| 2 | B1 **failed** (outer) | 1.52% | 54.6% | 74 h | 99.6% | +0.95 | [+390.8, +519.2] | [+218.6, +239.1] |
| 1 | B1 control | 2.05% | 99.0% | 10 h | 100% | — | — | — |
| 1 | B2 control | 1.35% | 83.7% | 84 h | 21.9% | — | — | — |
| 2 | B2/B3/B4 controls | 0.08 / 3.89 / 0.51% | 79.2 / 75.0 / 71.2% | 34–47 h | 97–100% | — | — | — |
| 3 | B3 failed (descriptive) | 1.07% | 70.9% | 313 h | 33.0% | +0.97 | [+37.9, +138.7] | [+3.2, +3.5] |
| 3 | B4 control (descriptive) | 16.20% | 32.2% | 730 h | 38.3% | — | — | — |

### Verdicts (pre-registered kill thresholds: ≥2 of 3 failed bearings)

- **H1L — SUPPORTED, 0 failures.** All three primary failed bearings
  pass (a) end-of-life vs healthy CI > 0, (b) occupancy rising over
  quintiles (ρ +0.90 / +1.00 / +0.95), and (c) Q5-vs-Q1 deepening.
  Statistical progressiveness of the margin holds on real
  run-to-failure degradation — with amplitudes ordered like physical
  stories (outer-race t2-B1 reaching +463 IQR at end of life). The
  descriptive test-3 failed bearing shows the same pattern (ρ +0.97).
- **H2L — SUPPORTED at 1 of 3 failures.** Sustained onset exists for
  all three (leads 74–148 h; persistence 93.5–99.6%). One failure
  recorded honestly: t1-B3's healthy-window FAR is 6.92% (13.8× the
  0.5% design) — genuinely elevated false alarms, not early onset
  (its Q1–Q4 occupancies are 1–2%). Per-asset FAR at design rate is
  not automatic on this rig; 2 of 3 failed bearings and most controls
  sit at 0.1–2%.
- **H3L — KILLED, 3 of 3. The headline.** The E3 fleet margin
  (reference bearing's geometry + the unit's commissioning
  location/scale) delays sustained onset by **+13.96% of life**
  (t1-B3), **misses onset entirely** (t1-B4), and delays by
  **+11.18% of life** (t2-B1). The #3 standing risk is real on
  run-to-failure data: fleet-transferred alarm calibration reaches
  design FAR on healthy data (#3) but **compresses damage-phase
  margins enough to be late — or silent — at failure**. Disclosed
  design note: this H3L statistic bundles reference-geometry mismatch
  and personal-scale compression (both are parts of the E3 fleet
  mechanism as registered); decomposing the two is future work.
- **H4L — controls (finding, as anticipated).** Every same-shaft
  control shows a late-life sustained onset with high persistence
  (t2 controls: 71–79% of life, persistence 97–100%, at healthy FARs
  of 0.1–3.9%) — physically consistent with shared-shaft vibration
  transmission from the failing neighbor; the shaft is one mechanical
  system and "control" is only approximately true. Test-3 B4's
  16.2% healthy FAR and 32%-of-life onset is disclosed as-is
  (test 3's data quality is the reason it was registered as
  descriptive).
- **M — milling (descriptive).** ρ(margin, VB) median +0.38 over 14
  cases; 11 of 14 positive (up to +0.92), two near zero, one strongly
  negative (case 12, −0.82). The margin tracks continuous physical
  wear in most but not all cutting conditions — reported without
  smoothing.

### Reading

The longitudinal loop closes with a clean division: **per-asset
normal structure from a unit's own early life detects its own
degradation progressively, persistently, and with useful lead time
(H1L+H2L); fleet-style E3 commissioning — the #3 cross-sectional
winner — is late or silent in the damage phase (H3L).** Deployment
shape: E3 commissioning is an alarm-origin bridge for the healthy
phase; the severity geometry and the damage-phase alarm should come
from the unit's own accumulated normal data as soon as it exists.
The #3 conclusion is now bounded on both sides by measurement:
its FAR transfer is real (cross-sectional), and its damage-phase
limit is real (longitudinal) — both from pre-registered runs.

## 5. Interpretive refinement (post-execution, logged; verdicts and numbers unchanged)

**H2L, split for the reader** (the registered verdict — supported at
1/3 failures — stands; the split is presentational):
- **H2L-a — early, persistent detection: SUPPORTED 3/3.** Sustained
  onset on every failed bearing, leads 74–148 h, persistence
  93.5–99.6%.
- **H2L-b — design-rate healthy FAR from self-reference: NOT
  universally supported.** t1-B3's 6.92% is a genuine healthy false
  alarm rate (occupancy-verified, not early onset). Self-history is
  necessary for damage detection; it does not by itself guarantee
  probability calibration.

**H3L, stated as the central proposition of #4:**
*cross-sectional calibration success does not imply longitudinal
detection validity.* Median–IQR standardization excels at healthy
distribution alignment; on a unit with large healthy IQR, the damage
displacement is divided down with it — absolute anomaly growth is
compressed. E3 is therefore not killed as a mechanism; **its role is
bounded: healthy commissioning / admission calibration, never the
failure alarm.**

**H4L, semantics corrected: detection vs localization.** The
same-shaft controls' late-life onsets are not (only) false alarms:
vibration from a local fault propagates through shaft, housing, and
load path, so each sensor observes the MACHINE SYSTEM, not only the
bearing beneath it. NSAD succeeded at system-level anomaly detection;
fault **localization** (which bearing, which component) is a separate
spatial-inference task (arrival order, amplitude ratios, phase,
propagation structure across sensors) — a scope statement about what
a fault detector means, not merely future work.
