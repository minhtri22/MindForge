# OIR-PPV Audit Fix-1 — Provenance Status

Date: 2026-09-07
Branch: research/oir-ppv

## Purpose

This document separates OIR-PPV artifacts into four provenance classes:

1. VERIFIED ARTIFACT — exists in repository and can be inspected directly.
2. RECONSTRUCTED ARTIFACT — artifact structure exists but requires execution validation.
3. DESIGN / SPEC ONLY — hypothesis, protocol, or intended architecture; not experimental evidence.
4. PENDING EXECUTION — requires runtime execution and raw output.

The goal is to prevent accidental promotion of design documents into research evidence.

---

# Provenance Matrix

| Component | Status | Notes |
|---|---|---|
| research/oir-ppv branch | VERIFIED ARTIFACT | Repository branch exists |
| Research protocol documents | VERIFIED ARTIFACT | Documentation artifacts |
| Failure case definitions S11-A/B/C | VERIFIED ARTIFACT | Frozen experiment descriptions |
| Seed registry | VERIFIED ARTIFACT | Seed provenance exists |
| Replay runner | VERIFIED ARTIFACT | Generates execution records; does not prove outcomes |
| GitHub Actions workflow | VERIFIED ARTIFACT | Execution infrastructure |
| Execution schema | VERIFIED ARTIFACT | Output contract |
| Simulator lineage v0.11-v0.13.10 | REQUIRES AUDIT | Must verify executable source for every version |
| Simulator configs | REQUIRES AUDIT | Must verify frozen parameters |
| Historical replay execution | PENDING EXECUTION | No raw runtime outputs yet |
| Comparison report | PENDING EXECUTION | Must be generated from raw outputs |

---

# Current Research Claim Level

Current valid claim:

> OIR-PPV has a documented hypothesis evolution and a reproducibility framework.

Current invalid claim:

> OIR-PPV v0.13.10 has been experimentally validated against v0.11 failures.

That claim requires:

- executable simulator versions
- frozen environment
- replay execution
- raw outputs
- independent verification

---

# Required Next Gate

OIR-PPV v0.13.11 Historical Replay Execution:

1. Verify simulator source lineage.
2. Execute v0.11 and v0.13.10 with identical seeds.
3. Store raw execution artifacts.
4. Generate comparison report.
5. Only then update validation status.
