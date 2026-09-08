# PIT Research Roadmap

## PIT Track

Completed:

- PIT-1 Teacher Requirements
- PIT-2 Literature & Repository Qualification
- PIT-3 Candidate Architecture & Teacher Strategy
- PIT-4 Evaluation Protocol & Data Requirements
- PIT-5 Minimal Proof Experiment Design
- PIT-6 Minimal PIT Simulator
- PIT-6.1 Adversarial Personal Pattern Simulator
- PIT-7 Teacher Strategy Selection
- PIT-8 Teacher Strategy Evaluation Protocol
- PIT-9 Candidate Teacher Qualification
- PIT-10 Frozen Evaluation Contract
- PIT-11.1 Candidate Landscape and Shortlist
- PIT-11.2 Candidate Qualification Execution
- PIT-12 Candidate Qualification Evidence Generation
- PIT-12.1 Candidate Access Policy Update
- PIT-12.2 Candidate Execution Strategy Update
- PIT-13.0 Candidate API Evaluation Freeze
- PIT-13.0.1 API Candidate Manifest Freeze
- PIT-13.1.A.1 Smoke Harness Contract Audit
- PIT-13.1.A.2 Smoke Gate Semantics Review

Current:

PIT-13.1.A Candidate Smoke Qualification: `PARTIAL_CANDIDATE_QUALIFICATION`.

Eligible: 3 / 4 candidates.

Next:

PIT-13.1.B Evidence Collection: `COMPLETED` for the three smoke-qualified candidates; 21/21 API samples completed and schema valid. Mistral remained excluded with zero PIT-13.1.B calls.

PIT-14 Candidate Qualification Review: `COMPLETED`.

Qualified / qualified-with-limits: 1 / 3.

Strongest current candidate: `minimax/minimax-m3:free` under PIT-13 evidence.

PIT-14.1 NVIDIA NIM Candidate Expansion:

- PIT-14.1.A Candidate Manifest & Execution Freeze — `COMPLETED`
- PIT-14.1.B NVIDIA NIM Smoke Qualification — `COMPLETED`
- PIT-14.1.C NVIDIA NIM Full Evidence Collection — `COMPLETED`
- PIT-14.1.D Expanded Candidate Qualification Review — `COMPLETED`

Smoke-qualified: 5 / 5.

Expanded reviewed candidates: 8.

Qualified / qualified-with-limits under expanded evidence: 4 / 8.

Strongest current candidate: `meta/muse-glimmer-30b` under expanded PIT-14.1 evidence.

This is not final teacher selection.

PIT-15 Teaching Signal Guardrail Experiment: `COMPLETED`.

Guardrail verdict: `GUARDRAIL_EFFECTIVE` under the frozen PIT-15 sample-level acceptance contract.

Positive-control preservation: Muse Glimmer 7/7 accepted; material false BLOCKs = 0.

PIT-16 Guardrail Refinement / Adversarial Validation: `COMPLETED`.

Generalization verdict: `MIXED_NEEDS_MORE_EVIDENCE`.

HELD_OUT: unsafe recall 93.4783%, unsafe precision 100%, violation-class recall 94%, violation-class precision 100%, hard-negative FPR 0%, critical conflict recall 87.5%.

PIT-15 regression preservation: FAILED (1/10 known failures detected by V2). Muse preservation remained 100%.

Next: PIT-17 Guardrail V3 Refinement with Canonical Evidence-Fact Extraction.

PIT-17 Semantic Fact Representation / Guardrail Unification: `COMPLETED`.

Representation verdict: `REPRESENTATION_LAYER_INSUFFICIENT`.

Key metrics: fact precision/recall 100% on the frozen 36-sample goldset; representation-cluster consistency 100%; PIT-15 regression 6/10 known failures detected; PIT-16 HELD_OUT unsafe recall 91.3043%, violation-class recall 90%, hard-negative FPR 0%, critical conflict recall 75%.

Next: PIT-18 Representation Layer Refinement.

