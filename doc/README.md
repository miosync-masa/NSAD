# Lambda³ Documentation

Paper drafts, pre-registered experiment records, and system reference.

## Layout

```
doc/
├── README.md            this index
├── architecture.md      system reference (scorers, calibration math, §13 adapter view)
├── figures/             generated manuscript figures (python -m tests.figures.make_figures)
├── paper/               the manuscript line
├── preregistrations/    the five executed pre-registrations (+ multivariate arm) + synthesis
└── explorations/        post-freeze explorations — NOT in the paper
```

## paper/ — the manuscript line

| File | Content |
|---|---|
| **[paper_v2_outline.md](paper/paper_v2_outline.md)** | **The main line (v2, engineering pivot)**: central problem (healthy individuality vs damage severity collapsed into one outlier score), the three-layer deployment answer, section-by-section outline (Paderborn #1–#3 and IMS #4 primary; NAB/SKAB/TEP → Appendix breadth checks), detection-vs-localization scope separation, figures plan, fixed not-in-this-paper list |
| **[claim_evidence_map.md](paper/claim_evidence_map.md)** | Claim–evidence correspondence for the five pre-registrations: hypothesis / verdict / key numbers / freeze SHAs per pillar, the failure-and-limitation registry (everything retained), the pre-registered-vs-post-hoc ledger |
| **[abstract.md](paper/abstract.md)** | EAAI paper concept (v2): title candidates, core claim ("share the geometry, commission the individual, monitor degradation against its own history"), AI vs engineering contribution split, abstract draft, contribution bullets, review risks, limitations |
| **[paper_draft.md](paper/paper_draft.md)** | The v1 manuscript (complete first draft §1–§10, NAB/SKAB/TEP-centered). **Superseded as the main line; retained unchanged as the designated Appendix source** (architecture §3–§4, protocol §5, benchmark results §6, worked consumer §7) |
| **[scoreboard.md](paper/scoreboard.md)** | Full benchmark record (Appendix material): NAB under three disclosed protocols (self-calibrated ★ / per-file sweep diagnostic / corpus-level), self-run baselines, failure taxonomy, SKAB/TEP multivariate arm (§8), reproducibility recipe |

## preregistrations/ — the evidence arc (all executed; freeze SHA precedes results SHA)

| # | File | Verdict chain |
|---|---|---|
| — | **[nsad_deployment_principles.md](preregistrations/nsad_deployment_principles.md)** | **The synthesis**: shareable ruler / non-shareable baseline history / calibratable healthy FAR / breaks-if-forced failure alarm / detectable progression / non-localizable source; the three-layer deployment shape |
| 1 | [experiment_plan_paderborn.md](preregistrations/experiment_plan_paderborn.md) | H1 severity ordering SUPPORTED 12/12 (ρ +0.845/+0.866, zero reversals); H2 killed on purity (confound disclosed); H3 flat fleet support KILLED by its own kill condition |
| 2 | [experiment_plan_paderborn2.md](preregistrations/experiment_plan_paderborn2.md) | Support-widening A/B/C/D KILLED (extent-1 absorption up to 41%); E commissioning offset INCONCLUSIVE-positive (FAR 43%→14%, zero severity cost) |
| 3 | [experiment_plan_paderborn3.md](preregistrations/experiment_plan_paderborn3.md) | E3 location+scale SUPPORTED — unseen-bearing FAR 0.10% from ~64 s of healthy commissioning, severity audit bit-identical; E0/E2 killed; E1 ladder flat (the model, not sample size, was binding) |
| 4 | [experiment_plan_ims.md](preregistrations/experiment_plan_ims.md) | H1L progressiveness SUPPORTED 3/3 (occupancy ρ +0.90/+1.00/+0.95, lead 74–148 h); H2L supported with one healthy-FAR miss disclosed; **H3L fleet-E3-as-failure-alarm KILLED 3/3** (11–14% of life late, or silent); H4L same-shaft finding; milling ρ median +0.38 |
| 5 | [experiment_plan_hydraulic.md](preregistrations/experiment_plan_hydraulic.md) | Registered confirmatory validation on the cyclic hydraulic rig: H1H cooler ordering SUPPORTED 5/5 (100% detection, CI-separated margins); H2H valve margin ordering SUPPORTED (ρ +0.89…+0.93 even below the alarm floor); **H3H leak KILLED by its registered kill** (severe-stage detection < 50% on 3/5 splits); H4H accumulator observability limit confirmed |
| ~ | [experiment_plan_multivariate.md](preregistrations/experiment_plan_multivariate.md) | The SKAB/TEP arm and its amendment record (pre-pivot; feeds the Appendix and paper/scoreboard.md §8) |

## explorations/ — post-freeze, not in the paper

| File | Content |
|---|---|
| [hydraulic_exploration.md](explorations/hydraulic_exploration.md) | UCI hydraulic rig (id 447): cooler 100% detection with monotone stage grading; valve granularity finding + cycle-phase vocabulary; leak FAR-drift lesson; accumulator below floor. **Converted into pre-registration #5** (its single-split leak numbers did not survive the registered splits — see the #5 verdicts) |
| [paderborn_exploration.md](explorations/paderborn_exploration.md) | Paderborn subset: BIC discovers the two operating conditions at 100% purity; 100% detection of both artificial damages; FAR coverage caveat (×8.6, single healthy bearing) reported as-is |

## Quick navigation

| Question | See |
|---|---|
| The paper's main line (v2)? | [paper/paper_v2_outline.md](paper/paper_v2_outline.md) |
| Which claim rests on which pre-registered run? | [paper/claim_evidence_map.md](paper/claim_evidence_map.md) |
| Deployment principle in one page? | [preregistrations/nsad_deployment_principles.md](preregistrations/nsad_deployment_principles.md) |
| Abstract / contributions / review risks? | [paper/abstract.md](paper/abstract.md) |
| Benchmark headline (Appendix / breadth check)? | [paper/scoreboard.md §2](paper/scoreboard.md#2-self-calibrated-operating-points--headline) — unknown channel **85% catch @ 56 FP/10k**, combined **96.3%**, label-free |
| What's the legitimacy rule? | [paper/scoreboard.md §1](paper/scoreboard.md#1-the-legitimacy-rule) |
| Self-run baselines (OC-SVM etc.)? | [paper/scoreboard.md §2.3, §4](paper/scoreboard.md#23-clean-quantile-operating-points-incl-self-run-baselines) |
| How do the 6 scorers work? | [architecture.md §2](architecture.md#2-the-six-streaming-scorers) |
| Unknown-regime channel? | [architecture.md §4.5b](architecture.md#45b-unknown-regime-channel-three-state-output) |
| How does Tier 2 use anomaly labels? | [architecture.md §4.5](architecture.md#45-semi-supervised-normal-label-only) |
| Adapter qualification law? | [architecture.md §13](architecture.md) |
| Connection to Lambda³ theory? | [architecture.md §11](architecture.md#11-connection-to-lambda³-theory-background) |

## Reproducing the results

Which command reproduces which result: [tests/README.md](../tests/README.md).
The five pre-registered validations:

```bash
python -m tests.paderborn.exp_paderborn_full   # #1
python -m tests.paderborn.exp_paderborn2       # #2
python -m tests.paderborn.exp_paderborn3       # #3
python -m tests.ims.exp_ims                    # #4
python -m tests.hydraulic.exp_hydraulic_prereg # #5
```

Benchmarks (Appendix): [paper/scoreboard.md §9](paper/scoreboard.md#9-reproducibility) — one frozen configuration, deterministic (`random_state=0`).
