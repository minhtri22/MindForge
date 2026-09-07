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

Runner inspection found the request structure aligned with the expected xKiro API contract. The runner did not normalize the externally supplied API key value before constructing the Authorization header, which could preserve accidental surrounding whitespace from the process environment.

Fix applied:

Normalized `XTROUTER_API_KEY` after reading it from the process environment by trimming surrounding whitespace before request construction.

Evidence execution status:

Unchanged. No PIT evidence generated. Smoke qualification has not started.

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
