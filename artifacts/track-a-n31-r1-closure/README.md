# N3.1-R1 Git-native closure bundle

Purpose: allow a remote Windows agent to reconstruct the canonical Track-A Benchmark v1 R1 materializer directly from Git without needing ChatGPT sandbox files.

## Source reconstruction

Canonical source artifact from the original closure bundle:

- `scripts/materialize_track_a_v1_r1.py`
- original Linux/sandbox SHA256: `41c8e61a04ab131d1060004ebcef7b014f7655e5af8c75e6ff8b10e1fb9ffa8d`

The source is stored here as three UTF-8 line-safe parts:

- `generator.linepart00`
- `generator.linepart01`
- `generator.linepart02`

Reconstruct from Git blobs rather than PowerShell text concatenation so checkout line endings cannot alter source bytes:

```powershell
python - <<'PY'
import subprocess
from pathlib import Path
parts = [
    'artifacts/track-a-n31-r1-closure/generator.linepart00',
    'artifacts/track-a-n31-r1-closure/generator.linepart01',
    'artifacts/track-a-n31-r1-closure/generator.linepart02',
]
out = Path('scripts/materialize_track_a_v1_r1.py')
with out.open('wb') as f:
    for part in parts:
        f.write(subprocess.check_output(['git','show',f'HEAD:{part}']))
PY
```

The reconstructed pre-fix generator must hash to:

`41c8e61a04ab131d1060004ebcef7b014f7655e5af8c75e6ff8b10e1fb9ffa8d`

## Windows LF determinism amendment

A remote Windows qualification run discovered a cross-platform reproducibility defect: the semantic R1 generator wrote `schema.json` and `manifest.json` with `Path.write_text(...)` without explicitly setting `newline="\n"`. Linux produced the frozen LF bytes, while Windows converted those two files to CRLF. The benchmark truth and JSON content were unchanged, but the frozen schema hash failed on Windows.

Apply the repository-provided deterministic fix:

```powershell
python artifacts\track-a-n31-r1-closure\apply_windows_lf_fix.py
```

The patched cross-platform generator must hash to:

`d9f2bf58b102d2cf9a19bba4468adc34de148682245e5e550bdbc6c18d6514b9`

The amendment only adds `newline="\n"` to the two `schema.json` / `manifest.json` writes and rewrites the generator itself with LF. It does not modify benchmark truth, templates, labels, scoring, quotas, RVE/TUE, or held-out semantics.

## Canonical benchmark reconstruction

Run:

```powershell
python scripts\materialize_track_a_v1_r1.py
```

Expected frozen artifact SHA256 values:

- calibration.jsonl: `7c2e135fc5c405b298d4b460bbf482cfba4c4d180acbfd9fedb7650f131384bb`
- development.jsonl: `2a1b035d444bfb144891778590a7eab5603da04d221cfdc6e1682c4e2374ea42`
- test.jsonl: `3d220e1b5b0b98d04aa3f7e7eebf83008faf344155a94a571ee28f4755ba12cf`
- schema.json: `6869e437e8c8a1b935be7ed3d6650977e0dc09a8531dbbdea191ca832d748feb`
- human-review-sample.jsonl: `d81c29d6bd549d756cdac055c3e43c82579942871f0c9d6f942c136d831cf693`

Canonical manifest SHA256 produced by the patched generator:

- manifest.json: `09660d9e3b1d294fa82fbde702083d0d818431692a55f30387c78adfc697a210`

Original closure tarball SHA256 from sandbox provenance:

`019287592b580925f7fe7c7250bceec632d977bc4029314be6c75eb138bb9d24`

This Git-native bundle intentionally does not publish raw held-out truth. It publishes the exact R1 source plus the minimal Windows determinism amendment needed to reconstruct the frozen artifacts and verify their frozen hashes locally.

Do not use the older `scripts/materialize_track_a_v1.py` as R1 provenance authority until it has been replaced by a thin compatibility wrapper around the patched R1 generator.
