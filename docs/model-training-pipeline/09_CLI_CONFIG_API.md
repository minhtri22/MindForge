# 09 — CLI, Config & API

## 1. Canonical config

schemas/experiment_config.schema.json is the only authoring vocabulary. 16_CANONICAL_CONFIG_STATE_MACHINE.md defines resolution/lock semantics.

CLI rejects unknown fields by default for locked runs.

## 2. CLI

pipeline init <workspace>
pipeline doctor
pipeline model inspect <model-spec>
pipeline data prepare -c <config>
pipeline data audit <run-id>
pipeline preflight -c <config>
pipeline lock <run-id>
pipeline train <run-id>
pipeline resume <run-id> --checkpoint <id>
pipeline eval <run-id>
pipeline adjudicate <run-id>
pipeline export <run-id>
pipeline verify-runtime <run-id> --runtime llama.cpp
pipeline verify-runtime <run-id> --runtime ollama
pipeline chat --model run:<id> --reasoning visible|hidden|off
pipeline bundle <run-id>
pipeline status <run-id>

Host-mutating runtime installation is a separate explicit command/policy, never implicit in preflight/train.

## 3. Config resolution

Includes/profiles expand, refs/device/precision/tool versions resolve, then canonical normalized config is written and hashed. Confirmatory/release cannot lock unresolved main/latest/auto/placeholders.

## 4. Programmatic API

Methods return typed results with state transition, evidence refs and error codes.

## 5. Failure model

Every failure records code, stage, message, recoverability, evidence refs and whether verdict is FAIL or INVALID. No exception path may silently mutate scientific config.
