# OIR-PPV Research Execution Plan v1.0

## 1. Document purpose

Tài liệu này là roadmap và execution contract hiện hành của OIR-PPV Research v1.0.

Nó được viết lại sau khi rà soát:

- `README.md`;
- `theory.md`;
- toàn bộ `tasks/DEV_TASK_*.md`;
- các `HANDOFF_*.md`;
- `QA_REPORT_HANDOFF_007_v5.md`;
- `PM_STATUS_2026-09-08.md`;
- `H6_CREATIVE.md`;
- lineage đã archive tại `../archive/`, bao gồm checkpoint cuối v0.13.10.

Mục tiêu của PLAN là giữ ba lớp tách biệt:

1. **historical research lineage**;
2. **benchmark/software infrastructure**;
3. **scientific evidence và claim closure**.

Implementation PASS không được tự động nâng thành scientific PASS.

---

## 2. Research lineage và boundary với toy lab

OIR-PPV v1.0 hình thành từ chuỗi nghiên cứu toy-lab v0.1 -> v0.13.10.

Các artifact cũ được lưu tại:

```text
D:\WORK\RESEARCH\MindForge\docs\research\oir-ppv\archive
```

Checkpoint cuối của lineage là v0.13.10, nhưng archive hiện xác nhận:

```text
status: RECONSTRUCTED
historical_source_found: false
claim_level: reconstruction_only
```

Do đó v0.13.10 có vai trò:

- nguồn gốc hypothesis;
- nguồn gốc kiến trúc invariant -> generator -> intervention -> counterfactual;
- nguồn tham khảo cho failure history và research motivation;
- historical/reconstruction checkpoint.

v0.13.10 **không** được dùng như:

- verified implementation của research v1.0;
- original historical replay khi original source/seed/artifact chưa được xác nhận;
- bằng chứng trực tiếp để PASS hypothesis hiện tại;
- baseline có thể trộn vào evidence CCB mà không có provenance riêng.

Nguyên tắc kế thừa:

```text
Toy lab v0.1 -> v0.13.10
        |
        | hypothesis / failure / architecture lineage only
        v
OIR-PPV Research v1.0
        |
        v
Controlled Causal Benchmark evidence
```

Archive là research history. `research/` là chương trình validation hiện hành.

---

## 3. Current research objective

OIR-PPV không claim phát minh invariant learning, causal representation learning,
domain generalization hoặc causal intervention.

Research v1.0 kiểm tra một câu hỏi hẹp và có thể falsify hơn:

> Một invariant representation có thể được đưa qua một pipeline thống nhất để
> dự đoán, sinh manifestation theo context, chịu nuisance/context shift và giữ
> causal consistency dưới intervention tốt hơn các baseline hợp lý hay không?

Pipeline mục tiêu:

```text
Ground Truth SCM
      |
      v
Environment Generator
      |
      v
Experience (S,A,Y,Z,N)
      |
      v
Invariant Learner
      |
      v
Invariant I
      |----------------------|
      v                      v
Policy/Predictor      Manifestation Generator
pi(I,S,Z)             G(I,Z,N)
      |                      |
      +----------+-----------+
                 v
         Intervention Engine
          do(Z), do(N), do(A)
                 |
                 v
      Counterfactual Evaluator
                 |
                 v
              Evidence
```

Current empirical state:

```text
Software / protocol / reproducibility: PASS
Robust invariant/generalization claim: NOT_SUPPORTED
```

README `Claim Boundary` phải được hiểu là **target/conditional claim**, chưa phải
kết luận đã được chứng minh.

---

## 4. Research question tree

### H1 — Compression

Invariant đạt complexity/utility trade-off tốt hơn raw/context memorization.

State: `CLOSED_WITH_LIMITS`.

Scientific classification: `SUPPORTED_WITH_LIMITS`.

Accepted scope:

- frozen exact-row `MEM` comparator;
- ENV-1..ENV-4;
- seeds `42, 123, 456, 789, 1011`;
- frozen `epsilon = 0.02` utility non-inferiority rule;
- corrected canonical `X -> I` inference-state accounting from
  `DEV_TASK_009_FIX_01` / `HANDOFF_009_H1_v2.md`.

Claim boundary: H1 does **not** establish superiority to RAW and does **not**
establish superiority to memory architectures in general. `MEM` had zero exact
test hits under this benchmark, so the accepted result is intentionally narrow.

### H2 — Transfer

Invariant cải thiện performance trên context/environment chưa thấy.

State: `CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS`.

Independent QA source: `QA_REPORT_HANDOFF_010_H2.md`.

Frozen tested scope:

- primary baseline: `L0/PCA`;
- tested learners: `L1 MLP`, `L2 VAE`, `L3 IRM-style surrogate`, `L4 DANN`;
- eligible OOD environments: `ENV-1`, `ENV-3`, `ENV-4`;
- seeds: `42, 123, 456, 789, 1011`;
- paired unit: same environment + same seed;
- 60/60 primary pairs retained and independently replayed.

All four learner families produced negative mean paired `Delta_OOD`, with 95%
bootstrap confidence intervals entirely below zero under the frozen H2 rule.

Claim boundary: this falsifies only the tested L1-L4 configurations relative to
the frozen L0/PCA reference in the tested synthetic environments/seeds. It does
not falsify invariant learning in general, canonical MLP/VAE/IRM/DANN methods,
MindForge, or untested environment families.

Research interpretation retained from H2:

```text
compression / compact representation
        does not imply
OOD transfer improvement
```

H2 therefore removes the assumption that a learned or more complex
representation automatically transfers better than a simpler reference.

### Q-H2.1 — What makes an invariant transferable?

H2 creates a new research question to analyze before PM closes H3:

> Một invariant phải có những thuộc tính nào thì mới chuyển giao tốt sang
> environment/context chưa thấy?

Working interpretation:

```text
E -> I_right -> Transfer
```

where `I_right` is not assumed to mean a larger, nonlinear, variational,
environment-regularized, or domain-adversarial representation merely by method
class. Candidate properties to distinguish include:

- retaining task/causal signal required across environments;
- suppressing nuisance/shortcut information;
- stability under task-preserving intervention;
- avoiding representational complexity that does not add transferable signal;
- preserving the minimum structure needed for unseen-context prediction.

This is a **research question**, not a new supported claim and not a new H3
implementation requirement. It must be investigated from already accepted H1/H2,
EXP-LRN-001, and available H3-preparation evidence before H3 PM closure.

Q-H2.1 must not modify or invalidate the existing H3 closure design, code,
protocol semantics, matrix, seeds, metrics, or work already completed. If the
existing evidence cannot answer it, record `UNRESOLVED` and continue H3 under its
already-defined closure contract. Do not alter H2 thresholds, seeds, baseline, or
evidence to pursue this question.

Pre-H3 analysis result: `UNRESOLVED`.

Analysis artifact: `Q_H2_1_TRANSFERABLE_INVARIANT_ANALYSIS.md`.

Current evidence supports only a directional candidate: a transferable invariant
may need to retain task/causal signal while suppressing nuisance/shortcut signal
and preserving utility under task-preserving intervention. A stronger candidate
definition is `I_candidate = causal sufficient statistic for the task under the
tested shifts`, but this is not yet an established OIR-PPV result. H3 may
strengthen, contradict, or leave this interpretation unresolved without changing
its already-defined closure contract.

### H3 — Nuisance Robustness

Representation/policy ít phụ thuộc nuisance hơn baseline dưới `do(N)` và shift.

State: `CLOSED_WITH_LIMITS / NOT_SUPPORTED`.

Independent QA source: `QA_REPORT_HANDOFF_011_H3_v3.md`.

Accepted evidence authority: `correction_v3`, with the metadata erratum recorded
in `protocols/h3/historical/README.md`.

Frozen tested scope:

- baseline: `L0/PCA`;
- tested learners: `L1-L4` adapted/surrogate configurations;
- seeds: `42, 123, 456, 789, 1011`;
- selected targets: `background_noise` in ENV-1, `occlusion` in ENV-2,
  `spurious_feature` in ENV-4;
- ENV-3: `INAPPLICABLE` because selected `do(N)` changes `Y` and task labels;
- 100/100 cells preserved; 60/60 eligible candidate-vs-L0 pairs valid;
- 225/225 eligible intervention records satisfy causal-isolation checks.

All L1-L4 configurations fail the frozen H3 success rule relative to L0/PCA.
The historical claim remains target-specific and does not generalize to nuisance
robustness overall, canonical external implementations, MindForge, or untested
environments/targets.

Q-H2.1 remains `UNRESOLVED`: H3 does not establish what property is sufficient
for transfer. Its negative result is retained as evidence that the tested learned
representations do not jointly improve transfer and the historical nuisance-
robustness criteria over the PCA reference.

### H3R — Revised Robustness under Formal Spec v1.0

State: `PROTOCOL_PREPARATION / NOT_EXECUTED / NOT_FROZEN`.

H3R is a revised successor protocol, not a rerun or relabeling of H3.

Canonical sources:

- `ontology/ontology_v1.0.md` — `PRINCIPLE-LEVEL LOCKED`;
- `formal/formal_spec_v1.0.md` — `FINAL`;
- `protocols/h3r/H3_TO_H3R_LINEAGE.md`;
- `protocols/h3r/H3R_PROTOCOL_v1.0_DRAFT.md`;
- `protocols/h3r/h3r_protocol_schema.json`;
- `protocols/h3r/h3r_freeze_checklist.md`.

H3R revises the future robustness estimand around a predeclared observation-noise
family that preserves mechanism semantics, retained clean utility, Formal v1.0
representation lifecycle/split/metric/evidence/test-lock contracts, and explicit
separation of `eta`, `Z_e`, `S_t`, and `I_M`.

H3R inherits H3 design lineage only. `evidence_status = NONE_YET`.

### H4 — Counterfactual / Causal Accuracy

Representation giữ causal response dưới intervention và giảm counterfactual error.

State: `NOT_OPENED / DEFERRED_BY_OWNER`.

H4 has historical formalization material, but no H4 task/protocol is active after
H3 closure. H3R review/freeze is the only active frontier.

### H5 — Minimal Sufficiency

Ablation phải làm giảm performance khi bỏ thành phần cần thiết; thêm redundancy
không được tạo uplift giả.

State: `FORMALIZED`, chưa tới closure gate.

### H6 — Creative Recombination

Một invariant hữu ích có thể hỗ trợ manifestation mới khi kết hợp với context,
constraint hoặc goal mới mà vẫn giữ validity và invariant consistency.

Candidate metric:

```text
CreativeScore = Validity x Novelty x InvariantConsistency
```

State: `PARKED / FORMALIZATION_PENDING`.

H6 đã được giữ trong roadmap nhưng chưa được nhập vào frozen core protocol.
Prototype hiện có tại:

```text
experiments/OIR_PPV_Creative_Recombination_Experiment_v0.1/
```

H6 chỉ được promote sau khi reference learner benchmark được freeze và QA accept,
trừ khi một câu hỏi validity của benchmark lõi bắt buộc phải dùng H6 để giải quyết.

---

## 5. Source-of-truth hierarchy

Không có một file duy nhất được phép override mọi lớp. Authority được chia theo
loại quyết định:

| Layer | Authority |
| --- | --- |
| Research framing / scope | `README.md` + quyết định owner hiện hành |
| Formal hypothesis | `theory.md`, và tài liệu hypothesis đã được PM freeze |
| Execution order / milestone / dependency | `PLAN.md` |
| Frozen metric/protocol semantics | `benchmark/M3_PROTOCOL.md` (`M3-Protocol-v1.0`) |
| Development scope | task hiện hành trong `tasks/` |
| Implementation claim | latest developer handoff |
| Acceptance | independent QA report / PM acceptance gate |
| Historical lineage | `../archive/` |

Khi có conflict:

1. không sửa protocol để làm implementation PASS;
2. không dùng handoff để override QA verdict;
3. không dùng archive reconstruction để override current evidence;
4. PM phải mở amendment/version mới nếu semantics thực sự cần đổi.

---

## 6. Protocol freeze

Frozen protocol hiện hành:

```text
Name:    M3_PROTOCOL
Version: M3-Protocol-v1.0
Path:    benchmark/M3_PROTOCOL.md
SHA256:  f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a
```

Protocol semantics không được sửa in-place trong M4.1.

Nếu reference learner integration cho thấy protocol cần thay đổi về:

- metric definition;
- threshold;
- seed policy;
- split semantics;
- intervention semantics;
- evaluator behavior;
- artifact schema có ý nghĩa khoa học;

thì dev phải dừng phần bị ảnh hưởng và báo PM. PM quyết định:

```text
NO_CHANGE
hoặc
M3-Protocol-v1.1 amendment / protocol successor
```

Evidence đã sinh dưới protocol cũ không được trộn im lặng với evidence mới.

---

## 7. Milestone roadmap

### M0 — Research Foundation Freeze

**Goal**

Tạo research structure, provenance skeleton và executable foundation.

**Primary task**

- `DEV_TASK_001.md`

**Handoff**

- `HANDOFF_001.md`

**State**

`ACCEPTED` theo project history.

**What it unlocked**

Controlled environment implementation.

---

### M1 — Controlled Environment Implementation

**Goal**

Implement ENV-1..ENV-4 và deterministic generation/intervention infrastructure.

**Tasks**

- `DEV_TASK_002.md`
- `DEV_TASK_003.md` — M1 QA corrections

**Accepted handoff lineage**

- `HANDOFF_002_v2.md`

**State**

`ACCEPTED` theo project history.

**What it unlocked**

Common baseline benchmark execution.

---

### M2 — Baseline Benchmark Suite

**Goal**

Tạo common benchmark runner, B0-B5 baseline slots, metric/provenance foundation và
đóng các QA gaps về probability/counterfactual/limitation metadata.

**Tasks**

- `DEV_TASK_004.md`
- `DEV_TASK_005.md`

**Handoffs**

- `HANDOFF_003.md`
- `HANDOFF_004.md`

**State**

`ACCEPTED` theo project history.

**Important limitation inherited**

M2 baseline slots ban đầu có placeholder behavior. M2 acceptance là acceptance
của benchmark infrastructure, không phải scientific benchmark quality.

---

### M3 — OIR-PPV Pipeline + Causal Validation + Protocol Freeze

**Goal**

Tạo measurable path:

```text
Experience -> I -> G(I,Z,N) -> Evaluation
```

và chuẩn hóa:

- causal validation;
- dependency/leakage analysis;
- pluggable learner interfaces;
- frozen benchmark protocol.

**Tasks**

- `DEV_TASK_006.md`
- `DEV_TASK_007.md`

**Handoffs**

- `HANDOFF_005.md`
- `HANDOFF_006.md`

**State**

`ACCEPTED` theo project history.

**What it unlocked**

Real learner integration under a frozen protocol.

---

### M4 — Real Learner Plumbing + Stress Protocol Closure

**Goal**

Chứng minh benchmark/software path thực sự chạy real learner, stress shift,
runtime provenance và reproducibility mà không silent fallback hoặc protocol drift.

**Task lineage**

- `DEV_TASK_008.md`
- `DEV_TASK_008_FIX_01.md`
- `DEV_TASK_008_FIX_02.md`
- `DEV_TASK_008_FIX_03.md`
- `DEV_TASK_008_FIX_04.md`

Các FIX task là historical correction chain. Trạng thái `OPEN` còn ghi trong
task file cũ không override QA closure mới hơn.

**Accepted handoff**

- `HANDOFF_007_v5.md`

**Independent QA**

- `QA_REPORT_HANDOFF_007_v5.md`
- verdict: `PASS`

**Accepted source SHA**

```text
f7e446d64d1c040cd168ae859d04503509cfe8ec
```

**Infrastructure evidence**

- FIX_04 tests: 6/6 PASS in independent QA replay;
- full regression: 51/51 PASS;
- Windows CP1252 M2 CLI: PASS;
- four stress scenarios x two repeat runs: reproducibility 4/4 PASS;
- protocol/source provenance audit: PASS.

**Research result retained**

```text
ROBUST INVARIANT / GENERALIZATION: NOT_SUPPORTED
```

Observed limitations include:

- context leakage: 4/4 stress scenarios;
- nuisance leakage: 3/4;
- Context Stress `generalization_delta ~= -0.83048`;
- trained predictive accuracy in retained controlled comparison below PCA
  placeholder (`0.848` vs `0.984`).

**State**

`ACCEPTED FOR INFRASTRUCTURE / PROTOCOL CLOSURE`.

M4 does not close H1-H5.

---

### M4.1 — Standard Learner Benchmark Freeze

**Reference benchmark milestone**

**Task**

- `tasks/DEV_TASK_008_1.md`

**State**

`ACCEPTED_WITH_LIMITS`.

QA/PM acceptance records:

- `HANDOFF_008_1.md`
- `QA_REPORT_HANDOFF_008_1.md`

`EXP-LRN-001` is now the frozen reference learner benchmark for downstream
H1-H4 closure work. Its fidelity and scope limitations remain binding.

**Expected starting source SHA**

```text
f7e446d64d1c040cd168ae859d04503509cfe8ec
```

**Research purpose**

Xác định benchmark có phân biệt được các representation learner family hợp lý
dưới cùng environment, split, intervention, metric và seed policy hay không.

**Reference learners**

```text
L0 PCA
L1 MLP
L2 VAE
L3 IRM-style
L4 DANN
```

MindForge không được tham gia milestone này.

**Required execution order**

```text
learner contract audit
  -> implementation fidelity/provenance
  -> one smoke cell per learner
  -> smoke reproducibility
  -> freeze matrix + seed list
  -> full EXP-LRN-001 matrix
  -> aggregate comparison
  -> developer handoff HANDOFF_008_1.md
  -> independent QA
  -> PM freeze decision
```

Không được chạy full matrix nếu smoke contract/artifact schema fail.

**Milestone success condition**

M4.1 được accepted khi:

1. PCA, MLP, VAE, IRM-style, DANN dùng common learner contract;
2. non-PCA learners thực sự train parameters;
3. evaluator/protocol không có learner-specific semantic changes;
4. full matrix dùng frozen split/intervention/seed set;
5. failed cells được giữ nguyên;
6. implementation fidelity được ghi `faithful`, `adapted` hoặc `surrogate`;
7. reproducibility và provenance đủ để QA replay;
8. `EXP-LRN-001` được PM/QA freeze.

**Decision gate after M4.1**

```text
CASE A: Benchmark discriminates learner families plausibly
        -> freeze EXP-LRN-001
        -> allow MindForge integration

CASE B: All learners fail similarly / evaluator cannot distinguish
        -> do NOT add MindForge
        -> open benchmark-validity investigation

CASE C: Protocol defect discovered
        -> freeze current evidence
        -> protocol amendment/version decision
        -> rerun only invalidated matrix scope
```

---

### M5 — MindForge Learner Integration

**State**

`ELIGIBLE_BUT_DEFERRED_BY H1-H4 REFERENCE CLOSURE ORDER`.

**Entry gate**

- `EXP-LRN-001` is QA accepted;
- reference learner implementations and fidelity labels frozen;
- evaluator/protocol frozen;
- seed/split/intervention matrix frozen.

**Goal**

Đưa MindForge vào như một learner mới và so sánh trên benchmark đã tồn tại trước
khi MindForge tham gia.

**Scientific constraint**

Không tune benchmark theo MindForge result.

MindForge phải dùng:

- cùng environment;
- cùng held-out/OOD definition;
- cùng intervention;
- cùng metric;
- cùng seed policy;
- cùng compute/reporting policy ở mức hợp lý.

Nếu MindForge cần interface khác, adapter phải nằm ở learner boundary; evaluator
không được đổi riêng cho MindForge.

**Primary outputs**

- MindForge learner adapter;
- frozen comparison against EXP-LRN-001;
- per-seed and aggregate metrics;
- leakage/generalization/counterfactual evidence;
- complexity/cost report;
- independent QA verdict.

---

### M6 — H1-H5 Claim Closure

**State**

`ACTIVE` for reference-learner hypothesis closure.

Current closure state:

```text
H1  CLOSED_WITH_LIMITS / SUPPORTED_WITH_LIMITS
H2  CLOSED / FALSIFIED_UNDER_TESTED_CONDITIONS
H3  CLOSED_WITH_LIMITS / NOT_SUPPORTED
H3R PROTOCOL_v1.0_FROZEN / NOT_EXECUTED / TEST_LOCKED
H4  NOT_OPENED / DEFERRED_BY_OWNER
H5  FORMALIZED / LATER
```

MindForge-specific conclusions remain deferred until the reference closure layer
is stable enough to preserve benchmark independence.

**Goal**

Tách hai câu hỏi:

1. OIR-PPV benchmark có đo được điều nó tuyên bố đo không?
2. Learner nào, nếu có, thực sự hỗ trợ H1-H5 dưới benchmark đã freeze?

**Required closure evidence**

- multi-seed results;
- per-seed failures;
- uncertainty/variance phù hợp;
- baseline/control integrity;
- ablation cho H5;
- intervention/counterfactual evidence cho H3/H4;
- complexity accounting cho H1/H5;
- exact claim boundary theo tested environment families.

Possible hypothesis labels:

```text
SUPPORTED
SUPPORTED_WITH_LIMITS
INCONCLUSIVE
NOT_SUPPORTED
FALSIFIED_UNDER_TESTED_CONDITIONS
```

Không dùng từ `proved` cho evidence synthetic giới hạn.

---

### M7 — H6 Creative Recombination Benchmark

**State**

`PARKED` cho đến khi M4.1 được freeze; activation cần PM promotion.

**Goal**

Formalize và test:

```text
old experience + invariant + unseen context/constraint/goal
    -> novel valid manifestation
```

**Required work before execution**

1. formalize H6 trong hypothesis/theory amendment;
2. define competing nulls: memorization, nearest-neighbor recombination,
   random novelty, context-only generation;
3. freeze validity/novelty/invariant-consistency metrics;
4. define leakage/contamination checks;
5. freeze baseline family trước decisive run;
6. version H6 protocol riêng nếu metric semantics vượt M3-Protocol-v1.0.

**Important boundary**

H6 là nghiên cứu về recombination capability, không phải bằng chứng consciousness,
human creativity hay AGI.

---

### M8 — Research Release / Paper-Quality Freeze

**State**

`NOT_READY`.

Research release chỉ mở khi:

- reference benchmark được accepted;
- core hypotheses được đóng hoặc ghi inconclusive rõ ràng;
- negative findings được giữ nguyên;
- provenance đủ tái tạo;
- literature positioning được cập nhật;
- novelty claim không phụ thuộc toy-lab history;
- limitations/external-validity boundary được viết rõ;
- H6 được hoặc hoàn tất, hoặc tách thành follow-up research rõ ràng.

Possible release outcomes:

```text
FREEZE_SUPPORTED
FREEZE_SUPPORTED_WITH_LIMITS
FREEZE_INCONCLUSIVE
FREEZE_FALSIFIED
OPEN_NEW_RESEARCH_PHASE
```

---

## 8. Dependency graph

```text
Toy Lab v0.1 -> v0.13.10 archive
          |
          v
M0 Foundation
  |
  v
M1 Controlled Environments
  |
  v
M2 Benchmark Infrastructure
  |
  v
M3 Pipeline + Frozen Protocol
  |
  v
M4 Real-Learner/Stress Infrastructure Closure
  |
  v
M4.1 Reference Learner Benchmark Freeze
  |\
  | \--------------------------+
  v                            v
M5 MindForge Integration     M7 H6 Recombination
  |                            |
  +-------------+--------------+
                v
         M6/M7 Claim Closure
                |
                v
         M8 Research Release
```

Execution rule: M5 không được chạy trước M4.1 acceptance. H6 có thể được chuẩn bị
docs-only sau M4.1 freeze nhưng không được làm thay đổi core benchmark evidence.

---

## 9. Developer -> QA -> PM handoff contract

### Developer task files

Task operational files đặt tại:

```text
research/tasks/DEV_TASK_*.md
```

Theo project policy đã được owner chỉ định, `tasks/` là operational planning
artifact và không được đưa lên Git repository chỉ vì task được thực thi.

Task file phải có tối thiểu:

- objective;
- why now;
- dependencies;
- exact scope/out-of-scope;
- source of truth;
- branch/expected SHA khi cần;
- acceptance criteria;
- required tests/evidence;
- stop conditions;
- handoff deliverable;
- what completion unlocks.

### Developer handoff

Handoff phải là implementation claim, không phải acceptance verdict.

Tối thiểu gồm tám phần:

1. implementation summary;
2. changed files;
3. Git/source provenance;
4. exact commands;
5. runtime/dependencies;
6. artifact paths;
7. known limitations/failures;
8. developer self-check.

Research handoff bổ sung:

- protocol version/hash;
- dataset/environment/split identity;
- seed list;
- baseline/control/treatment identity;
- implementation fidelity;
- failed/skipped runs;
- per-seed evidence;
- exact claim boundary.

### QA gate

QA phải độc lập kiểm tra:

```text
Requirement
 -> Acceptance criterion
 -> Replay/inspection
 -> Raw evidence
 -> Verdict
```

Allowed QA verdicts:

```text
PASS
PASS_WITH_LIMITS
PARTIAL
FAIL
BLOCKED
UNVERIFIED
```

Scientific conclusion phải tách riêng khỏi software verdict.

### PM acceptance

PM chỉ mở task downstream khi:

- required QA verdict permits progression;
- blocking P0/P1 findings are closed;
- limitations are carried forward;
- dependency/branch/protocol identities are known.

---

## 10. Artifact and provenance governance

Mỗi decisive experiment phải có provenance đủ để tái tạo:

```text
code SHA
protocol version/hash
learner implementation identity
environment/config revision
split identity
seed
hyperparameters
runtime/dependency versions
exact command
raw artifact paths
derived metric paths
source clean/dirty state
```

Rules:

1. Artifact mới không overwrite accepted historical evidence.
2. Failed run là evidence; không xóa để làm matrix đẹp hơn.
3. Retry phải có lý do và provenance; không cherry-pick successful retry.
4. Large arrays ở binary/container artifact, JSON chỉ chứa metadata/hash/path.
5. Non-finite metric phải có explicit status/policy; không silently coerce thành
   scientific success.
6. Generated report không được sửa tay làm thay đổi metric mà không ghi provenance.

---

## 11. Benchmark contamination controls

Từ M4.1 trở đi, full matrix phải được coi như frozen evaluation asset.

Trước full run cần freeze:

- learner list;
- implementation fidelity label;
- environment list;
- split/OOD definitions;
- intervention settings;
- seed list;
- metrics;
- tolerance/reproducibility rule;
- stopping rule.

Sau khi full matrix được dùng để đánh giá:

- không tune learner hyperparameter trên test/OOD final cells rồi giữ cùng label;
- không thay seed vì result xấu;
- không bỏ environment khó;
- không sửa metric threshold post-hoc;
- không đưa benchmark expected outputs vào learner logic.

Nếu tuning là cần thiết, phải có development partition riêng và final evaluation
partition chưa được dùng cho tuning.

---

## 12. Risk register

| ID | Risk | Likelihood | Impact | Mitigation / Gate |
| --- | --- | --- | --- | --- |
| R1 | Current learner leaks context/nuisance | High | High | M4.1 phân biệt learner-specific failure với benchmark/evaluator problem |
| R2 | Synthetic ENV-1..4 quá hẹp | High | High | Giữ claim boundary hẹp; external/held-out family chỉ thêm sau core freeze |
| R3 | IRM/DANN/VAE implementation fidelity drift | Medium | High | Paper provenance + `faithful/adapted/surrogate` label + QA inspection |
| R4 | Full benchmark trở thành development set | Medium | High | Freeze matrix/seeds trước run; dev/final partitions; retain failed cells |
| R5 | Protocol semantics drift để cứu result | Medium | Critical | Frozen hash + fail-fast identity + versioned amendment only |
| R6 | Trộn toy-lab reconstruction với current evidence | Medium | High | Archive boundary trong Section 2; provenance labels bắt buộc |
| R7 | Infrastructure PASS bị hiểu thành research PASS | High | High | Tách software QA và scientific conclusion trong mọi report |
| R8 | MindForge vào quá sớm gây circular benchmark design | Medium | High | Hard block M5 cho tới EXP-LRN-001 QA freeze |
| R9 | H6 mở scope trước core benchmark closure | Medium | Medium/High | PARKED; promote bằng PM gate sau M4.1 |
| R10 | Single-seed reproducibility bị hiểu thành statistical support | High | High | M4.1/M6 bắt buộc documented multi-seed scientific evaluation |
| R11 | Reference methods cùng thất bại vì evaluator/environment defect | Medium | High | CASE B gate sau M4.1: benchmark-validity investigation trước MindForge |
| R12 | README/theory wording bị hiểu như established result | Medium | Medium | PLAN xác định target claim; docs cleanup ở PM-controlled docs task sau |

---

## 13. Evidence debt

Current evidence debt phải được giữ visible:

1. archive v0.13.10 không có verified original historical source/seed/artifact;
2. current real learner không chứng minh robust invariant/generalization;
3. `EXP-LRN-001` đã freeze/accept với limits; external validity và paper-fidelity
   limits vẫn phải carry forward;
4. H1 đã đóng với limits; H2 đã đóng `FALSIFIED_UNDER_TESTED_CONDITIONS` trong
   frozen L1-L4 vs L0/PCA scope; H3-H5 chưa có final closure;
5. H5 ablation/minimal sufficiency chưa được đóng;
6. H6 chưa formalize thành frozen experiment protocol;
7. external validity ngoài controlled synthetic environments chưa được chứng minh.

Không mở architecture generation mới chỉ để tránh các evidence debt này.

---

## 14. Stop rules

### Stop M4.1 and investigate benchmark validity when

- common learner contract cannot represent cited methods fairly;
- all reference learners produce indistinguishable pathological results;
- evaluator changes are required per learner;
- held-out leakage/contamination is found;
- protocol identity or provenance fails;
- full matrix was tuned after seeing final results.

### Stop MindForge comparison when

- EXP-LRN-001 is not frozen/accepted;
- MindForge requires changing evaluator semantics specifically for itself;
- baseline compute/data conditions become materially incomparable;
- final evaluation cells have already been used for MindForge tuning without a
  separate untouched evaluation set.

### Stop research v1.0 and freeze result when

- H1-H5 have a stable supported/not-supported/inconclusive conclusion under the
  defined scope;
- remaining uncertainty no longer changes the claim materially;
- further experiments are only low-information repetition;
- next questions require a new environment family, protocol family or theory
  version.

Negative result is a valid research closure.

---

## 15. Current project state

As of 2026-09-09:

```text
M0    ACCEPTED
M1    ACCEPTED
M2    ACCEPTED
M3    ACCEPTED
M4    ACCEPTED FOR INFRASTRUCTURE/PROTOCOL
M4.1  ACCEPTED_WITH_LIMITS
M5    ELIGIBLE_BUT_DEFERRED
M6    ACTIVE — H1 CLOSED_WITH_LIMITS; H2 FALSIFIED; H3 CLOSED_WITH_LIMITS; H3R NEXT
M7    PARKED
M8    NOT_READY
```

Overall PM state:

```text
Benchmark/software infrastructure: ON_TRACK
H1 scientific claim: SUPPORTED_WITH_LIMITS within frozen MEM comparator scope
H2 scientific claim: FALSIFIED_UNDER_TESTED_CONDITIONS within frozen L1-L4 vs L0/PCA scope
H3 scientific claim: NOT_SUPPORTED within frozen target-specific historical scope
H3R: PROTOCOL_v1.0_FROZEN / NOT_EXECUTED / TEST_LOCKED
H4: NOT_OPENED
H5 scientific claim: OPEN
```

`PM_STATUS_2026-09-08.md` remains a historical PM snapshot. Its prior
`Missing PLAN.md` risk is resolved by creation of this document; other research
risks remain active.

---

## 16. Next executable step

The protocol review/freeze and publication/provenance closure actions are complete. The freeze package was published at `7e90366fc062b425d0e5c529c4be81ad2bd54ac2`. The next governance action is:

```text
SEPARATELY AUTHORIZE H3R DECISIVE EXECUTION
```

Frozen H3R authority:

- `protocols/h3r/H3R_PROTOCOL_v1.0.md`;
- `protocols/h3r/h3r_protocol_v1.0.json`;
- `protocols/h3r/h3r_test_manifest_v1.0.json`;
- `protocols/h3r/h3r_test_access_log.md`;
- `QA_REPORT_H3R_PROTOCOL_v1.0_FREEZE.md`;
- `protocols/h3r/H3R_PROTOCOL_v1.0_DRAFT.md` (preserved pre-freeze draft);
- `protocols/h3r/h3r_protocol_schema.json`;
- `protocols/h3r/h3r_freeze_checklist.md`;
- Ontology v1.0 and Formal Spec v1.0 canonical manifests;
- historical H3 lineage and preserved closure evidence.

Independent review reports `PASS_WITH_LIMITS`, `P0=0`, `P1=0`; final
protocol/test/candidate identities are locked. Publication/provenance debt is closed.
Decisive H3R execution remains forbidden until a separate explicit execution task
unlocks the test. H4 remains unopened.
