import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_benchmark_validation():
    p=subprocess.run([sys.executable,str(ROOT/"scripts"/"validate_track_a_v1.py")],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert '"status": "PASS"' in p.stdout
def test_oracle_scores_perfect(tmp_path):
    cases=[]
    for name in ["calibration.jsonl","development.jsonl","test.jsonl"]:
        with (ROOT/"benchmarks"/"track-a-capability-v1"/name).open(encoding="utf-8") as f: cases += [json.loads(x) for x in f if x.strip()]
    pred=tmp_path/"pred.jsonl"
    with pred.open("w",encoding="utf-8") as f:
        for c in cases: f.write(json.dumps({"case_id":c["case_id"],"prediction":c["expected"]},ensure_ascii=False)+"\n")
    for name in ["calibration.jsonl","development.jsonl","test.jsonl"]:
        p=subprocess.run([sys.executable,str(ROOT/"scripts"/"score_track_a_v1.py"),"--cases",str(ROOT/"benchmarks"/"track-a-capability-v1"/name),"--predictions",str(pred)],capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        r=json.loads(p.stdout); assert r["macro_family_primary"]==1.0; assert r["RVE_PASS"]
        if name=="test.jsonl": assert r["TUE_PASS"]
