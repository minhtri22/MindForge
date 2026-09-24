# MSA-1 Formal Transition Review

Status: **CLOSED**

Date: 2026-09-25

Trigger:

```text
MSA-1 PASS
ACCURACY_COARSE_LOSS_INFORMATIVE
```

This review is governance/evidence synthesis only.

No new experiment is run.
No difficulty is changed.
No predictor is fitted.
No MSA-1 gate is changed.

## 1. Question before the review

MSA-2 is explicitly conditional in the frozen roadmap.

The review must therefore decide whether the MSA-1 result creates an
independent scientific need to compare alternative pre-CPRM substrate/task
structures, or whether the next test should replicate the discovery-qualified
current-substrate classification unchanged.

## 2. Facts that control the decision

MSA-1 has already answered the current-substrate adequacy question:

```text
accuracy = globally saturated
loss     = globally informative
```

The frozen current substrate was not jointly endpoint-saturated.

The discrepancy is scientifically meaningful, but it does not by itself prove
that changing substrate structure is necessary.

## 3. Candidate transition paths

### Path A — Open MSA-2 to find a structure where accuracy becomes informative

Decision:

```text
REJECTED
```

Reason:

That would turn MSA-2 into a search for a preferred outcome and would be a
difficulty/measurement rescue of terminal accuracy.

### Path B — Open MSA-2 immediately to map structure-dependence of the
accuracy/loss discordance

Decision:

```text
NOT AUTHORIZED NOW
```

This is a scientifically coherent future question, but the current program has
not established that any downstream decision depends on knowing whether the
discordance changes across task/substrate families.

MSA-2 is conditional rather than mandatory. Opening it now would broaden the
research object before the current-substrate claim has been independently
replicated.

MSA-2 may be reconsidered only if a later formal decision identifies a concrete
scientific dependency on structure-dependence. It may never be used as
adaptive difficulty search.

### Path C — Replicate the exact MSA-1 classification on a fully fresh cohort

Decision:

```text
SELECTED
```

This is the narrowest falsifiable next step.

It tests whether:

```text
ACCURACY_COARSE_LOSS_INFORMATIVE
```

persists under the exact same:

- substrate identity;
- task order;
- A/B/C policies;
- endpoint step;
- terminal accuracy definition;
- terminal cross-entropy loss definition;
- reliability gate;
- support gate;
- accuracy classification gates;
- loss classification gates;
- joint classification matrix.

No gate or substrate change is justified before replication.

## 4. Transition decision

```text
MSA-1                         PASS / CLOSED
MSA-1 CLAIM                   ACCURACY_COARSE_LOSS_INFORMATIVE

MSA-2                         NOT AUTHORIZED
MSA-2 STATUS                  DEFERRED / CONDITIONAL ONLY

NEXT SCIENTIFIC MILESTONE     MSA-3
MSA-3 PURPOSE                 INDEPENDENT FRESH REPLICATION
MSA-3 DESIGN AUTHORIZED       YES
MSA-3 EXECUTION AUTHORIZED    NO

difficulty mutation           FORBIDDEN
new endpoint metric           FORBIDDEN
predictor fitting             CLOSED
controller                    CLOSED
KCL-7                         CLOSED
```

## 5. MSA-3 design constraints

The next admissible work is preregistration/specification only.

MSA-3 must:

1. use a completely fresh cohort disjoint from historical KCL, protected KCL,
   spent ACO-1, spent CPRM-1 and spent MSA-1 seeds;
2. preserve the exact current-substrate source identity;
3. preserve the exact terminal accuracy and terminal cross-entropy loss
   definitions;
4. preserve the exact MSA-1 classification gates and matrix;
5. preserve exact deterministic reliability requirements;
6. define replication success before fresh execution;
7. prohibit tuning between MSA-1 discovery and MSA-3 replication;
8. use an execution lock, zero-science preflight and independent lock
   verification before collection;
9. keep MSA-2, predictor fitting and controller work closed.

## 6. Replication interpretation

A successful MSA-3 replication permits MSA-4 downstream governance review.

A failure to replicate triggers mandatory convergence review.

Neither outcome automatically opens predictor training.
