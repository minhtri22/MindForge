# ACO Origin Audit — Why KCL Existed

Status: **AUDIT CLOSED BEFORE NEW SCIENTIFIC EXECUTION**

Base audited state: `research/kernel-cl@a9159ae8f17693453e7b6378c92deb5effc4a56f`

## 1. Q1 — KCL ban đầu được sinh ra để giải quyết vấn đề gì?

KCL không được sinh ra để dự đoán optimizer-boundary action.

Nguồn gốc trực tiếp là một prerequisite khoa học của continual learning:

1. Phase-0 P0.9 đã cố tìm một catastrophic-forgetting substrate trên real/natural language nhưng kết thúc `STOP`.
2. R1 giữ nguyên quyết định không thêm learning/memory architecture nếu chưa có bằng chứng.
3. KCL-0/KCL-1 mở lại câu hỏi ở một **kernel-only controlled substrate**, giữ nguyên `TransformerLM`, để chứng minh trước rằng:
   - A và B đều học được;
   - B được acquire sau A;
   - A bị quên sau B;
   - matched A→A control không tạo cùng failure.

Vì vậy `WHY_KCL_EXISTS` là:

> tạo một nền thực nghiệm có kiểm soát để MindForge có thể kiểm tra causal continual-learning mechanisms mà không thêm kiến trúc theo niềm tin.

Primary source:
- `docs/phases/phase-0-continual-protocol.md`
- `docs/phases/phase-0-continual-validation.md`
- `docs/research/deferred/continual-learning-memory.md`
- `docs/research/r1-open-source-learning-memory.md`
- `docs/research/kernel-continual-learning/kcl0-kcl1-protocol.md`

## 2. Q2 — Capability cuối mà KCL phục vụ là gì?

Phải phân biệt immediate KCL objective với broader MindForge capability.

### Immediate KCL objective

```text
reproducible sequential forgetting
        ↓
one causal mitigation
        ↓
retention + plasticity under controlled budget
```

### Broader MindForge capability

Historical roadmap:

```text
Phase 3 — continual learning
        ↓
Phase 4 — memory as a measurable mechanism
        ↓
Phase 5 — adaptive learning
```

Do đó capability đích không phải “optimizer-state management”.

Capability đích là:

> kernel có thể tiếp tục học thông tin/task mới trong chuỗi, giữ tri thức cũ ở mức đo được, quản lý chi phí compute/memory, và cuối cùng thích nghi cơ chế học dựa trên trạng thái thay vì một global rule cố định.

## 3. Q3 — Milestone KCL đã thay đổi objective như thế nào?

| Giai đoạn | Điều KCL chứng minh / phát hiện | Tác động lên objective |
|---|---|---|
| KCL-1/2 | controlled forgetting substrate + reproducibility | prerequisite được thiết lập |
| KCL-3/4 | bounded replay giảm forgetting; 6.25% là minimum positive dose dưới batch=16 | chuyển từ “failure exists?” sang “mitigation works?” |
| KCL-5/5.2 | replay generalizes qua unseen qualified task-pair families | giảm nguy cơ treatment overfit vào một task family |
| KCL-6 | fixed replay compute sống qua 4-task horizon nhưng storage tăng tuyến tính | lộ ra memory-scaling problem |
| KCL-6.1/6.2 | exact weighting không giúp; reconstructive schema nén losslessly trên workload | mở memory representation line |
| KCL-6.3/6.4/6.5 | fuzzy trace recoverable; naive fuzzy replay hại; clarification có causal retention benefit nhưng confirmatory plasticity không ổn định tuyệt đối | tách memory representation khỏi replay policy |
| KCL-6.5.1/2 | failure hiện diện cả trong sequential current-only trajectory | vấn đề không còn quy về clarification/replay |
| KCL-6.5.3/4 | joint model–optimizer interaction; AdamW moments là sufficient contributors trong tested transition | xác định task-boundary coordination problem |
| KCL-6.5.5 | A/B/C fixed policies có plasticity–retention tradeoff | global fixed rule bị loại |
| KCL-6.5.6→6.5.9.8 | nhiều observable representations không qualify hard boundary target/controller | predictive formulation hiện tại hội tụ âm |

## 4. Q4 — 6.5.x có còn giải đúng mục tiêu gốc?

**Có, nhưng chỉ như một subproblem.**

Chuỗi 6.5.x giải thích một nguyên nhân quan trọng của future plasticity failure và chứng minh rằng boundary action phải state-dependent trong tested envelope.

Tuy nhiên, từ KCL-6.5.6 trở đi research object đã thu hẹp thành:

```text
pre-boundary representation
        ↓
hard safe-action / mechanism label
        ↓
future controller
```

Đây không tương đương với original continual-learning objective.

Formal convergence vì thế đóng đúng **formulation này**, không đóng continual learning.

## 5. Q5 — Original objective hiện ở đâu?

| Original objective | Trạng thái | Evidence |
|---|---|---|
| Có controlled forgetting substrate | **ACHIEVED** | KCL-1/2 |
| Có causal anti-forgetting treatment | **ACHIEVED trong tested substrate** | KCL-3 |
| Có low-dose bounded replay | **ACHIEVED trong batch granularity hiện tại** | KCL-4 |
| Treatment generalizes qua >1 qualified pair family | **ACHIEVED trong synthetic family set** | KCL-5.2 |
| Fixed replay compute qua longer horizon | **ACHIEVED tới 4 tasks** | KCL-6 |
| Bounded/general memory storage | **CHƯA ACHIEVED tổng quát** | KCL-6.2 chỉ exact structural compression trên workload |
| Lossy/fuzzy memory usable trực tiếp | **FALSIFIED cho frozen naive replay policy** | KCL-6.3 |
| Clarification can reactivate fuzzy trace | **SUPPORTED**, nhưng absolute plasticity robustness chưa ổn định | KCL-6.4→6.5.2 |
| Need for state-dependent boundary treatment | **SUPPORTED / REPLICATED structurally** | KCL-6.5.5 + 6.5.9.1 |
| Hard-label boundary predictor/controller | **NOT QUALIFIED / STOP current formulation** | KCL-6.5.6→6.5.9.8 |
| Real-language / scale transfer of KCL mechanisms | **UNRESOLVED** | chưa được KCL chứng minh |
| Operational adaptive continual-learning controller | **UNRESOLVED** | KCL-7 unauthorized |

## 6. Q6 — Pivot mới phải phục vụ original objective như thế nào?

Pivot phải quay lại đại lượng trực tiếp của continual learning:

- plasticity;
- retention;
- strict current-task accuracy;
- action-specific tradeoff;
- uncertainty / distance to frozen safety margins.

Không được lấy việc predict một derived hard label làm goal tự thân.

## 7. Chosen pivot

Research object mới:

> **policy-specific continuous boundary outcomes**, sau đó mới đến action contrasts và cuối cùng mới có thể cân nhắc decision rule.

Working program name:

```text
Adaptive Continual Outcome Modeling (ACO)
```

Branch:

```text
research/adaptive-continual-outcomes
```

Đây là scientific pivot vì nó thay đổi **object being predicted** từ derived categorical label sang continuous generating outcomes. Nó không phải “thêm feature để cứu classifier”.

## 8. Literature bridge

Literature chỉ được dùng để định hình câu hỏi, không override KCL evidence.

- Murphy (2003), *Optimal dynamic treatment regimes*: state/history → action → outcome.
- Schulte et al. (2014), *Q- and A-learning Methods for Estimating Optimal Dynamic Treatment Regimes*: Q-learning models action-conditioned expected outcome; A-learning models action contrasts.
- Shalit, Johansson & Sontag (2017): potential-outcome response modeling under treatment heterogeneity.
- Zhao et al. (2012): outcome-weighted learning, emphasizing decision value rather than unweighted label accuracy.
- Chakraborty et al. (2010): nonregularity near weak/indifferent treatment effects motivates explicit margin/stability analysis.

ACO does **not** import medical causal assumptions wholesale. KCL is unusually favorable because the simulator can evaluate matched A/B/C counterfactual branches from the same pre-boundary state.
