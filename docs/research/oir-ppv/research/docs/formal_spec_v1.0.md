# OIR-PPV Formal Specification v1.0

**Trạng thái:** Draft  
**Phiên bản:** v1.0  
**Ngày:** 2026-09-09  
**Phụ thuộc:** `ontology_v1.0.md`  
**Điều kiện phát hành:** Chưa được tuyên bố final cho tới khi cả 10 mục được khóa.

---

## 0. Mục tiêu

Đặc tả này chuyển ontology OIR-PPV v1.0 thành các định nghĩa vận hành có thể triển khai, tái lập và kiểm định.

Mỗi mục phải xác định:

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

## 1.2. Định nghĩa

Mỗi benchmark phải công bố thành phần cơ chế nào được xem là chung và thành phần nào được phép thay đổi.

Tập bất biến:

\[
\operatorname{Inv}(\mathcal S_k)
\]

phải được định nghĩa trước khi sinh dữ liệu hoặc huấn luyện mô hình.

## 1.3. Đối tượng đo

- cấu trúc nhân quả;
- hàm hoặc cơ chế sinh;
- tham số chung;
- tham số thay đổi;
- điều kiện môi trường;
- điều kiện ban đầu.

## 1.4. Điều kiện khóa trước

Phải công bố:

1. \(\mathcal G_{\text{shared}}\);
2. \(F_{\text{shared}}\);
3. \(\Theta_{\text{shared}}\);
4. miền của \(\Delta_e\);
5. \(\operatorname{Inv}(\mathcal S_k)\);
6. tiêu chí xác định một môi trường có thuộc lớp hay không.

## 1.5. Trường hợp không áp dụng

Nếu test thay đổi một thành phần thuộc:

\[
\operatorname{Inv}(\mathcal S_k)
\]

thì kết quả không được gọi là transfer trong lớp \(\mathcal S_k\). Có thể gắn nhãn là stress test ngoài miền hoặc cơ chế mới.

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

Mỗi môi trường phải được gán lớp dịch chuyển trước khi đánh giá.

Lớp thực tế phải được suy ra từ các thành phần thật sự thay đổi, không được gán hậu nghiệm dựa trên kết quả.

## 2.3. Quy tắc bất nhất

Nếu:

\[
\operatorname{ShiftClass}_{\text{declared}}
\neq
\operatorname{ShiftClass}_{\text{realized}}
\]

thì môi trường:

- không được dùng để chứng minh claim ban đầu;
- phải được gắn nhãn lệch giao thức;
- hoặc phải tạo phiên bản benchmark mới.

## 2.4. Các chế độ tối thiểu

Benchmark có thể khai báo một hoặc nhiều chế độ:

- thay đổi bề mặt;
- thay đổi phân phối trạng thái;
- thay đổi tham số;
- thay đổi điều kiện môi trường;
- thay đổi thành phần cơ chế;
- thay đổi cấu trúc nhân quả.

Chế độ cuối cùng không được gọi là transfer trong cùng lớp nếu nó phá vỡ bất biến đã khai báo.

---

# 3. Environment, State, and Intervention Distributions

## 3.1. Phân phối đánh giá

Phải công bố:

\[
e\sim\mu_{\text{test}}
\]

\[
S\sim\rho_e
\]

\[
a\sim\pi_{\text{test}}
\]

Trong đó:

- \(\mu_{\text{test}}\): phân phối hoặc tập chọn môi trường;
- \(\rho_e\): phân phối trạng thái trong môi trường \(e\);
- \(\pi_{\text{test}}\): phân phối hành động hoặc can thiệp.

## 3.2. Loại phân phối môi trường

Phải chỉ rõ:

\[
\mu_{\text{test}}
\in
\{
\text{known-distribution},
\text{held-out finite set},
\text{interpolation},
\text{extrapolation},
\text{adversarial},
\text{worst-case}
\}
\]

## 3.3. Estimand

Sai số trung bình:

\[
\theta_{\text{mean}}
=
\mathbb E_{
e\sim\mu_{\text{test}},
S\sim\rho_e,
a\sim\pi_{\text{test}}
}
[
d(\hat p_\psi,p_{M_e})
]
\]

Sai số theo môi trường:

\[
R_e
=
\mathbb E_{
S\sim\rho_e,
a\sim\pi_{\text{test}}
}
[
d(\hat p_\psi,p_{M_e})
]
\]

Sai số tệ nhất:

\[
\theta_{\text{worst}}
=
\max_{e\in\mathcal E_{\text{test}}}R_e
\]

## 3.4. Báo cáo bắt buộc

Phải báo cáo tối thiểu:

- giá trị trung bình;
- độ lệch chuẩn hoặc khoảng tin cậy;
- sai số theo môi trường;
- sai số tệ nhất;
- số lượng môi trường;
- số lượng trạng thái;
- số lượng can thiệp.

---

# 4. Observation, Intervention, and Counterfactual Estimands

## 4.1. Quan sát

\[
p(Y\mid X)
\]

## 4.2. Hậu can thiệp

\[
p(Y\mid do(A=a),S,Z)
\]

Mô hình dự đoán:

\[
\hat p_\psi
(
y\mid I_M,S_t,Z_e,a
)
\]

Mục tiêu tham chiếu:

\[
p_{M_e}
(
Y\mid do(A=a),S_t,Z_e
)
\]

## 4.3. Phản thực

\[
Y_{a'}\mid A=a
\]

Nếu benchmark đánh giá phản thực, phải công bố:

- biến hành động đã xảy ra;
- hành động thay thế;
- biến ngoại sinh;
- điều kiện ghép cặp giữa hai thế giới;
- quy tắc xác định ground truth.

## 4.4. Quy tắc ký hiệu

Không dùng \(do(a)\) như một đầu vào thông thường của predictor.

- dùng \(do(A=a)\) để chỉ toán tử can thiệp trong SCM;
- dùng \(a\) trong danh sách đầu vào của mô hình học;
- công bố rõ khi hai biểu thức được dùng để xấp xỉ nhau.

---

# 5. Interventional Sufficiency of \(I_M\)

## 5.1. Định nghĩa

Một biểu diễn \(I_M\) đủ nhân quả tương đối với:

\[
(
\mathcal T,
\mathcal A,
\mathcal E
)
\]

nếu nó cho phép tái tạo đủ chính xác các phân phối hậu can thiệp trong phạm vi đó.

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

## 5.3. Tập can thiệp

Có thể dùng ba chế độ:

### Interventional interpolation

\[
\mathcal A_{\text{test}}
\cap
\mathcal A_{\text{train}}
\neq
\varnothing
\]

### Interventional extrapolation

\[
\mathcal A_{\text{test}}
\cap
\mathcal A_{\text{train}}
=
\varnothing
\]

### Compositional intervention

Các hành động thành phần đã thấy nhưng tổ hợp hành động mới.

Chế độ được dùng phải được khai báo trước.

## 5.4. Trường hợp không áp dụng

Không được gọi là “đủ nhân quả” nếu chỉ đánh giá dự đoán quan sát mà không có truy vấn can thiệp hoặc phản thực tương ứng.

---

# 6. Leakage Control and Benchmark Locking

## 6.1. Các cấp độ độc lập

Benchmark phải kiểm soát tối thiểu:

1. độc lập mẫu;
2. độc lập quỹ đạo;
3. độc lập hạt giống;
4. độc lập tham số môi trường;
5. độc lập cấu hình cơ chế;
6. độc lập quy trình sinh benchmark.

## 6.2. Phân chia dữ liệu

\[
\mathcal E_{\text{train}}
\cap
\mathcal E_{\text{validation}}
=
\varnothing
\]

\[
\mathcal E_{\text{train}}
\cap
\mathcal E_{\text{test}}
=
\varnothing
\]

\[
\mathcal E_{\text{validation}}
\cap
\mathcal E_{\text{test}}
=
\varnothing
\]

Các điều kiện trên chỉ có ý nghĩa khi môi trường, quỹ đạo, seed và tham số cũng được kiểm soát.

## 6.3. Test lock

Tập kiểm tra phải:

- được sinh hoặc khóa trước;
- không dùng để chọn kiến trúc;
- không dùng để chọn siêu tham số;
- không dùng để chọn checkpoint;
- không dùng để sửa ontology;
- không dùng để thay đổi metric;
- được ghi lại số lần truy cập.

Mỗi lần mở lại hoặc sửa test phải tăng phiên bản benchmark.

---

# 7. Noise Model and Robustness Evaluation

## 7.1. Tập nhiễu

\[
\mathcal N
=
\{
\eta:
\|\eta\|\le\delta,
\eta\sim q_\eta
\}
\]

Phải công bố:

- loại nhiễu;
- cường độ;
- miền tác động;
- phân phối;
- mối quan hệ với trạng thái;
- mối quan hệ với nhãn hoặc cơ chế.

## 7.2. Sai số trung bình

\[
\mathcal R_{\text{noise}}
=
\mathbb E_{\eta\sim q_\eta}
[
d(
\hat Y(X+\eta),
Y
)
]
\]

## 7.3. Sai số tệ nhất

\[
\mathcal R_{\text{noise}}^{\max}
=
\sup_{\eta\in\mathcal N}
d(
\hat Y(X+\eta),
Y
)
\]

## 7.4. Chỉ số representation

\[
\mathcal R_{\text{repr-noise}}
=
d(
\phi(X+\eta),
\phi(X)
)
\]

Đây là chỉ số chẩn đoán, không phải tiêu chí bắt buộc nếu việc giữ nguyên representation làm giảm năng lực dự đoán.

## 7.5. Phân biệt với biến môi trường

Nếu \(Z\) có ảnh hưởng thật đến \(Y\), mô hình không được yêu cầu loại bỏ \(Z\). \(Z\) phải được mô hình hóa hoặc cung cấp như điều kiện dự đoán.

---

# 8. Cost, Uncertainty, and Pareto Comparison

## 8.1. Tập ứng viên hợp lệ

\[
\mathcal I_{\text{valid}}
=
\left\{
I:
\begin{array}{l}
R_{\text{task}}\le\epsilon_u\\
R_{\text{int-suff}}\le\epsilon_c\\
R_{\text{transfer}}\le\epsilon_t\\
R_{\text{noise}}\le\epsilon_n
\end{array}
\right\}
\]

Các ngưỡng phải được khóa trước.

## 8.2. Vector chi phí

\[
\mathbf C=
(
C_{\text{dim}},
C_{\text{param}},
C_{\text{compute}},
C_{\text{data}},
C_{\text{memory}}
)
\]

Phải công bố thành phần chi phí nào được sử dụng trong so sánh.

## 8.3. Mặt Pareto

\[
\mathcal F_I
=
\operatorname{ParetoFront}
\left(
\mathcal I_{\text{valid}};
\mathbf C,
R_{\text{task}},
R_{\text{int-suff}},
R_{\text{transfer}},
R_{\text{noise}}
\right)
\]

Không tuyên bố một mô hình là tốt nhất tuyệt đối nếu nó chỉ tốt hơn trên một tiêu chí.

## 8.4. Bất định thống kê

Mỗi tiêu chí phải báo cáo:

\[
\widehat R_j
\pm
CI_j
\]

Có thể dùng:

- khoảng tin cậy bootstrap;
- khoảng tin cậy theo môi trường;
- khoảng tin cậy theo seed;
- kiểm định chênh lệch ghép cặp.

Một chênh lệch nhỏ hơn bất định thống kê không được diễn giải là ưu thế chắc chắn.

---

# 9. Generation Validity, Novelty, and Mechanism Fidelity

## 9.1. Mô hình sinh

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

Phải công bố miền của \(S,Z,A\).

## 9.2. Tính hợp lệ

\[
V_{\text{valid}}
\]

có thể bao gồm:

- tuân thủ miền giá trị;
- nhất quán nội tại;
- không vi phạm ràng buộc;
- được simulator hoặc bộ kiểm tra chấp nhận;
- hợp lệ theo điều kiện môi trường.

## 9.3. Tính mới

\[
N_{\text{novel}}
\]

phải được định nghĩa trong một không gian cụ thể, chẳng hạn:

\[
d(
X_{\text{new}},
D_{\text{train}}
)
>
\tau
\]

Không xem “không trùng từng bit” là điều kiện đủ cho tính mới.

## 9.4. Trung thành cơ chế

Mẫu sinh phải được kiểm tra dưới can thiệp:

\[
X_{\text{new}}
\rightarrow
do(a)
\rightarrow
Y^{do(a)}
\]

và so sánh với:

\[
Y_{M_e}^{do(a)}
\]

Một mẫu sinh không được coi là trung thành cơ chế chỉ dựa trên hình thức bề mặt.

## 9.5. Tiêu chí H6

H6 chỉ được xem là đạt mạnh khi cả ba thành phần đạt yêu cầu:

\[
V_{\text{valid}}\le/\ge\tau_V
\]

\[
N_{\text{novel}}\ge\tau_N
\]

\[
F_{\text{mechanism}}\ge\tau_F
\]

Chiều của bất đẳng thức tùy định nghĩa metric.

---

# 10. Hypothesis Dependencies, Evidence Levels, and Versioning

## 10.1. Phụ thuộc H1–H6

Các giả thuyết được xem là tương đối độc lập về mặt claim, nhưng có thể phụ thuộc về mặt cơ chế.

Ma trận:

\[
D_{ij}
=
\text{mức phụ thuộc giữa }H_i,H_j
\]

phải ghi rõ:

- H_i có sử dụng kết quả của H_j không;
- H_i có sử dụng cùng test set không;
- H_i có dùng H_j để chọn mô hình không;
- H_i có thể diễn giải độc lập không.

## 10.2. Thang bằng chứng

\[
E_4:
\text{ground-truth cơ chế}
\]

\[
E_3:
\text{bằng chứng can thiệp}
\]

\[
E_2:
\text{bằng chứng nhất quán cơ chế}
\]

\[
E_1:
\text{bằng chứng chuyển giao dự đoán}
\]

Không suy diễn:

\[
E_1\Rightarrow E_4
\]

hoặc:

\[
E_2\Rightarrow E_4
\]

Các mức này mô tả loại claim có thể hỗ trợ, không phải thứ bậc chất lượng tuyệt đối.

## 10.3. Phiên bản hóa

Không hồi tố:

- không sửa dữ liệu cũ;
- không sửa kết quả cũ;
- không đổi metric nhưng giữ nguyên tên phiên bản;
- không đổi giao thức sau khi xem test.

Được tái diễn giải:

- có thể giải thích claim cũ theo ontology mới;
- phải ghi rõ đây là diễn giải lại;
- không được trình bày như kết quả mới.

Phải tái đánh giá:

- nếu phát hiện lỗi định nghĩa;
- nếu phát hiện leakage;
- nếu thay đổi estimand;
- nếu thay đổi lớp chuyển giao;
- nếu thay đổi metric chính;
- nếu thay đổi quy tắc chọn mô hình.

Khi đó:

\[
\texttt{Protocol\_1.0}
\neq
\texttt{Protocol\_1.1}
\]

Mọi kết quả phải gắn với phiên bản giao thức tương ứng.

---

# 11. Schema dữ liệu tối thiểu

Mỗi benchmark phải lưu:

```text
benchmark_id
ontology_version
protocol_version
environment_id
shift_class_declared
shift_class_realized
mechanism_id
graph_id
mechanism_parameters
delta_parameters
state_distribution
intervention_distribution
noise_distribution
train_validation_test_split
random_seed
model_id
representation_id
generator_id
metric_definitions
estimands
point_estimates
confidence_intervals
test_access_log
```

---

# 12. Điều kiện chuyển từ DRAFT sang FINAL

`FORMAL_SPEC_v1.0` chỉ được chuyển sang trạng thái final khi:

- 10 mục đã có định nghĩa vận hành;
- mọi estimand đã được khóa;
- mọi metric chính đã được khóa;
- \(\operatorname{Inv}(\mathcal S_k)\) đã được công bố;
- phân phối môi trường, trạng thái và can thiệp đã được công bố;
- test set đã được khóa;
- leakage audit đã hoàn tất;
- quy tắc bất định thống kê đã được xác định;
- H1–H6 đã có ma trận phụ thuộc;
- schema dữ liệu đã được triển khai;
- phiên bản benchmark đã được ghi nhận.

---

## 13. Trạng thái hiện tại

\[
\boxed{
\texttt{FORMAL\_SPEC\_v1.0}
=
\texttt{DRAFTING\_AUTHORIZED}
}
\]

Chưa được tuyên bố:

\[
\texttt{FINAL}
\]

cho tới khi hoàn tất toàn bộ điều kiện tại Mục 12.
