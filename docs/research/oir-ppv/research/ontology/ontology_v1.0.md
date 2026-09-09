# OIR-PPV Ontology v1.0
## Khóa ở cấp nguyên tắc

**Trạng thái:** `PRINCIPLE-LEVEL LOCKED`  
**Phạm vi:** Ontology và semantics khái niệm cốt lõi của OIR-PPV v1.0  
**Không đồng nghĩa:** `FORMAL_SPEC_v1.0` đã khóa hoàn toàn.

---

## 1. Mục đích

OIR-PPV nghiên cứu việc học một biểu diễn của phần cơ chế chung tồn tại qua một lớp biến thiên môi trường được xác định trước, nhằm giữ đủ thông tin cho các nhiệm vụ và truy vấn can thiệp quan tâm, trong khi giảm chi phí biểu diễn và hỗ trợ chuyển giao.

Khả năng sinh biểu hiện mới được đánh giá riêng ở cấp cặp `(I_M, G)`, không được coi là thuộc tính tự động của `I_M`.

---

## 2. Các đối tượng nền tảng

OIR-PPV phân biệt rõ:

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

- \(M_{\text{shared}}\): phần cấu trúc/cơ chế thật được giả định là chung trong lớp chuyển giao.
- \(I_M\): biểu diễn học được về phần cơ chế chung đó.
- \(S_t\): trạng thái cụ thể của hệ tại thời điểm \(t\).
- \(Z_e\): điều kiện môi trường có ý nghĩa đối với kết quả.
- \(A\): hành động hoặc can thiệp.

Không được dùng một ký hiệu duy nhất để đồng nhất cơ chế thật với biểu diễn học được.

---

## 3. Cơ chế chung và biến thiên môi trường

Phần cơ chế chung được mô tả ở cấp nguyên tắc bởi:

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

- \(\mathcal G_{\text{shared}}\): cấu trúc phụ thuộc/đồ thị nhân quả được giữ chung;
- \(F_{\text{shared}}\): họ hàm/cơ chế sinh được giữ chung;
- \(\Theta_{\text{shared}}\): các tham số được yêu cầu giữ cố định trong lớp chuyển giao đang xét.

Một môi trường cụ thể được tạo từ phần chung và phần biến thiên hợp lệ:

\[
M_e
=
\mathcal M
(
\mathcal G_{\text{shared}},
F_{\text{shared}},
\Theta_{\text{shared}},
\Delta_e
)
\]

Trong đó \(\Delta_e\) biểu diễn các điều kiện, tham số hoặc thành phần được phép thay đổi theo môi trường.

Không được giả định rằng mọi \(M_e\) có thể thay đổi tùy ý.

---

## 4. Lớp chuyển giao

Chuyển giao chỉ có nghĩa trong một lớp biến thiên môi trường được công bố trước.

Với mỗi lớp chuyển giao \(\mathcal S_k\), phải chỉ rõ:

\[
\operatorname{Inv}(\mathcal S_k)
=
\{
\text{các thành phần của } M_e \text{ bắt buộc giữ nguyên}
\}
\]

Và phải phân biệt:

\[
\operatorname{ShiftClass}_{\text{declared}}
\]

với:

\[
\operatorname{ShiftClass}_{\text{realized}}
\]

Mỗi môi trường kiểm tra phải có ánh xạ:

\[
\Delta_e
\rightarrow
\operatorname{ShiftClass}
\rightarrow
\operatorname{Inv}
\]

Không được gán lại loại dịch chuyển sau khi đã xem kết quả.

Nếu môi trường kiểm tra phá luôn phần \(M_{\text{shared}}\) mà benchmark tuyên bố phải giữ, thì đó không còn là phép thử chuyển giao trong cùng lớp cơ chế.

---

## 5. Biểu diễn học được

Biểu diễn cơ chế được học từ dữ liệu huấn luyện:

\[
I_M
=
\phi
(
D_{\text{train}};
\mathcal T,
\mathcal A
)
\]

Trong đó:

- \(D_{\text{train}}\): dữ liệu/trải nghiệm huấn luyện;
- \(\mathcal T\): tập nhiệm vụ;
- \(\mathcal A\): tập truy vấn hoặc can thiệp quan tâm.

Môi trường kiểm tra không được dùng để học \(I_M\).

Môi trường xác thực chỉ được dùng cho lựa chọn mô hình/cấu hình theo giao thức đã công bố.

---

## 6. Không yêu cầu định danh duy nhất của biểu diễn

OIR-PPV không giả định tồn tại một mã hóa duy nhất của cơ chế thật.

Nếu \(h\) là phép biến đổi được chấp nhận, các biểu diễn:

\[
I_M
\quad \text{và} \quad
h(I_M)
\]

có thể tương đương nếu chúng tạo ra cùng kết quả trên tập nhiệm vụ, tập can thiệp và lớp chuyển giao đã định nghĩa.

Lớp tương đương được ký hiệu:

\[
[I_M]_{\sim}
=
\{
h(I_M):
h\in\mathcal H_{\text{admissible}}
\}
\]

Do đó:

> tính đúng của biểu diễn không đồng nghĩa với khả năng đọc trực tiếp hoặc sự giống nhau về tọa độ latent.

---

## 7. Tách cơ chế khỏi trạng thái và điều kiện môi trường

\(I_M\) không được buộc phải chứa toàn bộ trạng thái hiện tại hoặc toàn bộ điều kiện môi trường.

Dự đoán hậu quả cần có dạng:

\[
\hat p_\psi
(
y
\mid
I_M,
S_t,
Z_e,
a
)
\]

và được so với phân phối hậu can thiệp của môi trường thật:

\[
p_{M_e}
(
Y
\mid
do(A=a),
S_t,
Z_e
)
\]

Như vậy:

- \(I_M\) giữ thông tin về cơ chế;
- \(S_t\) mô tả trạng thái hiện tại;
- \(Z_e\) mô tả điều kiện môi trường;
- \(a\) mô tả hành động được đưa vào mô hình học;
- \(do(A=a)\) thuộc ngữ nghĩa can thiệp của SCM.

---

## 8. Ba loại truy vấn phải được tách riêng

### 8.1 Dự đoán quan sát

\[
P(Y\mid X)
\]

### 8.2 Dự đoán hậu can thiệp

\[
P(Y\mid do(A=a),S,Z)
\]

### 8.3 Dự đoán phản thực

\[
Y_{a'}\mid A=a
\]

Không được dùng một chữ “nhân quả” để bao trùm ba loại truy vấn này.

---

## 9. Đủ nhân quả là tương đối

Không tồn tại “đủ nhân quả tuyệt đối” nếu không xác định rõ phạm vi.

Một biểu diễn chỉ được gọi là đủ nhân quả tương đối với:

\[
(
\mathcal T,
\mathcal A,
\mathcal E
)
\]

nếu nó cho phép tái tạo đủ chính xác các phân phối hậu can thiệp cần thiết trong tập nhiệm vụ, tập can thiệp và lớp môi trường đã định trước.

Ở cấp vận hành, nên ưu tiên khái niệm:

\[
\mathcal R_{\text{interventional-sufficiency}}
\]

thay vì suy diễn rằng biểu diễn đã học được toàn bộ cơ chế nhân quả.

Nếu mục tiêu là kiểm tra khả năng học cơ chế thay vì ghi nhớ phản ứng theo hành động, benchmark có thể yêu cầu:

\[
\mathcal A_{\text{train}}
\cap
\mathcal A_{\text{test}}
=
\varnothing
\]

---

## 10. Chuyển giao là bảo toàn cơ chế trong lớp biến thiên đã định nghĩa

Chuyển giao không yêu cầu phân phối kết quả giữa các môi trường phải giống nhau.

Cùng một cơ chế có thể tạo kết quả khác nhau khi:

- trạng thái khác;
- tham số nền khác;
- điều kiện môi trường khác;
- can thiệp khác.

Điều cần bảo toàn là năng lực của cùng biểu diễn \(I_M\), kết hợp với \(S_t\), \(Z_e\) và \(A\), để dự đoán đúng hệ quả trong môi trường mới thuộc lớp dịch chuyển đã công bố.

Do đó:

\[
\text{chuyển giao cơ chế}
\neq
\text{đầu ra giống hệt giữa các môi trường}
\]

---

## 11. Huấn luyện, xác thực và kiểm tra

Phải tách:

\[
\mathcal E_{\text{train}},
\qquad
\mathcal E_{\text{validation}},
\qquad
\mathcal E_{\text{test}}
\]

Tập kiểm tra không được dùng để:

- chọn kiến trúc;
- chọn siêu tham số;
- chọn checkpoint;
- thay đổi ontology;
- thay đổi định nghĩa chi phí;
- thay đổi tập biến;
- chọn ngưỡng sau khi xem kết quả.

Chống rò rỉ phải xem xét ít nhất:

1. độc lập mẫu;
2. độc lập quỹ đạo;
3. độc lập hạt giống;
4. độc lập tham số môi trường;
5. độc lập cấu hình cơ chế;
6. độc lập quy trình tạo benchmark.

Tập kiểm tra phải được khóa; mọi lần mở lại để sửa benchmark phải tạo phiên bản benchmark mới.

---

## 12. Hai chế độ bằng chứng

### 12.1 Có cơ chế thật

Dùng trong simulator hoặc SCM đã biết.

Có thể trực tiếp so sánh với:

\[
p_M
(
Y
\mid
do(A=a),
S,
Z
)
\]

Đây là chế độ phù hợp nhất để kiểm chứng lý thuyết.

### 12.2 Không có cơ chế thật

Dùng với dữ liệu thực.

Không được giả định biết \(M\).

Bằng chứng cần được phân cấp:

1. **cơ chế thật biết được**;
2. **bằng chứng can thiệp**;
3. **bằng chứng nhất quán cơ chế**;
4. **bằng chứng chuyển giao dự đoán**.

Không được suy diễn bằng chứng cấp thấp thành ground truth nhân quả.

---

## 13. Robustness: tách nhiễu quan sát khỏi biến môi trường

### 13.1 Nhiễu quan sát

Ký hiệu \(\eta\), ví dụ:

\[
X' = X+\eta
\]

Nhiễu này không được làm thay đổi cơ chế thật.

Mục tiêu chính là giữ hiệu năng nhiệm vụ hoặc hiệu năng hậu can thiệp ổn định.

Sự ổn định của latent:

\[
\phi(X+\eta)
\approx
\phi(X)
\]

chỉ là chỉ số chẩn đoán, không phải mục tiêu bắt buộc.

### 13.2 Biến môi trường

Nếu một biến thật sự ảnh hưởng tới kết quả, nó phải được mô hình hóa qua \(Z_e\), không được tùy tiện xem là “nhiễu cần bỏ”.

---

## 14. Không tìm một nghiệm tối ưu duy nhất

OIR-PPV không định nghĩa một \(I^*\) duy nhất bằng một hàm mục tiêu vô hướng bắt buộc.

Thay vào đó, các ứng viên được xem xét trên một vùng đánh đổi giữa:

- chi phí;
- hiệu năng nhiệm vụ;
- đủ hậu can thiệp;
- khả năng chuyển giao;
- độ bền.

Chi phí có thể là vector:

\[
\mathbf C
=
(
C_{\text{dim}},
C_{\text{param}},
C_{\text{memory}},
C_{\text{compute}},
C_{\text{data}}
)
\]

và đánh giá nên xem xét bất định thống kê.

Mục tiêu là xác định các biểu diễn hoặc lớp biểu diễn không bị trội trên mặt Pareto, không phải tuyên bố một biểu diễn tối ưu tuyệt đối.

---

## 15. Khả năng sinh là thuộc tính của cặp \((I_M,G)\)

Sinh tạo không phải thuộc tính tự động của \(I_M\).

Phần sinh được mô tả:

\[
(
I_M,
G,
S,
Z,
A
)
\longrightarrow
X_{\text{new}}
\]

và phải đánh giá riêng ít nhất ba trục:

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

Ba khái niệm này không đồng nhất:

\[
\text{hợp lệ}
\neq
\text{mới}
\neq
\text{trung thành cơ chế}
\]

Một mẫu sinh mạnh cần chịu được các phép can thiệp tương ứng và vẫn hành xử như một mẫu hợp lệ của cơ chế được tuyên bố.

---

## 16. H1–H6 là các trục đánh giá tương đối độc lập về claim

H1–H6 không phải một chuỗi suy diễn tuyến tính.

Một hệ có thể:

- nén tốt nhưng chuyển giao kém;
- chuyển giao tốt nhưng phản thực kém;
- sinh được nhưng không giữ cơ chế;
- giữ cơ chế nhưng không tối giản.

Do đó H1–H6 được xem là:

> các trục đánh giá tương đối độc lập về mặt claim, nhưng có thể phụ thuộc hoặc tương tác về mặt cơ chế và triển khai.

Không gọi chúng là trực giao tuyệt đối.

---

## 17. Quy tắc phiên bản hóa

Ba nguyên tắc:

### Không hồi tố

Không thay giao thức, dữ liệu hoặc kết quả cũ rồi giữ nguyên nhãn phiên bản.

### Được tái diễn giải

Ontology mới có thể thu hẹp hoặc giải thích lại claim cũ, nhưng phải ghi rõ đó là tái diễn giải.

### Phải tái đánh giá khi cần

Nếu phát hiện lỗi định nghĩa hoặc rò rỉ làm thay đổi phép đo, phải tạo giao thức mới và chạy lại.

Ví dụ:

\[
Protocol_{v1.0}
\neq
Protocol_{v1.1}
\]

Mọi kết quả phải gắn với đúng phiên bản giao thức.

---

## 18. Định nghĩa trung tâm v1.0

> **OIR-PPV nghiên cứu việc học một biểu diễn \(I_M\) của một lớp cơ chế chung được xác định tương đối bởi cấu trúc, hàm hoặc tham số bất biến trong một lớp chuyển giao đã công bố trước. Biểu diễn được đánh giá theo tập nhiệm vụ, tập truy vấn can thiệp, phân phối trạng thái và lớp môi trường được xác định trước. Một ứng viên đạt yêu cầu khi, kết hợp với trạng thái và các điều kiện môi trường được phép quan sát, nó giữ đủ thông tin để tái tạo các phân phối hậu can thiệp liên quan trong miền đánh giá, duy trì năng lực đó dưới các biến thiên môi trường hợp lệ chưa thấy, chịu được nhiễu quan sát không làm thay đổi cơ chế, và đạt một vị trí xác định trên mặt đánh đổi giữa chi phí và năng lực. Tính đúng của \(I_M\) được hiểu theo lớp tương đương biểu diễn, không nhất thiết theo một mã hóa duy nhất. Khả năng sinh được đánh giá riêng trên cặp \((I_M,G)\) theo tính hợp lệ, tính mới và độ trung thành với cơ chế.**

---

## 19. Những nguyên tắc đã khóa

Các nguyên tắc sau được xem là khóa ở cấp ontology v1.0:

1. Cơ chế thật và biểu diễn học được là hai đối tượng khác nhau.
2. Biểu diễn cơ chế, trạng thái hiện tại, điều kiện môi trường và hành động là các vai trò khác nhau.
3. Chuyển giao chỉ có nghĩa trong một lớp dịch chuyển được xác định trước.
4. Mỗi lớp dịch chuyển phải công bố thành phần nào của cơ chế được giữ bất biến.
5. Chuyển giao cơ chế không đồng nghĩa với đầu ra giống nhau giữa các môi trường.
6. Đủ nhân quả luôn tương đối với tập nhiệm vụ, tập can thiệp và lớp môi trường.
7. Không yêu cầu định danh duy nhất của latent representation.
8. Dữ liệu huấn luyện, xác thực và kiểm tra phải được phân tách và chống rò rỉ ở nhiều cấp.
9. Nhiễu quan sát và biến môi trường có ý nghĩa nhân quả không được gộp chung.
10. Sinh tạo là thuộc tính của cặp \((I_M,G)\), không phải của \(I_M\) riêng lẻ.
11. Không chọn một nghiệm tối ưu tuyệt đối bằng một thước đo chi phí duy nhất; ưu tiên báo cáo mặt đánh đổi.
12. H1–H6 là các trục claim khác nhau nhưng có thể tương tác.
13. Kết quả cũ không bị sửa hồi tố; mọi thay đổi định nghĩa phải được phiên bản hóa.
14. Bằng chứng trên dữ liệu thực không được mặc nhiên coi là ground truth nhân quả.

---

## 20. Những phần chưa khóa

Ontology này **không** tuyên bố các nội dung sau đã hoàn tất:

- định nghĩa vận hành đầy đủ của từng `ShiftClass`;
- phân phối chính thức trên môi trường, trạng thái và can thiệp;
- ngưỡng chấp nhận cụ thể;
- cách tính thống kê và khoảng tin cậy;
- thước đo chi phí chính thức;
- định nghĩa định lượng đầy đủ cho validity, novelty, mechanism fidelity;
- giao thức H3/H4/H5/H6 cuối cùng;
- `FORMAL_SPEC_v1.0`.

Các nội dung này thuộc vòng khóa đặc tả hình thức tiếp theo.

---

## 21. Trạng thái

\[
\boxed{
\text{ONTOLOGY v1.0 = PRINCIPLE-LEVEL LOCKED}
}
\]

\[
\boxed{
\text{FORMAL\_SPEC v1.0 = NOT YET LOCKED}
}
\]

Từ thời điểm này, thay đổi ontology phải được thực hiện bằng phiên bản mới hoặc một quyết định sửa đổi có truy nguyên, không sửa âm thầm định nghĩa đã khóa.
