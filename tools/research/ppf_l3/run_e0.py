from pathlib import Path
import json
from .e0 import run_e0


def main() -> int:
    summary = run_e0()
    root = Path(__file__).resolve().parents[3]
    out = root / "docs" / "research" / "data" / "ppf-l3" / "e0-summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
