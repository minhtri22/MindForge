"""Standalone M5 converter-environment probe.

Executed directly by the isolated converter Python. It intentionally imports no
MindForge package code.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

MODULES = {
    "torch": "torch",
    "transformers": "transformers",
    "numpy": "numpy",
    "sentencepiece": "sentencepiece",
    "protobuf": "google.protobuf",
    "gguf": "gguf",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    result = {}
    for logical, module_name in MODULES.items():
        try:
            module = importlib.import_module(module_name)
            file_value = getattr(module, "__file__", None)
            module_path = Path(file_value).resolve() if file_value else None
            version = getattr(module, "__version__", None)
            result[logical] = {
                "import_ok": True,
                "module": module_name,
                "version": str(version) if version is not None else "module-present-version-unavailable",
                "module_file": str(module_path) if module_path else None,
                "module_file_sha256": (
                    _sha256(module_path)
                    if module_path is not None and module_path.is_file()
                    else None
                ),
            }
        except Exception as error:
            result[logical] = {
                "import_ok": False,
                "module": module_name,
                "error_type": type(error).__name__,
                "error": str(error),
            }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
