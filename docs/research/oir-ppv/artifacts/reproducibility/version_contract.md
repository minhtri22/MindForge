# OIR-PPV Simulator Version Contract

Every simulator version must declare:

```yaml
version:
hypothesis:
architecture_changes:
known_failure:
metrics:
seed_policy:
```

Rules:

- Older versions must not contain future fixes.
- New versions may add validation layers only after documented failure discovery.
- Replay comparisons must change architecture only, not seed or environment.
