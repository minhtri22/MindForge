# Theory

E={(S_t,A_t,Y_t,Z_t,N_t)}

I=f(E)

X=G(I,Z,N)

I*=argmin_I[C(I)+lambda L(E|I)]

SCM:
S(t+1)=F_S(S,A,Z,U_S)
A=F_A(I,S,Z,U_A)
Y=F_Y(S,A,Z,U_Y)
============================================
# OIR-PPV Theory Specification v1.0

# 1. Formal Environment Model

Một environment sinh experience:

\[
E=
\{(S_t,A_t,Y_t,Z_t,N_t)\}_{t=1}^{T}
\]


Trong đó:

| Symbol | Meaning |
|-|-|
| S | state |
| A | action |
| Y | outcome |
| Z | context |
| N | nuisance |

---

# 2. Structural Causal Model

Hệ thống được mô hình hóa:

\[
S_{t+1}
=
F_S(S_t,A_t,Z_t,U_S)
\]


\[
A_t
=
F_A(I,S_t,Z_t,U_A)
\]


\[
Y_t
=
F_Y(S_t,A_t,Z_t,U_Y)
\]


Invariant I ảnh hưởng tới policy nhưng không phụ thuộc nuisance.

---

# 3. Invariant Representation

Mục tiêu:

\[
I=f(E)
\]


Một invariant tốt phải giữ:

- predictive information;
- causal information;
- transfer ability.

---

# 4. Minimal Invariant Objective

Không giả định invariant tối giản tuyệt đối.

Định nghĩa:

\[
I^*
=
\arg\min_I
[
C(I)
+
\lambda L(E|I)
]
\]


Trong đó:

## Complexity

\[
C(I)
=
\alpha d_I
+
\beta DL(I)
+
\gamma Params(I)
\]


## Explanation loss

\[
L(E|I)
\]

đo lượng thông tin mất khi chỉ sử dụng invariant.

Claim:

\[
Empirically\ minimal
under\ defined\ complexity
\]

---

# 5. Invariance Constraint

Invariant không được encode nuisance:

\[
I \perp N
\]


Thực nghiệm:

Khi thay:

\[
do(N=n_1)
\]

sang:

\[
do(N=n_2)
\]

policy phải ổn định:

\[
D(
\pi_I(N_1),
\pi_I(N_2)
)
\rightarrow min
\]

---

# 6. Generator Model

Invariant phải sinh manifestation:

\[
X=G(I,Z,N)
\]


Một generator tốt:

- giữ invariant;
- thay đổi context;
- cho phép variation hợp lệ.

---

# 7. Intervention Model

## Context intervention

\[
do(Z=z')
\]


Mục tiêu:

Test transfer.

---

## Nuisance intervention

\[
do(N=n')
\]


Mục tiêu:

Test robustness.

---

## Action intervention

\[
do(A=a')
\]


Mục tiêu:

Test causal response.

---

# 8. Counterfactual Validation

Counterfactual:

\[
Y^{cf}(z')
=
Y(do(Z=z'))
\]


Sai số:

\[
D_{cf}
=
d(
\hat Y^{cf},
Y^{cf}_{SCM}
)
\]


Điều kiện:

Ground truth phải đến từ SCM/environment.

Không được dùng:

\[
Generator
\rightarrow
GroundTruth
\]

vì gây circular evaluation.

---

# 9. Hypotheses

## H1 Compression

Invariant đạt trade-off tốt hơn:

\[
C(I)<C(M)
\]

với:

\[
Performance_I
\geq
Performance_M
\]


---

## H2 Transfer

Context mới:

\[
\Delta_{new}
=
Perf_{I,new}
-
Perf_{baseline,new}
>0
\]


---

## H3 Nuisance Robustness

\[
D(
\pi_I(N_1),
\pi_I(N_2)
)
<
D(
\pi_M(N_1),
\pi_M(N_2)
)
\]


---

## H4 Counterfactual Accuracy

\[
D_{cf}(I)
<
D_{cf}(M)
\]


---

## H5 Minimal Sufficiency

Ablation:

Loại thành phần quan trọng:

\[
\Delta Performance<0
\]


Thêm thành phần dư thừa:

\[
\Delta Transfer\leq0
\]

---

# 10. Success Criteria

OIR-PPV được hỗ trợ nếu:

1. invariant model vượt baseline trên novel context;
2. giữ policy dưới nuisance shift;
3. giảm counterfactual error;
4. generator sinh manifestation hợp lệ;
5. kết quả lặp lại qua nhiều seed.

Nếu không đạt:

Giả thuyết bị bác bỏ.