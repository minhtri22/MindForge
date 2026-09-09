---
name: tester-performance
description: >
  Tester rules for performance, load, soak, latency, throughput, capacity, resource usage, tail behavior, context scaling, concurrency limits, and repeatable performance evidence. Use together with tester-core.
---

# Tester Performance

## Dependency

Use together with `tester-core`.

## 1. Scope

Use when latency, throughput, resource usage, capacity, reliability under load, or sustained operation is part of acceptance.

## 2. Freeze the Test Shape

Before comparing candidates freeze:

- workload;
- input sizes;
- concurrency;
- warmup;
- duration;
- repetitions;
- hardware;
- runtime;
- config;
- caching policy;
- network conditions where relevant.

Do not compare measurements taken under materially different conditions without disclosure.

## 3. Metrics

Use relevant metrics:

- latency;
- TTFT;
- throughput;
- tokens/s;
- p50/p95/p99;
- max;
- CPU/GPU;
- RAM/VRAM;
- disk/network;
- startup;
- queue time;
- error rate;
- timeout rate.

## 4. Test Classes

### Baseline
Single request / light workload.

### Boundary
Near supported maximums.

### Load
Expected sustained workload.

### Stress
Beyond expected workload to find failure mode.

### Soak
Long enough to reveal leaks/degradation.

### Spike
Sudden burst.

## 5. Capacity Mapping

Distinguish:

- recommended operating range;
- soft ceiling;
- hard ceiling;
- failure point.

Record the first observed degradation and first hard failure.

## 6. Warm vs Cold

Where material, separate:

- cold start;
- warmed cache/model;
- first request;
- steady state.

## 7. Tail Behavior

Do not report mean alone.

For user-facing or critical systems, tail latency and timeout frequency often matter more.

## 8. Repetition

Repeat enough times to detect noise.

Report failed runs and variance; do not discard them without a predefined rule.

## 9. Resource Saturation

Observe whether latency/failure correlates with:

- CPU;
- GPU;
- RAM/VRAM;
- disk;
- queue depth;
- concurrency.

## 10. Evidence

Preserve raw measurement files and exact command/config.

Performance charts/summaries must remain traceable to raw data.
