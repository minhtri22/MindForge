# MindForge + sol_recon — Replay Anti-Forgetting Ablation

## Scope

Same sandbox neural student, same teacher lessons, same train/held-out split, seed, N10 update budget, learning rate and batch size. PPF remains excluded. The only experimental change is the N10 sampling policy.

## Retention baseline

At N5, before lessons 6–10 are introduced, the first five behavior families score **10/15 = 66.7%** on held-out prompts. After ordinary N10 training, those same five families fall to **5/15 = 33.3%**. This is the observed forgetting/interference to address.

## Results

| N10 policy | Overall | Old-5 retention | New-5 learning | vs original overall | vs original old retention |
|---|---:|---:|---:|---:|---:|
| Original random sampling over all 10 families | 14/30 = 46.7% | 5/15 = 33.3% | 9/15 = 60.0% | — | — |
| Explicit replay 4 old / 4 new per batch | 15/30 = 50.0% | 5/15 = 33.3% | 10/15 = 66.7% | +3.3 pp | 0.0 pp |
| Retention-weighted replay 6 old / 2 new per batch | 14/30 = 46.7% | 4/15 = 26.7% | 10/15 = 66.7% | 0.0 pp | -6.7 pp |

## Verdict

**REPLAY_ONLY_INSUFFICIENT_FOR_ANTI_FORGETTING.** Balanced replay slightly improves total/new-task performance but does not recover old-task retention. Increasing old-task replay to 75% makes retention worse. Replay is therefore preserved only as an ablation/negative result and is not promoted into the default MindForge + sol_recon architecture.

## Diagnostic finding

There are at least two interference sources:

1. **Neural interference:** old families with the correct retrieved lesson still switch to newer labels after N10.
2. **Memory-retrieval interference:** at least one old frontier prompt, `Find the latest global market developments.`, retrieves the newer `latest correction` lesson because of the token `latest`, steering the model toward `BLUE`. Replay cannot fix a wrong lesson being injected at inference time.

## Next controlled experiment

Do not merely increase replay ratio. Separately ablate:

- replay + **retention regularization / teacher-logit distillation from the N5 snapshot** to constrain neural drift; and
- retrieval conflict handling in lightweight memory, without changing PPF.

These must remain independent treatments so gain can be attributed to neural retention versus memory retrieval quality.
