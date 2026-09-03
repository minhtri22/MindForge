import json
from tools.research.ppf_l3.e2 import run_e2

summary = run_e2()
print(json.dumps(summary, indent=2, sort_keys=True))
raise SystemExit(0 if summary["status"] == "PASS" else 1)
