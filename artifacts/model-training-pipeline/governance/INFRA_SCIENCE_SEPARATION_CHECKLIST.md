# Infrastructure / Science Separation QA Checklist

Status: PASS  
Unresolved findings: **0**

## Initial review findings repaired

- [x] QA-01 — Historical M6R2 opening artifact could be mistaken for current canonical policy. Repaired by explicit in-folder supersession artifact + RFD lineage entry.
- [x] QA-02 — README read-order still ended at §22. Repaired to §23.

## Final invariants

- [x] Historical M6 and M6R verdicts remain immutable.
- [x] RFD-C1 root-cause finding remains unchanged.
- [x] Infrastructure failure is explicitly prevented from setting a scientific FAIL.
- [x] Infrastructure repair budget is separated from scientific attempt/repair budget.
- [x] Science design may proceed while infrastructure is unresolved.
- [x] Runtime execution still requires an exact qualified-infrastructure binding.
- [x] Reusable infrastructure qualification has a frozen scope tuple.
- [x] A single consolidated binding check replaces repeated micro-gates when scope is unchanged.
- [x] Prior M6R2 decision is superseded only where it misclassified runtime repair as scientific intervention.
- [x] q4_0 -> f16/default is classified as runtime-adapter repair, not a scientific treatment.
- [x] Enabling flash-attention is not silently authorized.
- [x] M6R2 keeps Q4, Modelfile, fixtures, generation contract, comparator, parity and reasoning semantics frozen.
- [x] OWRQ is explicitly non-scientific and uses a scientific firewall.
- [x] OWRQ qualification cannot reinterpret M6/M6R outcomes.
- [x] M6R2 execution is not authorized by this reframe.
- [x] M7 and bulk training remain closed.
