# OIR-PPV Simulator Evolution Archive

This archive contains the complete simulator evolution from v0.1 → v0.13.10 for the OIR-PPV research track.

## Archive Structure

```
archive/
├── reconstruction/          # Full simulator version history
│   ├── v0.11/              # Baseline v0.11 (used as v0.1 reference)
│   ├── v0.12/
│   ├── v0.13/
│   ├── v0.13.1/
│   ├── v0.13.2/
│   ├── v0.13.3/
│   ├── v0.13.4/
│   ├── v0.13.5/
│   ├── v0.13.6/
│   ├── v0.13.7/
│   ├── v0.13.8/
│   ├── v0.13.9/
│   └── v0.13.10/           # Final version before hypothesis freeze
└── benchmarks/
    └── reconstruction_v0.1/ # v0.1 baseline for reconstruction benchmarking
        ├── seeds/          # Seed manifests
        └── (v0.11 content used as v0.1 proxy)
```

## Version History

| Version | Description |
|---------|-------------|
| v0.1 (proxy: v0.11) | Initial OIR-PPV simulator |
| v0.11 | First stable baseline |
| v0.12 | Minor update |
| v0.13 | Major revision |
| v0.13.1 - v0.13.9 | Iterative improvements |
| v0.13.10 | Final version before hypothesis freeze |

## Provenance

All versions sourced from `origin/research/oir-ppv` branch at commit `61be5747915d004bf72be718f9b6c4d401c85ad7`.

## Usage

For reconstruction validation:
```bash
python docs/research/oir-ppv/artifacts/simulator/run_replay.py --version v0.13.10
```