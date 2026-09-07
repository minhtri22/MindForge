# PIT-13.1 Candidate API Evidence Collection

Status:

NOT STARTED

## Execution methodology

PIT-13.1 follows the frozen PIT-10 teaching signal contract and requires two phases:

- PIT-13.1.A Smoke Qualification
- PIT-13.1.B Evidence Collection

The execution layer is xKiro API. Credentials remain external and are not stored in research artifacts.

## Smoke qualification result

NOT STARTED

## PIT-13.1.A.0 Runner Validation

Issue observed:

Python runner requests returned HTTP 403 while a PowerShell xKiro API request succeeded.

Root cause:

The runner bypassed xKiro's documented OpenAI-compatible client and manually constructed the HTTP request with Python `urllib`. That transport did not match the known-working OpenAI client request path and produced HTTP 403 even though the endpoint, bearer credential, payload, and model ID were otherwise aligned.

Fix applied:

Kept `XTROUTER_API_KEY` sourced from the process environment and normalized surrounding whitespace. Replaced the manual `urllib` transport with `OpenAI(api_key=..., base_url="https://api.xkiro.com/v1")`, which delegates the bearer header, JSON serialization, and `/chat/completions` request behavior to the provider-compatible client. Candidate IDs are passed unchanged.

Evidence execution status:

Unchanged. No PIT evidence generated. Smoke qualification has not started.

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

NOT STARTED

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

PIT-13.1.A Smoke Qualification after execution access validation.

Execution artifact location (after smoke execution): `experiments/pit13/smoke/`.
