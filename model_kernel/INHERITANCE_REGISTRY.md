# Model Kernel Inheritance Registry

Status: **MK-0 FROZEN SNAPSHOT**

Audit date: **2026-09-19**

## 1. Purpose

This registry records what Model Kernel research may inherit from upstream research and, equally importantly, what it may **not** inherit.

Inheritance classes:

- **ARCHITECTURAL_INVARIANT** — frozen boundary/contract that new work must preserve unless separately amended.
- **BASELINE** — canonical comparison state.
- **SUPPORTED_EVIDENCE** — result that may motivate or constrain a new hypothesis within its original scope.
- **NEGATIVE_EVIDENCE** — failed or limiting result that should remove or narrow downstream experiments.
- **HARNESS_ASSET** — benchmark, ontology, evaluator, protocol, or fixture that may be reused with provenance.
- **PENDING** — upstream question not yet closed; no scientific conclusion may be imported.
- **INFRA_ONLY** — execution/runtime evidence, not model evidence.
- **NON_TRANSFERABLE** — finding cannot be promoted to a model claim without a new prospective transfer study.

Every entry is a snapshot. Before activating a later Model Kernel phase, the source branch and append-only lineage must be re-audited.

## 2. Registry

| Source | Evidence state at MK-0 audit | Class | Allowed inheritance | Explicitly forbidden inference | Downstream relevance |
|---|---|---|---|---|---|
| MindForge MKS-1 | PASS / CLOSED; full local evidence validated | ARCHITECTURAL_INVARIANT | Model != Kernel; minimal PyTorch TokenModel v0 runtime boundary; model internals remain model-owned | "Model Kernel" may redefine runtime Kernel semantics | All phases |
| MindForge Phase-1 compact model | PASS historical baseline | BASELINE | Plain decoder-only Transformer as B0; existing checkpoint/eval/generation compatibility expectations | B0 is already an improved model mechanism | MK-1 onward |
| PIT-19 | DETERMINISTIC_REPRESENTATION_CEILING_SUSPECTED on pristine held-out | NEGATIVE_EVIDENCE | Representation-acquisition failure surface; semantic target/error taxonomy; pristine-heldout discipline | Learned representation is already proven superior | MK-1 |
| CQG H-Q1 | Confirmatory PASS | SUPPORTED_EVIDENCE | Decision-relevant TaskState can materially improve WHAT-to-ask ranking in the controlled benchmark | The exact CQG TaskState is the correct MindForge latent representation | MK-1 / MK-2 |
| CQG H-Q2 | Confirmatory PASS across five frozen shifts | SUPPORTED_EVIDENCE | Strong evidence that an explicit decision-relevant state can retain utility under specified shifts without retraining | Open-world/general language generalization | MK-2 |
| CQG J3.12 | Target/validator integrity supported; strong ranking; absolute ECV fidelity FAIL | NEGATIVE_EVIDENCE | Do not equate ranking quality with cardinal-value calibration; retain ordering/cardinal separation as a design constraint | A scalar value/confidence head is justified as first intervention | MK-2 / MK-4 |
| CQG J3.13 | FORMALLY CLOSED: `CARDINAL_IDENTIFIABLE_BUT_CURRENT_LEARNER_CONTRACT_INSUFFICIENT`; report `008a49f7...`, formal-result commit `5f98364d...`, lineage evidence `ce077cd0...` | SUPPORTED_EVIDENCE | Strict cardinal nonidentifiability is falsified in this tested setup; scale-only, representation-factor-only, and combined ExtraTrees arms did not pass the cardinal gate | Factorized representation is useless for non-cardinal representation learning, or the J3.13 learner failure transfers directly to MindForge | MK-1 design narrowing / MK-4 |
| CQG J3.14→J3.16 | J3.14 formal verdict `CURRENT_TESTED_REMEDIES_INSUFFICIENT`; J3.15 supports numerical/near-tie pathology in raw Spearman; J3.16 formally closes `STRUCTURED_OBSERVABLE_ECV_SUPPORTED` | SUPPORTED_EVIDENCE + NEGATIVE_EVIDENCE | Structured/factorized observable decomposition can support near-exact cardinal reconstruction and selection utility in the CQG substrate; raw Spearman near ties must not be over-interpreted | Exact CQG PHI schema transfers to MindForge, or structured state is automatically learnable from raw language/context | MK-1 design constraints / MK-2 / MK-4 |
| MindForge KCL-6.5.9.x convergence | Formal convergence review CLOSED at branch HEAD `a9159ae8...`: diagnostic convergence achieved, no qualified boundary controller, active 6.5.9.x STOP | SUPPORTED_EVIDENCE + NEGATIVE_EVIDENCE | Fixed global policies are insufficient; action/failure regimes are real; useful structure need not be predictable from current observables; current hard-target representation rescue family is closed | Any KCL predictor/controller transfers to Model Core, or all future/temporal/nonlinear representations are useless | MK-1 design constraints / MK-5 |
| KCL post-convergence pivots | BL-1 continuous potential outcomes, BL-2 policy-conditioned factorization, BL-4 target-margin audit retained as future programs but not executed | PENDING | Design questions only: audit target stability, prefer generating quantities over brittle hard labels when justified, preserve policy/mechanism identity before recombination | These pivots are already validated mechanisms or must block MK-1 | MK-1 protocol design / future MK-5 |
| MindForge OIR-PPV | Mixed closed findings plus open/deferred frontier; strong provenance/falsification machinery | HARNESS_ASSET + PENDING | Invariance/counterfactual methodology; candidate hypotheses; provenance discipline | Invariant loss/head is an established model mechanism | MK-6 |
| PPF L1/L2 | Foundation/semantic work with frozen findings in its own scope | HARNESS_ASSET | Semantic/event contracts, ontology/ground-truth structure where applicable | PPF semantics belong in Kernel or learned weights by default | MK-1 evaluation assets |
| Track-A | Controlled benchmark/capability research with its own closure rules | HARNESS_ASSET | Later capability evaluation and adversarial task discipline | Benchmark success proves architectural mechanism | MK-3+ |
| sol_recon teacher-learning | Positive-but-weak controlled mechanism evidence | SUPPORTED_EVIDENCE, weak | Compact Transformer can absorb some supervised behavioral signal under tested setup | Production-scale learned mechanism established | MK-1 motivation only |
| ARN R1/R2 | Downgraded after methodological audit | NON_TRANSFERABLE | Failure modes and experimental-design lessons only | Verification/router effectiveness established | Memory research design |
| ARN R3 | READY_FOR_REPAIRED_REAL_PILOT; no confirmatory result at audit point | PENDING | Paired NONE/SHAM/HELP/HARM causal design; cost-matched NM2 comparison | Memory has useful heterogeneous causal value in MindForge | MK-M1 |
| NEXUS canonical R0-R4 | Systems/runtime evidence; H2 unresolved at audit point | INFRA_ONLY | Sparse-runtime semantics, measurement discipline, known full-N scheduling bottlenecks | Sparse/entity architecture should be adopted by the model | MK-7 |
| NEXUS event-ledger branch | EL-L1 mechanism support; later representation/contention work still noncanonical/in progress | INFRA_ONLY + PENDING | Candidate runtime substrate if future model creates sparse conditional work | Canonical H2 PASS or model-level sparse-capacity claim | MK-7 |
| ArcLLM/LTR | Runtime/memory hierarchy research | INFRA_ONLY | Future deployment/runtime characterization | Runtime gain implies cognitive/model gain | MK-7 |

## 3. Transfer rules

### 3.1 Scientific evidence does not transfer automatically

If an upstream study supports proposition P on substrate S, Model Kernel may not state P for a new substrate S' without a prospective transfer qualification when the substrate difference can affect the mechanism.

### 3.2 Failed mechanisms are valuable

A clean upstream FAIL should normally remove the corresponding downstream arm unless Model Kernel has a specific, preregistered reason why the changed substrate invalidates the upstream failure.

### 3.3 Harness reuse is not result reuse

A benchmark, ontology, evaluator, or protocol may be reused with exact provenance. Reusing it does not transfer the original verdict to a new model.

### 3.4 Pending evidence cannot guide outcome-dependent tuning

Pending branches may inform broad protocol questions before outcome inspection, but no unobserved future result may be assumed, and no Model Kernel conclusion may cite a pending mechanism as supported.

### 3.5 Infrastructure remains infrastructure

Runtime savings, sparse scheduling, memory residency, or event-ledger behavior become model-science variables only in a separately preregistered interaction study where the learned model actually creates the relevant conditional workload.

## 4. Current inheritance decision

For the first prospective model studies, the strongest admissible evidence pattern is:

~~~
PIT negative evidence:
deterministic semantic representation has a pristine-generalization bottleneck

CQG positive evidence:
decision-relevant TaskState materially improves ranking/selection

CQG negative evidence:
strong ranking does not guarantee absolute/cardinal calibration

CQG J3.13→J3.16:
generic cardinal remedies fail, but a prospectively validated structured observable
decomposition supports near-exact cardinal reconstruction, material-order preservation,
selection utility, and an exact-SE stochastic bridge in the CQG substrate.

KCL-6.5.9.x convergence:
replicated structural heterogeneity does not imply predictability from current observables;
hard derived labels can hide mechanism heterogeneity; repeated representation rescue without
a new target/objective uncertainty must STOP.
~~~

Therefore the first Model Core hypothesis should concern **learned structured decision-state formation from raw/current input**, while keeping representation formation separate from decision sufficiency.

The inherited design constraints are now explicit:

- audit target stability/margins before blaming representation learning;
- every structured target must have an observable-identifiability contract;
- factorize mechanism-relevant quantities before premature recombination when scientifically justified;
- do not treat CQG PHI or any KCL feature/controller as transferable architecture;
- if the formulation fails cleanly, do not open an unbounded feature/history/capacity rescue chain without a new preregistered uncertainty.

These constraints authorize MK-1 **specification/preregistration work only**. Activation and execution remain governed by DEPENDENCY_GATES.md.