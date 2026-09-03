# PPF-L3 Benchmark Artifact Layout

Status: **FROZEN LAYOUT PLAN / NO BENCHMARK ARTIFACTS GENERATED**

The layout separates method-visible data from evaluator-only truth and protected final-test inputs. It is a future execution contract, not an implementation.

## 1. Visibility classes

Every artifact belongs to exactly one operational visibility class.

```text
PUBLIC / METHOD-VISIBLE
EVALUATOR-ONLY
DEVELOPMENT-ONLY
```

`PUBLIC / METHOD-VISIBLE` means a future recognizer may inspect it during the relevant benchmark phase. `EVALUATOR-ONLY` contains truth, expected answers, identifiability, protected seeds, or family metadata. `DEVELOPMENT-ONLY` may expose additional debugging information and cannot be reused as final-held-out evidence.

## 2. Planned repository/runtime tree

```text
benchmarks/ppf_l3/
  VERSION                                  # PUBLIC
  README.md                                # PUBLIC

  specs/
    public_execution_contract.json         # PUBLIC
    public_case_schema.json                # PUBLIC
    dev_scenario_registry.json             # DEVELOPMENT-ONLY
    validation_policy.json                 # PUBLIC

  generated/
    dev/
      cases/
        <opaque-case-id>/
          history.json                     # PUBLIC/METHOD-VISIBLE for DEV
          checkpoints.json                 # PUBLIC checkpoint request metadata only
    validation/
      cases/
        <opaque-case-id>/
          history.json                     # METHOD-VISIBLE during validation
          checkpoints.json                 # METHOD-VISIBLE, no expected answers
    final/
      cases/
        <opaque-case-id>/
          history.json                     # METHOD-VISIBLE only when final evaluation opens
          checkpoints.json                 # METHOD-VISIBLE, no expected answers

  evaluator/
    dev/
      truth/<opaque-case-id>.json           # DEVELOPMENT-ONLY
      expected/<opaque-case-id>.json        # DEVELOPMENT-ONLY
    validation/
      truth/<opaque-case-id>.json           # EVALUATOR-ONLY until policy exposes it
      expected/<opaque-case-id>.json        # EVALUATOR-ONLY

  manifests/
    public_benchmark_manifest.json          # PUBLIC, opaque/non-semantic metadata only
    dev_manifest.json                       # DEVELOPMENT-ONLY
    validation_manifest.json                # EVALUATOR-ONLY during validation
    pair_public_contract.json               # PUBLIC pair semantics, not protected instances

  reports/
    generator_qa.json                       # PUBLIC after generator freeze, scrubbed of final secrets
    oracle_qa.json                          # PUBLIC summary; protected details withheld
    dev_dataset_summary.json                # PUBLIC/DEVELOPMENT
    validation_dataset_summary.json         # policy-dependent, no protected truth leakage
```

Protected final evaluator inputs are intentionally **outside the public Git repository**:

```text
<evaluator-private-root>/ppf-l3-benchmark-v1/
  final/
    secret_scenario_specs.json
    secret_seed_manifest.json
    split_manifest.json
    pair_instances.json
    truth/
      <opaque-case-id>.json
    expected/
      <opaque-case-id>.json
    identifiability/
      <opaque-case-id>.json
    structural_holdouts.json
    artifact_hashes.json
    provenance.json
```

This private root is generated/retained locally or in another access-controlled evaluator store after separate authorization. It is not implemented by this planning task.

## 3. Method-visible case contract

A future case directory may expose only:

```text
opaque case_id
visible L2-compliant history
checkpoint IDs/times or prefix requests needed to run evaluation
public benchmark version/interface metadata
```

It must not expose:

```text
scenario family
truth type/status
positive/negative label
identifiability
expected answer
behavior/observation seeds
counterfactual pair membership when revealing it could leak semantics
structural-holdout membership
change-point truth
correction/deletion expected state
```

## 4. Evaluator-only truth contract

Evaluator-only artifacts may contain:

```text
latent truth
truth configuration
opportunity process provenance
behavior realization provenance
observation corruption provenance
expected answers by checkpoint
identifiability by unit/checkpoint
scenario-family/difficulty labels
seed provenance
counterfactual pair identity
structural/adversarial holdout identity
metric evaluation-unit registry
```

These artifacts are never input to a recognizer.

## 5. Planned machine-readable manifests

### Public benchmark manifest

Contains only non-semantic information needed to locate method-visible cases:

```text
benchmark_version
case_id
split availability/status
history path
checkpoint request path
content hashes
public schema/interface version
```

### Evaluator manifest

Contains:

```text
case_id
person_id
split
truth_configuration_ref
scenario-family refs
behavior seed
observation seed
difficulty axes
checkpoint IDs
evaluation-unit IDs
counterfactual pair instance
holdout membership
truth/expected-answer paths
```

### Pair manifest

Contains evaluator-only controlled/held-constant field declarations and semantic hashes proving isolation.

## 6. Opaque identity rules

Allowed example:

```text
case-a91f72
person-18d2
unit-3b0c
```

Forbidden examples:

```text
fake-drift-03
no-pattern-sparse-07
relationship-hidden-case
post-delete-case
```

Opaque identifiers may be deterministic for reproducibility but their derivation must not contain readable family/status/seed semantics.

## 7. Canonical JSON and hashes

All machine-readable benchmark artifacts use canonical semantic JSON for QA/reproducibility. The future implementation must define a deterministic canonicalization before generator freeze.

Manifests record hashes at freeze stages so that:

```text
same version + same registered inputs -> same semantic artifact hashes
```

Formatting-only differences must not masquerade as semantic changes.

## 8. Freeze-stage provenance

Each stage records:

```text
benchmark version
MindForge git commit
frozen protocol/plan commit refs
generator source commit after authorization
schema versions
artifact hashes
QA report hashes
creation timestamp
```

Stages:

```text
PLAN FROZEN
GENERATOR FROZEN
DEV DATASET FROZEN
VALIDATION DATASET FROZEN
FINAL TEST FROZEN
```

No stage may silently mutate artifacts from a previous freeze.

## 9. Public-repository boundary

Because `minhtri22/MindForge` is public, v1 FINAL_TEST evaluator truth/seeds/structural parameterization must not be committed to it before final evaluation is retired.

Chosen strategy:

```text
public repo:
  protocol + plan + future generator + public interfaces + DEV artifacts

private evaluator store:
  final secret specs/seeds/truth/answers/identifiability/holdout mapping
```

The private store must record public-repo commit provenance and hashes so final evidence remains reproducible/auditable by the evaluator.

After final-test truth is published, that set is considered exposed and cannot support a fresh confirmatory claim.

## 10. Version discipline

Initial benchmark identifier:

```text
ppf-l3-benchmark/v1
```

After exposure, changing any of the following requires a new version:

```text
truth semantics
scenario/evaluation-unit semantics
metric semantics
oracle logic
protected final cases
structural holdout design
```

Implementation bug fixes before final-test freeze may remain within v1 only if documented, QA rerun, and no recognizer result was used to select the fix.

## 11. Report layout

Future generator execution reports must include at least:

```text
dataset_summary.json
  persons/configs/histories/checkpoints/events/units
  split totals
  regime totals
  positive/negative/abstention balance
  identifiability balance
  family coverage
  pair coverage

generator_qa.json
  schema/truth/opportunity/behavior/observation/seed/pair/leakage checks

oracle_qa.json
  checkpoint/lifecycle/identifiability/mutation checks

split_leakage_qa.json
  person/config/case/holdout leakage checks
```

No recognizer result belongs in these generator/oracle reports.

## 12. Layout gate

```text
method-visible and evaluator-only artifacts separable: PASS
final truth absent from public repo before evaluation: PASS by design
opaque IDs required: PASS
protected split manifests separated: PASS
freeze-stage provenance defined: PASS
benchmark version discipline defined: PASS
no recognizer-specific artifact format introduced: PASS
```
