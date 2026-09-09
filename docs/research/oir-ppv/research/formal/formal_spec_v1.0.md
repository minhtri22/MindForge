# OIR-PPV Formal Specification v1.0

**Trạng thái:** `FINAL`  
**Phiên bản:** v1.0  
**Ngày:** 2026-09-09  
**Phụ thuộc:** `ontology_v1.0.md`  
**Nguồn:** `formal_revised_v1.0.md` + closure review + FIX_01 reviewer amendments  
**Phạm vi:** Đặc tả chuẩn hóa; các giá trị benchmark cụ thể phải được khóa trong protocol riêng.

---

# 0. Mục tiêu và nguyên tắc

Đặc tả này chuyển ontology OIR-PPV v1.0 thành các định nghĩa vận hành có thể triển khai, tái lập và kiểm định.

Mỗi mục phải xác định tối thiểu:

- ký hiệu;
- định nghĩa;
- đối tượng đo;
- estimand;
- metric;
- phạm vi áp dụng;
- trường hợp không áp dụng;
- điều kiện khóa trước;
- dữ liệu cần lưu;
- phiên bản giao thức.


## 0.1. Ngôn ngữ quy phạm

Trong đặc tả này:

- **PHẢI**: bắt buộc để một protocol được coi là tuân thủ v1.0;
- **KHÔNG ĐƯỢC**: hành vi bị cấm;
- **NÊN**: mặc định được khuyến nghị, có thể lệch nếu protocol nêu lý do;
- **CÓ THỂ**: tùy chọn.

`FORMAL_SPEC_v1.0` định nghĩa **hợp đồng đo lường**. Nó không khóa các giá trị cụ thể như seed, threshold, shift magnitude hoặc test set của từng benchmark. Các giá trị đó thuộc protocol benchmark và phải được khóa trước khi chạy quyết định.

Ba nguyên tắc xuyên suốt:

1. **Không dùng test để chọn mô hình.**
2. **Không đồng nhất cơ chế thật với biểu diễn học được.**
3. **Mọi claim chỉ có nghĩa trong phạm vi task, intervention và shift class đã khóa trước.**

---

# 1. Mechanism Decomposition and Invariants

## 1.1. Ký hiệu

\[
M_{\text{shared}}
=
(
\mathcal G_{\text{shared}},
F_{\text{shared}},
\Theta_{\text{shared}}
)
\]

\[
M_e
=
\mathcal M(
\mathcal G_{\text{shared}},
F_{\text{shared}},
\Theta_{\text{shared}},
\Delta_e
)
\]

Trong đó:

- \(\mathcal G_{\text{shared}}\): cấu trúc phụ thuộc/đồ thị nhân quả được giả định chung;
- \(F_{\text{shared}}\): họ cơ chế/hàm sinh được giả định chung;
- \(\Theta_{\text{shared}}\): các tham số phải giữ cố định trong shift class đang xét;
- \(\Delta_e\): phần được phép biến thiên theo môi trường \(e\).

## 1.2. Tập bất biến của lớp dịch chuyển

\[
\operatorname{Inv}(\mathcal S_k)
=
\{
\text{các thành phần của }M_e\text{ phải giữ nguyên trong }\mathcal S_k
\}
\]

Mỗi benchmark phải công bố \(\operatorname{Inv}(\mathcal S_k)\) trước khi sinh dữ liệu quyết định hoặc huấn luyện mô hình.

## 1.3. Đối tượng đo

- cấu trúc nhân quả;
- hàm/cơ chế sinh;
- tham số chung;
- tham số biến thiên;
- điều kiện môi trường;
- điều kiện ban đầu.

## 1.4. Điều kiện khóa trước

Phải công bố:

1. \(\mathcal G_{\text{shared}}\);
2. \(F_{\text{shared}}\);
3. \(\Theta_{\text{shared}}\);
4. miền của \(\Delta_e\);
5. \(\operatorname{Inv}(\mathcal S_k)\);
6. tiêu chí xác định một môi trường thuộc hay không thuộc shift class.

## 1.5. Trường hợp không áp dụng

Nếu test thay đổi một thành phần thuộc:

\[
\operatorname{Inv}(\mathcal S_k)
\]

thì kết quả không được dùng để chứng minh transfer trong \(\mathcal S_k\). Có thể gắn nhãn:

- out-of-class stress test;
- mechanism-change test;
- benchmark version mới.

---

# 2. Shift-Class Declaration and Realization

## 2.1. Ký hiệu

\[
\operatorname{ShiftClass}_{\text{declared}}
\]

\[
\operatorname{ShiftClass}_{\text{realized}}
\]

\[
\Delta_e
\rightarrow
\operatorname{ShiftClass}
\rightarrow
\operatorname{Inv}
\]

## 2.2. Định nghĩa

Mỗi môi trường phải được gán shift class theo các thay đổi thật sự được sinh ra.

Không được gán hậu nghiệm shift class dựa trên việc kết quả tốt hay xấu.

## 2.3. Bất nhất declared/realized

Nếu:

\[
\operatorname{ShiftClass}_{\text{declared}}
\neq
\operatorname{ShiftClass}_{\text{realized}}
\]

thì môi trường:

- không được dùng để chứng minh claim ban đầu;
- phải được đánh dấu protocol deviation;
- hoặc benchmark phải tăng phiên bản.

## 2.4. Các trục shift tối thiểu

Không gộp mọi loại thay đổi vào một nhãn duy nhất. Benchmark phải mô tả riêng tối thiểu:

### A. Observation/surface shift

Thay đổi bề mặt hoặc cách quan sát, không đổi cơ chế.

### B. State-distribution shift

Thay đổi \(P(S)\).

### C. Parameter shift

Thay đổi các tham số được phép trong \(\Delta_e\).

### D. Environment-condition shift

Thay đổi \(Z_e\).

### E. Mechanism-component shift

Thay đổi một thành phần cơ chế nhưng vẫn giữ các thành phần trong \(\operatorname{Inv}(\mathcal S_k)\).

### F. Causal-structure shift

Thay đổi \(\mathcal G\).

Nếu causal-structure shift phá thành phần được khai báo trong \(\operatorname{Inv}(\mathcal S_k)\), không được gọi đó là transfer trong cùng lớp.


## 2.5. Hồ sơ dịch chuyển

Các trục A–F không bắt buộc loại trừ nhau. Một môi trường có thể đồng thời có nhiều loại thay đổi.

Mỗi môi trường PHẢI lưu một hồ sơ:

\[
\mathbf s_e
=
(
s_{\text{surface}},
s_{\text{state}},
s_{\text{parameter}},
s_{\text{environment}},
s_{\text{mechanism}},
s_{\text{graph}}
)
\]

cùng các giá trị \(\Delta_e\) thực tế.

`shift_class_declared` là claim class được khóa trước; `shift_profile_realized` ghi những thay đổi thật sự đã xảy ra. Tính hợp lệ của claim được kiểm tra từ cả hai.

---

# 3. Environment, State, and Intervention Distributions

## 3.1. Phân phối đánh giá

Phải công bố:

\[
e\sim\mu
\]

\[
S\sim\rho_e
\]

\[
a\sim\pi
\]

Trong đó:

- \(\mu\): quy tắc/phân phối chọn môi trường;
- \(\rho_e\): phân phối trạng thái trong môi trường \(e\);
- \(\pi\): phân phối hành động/can thiệp.

## 3.2. Không dùng một trường duy nhất cho mọi loại thiết kế test

Ba trục phải được khai báo riêng.

### 3.2.1. Domain relation

\[
\texttt{domain\_relation}
\in
\{
\text{interpolation},
\text{extrapolation}
\}
\]

### 3.2.2. Environment selection mode

\[
\texttt{selection\_mode}
\in
\{
\text{random},
\text{fixed-held-out},
\text{adversarial}
\}
\]

### 3.2.3. Aggregation mode

\[
\texttt{aggregation\_mode}
\in
\{
\text{mean},
\text{worst-case},
\text{quantile}
\}
\]

Các trường này độc lập và phải được lưu riêng.

## 3.3. Estimand trung bình

\[
\theta_{\text{mean}}
=
\mathbb E_{
e\sim\mu,
S\sim\rho_e,
a\sim\pi
}
\left[
d\left(
\hat p_\psi(\cdot\mid I_M,S,Z_e,a),
p_{M_e}(\cdot\mid do(A=a),S,Z_e)
\right)
\right]
\]

## 3.4. Sai số theo môi trường

\[
R_e
=
\mathbb E_{
S\sim\rho_e,
a\sim\pi
}
\left[
d\left(
\hat p_\psi(\cdot\mid I_M,S,Z_e,a),
p_{M_e}(\cdot\mid do(A=a),S,Z_e)
\right)
\right]
\]

## 3.5. Sai số tệ nhất

\[
\theta_{\text{worst}}
=
\max_{e\in\mathcal E_{\text{test}}}
R_e
\]

Nếu môi trường test là lấy mẫu từ một phân phối liên tục, phải định nghĩa rõ cách xấp xỉ worst-case.

## 3.6. Báo cáo bắt buộc

- mean;
- median nếu phù hợp;
- CI hoặc độ lệch chuẩn;
- per-environment risk;
- worst-case;
- số môi trường;
- số trạng thái;
- số can thiệp;
- domain relation;
- selection mode;
- aggregation mode.

---

# 4. Observation, Intervention, and Counterfactual Estimands

## 4.1. Quan sát

\[
p(Y\mid X)
\]

## 4.2. Hậu can thiệp

SCM:

\[
p_{M_e}
(
Y
\mid
do(A=a),
S_t^{-},
Z_e^{-}
)
\]

Trong đó \(S_t^{-}\) và \(Z_e^{-}\) là trạng thái/điều kiện trước can thiệp hoặc các biến được xác nhận không phải hậu duệ của can thiệp đang xét.

Mô hình học nhận hành động \(a\) như đầu vào:

\[
\hat p_\psi
(
y
\mid
I_M,
S_t^{-},
Z_e^{-},
a
)
\]

và được đánh giá bằng khoảng cách tới phân phối hậu can thiệp của SCM.

## 4.3. Phản thực

\[
Y_{a'}
\mid
A=a
\]

Nếu đánh giá phản thực, benchmark phải công bố:

- hành động factual;
- hành động counterfactual;
- biến ngoại sinh;
- quy tắc giữ/chia sẻ biến ngoại sinh giữa hai thế giới;
- điều kiện ghép cặp;
- cách sinh ground truth.

## 4.4. Quy tắc ký hiệu

- dùng \(do(A=a)\) cho toán tử can thiệp trong SCM;
- dùng \(a\) trong đầu vào predictor;
- không viết \(do(a)\) như một feature thông thường.


## 4.5. Rủi ro nhiệm vụ quan sát

Khi task là dự đoán quan sát, protocol PHẢI định nghĩa:

\[
R_{\text{task}}
=
\mathbb E_{(X,Y)\sim\nu}
\left[
\ell(
\hat p_\psi(\cdot\mid I_M,X),
Y
)
\right]
\]

hoặc một estimand tương đương được khóa trước.

## 4.6. Rủi ro phản thực

Khi có ground truth phản thực:

\[
R_{\text{cf}}
=
\mathbb E_{q\sim\kappa_{\text{cf}}}
\left[
d(
\hat Y_{a'}(q),
Y^{M_e}_{a'}(q)
)
\right]
\]

Trong đó \(q\) chứa factual state, factual action, counterfactual action và các biến ngoại sinh/ghép cặp cần thiết. \(\kappa_{\text{cf}}\) PHẢI được khóa trước.

Nếu không có ground truth phản thực, protocol KHÔNG ĐƯỢC báo cáo \(R_{\text{cf}}\) như một causal-ground-truth metric; chỉ được dùng proxy kèm evidence level phù hợp.

---

# 5. Interventional Sufficiency of \(I_M\)

## 5.1. Định nghĩa

\(I_M\) được gọi là **đủ hậu can thiệp tương đối** với:

\[
(
\mathcal T,
\mathcal A,
\mathcal E
)
\]

nếu nó cho phép tái tạo đủ chính xác các phân phối hậu can thiệp cần thiết trong phạm vi đó.

Đây không phải claim rằng \(I_M\) đã định danh toàn bộ cơ chế nhân quả thật.

## 5.2. Sai số

\[
\mathcal R_{\text{int-suff}}
=
\mathbb E_{
e\sim\mu,
S\sim\rho_e,
a\sim\pi
}
\left[
d
\left(
\hat p_\psi(
\cdot\mid I_M,S,Z_e,a
),
p_{M_e}(
\cdot\mid do(A=a),S,Z_e
)
\right)
\right]
\]

## 5.3. Chế độ can thiệp

### A. Interventional interpolation

Với action rời rạc:

\[
\mathcal A_{\text{test}}
\cap
\mathcal A_{\text{train}}
\neq
\varnothing
\]

Với action liên tục, phải dựa trên support hoặc vùng giá trị.

### B. Interventional extrapolation

Không định nghĩa chỉ bằng việc hai tập action không giao nhau.

Với action liên tục, dùng:

\[
\operatorname{supp}(\pi_{\text{test}})
\not\subseteq
\operatorname{supp}(\pi_{\text{train}})
\]

hoặc định nghĩa một vùng ngoại suy được khóa trước.

### C. Compositional intervention

Các thành phần can thiệp đã thấy nhưng tổ hợp mới chưa từng xuất hiện trong huấn luyện.

## 5.4. Trường hợp không áp dụng

Không được gọi là interventional sufficiency nếu chỉ có observational prediction mà không có truy vấn hậu can thiệp hoặc phản thực tương ứng.


## 5.5. Tách interventional sufficiency và transfer

Hai phép đo có thể dùng cùng loss nhưng khác miền đánh giá.

Trong miền học/xác thực:

\[
R_{\text{int-suff,val}}
=
\mathbb E_{
e\sim\mu_{\text{val}},
S\sim\rho_e,
a\sim\pi_{\text{val}}
}
\left[
d(
\hat p_\psi(\cdot\mid I_M,S,Z_e,a),
p_{M_e}(\cdot\mid do(A=a),S,Z_e)
)
\right]
\]

Trên miền kiểm tra chưa thấy:

\[
R_{\text{transfer,test}}
=
\mathbb E_{
e\sim\mu_{\text{test}},
S\sim\rho_e,
a\sim\pi_{\text{test}}
}
\left[
d(
\hat p_\psi(\cdot\mid I_M,S,Z_e,a),
p_{M_e}(\cdot\mid do(A=a),S,Z_e)
)
\right]
\]

với:

\[
e\in
\operatorname{ShiftClass}_{\text{declared}}
(\mathcal E_{\text{train}})
\]

theo semantics của benchmark.

Nếu claim transfer là **so sánh với baseline** \(B\), protocol PHẢI khóa dấu và định nghĩa effect, ví dụ:

\[
\Delta_{\text{transfer}}(I,B)
=
R_{\text{transfer,test}}(I)
-
R_{\text{transfer,test}}(B)
\]

với giá trị âm là tốt hơn khi \(R\) là risk.

`R_int-suff` trả lời “có giữ được quan hệ hậu can thiệp trong miền được học/validation không”; `R_transfer` trả lời “năng lực đó có còn đúng trên shift chưa thấy không”.


## 5.6. Representation Scope and Lifecycle

Formal Spec v1.0 PHẢI phân biệt ba chế độ vòng đời của \(I_M\):

### A. `GLOBAL_SHARED_MECHANISM`

\[
I_M
=
\phi(D_{\text{train}})
\]

Sau khi huấn luyện và khóa candidate, cùng một \(I_M\) được dùng trên validation/test.

Không được dùng dữ liệu từ môi trường test để cập nhật \(I_M\).

Đây là chế độ mặc định cho các claim về **transfer của một cơ chế đã học**.

### B. `ENVIRONMENT_CONDITIONED`

\[
I_M^{(e)}
=
\phi(D_{\text{train}},C_e)
\]

trong đó \(C_e\) chỉ chứa thông tin môi trường được protocol cho phép biết trước.

Protocol PHẢI công bố chính xác:

- biến nào thuộc \(C_e\);
- biến nào bị cấm;
- \(C_e\) có xuất hiện ở train/validation/test hay không;
- \(C_e\) có chứa dữ liệu quan sát từ chính test environment hay không.

Nếu \(C_e\) chứa dữ liệu từ test environment, claim không còn là zero-shot transfer thuần túy và PHẢI được gắn nhãn phù hợp.

### C. `ONLINE_INFERRED`

\[
I_{M,t}^{(e)}
=
\phi(
D_{\text{train}},
H^{(e)}_{\le t}
)
\]

với \(H^{(e)}_{\le t}\) là lịch sử quan sát được phép dùng tại môi trường mới.

Đây là bài toán **adaptation / online inference**, không được gộp với zero-shot transfer.

### 5.6.1. Trường bắt buộc trong protocol

Mỗi benchmark PHẢI khai báo:

```text
representation_scope:
  GLOBAL_SHARED_MECHANISM
  | ENVIRONMENT_CONDITIONED
  | ONLINE_INFERRED

representation_update_after_train: true|false
allowed_post_train_inputs: [...]
forbidden_post_train_inputs: [...]
adaptation_budget: ...
adaptation_steps: ...
adaptation_data_source: ...
```

### 5.6.2. Claim boundary

Nếu `representation_update_after_train = true`, benchmark KHÔNG ĐƯỢC báo cáo kết quả như zero-shot transfer.

Phải phân biệt tối thiểu:

```text
ZERO_SHOT_TRANSFER
CONDITIONED_TRANSFER
TEST_TIME_ADAPTATION
ONLINE_ADAPTATION
```


---

# 6. Leakage Control and Benchmark Locking

## 6.1. Các cấp độ độc lập

Benchmark phải kiểm soát tối thiểu:

1. độc lập mẫu;
2. độc lập quỹ đạo;
3. độc lập seed;
4. độc lập tham số môi trường;
5. độc lập cấu hình cơ chế;
6. độc lập quy trình sinh benchmark.

## 6.2. Phân chia dữ liệu và đơn vị split

Formal Spec không bắt buộc `environment_id` phải luôn rời nhau trong mọi benchmark.

Mỗi protocol PHẢI khai báo **đơn vị split quyết định**:

```text
split_unit:
  ENVIRONMENT_ID
  | PARAMETER_REGION
  | TRAJECTORY
  | MECHANISM_CONFIG
  | STATE_REGION
  | SEED
  | COMPOSITE
```

Nếu dùng `COMPOSITE`, phải công bố tập thành phần.

Với đơn vị split đã chọn \(U\), phải có:

\[
U_{\text{train}}
\cap
U_{\text{validation}}
=
\varnothing
\]

\[
U_{\text{train}}
\cap
U_{\text{test}}
=
\varnothing
\]

\[
U_{\text{validation}}
\cap
U_{\text{test}}
=
\varnothing
\]

Ví dụ, cùng một environment generator có thể xuất hiện ở cả train và test nếu protocol khóa các miền tham số khác nhau và `split_unit = PARAMETER_REGION`.

Protocol PHẢI lưu cả:

```text
split_unit
split_definition
split_support_train
split_support_validation
split_support_test
split_manifest_hash
```

Không được gọi một test là held-out nếu đơn vị split quyết định thực tế đã xuất hiện trong train.

## 6.3. Test lock

Tập test:

- được sinh/khóa trước;
- không dùng để chọn kiến trúc;
- không dùng để chọn siêu tham số;
- không dùng để chọn checkpoint;
- không dùng để chọn metric;
- không dùng để sửa ontology;
- không dùng để thay đổi cost definition;
- phải có access log;
- mọi lần mở lại test để sửa benchmark phải tăng version.

## 6.4. Model selection boundary

**Mọi lựa chọn mô hình phải kết thúc trước test.**

Tập ứng viên được chọn bằng train + validation:

\[
\mathcal I_{\text{eligible}}
=
\left\{
I:
\begin{array}{l}
R_{\text{task,val}}\le\epsilon_u\\
R_{\text{int-suff,val}}\le\epsilon_c\\
R_{\text{noise,val}}\le\epsilon_n
\end{array}
\right\}
\]

Nếu transfer validation được phép theo thiết kế benchmark, phải dùng:

\[
R_{\text{transfer,val}}
\]

trên \(\mathcal E_{\text{validation}}\), không phải test.

Sau khi candidate/configuration được khóa:

\[
\boxed{
R_{\text{test}}
\text{ chỉ được dùng để báo cáo, không được dùng để chọn lại mô hình}
}
\]

---

# 7. Noise Model and Robustness Evaluation

## 7.1. Tách tập nhiễu và phân phối nhiễu

Tập nhiễu:

\[
\mathcal N_\delta
=
\{
\eta:
\|\eta\|\le\delta
\}
\]

Phân phối nhiễu:

\[
\eta\sim q_\eta
\]

với:

\[
\operatorname{supp}(q_\eta)
\subseteq
\mathcal N_\delta
\]

Phải công bố:

- loại nhiễu;
- norm;
- \(\delta\);
- phân phối;
- biến bị tác động;
- quan hệ với state;
- quan hệ với label;
- xác nhận rằng nhiễu không làm thay đổi cơ chế thật nếu được gọi là observation noise.

## 7.2. Rủi ro sạch

\[
R_{\text{clean}}
\]

## 7.3. Rủi ro có nhiễu

\[
R_{\text{noisy}}
=
\mathbb E_{\eta\sim q_\eta}
[
d(
\hat Y(X+\eta),
Y
)
]
\]

## 7.4. Suy giảm do nhiễu

\[
\Delta R_{\text{noise}}
=
R_{\text{noisy}}
-
R_{\text{clean}}
\]

Đây là metric chính khi mục tiêu là robustness degradation.

## 7.5. Worst-case noise risk

\[
R_{\text{noise}}^{\max}
=
\sup_{\eta\in\mathcal N_\delta}
d(
\hat Y(X+\eta),
Y
)
\]

## 7.6. Chẩn đoán representation

\[
R_{\text{repr-noise}}
=
d(
\phi(X+\eta),
\phi(X)
)
\]

Đây là metric chẩn đoán, không phải điều kiện bắt buộc.

## 7.7. Phân biệt với \(Z_e\)

Nếu \(Z_e\) ảnh hưởng thật đến \(Y\), không được buộc representation loại bỏ \(Z_e\). Biến đó phải được mô hình hóa như environmental condition.

---

# 8. Representation Equivalence

## 8.1. Nguyên tắc

OIR-PPV không yêu cầu một latent representation duy nhất.

Hai biểu diễn có thể khác nhau về tọa độ nhưng tương đương về hành vi đối với benchmark.

## 8.2. Tương đương chức năng và bất khả phân biệt thực nghiệm

Cho tập truy vấn khóa trước:

\[
\mathcal Q
=
\mathcal Q(
\mathcal T,
\mathcal A,
\mathcal E
)
\]

**Tương đương chức năng lý thuyết**:

\[
I_1
\sim_{\mathcal Q}
I_2
\]

khi hai biểu diễn tạo cùng phân phối/trả lời cho mọi truy vấn trong \(\mathcal Q\) theo semantics của benchmark. Quan hệ này được dùng khi nói về lớp tương đương:

\[
[I_M]_{\sim}
=
\{
I':
I'\sim_{\mathcal Q} I_M
\}
\]

Trong thực nghiệm, do sai số số học và lấy mẫu, dùng một quan hệ khác:

\[
I_1
\approx_{\mathcal Q,\epsilon}
I_2
\]

nếu:

\[
\forall q\in\mathcal Q:
\quad
d(
\hat p_{I_1}(q),
\hat p_{I_2}(q)
)
\le
\epsilon_{\sim}
\]

với \(\epsilon_{\sim}\) khóa trước.

\(\approx_{\mathcal Q,\epsilon}\) chỉ là **bất khả phân biệt trong sai số cho phép**, không mặc nhiên được coi là quan hệ tương đương toán học vì tính bắc cầu có thể không giữ.

## 8.3. Decoder/Probe Contract

Tương đương của \(I_M\) chỉ có nghĩa khi protocol khóa cách đọc representation.

Formal Spec phân biệt hai loại claim:

### A. Representation-level equivalence

Dùng một probe/decoder chuẩn \(P^*\), cùng kiến trúc và cùng ngân sách:

\[
I_1
\sim_{\mathcal Q}^{P^*}
I_2
\]

nếu:

\[
\forall q\in\mathcal Q:
\quad
P^*(I_1,q)
=
P^*(I_2,q)
\]

theo semantics lý thuyết của benchmark.

Trong thực nghiệm:

\[
I_1
\approx_{\mathcal Q,\epsilon}^{P^*}
I_2
\]

nếu chênh lệch đầu ra dưới probe chuẩn không vượt \(\epsilon_{\sim}\).

Probe contract PHẢI khóa:

```text
probe_id
probe_architecture
probe_parameter_budget
probe_training_data
probe_training_steps
probe_optimizer
probe_selection_rule
probe_random_seeds
```

### B. System-level functional equivalence

Nếu mỗi representation dùng predictor riêng:

\[
(I_1,P_1)
\sim_{\mathcal Q}
(I_2,P_2)
\]

thì claim chỉ được gọi là **system-level functional equivalence**, không phải representation equivalence.

Protocol PHẢI báo cáo loại claim:

```text
equivalence_scope:
  REPRESENTATION_WITH_SHARED_PROBE
  | SYSTEM_FUNCTIONAL
```

## 8.4. Hệ quả

Không dùng khoảng cách tới một ground-truth latent vector như tiêu chí mặc định để tuyên bố representation đúng.

Interpretability và correctness là hai tiêu chí khác nhau.

Một predictor riêng có năng lực lớn không được phép che giấu representation yếu rồi vẫn được diễn giải là representation-level equivalence.

---

# 9. Cost, Uncertainty, Eligibility, and Pareto Reporting

## 9.1. Phạm vi chi phí

Phải tách tối thiểu hai mức.

### Representation cost

\[
\mathbf C_{\text{repr}}
=
(
C_{I,\text{dim}},
C_{I,\text{memory}},
C_{I,\text{serialize}}
)
\]

### System cost

Đối với prediction:

\[
\mathbf C_{\text{system}}
=
\mathbf C_\phi
+
\mathbf C_I
+
\mathbf C_P
\]

Đối với generation:

\[
\mathbf C_{\text{system+gen}}
=
\mathbf C_\phi
+
\mathbf C_I
+
\mathbf C_P
+
\mathbf C_G
\]

Các thành phần chung giữa mọi condition có thể bị loại khỏi so sánh chỉ khi được tuyên bố trước.

## 9.2. Vector chi phí tổng quát

\[
\mathbf C
=
(
C_{\text{dim}},
C_{\text{param}},
C_{\text{memory}},
C_{\text{compute}},
C_{\text{data}},
C_{\text{train}}
)
\]

Không được cộng các đại lượng khác đơn vị thành một scalar nếu không có quy tắc trọng số được khóa trước.


## 9.2.1. Schema chi phí theo từng thành phần

Phép cộng:

\[
\mathbf C_{\text{system}}
=
\sum_X
\mathbf C_X
\]

chỉ được thực hiện **theo từng thành phần cùng đơn vị**.

Mỗi thành phần \(X\in\{\phi,I,P,G\}\) PHẢI khai báo vector theo cùng schema:

\[
\mathbf C_X
=
(
C^{(X)}_{\text{dim}},
C^{(X)}_{\text{param}},
C^{(X)}_{\text{memory-bytes}},
C^{(X)}_{\text{compute}},
C^{(X)}_{\text{latency}},
C^{(X)}_{\text{data}},
C^{(X)}_{\text{train}}
)
\]

Trong đó metric không áp dụng phải là `NA`, không được ngầm coi là 0.

Ví dụ:

```text
cost_schema:
  dim: integer | NA
  params: integer | NA
  memory_bytes: integer | NA
  compute_unit: FLOPs | MACs | measured_time | NA
  latency_ms: float | NA
  data_examples: integer | NA
  training_compute: ...
```

Không được cộng chéo đơn vị như:

```text
bytes + parameters + milliseconds
```

thành một scalar nếu không có hàm scalarization và trọng số được khóa trước.

## 9.3. Eligibility trước test

Candidate phải được chọn trước test bằng validation.

\[
\mathcal I_{\text{eligible}}
\]

không được phụ thuộc vào test result.

## 9.4. Test report frontier

Sau khi candidate được khóa, có thể báo cáo mặt Pareto trên test:

\[
\mathcal F_{\text{report}}
=
\operatorname{ParetoFront}
\left(
\mathcal I_{\text{eligible}};
\mathbf C,
R_{\text{task,test}},
R_{\text{int-suff,test}},
R_{\text{transfer,test}},
R_{\text{noise,test}}
\right)
\]

**Mặt Pareto này chỉ để báo cáo.**

Không được dùng:

\[
\mathcal F_{\text{report}}
\]

để quay lại chọn architecture/configuration và vẫn dùng cùng test set như test cuối.

## 9.5. Bất định thống kê

Mỗi estimand phải báo cáo:

\[
\widehat R_j
\pm
CI_j
\]

và ghi rõ cách tính CI:

- bootstrap;
- across environments;
- across seeds;
- paired comparison;
- hoặc phương pháp khác đã khóa.

Một mô hình không được tuyên bố dominance nếu chênh lệch nằm trong bất định theo rule đã freeze.


## 9.6. Uncertainty-Aware Pareto Dominance

Mỗi protocol PHẢI khóa:

```text
pareto_uncertainty_rule
dominance_alpha
multiple_comparison_rule
practical_equivalence_margin
```

Với hai candidate \(A,B\), chỉ được tuyên bố:

\[
A
\succ_{\text{stat}}
B
\]

nếu:

1. \(A\) không kém \(B\) trên mọi objective theo orientation đã khóa;
2. \(A\) tốt hơn \(B\) trên ít nhất một objective;
3. chênh lệch vượt quy tắc bất định thống kê và, nếu dùng, ngưỡng ý nghĩa thực tế đã khóa.

Một dạng pairwise effect có thể là:

\[
\Delta_j(A,B)
=
R_j(A)-R_j(B)
\]

với lower-is-better.

Nếu CI của \(\Delta_j\) cắt qua vùng tương đương thực tế đã khóa, objective đó được coi là `STATISTICALLY_UNRESOLVED` cho dominance.

Formal Spec không bắt buộc một phương pháp CI duy nhất, nhưng protocol PHẢI khóa phương pháp trước test.

Kết quả Pareto PHẢI phân biệt:

```text
DOMINATES
DOMINATED
NON_DOMINATED
STATISTICALLY_UNRESOLVED
```

---

# 10. Ground-Truth Modes and Evidence Levels

## 10.1. Chế độ A — Known mechanism

Khi simulator/SCM có ground truth:

\[
p_{M_e}
(
Y
\mid
do(A=a),
S,Z
)
\]

có thể tính trực tiếp.

Các metric như \(R_{\text{int-suff}}\) và mechanism fidelity có thể được đánh giá trực tiếp.

## 10.2. Chế độ B — Unknown mechanism

Với dữ liệu thực, không giả định biết \(M_e\).

Mỗi metric phải khai báo:

```text
requires_ground_truth_mechanism: true|false
real_data_applicable: true|false
proxy_metric_if_no_ground_truth: ...
```


## 10.2.1. Causal Identification Contract

Khi protocol dùng metric hoặc claim có ý nghĩa hậu can thiệp nhưng không biết đầy đủ \(M_e\), protocol PHẢI khai báo:

```text
identification_basis:
  RANDOMIZED_INTERVENTION
  | CONTROLLED_EXPERIMENT
  | BACKDOOR_ADJUSTMENT
  | FRONTDOOR_ADJUSTMENT
  | INSTRUMENTAL_VARIABLE
  | NATURAL_EXPERIMENT
  | OTHER_DECLARED_METHOD
  | NOT_IDENTIFIED

adjustment_set: [...]
randomization_status: ...
positivity_support: ...
consistency_assumption: ...
interference_assumption: ...
unmeasured_confounding_assumption: ...
identification_reference_or_derivation: ...
```

Nếu `identification_basis = NOT_IDENTIFIED`, protocol:

- KHÔNG ĐƯỢC gọi estimand đó là ground-truth interventional risk;
- KHÔNG ĐƯỢC nâng evidence level lên E3 chỉ từ observational association;
- chỉ được báo cáo proxy hoặc predictive/mechanism-consistency evidence phù hợp.

Nếu dùng adjustment method, protocol PHẢI ghi rõ điều kiện nhận dạng mà phương pháp cần.

### 10.2.2. Positivity / support

Nếu:

\[
P(A=a\mid Z=z)=0
\]

trong vùng truy vấn cần đánh giá, interventional estimand không được coi là identified bằng phương pháp cần positivity trong vùng đó.

Protocol phải đánh dấu các vùng không được hỗ trợ thay vì ngoại suy im lặng.

### 10.2.3. Không đồng nhất hành động quan sát với can thiệp

Quan sát:

\[
A=a,\;Y=y
\]

không tự động cho nhãn:

\[
Y^{do(A=a)}
\]

trừ khi identification contract cho phép suy ra như vậy.

## 10.3. Thang bằng chứng

### E4 — Ground-truth mechanism evidence

Có SCM hoặc cơ chế thật được biết/kiểm soát đủ mạnh.

### E3 — Interventional evidence

Có can thiệp thực, nhưng SCM không hoàn toàn biết.

### E2 — Mechanism-consistency evidence

Dữ liệu phù hợp với một lớp cơ chế/giả thuyết nhưng chưa định danh ground truth.

### E1 — Predictive-transfer evidence

Chỉ chứng minh dự đoán ngoài miền.

Không suy diễn:

\[
E_1\Rightarrow E_4
\]

hoặc:

\[
E_2\Rightarrow E_4
\]

Các mức này mô tả loại claim được hỗ trợ, không phải thứ hạng chất lượng tuyệt đối.


## 10.4. Metric registry bắt buộc

Mỗi metric PHẢI có một record tối thiểu:

```text
metric_id
metric_version
estimand_id
orientation                  # lower-is-better | higher-is-better
requires_ground_truth_mechanism
requires_intervention
requires_counterfactual_pairing
real_data_applicable
proxy_metric_if_no_ground_truth
identification_basis_required
aggregation_rule
uncertainty_rule
acceptance_rule
```

Một proxy không được kế thừa claim level của metric ground-truth mà nó thay thế.

---

# 11. Generation Validity, Novelty, and Mechanism Fidelity

## 11.1. Mô hình sinh

\[
X_{\text{new}}
\sim
G(
I_M,
S,
Z,
A
)
\]

Phải khóa miền của \(S,Z,A\).

## 11.2. Quy ước metric

Để tránh `≤/≥` mơ hồ, v1.0 dùng **risk orientation** cho acceptance.

### Validity risk

\[
R_V
\le
\epsilon_V
\]

### Novelty risk

\[
R_N
\le
\epsilon_N
\]

Trong đó \(R_N\) phải được định nghĩa sao cho nhỏ hơn là tốt hơn; ví dụ penalty khi mẫu quá gần dữ liệu huấn luyện.

### Mechanism-fidelity risk

\[
R_F
\le
\epsilon_F
\]

Mọi \(\epsilon\) phải khóa trước.

## 11.3. Tính hợp lệ

Validity phải có operational definition, ví dụ:

- đúng miền giá trị;
- nhất quán nội tại;
- không vi phạm ràng buộc;
- simulator chấp nhận;
- phù hợp environmental constraints.

## 11.4. Tính mới

Novelty không được định nghĩa bằng “không trùng bit”.

Có thể dùng:

\[
d(
X_{\text{new}},
D_{\text{train}}
)
>
\tau_N
\]

hoặc một metric trong không gian state/configuration/trajectory/causal relation đã khóa.

Nếu dùng score cao-hơn-tốt hơn để báo cáo, phải đồng thời định nghĩa risk chuyển đổi nhất quán cho acceptance.

## 11.5. Trung thành cơ chế

Mẫu sinh phải chịu test can thiệp:

\[
X_{\text{new}}
\rightarrow
do(A=a)
\rightarrow
Y^{do(a)}
\]

và so với ground truth hoặc proxy phù hợp với evidence mode.

Mechanism fidelity không được suy ra chỉ từ hình thức bề mặt.

## 11.6. H6 acceptance

H6 chỉ được xem là đạt mạnh khi:

\[
R_V\le\epsilon_V
\]

\[
R_N\le\epsilon_N
\]

\[
R_F\le\epsilon_F
\]

đồng thời theo protocol đã khóa.

---

# 12. Hypothesis Dependencies and Versioning

## 12.1. Không dùng một scalar mơ hồ cho phụ thuộc H1–H6

Thay vì:

\[
D_{ij}=\text{một số không rõ nghĩa}
\]

sử dụng ma trận quan hệ có kiểu.

Mỗi cặp \(H_i,H_j\) có thể mang một hoặc nhiều nhãn:

```text
NONE
DATA_SHARED
TEST_SHARED
MODEL_SELECTION_DEPENDENCY
METRIC_DEPENDENCY
LOGICAL_DEPENDENCY
IMPLEMENTATION_DEPENDENCY
INTERPRETATION_DEPENDENCY
```

## 12.2. Yêu cầu khai báo

Với mỗi hypothesis phải ghi:

- có dùng artifact của hypothesis khác không;
- có dùng cùng dataset/test set không;
- có dùng kết quả khác để chọn model không;
- có phụ thuộc metric khác không;
- claim có thể diễn giải độc lập không.

## 12.3. Phiên bản hóa

### Không hồi tố

- không sửa dữ liệu cũ;
- không sửa raw result cũ;
- không thay metric rồi giữ version cũ;
- không thay protocol sau khi xem test.

### Được tái diễn giải

- có thể giải thích lại claim cũ theo ontology mới;
- phải đánh dấu rõ là reinterpretation;
- không được trình bày như kết quả mới.

### Phải tái đánh giá

Tạo protocol mới nếu:

- lỗi định nghĩa;
- leakage;
- estimand thay đổi;
- shift class thay đổi;
- primary metric thay đổi;
- model-selection rule thay đổi;
- test lock bị phá.

\[
Protocol_{1.0}
\neq
Protocol_{1.1}
\]

---

# 13. Schema dữ liệu tối thiểu

Mỗi benchmark/run phải lưu tối thiểu:

```text
benchmark_id
benchmark_version
ontology_version
formal_spec_version
protocol_version
protocol_hash
manifest_hash
split_manifest_hash

code_commit
dataset_version
environment_generator_version
scm_version

environment_id
shift_class_declared
shift_class_realized
shift_profile_realized
invariant_components_declared
split_unit
split_definition

mechanism_id
graph_id
mechanism_parameters
delta_parameters

state_distribution
intervention_distribution
noise_set_definition
noise_distribution

train_validation_test_split
random_seed

model_id
model_config_hash
training_config
selection_config

representation_id
representation_scope
representation_update_after_train
allowed_post_train_inputs
adaptation_budget
equivalence_scope
probe_id
generator_id

metric_registry
metric_definitions
estimands
ground_truth_requirement
evidence_level
identification_basis
identification_assumptions
adjustment_set

point_estimates
confidence_intervals
pareto_uncertainty_rule
dominance_status

artifact_hashes
test_access_log
test_access_count
protocol_freeze_timestamp
candidate_lock_timestamp
test_unlock_timestamp
```

Các artifact hash phải bao phủ tối thiểu:

- source config;
- protocol;
- environment config;
- result;
- provenance.

---

# 14. Formal-Spec Closure Gate

`FORMAL_SPEC_v1.0` được coi là đóng khi bản thân đặc tả:

1. nhất quán với `ontology_v1.0`;
2. tách rõ mechanism, representation, state, environment và intervention;
3. định nghĩa shift semantics và declared/realized shift;
4. định nghĩa observation/intervention/counterfactual estimands;
5. định nghĩa interventional sufficiency và transfer trên các miền khác nhau;
6. ngăn test leakage trong model selection;
7. tách noise set khỏi noise distribution;
8. phân biệt functional equivalence và empirical indistinguishability;
9. định nghĩa representation cost và whole-system cost;
10. quy định uncertainty và test-only Pareto reporting;
11. tách known-mechanism và unknown-mechanism evidence modes;
12. chuẩn hóa H6 acceptance orientation;
13. dùng typed dependency relations cho H1–H6;
14. có schema provenance/version/hash/test-access bắt buộc;
15. không còn ký hiệu placeholder hoặc mâu thuẫn quy phạm chặn triển khai độc lập;
16. khóa representation scope/lifecycle và test-time adaptation boundary;
17. khóa decoder/probe contract cho representation equivalence;
18. có causal-identification contract cho chế độ không có mechanism ground truth;
19. dùng split-unit contract thay vì giả định environment-ID luôn phải rời nhau;
20. định nghĩa component-wise cost schema;
21. định nghĩa uncertainty-aware Pareto dominance.

Closure review FIX_01 ngày 2026-09-09 xác nhận các điều kiện trên đã được thỏa sau khi xử lý toàn bộ 6 điểm reviewer yêu cầu.

\[
\boxed{
\texttt{FORMAL\_SPEC\_v1.0}
=
\texttt{FINAL}
}
\]

## 14.1. Benchmark Protocol Activation Gate

Việc Formal Spec là `FINAL` **không có nghĩa một benchmark cụ thể đã sẵn sàng chạy**.

Trước mỗi decisive benchmark, protocol riêng PHẢI khóa tối thiểu:

1. \(\operatorname{Inv}(\mathcal S_k)\);
2. shift class và realized-shift validator;
3. domain relation / selection mode / aggregation mode;
4. \(\mu,\rho,\pi\);
5. estimands áp dụng;
6. intervention regime;
7. leakage audit;
8. test set và test-access policy;
9. candidate-selection rule chỉ dùng train/validation;
10. noise set/distribution nếu áp dụng;
11. \(\mathcal Q\) và \(\epsilon_{\sim}\) nếu đánh giá representation equivalence;
12. cost scope;
13. uncertainty rule;
14. evidence-mode applicability của từng metric;
15. H6 metrics/thresholds nếu áp dụng;
16. H1–H6 dependency declarations;
17. schema/provenance/hash contract;
18. protocol freeze timestamp;
19. independent QA acceptance;
20. không còn P0/P1 blocker;
21. representation scope/lifecycle đã khóa;
22. probe/equivalence scope đã khóa nếu áp dụng;
23. causal identification contract đã khóa nếu dùng dữ liệu không có mechanism ground truth;
24. split unit đã khóa;
25. component-wise cost schema đã khóa;
26. pareto uncertainty rule đã khóa.

Các giá trị trên thuộc **benchmark protocol**, không phải điều kiện để Formal Spec tồn tại ở trạng thái FINAL.

---

# 15. Trạng thái hiện tại

\[
\boxed{
\texttt{FORMAL\_SPEC\_v1.0}
=
\texttt{FINAL}
}
\]

**Closure type:** `SPECIFICATION_CLOSED_AFTER_FIX_01 / BENCHMARK_PROTOCOLS_NOT_IMPLIED`

Mọi thay đổi semantic hoặc normative sau closure phải tăng phiên bản (`v1.1+`) hoặc đi qua amendment có truy nguyên.

---

# 16. Claim Boundary

Formal specification này không chứng minh rằng:

- \(I_M\) là cơ chế thật;
- mọi representation tốt đều identifiable;
- compression tự động dẫn đến transfer;
- transfer tự động dẫn đến causal understanding;
- interventional prediction trên một tập hữu hạn tương đương với học đúng toàn bộ causal mechanism;
- generation tương đương creativity;
- kết quả synthetic tự động chuyển sang dữ liệu thực.

Nó chỉ định nghĩa một framework để đo các claim này một cách có kiểm soát, tái lập và có version.

---

# 17. Tóm tắt sửa đổi và closure amendments

Các sửa đổi chính:

1. loại bỏ việc dùng test transfer để xác định candidate hợp lệ;
2. tách model selection trên validation khỏi test-only reporting;
3. tách domain relation, selection mode và aggregation mode;
4. khóa phạm vi chi phí representation và toàn hệ;
5. thêm representation equivalence \([I_M]_\sim\);
6. chuẩn hóa H6 sang risk orientation;
7. làm rõ conditioning trước can thiệp;
8. sửa interventional extrapolation cho action liên tục;
9. tách noise set khỏi noise distribution;
10. thêm \(\Delta R_{\text{noise}}\);
11. thay scalar dependency bằng typed dependency relation;
12. thêm ground-truth/evidence applicability cho metric;
13. mở rộng provenance/schema với commit, hash, version và test access;
14. giữ `FINAL` sau QA độc lập.


## 17.1. Closure amendments bổ sung

Closure review đã bổ sung thêm:

15. quy tắc PHẢI/NÊN/CÓ THỂ và tách Formal Spec khỏi benchmark instantiation;
16. shift profile đa nhãn thay vì giả định shift classes loại trừ nhau;
17. explicit \(R_{\text{task}}\), \(R_{\text{cf}}\), \(R_{\text{int-suff}}\) và \(R_{\text{transfer}}\);
18. transfer risk được định nghĩa trên held-out shift và tách khỏi in-domain interventional sufficiency;
19. functional equivalence được tách khỏi epsilon-indistinguishability để tránh lỗi bắc cầu;
20. metric registry bắt buộc và proxy claim-boundary;
21. Formal-Spec Closure Gate được tách khỏi Benchmark Protocol Activation Gate.


---

# 18. FIX_01 Reviewer Closure Amendments

Sáu điểm reviewer cuối cùng đã được xử lý:

1. **Representation lifecycle/scope**  
   Đã thêm `GLOBAL_SHARED_MECHANISM`, `ENVIRONMENT_CONDITIONED`, `ONLINE_INFERRED` và claim boundary zero-shot/adaptation.

2. **Representation equivalence vs predictor/decoder**  
   Đã tách representation-level equivalence dưới shared probe khỏi system-level functional equivalence.

3. **Causal identification khi không có mechanism ground truth**  
   Đã thêm `identification_basis`, adjustment assumptions, positivity và rule `NOT_IDENTIFIED`.

4. **Split unit**  
   Đã bỏ yêu cầu cứng environment-ID luôn rời nhau; thay bằng split unit phải được khai báo và rời nhau.

5. **Component-wise cost schema**  
   Đã khóa phép cộng theo từng đơn vị và cấm cộng chéo đơn vị không có scalarization freeze.

6. **Uncertainty-aware Pareto rule**  
   Đã thêm `DOMINATES / DOMINATED / NON_DOMINATED / STATISTICALLY_UNRESOLVED`.

## 18.1. Reviewer closure status

\[
\boxed{
\texttt{P0}=0,\quad
\texttt{P1}=0
}
\]

\[
\boxed{
\texttt{FORMAL\_SPEC\_v1.0}
=
\texttt{FINAL}
}
\]

Sau trạng thái này, thay đổi semantic hoặc normative phải đi qua amendment có truy nguyên hoặc tăng phiên bản `v1.1+`.
