"""Overlap and integrity checks for PIT-19 CLEAN_HELD_OUT before freeze."""
from __future__ import annotations
import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EXP=ROOT/"experiments/pit19"

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def norm(s): return " ".join(re.findall(r"[a-z0-9]+",str(s).lower()))
def tokens(s): return set(norm(s).split())
def ngrams(s,n=5):
    t=norm(s).split(); return set(tuple(t[i:i+n]) for i in range(max(0,len(t)-n+1)))
def jac(a,b):
    # Empty n-gram sets contain no evidence of lexical overlap. Treating two
    # short strings as identical merely because both lack 5-grams is a false positive.
    if not a or not b: return 0.0
    return len(a&b)/len(a|b)
def skeleton(s):
    x=norm(s); x=re.sub(r"\b\d+\b","<num>",x); x=re.sub(r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|thirty|sixty|ninety)\b","<num>",x); return x
def flatten(obj):
    out=[]
    if isinstance(obj,str): out.append(obj)
    elif isinstance(obj,list):
        for x in obj: out.extend(flatten(x))
    elif isinstance(obj,dict):
        for k,v in obj.items():
            if k not in {"expected_violation_classes","expected_status","gold","rationale"}: out.extend(flatten(v))
    return out

def prior_texts():
    paths=[ROOT/"experiments/pit13/evidence/scenarios.json",ROOT/"experiments/pit15/control/control-results.jsonl",ROOT/"experiments/pit16/corpus.json",ROOT/"experiments/pit17/fact-goldset.json",ROOT/"experiments/pit18/representation-gold-dev.json",ROOT/"experiments/pit18/representation-gold-heldout.json"]
    texts=[]
    for p in paths:
        if p.suffix==".jsonl":
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip(): texts.extend(flatten(json.loads(line)))
        else: texts.extend(flatten(load(p)))
    return [x for x in texts if len(norm(x).split())>=4]

def main():
    corpus=load(EXP/"clean-heldout.json"); gold=load(EXP/"clean-heldout-gold.json"); prior=prior_texts(); suspicious=[]; maxima={"token_jaccard":0.0,"ngram_jaccard":0.0}
    prior_norm={norm(x) for x in prior}; prior_skel={skeleton(x) for x in prior}; prior_t=[tokens(x) for x in prior]; prior_n=[ngrams(x) for x in prior]
    for sample in corpus["samples"]:
        for text in flatten({"evidence":sample["evidence"],"teaching_signal":sample["teaching_signal"]}):
            n=norm(text); sk=skeleton(text)
            exact=n in prior_norm; templ=sk in prior_skel
            tt=tokens(text); ng=ngrams(text); mt=max((jac(tt,x) for x in prior_t),default=0.0); mn=max((jac(ng,x) for x in prior_n),default=0.0)
            maxima["token_jaccard"]=max(maxima["token_jaccard"],mt); maxima["ngram_jaccard"]=max(maxima["ngram_jaccard"],mn)
            if exact or templ or mt>=0.80 or mn>=0.60: suspicious.append({"sample_id":sample["sample_id"],"exact":exact,"template":templ,"max_token_jaccard":round(mt,6),"max_5gram_jaccard":round(mn,6),"text":text})
    ids=[x["sample_id"] for x in corpus["samples"]]; classes={}
    for sid,g in gold["gold"].items():
        for c in g["expected_violation_classes"]: classes[c]=classes.get(c,0)+1
    unsafe=sum(bool(g["expected_violation_classes"]) for g in gold["gold"].values()); valid=len(ids)-unsafe
    integrity={"status":"PASS" if len(ids)==len(set(ids))==100 and unsafe==70 and valid==30 and not suspicious else "FAIL","clean_heldout_integrity":"PRISTINE" if not suspicious else "FAILED","samples":len(ids),"unsafe":unsafe,"hard_negatives":valid,"class_counts":classes,"compound_samples":sum(len(g["expected_violation_classes"])>1 for g in gold["gold"].values()),"exact_match_count":sum(x["exact"] for x in suspicious),"template_match_count":sum(x["template"] for x in suspicious),"suspicious_overlap_count":len(suspicious),"max_overlap":{k:round(v,6) for k,v in maxima.items()},"suspicious":suspicious,"corpus_sha256":hashlib.sha256((EXP/"clean-heldout.json").read_bytes()).hexdigest(),"gold_sha256":hashlib.sha256((EXP/"clean-heldout-gold.json").read_bytes()).hexdigest()}
    (EXP/"corpus-overlap-analysis.json").write_text(json.dumps(integrity,ensure_ascii=False,indent=2),encoding="utf-8"); (EXP/"clean-heldout-integrity.json").write_text(json.dumps({k:v for k,v in integrity.items() if k!="suspicious"},ensure_ascii=False,indent=2),encoding="utf-8"); print(json.dumps({k:v for k,v in integrity.items() if k!="suspicious"},indent=2))
    if integrity["status"]!="PASS": raise SystemExit(2)

if __name__=="__main__": main()
