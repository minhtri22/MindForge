# OIR-PPV Research v1.0

Invariant -> Generator -> Manifestation -> Causal Validation
============================================================
# OIR-PPV v1.0
## Invariant → Representation → Generation → Predictive Validation

## 1. Research Motivation

OIR-PPV xuất phát từ một quan sát:

Một hệ thống có thể thay đổi biểu hiện bên ngoài nhưng vẫn duy trì một cấu trúc hành vi ổn định.

Ví dụ:

Một nhân vật cartoon có thể xuất hiện trong:

- phòng livestream
- công sở
- gia đình
- môi trường giả tưởng

Nhưng vẫn giữ:

- cách phản ứng
- mục tiêu
- phong cách hành động
- quan hệ nhân quả

Câu hỏi nghiên cứu:

> Liệu một hệ thống học được một latent invariant representation có thể sinh biểu hiện mới theo context và vẫn duy trì causal structure hay không?

---

# 2. Research Status

## Historical artifacts

Các phiên bản:

- v0.1 → v0.13.10

được xem là quá trình phát triển giả thuyết.

Hiện trạng:

- một số mô tả thiết kế còn tồn tại;
- source code, seed và raw experiment artifact của v0.13.10 chưa được xác nhận.

Vì vậy:

v0.13.10 được xem là:


Historical hypothesis checkpoint


không phải:


Verified implementation


---

# 3. Core Research Question

OIR-PPV nghiên cứu pipeline:

\[
E
\rightarrow
I
\rightarrow
G(I,Z,N)
\rightarrow
X'
\rightarrow
Intervention
\rightarrow
Counterfactual Validation
\]

Trong đó:

- E: experience
- I: invariant representation
- Z: meaningful context
- N: nuisance variation
- X: manifestation

---

# 4. Main Hypothesis

Một invariant representation tốt phải:

1. dự đoán được outcome;
2. tổng quát sang context mới;
3. không phụ thuộc nuisance;
4. sinh được manifestation mới;
5. giữ causal relationship dưới intervention.

---

# 5. Research Contribution

OIR-PPV không tuyên bố phát minh:

- invariant learning;
- causal representation learning;
- domain generalization.

Các lĩnh vực này đã có nền tảng.

Đóng góp mục tiêu:

Xây dựng benchmark thống nhất kiểm tra:

\[
Invariant
\rightarrow
Generator
\rightarrow
Manifestation
\rightarrow
Causal Validation
\]

---

# 6. Experimental Philosophy

Không chứng minh bằng:

- reconstruction score;
- visual similarity;
- prediction trên cùng domain.

Phải chứng minh bằng:

- transfer;
- nuisance robustness;
- counterfactual accuracy;
- causal consistency;
- complexity control.

---

# 7. Research Pipeline


Environment Generator
|
v
Experience Collection
|
v
Invariant Learner
|
v
Invariant Representation I
|
+----------------+
| |
v v

Policy Model Generator

    |                |
    +-------+--------+

            |
            v

    Intervention Engine

            |
            v

    Counterfactual Evaluation

            |
            v

         Evidence

---

# 8. Claim Boundary

Claim được phép:

> Trong các environment nhân quả được kiểm soát, invariant representation kết hợp context-conditioned generator có thể cải thiện transfer, robustness và counterfactual consistency so với baseline.

Không claim:

- invariant giống con người;
- consciousness;
- identity tâm lý;
- AGI.