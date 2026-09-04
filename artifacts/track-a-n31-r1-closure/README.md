# N3.1-R1 Git-native closure bundle

Purpose: allow a remote Windows agent to reconstruct the canonical Track-A Benchmark v1 R1 materializer directly from Git without needing ChatGPT sandbox files.

Canonical source artifact in the original closure bundle:

- `scripts/materialize_track_a_v1_r1.py`
- SHA256: `41c8e61a04ab131d1060004ebcef7b014f7655e5af8c75e6ff8b10e1fb9ffa8d`

The source is stored here as three UTF-8 line-safe parts:

- `generator.linepart00`
- `generator.linepart01`
- `generator.linepart02`

Reconstruct on Windows PowerShell from repository root:

```powershell
$parts = @(
  'artifacts\track-a-n31-r1-closure\generator.linepart00',
  'artifacts\track-a-n31-r1-closure\generator.linepart01',
  'artifacts\track-a-n31-r1-closure\generator.linepart02'
)
Get-Content $parts -Raw | Set-Content -NoNewline -Encoding utf8NoBOM scripts\materialize_track_a_v1_r1.py
Get-FileHash scripts\materialize_track_a_v1_r1.py -Algorithm SHA256
```

Expected generator SHA256:

`41c8e61a04ab131d1060004ebcef7b014f7655e5af8c75e6ff8b10e1fb9ffa8d`

Then run the canonical generator:

```powershell
python scripts\materialize_track_a_v1_r1.py
```

Expected frozen artifact SHA256 values:

- calibration.jsonl: `7c2e135fc5c405b298d4b460bbf482cfba4c4d180acbfd9fedb7650f131384bb`
- development.jsonl: `2a1b035d444bfb144891778590a7eab5603da04d221cfdc6e1682c4e2374ea42`
- test.jsonl: `3d220e1b5b0b98d04aa3f7e7eebf83008faf344155a94a571ee28f4755ba12cf`
- schema.json: `6869e437e8c8a1b935be7ed3d6650977e0dc09a8531dbbdea191ca832d748feb`
- human-review-sample.jsonl: `d81c29d6bd549d756cdac055c3e43c82579942871f0c9d6f942c136d831cf693`

Original closure tarball SHA256 from sandbox provenance:

`019287592b580925f7fe7c7250bceec632d977bc4029314be6c75eb138bb9d24`

This Git-native bundle intentionally does not publish raw held-out truth. It publishes the exact canonical generator needed to deterministically reconstruct the frozen artifacts and verify the frozen hashes locally.

Do not use the older `scripts/materialize_track_a_v1.py` as proof of R1 provenance until it has been replaced with a thin compatibility wrapper around the reconstructed R1 generator.
