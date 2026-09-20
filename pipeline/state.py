"""Pure run/phase state transition guards."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import StateTransitionError
from .models import PhaseState, RunState


RUN_TRANSITIONS: dict[RunState, set[RunState]] = {
    RunState.DRAFT: {RunState.PREPARED, RunState.INVALID},
    RunState.PREPARED: {RunState.PREFLIGHT_PASS, RunState.INVALID},
    RunState.PREFLIGHT_PASS: {RunState.EXECUTION_LOCKED, RunState.INVALID},
    RunState.EXECUTION_LOCKED: {RunState.RUNNING, RunState.INVALID},
    RunState.RUNNING: {RunState.EVALUATED, RunState.INVALID},
    RunState.EVALUATED: {RunState.ADJUDICATED_PASS, RunState.ADJUDICATED_FAIL, RunState.INVALID},
    RunState.ADJUDICATED_PASS: {RunState.EXPORTED, RunState.QUALIFICATION_FAIL},
    RunState.ADJUDICATED_FAIL: set(),
    RunState.INVALID: set(),
    RunState.EXPORTED: {RunState.RUNTIME_VERIFIED, RunState.QUALIFICATION_FAIL},
    RunState.RUNTIME_VERIFIED: {RunState.REPRO_VERIFIED, RunState.QUALIFICATION_FAIL},
    RunState.REPRO_VERIFIED: {RunState.PROMOTED, RunState.QUALIFICATION_FAIL},
    RunState.QUALIFICATION_FAIL: set(),
    RunState.PROMOTED: set(),
}

PHASE_TRANSITIONS: dict[PhaseState, set[PhaseState]] = {
    PhaseState.PLANNED: {PhaseState.INPUT_READY, PhaseState.PHASE_INVALID},
    PhaseState.INPUT_READY: {PhaseState.TRAINING, PhaseState.PHASE_INVALID},
    PhaseState.TRAINING: {PhaseState.TRAINED, PhaseState.PHASE_INVALID},
    PhaseState.TRAINED: {PhaseState.CHECKPOINT_SELECTED, PhaseState.PHASE_INVALID},
    PhaseState.CHECKPOINT_SELECTED: {PhaseState.PHASE_EVALUATED, PhaseState.PHASE_INVALID},
    PhaseState.PHASE_EVALUATED: {PhaseState.PHASE_PASS, PhaseState.PHASE_FAIL, PhaseState.PHASE_INVALID},
    PhaseState.PHASE_PASS: set(),
    PhaseState.PHASE_FAIL: set(),
    PhaseState.PHASE_INVALID: set(),
}


def validate_run_transition(current: RunState, target: RunState) -> None:
    if target not in RUN_TRANSITIONS[current]:
        raise StateTransitionError(f"invalid run transition {current.value} -> {target.value}")


def validate_phase_transition(current: PhaseState, target: PhaseState) -> None:
    if target not in PHASE_TRANSITIONS[current]:
        raise StateTransitionError(f"invalid phase transition {current.value} -> {target.value}")


@dataclass
class RunMachine:
    state: RunState = RunState.DRAFT

    def advance(self, target: RunState) -> RunState:
        validate_run_transition(self.state, target)
        self.state = target
        return self.state


@dataclass
class PhaseMachine:
    state: PhaseState = PhaseState.PLANNED

    def advance(self, target: PhaseState) -> PhaseState:
        validate_phase_transition(self.state, target)
        self.state = target
        return self.state
