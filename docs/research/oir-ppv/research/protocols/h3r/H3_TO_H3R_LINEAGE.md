# H3 -> H3R Protocol Lineage

## Identity

```text
hypothesis_id: H3R
protocol_id: OIR-PPV-H3R
protocol_version: v1.0
relation_to_historical_h3: REVISED_SUCCESSOR
supersedes_protocol_semantics: true
supersedes_historical_evidence: false
```

## 1. What historical H3 tested

Historical H3 tested whether the candidate representation/policy was less sensitive to selected nuisance interventions than the frozen L0/PCA reference while retaining predictive utility. The decisive comparison used paired factual/intervened samples, task degradation, a frozen nuisance-leakage proxy, and factual utility.

The selected historical targets were `background_noise` in ENV-1, `occlusion` in ENV-2, and `spurious_feature` in ENV-4. ENV-3 was retained as inapplicable because the selected intervention changed `Y` and task labels.

## 2. Historical protocol/version

- protocol: `benchmark/M3_PROTOCOL.md`
- identity: `M3-Protocol-v1.0`
- SHA256: `f7df21e8a0d24c4c9ddb5a5c504cca9c7d3a7a2c89fd7c4bef876da2d0f58e3a`
- reference benchmark: `EXP-LRN-001`
- accepted evidence authority: `correction_v3`
- QA authority: `QA_REPORT_HANDOFF_011_H3_v3.md`

## 3. Historical H3 verdict

`CLOSED_WITH_LIMITS / NOT_SUPPORTED`.

All tested L1-L4 adapted/surrogate configurations failed the frozen H3 success rule relative to L0/PCA within the target-specific tested scope. The historical result remains preserved.

## 4. What is incomplete under Formal Spec v1.0

The following items are incomplete for future use under Formal Spec v1.0. They do not retroactively invalidate H3:

1. The historical nuisance concept was target-specific and did not provide a full observation-noise family contract `N_delta`, sampling distribution `q_eta`, or realized-shift validator.
2. ENV-3 exposed the need to separate observation noise from variables that change the causal target/mechanism.
3. Representation lifecycle/scope and allowed post-train inputs were not frozen using the Formal v1.0 lifecycle contract.
4. Split-unit semantics were inherited from the benchmark rather than declared with the Formal v1.0 split contract.
5. Metric entries did not use the complete Formal v1.0 metric registry fields, including estimand, orientation, identification basis, aggregation, uncertainty, and acceptance rule.
6. Representation-distance stability was scale-sensitive and is not suitable as the primary revised robustness criterion.
7. The adapted leakage probe is useful only as a diagnostic unless a shared-probe or system-functional equivalence contract is frozen.
8. Formal v1.0 test-lock, component-wise cost, and uncertainty-aware Pareto contracts were not part of historical H3.

## 5. What H3R revises

H3R asks whether a frozen candidate preserves task and/or interventional performance under a predeclared **observation-noise** family that preserves the task mechanism better than a frozen baseline, while retaining clean utility.

H3R explicitly separates:

```text
eta   = observation noise
Z_e   = environment / causal condition
S_t   = state
I_M   = mechanism representation
```

It adds Formal v1.0 contracts for representation lifecycle, mechanism identity, shift class, split unit, observation-noise support, metrics, evidence/identification, statistics, test lock, and claim boundary.

## 6. Reusable parts from H3

- L0/PCA as the historical primary comparator candidate for the revised baseline freeze;
- L1-L4 learner identities and fidelity labels as historical candidate lineage;
- environment generators and known-SCM provenance where they satisfy the new mechanism/noise contract;
- paired factual/perturbed sample construction pattern;
- retained-utility guard concept;
- negative-result lessons, especially ENV-3 inapplicability;
- seed set as a design input, subject to H3R freeze rather than automatic inheritance.

## 7. Parts that must not be reused as H3R evidence

- H3 task-degradation values;
- H3 leakage values;
- H3 aggregate verdicts;
- historical thresholds as automatic H3R thresholds;
- historical nuisance interventions that fail the revised observation-noise mechanism-preservation contract;
- historical test access as a substitute for a new H3R test lock.

## 8. Does H3R inherit H3 evidence?

**NO.** H3 evidence is design lineage and historical evidence only. H3R starts with `evidence_status: NONE_YET`.

## 9. Does H3R supersede H3 semantics?

**YES**, for future revised robustness work under Ontology v1.0 + Formal Spec v1.0.

## 10. Does H3R supersede historical H3 evidence?

**NO.** Historical H3 remains permanently attached to its frozen protocol and claim boundary.

