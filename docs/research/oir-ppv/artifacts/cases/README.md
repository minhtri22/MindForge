# OIR-PPV Failure Case Registry

This directory contains frozen failure-case artifacts used by historical replay.

Contract:

```
case_id -> JSON artifact -> replay runner
```

Each case file must contain:

```json
{
  "id": "S11-X",
  "seed": 0,
  "attack": {
    "type": "example"
  }
}
```

Case identifiers are passed explicitly to the replay runner:

```
--case S11-X
```

The runner resolves the identifier through this registry. No hidden defaults are allowed.
