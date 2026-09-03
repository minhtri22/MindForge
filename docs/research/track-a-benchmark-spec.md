# Track A Benchmark v1 Specification

Status: **FROZEN SPECIFICATION / DATASET NOT YET MATERIALIZED**

Protocol authority: `docs/research/track-a-foundation-protocol.md`

## 1. Benchmark identity

```text
benchmark_id: track-a-capability-v1
version: 1.0
families: 7
cases_per_family: 200
total_cases: 1400
```

This specification freezes benchmark structure before any 5M/10M/20M/50M candidate is evaluated.

## 2. Split matrix

| Family | Calibration | Development | Held-out test | Total |
|---|---:|---:|---:|---:|
| A1 intent | 40 | 60 | 100 | 200 |
| A2 entity | 40 | 60 | 100 | 200 |
| A3 contextual interpretation | 40 | 60 | 100 | 200 |
| A4 tool/app selection | 40 | 60 | 100 | 200 |
| A5 argument extraction | 40 | 60 | 100 | 200 |
| A6 clarification | 40 | 60 | 100 | 200 |
| A7 local/external routing | 40 | 60 | 100 | 200 |
| **Total** | **280** | **420** | **700** | **1400** |

## 3. Case schema

Each materialized case must be representable as a versioned structured record with at least:

```text
case_id
benchmark_version
family
split
language_group
difficulty
adversarial_tags
counterfactual_group_id (nullable)
input
expected
scoring
provenance
```

Recommended conceptual structure:

```json
{
  "case_id": "A7-T-0001",
  "benchmark_version": "1.0",
  "family": "A7",
  "split": "test",
  "language_group": "vi",
  "difficulty": "adversarial",
  "adversarial_tags": ["unavailable_tool", "world_knowledge_trap"],
  "counterfactual_group_id": "CF-0042",
  "input": {
    "user_utterance": "...",
    "current_context": {},
    "personal_state": {},
    "available_actions": [],
    "available_local_capabilities": [],
    "external_capabilities": []
  },
  "expected": {
    "route": "EXTERNAL"
  },
  "scoring": {
    "primary": "route"
  },
  "provenance": {
    "truth_source": "human_or_rule",
    "generator_seed": null,
    "review_status": "reviewed"
  }
}
```

Exact serialization is deferred until dataset-materialization authorization. The semantic fields above are frozen.

## 4. Language quotas

Across 1,400 cases:

```text
Vietnamese: 840
Vietnamese-English code-mixed: 350
English: 210
```

Within each family the distribution should approximate the same ratio without allowing one split to become language-skewed.

## 5. Difficulty quotas

Across each family of 200:

```text
straightforward: 80
contextual/conditional: 70
adversarial/ambiguity-sensitive: 50
```

Across all families:

```text
straightforward: 560
contextual/conditional: 490
adversarial/ambiguity-sensitive: 350
```

## 6. Counterfactual quota

At least 20% of held-out test cases must participate in a controlled counterfactual pair/set.

Minimum:

```text
140 of 700 held-out cases
```

A counterfactual group must vary only a small declared field set, for example:

```text
current location
available action
personal entity mapping
explicit preference
missing argument
local capability availability
```

Scoring must include group consistency in addition to individual-case correctness.

## 7. Family-specific expected labels

### A1

Required scored field:

```text
intent_label
```

Intent label taxonomy must be frozen during materialization and may not be changed after held-out evaluation begins.

### A2

Required scored fields:

```text
entity_mentions
resolved_entity_ids / resolved_values
```

A case may require clarification rather than forced resolution.

### A3

Required scored field:

```text
interpretation_label or normalized interpretation record
```

The chosen representation must permit deterministic scoring.

### A4

Required scored field:

```text
action_id
```

Possible special labels:

```text
NONE
CLARIFY
```

The model must not receive credit for inventing an unavailable action.

### A5

Required scored field:

```text
arguments
```

Arguments are key/value slots. Optional slots must be distinguished from required missing slots.

### A6

Required scored fields:

```text
clarification_required: true|false
clarification_reason
```

Question wording itself is not a v1 primary score unless separately normalized.

### A7

Required scored field:

```text
route in {LOCAL_MODEL, LOCAL_APP_OR_TOOL, EXTERNAL, CLARIFY}
```

## 8. Adversarial tag vocabulary

The materialized v1 benchmark must support at least these tags:

```text
ambiguous_pronoun
similar_entity_names
irrelevant_personal_state
context_preference_conflict
missing_required_argument
unavailable_tool
local_vs_external_trap
world_knowledge_trap
stale_personal_fact
code_mix
noisy_text
clarification_required
semantically_similar_tools
unsupported_action
counterfactual_context
```

More tags may be added during materialization only if they do not change the frozen benchmark question or metrics.

## 9. Scoring normalization

Model output must be normalized to the benchmark expected representation before scoring.

Normalization may handle superficial differences such as:

```text
case
whitespace
JSON key order
canonical aliases explicitly listed in benchmark metadata
```

Normalization must not reinterpret a wrong semantic answer into a correct one.

Parser failures count as failures for the relevant scored fields.

## 10. Required metric report

Every candidate evaluation must output at least:

```text
candidate_id
parameter_count
benchmark_version
prompt/eval-template version
decoding settings
per-family primary metrics
per-family secondary metrics
macro family-primary
language-group metrics
difficulty-group metrics
adversarial-only metrics
counterfactual consistency
RVE PASS/FAIL
TUE PASS/FAIL
```

## 11. Critical-error accounting

Critical-error denominators must be explicit.

Examples:

```text
A6 under-clarification rate
= cases requiring clarification but predicted do-not-clarify
  / all cases requiring clarification

A7 false-local rate
= externally-required cases routed LOCAL_MODEL or LOCAL_APP_OR_TOOL
  / all externally-required cases

A4 unavailable-action false-selection
= cases where selected action is unavailable
  / cases containing unavailable-action traps
```

Do not report these only as raw counts.

## 12. Benchmark materialization acceptance

A future materialization task may mark Benchmark v1 `READY` only if:

```text
1400 unique stable IDs exist
split counts exactly match this specification
language quotas match exactly or have a documented <=1-case rounding adjustment per family
held-out counterfactual minimum is satisfied
all held-out labels are independently reviewed
all expected outputs are deterministically scoreable
no held-out truth was generated by a candidate model acting as final authority
artifact hashes are recorded
held-out content is frozen before N4 candidate tuning
```

## 13. Non-goals

Benchmark v1 does not test:

```text
general factual QA
general coding ability
open-ended reasoning quality
creative writing
broad multilingual coverage
long-horizon agent planning
PPF pattern inference
mobile OS permissions
real app execution
```

These exclusions are intentional. Track A asks for the smallest useful personal-understanding/router model, not a general assistant leaderboard.

## 14. Current status

```text
SPECIFICATION: FROZEN
DATASET: NOT MATERIALIZED
HELD-OUT SET: NOT CREATED
CANDIDATE RESULTS: NONE
N4: NOT AUTHORIZED
```
