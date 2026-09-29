# MindForge Research Portfolio Audit — 2026-09-29

Status: PORTFOLIO GOVERNANCE AUDIT / NO SCIENTIFIC EXECUTION

Canonical root reviewed:

~~~text
main
924654c81c08832c23ff192fdcbf63d3f2680d3a
~~~

This audit answers exactly three questions for every branch reviewed:

1. WHAT DID IT PROVE?
2. WHAT CAPABILITY DID IT CREATE?
3. SHOULD THAT CAPABILITY ENTER MINDFORGE CORE?

It then assigns a portfolio disposition. A negative scientific result is not treated as wasted work, but a deep branch is not retained merely because it consumed significant effort.

## 1. Decision classes

- PROMOTE_TO_CORE — evidence supports importing the capability/contract into canonical MindForge.
- KEEP_ACTIVE_PRIMARY_AXIS — the only active scientific axis allowed to continue.
- MERGE_EVIDENCE_THEN_ARCHIVE — preserve a validated lesson/contract in canonical docs, then retire the branch.
- SUPPORTING_PLATFORM_FREEZE — useful engineering substrate; not an active research axis and not automatically core.
- FINISH_AND_ARCHIVE — only a bounded already-open closure action remains; no successor chain may auto-open.
- ARCHIVE — scientific or governance question is closed, falsified, superseded, or no longer strategically active.
- QUARANTINE_ARCHIVE — preserve for forensics only; never use as a scientific parent.

## 2. Portfolio-level conclusions

### 2.1 Canonical core already proven on main

The current canonical core remains:

~~~text
dataset
→ tokenizer
→ Transformer
→ training
→ checkpoint/resume
→ evaluation
→ generation
→ reproducible experiment system
~~~

Phase 0/1/2 are the actual MindForge core foundation.

### 2.2 Only one branch should remain an active scientific axis

Selected primary research axis: Personal Intelligence, PPF-first.

Current execution branch:

~~~text
research/ppf-l1-l2
~~~

Reason:

- Track-A established that a general LLM is not automatically a suitable Personal Intelligence teacher.
- PIT established a pristine held-out deterministic representation ceiling.
- PPF independently established a personal-event foundation and a blindly confirmed Observability Eligibility primitive.
- PPF explicitly remains outside Kernel and does not require a Model modification.
- The PPF roadmap has a finite closure path G1→G5 and therefore does not require a new branch for each question.

The active research question is therefore not “what feature do we add next?” but:

> Can Personal Intelligence be grounded as an isolated, evidence-bearing PPF extension with a finite real-world feasibility closure, and only then justify a narrowly scoped learned-model capability if deterministic representation remains insufficient?

No other current research family is admitted as a concurrent primary science axis.

### 2.3 Core admission candidate

One branch currently has a strong enough architecture result to recommend promotion:

~~~text
refactor/mks-1-model-kernel-separation
~~~

MKS-1 is PASS/CLOSED with full local evidence, full regression, Phase-2 compatibility, checkpoint compatibility, deterministic evaluation/generation replay, and a deliberately minimal PyTorch-bound TokenModel contract. This is architectural capability rather than a speculative mechanism.

Recommendation: PROMOTE_TO_CORE through a dedicated merge/reconciliation review against current main. Do not merge unrelated descendant research.

### 2.4 Research families that should stop consuming active bandwidth

The following families contain useful evidence but should not remain open-ended active programs:

- KCL / ACO / CPRM / MSA / CLRM continuous-learning chain;
- OIR-PPV / H3R / H3R2-R;
- Model Core MK-1;
- Track-A and PIT as independent active branches;
- SOL reconstruction;
- M6/M6R/RFD as science;
- M6R2 after its already-authorized bounded closure action.

Their evidence should be retained, but successor creation must require a new portfolio-level justification rather than a local “next milestone”.

# 3. Branch-by-branch audit

## Canonical trunk

### main@924654c81c08832c23ff192fdcbf63d3f2680d3a

WHAT DID IT PROVE?  
Phase 0/1/2 establish a compact local LLM kernel, reproducible XPU/BF16 execution, checkpoint/resume, evaluation/generation and a machine-readable experiment system. P0.9/P0.10 also preserve explicit STOP evidence for the original continual-learning/memory hypotheses.

WHAT CAPABILITY DID IT CREATE?  
The actual reusable MindForge research kernel.

SHOULD IT ENTER CORE?  
Already core.

Disposition: CANONICAL.

## Architecture / core boundary

### refactor/mks-1-model-kernel-separation@5280243a54ba8977b0d02a5b4ed85c657e03193f

WHAT DID IT PROVE?  
Model/runtime separation can be introduced without changing Transformer math, checkpoint format, evaluation/generation semantics or Phase-2 behavior. Full local validation closed PASS; 61 regression tests and focused MKS tests passed.

WHAT CAPABILITY DID IT CREATE?  
A minimal PyTorch-bound TokenModel runtime contract and cleaner Model/Kernel architectural responsibility boundary.

SHOULD IT ENTER CORE?  
YES. This is a validated architecture improvement with broad reuse and no speculative model mechanism.

Disposition: PROMOTE_TO_CORE.

### research/model_kernel@d6e3c50abdb8606afa9615db221f45e49de3db81

WHAT DID IT PROVE?  
Primarily MK-0 governance/inheritance framing; it was later logically superseded by research/model_core.

WHAT CAPABILITY DID IT CREATE?  
No unique final capability beyond the successor branch.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE — superseded predecessor.

### research/model_core@256849fe29c870bc7d1cfbda5930a847ede63e6a

WHAT DID IT PROVE?  
The MK-1 training infrastructure executed cleanly, but the one-shot H1a confirmatory study failed for all five preregistered M1-Z seeds. Formal terminal verdict: LEARNED_STRUCTURED_REPRESENTATION_NOT_SUPPORTED. H1b/H1c are blocked by the preregistered sequential rule.

WHAT CAPABILITY DID IT CREATE?  
A rigorous paired model-training/confirmatory harness and a negative result against the tested learned structured representation. It did not create a qualified structured-representation capability.

SHOULD IT ENTER CORE?  
No model mechanism should enter core. Generic harness pieces may be reused only if independently justified as tooling.

Disposition: ARCHIVE current MK-1 hypothesis. No rescue branch. Any later learned-representation study must start from a new question.

## Continual-learning family

### research/kernel-cl@a9159ae8f17693453e7b6378c92deb5effc4a56f

WHAT DID IT PROVE?  
A valid forgetting substrate exists; bounded replay causally reduces forgetting; 6.25% replay is effective on the frozen substrate; the frozen replay mechanism generalized across two qualified unseen synthetic task pairs. Later work replicated policy-effect heterogeneity, but the KCL-6.5.9.x controller-identifiability sequence converged negative and formally stopped.

WHAT CAPABILITY DID IT CREATE?  
Strong research evidence that replay is causally useful on tested synthetic families and that fixed boundary policy is insufficient. It did not create a qualified online controller or real-language continual-learning capability.

SHOULD IT ENTER CORE?  
No. Synthetic replay findings are insufficient for a core learning mechanism.

Disposition: ARCHIVE / evidence retained. Reopen only from an independently justified real-use or transfer question.

### research/cl-potential-outcomes@4fca2b5639e581614e33d9dbfbae576c2bddf9c7

WHAT DID IT PROVE?  
Nothing scientifically yet; it froze a pivot from hard labels to continuous action-specific potential outcomes.

WHAT CAPABILITY DID IT CREATE?  
A useful conceptual reframing, but no executed capability.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE / design reference. Later MSA/CLRM work tested the continuous-response direction more directly.

### research/adaptive-continual-outcomes@0700601f9196d3c5989fa8eb5169f28b1bb01799

WHAT DID IT PROVE?  
ACO-1's frozen rare hard-target design had insufficient prospective support: only 12 canonical Y_PRR boundaries versus the required 30. It did not test the continuous-response hypothesis.

WHAT CAPABILITY DID IT CREATE?  
A valid STOP result and a governance lesson about rare thresholded targets.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE.

### research/continual-policy-response@c1837438d944c0e11dcb961fa669cfef92bc3c2d

WHAT DID IT PROVE?  
CPRM-1 collected valid continuous responses; three dimensions had useful geometry, while final_current_accuracy was ceiling-saturated. The frozen four-component response object therefore failed qualification.

WHAT CAPABILITY DID IT CREATE?  
It localized the next uncertainty to endpoint measurement adequacy. It did not create a predictor/controller.

SHOULD IT ENTER CORE?  
No mechanism. The measurement lesson should be retained.

Disposition: ARCHIVE; successor evidence is represented by MSA.

### research/measurement-substrate-adequacy@64138ab9cb09dcb56a387d3b1f500063eff8302d

WHAT DID IT PROVE?  
MSA-1 found ACCURACY_COARSE_LOSS_INFORMATIVE; MSA-3 independently replicated the same finding on a fresh 72-seed cohort. Under the current controlled CL substrate, terminal accuracy is coarse/saturated while terminal cross-entropy loss remains informative. MSA formally converged and closed.

WHAT CAPABILITY DID IT CREATE?  
A replicated measurement rule for this CL substrate: use CE-loss response as the informative endpoint and treat terminal accuracy as a sentinel rather than the main response signal.

SHOULD IT ENTER CORE?  
Partially, as research methodology/evidence only. It should not become a universal model claim or new model mechanism.

Disposition: MERGE_EVIDENCE_THEN_ARCHIVE. Add the replicated measurement lesson to canonical research/evaluation guidance.

### research/continual-loss-response@44ebebc65a76a8233c5323a2a56a0222d3813bf8

WHAT DID IT PROVE?  
CLRM-1 established that all six direct CE-loss response channels have non-degenerate support. CLRM2-A selected/froze an RBF-KRR-v1 candidate on D-train. The current formal result file reports sealed-validation NEGATIVE / LOSS_RESPONSE_PREDICTABILITY_NOT_QUALIFIED: the candidate does not beat the strongest B2 baseline under the frozen Gate-2 and calibration also fails.

WHAT CAPABILITY DID IT CREATE?  
It created a qualified measurement target, not a qualified predictor. The tested OBS11→loss-response prediction path is not supported.

SHOULD IT ENTER CORE?  
No.

Disposition: FINISH FORMAL CLOSURE THEN ARCHIVE. Do not open another in-family predictor-rescue ladder.

## Personal Intelligence family

### research/track-a-foundation-protocol@627044cc06d3e411b1388b57cd94906fefa74343

WHAT DID IT PROVE?  
It froze a strong capability benchmark protocol for personal understanding/routing without prematurely changing Model/Kernel architecture.

WHAT CAPABILITY DID IT CREATE?  
A benchmark contract, not a model capability.

SHOULD IT ENTER CORE?  
No model/runtime capability. Benchmark artifacts remain useful as research evidence.

Disposition: ARCHIVE / retain benchmark contract because downstream Track-A is closed.

### research/track-a-benchmark-v1@e17c4f886381e24bc9f3b14d719b0a6e60f41485

WHAT DID IT PROVE?  
Qwen3.8-27B Q4_K_M passed runtime qualification and 700/700 held-out completion but was rejected as a Personal Intelligence quality reference. General intelligence capability is not equivalent to the required personal-intelligence capability.

WHAT CAPABILITY DID IT CREATE?  
A negative reference-model result and teacher-role separation.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE.

### research/pit@8a1628d0fba93029f9b9bd6825865145278ff0c9

WHAT DID IT PROVE?  
PIT built teacher/guardrail/evaluation machinery and ultimately reached DETERMINISTIC_REPRESENTATION_CEILING_SUSPECTED on pristine clean held-out evidence. The dominant remaining failure is upstream semantic representation acquisition/generalization, not merely the downstream guardrail policy.

WHAT CAPABILITY DID IT CREATE?  
A strong benchmark/diagnostic boundary and negative baseline for deterministic personal-semantic representation. It did not produce a solved PIT teacher or robust learned representation.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE AS INPUT EVIDENCE to the single Personal Intelligence axis. PIT-20 must not auto-open.

### research/ppf-l1-l2@18b57e70a62c2468e6940d6741c705f0ff850a31

WHAT DID IT PROVE?  
PPF L1/L2/L3/L4/L5 progressed through foundation, benchmark and minimal-mechanism evidence; PPF-C1 blindly confirmed the key primitive Observability Eligibility. PPF-F1 placed PPF outside Kernel and outside mandatory Model modification.

WHAT CAPABILITY DID IT CREATE?  
A platform-neutral personal-event/evidence foundation and a confirmed observability-eligibility primitive, with a finite plugin-feasibility roadmap.

SHOULD IT ENTER CORE?  
No, by design. PPF belongs as an optional Plugin/Extension. What may eventually enter Model research is only a narrowly justified learned capability discovered after PPF closure.

Disposition: KEEP_ACTIVE_PRIMARY_AXIS. This is the sole active scientific program.

### research/sol-recon-teacher-learning@3a11517dc7011d4620b5328224dca669f79b0abc

WHAT DID IT PROVE?  
A sandbox replay ablation found REPLAY_ONLY_INSUFFICIENT_FOR_ANTI_FORGETTING.

WHAT CAPABILITY DID IT CREATE?  
No promoted capability; only exploratory negative evidence.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE.

## OIR / invariant / causal representation family

### research/oir-ppv@9d0879b038b9792809e6589a92ddff5ba2636f4e

WHAT DID IT PROVE?  
It rebuilt/audited the OIR-PPV provenance framework and correctly downgraded historical v0.13.10 validation claims where executable evidence was missing.

WHAT CAPABILITY DID IT CREATE?  
Reproducibility/provenance infrastructure and corrected claim boundaries, not a proven invariant representation.

SHOULD IT ENTER CORE?  
No model mechanism.

Disposition: ARCHIVE — superseded by later OIR evidence branches.

### codex/oir-lineage-cleanup@d642371582d301db66e8a996c91536904636f79a

WHAT DID IT PROVE?  
Administrative/provenance cleanup and reconstruction support; it does not independently establish a scientific mechanism.

WHAT CAPABILITY DID IT CREATE?  
Lineage hygiene only.

SHOULD IT ENTER CORE?  
Only selected provenance corrections if still missing from canonical docs.

Disposition: MERGE NECESSARY LINEAGE CORRECTIONS THEN ARCHIVE.

### oir-ppv-research@e8cf4a958108e048d8d93f8b61bc0c3d63c6bb51

WHAT DID IT PROVE?  
The controlled OIR program built substantial benchmark/reproducibility infrastructure, but the robust invariant/generalization claim was not supported by the learner evidence. H3R v1.1 later closed FALSIFIED_UNDER_TESTED_CONDITIONS.

WHAT CAPABILITY DID IT CREATE?  
A strong causal/invariance benchmark and falsification methodology, not a qualified invariant model mechanism.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE / retain benchmark methodology.

### research/h3r2-r-closure@2e9ad80af6479409e71dc4d3aff90398740112ff

WHAT DID IT PROVE?  
Historical reconstruction was exact 100/100 and the fresh 20-cell prospective execution had valid integrity, but the protocol lacked frozen quantitative confirmatory acceptance/statistical criteria. Final state is PROTOCOL_DEVIATION, not a positive or negative confirmatory mechanism result.

WHAT CAPABILITY DID IT CREATE?  
A reconstruction/protocol lesson; no scientific capability.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE / NO RERUN.

## Model Training / export / runtime family

### docs/evidence-model-training-pipeline@9ff987ebd95cd23fef4cd2a0511774d772b14400

WHAT DID IT PROVE?  
It established a broad evidence-governed pipeline specification and engineering scaffolding from dataset/training contracts through GGUF/Ollama/runtime evidence.

WHAT CAPABILITY DID IT CREATE?  
A supporting training/export/evidence platform specification.

SHOULD IT ENTER CORE?  
Not wholesale. Main explicitly keeps quantization/serving outside current core commitments.

Disposition: SUPPORTING_PLATFORM_FREEZE. It must not count as an active science axis.

### quarantine/m5-quantization-agent-drift-20260921@ddb0a080ae06c99b6f72ffa633d34f255989b485

WHAT DID IT PROVE?  
Nothing admissible beyond forensic history; the branch exists specifically because of agent drift/quarantine.

WHAT CAPABILITY DID IT CREATE?  
None.

SHOULD IT ENTER CORE?  
No.

Disposition: QUARANTINE_ARCHIVE. Never use as a scientific parent.

### research/model-pipeline-m5-quantization-qualification@7bcacfa8fb291a9a55e2acf19077c8e61f33c329

WHAT DID IT PROVE?  
The model pipeline reached frozen, reproducible Q4_K_M qualification and exact artifact identity.

WHAT CAPABILITY DID IT CREATE?  
A reproducible quantization/export capability.

SHOULD IT ENTER CORE?  
Not current core; quantization remains product/platform scope under main policy.

Disposition: SUPPORTING_PLATFORM_FREEZE.

### research/model-pipeline-m6-ollama@c9952ac66be2a15776dcfb92d7bd7e2e1355242e

WHAT DID IT PROVE?  
The isolated Ollama attempt closed FAIL_PACKAGE; the failure was wrapper/orchestration related before parity could be measured.

WHAT CAPABILITY DID IT CREATE?  
Failure evidence and orchestration lessons only.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE.

### research/model-pipeline-m6r-installed-ollama@63cfcd12fae036dd94cf8ce64854796142751b49

WHAT DID IT PROVE?  
Exact Q4 packaging succeeded, but the first chat failed HTTP 500; parity/reasoning remained unmeasured. M6R closed FAIL_RUNTIME.

WHAT CAPABILITY DID IT CREATE?  
A clean failure localization point, not runtime parity.

SHOULD IT ENTER CORE?  
No.

Disposition: ARCHIVE.

### research/model-pipeline-m6r-runtime-failure-decomposition@fdfec8a926ff11f5e10ce0e360251b0ce86e5221

WHAT DID IT PROVE?  
Existing evidence directly identified the q4_0 V-cache + flash-attention-off runtime configuration conflict causing llama-server initialization failure and the HTTP 500.

WHAT CAPABILITY DID IT CREATE?  
A reusable diagnostic lesson and the trigger for separating infrastructure qualification from scientific gates.

SHOULD IT ENTER CORE?  
Not as model code. The governance lesson should be preserved.

Disposition: MERGE EVIDENCE LESSON THEN ARCHIVE.

### governance/model-pipeline-infra-science-separation@750d6358a88e738cfaf971b3a5db3192f7622889

WHAT DID IT PROVE?  
It formalized the distinction between SCIENCE_GATE, INFRA_QUALIFICATION and INFRA_BINDING_CHECK, preventing infrastructure faults from silently consuming or redefining science.

WHAT CAPABILITY DID IT CREATE?  
A broadly reusable research-governance capability.

SHOULD IT ENTER CORE?  
YES as governance doctrine, not model runtime code.

Disposition: MERGE_EVIDENCE_THEN_ARCHIVE.

### infra/ollama-windows-runtime-qualification@46709f0266970a7a16ce4ca2b07b9365c55329b4

WHAT DID IT PROVE?  
A specific Windows/Ollama 0.34.2 runtime scope is qualified with f16 KV cache, flash-attention resolved off, exact adapter identity, and a scientific firewall.

WHAT CAPABILITY DID IT CREATE?  
A reusable local runtime qualification artifact for dependent studies.

SHOULD IT ENTER CORE?  
No. It is platform infrastructure tied to a specific runtime scope.

Disposition: SUPPORTING_PLATFORM_FREEZE.

### research/model-pipeline-m6r2-parity@c3c3537d53e76729fa76d42e263d1969f3f54bc2

WHAT DID IT PROVE?  
Not yet a scientific parity result. S1/S2 are locked and qualified; S3 has one authorized fresh outcome execution and zero consumed attempts.

WHAT CAPABILITY DID IT CREATE?  
So far only a clean qualified path to answer one narrow llama.cpp↔Ollama behavioral-parity question.

SHOULD IT ENTER CORE?  
No. Even a PASS would be packaging/runtime acceptance evidence, not model capability.

Disposition: FINISH_AND_ARCHIVE. Execute at most the already-authorized S3 once, adjudicate as-is, then close. No M7 auto-open.

# 4. Portfolio disposition summary

## Promote to canonical core

1. MKS-1 Model/Kernel Separation
   - promote the minimal TokenModel/architecture contract after reconciliation with current main.

## Merge lessons/evidence into canonical governance/docs, then archive

1. Infrastructure ≠ Science governance separation.
2. MSA replicated measurement lesson:
   - terminal CE loss informative;
   - terminal accuracy coarse/saturated on the tested CL substrate.
3. RFD runtime diagnostic lesson.
4. Any still-missing OIR provenance correction required for historical truth.

## Keep as supporting platform, not research

1. docs/evidence-model-training-pipeline
2. research/model-pipeline-m5-quantization-qualification
3. infra/ollama-windows-runtime-qualification

These may support future research but cannot create scientific successor work by themselves.

## Finish one bounded closure, then archive

1. research/model-pipeline-m6r2-parity
   - one already-authorized S3 only.
2. research/continual-loss-response
   - formalize the existing negative CLRM2 validation result/convergence; no rescue ladder.

## Archive now / preserve evidence read-only

- research/kernel-cl
- research/cl-potential-outcomes
- research/adaptive-continual-outcomes
- research/continual-policy-response
- research/model_kernel
- research/model_core current MK-1
- research/oir-ppv
- oir-ppv-research
- research/h3r2-r-closure
- research/pit
- research/track-a-foundation-protocol
- research/track-a-benchmark-v1
- research/sol-recon-teacher-learning
- research/model-pipeline-m6-ollama
- research/model-pipeline-m6r-installed-ollama
- quarantine/m5-quantization-agent-drift-20260921

# 5. Single primary research axis

## Decision

~~~text
MINDFORGE PRIMARY RESEARCH AXIS
=
PERSONAL INTELLIGENCE
PPF-FIRST
~~~

Current active execution home:

~~~text
research/ppf-l1-l2
~~~

Current finite path:

~~~text
PPF confirmed foundation
        ↓
G1 Plugin Contract Feasibility
        ↓
G2 Boundary / Runtime Isolation
        ↓
G3 Minimal Plugin Prototype
        ↓
G4 Real-world Interface Feasibility
        ↓
G5 Research Closure Decision
~~~

No parallel Model, KCL, OIR or teacher-learning successor is authorized by this portfolio audit.

### Why this axis survives

It has the best combination of:

- an explicit strategic link to MindForge's stated Personal Intelligence direction;
- positive blind-confirmed evidence rather than only infrastructure completion;
- a clear architectural boundary that avoids contaminating Kernel;
- a finite roadmap with an explicit closure state;
- direct use of lessons from Track-A and PIT without treating their failures as mechanisms;
- a path to a future learned-model question only if PPF evidence demonstrates one is necessary.

### Core admission rule for the axis

PPF itself remains a Plugin/Extension.

A future model capability may enter MindForge core only if all of the following occur:

1. PPF reaches a valid G5 closure that preserves Model/Kernel isolation.
2. A concrete personal-semantic failure remains after the deterministic PPF path.
3. The failure can be expressed as one bounded model hypothesis.
4. A boring baseline and pristine held-out falsification set are frozen first.
5. The candidate beats the baseline without requiring PPF semantics inside Kernel.
6. Independent replication passes.
7. Only then is a core-admission review opened.

PIT-19 and MK-1 are negative controls, not candidates to rescue.

# 6. Portfolio operating rules after this audit

To prevent branch explosion:

~~~text
MAX ACTIVE SCIENCE AXES = 1
MAX ACTIVE SCIENCE BRANCHES = 1
~~~

Supporting platform/governance branches may exist, but they do not count as science and may not generate scientific successors.

For every proposed successor:

~~~text
WHAT DID THE PARENT PROVE?
        ↓
WHAT NEW CAPABILITY EXISTS?
        ↓
DOES THE NEXT QUESTION CHANGE
A MINDFORGE CAPABILITY DECISION?
        ↓
NO → DO NOT OPEN BRANCH
YES → smallest preregistered study
~~~

A PASS does not automatically authorize a successor.  
A FAIL does not automatically authorize a rescue.  
A deep branch has no special right to continue.

## Branch lifecycle target

After evidence extraction:

~~~text
main
│
├─ one active science branch:
│    research/ppf-l1-l2
│
├─ at most one supporting platform lineage:
│    model-training/runtime tooling
│
└─ archived historical branches:
     read-only evidence
~~~

# 7. Immediate governance actions recommended

1. Do not open any new research branch.
2. Reconcile and promote MKS-1 into main.
3. Add the infra/science separation doctrine to canonical governance.
4. Add the replicated MSA measurement lesson to canonical research methodology.
5. Formally close the existing CLRM2 negative result and archive that chain.
6. Run at most the already-authorized M6R2 S3 once, close it, and archive the parity chain.
7. Freeze all KCL/OIR/MK/PIT/Track-A/SOL branches as historical evidence.
8. Continue only PPF G1→G5 on the existing PPF branch.
9. At PPF G5, perform another portfolio/core-admission review before any learned-model successor is opened.

# 8. Final portfolio verdict

~~~text
CANONICAL CORE
  Phase 0 / Phase 1 / Phase 2
        +
  candidate promotion: MKS-1

SOLE ACTIVE RESEARCH AXIS
  Personal Intelligence
  current program = PPF

SUPPORTING PLATFORM
  Model Training / GGUF / Ollama qualification
  ≠ scientific axis

HISTORICAL / ARCHIVE
  KCL → ACO → CPRM → MSA → CLRM
  OIR-PPV → H3R → H3R2-R
  Model Core MK-1
  Track-A
  PIT
  SOL reconstruction
  M6 / M6R / RFD after evidence extraction

NO NEW BRANCH
until the current PPF finite closure produces
a capability-level reason to open one.
~~~
