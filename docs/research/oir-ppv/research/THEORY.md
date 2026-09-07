# OIR-PPV Theory

## 1. Problem Definition

An environment produces observations:

\[
E=(S,A,Y,Z,N)
\]

where:

- \(S\): system state,
- \(A\): action or intervention variable,
- \(Y\): target outcome,
- \(Z\): context variable,
- \(N\): nuisance variable.

The objective is to learn a representation:

\[
I=f(E)
\]

that captures stable structure while reducing dependence on nuisance variation.

## 2. Invariant Representation

The desired property is that the predictive relationship remains stable across environments:

\[
P(Y|I,Z_i) \approx P(Y|I,Z_j)
\]

for different contexts \(Z_i,Z_j\).

Shortcut resistance is evaluated by measuring dependence between invariant representation and nuisance factors:

\[
I \perp N
\]

## 3. Generation Hypothesis

OIR-PPV extends evaluation from representation quality to manifestation generation.

The generator is defined as:

\[
X_{new}=G(I,Z_{new},N)
\]

The generated manifestation must preserve the invariant mechanism while allowing controlled context variation.

## 4. Intervention Validation

The benchmark uses a structural causal model:

\[
SCM=(U,V,F)
\]

and evaluates intervention stability:

\[
P(Y|do(A),I)
\]

across environments.

## 5. Core Evaluation Metrics

### Generalization

\[
Perf(I,Z_{new}) > Perf(Baseline,Z_{new})
\]

### Causal Stability

Compare intervention outcomes under controlled changes:

\[
\Delta_{causal}=P(Y|do(A),I,Z_1)-P(Y|do(A),I,Z_2)
\]

### Generation Validity

Generated samples are evaluated for preservation of invariant factors and correct response to context changes.

## 6. Research Position

OIR-PPV evaluates the complete chain:

\[
E \rightarrow I \rightarrow G(I,Z,N) \rightarrow X' \rightarrow SCM \rightarrow Counterfactual
\]

The contribution is a unified benchmark protocol connecting invariant learning, generation, and causal validation.

