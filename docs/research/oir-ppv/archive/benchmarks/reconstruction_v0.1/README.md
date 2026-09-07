# Benchmarks Archive - v0.1 Reconstruction

Contains the v0.1 baseline simulator (using v0.11 as proxy) for reconstruction benchmarking.

## Purpose

Provide a frozen baseline for comparing simulator evolution v0.1 → v0.13.10.

## Structure

- `seeds/` - Seed manifests for reproducible runs
- `v0.11_baseline/` - Baseline v0.11 simulator (used as v0.1 proxy)
- `v0.13.10_reconstruction/` - Target reconstruction version
- `benchmark_protocol.md` - Benchmark protocol
- `provenance.json` - Provenance tracking

## Usage

```bash
# Run baseline benchmark
python run_benchmark.py --version v0.11_baseline

# Run reconstruction benchmark
python run_benchmark.py --version v0.13.10_reconstruction
```
