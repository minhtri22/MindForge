"""PIT-17 methodology and freeze validator."""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EXP=ROOT/"experiments/pit17"
DEFAULT_FILES=["scripts/pit17/semantic_facts.py","scripts/pit17/fact_extractor.py","scripts/pit17/support_relations.py","scripts/pit17/guardrail_v3.py"]
def main():
    phase=sys.argv[1] if len(sys.argv)>1 else "pre"
    protocol=json.loads((EXP/"protocol.json").read_text(encoding="utf-8"))
    FILES=(protocol.get("freeze") or {}).get("implementation_files",DEFAULT_FILES)
    texts="\n".join((ROOT/f).read_text(encoding="utf-8") for f in FILES)
    bad_candidate=bool(re.search(r"qwen|deepseek|minimax|muse|nemotron|gemma|gpt-oss|candidate_id|provider",texts,re.I))
    bad_scenario=bool(re.search(r"stable_preference_001|conflicting_evidence_001|scenario_id",texts,re.I))
    gold_leak=bool(re.search(r"expected_status|expected_violation_classes|known_expected_violations|rationale",texts,re.I))
    h=hashlib.sha256(); [h.update((ROOT/f).read_bytes()) for f in FILES]
    result={"status":"PASS" if not(any((bad_candidate,bad_scenario,gold_leak))) else "FAIL","phase":phase,"candidate_specific_logic":bad_candidate,"provider_specific_logic":bad_candidate,"scenario_id_logic":bad_scenario,"gold_label_leakage":gold_leak,"implementation_sha256":h.hexdigest()}
    if phase=="post":
        result["freeze_hash_match"]=protocol["freeze"]["implementation_sha256"]==h.hexdigest(); result["held_out_post_hoc_tuning"]=not result["freeze_hash_match"]
        if not result["freeze_hash_match"]: result["status"]="FAIL"
    (EXP/"methodology-validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    if result["status"]!="PASS": raise SystemExit(1)
if __name__=="__main__": main()
