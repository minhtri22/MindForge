"""Research-only PPF-L3 E0 generator skeleton; no recognizer or runtime code."""
from __future__ import annotations
import copy, hashlib, inspect, json, random, re
from datetime import datetime, timedelta, timezone
from tools.research.ppf_l2_validation import validate_fixture
V="ppf-l3-e0-smoke/1"; MASTER="mindforge-ppf-l3-e0-v1"
LEAK={"fake_drift","no_pattern","deleted","correction","user_rejected","truth_status","expected_answer","identifiability","scenario_family","behavior_seed","observation_seed","pair_id","latent_truth"}
def cb(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
def sh(x): return hashlib.sha256(cb(x)).hexdigest()
def seed(*x): return int.from_bytes(hashlib.sha256(cb([str(v) for v in x])).digest()[:8],"big")
def oid(k,x): return f"{k}-{hashlib.sha256(f'{V}|{k}|{x}'.encode()).hexdigest()[:10]}"
def z(base,m): return (base+timedelta(minutes=m)).isoformat().replace("+00:00","Z")
def specs():
 return [
 ["s1","p1","E0-S1","primary","STABLE_ROUTINE",[1,1,0,1],"FULL",[5,25,65,190],["INSUFFICIENT_EVIDENCE","INSUFFICIENT_EVIDENCE","SUPPORTED","SUPPORTED"],None,0,3],
 ["s2","p2","E0-S2","primary","NO_PATTERN",[1,0,1,0],"FULL",[5,25,65,130],["INSUFFICIENT_EVIDENCE"]*4,None,0,None],
 ["s3a","p3","E0-S3","full","STABLE_ROUTINE",[1,1,1,1],"FULL",[5,35,75,130],["INSUFFICIENT_EVIDENCE","SUPPORTED","SUPPORTED","SUPPORTED"],None,0,None],
 ["s3b","p3","E0-S3","loss","STABLE_ROUTINE",[1,1,1,1],"PERMISSION_LOSS",[5,35,75,130],["INSUFFICIENT_EVIDENCE","SUPPORTED","NOT_OBSERVABLE","NOT_OBSERVABLE"],None,0,None],
 ["s4a","p4","E0-S4","base","STABLE_ROUTINE",[1,1,1,1],"FULL",[5,45,75,130],["INSUFFICIENT_EVIDENCE","SUPPORTED","SUPPORTED","SUPPORTED"],None,0,None],
 ["s4b","p4","E0-S4","control","STABLE_ROUTINE",[1,1,1,1],"FULL",[5,45,75,130],["INSUFFICIENT_EVIDENCE","SUPPORTED","USER_REJECTED","USER_REJECTED"],"REJECT",0,None],
 ["s5","p5","E0-S5","primary","STABLE_ROUTINE",[1,1,1,1],"FULL",[5,45,75,130],["INSUFFICIENT_EVIDENCE","SUPPORTED","DELETED","DELETED"],"DELETE",0,None],
 ["s6a","p6","E0-S6","single","SINGLE_OCCURRENCE",[1],"FULL",[5,30],["INSUFFICIENT_EVIDENCE"]*2,None,0,None],
 ["s6b","p6","E0-S6","replica","SINGLE_OCCURRENCE",[1],"FULL",[5,30],["INSUFFICIENT_EVIDENCE"]*2,None,1,None]]
def truth(s): return {"person_id":oid("person",s[1]),"structure_id":s[2],"behavioral_truth":s[4],"scope":"activity:generic","lifecycle":"ACTIVE"}
def opps(s,t):
 r=random.Random(seed(MASTER,s[2],s[1],"opportunity")); b=datetime(2026,1,1,8,tzinfo=timezone.utc)
 return [{"opportunity_id":oid("opp",f"{t['person_id']}:{s[2]}:{i}"),"phenomenon_time":z(b,i*30+r.randint(0,2)),"context":{"period":"morning" if i<2 else "later"},"alternatives":["act","not-act"]} for i in range(len(s[5]))]
def behavior(s,o,rep=0):
 r=random.Random(seed(MASTER,s[1],s[2],"behavior",rep)); return [{"opportunity_id":x["opportunity_id"],"occurred":bool(s[5][i]),"behavior_nonce":r.randint(0,10**6),"phenomenon_time":x["phenomenon_time"]} for i,x in enumerate(o)]
def ev(eid,sid,pt,it,occ,opid):
 st="OBSERVED_OCCURRENCE" if occ else "OBSERVABLE_NON_OCCURRENCE"; os="OCCURRENCE" if occ else "OBSERVABLE_NON_OCCURRENCE"
 return {"schema_version":"ppf-l2/1","event_id":eid,"event_type":"activity.sample","source":{"platform":"GENERIC","device_class":"SERVICE","provider":"e0-sensor","source_event_id":sid},"time":{"phenomenon_time":{"start":pt,"timezone":"UTC","timing_quality":"KNOWN"},"result_or_observed_time":pt,"ingested_time":it},"evidence_kind":"RAW_OBSERVATION","capture_policy":{"mode":"EVENT_DRIVEN","expected_observability":"EXPECTED"},"observability":{"state":st},"opportunity":{"id":opid,"state":os,"alternatives":["act","not-act"],"observability":"FULL"},"context":{"period":{"status":"KNOWN","value":"generic","sources":["e0-sensor"]}},"quality":{"quality_state":"GOOD","coverage_state":"COMPLETE"},"provenance":{"procedure_status":"NOT_APPLICABLE"},"payload":{"action":"act" if occ else "not-act"}}
def render(s,o,b,rep=0):
 r=random.Random(seed(MASTER,s[1],s[2],"observation",rep)); rec=[]; prov={"policy":s[6],"render_nonce":r.randint(0,10**6),"records":[]}
 for i,(x,y) in enumerate(zip(o,b)):
  pt=y["phenomenon_time"]; off=(80+r.randint(0,2)) if s[11]==i else (1+r.randint(0,2)); p=datetime.fromisoformat(pt.replace("Z","+00:00")); it=(p+timedelta(minutes=off)).isoformat().replace("+00:00","Z"); eid=oid("event",f"{s[1]}:{s[2]}:{i}:base"); e=ev(eid,oid("src",f"{s[1]}:{i}"),pt,it,y["occurred"],x["opportunity_id"])
  if s[6]=="PERMISSION_LOSS" and i>=2:
   e.update(event_type="source.observability",evidence_kind="OBSERVABILITY_RECORD"); e["observability"]={"state":"PERMISSION_UNAVAILABLE_OR_UNKNOWN","missingness_reason":"PERMISSION_LIMITATION"}; e["opportunity"].update(state="UNKNOWN_OUTCOME",observability="UNKNOWN"); e["quality"]={"quality_state":"UNKNOWN","coverage_state":"UNKNOWN"}; e["payload"]={"availability":"unavailable"}
  rec.append(e); prov["records"].append({"event_id":eid,"opportunity_id":x["opportunity_id"],"behavior_occurred":y["occurred"]})
  if s[10] and i==0:
   q=copy.deepcopy(e); q["event_id"]=oid("event",f"{s[1]}:{s[2]}:{i}:replica"); q["source"].update(platform="ANDROID",device_class="PHONE",provider="e0-mirror"); q["relations"]=[{"type":"SAME_ORIGIN_REPLICATED","target_event_id":eid}]; rec.append(q); prov["records"].append({"event_id":q["event_id"],"same_origin_of":eid,"behavior_occurred":y["occurred"]})
 if s[9]:
  ct="2026-01-01T09:00:00Z"; target=rec[1]["event_id"]; cid=oid("event",f"{s[0]}:control"); rel="CORRECTS" if s[9]=="REJECT" else "DELETES"; rec.append({"schema_version":"ppf-l2/1","event_id":cid,"event_type":"user.feedback","source":{"platform":"USER","device_class":"USER","provider":"user"},"time":{"phenomenon_time":{"start":ct,"timezone":"UTC","timing_quality":"KNOWN"},"result_or_observed_time":ct,"ingested_time":ct},"evidence_kind":"USER_FEEDBACK","observability":{"state":"OBSERVED_OCCURRENCE"},"context":{},"quality":{"quality_state":"GOOD","coverage_state":"NOT_APPLICABLE"},"provenance":{"procedure_status":"NOT_APPLICABLE"},"relations":[{"type":rel,"target_event_id":target}],"payload":{"operation":"reject" if s[9]=="REJECT" else "remove","scope":"activity:generic"}}); prov["control"]={"event_id":cid,"operation":s[9],"effective_time":ct}
 f={"fixture_id":"L2-F001","title":"E0 smoke visible history","family":"E0_SMOKE","purpose":"Validate frozen L2 event structure for E0 smoke history","source_platform_class":"GENERIC","records":rec,"expected":{"semantic_interpretation":"Visible evidence only","observability":"Explicit","opportunity":"Explicit","time":"Three-time explicit","provenance":"Retained","multi_device":"Replica lineage explicit","raw_derived":"No derived evidence","lineage":"Control/replica explicit","must_not_infer":"Truth is evaluator-only"},"adversarial":s[2]!="E0-S1","gates":["L2-G1"]}; return f,prov
def l2(f): return validate_fixture(f)
def prefix(r,t):
 x=datetime.fromisoformat(t.replace("Z","+00:00")); return [e for e in r if datetime.fromisoformat(e["time"]["ingested_time"].replace("Z","+00:00"))<=x]
def oracle(s,r):
 b=datetime(2026,1,1,8,tzinfo=timezone.utc); return [{"checkpoint_id":oid("cp",f"{s[0]}:{i}"),"time":z(b,m),"expected_answer":s[8][i],"visible_event_ids":[e["event_id"] for e in prefix(r,z(b,m))]} for i,m in enumerate(s[7])]
def gen(s,br=0,orr=0):
 t=truth(s); o=opps(s,t); b=behavior(s,o,br); f,p=render(s,o,b,orr); c=oracle(s,f["records"]); cid=oid("case",s[0]); E={"case_id":cid,"smoke_version":V,"structure_id":s[2],"variant":s[3],"truth":t,"seeds":{"master_seed":MASTER,"scenario_seed":seed(MASTER,s[2],"scenario"),"person_seed":seed(MASTER,s[1],"person"),"behavior_seed":seed(MASTER,s[1],s[2],"behavior",br),"observation_seed":seed(MASTER,s[1],s[2],"observation",orr)},"expected_answers":[{"checkpoint_id":x["checkpoint_id"],"answer":x["expected_answer"]} for x in c],"observation_provenance":p}; return {"id":cid,"truth":t,"opps":o,"behavior":b,"fixture":f,"cp":c,"eval":E}
def method(c): return {"case_id":c["id"],"smoke_version":V,"history":c["fixture"]["records"],"checkpoints":[{"checkpoint_id":x["checkpoint_id"],"time":x["time"]} for x in c["cp"]]}
def leaks(c):
 x=json.dumps(method(c),sort_keys=True).lower(); return sorted(v for v in LEAK if v in x)
def pairs(): return [{"id":"E0-CF1","a":"s3a","b":"s3b","ctrl":6},{"id":"E0-CF2","a":"s6a","b":"s6b","ctrl":10},{"id":"E0-CF3","a":"s4a","b":"s4b","ctrl":9}]
def paircheck(p,sm,cs):
 a,b=cs[p["a"]],cs[p["b"]]; sa,sb=sm[p["a"]],sm[p["b"]]; q={"truth_equal":a["truth"]==b["truth"],"opportunities_equal":a["opps"]==b["opps"],"behavior_equal":a["behavior"]==b["behavior"]}; allowed={0,3,8,p["ctrl"]}; q["no_undeclared_spec_difference"]=all(sa[i]==sb[i] or i in allowed for i in range(len(sa))); ar,br=a["fixture"]["records"],b["fixture"]["records"]
 if p["id"]=="E0-CF1": q["visible_change_is_observation_only"]=len(ar)==len(br) and all(x["event_id"]==y["event_id"] for x,y in zip(ar,br))
 if p["id"]=="E0-CF2": q["visible_change_is_replica_only"]=len(br)==len(ar)+1 and br[0]==ar[0] and br[1]["relations"][0]["type"]=="SAME_ORIGIN_REPLICATED"
 if p["id"]=="E0-CF3": q["visible_change_is_control_only"]=br[:-1]==ar and br[-1]["evidence_kind"]=="USER_FEEDBACK"
 return q
def run_e0():
 ss=specs(); sm={x[0]:x for x in ss}; cs={x[0]:gen(x) for x in ss}; cs2={x[0]:gen(x) for x in ss}; base,oc,bc=gen(sm["s1"]),gen(sm["s1"],0,1),gen(sm["s1"],1,0); errs={k:l2(v["fixture"]) for k,v in cs.items()}; pp={p["id"]:paircheck(p,sm,cs) for p in pairs()}; delayed=cs["s1"]["fixture"]["records"][3]["event_id"]; gok={}
 gok["E0-G1"]=all(truth(s)["behavioral_truth"]==s[4] for s in ss); gok["E0-G2"]=all(sh(cs[k]["eval"])==sh(cs2[k]["eval"]) and sh(method(cs[k]))==sh(method(cs2[k])) for k in cs); gok["E0-G3"]=base["truth"]==oc["truth"] and base["opps"]==oc["opps"] and base["behavior"]==oc["behavior"]; gok["E0-G4"]=base["truth"]==bc["truth"] and base["opps"]==bc["opps"]; gok["E0-G5"]=all(not x for x in errs.values()); gok["E0-G6"]=delayed not in cs["s1"]["cp"][2]["visible_event_ids"] and delayed in cs["s1"]["cp"][3]["visible_event_ids"]; gok["E0-G7"]=cs["s3a"]["truth"]==cs["s3b"]["truth"] and cs["s3a"]["opps"]==cs["s3b"]["opps"] and cs["s3a"]["behavior"]==cs["s3b"]["behavior"]; gok["E0-G8"]=sum(x["occurred"] for x in cs["s6a"]["behavior"])==sum(x["occurred"] for x in cs["s6b"]["behavior"])==1 and len(cs["s6b"]["fixture"]["records"])==2; ca=[x["expected_answer"] for x in cs["s4b"]["cp"]]; da=[x["expected_answer"] for x in cs["s5"]["cp"]]; gok["E0-G9"]=ca[-2:]==["USER_REJECTED"]*2 and da[-2:]==["DELETED"]*2; lm={k:leaks(v) for k,v in cs.items()}; gok["E0-G10"]=not any(lm.values()); gok["E0-G11"]=all(all(v.values()) for v in pp.values()); src=inspect.getsource(oracle); gok["E0-G12"]=not any(re.search(x,src,re.I) for x in [r"occurrences\s*>?=",r"confidence\s*[><=]",r"pattern_score",r"classifier"])
 n=sum(len(v["fixture"]["records"]) for v in cs.values()); people={v["truth"]["person_id"] for v in cs.values()}; structs={v["eval"]["structure_id"] for v in cs.values()}; return {"smoke_version":V,"status":"PASS" if all(gok.values()) and len(people)==len(structs)==6 else "REVISE","smoke_persons":len(people),"smoke_structures":len(structs),"smoke_histories":len(cs),"smoke_checkpoints":sum(len(v["cp"]) for v in cs.values()),"visible_l2_events":n,"l2_valid_visible_events":sum(len(cs[k]["fixture"]["records"]) for k in cs if not errs[k]),"counterfactual_pairs":3,"checkpoint_future_leak_violations":0 if gok["E0-G6"] else 1,"truth_leak_violations":sum(map(len,lm.values())),"gates":gok,"seed_reproducibility_hashes":{k:sh(v["eval"]) for k,v in cs.items()},"correction_lifecycle":ca,"deletion_lifecycle":da,"pair_isolation":pp,"l2_errors":errs,"oracle_boundary":{"declarative_expected_answers":True,"generic_threshold_patterns_found":False}}
build_specs=specs; generate_case=gen; semantic_hash=sh; method_manifest=method; checkpoint_prefix=prefix; iso=z
def behavior_core(c): return c["behavior"]
def count_behavior_occurrences(c): return sum(x["occurred"] for x in c["behavior"])
