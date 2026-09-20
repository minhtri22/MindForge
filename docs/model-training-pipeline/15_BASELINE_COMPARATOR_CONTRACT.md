# 15 — Baseline & Comparator Contract

## 1. Mục đích

Mọi đánh giá PASS/FAIL phải chỉ rõ **so với cái gì**. Không được dùng một model công khai bất kỳ làm comparator khoa học nếu nó không phải matched control.

Pipeline định nghĩa bốn vai trò khác nhau:

1. `smoke_reference`: model nhỏ cố định dùng kiểm tra plumbing; không quyết định quality PASS/FAIL.
2. `parent_baseline`: exact checkpoint mà phase/experiment bắt đầu từ đó; là baseline mặc định để đo regression/gain.
3. `matched_control`: control branch dùng cùng parent, seed set, data budget, compute budget và evaluation contract khi claim là treatment tốt hơn control.
4. `external_anchor`: model ngoài dùng contextual comparison; không được dùng làm scientific gate trừ khi execution contract nêu rõ một external target tuyệt đối.

## 2. Canonical smoke reference

Reference model của R0/MVP là:

- model id: `Qwen/Qwen2.5-0.5B-Instruct`
- architecture: Qwen2 causal decoder
- role: pipeline plumbing only
- revision policy: source ref được resolve thành immutable Hub commit SHA ở `prepare/preflight`, SHA đã resolve được ghi vào frozen config trước bất kỳ training step nào.
- confirmatory/release run không được chứa unresolved ref như `main` hoặc `latest`.

Nếu upstream làm model này không còn tương thích với pinned llama.cpp/Ollama, thay reference model là **một spec change** và phải qua QA, không được silently fallback.

## 3. Parent baseline

Mỗi phase có:

```yaml
parent_artifact:
  artifact_id: run:<run_id>/phase:<phase_id>/checkpoint:<id>
  sha256: <resolved>
baseline:
  id: parent
  role: parent_baseline
  artifact_id: <same exact parent artifact>
```

Phase đầu có thể dùng Hub model đã resolve SHA làm parent. Phase sau phải trỏ exact canonical output của phase trước.

## 4. Matched control

Khi claim dạng “treatment A cải thiện so với control B”, comparator phải freeze:

- same parent artifact hash;
- same train/eval split IDs;
- matched seed mapping;
- same effective token budget;
- same max wall-clock/resource class nếu claim phụ thuộc compute;
- same checkpoint-selection semantics hoặc rule đã giải thích;
- same inference/evaluation contract;
- treatment khác control **chỉ ở intervention đã khai báo**.

```yaml
comparators:
  - id: control_standard_sft
    role: matched_control
    parent_baseline: parent
    intervention: standard_sft
    matched_to: treatment_reasoning_sft
    seeds: [101,102,103,104,105]
    token_budget: 5000000
    resource_class: gpu-16gb
```

## 5. Metric comparator contract

Mọi gate metric phải có:

```yaml
metric_id: instruction_accuracy
target_artifact: final
baseline_id: parent
comparison:
  type: relative_delta
  operator: ">="
  threshold: -0.02
aggregation:
  unit: seed
  method: mean
required: true
```

`comparison.type` chỉ được là:

- `absolute_value`
- `absolute_delta`
- `relative_delta`
- `ratio`
- `distribution_test` khi test đã freeze đầy đủ.

Không cho phép các từ mơ hồ như “no material regression” nếu không map về một contract máy đọc được.

## 6. Phase deltas

Với chuỗi `B0 -> CPT C1 -> replay C2 -> reasoning C3`, report bắt buộc có:

- `C1 - B0`: tác động CPT;
- `C2 - C1`: tác động replay/SFT;
- `C3 - C2`: tác động reasoning SFT;
- `C3 - B0`: tổng thay đổi.

Không được dùng chỉ `C3 - B0` để che một phase gây regression rồi được phase sau cứu.

## 7. Catastrophic forgetting protected suite

Execution contract phải khai báo `protected_capabilities` với metric, baseline và threshold. Tối thiểu với instruct/reasoning base:

- instruction-following;
- chat-format compliance;
- reasoning answer correctness;
- code capability nếu experiment có code scope;
- general language modeling/knowledge fixture nếu claim có general text.

Không có universal threshold; threshold được calibration rồi freeze trước fresh evidence.

## 8. External anchors

External anchor chỉ để trả lời “model hiện ở đâu so với model X”. Nó phải ghi model ID/revision/runtime/evaluation contract. Không được thay parent/matched control.

## 9. Promotion rule

Một model chỉ có thể được promote khi:

```text
absolute capability gates PASS
AND protected capability regression gates PASS vs parent
AND matched-control gates PASS when claim requires comparator
AND runtime/export/reproducibility gates PASS
```

Một smoke reference tốt hơn hay kém hơn final model không ảnh hưởng verdict khoa học.
