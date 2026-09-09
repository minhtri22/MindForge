# OIR-PPV PM Milestone & Quality Tracker

Last updated: 2026-09-09

## 1. Purpose

This file is the PM operational tracker for milestone progress, hypothesis closure,
quality gates, evidence debt, and the next executable research step.

It does not replace:

- `PLAN.md` for roadmap/dependency authority;
- `THEORY.md` for formal hypotheses;
- frozen protocol artifacts for metric semantics;
- QA reports for acceptance evidence.

## 2. Current PM Review Baseline

Reviewed sources:

- `PLAN.md`
- `README.md`
- `THEORY.md`
- `H1_H4_CLOSURE_PLAN.md`
- `QA_REPORT_HANDOFF_008_1.md`
- `QA_REPORT_HANDOFF_009_H1_v2.md`
- `QA_REPORT_HANDOFF_010_H2.md`

Current repository state observed during PM review:

- branch: `oir-ppv-research`
- HEAD: `0521c5754a32e2625930de75fe2635c6ce5ec9a0`
- branch is ahead of origin by 4 commits;
- worktree contains existing modified/untracked research artifacts, so future
  handoffs must record exact staged/source provenance rather than assume a clean
  tree.

## 3. Milestone Tracker

| Milestone | Objective | Evidence / QA gate | PM state | Quality note |
| --- | --- | --- | --- | --- |
| M0 | Research foundation | historical accepted handoff | ACCEPTED | Foundation lineage retained |
| M1 | Controlled ENV-1..ENV-4 | accepted project history | ACCEPTED | Deterministic environment infrastructure established |
| M2 | Baseline benchmark suite | accepted project history | ACCEPTED | Infrastructure acceptance only; early baseline quality limitations retained |
| M3 | OIR-PPV pipeline + protocol freeze | `M3-Protocol-v1.0` | ACCEPTED | Protocol identity remains frozen/versioned |
| M4 | Real learner + stress infrastructure | `QA_REPORT_HANDOFF_007_v5.md` PASS | ACCEPTED_FOR_INFRASTRUCTURE | Scientific robust-invariant claim remained unsupported at this stage |
| M4.1 | Reference learner benchmark | `QA_REPORT_HANDOFF_008_1.md` PASS_WITH_LIMITS | ACCEPTED_WITH_LIMITS | `EXP-LRN-001` frozen; benchmark discriminates learner families |
| H1 closure | Compression / complexity-utility | `QA_REPORT_HANDOFF_009_H1_v2.md` | CLOSED_WITH_LIMITS | QA classification `SUPPORTED_WITH_LIMITS`; claim boundary must be preserved |
| H2 closure | Transfer | `QA_REPORT_HANDOFF_010_H2.md` PASS | CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS | 60/60 paired evidence valid; L1-L4 all negative vs L0/PCA under frozen rule |
| H3 closure | Nuisance robustness | `QA_REPORT_HANDOFF_011_H3_v3.md` PASS_WITH_LIMITS | CLOSED_WITH_LIMITS / NOT_SUPPORTED | correction_v3 accepted with metadata erratum; exact target-specific boundary preserved |
| H3R protocol | Revised observation-noise robustness under Formal v1.0 | `H3R_PROTOCOL_v1.0.md` + machine-readable protocol + frozen test manifest + independent review | FROZEN / NOT_EXECUTED / TEST_LOCKED | Commit/publish freeze package, then separate explicit H3R execution task |
| H4 closure | Counterfactual accuracy | owner explicitly deferred after H3 closure | NOT_OPENED / DEFERRED_BY_OWNER | Do not instantiate H4 while H3R is active frontier |
| H5 closure | Minimal sufficiency | no closure protocol yet | PLANNED / BLOCKED | Requires ablation/redundancy protocol after earlier evidence stabilizes |
| M5 | MindForge learner integration | dependency in PLAN | BLOCKED_BY_CLAIM_SEQUENCE_DECISION | Reference benchmark is frozen; integration timing must remain PM-controlled |
| M7 / H6 | Creative recombination | parked branch | PARKED | Do not let H6 alter core closure evidence |
| M8 | Research release | depends on hypothesis closure | NOT_READY | Release claim boundary remains unresolved |

## 4. Hypothesis Quality Tracker

| Hypothesis | Formal state | Evidence state | QA scientific classification | PM record | Main limitation / debt |
| --- | --- | --- | --- | --- | --- |
| H1 Compression | FORMALIZED + protocol executed | QA reviewed | `SUPPORTED_WITH_LIMITS` | CLOSED_WITH_LIMITS | MEM is a weak exact-row/global-majority control; RAW has `C_total=0`; no superiority to RAW or memory systems generally |
| H2 Transfer | PROTOCOL_FROZEN + QA_REVIEWED | 60/60 paired primary evidence complete | `FALSIFIED_UNDER_TESTED_CONDITIONS` | CLOSED | Applies only to tested L1-L4 vs L0/PCA on ENV-1/3/4 x 5 seeds; no generalization to invariant learning/MindForge/canonical methods |
| H3 Nuisance Robustness | PROTOCOL_EXECUTED + QA_REVIEWED | correction_v3 accepted; 100/100 cells, 60/60 eligible pairs | `NOT_SUPPORTED` | CLOSED_WITH_LIMITS | P2 metadata erratum: h3_summary_v3 embeds version=2; frozen bytes preserved |
| H3R Revised Robustness | FORMAL v1 FROZEN | no decisive evidence | PROTOCOL_REVIEW `PASS_WITH_LIMITS` | FROZEN / NOT_EXECUTED | P0=0/P1=0; remaining P2 provenance-publication debt; decisive test still locked |
| H4 Counterfactual Accuracy | HISTORICAL_FORMALIZATION_ONLY | no active protocol | UNREVIEWED | NOT_OPENED | Owner deferred H4; H3R is current frontier |
| H5 Minimal Sufficiency | FORMALIZED | not yet collected | UNREVIEWED | BLOCKED | Ablation/redundancy protocol and acceptance thresholds absent |
| H6 Creative Recombination | PARKED / FORMALIZATION_PENDING | prototype only | UNREVIEWED | PARKED | Must not be promoted until core benchmark/claim sequence permits it |

## 5. H1 Closure PM Review

PM records the independent QA result from `QA_REPORT_HANDOFF_009_H1_v2.md` as the
current H1 source of truth:

- software/evidence integrity: `PASS`;
- correction task acceptance: `PASS`;
- H1 closure readiness: `PASS_WITH_LIMITS`;
- scientific classification: `SUPPORTED_WITH_LIMITS`;
- no open P0/P1 blocker from the H1 closure re-review.

The defensible H1 claim boundary to carry forward is:

> Within ENV-1..ENV-4 and seeds 42, 123, 456, 789, 1011, at least the tested
> L0/PCA and L3/IRM-style representations require substantially less retained
> inference state than the frozen exact-row MEM control while maintaining utility
> within the frozen non-inferiority criterion. This does not establish superiority
> over RAW or memory systems generally.

This boundary is mandatory downstream. H2/H3/H4 reports must not restate H1 as
general superiority over raw features, memorization, or memory architectures.

## 5.1 H2 Closure PM Review

PM accepts `QA_REPORT_HANDOFF_010_H2.md` and freezes H2 as:

- software/evidence integrity: `PASS`;
- `DEV_TASK_010_H2_CLOSURE`: `PASS`;
- H2 closure readiness: `PASS`;
- scientific classification: `FALSIFIED_UNDER_TESTED_CONDITIONS`;
- P0/P1 blockers: none.

Frozen claim boundary:

> Within ENV-1, ENV-3, ENV-4 and seeds 42, 123, 456, 789, 1011, the tested
> L1 MLP, L2 VAE, L3 IRM-style surrogate, and L4 DANN configurations do not
> improve paired unseen/OOD performance over L0/PCA and show negative paired
> effects under the frozen H2 rule.

This result must not be generalized to invariant learning in general, canonical
implementations of those method families, MindForge, or untested environments.

PM interpretation carried forward: H1 and H2 together show that compression or
retained-state efficiency is not sufficient evidence of transfer. The next
research question is `Q-H2.1`: **what properties must an invariant retain/remove
to become transferable?** H3 must examine whether nuisance robustness and
task-preserving intervention stability explain part of that distinction.

## 6. Quality Gates

| Quality dimension | Current state | Gate for progression |
| --- | --- | --- |
| Protocol integrity | PASS | No in-place semantic changes; version amendments if required |
| Provenance | PASS_WITH_CAUTION | Dirty worktree means every new task/handoff must record exact HEAD, changed files, artifact hashes and run identity |
| Reproducibility | PASS for accepted benchmark/H1 evidence | Preserve frozen seeds and failed-run history |
| Learner fidelity | PASS_WITH_LIMITS | Keep labels: L0 faithful; L1/L2/L4 adapted; L3 surrogate |
| Benchmark discrimination | PASS_WITH_LIMITS | EXP-LRN-001 accepted as reference layer |
| H1 scientific evidence | CLOSED_WITH_LIMITS | Preserve MEM/RAW limitations and exact claim boundary |
| H2 scientific evidence | CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS | Preserve frozen negative result and narrow claim boundary |
| H3 scientific evidence | OPEN / NEXT | Freeze paired nuisance intervention evidence and address Q-H2.1 before closure |
| H4 scientific evidence | OPEN | Requires explicit SCM counterfactual ground truth and `D_cf` freeze |
| H5 scientific evidence | OPEN | Requires ablation/redundancy protocol |
| External validity | OPEN / HIGH DEBT | Claims remain bounded to controlled synthetic environment families |

## 7. Evidence Debt Register

| ID | Evidence debt | Impact | Status / action |
| --- | --- | --- | --- |
| ED-01 | Historical v0.13.10 source/seed/raw artifact not verified | limits historical provenance claims | RETAIN |
| ED-02 | H1 MEM control has zero test lookup hits and falls back globally | weakens general interpretation of memory comparison | RETAIN_IN_CLAIM_BOUNDARY |
| ED-03 | RAW uses frozen `C_total=0` and learned representations do not establish RAW superiority | prevents broad compression-superiority claim | RETAIN_IN_CLAIM_BOUNDARY |
| ED-04 | Tested L1-L4 transfer is below PCA under frozen H2 rule | falsifies tested H2 operational prediction | CLOSED_AS_NEGATIVE_EVIDENCE; retain claim boundary |
| ED-05 | Reference learner nuisance leakage is not better than PCA overall | challenges H3 | RESOLVE_BY_H3_CLOSURE |
| ED-06 | No frozen SCM-ground-truth counterfactual error benchmark yet | blocks H4 | RESOLVE_BY_H4_PROTOCOL |
| ED-07 | H5 ablation/minimal-sufficiency evidence absent | blocks H5 | FUTURE_CLOSURE_TASK |
| ED-08 | ENV-1..ENV-4 are synthetic/narrow | limits external validity | RETAIN_UNTIL_NEW_RESEARCH_PHASE |

## 8. Documentation Consistency Findings

The reviewed documents are not fully synchronized with the current evidence state:

1. `PLAN.md` still describes M4.1 as `READY / NEXT` and H1-H5 as not closed.
   QA evidence now shows M4.1 accepted with limits and H1 closed with limits.
2. `README.md` contains target-claim language that can be read as an established
   result unless interpreted through PLAN/QA claim boundaries.
3. `THEORY.md` says "Nếu không đạt: Giả thuyết bị bác bỏ", while the project
   governance allows `SUPPORTED_WITH_LIMITS` and `INCONCLUSIVE`; this wording is
   too binary for the current evidence model.

These are PM documentation-debt findings. They should be handled by a separately
scoped PM-controlled documentation amendment so accepted scientific artifacts and
protocol evidence are not mixed with roadmap cleanup.

## 9. Active Risks

| Risk | Likelihood | Impact | PM control |
| --- | --- | --- | --- |
| H1 overgeneralized beyond MEM comparator | High | High | Carry exact QA claim boundary into every downstream task/report |
| H2 negative result is overgeneralized to invariant learning in general | High | Critical | Preserve exact QA boundary: L1-L4 vs L0/PCA, ENV-1/3/4 x 5 seeds only |
| Protocol changes after seeing negative results | Medium | Critical | Versioned amendment only; retain old evidence |
| Dirty worktree weakens provenance clarity | High | High | Record exact source/dirty state and stage only scoped files |
| H6 or MindForge expands scope before H2-H4 closure logic is settled | Medium | High | Keep PM gate and one active closure hypothesis at a time |
| Synthetic environment conclusions are presented as general intelligence claims | Medium | Critical | Keep external-validity boundary explicit |

## 10. Decisions Recorded

### PM-DEC-2026-09-09-01

- Decision: record M4.1 / `EXP-LRN-001` as accepted with limits.
- Evidence: `QA_REPORT_HANDOFF_008_1.md`.
- Impact: reference benchmark is frozen and may be used by H1-H4 closure tasks.

### PM-DEC-2026-09-09-02

- Decision: record H1 as `CLOSED_WITH_LIMITS` with QA scientific classification
  `SUPPORTED_WITH_LIMITS`.
- Evidence: `QA_REPORT_HANDOFF_009_H1_v2.md`.
- Impact: H1 complexity accounting is frozen for downstream comparisons; its
  claim cannot be broadened to RAW or memory systems generally.

### PM-DEC-2026-09-09-03

- Status: `SUPERSEDED_BY PM-DEC-2026-09-09-04/05`.
- Decision at the time: move the active research frontier to H2.
- Reason: H1 QA closure gate is complete and `H1_H4_CLOSURE_PLAN.md` mandates
  sequential `H1 -> H2 -> H3 -> H4` closure.
- Historical impact: H3/H4 remained blocked pending H2 closure; H6 remained parked.

### PM-DEC-2026-09-09-04

- Decision: freeze H2 as `CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS`.
- Evidence: `QA_REPORT_HANDOFF_010_H2.md`.
- Impact: the tested L1-L4 configurations cannot be claimed to improve OOD
  transfer over L0/PCA in ENV-1/3/4 under the five frozen seeds. H2 is not to be
  rescued through threshold, seed, baseline, or learner changes.

### PM-DEC-2026-09-09-05

- Decision: keep the existing H3 closure preparation unchanged and insert
  `Q-H2.1 — What makes an invariant transferable?` as a pre-closure research
  analysis step.
- Reason: H2 demonstrates that learned/complex representation alone is not a
  sufficient transfer mechanism; H3 can test whether nuisance robustness and
  intervention stability discriminate better from worse transfer behavior.
- Impact: Q-H2.1 uses accepted/current evidence only. It must not change H3 code,
  protocol, matrix, seeds, metrics, thresholds, or previously completed work.
  If evidence is insufficient, record `UNRESOLVED` and continue H3 closure.

### PM-DEC-2026-09-09-06

- Decision: record Q-H2.1 as `UNRESOLVED` after pre-H3 evidence analysis.
- Artifact: `Q_H2_1_TRANSFERABLE_INVARIANT_ANALYSIS.md`.
- Evidence interpretation: H1 shows compression can coexist with retained utility,
  while H2 shows that this does not imply transfer. Existing reference evidence is
  directionally consistent with lower nuisance leakage being useful, but does not
  establish causal sufficiency.
- Candidate carried forward: `I_candidate = causal sufficient statistic for the
  task under the tested shifts`.
- Impact: resume H3 closure unchanged. H3 may strengthen, contradict, or leave the
  candidate unresolved; no H3 implementation/protocol change is authorized.

### PM-DEC-2026-09-09-07

- Decision: accept `QA_REPORT_HANDOFF_011_H3_v3.md` and close historical H3 as
  `CLOSED_WITH_LIMITS / NOT_SUPPORTED`.
- Evidence authority: `correction_v3 accepted with metadata limits`.
- P0/P1: none.
- Metadata erratum: preserve `h3_summary_v3.json` with embedded `"version": 2`;
  do not rewrite accepted evidence solely to correct metadata.
- Claim boundary: selected target-specific ENV-1/2/4 result only; ENV-3 remains
  inapplicable because the selected intervention changes `Y` and task labels.

### PM-DEC-2026-09-09-08

- Decision: open H3R protocol preparation immediately after H3 closure and keep
  H4 unopened.
- H3R relation: `REVISED_SUCCESSOR`; Formal Spec v1.0 semantics; no inherited H3
  scientific evidence.
- Current state: `PROTOCOL_PREPARATION / NOT_EXECUTED / NOT_FROZEN`.
- Only next action: `INDEPENDENT REVIEW + FREEZE OF H3R_PROTOCOL_v1.0`.

### PM-DEC-2026-09-09-09

- Decision: freeze `OIR-PPV-H3R v1.0` after independent protocol review.
- Review verdict: `PASS_WITH_LIMITS`; `P0=0`; `P1=0`.
- Frozen protocol SHA256: `1cb444f9e5a48f8f3a69f866097611863d6177fbeb570aa5ceb78a2a7ee730e7`.
- Frozen test-manifest SHA256: `4996c014aae5aba8aaaa72952e89692cb0f2fe439b2030a34ad72b271985349e`.
- Scientific evidence: `NONE_YET`; decisive H3R experiment was not executed.
- P2 debt: commit/publish freeze package from MindForge repository root and record the resulting commit SHA before test unlock.
- H4 remains `NOT_OPENED / DEFERRED_BY_OWNER`.

## 11. Next Executable Step

`COMMIT / PUBLISH H3R v1.0 FREEZE PACKAGE FROM MINDFORGE REPOSITORY ROOT`.

Do not alter frozen scientific semantics during provenance publication. After the
commit SHA is recorded, H3R decisive execution requires a separate explicit task.
Do not open H4 while H3R remains the active frontier.

## 12. Overall Project State

```text
Benchmark / software infrastructure: ON_TRACK
Reference learner benchmark: ACCEPTED_WITH_LIMITS
H1: CLOSED_WITH_LIMITS
H2: CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS
H3: CLOSED_WITH_LIMITS / NOT_SUPPORTED
H3R: PROTOCOL_v1.0_FROZEN / NOT_EXECUTED / TEST_LOCKED
H4: NOT_OPENED / DEFERRED_BY_OWNER
H5 scientific closure: OPEN
External validity: AT_RISK / UNPROVEN
Research release: NOT_READY
Current frontier: H3R FREEZE-PACKAGE PROVENANCE PUBLICATION
```
