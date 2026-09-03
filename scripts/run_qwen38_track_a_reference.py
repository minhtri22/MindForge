#!/usr/bin/env python3
"""Run frozen Track-A cases against a local OpenAI-compatible llama.cpp server. Truth is never included in prompts."""
import argparse, json, time, urllib.request
SYSTEM="""You are a bounded personal-understanding and routing evaluator.
Return exactly one JSON object and no prose. Use only supplied context/state/capabilities.
Do not invent unavailable tools, personal facts, or world knowledge."""
FIELDS={"A1":{"intent_label":"string"},"A2":{"resolved_entity_ids":["string"],"resolved_values":["string"],"clarification_required":"boolean"},"A3":{"normalized":"object"},"A4":{"action_id":"string"},"A5":{"arguments":"object"},"A6":{"clarification_required":"boolean","clarification_reason":"string"},"A7":{"route":"LOCAL_MODEL|LOCAL_APP_OR_TOOL|EXTERNAL|CLARIFY"}}
def read_jsonl(path):
    with open(path,encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]
def prompt_for(c):
    payload={"family":c["family"],"input":c["input"],"required_output":FIELDS[c["family"]]}
    return json.dumps(payload,ensure_ascii=False,separators=(",",":"))
def call(base_url,model,prompt,temperature,seed,timeout):
    body={"model":model,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],"temperature":temperature,"seed":seed,"stream":False}
    req=urllib.request.Request(base_url.rstrip("/")+"/v1/chat/completions",data=json.dumps(body).encode("utf-8"),headers={"Content-Type":"application/json"},method="POST")
    t=time.perf_counter()
    with urllib.request.urlopen(req,timeout=timeout) as r: obj=json.loads(r.read().decode("utf-8"))
    elapsed=time.perf_counter()-t; text=obj["choices"][0]["message"]["content"]; s=text.strip()
    if s.startswith("```"): s=s.split("\n",1)[1].rsplit("```",1)[0].strip()
    return json.loads(s),elapsed,obj.get("usage",{})
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--cases",required=True); ap.add_argument("--out",required=True); ap.add_argument("--base-url",default="http://127.0.0.1:8080"); ap.add_argument("--model",default="Qwen3.8-27B-Q4_K_M"); ap.add_argument("--temperature",type=float,default=0.0); ap.add_argument("--seed",type=int,default=20260904); ap.add_argument("--limit",type=int); ap.add_argument("--timeout",type=float,default=300); ap.add_argument("--dry-run",action="store_true"); args=ap.parse_args()
    cases=read_jsonl(args.cases); cases=cases[:args.limit] if args.limit else cases; rows=[]
    for c in cases:
        p=prompt_for(c); assert "expected" not in p,"truth leakage into prompt"
        if args.dry_run: rows.append({"case_id":c["case_id"],"prompt":p}); continue
        try:
            pred,elapsed,usage=call(args.base_url,args.model,p,args.temperature,args.seed,args.timeout); rows.append({"case_id":c["case_id"],"prediction":pred,"elapsed_seconds":elapsed,"usage":usage,"status":"ok"})
        except Exception as e: rows.append({"case_id":c["case_id"],"prediction":{},"status":"error","error":repr(e)})
    with open(args.out,"w",encoding="utf-8",newline="\n") as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n")
    print(json.dumps({"cases":len(rows),"ok":sum(r.get("status","ok")=="ok" for r in rows),"out":args.out},indent=2))
if __name__=="__main__": main()
