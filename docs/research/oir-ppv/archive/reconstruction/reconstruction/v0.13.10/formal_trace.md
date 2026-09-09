# v0.13.10 Formal Trace

## Experience

E = {(s_t, a_t, r_t, c_t)}

## Invariant

I = f(E)

Implementation requirement:
InvariantExtractor

## Objective

I* = argmin_I C(I) + lambda L(E|I)

Where:
- C(I): invariant complexity
- L(E|I): explanation error

## Generator

x = G(I,c)

## Intervention

do(X=x')

## Counterfactual Metric

D(Y,Y')
