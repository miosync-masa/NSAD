# Post-freeze exploration — UCI hydraulic rig (id 447)

**Status: exploratory, NOT part of the frozen paper evidence base.**
Run after the manuscript freeze because the dataset offers something no
corpus in the paper does: **physically labeled, graded degradation
stages** (valve 100/90/80/73%, accumulator 130/115/100/90 bar, cooler
100/20/3%, leak 0/1/2) on a real rig — i.e. ground truth for the
severity-gradation claim, previously demonstrated only on designed
ghost geometry.

Data: Condition Monitoring of Hydraulic Systems (ZeMA / Helwig,
Pignanelli & Schuetze 2015), UCI id 447, CC BY 4.0; 2205 constant
60-second load cycles, 17 sensors at 1/10/100 Hz. Obtained via the
Machine-Learning-FGA/Hydraulic-systems GitHub mirror (UCI archive not
reachable from this environment; files identical). Loader:
`tests/hydraulic/hydraulic_datasets.py`; experiment: `python -m
tests.hydraulic.exp_hydraulic`. Data dir `HYDRAULIC/` is gitignored.

## Design

**Structural fact that drives the setup**: only 10 of 2205 cycles have
all four components nominal — the rig varies components
simultaneously. "Normal" is therefore defined **per target component**:
cycles where the target is nominal (and the stable flag is 0), with the
other three components varying freely *inside* the normal set. Those
variations are operating conditions the regime layer must absorb — the
"same value, different meaning" setting on real hardware.

Detector = the paper's frozen support-floor path, untouched
(`exp_frozen_transfer._ours`): z-norm on fit split, PCA 90% for d>16,
GMM BIC auto-K full-cov, nested out-of-sample 0.5% likelihood floor.
No per-dataset tuning. Frames = per-cycle summaries on a
fault-agnostic granularity ladder: `mean` (d=17) → `mean+std` (d=34) →
`seg6` phase-resolved sixth-cycle means (d=102).

## Results (seg6 unless noted; FAR always paired with detection)

| Target | held-out FAR (designed 0.5%) | detection per stage (mild→severe) | median margin per stage (IQR) | verdict |
|---|---|---|---|---|
| **cooler** | **0.00%** | **100% / 100%** | **+2699 → +8183, monotone** | severity gradation confirmed on physical labels |
| valve | 0.00% | 2.5% / 12.8% / 15.3% | −2.5 / −2.5 / −2.4 | granularity finding: switching-*lag* fault lives in 100 Hz transients; invisible at cycle summaries (mean d=17: ~1%); detection *rate* becomes monotone with phase resolution but stays weak |
| leak | 4.08% (×8 drift) | 54% / 57% | +0.2 / +0.3 | partial; FAR drift flags normal-pool heterogeneity the K=2 structure under-covers — reported as-is, not tuned away |
| accumulator | 0.69% | 19% / 24% / 20% | −6.1 / −6.1 / −6.0 | largely below floor at this granularity (known hardest target in this dataset's literature) |

Cooler `mean` variant: identical detection (100/100), margins
+2336 → +6364 — the result is not an artifact of the seg6 features.

## Round 2 — cycle-phase features (the missing vocabulary)

The valve finding predicted its own fix: a switching *lag* is a
circular shift within the cycle, and the legacy frequency features
(`lambda3_detector/features/extractor.py`) are built from |FFT| — which
is **exactly invariant under circular shifts**. The lag lives entirely
in the discarded spectral phase. This is now a tested mechanism, not an
interpretation: `tests/core/test_cycle_phase.py` asserts that a pure lag
leaves every frequency-magnitude feature unchanged to 1e-9 while the
new phase features move monotonically with it.

The missing piece was added to the legacy extractor as
`extract_cycle_phase_features(cycle, n_bins)` — a normalized-phase
profile (12 bin means + slopes) plus a generic timing vocabulary
(`peak_pos`, `trough_pos`, `rise_time`, `settle_time`). Fault-agnostic:
nothing is aligned to any component.

Results with the same frozen detector path:

| Target | `shape` d=68 (timing only) | `phase12shape` d=272 | reading |
|---|---|---|---|
| cooler | 26% / 96% (magnitude info lost) | **100% / 100%, FAR 0.51%, margin +388→+1490 monotone** | needs both layers; phase+shape keeps the gradation AND lands FAR on design |
| **valve** | **2.2% / 81.7% / 100%**, margin −2.6 / +1.1 / +9.8 | 1.9% / 11.9% / 100% (profile dilutes timing at d=272) | **the timing vocabulary sees the lag** — detection and margin both ordered by degradation; mild stage (90%) remains near-normal, plausibly because "90% switching behavior" barely displaces timing |
| **leak** | 21% / 25% | **82% / 91%, margin +2.8→+7.6 monotone** | leak expresses in the within-cycle *profile*; FAR still drifted (3.6–4.1% across ALL variants — the coverage finding is robust, not feature-dependent) |
| accumulator | ~20%, below floor | ~20%, below floor | invariant across every granularity tried → representation-level observability limit of this sensor set, not a feature problem |

Two-layer conclusion (as anticipated): magnitude profile and timing
vocabulary are complementary — timing alone loses the cooler's
steady-state information, means alone lose the valve's lag; the
combined set is the first variant that sees three of four components
while holding cooler's FAR at design (0.51% vs 0.5%).

## Reading

1. **The severity-gradation claim survives contact with physical
   labels** where the fault expresses in the covered feature space:
   cooler degradation 100→20→3% maps to a monotone, *hugely* separated
   non-saturating margin (three orders of magnitude above the floor,
   stage-separated by ×3) at 0.00% held-out FAR, under the frozen
   config, with background component variation absorbed as regimes
   (BIC chose K=2).
2. **Granularity, not detector, is the binding constraint for
   transient faults**: the valve fault is a timing shift inside a
   60-second cycle; per-cycle summaries destroy it (the paper's §4.2
   channel-mean disclosure, reproduced at a different time scale).
   The honest fix is finer within-cycle temporal features, not
   thresholds.
3. **FAR drift as a coverage instrument**: the leak experiment's ×8
   realized-FAR drift on held-out *normal* cycles is the transfer
   test's lesson recurring in the wild — when the normal pool is
   heterogeneous beyond what the fitted structure covers, the designed
   rate silently degrades. The pairing rule (FAR with detection, §5.5)
   is what makes this visible instead of flattering.
4. **The observability chain closed in one loop**: finding (valve
   invisible) → mechanism (|FFT| is circular-shift invariant; tested)
   → vocabulary (cycle-phase features in the legacy extractor) →
   recovery (81.7/100% at the two severe stages, margin ordered).
   The detector was never touched; only what it was allowed to see.
5. Nothing here enters the paper; candidate future-work line: the
   two-layer cycle vocabulary (magnitude profile + timing) as the
   standard input convention for cyclic machines, cross-channel phase
   lag as its next feature, and the hydraulic rig as a second
   physical-label severity benchmark with pre-registered hypotheses
   (margin↔stage ordering, target-conditional normality, granularity,
   FAR-drift-as-coverage).
