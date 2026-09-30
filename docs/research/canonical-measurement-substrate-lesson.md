# Canonical Measurement Lesson — Current Continual-Learning Substrate

Status: **REPLICATED, SCOPE-BOUNDED METHODOLOGY LESSON**

Source evidence:
- discovery: MSA-1
- independent replication: MSA-3
- branch: `research/measurement-substrate-adequacy@64138ab9cb09dcb56a387d3b1f500063eff8302d`
- MSA-3 verdict: `REPLICATION_CONFIRMED`
- replicated classification: `ACCURACY_COARSE_LOSS_INFORMATIVE`

## Replicated finding

Within the frozen current synthetic continual-learning substrate:

~~~text
terminal argmax accuracy
  informative = false
  saturated   = true

terminal cross-entropy loss
  informative = true
  saturated   = false
~~~

The discovery and replication used independent fresh 72-seed cohorts under the same frozen classification rule.

## What MindForge may inherit

For future studies on the **same or demonstrably equivalent measurement regime**:

- terminal cross-entropy loss may be proposed as a high-resolution continuous endpoint candidate;
- terminal accuracy may remain a correctness sentinel / descriptive diagnostic;
- task difficulty should not be increased merely to make terminal accuracy vary when another endpoint already retains reproducible information.

## What MindForge may not infer

This evidence does **not** establish:

- that CE loss is universally the best endpoint;
- that accuracy should disappear from evaluation;
- that all continual-learning substrates share this geometry;
- that observable state predicts policy-conditioned loss response;
- that a predictor or controller is justified;
- that KCL/CPRM/CLRM mechanisms should enter core.

Any future substrate with materially different task, model, endpoint, or intervention structure must independently qualify its measurement regime.

## Portfolio consequence

This lesson enters canonical research methodology as measurement guidance only. The MSA research program itself remains closed/converged.
