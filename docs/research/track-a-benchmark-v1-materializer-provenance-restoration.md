# Track-A Benchmark v1 Materializer Provenance Restoration

## Executive result

The N3.1-R1 Track-A Benchmark v1 materializer provenance was restored as a reproducibility/provenance repair only.

## Prior stops

Initial N3.R1-B stop: correct.

Second N3.R1-B stop: correct.

The benchmark semantic truth was not invalidated by either stop. The first stop exposed that the public materializer was stale. The second stop exposed a Windows byte-level reproducibility defect in the R1 generator output for `schema.json` and `manifest.json`.

## Root causes

Root cause #1: the repository public entrypoint `scripts/materialize_track_a_v1.py` was a stale pre-R1 materializer and could generate non-canonical benchmark artifacts.

Root cause #2: the reconstructed R1 generator used `Path.write_text(...)` for `schema.json` and `manifest.json` without explicitly forcing `newline="\n"`. Linux produced the frozen LF bytes; Windows produced CRLF bytes for those two files. The semantic schema object was unchanged, but the Windows SHA-256 did not match the frozen canonical hash.

Windows symptom: `schema.json` hash `f29588392a8f526aa79c13057fbe841f26919d4fd4bdd555c848c519346b2110`.

## Canonical source

Recovered from:

```text
artifacts/track-a-n31-r1-closure/
```

Original reconstructed generator SHA-256:

```text
41c8e61a04ab131d1060004ebcef7b014f7655e5af8c75e6ff8b10e1fb9ffa8d
```

Canonical generator after deterministic LF fix:

```text
d9f2bf58b102d2cf9a19bba4468adc34de148682245e5e550bdbc6c18d6514b9
```

The patched source is now the cross-platform canonical materializer implementation for R1. The public historical entrypoint delegates to it and does not retain duplicate generation logic.

## Canonical output hashes

```text
calibration.jsonl
7c2e135fc5c405b298d4b460bbf482cfba4c4d180acbfd9fedb7650f131384bb

development.jsonl
2a1b035d444bfb144891778590a7eab5603da04d221cfdc6e1682c4e2374ea42

test.jsonl
3d220e1b5b0b98d04aa3f7e7eebf83008faf344155a94a571ee28f4755ba12cf

schema.json
6869e437e8c8a1b935be7ed3d6650977e0dc09a8531dbbdea191ca832d748feb

human-review-sample.jsonl
d81c29d6bd549d756cdac055c3e43c82579942871f0c9d6f942c136d831cf693

manifest.json
09660d9e3b1d294fa82fbde702083d0d818431692a55f30387c78adfc697a210
```

## Scope confirmation

```text
benchmark truth changed: NO
labels changed: NO
templates changed: NO
scorer changed: NO
RVE/TUE changed: NO
semantic review reopened: NO
```

This restoration changes provenance and cross-platform reproducibility only.
