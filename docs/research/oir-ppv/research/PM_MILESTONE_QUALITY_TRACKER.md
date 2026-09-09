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
- `QA_REPORT_HANDOFF_011_H3_v3.md`
- `governance/H3R_v1.0_DECISIVE_EXECUTION_CLOSURE.md`
- `QA_REPORT_H3R_PROTOCOL_v1.1_FREEZE.md`
- `governance/H3R_v1.1_freeze_manifest.json`
- `governance/H3R_v1.1_FREEZE_PUBLICATION_CLOSURE.md`

Current repository state observed during PM review:

- branch: `oir-ppv-research`
- decisive evidence commit: `f15fa5784bf0c59b48ad4513abca4a105d6f31b9`;
- G3-G8 closure package commit: `feeb5dc5d3d8beb1f14db1260c1f615356d70f19`, remotely verified on `origin/oir-ppv-research`;
- H3R v1.1 freeze-package publication commit: `723dac1f291206a1daa5d7e45ffa21ffe7f3a312`;
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
| H3R v1.0 | Revised observation-noise robustness under Formal v1.0 | frozen v1.0 protocol + `H3R_v1.0_DECISIVE_EXECUTION_CLOSURE.md` + preserved `EXP-H3R-001` failure provenance | CLOSED / PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT / NO_RERUN | One-shot access was consumed; implementation violated numeric-only perturbation realization on mixed ENV-1 observations; evidence preserved and rerun forbidden |
| H3R v1.1 | Versioned recovery with unchanged scientific core and fresh test identity | G1-G7 reports + immutable `EXP-H3R-002` + decisive closure | CLOSED_WITH_LIMITS / FALSIFIED_UNDER_TESTED_CONDITIONS / NO_RERUN | Exactly one decisive access; 20/20 valid cells; 6039/6039 rows; G3 PASS_WITH_LIMITS, G4 PASS, G6 PASS_WITH_LIMITS; P2 provenance-only metadata erratum retained |
| H4 closure | Counterfactual accuracy | owner explicitly deferred after H3 closure | NOT_OPENED / DEFERRED_BY_OWNER | H3R v1.1 is now closed; H4 still requires a new explicit owner decision |
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
| H3R Revised Robustness v1.0 | FORMAL v1 / versioned predecessor | one decisive access consumed; execution failed before first scientific cell | `PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT` | CLOSED / NO_RERUN | Failure is implementation fidelity, not scientific support/falsification; immutable predecessor evidence retained |
| H3R Revised Robustness v1.1 | FORMAL v1 FROZEN + PUBLISHED + EXECUTED | `EXP-H3R-002`: 20/20 valid cells, 6039/6039 rows, exactly one decisive access | `FALSIFIED_UNDER_TESTED_CONDITIONS` | CLOSED_WITH_LIMITS / NO_RERUN | All L1-L4 fail frozen joint robustness/utility support; P2 post-check observation-hash metadata erratum retained; no rescue/rerun |
| H4 Counterfactual Accuracy | HISTORICAL_FORMALIZATION_ONLY | no active protocol | UNREVIEWED | NOT_OPENED | Owner deferred H4; post-H3R frontier decision is pending |
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
| H3 scientific evidence | CLOSED_WITH_LIMITS / NOT_SUPPORTED | Preserve target-specific historical boundary and accepted metadata erratum |
| H3R v1.0 execution | CLOSED / PROTOCOL_DEVIATION | Preserve consumed access event and immutable failed-attempt evidence; no rerun |
| H3R v1.1 decisive closure | PASS_WITH_LIMITS / CLOSED_WITH_LIMITS | Preserve frozen protocol and immutable decisive evidence; scientific result is FALSIFIED_UNDER_TESTED_CONDITIONS; no rerun |
| H4 scientific evidence | NOT_OPENED / DEFERRED_BY_OWNER | Requires explicit owner decision after H3R frontier is resolved |
| H5 scientific evidence | OPEN | Requires ablation/redundancy protocol |
| External validity | OPEN / HIGH DEBT | Claims remain bounded to controlled synthetic environment families |

## 7. Evidence Debt Register

| ID | Evidence debt | Impact | Status / action |
| --- | --- | --- | --- |
| ED-01 | Historical v0.13.10 source/seed/raw artifact not verified | limits historical provenance claims | RETAIN |
| ED-02 | H1 MEM control has zero test lookup hits and falls back globally | weakens general interpretation of memory comparison | RETAIN_IN_CLAIM_BOUNDARY |
| ED-03 | RAW uses frozen `C_total=0` and learned representations do not establish RAW superiority | prevents broad compression-superiority claim | RETAIN_IN_CLAIM_BOUNDARY |
| ED-04 | Tested L1-L4 transfer is below PCA under frozen H2 rule | falsifies tested H2 operational prediction | CLOSED_AS_NEGATIVE_EVIDENCE; retain claim boundary |
| ED-05 | Reference learner nuisance leakage is not better than PCA overall | challenged historical H3 | CLOSED_AS_NEGATIVE_H3_EVIDENCE; retain narrow claim boundary |
| ED-06 | No frozen SCM-ground-truth counterfactual error benchmark yet | blocks H4 | RESOLVE_BY_H4_PROTOCOL |
| ED-07 | H5 ablation/minimal-sufficiency evidence absent | blocks H5 | FUTURE_CLOSURE_TASK |
| ED-08 | ENV-1..ENV-4 are synthetic/narrow | limits external validity | RETAIN_UNTIL_NEW_RESEARCH_PHASE |
| ED-09 | H3R v1.0 one-shot execution failed from mixed-schema implementation deviation after consuming scientific access | prevents valid v1.0 rerun or scientific verdict | CLOSED_BY_VERSIONED_SUCCESSOR; preserve v1.0 evidence permanently |
| ED-10 | H3R v1.1 freeze package required byte-identical Git publication and provenance closure | could invalidate frozen identity through line-ending normalization | CLOSED; `-text -eol` scoped rule, 8/8 canonical hashes verified at publication commit |
| ED-11 | `EXP-H3R-002/cells/*.json` records observation hash with a different helper than the frozen value-stable identity helper | redundant post-check provenance field differs in 20/20 cells | RETAIN_AS_P2_ERRATUM; correct frozen identity was enforced before metrics; do not rewrite evidence or rerun |

## 8. Documentation Consistency Findings

Current PM-critical governance documents are synchronized on the H3R frontier:

1. `PLAN.md` records H3R v1.0 as closed `PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT / NO_RERUN` and H3R v1.1 as `CLOSED_WITH_LIMITS / FALSIFIED_UNDER_TESTED_CONDITIONS / NO_RERUN`.
2. `governance/research_status_v1.0.md` and `governance/claim_registry.md` carry the same versioned H3R boundary.
3. Freeze publication remains anchored at `723dac1f291206a1daa5d7e45ffa21ffe7f3a312`; decisive evidence is anchored by `f15fa5784bf0c59b48ad4513abca4a105d6f31b9`; G3-G8 closure package `feeb5dc5d3d8beb1f14db1260c1f615356d70f19` is remotely verified.

Non-blocking historical documentation debt remains in broader explanatory material such as `README.md` / `THEORY.md`; it must not override frozen protocol, QA, claim-registry, or PLAN authority.

## 9. Active Risks

| Risk | Likelihood | Impact | PM control |
| --- | --- | --- | --- |
| H1 overgeneralized beyond MEM comparator | High | High | Carry exact QA claim boundary into every downstream task/report |
| H2 negative result is overgeneralized to invariant learning in general | High | Critical | Preserve exact QA boundary: L1-L4 vs L0/PCA, ENV-1/3/4 x 5 seeds only |
| Protocol changes after seeing negative results | Medium | Critical | Versioned amendment only; retain old evidence |
| Dirty worktree weakens provenance clarity | High | High | Record exact source/dirty state and stage only scoped files |
| Accidental rerun/overwrite of consumed H3R v1.0 | Low | Critical | Treat `EXP-H3R-001` and access event as immutable; v1.0 rerun forbidden |
| Accidental rerun/repair of consumed H3R v1.1 decisive evidence | Low | Critical | Treat `EXP-H3R-002` and `H3R_V1_1_DECISIVE_ACCESS_001` as immutable; v1.1 rerun and post-access repair forbidden |
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

### PM-DEC-2026-09-09-10

- Decision: close `P2 / PROVENANCE_PUBLICATION_DEBT` after publication-only remediation.
- Published freeze package commit: `7e90366fc062b425d0e5c529c4be81ad2bd54ac2`; remote verification: exact commit observed on `origin/oir-ppv-research`.
- Publication scope was sanitized to `docs/research/oir-ppv/**`; `.env`, Track-A, PIT13, unrelated run logs, and other out-of-scope paths were excluded from the publication commit.
- Four historical M4 raw JSON blobs above GitHub's 100 MB limit were omitted from Git and recorded by exact path/size/SHA256 in `governance/publication_exclusions_v1.0.json`; H3R frozen semantic impact: `NONE`.
- Frozen H3R protocol/test bytes and hashes remain unchanged. No scientific execution was performed.
- H3R remains `NOT_EXECUTED / TEST_LOCKED`; decisive execution requires a separate explicit authorization task.
- H4 remains `NOT_OPENED / DEFERRED_BY_OWNER`.

### PM-DEC-2026-09-09-11

- Decision: close the H3R v1.0 decisive attempt as `PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT` after its owner-authorized one-shot access was consumed.
- Evidence: `governance/H3R_v1.0_DECISIVE_EXECUTION_CLOSURE.md`, `experiments/OIR_PPV/H3R/EXP-H3R-001/failure.json`, and the v1.0 test-access log.
- Failure boundary: the runner attempted to cast mixed ENV-1 observations, including categorical `shape`, to float while the frozen contract permitted perturbation of numeric channels only.
- Governance consequence: v1.0 must not be rerun, overwritten, or reclassified as scientific support/falsification; recovery is permitted only through a versioned successor with a fresh test identity.

### PM-DEC-2026-09-09-12

- Decision: accept H3R v1.1 successor freeze QA as `PASS_WITH_LIMITS` and close the recovery-readiness gate.
- QA: `P0=0`, `P1=0`; one P2 wording ambiguity closed by `governance/H3R_v1.1_FREEZE_ERRATUM_001.md` without changing frozen scientific bytes.
- Verification: `tests/test_h3r_v11_execution.py` = `5/5 PASS`; preflight = `20/20` hash-only identities PASS + runtime smoke PASS; scientific test access increment = `0`.
- Frozen identity: protocol SHA256 `5cdecfe758b9908f0f2199b6e7cd5632e9636b887e141d265fdb9265c107334d`; test-manifest SHA256 `371799bb474f2f425db7acacf63cba3de7ca4876f61cbfa5a88549363d97255d`.
- Governance consequence: v1.1 is eligible for publication/provenance only; decisive execution remains locked.

### PM-DEC-2026-09-09-13

- Decision: close H3R v1.1 publication/provenance as `CLOSED / REMOTE_VERIFIED`.
- Freeze-package publication commit: `723dac1f291206a1daa5d7e45ffa21ffe7f3a312`.
- Publication/provenance closure commit: `17c9b258218b37924d042adcf11ed912d79ec524`; local HEAD and `origin/oir-ppv-research` match this SHA at PM review.
- Published integrity: all `8/8` canonical entries in `H3R_v1.1_freeze_manifest.json` match the published Git blobs. The frozen test manifest is byte-preserved with the scoped `.gitattributes` rule to prevent EOL normalization.
- Scientific state is unchanged: H3R v1.1 remains `NOT_EXECUTED / TEST_LOCKED`, scientific access count `0`.
- Next gate: `SEPARATELY AUTHORIZE H3R v1.1 DECISIVE EXECUTION`. H4 remains `NOT_OPENED / DEFERRED_BY_OWNER`.

### PM-DEC-2026-09-09-14

- Decision: accept G1 decisive pre-execution QA as `PASS` and record the separate owner authorization as valid only for the frozen H3R v1.1 protocol/test-manifest identity.
- Evidence: `QA_REPORT_H3R_v1.1_DECISIVE_PRE_EXECUTION.md`, authorization snapshot, protocol SHA256 `5cdecfe758b9908f0f2199b6e7cd5632e9636b887e141d265fdb9265c107334d`, test-manifest SHA256 `371799bb474f2f425db7acacf63cba3de7ca4876f61cbfa5a88549363d97255d`.
- Impact: exactly one decisive execution was eligible; rerun remained prohibited after scientific access consumption.

### PM-DEC-2026-09-09-15

- Decision: accept H3R v1.1 G2-G7 closure with `GATE_VERDICT = PASS_WITH_LIMITS` and `SCIENTIFIC_VERDICT = FALSIFIED_UNDER_TESTED_CONDITIONS`.
- Evidence: `EXP-H3R-002`, G3/G4/G5/G6/G7 reports, and `governance/H3R_v1.1_DECISIVE_EXECUTION_CLOSURE.md`.
- Integrity: exactly one decisive access event, 20/20 valid frozen cells, 6039/6039 test rows, no P0/P1 blockers.
- P2: redundant per-cell observation-hash metadata mismatch is retained by `governance/H3R_v1.1_DECISIVE_EVIDENCE_ERRATUM_001.md`; correct identity was enforced before metric access.
- Impact: H3R v1.1 is `CLOSED_WITH_LIMITS / NO_RERUN`. The negative result must not be rescued by tuning, seed/baseline/candidate changes, threshold changes, evidence repair, or rerun.

### PM-DEC-2026-09-09-16

- Decision: keep H4 `NOT_OPENED / DEFERRED_BY_OWNER` after H3R v1.1 closure.
- Reason: the autonomous H3R task closes H3R only; it does not contain owner authorization to instantiate H4.
- Next gate: explicit owner decision on the post-H3R research frontier.

## 11. Next Executable Step

`OWNER DECISION ON POST-H3R FRONTIER`.

H3R v1.1 is scientifically closed with a bounded negative result and no rerun. H4 remains `NOT_OPENED / DEFERRED_BY_OWNER` until an explicit owner decision opens it.

## 12. Overall Project State

```text
Benchmark / software infrastructure: ON_TRACK
Reference learner benchmark: ACCEPTED_WITH_LIMITS
H1: CLOSED_WITH_LIMITS
H2: CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS
H3: CLOSED_WITH_LIMITS / NOT_SUPPORTED
H3R v1.0: CLOSED / PROTOCOL_DEVIATION / NO_SCIENTIFIC_VERDICT / NO_RERUN
H3R v1.1: CLOSED_WITH_LIMITS / FALSIFIED_UNDER_TESTED_CONDITIONS / NO_RERUN
H4: NOT_OPENED / DEFERRED_BY_OWNER
H5 scientific closure: OPEN
External validity: AT_RISK / UNPROVEN
Research release: NOT_READY
Current frontier: POST-H3R OWNER DECISION — H4 REMAINS NOT_OPENED
```
