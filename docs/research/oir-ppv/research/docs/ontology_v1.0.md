# OIR-PPV Ontology v1.0

**Trạng thái:** Frozen at principle level  
**Phiên bản:** v1.0  
**Ngày:** 2026-09-09  
**Phạm vi:** Ontology và semantics cấp nguyên tắc của OIR-PPV

---

## 1. Phạm vi

OIR-PPV nghiên cứu việc học một biểu diễn của phần cơ chế chung giữa các môi trường, sau đó đánh giá biểu diễn đó theo các nhiệm vụ dự đoán, truy vấn can thiệp, lớp dịch chuyển môi trường và yêu cầu sinh tạo đã xác định trước.

Ontology này phân biệt:

\[
M_{\text{shared}}
\neq
I_M
\neq
S_t
\neq
Z_e
\neq
A
\]

Trong đó:

- \(M_{\text{shared}}\): cơ chế chung được giả định giữ bất biến trong một lớp chuyển giao;
- \(I_M\): biểu diễn cơ chế do hệ thống học được;
- \(S_t\): trạng thái cụ thể tại thời điểm \(t\);
- \(Z_e\): điều kiện môi trường có ý nghĩa đối với quá trình sinh;
- \(A\): hành động hoặc can thiệp.

---

## 2. Phân rã cơ chế chung

Cơ chế chung được biểu diễn:

\[
M_{\text{shared}}
=
(
\mathcal G_{\text{shared}},
F_{\text{shared}},
\Theta_{\text{shared}}
)
\]

Trong đó:

- \(\mathcal G_{\text{shared}}\): cấu trúc phụ thuộc hoặc cấu trúc nhân quả;
- \(F_{\text{shared}}\): họ hàm hoặc cơ chế sinh;
- \(\Theta_{\text{shared}}\): các tham số được yêu cầu giữ cố định;
- \(\Delta_e\): các thành phần được phép thay đổi theo môi trường.

Môi trường \(e\) được mô tả tổng quát:

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

Không mặc định rằng mọi môi trường được tạo bằng cách ghép cơ học hai khối \(M_{\text{shared}}\) và \(\Delta_e\). \(\Delta_e\) có thể bao gồm tham số, điều kiện biên, phân phối trạng thái, phân phối môi trường hoặc cơ chế phụ được phép thay đổi.

---

## 3. Biểu diễn cơ chế

Quá trình học tạo ra:

\[
I_M
=
\phi(
D_{\text{train}};
\mathcal T,
\mathcal A
)
\]

Trong đó:

- \(D_{\text{train}}\): dữ liệu huấn luyện;
- \(\mathcal T\): tập nhiệm vụ;
- \(\mathcal A\): tập hành động hoặc truy vấn can thiệp.

\(I_M\) không đồng nhất với:

- cơ chế thật \(M_{\text{shared}}\);
- trạng thái hiện tại \(S_t\);
- điều kiện môi trường \(Z_e\);
- toàn bộ thế giới hoặc toàn bộ mô hình nhân quả.

Một biểu diễn chỉ cần đủ đối với tập nhiệm vụ, tập truy vấn và lớp chuyển giao được xác định trước.

---

## 4. Lớp tương đương biểu diễn

OIR-PPV không yêu cầu một mã hóa latent duy nhất.

Lớp tương đương của một biểu diễn được viết:

\[
[I_M]_{\sim}
=
\{
h(I_M):
h\in\mathcal H_{\text{admissible}}
\}
\]

Hai biểu diễn được xem là tương đương nếu chúng tạo ra cùng kết quả trên:

\[
(
\mathcal T,
\mathcal A,
\operatorname{ShiftClass}
)
\]

hoặc trên các truy vấn được chỉ định trong đặc tả.

Sự tương đương về chức năng không đồng nghĩa với sự giống nhau về tọa độ latent hoặc khả năng diễn giải trực tiếp.

---

## 5. Lớp chuyển giao

Mỗi phép thử phải thuộc một lớp chuyển giao được xác định trước:

\[
\operatorname{ShiftClass}
=
\mathcal S_k
\]

Mỗi lớp phải công bố tập thành phần bất biến:

\[
\operatorname{Inv}(\mathcal S_k)
\]

Ví dụ:

\[
\operatorname{Inv}(\mathcal S_2)
=
\{
\mathcal G_{\text{shared}},
F_{\text{shared}}
\}
\]

Trong trường hợp này, có thể cho phép thay đổi:

\[
\Theta_e,\quad
P(S_0),\quad
P(Z_e)
\]

Các môi trường kiểm tra phải giữ các thành phần thuộc \(\operatorname{Inv}(\mathcal S_k)\).

---

## 6. Lớp chuyển giao khai báo và thực tế

Mỗi môi trường phải có hai nhãn:

\[
\operatorname{ShiftClass}_{\text{declared}}
\]

và:

\[
\operatorname{ShiftClass}_{\text{realized}}
\]

Ánh xạ bắt buộc:

\[
\Delta_e
\rightarrow
\operatorname{ShiftClass}
\rightarrow
\operatorname{Inv}
\]

Nếu lớp thực tế không khớp lớp đã khai báo, môi trường đó bị xem là lệch giao thức và không được dùng để chứng minh claim ban đầu nếu chưa được gắn nhãn lại hoặc tạo phiên bản benchmark mới.

---

## 7. Ba loại bài toán dự đoán

### 7.1. Dự đoán quan sát

\[
p(Y\mid X)
\]

Đây là bài toán dự đoán từ dữ liệu quan sát.

### 7.2. Dự đoán hậu can thiệp

\[
p(Y\mid do(A=a),S,Z)
\]

Đây là bài toán dự đoán kết quả khi áp dụng can thiệp \(do(A=a)\).

Mô hình học có thể được viết:

\[
\hat p_\psi
(
y\mid I_M,S_t,Z_e,a
)
\]

và được so sánh với:

\[
p_{M_e}
(
Y\mid do(A=a),S_t,Z_e
)
\]

### 7.3. Dự đoán phản thực

\[
Y_{a'}\mid A=a
\]

Phản thực yêu cầu phân biệt hành động đã xảy ra với hành động thay thế và cần điều kiện xác định rõ biến ngoại sinh hoặc cấu trúc SCM.

Ba loại bài toán này không được gộp chung dưới một nhãn “nhân quả”.

---

## 8. Đủ nhân quả tương đối

Khái niệm “đủ nhân quả” luôn có tính tương đối.

Một biểu diễn \(I_M\) được gọi là đủ nhân quả tương đối với:

\[
(
\mathcal T,
\mathcal A,
\mathcal E
)
\]

nếu nó cho phép tái tạo đủ chính xác các phân phối hậu can thiệp trong phạm vi nhiệm vụ, truy vấn và môi trường đã chỉ định.

Tên vận hành được sử dụng trong đặc tả:

\[
\mathcal R_{\text{int-suff}}
\]

Không diễn giải \(\mathcal R_{\text{int-suff}}\) như bằng chứng rằng \(I_M\) đã khôi phục toàn bộ mô hình nhân quả thật.

---

## 9. Robustness và nhiễu quan sát

Nhiễu quan sát được ký hiệu là \(\eta\), không làm thay đổi thế giới hoặc cơ chế thật:

\[
X'=X+\eta
\]

Tập nhiễu phải được định nghĩa:

\[
\mathcal N
=
\{
\eta:
\|\eta\|\le\delta,\;
\eta\sim q_\eta
\}
\]

Mục tiêu chính là bảo toàn năng lực dự đoán hoặc năng lực can thiệp:

\[
\mathcal R_{\text{noise}}
\approx 0
\]

hoặc:

\[
\mathcal R_{\text{task}}(X+\eta)
-
\mathcal R_{\text{task}}(X)
\approx 0
\]

Điều kiện:

\[
\phi(X+\eta)\approx\phi(X)
\]

chỉ là chỉ số chẩn đoán của representation, không phải yêu cầu bắt buộc trong mọi bài toán.

---

## 10. Sinh tạo

Sinh tạo là phần mở rộng độc lập của lõi học representation.

Lõi:

\[
D_{\text{train}}
\rightarrow
I_M
\]

Phần sinh:

\[
(
I_M,
G,
S,
Z,
A
)
\rightarrow
X_{\text{new}}
\]

Chất lượng sinh được đánh giá bằng:

\[
\mathbf S_G
=
(
V_{\text{valid}},
N_{\text{novel}},
F_{\text{mechanism}}
)
\]

Trong đó:

- \(V_{\text{valid}}\): tính hợp lệ;
- \(N_{\text{novel}}\): tính mới;
- \(F_{\text{mechanism}}\): độ trung thành với cơ chế.

Mẫu sinh phải được kiểm tra bằng can thiệp:

\[
X_{\text{new}}
\rightarrow
do(a)
\rightarrow
Y^{do(a)}
\]

Một mẫu sinh chỉ là bằng chứng mạnh cho năng lực sinh cơ chế nếu vừa hợp lệ, vừa mới, vừa giữ đúng các hệ quả can thiệp.

---

## 11. H1–H6

H1–H6 là các trục đánh giá tương đối độc lập về mặt phát biểu, nhưng có thể phụ thuộc và tương tác về mặt cơ chế.

Không giả định:

\[
H1\rightarrow H2\rightarrow H3\rightarrow\cdots
\]

và cũng không gọi chúng là hoàn toàn trực giao.

Có thể mô tả quan hệ giữa các giả thuyết bằng:

\[
D_{ij}
=
\text{mức phụ thuộc giữa }H_i,H_j
\]

với các mức như:

\[
D_{ij}
\in
\{0,\text{yếu},\text{vừa},\text{mạnh}\}
\]

---

## 12. Thang bằng chứng

Các loại bằng chứng được phân biệt:

\[
E_4:
\text{cơ chế thật hoặc ground truth được biết}
\]

\[
E_3:
\text{bằng chứng can thiệp}
\]

\[
E_2:
\text{bằng chứng nhất quán với cơ chế}
\]

\[
E_1:
\text{bằng chứng chuyển giao dự đoán}
\]

Các mức này mô tả khả năng xác minh claim, không phải thứ bậc chất lượng tuyệt đối của toàn bộ nghiên cứu.

Không được suy:

\[
E_1\Rightarrow E_4
\]

hoặc:

\[
E_2\Rightarrow E_4
\]

---

## 13. Định nghĩa trung tâm

> OIR-PPV nghiên cứu việc học một biểu diễn \(I_M\) của một lớp cơ chế chung được xác định tương đối bởi các cấu trúc, hàm hoặc tham số bất biến trong một lớp chuyển giao đã công bố trước. Biểu diễn được đánh giá theo tập nhiệm vụ, tập truy vấn can thiệp, phân phối trạng thái và lớp môi trường được xác định trước. Một ứng viên đạt yêu cầu nếu, khi kết hợp với trạng thái và các điều kiện môi trường được phép quan sát, nó có đủ thông tin để tái tạo các phân phối hậu can thiệp trong miền đánh giá, duy trì năng lực đó dưới các biến thiên môi trường hợp lệ chưa thấy, chịu được các nhiễu quan sát không làm thay đổi cơ chế, và đạt một vị trí xác định trên mặt đánh đổi giữa chi phí và năng lực. Tính đúng của \(I_M\) được hiểu theo lớp tương đương biểu diễn, không nhất thiết theo một mã hóa duy nhất. Khả năng sinh được đánh giá riêng theo tính hợp lệ, tính mới và độ trung thành cơ chế.

---

## 14. Trạng thái phiên bản

\[
\boxed{
\texttt{ONTOLOGY\_v1.0}
=
\texttt{FROZEN\_AT\_PRINCIPLE\_LEVEL}
}
\]

Ontology v1.0 không khóa các metric hoặc giao thức triển khai cụ thể. Những nội dung đó thuộc `FORMAL_SPEC_v1.0`.
