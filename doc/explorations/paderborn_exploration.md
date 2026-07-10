# Post-freeze exploration — Paderborn bearing subset (vibration adapter)

**Status: exploratory, NOT part of the frozen paper evidence base.**
Second entry in the adapter-validation series (first:
[hydraulic_exploration.md](hydraulic_exploration.md)). Target: the
**vibration/acoustics adapter** — until now inventory-only in the §13.5
registry — and the adapter view's central regime claim on rotating
machinery: *operating condition = regime, bearing damage = support
departure, current + vibration = joint structure*.

Data: Paderborn University Bearing Data Center (Lessmeier et al. 2016).
Official server and Zenodo are unreachable from this environment; the
[laiadc/PFM_Bearing_Fault_Detection](https://github.com/laiadc/PFM_Bearing_Fault_Detection)
GitHub mirror carries a subset used here: **K001** (healthy), **KA01**
(artificial outer-ring damage), **KI01** (artificial inner-ring
damage), each under two operating conditions (N09_M07_F10 900 rpm /
N15_M07_F10 1500 rpm), 20 recordings × 4 s. Channels: vibration + two
phase currents @64 kHz, force/speed/torque @4 kHz, temperature.
Loader: `tests/paderborn/paderborn_datasets.py`; experiment:
`python -m tests.paderborn.exp_paderborn`. `PADERBORN/` is gitignored.

**Subset limits, stated up front**: one healthy bearing (FAR is
within-bearing, across held-out recordings — cross-bearing healthy
generalization is NOT testable here), artificial damages only, single
damage extent (no severity-stage grading), two of the four official
operating conditions.

## Adapter (qualification-law compliant)

Per 0.25 s frame (d = 27): vibration log-RMS, 12 log-spaced band
energies (20 Hz–25.6 kHz), spectral entropy, and 6 **generic** envelope
band energies (|Hilbert| spectrum, 5–1000 Hz, log-spaced — deliberately
NOT aligned to any bearing fault frequency: BPFO/BPFI alignment would
name a fault class and violate §13.2 law 3); per phase current log-RMS
+ spectral entropy; mean speed/torque/force. Splits are BY RECORDING
(frames within a recording are correlated; a frame split would leak).

Detector: the frozen support-floor path, untouched (z-norm on fit,
PCA 90% for d>16, GMM BIC auto-K, nested out-of-sample 0.5% floor).

## Results

**Q1 — regimes = operating conditions, discovered not told.** BIC
selected K = 2 with two conditions in the data, and on held-out normal
frames the regime↔condition assignment is **100% pure** (regime 0 =
all N09, regime 1 = all N15). The adapter view's premise — operating
conditions are what the regime layer should absorb — held literally.

**Q2 — detection through the fault-agnostic vocabulary** (FAR pair
below):

| Bearing (damage) | Condition | Detection | Median margin |
|---|---|---:|---:|
| KA01 (outer ring, artificial) | N09 | 100.0% | +145 IQR |
| KA01 | N15 | 100.0% | +205 IQR |
| KI01 (inner ring, artificial) | N09 | 100.0% | +37 IQR |
| KI01 | N15 | 100.0% | +273 IQR |

Every damaged frame in the subset is deep outside the healthy support,
under both operating regimes, with no fault-frequency knowledge
anywhere in the pipeline.

**Q3 — the FAR pair: 4.30% on held-out healthy recordings vs 0.5%
designed (×8.6).** The third occurrence of the coverage lesson
(transfer test ×32 in-sample; hydraulic leak 3.6–4.1%): a single
healthy bearing's 24 fit recordings, with correlated frames inside
each recording, under-cover the healthy variation of its own held-out
recordings. Margins are so deep (+37 to +273 IQR) that detection is
untouched, but the operating point's designed meaning is not being
honored — more healthy bearings (K002–K006 in the full dataset) are
the fix, not a threshold adjustment. Reported as-is.

## Registry consequences (§13.5)

- **Vibration/acoustics** moves from "partial inventory" to
  "detection validated on a post-freeze physical subset (generic
  envelope bands implemented); resonance extraction still
  unimplemented; FAR coverage requires multi-bearing healthy data".
- The regime claim of the adapter view now has a rotating-machinery
  instance: **condition-as-regime discovered by BIC at 100% purity**.

## What the full dataset would add (future work)

Cross-bearing healthy holdout (K002–K006) for an honest FAR; real
accelerated-life damages (vs artificial); damage-extent levels for a
third severity-gradation test; all four operating conditions (K = 4
regime discovery); current-only vs vibration-only ablation for the
joint-structure claim.
