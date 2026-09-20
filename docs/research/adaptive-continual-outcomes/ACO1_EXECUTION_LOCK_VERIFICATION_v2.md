# ACO-1 Execution Lock v2 Verification

Status: **PASS / CLOSED**

- Lock commit: `ce5df9b2410951e6fbda427176e165910d770285`
- Lock SHA-256: `2104913295e85b66e8ef8f7bb66d7a182869d334ea2a6b2e0766f99e83787db8`
- Verification workflow run: `35511306898`
- Verifier tests: **5/5 PASS**
- Verification JSON SHA-256: `bb373c04874a0c7dbca1f311c146ace41de1cd1699cb5e78f05a4814565145e4`
- Verification artifact ID: `10605571130`
- Artifact ZIP SHA-256: `62d185f4cb3edc6a98d7ecf41a7a2b8fcf80341202e4d7789da2304a2fed9861`
- Corrected runner Git blob: `0fbafee7cfcaa2fbe6059faeead3835e74197bd5`
- Scientific implementation commit: `bd83799177839cef8948c96211abf2d7fc2f4dc4`
- Protocol SHA-256 unchanged: `a4615220a5fbe492e268bb23048ac6ec86fbb167f89eaa666141200ea16644eb`
- 40-seed manifest SHA-256 unchanged: `9673966a25f8992efbe5c6462b5b1d9e6a2d8af14436d2fb1180044198e56e91`
- Fresh seed execution during verification: **NO**
- Scientific outcome generated during verification: **NO**

Verdict:

```text
ACO1_EXECUTION_LOCK_VERIFICATION_PASS
```

The 40-seed fresh collection is eligible to retry under this exact v2 lock because attempt 1 terminated before the first fresh seed and produced no complete collection.
