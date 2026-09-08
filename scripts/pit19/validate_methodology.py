"""Methodology and freeze validation for PIT-19."""
from __future__ import annotations
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EXP=ROOT/"experiments/pit19"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def shaf(paths):
    h=hashlib.sha256()
    for rel in paths: h.update((ROOT/rel).read_bytes())
    return h.hexdigest()

def main():
    p=load(EXP/"protocol.json"); f=p["freeze"]; runtime_text="\n".join((ROOT/x).read_text(encoding="utf-8",errors="replace") for x in f["representation_runtime_files"])
    semantic_runtime_text="\n".join((ROOT/x).read_text(encoding="utf-8",errors="replace") for x in f["representation_runtime_files"] if x.startswith("scripts/pit19/"))
    integrity=load(EXP/"clean-heldout-integrity.json")
    changed=subprocess.run(["git","diff","--name-only","e125cb2e9b6b9968e38afaa70cc812800a187a50","--","scripts/pit15","scripts/pit16","scripts/pit17","scripts/pit18","experiments/pit15","experiments/pit16","experiments/pit17","experiments/pit18"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.splitlines()
    clean=load(EXP/"clean-heldout.json")
    leakage=[]
    for s in clean["samples"]:
        pieces=[]
        def walk(x):
            if isinstance(x,str): pieces.append(x)
            elif isinstance(x,list):
                for y in x: walk(y)
            elif isinstance(x,dict):
                for y in x.values(): walk(y)
        walk(s["evidence"]); walk(s["teaching_signal"])
        for text in pieces:
            if len(text)>=40 and text in runtime_text: leakage.append(s["sample_id"])
    known=load(EXP/"dev-corpus.json"); known_phrase_hits=[]
    def collect_text(x,out):
        if isinstance(x,str): out.append(x)
        elif isinstance(x,list):
            for y in x: collect_text(y,out)
        elif isinstance(x,dict):
            for y in x.values(): collect_text(y,out)
    known_text=[]; collect_text(known,known_text)
    for text in known_text:
        if len(text)>=60 and text in semantic_runtime_text: known_phrase_hits.append(text[:120])
    result={"candidate_specific_logic":bool(re.search(r"candidate_id|meta/muse|minimax|nemotron|qwen|deepseek|gemma|gpt-oss",semantic_runtime_text,re.I)),"provider_specific_logic":bool(re.search(r"provider_id|provider_name|nvidia|openai|google",semantic_runtime_text,re.I)),"scenario_id_logic":bool(re.search(r"scenario_id|fixture_id|clean-(?:conflict|numeric|temporal|fallback|scope|ground)-\d+",semantic_runtime_text,re.I)),"exact_known_phrase_patching":bool(known_phrase_hits),"exact_known_phrase_hits":known_phrase_hits[:10],"clean_heldout_leakage":bool(leakage),"clean_heldout_leakage_ids":sorted(set(leakage)),"gold_label_leakage":bool(re.search(r"clean-heldout-gold|expected_violation|gold_id",semantic_runtime_text,re.I)),"post_hoc_tuning":shaf(tuple(f["representation_runtime_files"]))!=f["representation_v3_sha256"],"guardrail_v3_modified_without_policy_defect":sha(ROOT/"scripts/pit17/guardrail_v3.py")!=f["guardrail_v3_sha256"],"historical_pit15_16_17_18_files_modified":changed,"clean_heldout_integrity":integrity.get("clean_heldout_integrity"),"clean_heldout_integrity_report_match":sha(EXP/"clean-heldout-integrity.json")==f["clean_heldout_integrity_sha256"],"metrics_definitions_match":shaf(tuple(f["metrics_definition_files"]))==f["metrics_definitions_sha256"]}
    result["status"]="PASS" if not any((result["candidate_specific_logic"],result["provider_specific_logic"],result["scenario_id_logic"],result["exact_known_phrase_patching"],result["clean_heldout_leakage"],result["gold_label_leakage"],result["post_hoc_tuning"],result["guardrail_v3_modified_without_policy_defect"],bool(changed))) and result["clean_heldout_integrity"]=="PRISTINE" and result["clean_heldout_integrity_report_match"] and result["metrics_definitions_match"] else "FAIL"
    (EXP/"methodology-validation.json").write_text(json.dumps(result,indent=2),encoding="utf-8"); print(json.dumps(result,indent=2))
if __name__=="__main__": main()
