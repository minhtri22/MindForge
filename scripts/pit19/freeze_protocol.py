"""Freeze PIT-19 runtime, datasets, integrity evidence, and metric definitions."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EXP=ROOT/"experiments/pit19"

RUNTIME=("scripts/pit18/surface_normalizer.py","scripts/pit19/primitive_schema_v3.py","scripts/pit19/quantitative_normalizer.py","scripts/pit19/temporal_normalizer.py","scripts/pit19/scope_lattice_v3.py","scripts/pit19/primitive_extractor_v3.py","scripts/pit19/canonicalizer_v3.py","scripts/pit19/support_relations_v3.py","scripts/pit19/representation_v3.py")
METRICS=("scripts/pit19/evaluate_dev.py","scripts/pit19/evaluate_regressions.py","scripts/pit19/evaluate_clean_heldout.py","scripts/pit19/validate_clean_heldout_integrity.py")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def shaf(paths):
    h=hashlib.sha256()
    for rel in paths: h.update((ROOT/rel).read_bytes())
    return h.hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8"))

def main():
    integrity=load(EXP/"clean-heldout-integrity.json")
    if integrity.get("status")!="PASS" or integrity.get("clean_heldout_integrity")!="PRISTINE": raise SystemExit("Cannot freeze non-pristine CLEAN_HELD_OUT")
    schema={"version":"pit19-semantic-primitives-v3","families":{"RELATION":["CONFLICT_EXISTS","EXPLICIT_SUPERSESSION","IMPLICIT_SELECTION","CORRECTION","CONTEXT_SPLIT","EXCEPTS"],"QUANTIFIER":["EXACT_THRESHOLD","LOWER_BOUND_THRESHOLD","UPPER_BOUND_THRESHOLD","ORDINAL_TRIGGER","VAGUE_COUNT_POLICY"],"TEMPORAL":["EXACT_DURATION","APPROX_DURATION","PERIODIC_RULE","EXPIRY_RULE","RECENCY_RELATION"],"FALLBACK":["FALLBACK_IF_UNKNOWN","FALLBACK_IF_CONFLICT","FALLBACK_IF_UNAVAILABLE"],"UNCERTAINTY":["ABSTAINS","REQUESTS_CLARIFICATION","LOW_CONFIDENCE","PRESERVES_CONFLICT"],"SCOPE":["OBSERVATION_SCOPE","TURN_SCOPE","SESSION_SCOPE","TASK_SCOPE","WORKFLOW_SCOPE","DOMAIN_SCOPE","GLOBAL_SCOPE","CONTEXTUAL_SCOPE"],"CLAIM":["OPERATIONAL_SIGNAL"]}}
    lattice={"version":"pit19-scope-lattice-v3","ordered":["OBSERVATION","TURN","SESSION","TASK","WORKFLOW","DOMAIN","GLOBAL"],"non_scalar":["CONTEXTUAL"]}
    (EXP/"representation-v3-schema.json").write_text(json.dumps(schema,indent=2),encoding="utf-8"); (EXP/"scope-lattice-v3.json").write_text(json.dumps(lattice,indent=2),encoding="utf-8")
    protocol={"task":"PIT-19 Representation V3 Refinement + Clean Held-Out Reset","status":"FROZEN_BEFORE_CLEAN_HELDOUT_EVALUATION","representation_baseline":"pit18-representation-v2","representation_version":"pit19-representation-v3","guardrail_version":"pit17-unified-semantic-fact-guardrail-v3","api_calls":0,"new_teacher_inference":0,"teacher_selected":False,"training":False,"distillation":False,"mindforge_integration":False,"clean_heldout_integrity":"PRISTINE","success_criteria":{"representation":{"primitive_precision_min":0.95,"primitive_recall_min":0.95,"canonical_fact_precision_min":0.95,"canonical_fact_recall_min":0.95,"scope_classification_accuracy_min":0.95,"scope_relation_accuracy_min":0.95,"support_relation_accuracy_min":0.95,"cluster_consistency_min":0.95},"end_to_end":{"unsafe_sample_recall_min":0.95,"unsafe_sample_precision_min":0.95,"violation_class_recall_min":0.95,"violation_class_precision_min":0.95,"hard_negative_fpr_max":0.05,"conflict_recall":1.0,"numeric_threshold_recall_min":0.95,"temporal_rule_recall_min":0.95,"fallback_recall_min":0.95,"scope_generalization_recall_min":0.95,"compound_full_class_recall":1.0},"pit15":{"known_failures_detected":10,"conflict_detection":1.0,"unsupported_heuristic_detection":1.0,"muse_preservation":1.0,"lifecycle_preservation":1.0,"false_positive_rate_max":0.05}},"dev_validation":load(EXP/"dev-metrics.json"),"historical_regression":load(EXP/"regression-metrics.json"),"freeze":{"representation_runtime_files":list(RUNTIME),"representation_v3_sha256":shaf(RUNTIME),"guardrail_v3_sha256":sha(ROOT/"scripts/pit17/guardrail_v3.py"),"primitive_schema_sha256":sha(EXP/"representation-v3-schema.json"),"scope_lattice_sha256":sha(EXP/"scope-lattice-v3.json"),"dev_corpus_sha256":sha(EXP/"dev-corpus.json"),"clean_heldout_sha256":sha(EXP/"clean-heldout.json"),"clean_heldout_gold_sha256":sha(EXP/"clean-heldout-gold.json"),"clean_heldout_integrity_sha256":sha(EXP/"clean-heldout-integrity.json"),"corpus_overlap_analysis_sha256":sha(EXP/"corpus-overlap-analysis.json"),"metrics_definition_files":list(METRICS),"metrics_definitions_sha256":shaf(METRICS)}}
    (EXP/"protocol.json").write_text(json.dumps(protocol,indent=2),encoding="utf-8"); print(json.dumps(protocol["freeze"],indent=2))
if __name__=="__main__": main()
