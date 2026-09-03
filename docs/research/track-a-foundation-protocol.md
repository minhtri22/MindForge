# Track A Foundation Protocol — MindForge-Mobile Capability Envelope

Status: **FROZEN RESEARCH PROTOCOL / N3 COMPLETE / N4 NOT AUTHORIZED**

Branch: `research/track-a-foundation-protocol`

Starting architectural reference: `5280243a54ba8977b0d02a5b4ed85c657e03193f`

## 1. Purpose

Track A asks one bounded question:

> **How small can the learned model be while preserving useful personal understanding and routing when persistent personal state and world knowledge are externalized?**

The candidate size ladder remains a hypothesis to test, not a product commitment:

```text
5M / 10M / 20M / 50M parameters
```

The <=20M target remains a hypothesis, not a claim.

This protocol freezes what Track A must prove before any compact-model scaling experiment is authorized.

## 2. Architecture boundary

Track A follows the frozen MindForge architecture invariants:

```text
Model != Kernel
learned/generalizable behavior -> Model candidate
universal runtime mechanics -> Kernel candidate only after KAT proof
feature-specific semantics -> Plugin
host/platform integration -> Host / Adapter
```

MindForge-Mobile is an optional host/product branch, not the architectural center.

Track A therefore does **not** authorize:

- Android/iOS integration;
- OEM permissions;
- app APIs;
- agent frameworks;
- PPF integration;
- personal-memory implementation;
- new kernel primitives;
- a mobile runtime architecture;
- quantization/runtime packaging;
- external model adapters.

## 3. Personal-state externalization assumption

Track A must not force the learned model to infer long-term personal history from weights.

Each benchmark case may provide an explicit bounded `personal_state` fixture containing facts relevant to the current request, for example:

```text
preferred commute app = Maps
partner = Linh
home = District 7
usual work location = District 1
preferred language = Vietnamese
```

This supplied state is benchmark input, not PPF output.

Track A must remain independently executable when PPF does not exist.

Benchmark truth must not depend on a PPF implementation.

## 4. Core behavioral contract

The benchmark treats the model as a bounded understanding/routing component.

A case contains some subset of:

```text
user_utterance
current_context
personal_state
available_actions
available_local_capabilities
external_capabilities
```

The expected answer contains only the fields needed for the task family under evaluation.

Conceptual output dimensions are:

```text
intent
resolved personal entities
contextual interpretation
target app/tool/action
arguments
clarification decision
local-vs-external route
```

This benchmark output schema is an evaluation representation only. It does not redefine the MKS `TokenModel` runtime contract.

## 5. Frozen capability families

N3 freezes seven capability families for v1.

### A1 — Personal intent recognition

Question:

> Can the model identify what the user is trying to accomplish without relying on broad world knowledge?

Examples include communication, navigation, reminder-like intent, local transformation, lookup delegation, app action, and no-action/clarification intent.

Primary metric: macro-F1.

### A2 — Personal entity resolution

Question:

> Can the model resolve personal references using only the supplied personal-state/context fixture?

Examples:

```text
"nhắn cho vợ"
"gọi anh Tuấn bên dự án A"
"đường về nhà"
"quán cà phê mình hay ngồi"
```

Primary metric: entity-set F1 plus resolved-value accuracy.

### A3 — Contextual interpretation

Question:

> Can the model use current context and supplied personal state to disambiguate the user's meaning?

Examples include time, location, current activity, available device/app state, and explicit preference/context conflicts.

Primary metric: normalized interpretation accuracy.

### A4 — Tool / app selection

Question:

> Given a frozen list of available actions, can the model select the correct target without inventing unavailable tools?

Primary metric: top-1 selection accuracy.

Secondary error metric: unavailable-action false-selection rate.

### A5 — Argument extraction

Question:

> Can the model extract the minimum action arguments correctly?

Examples include contact, destination, text payload, time expression, query string, app target, and bounded options.

Primary metric: slot micro-F1.

Secondary metric: exact record match.

### A6 — Clarification decision

Question:

> Can the model determine when information is insufficient or conflicting rather than guessing?

This includes both under-clarification and over-clarification.

Primary metric: macro-F1 over `clarify` / `do_not_clarify`.

Critical secondary metrics:

```text
under-clarification rate
over-clarification rate
```

### A7 — Local-vs-external routing

Question:

> Can the model decide whether the request can be handled by the supplied local/app capabilities or must be delegated externally?

Routes are benchmark labels, not kernel APIs.

Frozen route classes:

```text
LOCAL_MODEL
LOCAL_APP_OR_TOOL
EXTERNAL
CLARIFY
```

Primary metric: macro-F1 / route accuracy.

Critical secondary metrics:

```text
false-local rate on externally-required cases
unnecessary-external rate on locally-solvable cases
```

## 6. Explicitly deferred capabilities

The following remain useful Track-A ideas but are not part of benchmark v1:

```text
returned-result interpretation
free-form local summarization
free-form transformation
multi-step agent planning
long-horizon tool use
```

They may be admitted only by a separate protocol amendment after the seven core families are tested.

## 7. Benchmark scale and split freeze

Track-A Benchmark v1 contains exactly:

```text
7 families × 200 cases = 1,400 evaluation cases
```

Each family is partitioned as:

```text
40 calibration cases
60 development cases
100 held-out test cases
```

Total:

```text
calibration = 280
development = 420
held-out test = 700
```

The held-out test set is not used for prompt tuning, label-policy changes, threshold tuning, or training-data generation.

Any future training corpus is a separate artifact and must have entity/template/scenario leakage controls against all evaluation splits.

## 8. Language distribution

Because the initial personal-intelligence use case is Vietnam-focused while code-switching is common in digital interactions, v1 freezes:

```text
60% Vietnamese
25% Vietnamese-English code-mixed
15% English
```

The benchmark must include natural punctuation variation, abbreviations, casual phrasing, and bounded typo/noise cases.

Language mix is a benchmark choice, not a claim about final product geography.

## 9. Difficulty distribution

Within each capability family:

```text
40% straightforward
35% contextual/conditional
25% adversarial or ambiguity-sensitive
```

The held-out set must not be easier than calibration/development by construction.

## 10. Required adversarial families

At minimum v1 must include:

1. ambiguous pronouns / multiple candidate personal entities;
2. similar entity names;
3. irrelevant personal-state distractors;
4. conflict between current context and stored preference;
5. missing required argument;
6. unavailable requested app/tool;
7. locally-solvable request disguised as broad question;
8. world-knowledge request disguised as personal command;
9. stale or explicitly superseded personal fact;
10. code-mixed Vietnamese/English phrasing;
11. typo/noisy short utterance;
12. safe abstention/clarification cases;
13. app-choice distractors with semantically similar capabilities;
14. unsupported action where invention must be rejected;
15. counterfactual pairs differing in exactly one context/state field.

## 11. Counterfactual requirement

At least 20% of held-out cases must belong to controlled counterfactual pairs or sets.

Example:

```text
same utterance
same personal state
location = office   -> route/action A
location = home     -> route/action B
```

or:

```text
same utterance
available app present   -> LOCAL_APP_OR_TOOL
available app absent    -> EXTERNAL or CLARIFY
```

This prevents a model from passing only through lexical memorization.

## 12. Truth construction

Ground truth must be authored independently of candidate small-model output.

Allowed truth sources:

```text
rule-defined scenario truth
human-authored labels
independently reviewed structured fixtures
```

External large models may propose candidate examples but may not become the final truth authority.

Every held-out case must have deterministic expected labels for its scored fields.

Ambiguous cases must explicitly encode acceptable alternatives or a required clarification label.

## 13. External reference / teacher policy

A strong external model may be evaluated on the same frozen benchmark as a reference ceiling.

Reference models are **not** members of the 5M/10M/20M/50M candidate sweep.

A reference model may later assist with:

```text
candidate scenario generation
error taxonomy suggestions
training-example proposal
teacher/distillation research
```

but:

```text
reference output != benchmark truth
```

Any named reference model requires separate qualification for reproducibility, availability, license/runtime practicality, and prompt freeze.

Qwen3.8-27B is currently a proposed external reference candidate only; it is not admitted by this protocol and is not required for N3 PASS.

## 14. Metrics

Each family keeps its primary metric visible; no single aggregate score may hide a family failure.

Required family metrics:

| Family | Primary | Required secondary |
|---|---|---|
| A1 intent | macro-F1 | confusion matrix |
| A2 entity | entity-set F1 | resolved-value accuracy |
| A3 context | accuracy | counterfactual consistency |
| A4 tool/app | top-1 accuracy | unavailable-action false-selection |
| A5 arguments | slot micro-F1 | exact-record match |
| A6 clarification | macro-F1 | under/over-clarification |
| A7 routing | macro-F1 + accuracy | false-local + unnecessary-external |

Also report:

```text
macro average across family primary metrics
performance by language group
performance by difficulty group
adversarial-only performance
counterfactual consistency
```

## 15. Frozen capability envelopes

Two envelopes are frozen before model-size experiments.

### Research Viability Envelope — RVE

A model is Track-A viable only if:

```text
macro family-primary >= 0.80
no family primary < 0.70
A6 under-clarification <= 0.08
A7 false-local <= 0.05
unavailable-action false-selection <= 0.05
```

RVE means the hypothesis remains worth investigating. It is not a product-ready claim.

### Target Utility Envelope — TUE

A candidate satisfies the current Track-A target only if:

```text
macro family-primary >= 0.90
no family primary < 0.85
A2 resolved-value accuracy >= 0.90
A5 exact-record match >= 0.85
A6 under-clarification <= 0.03
A7 false-local <= 0.02
unavailable-action false-selection <= 0.02
counterfactual consistency >= 0.90
```

These gates are deliberately frozen before seeing 5M/10M/20M/50M results.

## 16. Size-sweep decision rule for N4

N4, if separately authorized, must evaluate candidate sizes in ascending order where practical:

```text
5M -> 10M -> 20M -> 50M
```

Decision rule:

1. The smallest candidate meeting TUE is the preferred capability winner.
2. If no model meets TUE but one or more meet RVE, classify Track A as `REVISE` and investigate the measured failure before adding architecture.
3. If no candidate meets RVE, classify the current Track-A compact-model hypothesis `STOP / REFRAME` rather than automatically increasing complexity.
4. A larger model is not preferred when a smaller model already meets TUE unless systems evidence demonstrates a separate material benefit.

## 17. Systems metrics reserved for N4

When N4 is authorized, every candidate must additionally report:

```text
parameter count
serialized model bytes
peak RAM / device memory
cold-start/load time
single-request latency
throughput
energy/power where measurement is practical
```

Systems metrics do not replace capability gates.

A model that is fast but fails the capability envelope does not pass Track A.

## 18. Reproducibility requirements

Before N4:

- benchmark generator/version must be frozen;
- case IDs must be stable;
- split membership must be frozen;
- label schema must be versioned;
- random seeds used in case generation must be recorded;
- benchmark artifacts must be hashable;
- candidate decoding settings must be frozen;
- prompts/templates used for evaluation must be versioned;
- any external reference model prompt must be separately frozen.

## 19. Leakage rules

Forbidden:

```text
training directly on held-out cases
paraphrasing held-out cases into training data
reusing held-out entity combinations/templates in a way that reveals answers
teacher generation conditioned on held-out truth
manual tuning against held-out errors before final score freeze
```

Entity names alone may recur only when the benchmark explicitly tests repeated personal entities; scenario/template leakage must still be controlled.

## 20. Track A / PPF isolation

PPF is not required for this benchmark.

Track-A fixtures may include supplied personal-state facts, but they must not include:

```text
PPF confidence semantics
PPF event model requirements
PPF pattern inference
PPF opportunity semantics
PPF plugin APIs
```

Future Track A + PPF composition is separately gated.

## 21. N3 gates

N3 is a protocol-freeze task, not a model-performance task.

N3 PASS requires:

```text
A-FP-G1 research question frozen
A-FP-G2 seven capability families frozen
A-FP-G3 input/state externalization assumption explicit
A-FP-G4 output/scoring contract frozen
A-FP-G5 benchmark size/splits frozen
A-FP-G6 adversarial/counterfactual requirements frozen
A-FP-G7 metrics frozen before model evaluation
A-FP-G8 RVE/TUE thresholds frozen before results
A-FP-G9 external-reference policy prevents teacher-as-truth leakage
A-FP-G10 PPF/kernel/mobile implementation not introduced
A-FP-G11 N4 not executed
A-FP-G12 5M/10M/20M/50M remain hypotheses, not claims
```

## 22. N3 decision

```text
TRACK A FOUNDATION PROTOCOL: FROZEN
N3: PASS
TRACK-A CAPABILITY ENVELOPE: NOT YET PROVEN
BENCHMARK DATASET: NOT YET MATERIALIZED
CANDIDATE TRAINING: NOT STARTED
N4 SIZE SWEEP: NOT AUTHORIZED / NOT STARTED
N5 CROSS-DEVICE: NOT AUTHORIZED / NOT STARTED
QWEN3.8-27B REFERENCE QUALIFICATION: SEPARATE OPTIONAL TASK
PPF INTEGRATION: NOT AUTHORIZED
KERNEL CHANGE: NO
MODEL ARCHITECTURE CHANGE: NO
```

N3 PASS means the experiment is now falsifiable. It does not mean a <=20M model is sufficient.
