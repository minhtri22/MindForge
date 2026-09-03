#!/usr/bin/env python3
import json, hashlib, sys
from pathlib import Path
from collections import Counter,defaultdict
root=Path(__file__).resolve().parents[1]/"benchmarks"/"track-a-capability-v1"

def diff_paths(a,b,prefix=""):
    paths=[]
    if type(a)!=type(b): return [prefix]
    if isinstance(a,dict):
        for k in sorted(set(a)|set(b)):
            pp=f"{prefix}.{k}" if prefix else k
            if k not in a or k not in b: paths.append(pp)
            else: paths += diff_paths(a[k],b[k],pp)
    elif isinstance(a,list):
        if a!=b: paths.append(prefix)
    elif a!=b:
        paths.append(prefix)
    return paths
def read(name):
    with (root/name).open(encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]
cases=read("calibration.jsonl")+read("development.jsonl")+read("test.jsonl")
assert len(cases)==1400
assert len({c["case_id"] for c in cases})==1400
assert Counter(c["family"] for c in cases)==Counter({f"A{i}":200 for i in range(1,8)})
assert Counter(c["split"] for c in cases)==Counter({"calibration":280,"development":420,"test":700})
assert Counter(c["language_group"] for c in cases)==Counter({"vi":840,"vi_en":350,"en":210})
assert Counter(c["difficulty"] for c in cases)==Counter({"straightforward":560,"contextual":490,"adversarial":350})
for fam in [f"A{i}" for i in range(1,8)]:
    cs=[c for c in cases if c["family"]==fam]
    assert Counter(c["language_group"] for c in cs)==Counter({"vi":120,"vi_en":50,"en":30})
    assert Counter(c["difficulty"] for c in cs)==Counter({"straightforward":80,"contextual":70,"adversarial":50})
    assert Counter(c["split"] for c in cs)==Counter({"calibration":40,"development":60,"test":100})
held=[c for c in cases if c["split"]=="test"]
assert sum(c["counterfactual_group_id"] is not None for c in held)>=140
groups=defaultdict(list)
for c in held:
    if c["counterfactual_group_id"]: groups[c["counterfactual_group_id"]].append(c)
assert all(len(v)==2 for v in groups.values())
for gid,pair in groups.items():
    assert pair[0]["language_group"]==pair[1]["language_group"], gid
    assert pair[0]["difficulty"]==pair[1]["difficulty"], gid
    changed=diff_paths(pair[0]["input"],pair[1]["input"])
    assert len(changed)==1, (gid,changed)
assert all(c["provenance"]["truth_source"]=="rule_defined" for c in cases)
assert all(c["provenance"]["review_status"]=="automated_qa_pass_human_spot_review_pending" for c in cases)
print(json.dumps({"status":"PASS","cases":len(cases),"heldout_counterfactual_cases":sum(c["counterfactual_group_id"] is not None for c in held),"counterfactual_groups":len(groups)},indent=2))
