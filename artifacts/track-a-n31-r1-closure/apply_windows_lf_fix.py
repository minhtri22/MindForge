#!/usr/bin/env python3
from pathlib import Path
import hashlib

p = Path("scripts/materialize_track_a_v1_r1.py")
s = p.read_text(encoding="utf-8")
replacements = {
    '(ROOT/"schema.json").write_text(json.dumps(schema,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")':
    '(ROOT/"schema.json").write_text(json.dumps(schema,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8",newline="\\n")',
    '(ROOT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")':
    '(ROOT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8",newline="\\n")',
}
for old, new in replacements.items():
    if old not in s:
        raise SystemExit(f"expected source line not found: {old}")
    s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8", newline="\n")
h = hashlib.sha256(p.read_bytes()).hexdigest()
expected = "d9f2bf58b102d2cf9a19bba4468adc34de148682245e5e550bdbc6c18d6514b9"
print(h)
if h != expected:
    raise SystemExit(f"patched generator hash mismatch: {h} != {expected}")
