<p align="center">
  <img src="https://www.miosync.link/github/0_4.jpg" alt="Lambda³" width="400"/>
</p>

<h1 align="center">📕 Normal-Structure Anomaly Detection — Lambda³ NNNU</h1>

<p align="center">
  <strong>Share the geometry, commission the individual, and monitor degradation against its own history.</strong><br>
  We do not learn anomalies; we clean normality.<br>
  No anomaly-shape learning. No neural networks. No per-dataset threshold tuning.
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="#"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License"></a>
  <a href="#"><img src="https://img.shields.io/badge/pre--registrations-5%2F5%20executed-blue.svg" alt="Pre-registrations 5/5"></a>
  <a href="https://colab.research.google.com/drive/1OObGOFRI8cFtR1tDS99iHtyWMQ9ZD4CI"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="colab"></a>
</p>

---

## The Problem

Generic one-class anomaly detection collapses two different sources of deviation into the same outlier score:

1. **normal variation between healthy individuals** of identical specification — run-in history, manufacturing tolerance, mounting, lubrication;
2. **change caused by physical damage.**

The consequence is a deployment dilemma with no tuning escape. Make the normal support narrow, and unseen healthy units false-alarm (Paderborn: **42% mean FAR** on unseen healthy bearings under a flat pooled support). Widen the support to absorb them, and shallow damage is swallowed with it (extent-1 absorption **11.9% → up to 41.1%**, with detection dropping and severity ordering damaged).

**The question this repository answers, with pre-registered experiments on physical bearing data:**

> How can a deployable alarm design handle distinct-but-same-spec healthy individuals without losing physical damage severity and longitudinal degradation progression?

---

## The Answer — Five Pre-Registered Experiments

All plans were written with hypotheses and kill conditions fixed **before** execution; implementations were frozen in commits **before** results were read. Successes, failures, and limitations are all retained — the failures are load-bearing.

### Pillar 1 — Damage severity lives on a shareable geometry

On Paderborn's real accelerated-lifetime damage (different physical bearings, same specification), the physical damage extent was **order-preserved on a shared severity margin** across bearing individuals:

- inner-ring ladder: **8/8** condition-pair tests ordered
- outer-ring ladder: **4/4** ordered
- **zero reversals**; Spearman ρ(extent, median margin) = **+0.845 / +0.866**

*The geometry that represents damage depth transfers across individuals.* → [`doc/preregistrations/experiment_plan_paderborn.md`](doc/preregistrations/experiment_plan_paderborn.md)

### Pillar 2 — Widening the population support fails

Every attempt to absorb unseen healthy individuals by thickening the shared support (global, component-conditional, condition-conditional, hierarchical envelope) was **killed by its own pre-registered criteria**: FAR barely improved while shallow damage was absorbed into the healthy buffer and detection dropped.

*Healthy individuality must not be represented as thickness of the shared support.* → [`doc/preregistrations/experiment_plan_paderborn2.md`](doc/preregistrations/experiment_plan_paderborn2.md)

### Pillar 3 — Two scalars of healthy commissioning fix the alarm origin

Standardizing each unit's clean likelihood by **its own commissioning median and IQR** — two scalars, estimated from **~64 seconds** of healthy operation — restored the designed false-alarm rate on unseen healthy bearings:

- unseen-healthy FAR **0.10%** (below the designed 0.5% rate)
- severity side **bit-identical**: H1 12/12, ρ, det_all, extent-1 absorption all unchanged
- the registered ladder diagnostic showed the one-scalar *model*, not sample size, was the binding constraint

*Role-bounded result: healthy commissioning / admission calibration — never the failure alarm.* → [`doc/preregistrations/experiment_plan_paderborn3.md`](doc/preregistrations/experiment_plan_paderborn3.md)

### Pillar 4 — Longitudinal degradation needs the unit's own history

On NASA IMS run-to-failure bearings, margins referenced to **each unit's own early life** were statistically progressive on all three primary failed bearings:

- alarm-occupancy Spearman **+0.90 / +1.00 / +0.95**
- lead time **74–148 h**, persistence **93.5–99.6%**
- end-of-life distributions clearly deepened beyond healthy (up to +463 IQR)

And the bound, measured from the refutation side: reusing Pillar 3's fleet location–scale calibration **as the failure alarm** was killed 3/3 — sustained onset **11–14% of life late** on two bearings, **silent** on one.

Disclosed honestly: one bearing's healthy-phase FAR missed design (6.92% vs 0.5%) — self-reference does not automatically give probability calibration. Same-shaft control bearings also showed late-life onsets: sensors observe the **machine system**, not only the bearing beneath them.

*Cross-sectional calibration success does not imply longitudinal detection validity.* → [`doc/preregistrations/experiment_plan_ims.md`](doc/preregistrations/experiment_plan_ims.md)

### Pillar 1 extension — graded severity on a second machine class

A fifth, **registered confirmatory** validation (the exploration preceded it — disclosed in the plan itself) extends the severity geometry to a cyclic hydraulic rig with graded physical degradation labels, under one fixed fault-agnostic vocabulary and five registered splits:

- **cooler**: 100% detection at both degradation stages on every split, margins ordered with CIs excluding zero
- **valve**: margins order all three stages (ρ **+0.89…+0.93**, 5/5 splits) *even where mild-stage detection is absent* — severity and alarm decoupled, this time on timing geometry
- reported as killed/limited: **leak** failed its registered detection criterion (the exploration's single lucky split had overstated it); **accumulator** confirmed unobservable at this granularity

*The graded-severity geometry is not bearings-only.* → [`doc/preregistrations/experiment_plan_hydraulic.md`](doc/preregistrations/experiment_plan_hydraulic.md)

---

## The Deployment Principle

```
Factory-shared (fleet prior)
├─ structural adapter (fault-agnostic vocabulary)
├─ shared structural geometry
├─ severity_margin (non-saturating, cross-unit comparable)
└─ three-state semantics

Commissioning of a new unit (admission)
├─ healthy median + healthy IQR (~64 s of healthy operation)
├─ initial FAR verification / normality admission
└─ bounded role: healthy bridge, NEVER the failure alarm

In service (asset posterior)
├─ accumulate the unit's own normal history
├─ per-asset longitudinal baseline
├─ monitor occupancy / distributional deepening / persistence
└─ failure alarms from self-history, not fleet calibration
```

Two quantities are kept as **distinct statistical objects** throughout: the `severity_margin` (an ordinal damage-depth ruler, shared across the fleet) and the alarm decision (a FAR-controlled variable, individual). Every pre-registered failure above is a measurement of what happens when one is forced to do the other's job.

**Scope separation** (stated, not hidden): this framework claims *anomaly detection* — has the machine system departed from its normal structure somewhere — and does **not** claim *fault localization* (which bearing or component is the source). Localization is a separate spatial-inference task and an explicit limitation. No RUL prediction is performed anywhere.

> **Physical damage severity was represented by a transferable geometry, whereas deployable failure alarms required an asset-specific longitudinal reference.**

Full synthesis: [`doc/preregistrations/nsad_deployment_principles.md`](doc/preregistrations/nsad_deployment_principles.md) · Claim–evidence map: [`doc/paper/claim_evidence_map.md`](doc/paper/claim_evidence_map.md)

---

## What the Detector Is

Lambda³-NSAD describes **normal structure** explicitly and reports deviation from it — the anomaly's shape is never learned:

1. **Structure normality** — a fault-agnostic feature vocabulary feeds a regime-aware GMM (BIC-selected K); each regime owns robust per-scorer thresholds; a clean-data likelihood floor defines the support boundary.
2. **Three-state output per frame** — `0` normal-in-regime, `1` deviation-in-regime (calibrated OR voting over six structural scorers), `2` **outside known normal structure** (support-floor egress) — "I don't know this state" is a first-class, measured channel, not silence.
3. **Non-saturating severity** — the support margin is an unbounded distance, so it keeps grading beyond the alarm boundary (this is what makes the severity ladders of Pillars 1 and 4 readable).

All thresholds are percentiles of the detector's own clean-score distribution: label-free, no per-dataset tuning (structural defaults, adjustable). Anomaly-window annotations in public corpora are used **only as exclusion masks** for constructing uncontaminated normality — data hygiene, not supervision.

Architecture detail (scorers, calibration math, adapter law): [`doc/architecture.md`](doc/architecture.md)

---

## Generic Breadth Checks (NAB / SKAB / TEP)

Before the engineering validations, the same frozen configuration was qualified on public benchmarks — retained as **breadth checks, not as the primary evidence or a leaderboard claim**:

| Corpus | Role | Result (label-free operating points) |
|---|---|---|
| NAB (52 labeled files) | generic time-series qualification | unknown channel alone **85.0% catch @ 0.56% FP**; combined three-state **96.3% @ 303/10k** |
| SKAB (8 sensors) | multivariate anomaly qualification | **100% (34/34) @ 382 FP/10k** |
| TEP (52 variables) | process/regime qualification | unknown channel degenerates exactly to Hotelling T² at K=1; reconstruction ≡ PCA-SPE (identity-tested) |

Full protocols, self-run baselines (including where they win), and the protocol-inflation audit: [`doc/paper/scoreboard.md`](doc/paper/scoreboard.md) — Appendix material of the paper.

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/miosync-masa/Lambda_inverse_problem.git
cd Lambda_inverse_problem
pip install .
```

### Basic usage (regime-aware detector, three-state output)

```python
from lambda3_detector.regime import RegimeAwareDetector

# anomaly_mask : (n,) bool — True at known-incident frames
#   (used only to clean training data, never as anomaly shape signal)
detector = RegimeAwareDetector(
    K='auto',                              # BIC auto K selection (1-5)
    threshold_method='trimmed_percentile', # rare-outlier-robust
    mask_margin=50,
    calibrate_combined=True,               # OR-output calibration (FP control)
)
result = detector.fit_predict(events, anomaly_mask)
result['score']    # calibrated ratio (>=1.0 = flagged)
result['state']    # 0 normal / 1 deviation / 2 outside known normal structure
```

The fleet→asset healthy-admission bridge (the Pillar 3 mechanism, role-bounded) lives in `lambda3_detector/regime/commissioning.py`. Production defaults were **not** changed by any of the five pre-registrations.

### Reproduce the five pre-registered validations

Data setup (gitignored directories at repo root): `PADERBORN/` from this repo's GitHub Release `pu-bearing-data` (CC BY-NC 4.0, Paderborn KAt Data Center); `IMS/` and `MILLING/` from the NASA Prognostics Data Repository (datasets 4 and 3); `HYDRAULIC/` (UCI id 447, CC BY 4.0) via the Machine-Learning-FGA/Hydraulic-systems mirror. See [`tests/README.md`](tests/README.md).

```bash
python -m tests.paderborn.exp_paderborn_full   # #1 severity ordering across individuals
python -m tests.paderborn.exp_paderborn2       # #2 support widening vs commissioning
python -m tests.paderborn.exp_paderborn3       # #3 two-scalar commissioning (E3)
python -m tests.ims.exp_ims                    # #4 IMS run-to-failure + milling
python -m tests.hydraulic.exp_hydraulic_prereg # #5 hydraulic graded severity
```

### Reproduce the breadth checks

```bash
# NAB (requires: git clone https://github.com/numenta/NAB.git alongside)
python -m tests.nab.benchmark_nab_selfcal
python -m tests.nab.benchmark_nab_corpus --compute --methods all && python -m tests.nab.benchmark_nab_corpus --aggregate
python -m tests.nab.benchmark_nab_baselines --category all

# SKAB / TEP
python -m tests.multivariate.benchmark_skab
python -m tests.multivariate.benchmark_tep
```

Deterministic (`random_state=0` in GMM); one frozen configuration everywhere — no per-dataset tuning.

---

## 📄 The Paper (v2, engineering pivot)

The manuscript's center of gravity is the five pre-registered engineering validations; the generic benchmarks are Appendix breadth checks.

| Document | Content |
|---|---|
| [`doc/paper/paper_v2_outline.md`](doc/paper/paper_v2_outline.md) | the main-line outline (§1 problem → §8 conclusion, appendix migration plan) |
| [`doc/paper/claim_evidence_map.md`](doc/paper/claim_evidence_map.md) | every claim ↔ pre-registered verdict, numbers, freeze SHAs; failure registry |
| [`doc/paper/abstract.md`](doc/paper/abstract.md) | title candidates, core claim, abstract draft, contribution bullets, review risks |
| [`doc/preregistrations/nsad_deployment_principles.md`](doc/preregistrations/nsad_deployment_principles.md) | the pre-registration synthesis (deployment principles) |
| [`doc/paper/paper_draft.md`](doc/paper/paper_draft.md) | v1 draft — retained unchanged as Appendix source (NAB/SKAB/TEP detail) |

---

## 📁 Repository Structure

Organized as the before/during/after observation system of
[doc/architecture.md §13](doc/architecture.md):

```
lambda3_detector/                # the NSAD package (see its README)
├── adapters/                    # BEFORE: fault-agnostic vocabularies
│   └── vibration.py             #   vibration_features (fs-generic; 4 pre-registered runs)
├── streaming/                   # DURING: 6 causal scorers + Tier 0 detector
├── regime/                      # DURING: RegimeAwareDetector — three-state output,
│   │                            #   OR calibration, opt-in floor guardrails (§13.9)
│   └── commissioning.py         #   fleet→asset healthy-admission bridge (role-bounded)
├── features/extractor.py        # incl. cycle-phase vocabulary (promoted)
└── core/ analysis/ scorers/ …   # LEGACY INVENTORY: Lambda³ batch research (§13.8)

tests/                           # evidence & evaluation — see tests/README.md
├── README.md                    #   final-spec entry points: which command reproduces which result
├── paderborn/  ims/             #   pre-registrations #1–#4 (SHA-anchored) — the paper's primary evidence
├── nab/  multivariate/          #   breadth checks (NAB · SKAB/TEP) — Appendix material
├── core/  probes/  baselines/   #   unit tests · synthetic mechanism probes · MSPC/FGMM rivals
├── hydraulic/                   #   post-freeze exploration
├── figures/                     #   manuscript figures
└── legacy/                      #   pre-NSAD harnesses (inventory)

doc/
├── README.md                    # documentation index
├── architecture.md              # system architecture + §13 adapter view + §13.9 promotion log
├── figures/                     # generated manuscript figures
├── paper/                       # manuscript line: v2 outline, claim–evidence map,
│                                #   abstract, v1 draft, benchmark scoreboard (Appendix)
├── preregistrations/            # executed pre-registrations #1–#4 + multivariate
│                                #   + nsad_deployment_principles.md (the synthesis)
└── explorations/                # post-freeze explorations (hydraulic, Paderborn subset)
```

---

## 🔬 Lambda³ Theory (Batch Mode Background)

The original Lambda³ batch system, on which the streaming/regime-aware modes build, models phenomena via:

1. **Structure tensors (Λ)** — high-dimensional semantic representation
2. **Progression vectors (ΛF)** — directional flow
3. **Tension scalars (ρT)** — energetic content
4. **Topological charge (Q_Λ)** — winding number for structural defects
5. **Jump-conditioned entropies** — Shannon / Rényi / Tsallis

### Inverse problem formulation
```
min ||K - ΛΛᵀ||²_F + α·TV(Λ) + β·||Λ||₁ + γ·J(Λ)
```
Where `J(Λ)` enforces jump consistency with detected ΔΛC events.

The streaming/regime-aware modes inherit the delay-embedded SVD subspace (reconstruction scorer), multi-scale jump detection, and kernel-space deviation (RKHS). For deep interpretability (per-frame physical explanation: which Q_Λ defect, which structural transition), use the batch mode `Lambda3ZeroShotDetector.analyze()`.

---

## 📦 Requirements

- Python 3.10+
- NumPy, SciPy, scikit-learn
- pandas
- (optional) CuPy for GPU acceleration of batch mode

```bash
# Core
pip install .

# + GPU (CuPy, Colab)
pip install ".[gpu]"

# + visualization
pip install ".[viz]"

# Dev
pip install ".[dev]"
```

---

## 📜 License

MIT License. *"Detects the moments of rupture — the unseen phase transitions, structural cracks, and the birth of new orders — before any black-box model can learn them."*

## 🙌 Citation

```bibtex
@software{lambda3_nnnu_2026,
  title  = {Normal-Structure Anomaly Detection (Lambda³ NNNU): detecting deviation from mathematically structured normality without neural networks},
  author = {Iizumi, Masamichi},
  year   = {2026},
  url    = {https://github.com/miosync-masa/Lambda_inverse_problem},
  note   = {Based on Dr. Iizumi's Lambda³ Theory}
}
```

For theoretical discussion, practical applications, or collaboration proposals,
please open an issue/PR — or connect via Zenodo, SSRN, or GitHub.

> Science is not property; it's a shared horizon.
> Let's redraw the boundaries, together.
> — Iizumi & Digital Partners
