# MK-1 Scientific Training Execution Audit Result v0.1

Status: **PASS / SCIENTIFIC TRAINING EXECUTION FORMALLY CLOSED**

Formal verdict:

`SCIENTIFIC_TRAINING_EXECUTION_AUDIT_PASS`

Canonical run:

- run: `35587028399`
- execution head: `063d92299ed8adf90786bea9b5bd6ad3acf23243`
- jobs: `10/10 SUCCESS`
- frozen artifacts: `10/10`

## Audit scope

This audit checks execution integrity only. It does not compare scientific outcomes between DIRECT and M1-Z and does not adjudicate H1a/H1b/H1c.

Each frozen training artifact was downloaded and inspected directly. Every artifact contains exactly:

- `run.json`
- `metrics.jsonl`
- `best.pt`
- `latest.pt`

The immutable training-input bundle `10629399106` was also inspected so each executed sample sequence could be compared row-by-row with the frozen schedule.

## PASS invariants

All 10 jobs satisfy all of the following:

- artifact ZIP SHA-256 matches GitHub frozen digest;
- `run.json.status = COMPLETE`;
- exactly `5000` metrics rows with steps `1..5000`;
- exact parameter contract for the arm;
- exact processed input-token total `6,457,260`;
- exact frozen schedule SHA-256;
- every executed `sample_ids` row equals the corresponding frozen schedule row;
- every per-step and cumulative input-token count equals the frozen schedule;
- all executed sample IDs are in frozen TRAIN namespace `7101000..7102999`;
- tokenizer SHA-256 equals `e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829`;
- paired B0 state provenance equals the frozen seed-specific state hash;
- learning-rate values match the locked warmup + cosine schedule at all 5000 steps;
- validation score appears at exactly `250,500,...,5000` and nowhere else;
- all validation scores are finite;
- all training losses are finite;
- `run.json.best_step` equals the earliest validation step attaining that job's maximum validation score;
- `best.pt` metadata matches that earliest maximum selector;
- `latest.pt.step = 5000` and preserves the same best-step metadata;
- no early stopping occurred;
- no confirmatory/pristine file is present in the training artifact.

Best-checkpoint steps, recorded only to verify selector semantics:

| Seed | DIRECT | M1-Z |
|---:|---:|---:|
| 71001 | 3250 | 5000 |
| 71002 | 3000 | 3500 |
| 71003 | 5000 | 5000 |
| 71004 | 5000 | 4750 |
| 71005 | 3750 | 3000 |

No cross-arm interpretation is made here.

## Execution-head provenance

Comparison of pre-trigger HEAD `d049617281bd0f120e55c5ef11e592424ef3fec8` to execution head `063d92299ed8adf90786bea9b5bd6ad3acf23243` shows exactly one added file:

`model_kernel/mk1/SCIENTIFIC_TRAINING_TRIGGER_v0.1.md`

At the execution head, the locked Git blobs for trainer, execution wrapper, workflow, contracts, modeling, losses, metrics and recomposition all match the execution lock exactly.

Therefore no scientific code/config drift occurred between execution-lock PASS and canonical training.

## Confirmatory isolation

The immutable training bundle has no confirmatory/pristine content.

The training workflow at the execution head downloads only that bundle.

Training artifacts contain no confirmatory/pristine files, and every logged training sample ID lies in the TRAIN namespace.

Result:

**PASS**

## Formal closure

Scientific training execution is now formally closed:

`SCIENTIFIC_TRAINING_EXECUTION_AUDIT_PASS`

This establishes that the 10 frozen checkpoints/results are admissible scientific evidence under the preregistered execution contract.

It does **not** establish H1a, H1b or H1c.

The next authorized stage is outcome adjudication in frozen order:

`H1a -> H1b -> H1c`

No retraining, seed replacement, schedule modification, threshold change, checkpoint reselection, or confirmatory access is authorized by this closure.
