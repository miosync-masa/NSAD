# `lambda3_detector` — the NSAD package

Normal-Structure Anomaly Detection: the package makes **normal
operating structure** explicit (regimes, per-regime thresholds, the
support boundary of described normality) and reports departure from it
as a three-state, regime-attributed, severity-preserving payload. No
anomaly shapes are learned anywhere.

The package is organized as the three-layer observation system of
[doc/architecture.md §13](../doc/architecture.md):

```
before  adapters/    fault-agnostic structural vocabularies
during  streaming/ + regime/   the NSAD core (frozen configuration)
after   (consumers live downstream; reference consumer in tests/probes/)
legacy  core/ analysis/ scorers/ features/ …  Lambda³ research inventory
```

## Quick start — Tier 2 (the headline configuration)

```python
import numpy as np
from lambda3_detector.regime import RegimeAwareDetector

# events: (n, d) stream; anomaly_mask: (n,) bool — incident windows,
# used ONLY to exclude contaminated frames from normal-structure
# construction (data hygiene, not supervision)
det = RegimeAwareDetector(K='auto', calibrate_combined=True)
result = det.fit_predict(events, anomaly_mask)

result['state']           # 0 normal-in-regime / 1 deviation / 2 outside known structure
result['score']           # calibrated deviation ratio (non-saturating severity)
result['per_scorer']      # attribution: which structural axis fired
result['log_likelihood']  # support margin vs result['ll_floor']
result['regimes']         # operating-regime assignment per frame
```

Opt-in guardrails for the unknown channel (validated in the
frozen-transfer / Paderborn / IMS arcs; defaults preserve the exact
paper configuration — see §13.9 promotion log):

```python
det = RegimeAwareDetector(
    K='auto', calibrate_combined=True,
    floor_holdout_fraction=0.4,   # out-of-sample floor (×32 in-sample drift measured without it)
    floor_reduce_dims=16,         # PCA(90%) density guardrail for d > 16
)
```

## Adapters (before layer)

Fault-agnostic vocabularies, promoted after pre-registered validation
(`adapters/`; qualification law: the vocabulary may speak about
structure, never about faults):

```python
from lambda3_detector.adapters import (
    vibration_features,             # d=20/channel, sample-rate generic
    extract_cycle_phase_features,   # cyclic machines: phase profile + timing
)
```

## Commissioning (fleet → asset bridge) — with its role boundary

```python
from lambda3_detector.regime import commission_unit

cal = commission_unit(reference_ll, new_unit_healthy_ll)  # 2 scalars: median + IQR
admitted = cal.alarm_margin(unit_ll, floor) <= 0          # healthy admission
```

**Boundary (measured, pre-registered — do not widen):** valid for
*healthy admission calibration* (unseen-unit FAR restored to design
from ~64 s of healthy data, zero severity cost — Paderborn #3);
**invalid as the failure alarm** (fleet-commissioned margins were
11–14% of life late, or silent, at real failures — IMS #4 H3L).
Failure alarms belong to the unit's own accumulated normal history.
See [doc/preregistrations/nsad_deployment_principles.md](../doc/preregistrations/nsad_deployment_principles.md).

## Tier 0 — streaming zero-shot (the controlled ablation baseline)

```python
from lambda3_detector.streaming import Lambda3StreamingDetector
```

Head-segment calibration, strict no-future-leakage, OR voting, no
regime layer — identical scorer bank to Tier 2, which is what isolates
the regime layer's effect (paper §6.2).

## Module layout

```
lambda3_detector/
├── adapters/            # BEFORE: vibration vocabulary (+ cyclic re-export)
├── streaming/           # DURING: 6 causal scorers + Tier 0 detector
├── regime/              # DURING: RegimeAwareDetector (three-state, τ_k,
│   │                    #   opt-in floor guardrails)
│   └── commissioning.py #   fleet→asset bridge (role-bounded)
├── features/
│   └── extractor.py     # incl. extract_cycle_phase_features (promoted)
├── core/ analysis/ scorers/ gpu/ detector.py …
│                        # LEGACY INVENTORY: Lambda³ batch research
│                        # (inverse problem, topology, entropy, batch
│                        # scorers). Governed by §13.8 — candidate
│                        # adapters / after-layer forensic consumers,
│                        # not on the current evidence path.
└── config.py, visualization.py, io_utils.py
```

Promotion policy: nothing enters the production path without meeting
the five §13.8 criteria; every promotion is logged in
[doc/architecture.md §13.9](../doc/architecture.md) with its
validation evidence and regression tests, and default behavior stays
byte-identical (the paper's frozen configuration is never disturbed).

## Evaluation & evidence

All harnesses, probes, pre-registered runners, and figure generators
live in [`../tests/`](../tests/README.md) — organized by dataset and
role, with a final-spec entry-point table (which command reproduces
which result). The `tests/` package consumes this package's public
surface and is never imported by production modules.

## Batch mode (legacy quick start)

```python
from lambda3_detector import Lambda3ZeroShotDetector, L3Config
result = Lambda3ZeroShotDetector(L3Config()).analyze(events)
```

The original Lambda³ batch system (structure tensor, inverse problem,
topological charge). Kept per §13.8: the repository is an inventory of
mathematical mechanisms; the adapter registry controls what enters a
deployed observation path. Historical note: this package is the split
form of the old monolith `lambda3_detector_v2.py`; the equivalence
test is retained at `tests/legacy/test_split_equivalence.py` (requires
the removed monolith — inventory, not CI).
