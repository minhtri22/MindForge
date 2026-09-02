# Deferred Research — Continual Learning and Memory

## Historical question

P0.9 asked whether MindForge could produce a reproducible, controlled catastrophic-forgetting signal suitable for testing continual-learning mechanisms. P0.10 was conditional on that substrate and would have asked whether an explicit memory mechanism had measurable value against a plain baseline.

## Outcome

```text
P0.9 = STOP / FROZEN
P0.10 = STOP / FROZEN
```

## Why stopped

The research stopped because the bounded falsification sequence did not establish a scientifically usable substrate:

- the historical synthetic token-transition `+1/+2` task produced positive transfer rather than forgetting;
- C1, Vietnamese Wikipedia → English Wikipedia, showed only weak independent learnability under the frozen thin-slice budget and did not meet the 5% qualification gate;
- C2, history/geography → science/technology Wikipedia, also failed the learnability gate and showed positive transfer on A;
- C3, controlled contradictory natural-language mappings, was strongly learnable independently but failed valid sequential B acquisition after A; therefore A degradation could not be interpreted as demonstrated catastrophic forgetting.

No replay, EWC, custom memory or other anti-forgetting mechanism was justified by this substrate.

## What STOP means

STOP is a bounded falsification result for the Phase-0 protocols, candidate families, thresholds and compute budgets that were actually tested. MindForge will not keep altering the benchmark or invent a custom mechanism until a desired signal appears.

## What STOP does not mean

STOP does **not** mean catastrophic forgetting is absent in neural networks, continual learning is impossible, memory systems are useless, or MindForge can never use learning/memory mechanisms.

It means only that the custom research branch lacked the controlled evidence required to justify more architecture at this stage.

## Reopen conditions

A future investigation may reopen only when there is a new independent reason, such as:

- a mature open-source mechanism with reproducible evidence relevant to MindForge;
- a benchmark already demonstrating the behavior MindForge needs to measure;
- a concrete product requirement that creates measurable learning or memory value;
- a new dataset/task whose memory value is independently justified rather than selected because it happens to forget.

Reopening must be a new scoped research decision. It must not rewrite the Phase-0 STOP evidence.

## Future adoption policy

MindForge may later benchmark, port, adapt or minimally clone established open-source mechanisms without treating them as novel MindForge research. Preference order is:

```text
discover
→ understand
→ reuse or port minimally
→ benchmark
→ retain only if justified
```

Large framework dependencies, new kernel hooks, memory APIs or continual-learning abstractions are not added pre-emptively. A future mechanism must first demonstrate that ordinary composition is insufficient and that the architectural cost is justified.

## Preserved evidence

- [P0.9 frozen protocol](../../phases/phase-0-continual-protocol.md)
- [P0.9 validation/STOP evidence](../../phases/phase-0-continual-validation.md)
- [P0.9 experiment implementation](../../../experiments/phase0_continual_real.py)
- [P0.9 qualification JSON](../../../experiments/results/phase0_continual_qualification.json)
- [P0.9 final STOP record](../../../experiments/results/phase0_continual_real.json)
