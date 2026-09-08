"""Measure semantic-fact consistency across surface transformations."""
from __future__ import annotations
import json
from pathlib import Path
from fact_extractor import extract_semantic_facts
ROOT=Path(__file__).resolve().parents[2]; EXP=ROOT/"experiments/pit17"
def main():
    doc=json.loads((EXP/"representation-clusters.json").read_text(encoding="utf-8")); rows=[]; consistent=0
    for c in doc["clusters"]:
        vals=[]
        for i,s in enumerate(c["signals"]):
            sig={"inference":s,"applicability_boundary":"Bounded to supplied evidence.","revision_trigger":"Revise only when evidence changes."}
            facts=extract_semantic_facts(c["evidence"],sig); value=bool(facts["teaching_signal_state"][c["expected_fact"]]); vals.append(value)
            rows.append({"cluster_id":c["cluster_id"],"variant":i+1,"expected_fact":c["expected_fact"],"fact_value":value})
        if all(vals) and len(set(vals))==1: consistent+=1
    rate=round(consistent/len(doc["clusters"]),6)
    (EXP/"representation-invariance-results.jsonl").write_text("".join(json.dumps(r)+"\n" for r in rows),encoding="utf-8")
    print(json.dumps({"clusters":len(doc["clusters"]),"variants":len(rows),"cluster_fact_consistency_rate":rate},indent=2))
if __name__=="__main__": main()
