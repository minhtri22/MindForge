---
name: tester-game
description: >
  Tester rules for game QA including controls, input latency, collision and hit registration, state closure, camera comfort, onboarding, deterministic/replayable mechanics where possible, platform/build compatibility, frame rate, haptics, and gameplay regressions. Use together with tester-core.
---

# Tester Game

## Dependency

Use together with `tester-core`.

## 1. Scope

Use for interactive games and real-time simulations.

## 2. Build Identity

Always record:

- repository;
- branch;
- commit SHA;
- build ID;
- platform;
- engine/runtime version;
- device/browser.

Never test an unknown or stale build.

## 3. Control Testing

Verify:

- input mapping;
- dead zones;
- simultaneous inputs;
- rapid repeated input;
- hold vs tap;
- lost touch/pointer;
- orientation/viewport changes;
- no-input state;
- input after pause/restart.

## 4. Combat / Collision / Hit Registration

For combat games test:

- distance boundaries;
- hitbox/hurtbox alignment;
- moving attacker;
- moving defender;
- simultaneous attacks;
- guard state;
- animation interruption;
- edge-of-range hit;
- miss just outside range;
- rollback/recovery if applicable.

Visual punch animation MUST NOT imply a hit when the mechanical range says miss.

## 5. Movement Coupling

Check whether movement causes:

- body-part separation;
- animation stretching;
- phantom hits;
- feet/body desynchronization;
- camera instability;
- collision tunneling.

## 6. Game-State Closure

Verify complete transitions:

- start;
- pause;
- resume;
- win;
- loss;
- timeout;
- restart;
- quit;
- rematch/training if available.

No state should leave input, camera, UI, physics, or audio in an inconsistent mode.

## 7. Camera / Comfort

For first-person or motion-heavy games test:

- head/camera coupling;
- sudden acceleration;
- shake;
- field-of-view changes;
- repeated movement;
- onboarding clarity.

Report discomfort-inducing behavior as a usability finding; do not dismiss it because mechanics are technically correct.

## 8. Performance

Record as relevant:

- FPS;
- frame-time spikes;
- input latency;
- loading time;
- memory;
- mobile thermal/resource issues;
- browser/WebGL stability.

## 9. Platform Compatibility

Verify required targets such as:

- Windows;
- WebGL/browser;
- Android/iOS;
- touch vs mouse/keyboard;
- screen sizes/orientation.

## 10. Haptics / Audio / Feedback

Where applicable verify:

- event maps to correct feedback;
- no feedback on misses when not intended;
- light/heavy distinctions;
- feedback timing;
- repeated-event behavior.

## 11. Regression Capture

Gameplay defects are often visual/temporal. Capture:

- short video;
- build ID;
- exact reproduction steps;
- approximate timestamp;
- expected vs observed;
- device/platform.

Convert repeatable gameplay bugs into regression scenarios.

## 12. Exploratory Charters

Useful charters include:

- "try to land hits from impossible ranges";
- "attempt to desynchronize movement and punch";
- "stress pause/restart during combat";
- "rapidly alternate guard/punch/move";
- "play without onboarding knowledge";
- "seek camera discomfort triggers".
