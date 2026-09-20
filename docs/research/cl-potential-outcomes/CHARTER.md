# CL-PO — Continual Learning Potential Outcomes

Trạng thái: **CHARTER / CHƯA THỰC NGHIỆM**

Nhánh:

```
research/cl-potential-outcomes
```

Điểm xuất phát:

```
research/kernel-cl
HEAD = a9159ae8f17693453e7b6378c92deb5effc4a56f
```

## 1. Vì sao KCL được sinh ra?

KCL — *Kernel Continual Learning* (**học liên tục ở tầng kernel**) không được tạo ra để xây một bộ phân loại action A/B/C.

Mục tiêu gốc của KCL là trả lời câu hỏi:

> MindForge kernel có thể học tuần tự nhiều task, tiếp tục học cái mới, giữ được kiến thức cũ, và làm điều đó bằng một cơ chế nhỏ/gọn có bằng chứng nhân quả hay không?

Chuỗi bằng chứng ban đầu đi theo đúng mục tiêu này:

- KCL-1: tạo *forgetting substrate* — **môi trường quên có kiểm soát**;
- KCL-2: chứng minh forgetting tái lập;
- KCL-3: chứng minh bounded replay giảm forgetting có tính nhân quả;
- KCL-4: xác định replay tối thiểu 6.25% trong cấu hình đã freeze;
- KCL-5/5.2: kiểm tra generalization trên task-pair mới;
- KCL-6: chứng minh fixed replay compute vẫn giữ hiệu quả qua 4 task;
- KCL-6.1→6.4: nghiên cứu cách biểu diễn/bảo toàn memory với chi phí nhỏ hơn.

Vì vậy capability đích của KCL luôn là:

```
learn new task
+
retain prior knowledge
+
bounded compute / memory
+
reproducible evidence
```

## 2. Vì sao KCL chuyển sang boundary coordination?

KCL-6.5.2/6.5.3 phát hiện một hiện tượng mới:

- task hiện tại có thể được học tốt;
- nhưng trạng thái kết hợp model + AdamW sau task có thể làm giảm khả năng học task tương lai;
- riêng model state hoặc optimizer state không đủ gây lỗi;
- lỗi xuất hiện từ *joint model–optimizer state* — **trạng thái kết hợp model và optimizer**.

Từ đó phát sinh yêu cầu kiến trúc:

```
JOINT_MODEL_OPTIMIZER_TASK_BOUNDARY_COORDINATION
```

hay một cơ chế điều phối trạng thái học tại điểm chuyển task.

KCL-6.5.5 sau đó cho thấy A/B/C có trade-off khác nhau:

- A carry-all: giữ state nhưng có thể làm giảm plasticity;
- B reset-all: có thể bảo toàn retention ở một số trường hợp nhưng làm acquisition chậm/xấu;
- C reset moments: tăng plasticity nhưng có thể làm retention giảm.

Do đó controller tương lai phải phụ thuộc trạng thái.

## 3. Vì sao hard-label route được mở?

KCL-6.5.6→6.5.9.8 cố tìm một representation đủ để dự đoán:

- safe reset opportunity;
- action regime;
- A_ONLY;
- mechanism-specific labels;
- đặc biệt `MECH{P+R,R}`.

Đây là một proxy hợp lý cho câu hỏi controller:

> trạng thái này nên dùng action nào?

Nhưng convergence review đã cho thấy formulation này không hội tụ thành predictor đủ điều kiện.

Các family đã test gồm:

- global/static state;
- localized LRBS-v1;
- mechanism-specific hard targets;
- MRIG-v1 static intervention geometry;
- TRIG-v1 temporal geometry;
- exact FUTURE-PROBE-v1 P1-P8.

Không family nào qualify target khó `MECH{P+R,R}`.

## 4. Pivot khoa học

CL-PO đổi **đối tượng cần học**, không chỉ đổi model.

Formulation cũ:

```
boundary state
→ hard label / mechanism class
→ action
```

Formulation mới:

```
boundary state
→ action-specific continuous outcomes
→ action contrasts / uncertainty
→ frozen safety contract
→ decision
```

Trong đó với mỗi action `a ∈ {A,B,C}` ta muốn ước lượng:

```
Y_a =
[
  plasticity / acquisition outcome,
  retention outcome,
  final current-task accuracy,
  robustness / safety margin
]
```

Sau đó mới suy ra:

```
Delta_B = Y_B - Y_A
Delta_C = Y_C - Y_A
```

và áp rule an toàn đã freeze.

## 5. Tại sao pivot này phù hợp hơn với mục tiêu gốc của KCL?

Mục tiêu gốc không phải đoán đúng tên mechanism.

Mục tiêu là:

> giữ khả năng học mới + giữ kiến thức cũ dưới sequential learning.

Các quantity liên quan trực tiếp đến mục tiêu này chính là:

- plasticity;
- retention;
- final acquisition;
- action cost;
- safety margin.

Hard label chỉ là sản phẩm hậu xử lý từ các quantity này qua threshold.

CL-PO vì vậy quay lại capability gốc thay vì tối ưu proxy.

## 6. Lợi thế đặc biệt của KCL simulator

Nhiều bài toán *Potential Outcomes* — **kết quả tiềm năng của các can thiệp khác nhau** chỉ quan sát được một action thực tế.

KCL simulator lại có thể fork cùng một boundary state và chạy:

```
same boundary
├── A → outcome_A
├── B → outcome_B
└── C → outcome_C
```

Do đó trong môi trường nghiên cứu ta có gần-full-information counterfactual data — **dữ liệu phản thực gần đầy đủ**.

Điều này cho phép kiểm tra outcome predictability trực tiếp trước khi cần một controller.

## 7. Câu hỏi nghiên cứu chính

### Q0 — Target stability

Các hard labels hiện tại có ổn định hay phần lớn được tạo ra bởi mẫu nằm sát threshold?

### Q1 — Absolute outcome predictability

Có thể dự đoán riêng outcome liên tục của A/B/C từ boundary-time state hay không?

### Q2 — Contrast predictability

Có thể dự đoán:

```
Y_B - Y_A
Y_C - Y_A
Y_C - Y_B
```

ổn định hơn việc dự đoán absolute outcome hay hard label không?

### Q3 — Policy-conditioned structure

B và C có cần model riêng vì cơ chế optimizer khác nhau không?

### Q4 — Decision utility

Nếu outcome/contrast predict được, policy suy ra từ chúng có giảm *regret* — **tổn thất do chọn action kém hơn oracle** — dưới frozen safety constraints không?

### Q5 — Uncertainty-aware decision

Có thể xác định khi nào model đủ chắc để chọn action và khi nào phải *abstain* — **từ chối quyết định vì bất định quá cao** — hay không?

## 8. Những gì CL-PO không được làm

CL-PO không được:

- mở KCL-6.5.9.9;
- gọi đây là KCL-7;
- dùng protected confirmatory seeds của KCL để exploration;
- relax các safety threshold cũ để tạo PASS;
- bắt đầu bằng neural network lớn;
- dùng validation outcome để thiết kế feature;
- implement controller trước khi outcome prediction qualify;
- tuyên bố continual-learning production capability từ simulator.

## 9. Quan hệ với KCL

KCL vẫn là lineage khoa học gốc.

CL-PO kế thừa các fact đã chứng minh:

- fixed policy không đủ;
- action effects khác nhau;
- plasticity và retention phải xem là hai trục riêng;
- hard action/mechanism labels khó identify;
- current hard-label representation family đã hội tụ âm.

CL-PO không sửa hay thay thế verdict KCL.

## 10. Gate mở thực nghiệm

Không chạy model prediction trước khi hoàn thành:

```
CL-PO-P0
Target-Margin / Label-Stability Qualification
```

P0 phải freeze trước:

- exact outcome quantities;
- exact historical thresholds;
- definition của distance-to-threshold;
- fresh cohort;
- margin bands;
- adjudication;
- STOP/PIVOT.

Nếu P0 cho thấy hard labels nằm sát threshold đáng kể, điều đó củng cố pivot sang continuous outcomes.

Nếu P0 cho thấy labels ổn định xa threshold, CL-PO vẫn tiếp tục P1 để kiểm tra trực tiếp continuous outcome predictability.

## 11. Thành công của chương trình

CL-PO chỉ được xem là thành công khi chuỗi sau được chứng minh prospectively:

```
continuous outcomes are predictable
        ↓
action contrasts are predictable
        ↓
decision utility beats frozen baselines
        ↓
uncertainty can be calibrated
        ↓
independent replication
        ↓
controller qualification becomes admissible
```

Không bước nào được bỏ qua.
