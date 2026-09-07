# Research Roadmap

## PPF-G1 → G5 Research Closure Roadmap

## Purpose

Sau PPF-F1, PPF chuyển sang giai đoạn Feasibility Closure.
Mục tiêu không phải mở rộng mechanism, mà xác định liệu PPF có thể tồn tại như một extension/plugin độc lập trong MindForge architecture hay chỉ nên đóng ở mức research foundation.

PPF hiện trạng:

- PPF-L1: PASS / FROZEN
- PPF-L2: PASS / FROZEN
- PPF-L3: PASS / DATASET FROZEN
- PPF-L4: PASS
- PPF-L5: PASS
- PPF-C1: BLINDLY CONFIRMED

Confirmed primitive:

- Observability Eligibility

## Architecture Decision

PPF không thuộc Kernel.
PPF không yêu cầu Model modification.
PPF được đánh giá như một optional Plugin / Extension.

Boundary:

Kernel:
- execution substrate
- lifecycle contracts
- plugin interface

PPF Plugin:
- personal event semantics
- observation eligibility
- pattern hypotheses
- evidence interpretation

Model:
- optional learned representation assistance

Host:
- user interaction
- device integrations

---

# Roadmap

```
PPF-F1
Feasibility & Capability Placement Review
PASS
        |
        v
PPF-G1
Plugin Contract Feasibility
        |
        v
PPF-G2
Boundary & Runtime Isolation Proof
        |
        v
PPF-G3
Minimal Plugin Prototype Feasibility
        |
        v
PPF-G4
Real World Interface Feasibility
        |
        v
PPF-G5
Research Closure Decision
```

---

# PPF-G1 — Plugin Contract Feasibility

Question:

PPF có thể tồn tại như plugin độc lập mà không làm ô nhiễm Kernel, Model hoặc Host không?

Scope:

- plugin lifecycle contract
- event contract
- evidence contract
- eligibility contract
- semantic output contract

Không implementation.

PASS khi:

- Kernel không biết personal semantics.
- PPF không phụ thuộc model implementation.
- Host không chứa reasoning logic.

---

# PPF-G2 — Boundary & Runtime Isolation Proof

Question:

PPF có thể bị cô lập khỏi MindForge Core không?

Kiểm tra dependency direction:

Host
 |
Plugin
 |
Contracts
 |
Kernel primitives

Không được:

Kernel -> PPF semantics

---

# PPF-G3 — Minimal Plugin Prototype Feasibility

Question:

Một PPF plugin tối thiểu có chạy được với contract đã định nghĩa không?

Chỉ chứng minh:

PersonalEvent
 -> Evidence Eligibility
 -> Semantic State

Không:

- recognizer
- pattern discovery
- ML training
- LLM reasoning loop

---

# PPF-G4 — Real World Interface Feasibility

Question:

PPF semantic contract có ánh xạ được sang dữ liệu cá nhân thực tế không?

Nguồn xem xét:

- Android events
- iOS events
- wearable signals
- calendar
- health data

Không xây product.

---

# PPF-G5 — Research Closure Decision

Question:

PPF có đủ nền tảng để trở thành extension thực tế của MindForge không?

Possible outcomes:

## Prototype Authorized

Nếu:

- G1 PASS
- G2 PASS
- G3 PASS
- G4 PASS

## Research Foundation Complete

Nếu:

- G1 PASS
- G2 PASS
- G3 PASS

nhưng G4 chưa đủ.

## Stop

Nếu:

- G1 FAIL
hoặc
- G2 FAIL

---

## Definition of Done

PPF research phase kết thúc khi đạt một trong:

1. Prototype Authorized
2. Research Foundation Complete
3. Stop

Không tồn tại trạng thái nghiên cứu vô hạn.
