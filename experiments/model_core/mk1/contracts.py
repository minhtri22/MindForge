"""Frozen MK-1 tensor, seed, split, and training contracts."""

from __future__ import annotations

from dataclasses import dataclass

Z1_LABELS = (
    "CONFLICT_EXISTS", "EXPLICIT_SUPERSESSION", "IMPLICIT_SELECTION", "CORRECTION", "CONTEXT_SPLIT", "EXCEPTS",
    "EXACT_THRESHOLD", "LOWER_BOUND_THRESHOLD", "UPPER_BOUND_THRESHOLD", "ORDINAL_TRIGGER", "VAGUE_COUNT_POLICY",
    "EXACT_DURATION", "APPROX_DURATION", "PERIODIC_RULE", "EXPIRY_RULE", "RECENCY_RELATION",
    "FALLBACK_IF_UNKNOWN", "FALLBACK_IF_CONFLICT", "FALLBACK_IF_UNAVAILABLE",
    "ABSTAINS", "REQUESTS_CLARIFICATION", "LOW_CONFIDENCE", "PRESERVES_CONFLICT",
    "OBSERVATION_SCOPE", "TURN_SCOPE", "SESSION_SCOPE", "TASK_SCOPE", "WORKFLOW_SCOPE", "DOMAIN_SCOPE", "GLOBAL_SCOPE", "CONTEXTUAL_SCOPE",
    "OPERATIONAL_SIGNAL",
)
RELATION_LABELS = Z1_LABELS[0:6]
QUANTIFIER_LABELS = Z1_LABELS[6:11]
TEMPORAL_LABELS = Z1_LABELS[11:16]
FALLBACK_LABELS = Z1_LABELS[16:19]
UNCERTAINTY_LABELS = Z1_LABELS[19:23]
SCOPE_PRIMITIVE_LABELS = Z1_LABELS[23:31]
SCOPES = ("OBSERVATION", "TURN", "SESSION", "TASK", "WORKFLOW", "DOMAIN", "GLOBAL", "CONTEXTUAL")
SCOPE_RELATIONS = ("NARROWER", "EQUAL", "BROADER", "INCOMPARABLE")
COMPARATORS = ("NONE", "EXACT", "LOWER_BOUND", "UPPER_BOUND")
TEMPORAL_PRECISIONS = ("NONE", "EXACT", "APPROX")
Z2_SCALARS = ("numeric_value", "ordinal_index", "duration_seconds", "period_seconds")
Z4_FIELDS = (
    "conflict_present", "supersession_supported", "scope_supported", "numeric_value_supported",
    "temporal_rule_supported", "fallback_policy_supported", "operational_signal_supported",
)
C1_FIELDS = (
    "evidence_has_conflict", "resolves_conflict", "asserts_numeric_threshold", "asserts_temporal_rule",
    "asserts_fallback_policy", "abstains", "requests_clarification", "has_operational_signal",
)
C5_FIELDS = (
    "supersession_supported", "scope_supported", "numeric_value_supported", "temporal_rule_supported",
    "fallback_policy_supported", "operational_signal_supported",
)
Z_SLICES = {
    "z1": slice(0, 32), "z2_comparator": slice(32, 36), "z2_temporal_precision": slice(36, 39),
    "z2_scalars": slice(39, 43), "z3_evidence_scope": slice(43, 51), "z3_asserted_scope": slice(51, 59),
    "z3_scope_relation": slice(59, 63), "z4": slice(63, 70),
}
C_SLICES = {"c1": slice(0, 8), "c2": slice(8, 16), "c3": slice(16, 24), "c4": slice(24, 28), "c5": slice(28, 34)}
D_Z = 70
D_C = 34
B0_PARAMETER_COUNT = 10_339_200
M1Z_PARAMETER_COUNT = 10_361_670
DIRECT_PARAMETER_COUNT = 10_350_114
TRAIN_SCENE_RANGE = range(7_101_000, 7_103_000)
VALIDATION_SCENE_RANGE = range(7_103_000, 7_103_400)
CONFIRMATORY_SCENE_RANGE = range(7_104_000, 7_104_600)
SCIENTIFIC_TRAINING_SEEDS = (71001, 71002, 71003, 71004, 71005)
H1B_BOOTSTRAP_SEED = 71101
H1B_BOOTSTRAP_RESAMPLES = 10_000
RENDERER_TRAIN_A = "A"
RENDERER_TRAIN_B = "B"
RENDERER_HELDOUT_C = "C"

@dataclass(frozen=True)
class TrainingLock:
    steps: int = 5_000
    micro_batch: int = 1
    accumulation: int = 8
    learning_rate: float = 3e-4
    weight_decay: float = 0.1
    gradient_clip: float = 1.0
    warmup_fraction: float = 0.05
    min_lr_fraction: float = 0.1
    validation_interval: int = 250
    max_context: int = 512
    dtype: str = "float32"
    device: str = "auto"

TRAINING_LOCK = TrainingLock()
assert len(Z1_LABELS) == 32
assert len(SCOPES) == 8 and len(SCOPE_RELATIONS) == 4
assert len(Z4_FIELDS) == 7 and len(C1_FIELDS) == 8 and len(C5_FIELDS) == 6
assert Z_SLICES["z4"].stop == D_Z and C_SLICES["c5"].stop == D_C
