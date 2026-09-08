# PIT-13.1 Candidate API Evidence Collection

Status:

SMOKE FAILED / HARNESS AUDIT COMPLETED

## Execution methodology

PIT-13.1 follows the frozen PIT-10 teaching signal contract and requires two phases:

- PIT-13.1.A Smoke Qualification
- PIT-13.1.B Evidence Collection

The execution layer is xKiro API. Credentials remain external and are not stored in research artifacts.

## Smoke qualification result

FAIL

Frozen execution:

- Attempt: one 16-sample run (`4 models x 4 scenarios`).
- Runner exit code: 0.
- Records written: 16/16.
- Schema-valid records: 4/16.
- Verified model identity mismatches: 0; identity was not recoverable for eight parse-path failures because the runner overwrote their raw responses.
- Credential leakage: 0.
- Manual repair: 0.
- Per-model tuning: 0.
- Retry: 0.

Candidate outcomes:

| Candidate | Records | Verified API completed | Schema valid | Outcome |
| --- | ---: | ---: | ---: | --- |
| `qwen/qwen3.8-max:free` | 4 | 0 | 0 | Four HTTP 500 `internal_error` responses |
| `deepseek/deepseek-v4-pro` | 4 | 4 | 4 | Completed and schema valid |
| `minimax/minimax-m3:free` | 4 | Unverified | 0 | Four JSON parse-path failures; raw response lost by runner |
| `mistralai/mistral-small-2603` | 4 | Unverified | 0 | Four JSON parse-path failures; raw response lost by runner |

Acceptance gate:

| Gate | Required | Observed | Result |
| --- | ---: | ---: | --- |
| API completed | 16/16 | 4 verified; 4 HTTP 500; 8 unverified parse-path failures | FAIL |
| Schema valid | 16/16 | 4/16 | FAIL |
| Model identity mismatch | 0 | 0 among recoverable responses; 8 unverified | FAIL (incomplete evidence) |
| Credential leakage | 0 | 0 | PASS |
| Manual repair | 0 | 0 | PASS |

Overall smoke verdict: **FAIL**.

PIT-13.1.B Evidence Collection remains **BLOCKED / NOT STARTED**.

Post-failure infrastructure correction:

The runner now records API and parse failures separately, preserves the raw API response when content parsing fails, and flushes every record after writing. This correction does not alter candidates, scenarios, prompt, Teaching Signal schema, temperature, scoring, or retry policy. The failed attempt was not rerun.

Candidate amendment for future execution:

- Replaced `qwen/qwen3.8-max:free` with `qwen/qwen3.7-max:free` by explicit research direction after the failed attempt.
- xKiro `/v1/models` listed `qwen/qwen3.7-max:free`.
- One non-evidence `Hello!` diagnostic returned HTTP 200 and the exact response model `qwen/qwen3.7-max:free`.
- The failed Qwen3.8 records above remain unchanged and are not combined with any future attempt.

## PIT-13.1.A Smoke Retry — Qwen3.7 Amendment

Result: **FAIL**

The complete amended manifest ran once across all 16 frozen samples with no retry, model-specific tuning, or manual repair.

| Candidate | API completed | Schema valid | Identity mismatch | Outcome |
| --- | ---: | ---: | ---: | --- |
| `qwen/qwen3.7-max:free` | 4/4 | 4/4 | 0 | PASS |
| `deepseek/deepseek-v4-pro` | 4/4 | 4/4 | 0 | PASS |
| `minimax/minimax-m3:free` | 4/4 | 1/4 | 0 | Three responses wrapped JSON in Markdown fences |
| `mistralai/mistral-small-2603` | 4/4 | 0/4 | 0 | Four responses wrapped JSON in Markdown fences |

Acceptance gate:

| Gate | Required | Observed | Result |
| --- | ---: | ---: | --- |
| API completed | 16/16 | 16/16 | PASS |
| Schema valid | 16/16 | 9/16 | FAIL |
| Model identity mismatch | 0 | 0 | PASS |
| Credential leakage | 0 | 0 | PASS |
| Manual repair | 0 | 0 | PASS |

The seven invalid responses began with a Markdown `json` code fence instead of a JSON object. The raw responses were preserved. Removing fences or accepting fenced output would alter the frozen output contract or repair model output, so no parser change was made.

Overall amended smoke verdict: **FAIL**.

PIT-13.1.B remains **BLOCKED / NOT STARTED**.

## PIT-13.1.A.1 Smoke Harness Contract Audit

Status: **COMPLETED**

### A. Serialization normalization freeze

The smoke harness now applies one deterministic, model-agnostic normalization function before `json.loads`.

Accepted forms:

- Bare JSON after leading/trailing whitespace removal.
- A full response wrapped only in one outer `json` Markdown code fence.
- A full response wrapped only in one outer generic Markdown code fence.

Forbidden repair behaviors:

- No JSON repair.
- No quote, comma, trailing-comma, key, field, or value modification.
- No extraction of JSON from prose.
- No first-brace/last-brace search.
- No model-specific handling.
- No retry or semantic repair.

Raw response preservation:

The raw API response remains stored unchanged under `raw_response`. Normalization is applied only to the text passed into `json.loads` for parsing.

### B. Scenario evidence mapping freeze

Audit result:

PIT-10, PIT-12, PIT-13.1, `experiments/pit6/`, and `experiments/pit13/` contained category-level requirements and historical smoke outputs, but no exact frozen evidence records for the four smoke scenario IDs. The four smoke instances are now frozen as a harness-contract manifest at `experiments/pit13/smoke/scenarios.json`.

Frozen scenario IDs:

- `stable_preference_001`
- `preference_drift_001`
- `user_correction_001`
- `insufficient_evidence_001`

The runner now resolves each scenario ID to non-empty evidence content and sends that evidence in the model-facing user message. It no longer sends only `PIT smoke scenario: <scenario_id>`.

Previous PIT-13.1.A result remains **FAIL** and is not overwritten.

## PIT-13.1.A.0 Runner Validation

Issue observed:

Python runner requests returned HTTP 403 while a PowerShell xKiro API request succeeded.

Root cause:

The runner bypassed xKiro's documented OpenAI-compatible client and manually constructed the HTTP request with Python `urllib`. That transport did not match the known-working OpenAI client request path and produced HTTP 403 even though the endpoint, bearer credential, payload, and model ID were otherwise aligned.

Fix applied:

Kept `XTROUTER_API_KEY` sourced from the process environment and normalized surrounding whitespace. Replaced the manual `urllib` transport with `OpenAI(api_key=..., base_url="https://api.xkiro.com/v1")`, which delegates the bearer header, JSON serialization, and `/chat/completions` request behavior to the provider-compatible client. Candidate IDs are passed unchanged.

Evidence execution status:

At PIT-13.1.A.0 validation time, no PIT evidence had been generated and smoke qualification had not started.

Validation:

- `python -m py_compile scripts/pit13/run_pit13_smoke.py`: PASS.
- One diagnostic connectivity request using `mistralai/mistral-small-2603`: HTTP 200.
- Requested and returned model IDs both remained `mistralai/mistral-small-2603`.
- The diagnostic request was not written to the PIT evidence directory and is not PIT evidence.

Required coverage:

- Stable preference
- Preference drift
- User correction
- Insufficient evidence

## Evidence collection result

BLOCKED / NOT STARTED

Required evidence coverage:

- Stable preference
- Preference drift
- Conflicting evidence
- User correction
- Rare exception
- Insufficient evidence
- Long-term consistency

## Limitations

Execution requires reproducible API access. No candidate ranking or teacher selection is performed in this milestone.

## Next step

The amended PIT-13.1.A smoke failed schema conformance. The harness contract audit is complete. Next is a PIT-13.1.A Smoke Qualification Rerun using the frozen scenario evidence manifest and deterministic fence normalization. PIT-13.1.B must not start unless that rerun passes all smoke gates.

Current amended attempt: `experiments/pit13/smoke/`.

Previous Qwen3.8 attempt: `experiments/pit13/smoke-attempt-01-qwen38-fail/`.
