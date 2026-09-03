import json
from pathlib import Path
from tools.research.ppf_l3.e1 import run_e1
ROOT=Path(__file__).resolve().parents[3]
summary=run_e1()
out=ROOT/'docs/research/data/ppf-l3/e1-summary.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding='utf-8')
print(json.dumps(summary,indent=2,sort_keys=True))
raise SystemExit(0 if summary['status']=='PASS' else 1)
