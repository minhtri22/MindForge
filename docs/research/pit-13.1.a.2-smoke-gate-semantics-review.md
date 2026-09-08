# PIT-13.1.A.2 Smoke Gate Semantics Review

## 1. Context

PIT-13.1.A has two preserved failed pool-wide smoke executions. The latest rerun completed all 16 frozen API requests and produced 15/16 schema-valid Teaching Signal records. The single remaining failure was `mistralai/mistral-small-2603` on `preference_drift_001`, classified as `SERIALIZATION_NONCONFORMANCE_AFTER_FROZEN_NORMALIZATION` because the response contained malformed JSON with an invalid control character inside a JSON string.

PIT-13.1.A.1 already froze deterministic outer Markdown fence normalization and the scenario evidence mapping. The remaining failure is therefore candidate output serialization nonconformance under the frozen interface contract, not a harness ambiguity that may be repaired.

This review changes no historical evidence and performs no API or inference execution.

## 2. Research Question

What is the correct semantic unit of smoke qualification before PIT-13.1.B evidence collection?

- Option A: one pool-wide gate requiring all 16/16 samples to be valid.
- Option B: one independent gate per frozen candidate requiring that candidate's 4/4 samples to satisfy the smoke contract.

The decision must follow the entity PIT is qualifying rather than whether a choice makes execution easier.

## 3. Frozen Evidence

The relevant PIT architecture consistently treats the teacher candidate as the evaluated entity:

- `pit-teacher-evaluation-protocol.md` requires each candidate to produce its own capability profile, strengths, weaknesses, failure modes, and suitability verdict.
- `pit-10-candidate-teacher-evaluation-design.md` states that each candidate evaluation produces its own capability profile, failure modes, Teaching Signal examples, and qualification verdict.
- `pit-11.2-candidate-qualification-execution.md` states that each candidate must be evaluated on the frozen scenario categories and receives a candidate qualification verdict.
- `pit-12-candidate-qualification-evidence-generation.md` defines each candidate evaluation evidence item independently and requires candidate teacher quality to be determined from its Teaching Signal evidence.
- `research_ledger.md` PIT-12.1 distinguishes the theoretical candidate universe from the executable candidate pool, showing that candidate membership may narrow without deleting candidates from research history.
- `pit-13.0.1-api-candidate-manifest.md` freezes candidate identity individually and requires execution metadata to record `candidate_id` and `model_id` per execution.

The latest frozen smoke rerun records:

| Candidate | API completed | Schema valid | Parse failures |
| --- | ---: | ---: | ---: |
| `qwen/qwen3.7-max:free` | 4/4 | 4/4 | 0 |
| `deepseek/deepseek-v4-pro` | 4/4 | 4/4 | 0 |
| `minimax/minimax-m3:free` | 4/4 | 4/4 | 0 |
| `mistralai/mistral-small-2603` | 4/4 | 3/4 | 1 |

Across the pool: API completion 16/16, schema validity 15/16, model identity mismatch 0, credential leakage 0, manual repair 0, semantic retries 0, and per-model tuning 0.

The historical pool-wide acceptance verdict remains `FAIL`.

### Explicit analysis questions

**Q1. What is the intended object of PIT-13 candidate qualification?**

Each teacher candidate independently. PIT's evaluation documents assign evidence, failure modes, and qualification verdicts to individual candidates. The pool is an execution set, not the semantic object receiving a teacher qualification verdict.

**Q2. Does PIT-10/PIT-12 define teacher candidates as independently evaluated entities?**

Yes. PIT-10 says "Each candidate evaluation should produce" candidate-specific outputs and a qualification verdict. PIT-12 says "Each candidate evaluation evidence item must record" the required evidence fields. PIT-11.2 likewise requires "Each candidate" to be evaluated on the frozen dimensions.

**Q3. Would pool-wide gating create artificial coupling between otherwise independent teacher candidates?**

Yes. The API requests, candidate identities, outputs, and later candidate qualification evidence are independent. A pool-wide gate makes one candidate's serialization failure prevent evidence generation for candidates that fully satisfied the same frozen smoke contract, even though no later PIT rule evaluates the pool as one teacher.

**Q4. Does per-candidate smoke gating weaken any frozen Teaching Signal requirement?**

No. Every candidate must still satisfy 4/4 API completion, 4/4 schema validity, zero identity mismatch, zero credential leakage, zero manual repair, zero semantic retries, and zero model-specific tuning. The Teaching Signal schema, scenarios, prompts, parser normalization, scoring contract, and outputs are unchanged.

**Q5. Is per-candidate gating a legitimate clarification or a post-hoc threshold relaxation?**

It is a legitimate clarification of the gate's semantic unit. No numeric threshold is lowered: a candidate still requires 100% smoke validity, now expressed as 4/4 for the entity being qualified. No failed record becomes valid, no score changes, and Mistral still fails its smoke gate. The historical 15/16 pool-wide run remains `FAIL` under the original gate. The amendment applies prospectively only to downstream candidate eligibility.

**Q6. Can existing 4/4 evidence for Qwen, DeepSeek, and MiniMax be used without rerunning them?**

Yes. Their existing frozen rerun records already satisfy the clarified per-candidate gate. Re-execution would add no missing qualification fact and would violate the intended one-run evidence boundary without a new research reason.

**Q7. What status should Mistral receive?**

`SMOKE_NOT_QUALIFIED`. It is deferred from PIT-13.1.B under the current frozen execution contract. This status makes no claim about Mistral's teacher quality because semantic teacher qualification has not been executed.

## 4. Option A — Pool-Wide Gate

Benefits:

- Provides the strongest uniform guarantee that every frozen candidate completed smoke successfully in one fully valid pool.
- Produces a simple all-or-nothing acceptance condition.
- Avoids downstream candidate membership changes after smoke.

Risks:

- Couples independent candidate execution outcomes.
- Allows one candidate's serialization failure to block evidence generation for all other candidates.
- Treats the pool as the qualified entity even though later PIT evidence and verdicts are candidate-specific.
- Prevents progressive narrowing already compatible with the PIT-12.1 distinction between research universe and executable pool.

Under this option, the current 15/16 rerun remains `FAIL` and all PIT-13.1.B evidence collection remains blocked.

## 5. Option B — Per-Candidate Gate

Per-candidate smoke qualification is defined as:

`SMOKE_QUALIFIED` requires all of the following for one candidate:

- API completed: 4/4
- Schema valid: 4/4
- Model identity mismatch: 0
- Credential leakage: 0
- Manual repair: 0
- Semantic retries: 0
- Model-specific tuning: 0

`SMOKE_NOT_QUALIFIED` applies if any required condition fails.

Benefits:

- Matches the candidate-specific qualification object defined by PIT-10, PIT-11.2, and PIT-12.
- Preserves independent failure evidence rather than allowing one candidate to block others.
- Supports evidence generation only for candidates proven machine-consumable under the frozen contract.
- Preserves failed candidates in research history while narrowing the executable pool.

Risks and controls:

- Downstream evidence membership becomes 3/4 rather than 4/4. PIT-13.1.B must explicitly record which candidates were smoke-qualified and which were excluded.
- Cross-candidate comparisons must never imply evidence exists for a candidate deferred at smoke.
- Pool-level status must remain non-PASS so historical all-candidate execution is not silently reinterpreted.

## 6. Anti-Post-Hoc Analysis

Adopting the per-candidate gate is not equivalent to changing the threshold because Mistral failed.

The frozen facts remain unchanged:

- Candidate identity is independently frozen in the candidate manifest.
- Each API request is issued for one candidate and one scenario.
- Teacher qualification is candidate-specific.
- PIT-12 evidence is candidate-specific.
- No sample score changes.
- No failed output is reclassified as valid.
- Mistral remains failed under the smoke contract at 3/4 schema-valid samples.
- The 15/16 pool-wide rerun remains `FAIL` under its original acceptance gate.
- The earlier PIT-13.1.A failures also remain historical `FAIL` evidence.

The semantic amendment changes only the mapping from already-frozen candidate smoke outcomes to prospective PIT-13.1.B eligibility. It does not relax serialization correctness, modify the parser, add repair, retry a candidate, tune a model, remove a scenario, or alter the Teaching Signal contract.

## 7. Decision

**DECISION B: `ADOPT_PER_CANDIDATE_GATE`**

Reason:

The PIT architecture defines teacher qualification evidence and verdicts per candidate. Smoke qualification asks whether a candidate can reliably produce machine-consumable Teaching Signal records under the frozen interface contract. Therefore the smoke gate should qualify that same entity independently. Pool-wide gating adds cross-candidate coupling that is not required by the downstream research objective.

This decision is prospective only. The pool-level state after the latest rerun is:

`PARTIAL_CANDIDATE_QUALIFICATION`

This state does not replace or overwrite the historical `FAIL` verdict of the 15/16 pool-wide rerun.

## 8. Candidate Eligibility Consequences

Based only on the existing frozen rerun evidence:

| Candidate | Smoke state | PIT-13.1.B eligibility |
| --- | --- | --- |
| `qwen/qwen3.7-max:free` | `SMOKE_QUALIFIED` | Eligible |
| `deepseek/deepseek-v4-pro` | `SMOKE_QUALIFIED` | Eligible |
| `minimax/minimax-m3:free` | `SMOKE_QUALIFIED` | Eligible |
| `mistralai/mistral-small-2603` | `SMOKE_NOT_QUALIFIED` | Not eligible / deferred |

Mistral remains in the frozen research candidate history and candidate manifest. No replacement is selected or implied.

`SMOKE_NOT_QUALIFIED` is an execution-fit result for this interface contract. It is not a teacher quality verdict.

## 9. Historical Evidence Preservation

Preserved unchanged:

- Initial PIT-13.1.A smoke `FAIL`.
- Qwen3.7-amended smoke `FAIL`.
- PIT-13.1.A.1 harness audit evidence.
- Latest PIT-13.1.A rerun 15/16 pool-wide `FAIL`.
- Raw smoke responses.
- Scenario manifest.
- Candidate manifest.
- Parser and normalization contract.
- Teaching Signal schema.

No historical run is reclassified as `PASS`.

## 10. Next Step

PIT-13.1.B may proceed in a later reviewed task only for the three `SMOKE_QUALIFIED` candidates: Qwen3.7-Max, DeepSeek V4 Pro, and MiniMax M3.

This review does not execute PIT-13.1.B, rank candidates, or select a teacher.
