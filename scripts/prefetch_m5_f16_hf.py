"""Infrastructure-only exact pinned Hugging Face prefetch for local M5 F16 fallback.

This helper does not train, convert, infer, quantize, or adjudicate. It only
materializes the model snapshot already pinned by the frozen experiment config
into a persistent cache so the scientific harness can execute offline.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from huggingface_hub import snapshot_download

from pipeline.canonical import sha256_file, sha256_object
from pipeline.loader import load_experiment_config

ALLOW_PATTERNS = [
    "*.json",
    "*.safetensors",
    "*.jinja",
    "tokenizer*",
    "vocab*",
    "merges*",
    "*.model",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    repo_root = Path(args.workspace).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()
    cache_dir = Path(args.cache_dir).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    config = load_experiment_config(config_path, repo_root)
    attempts: list[dict[str, object]] = []
    snapshot: Path | None = None

    for index in range(1, max(1, args.attempts) + 1):
        try:
            resolved = snapshot_download(
                repo_id=config.model.id,
                revision=config.model.revision,
                cache_dir=str(cache_dir),
                allow_patterns=ALLOW_PATTERNS,
                max_workers=1,
            )
            snapshot = Path(resolved).resolve()
            attempts.append({"attempt": index, "status": "PASS"})
            break
        except Exception as error:  # infrastructure capture only
            attempts.append(
                {
                    "attempt": index,
                    "status": "FAIL",
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )
            if index < max(1, args.attempts):
                time.sleep(3)

    if snapshot is None:
        result = {
            "schema": "mindforge-local-hf-prefetch-v1",
            "status": "FAIL",
            "model_id": config.model.id,
            "revision": config.model.revision,
            "allow_patterns": ALLOW_PATTERNS,
            "attempts": attempts,
        }
        if args.as_json:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    files = []
    for path in sorted(snapshot.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "path": path.relative_to(snapshot).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )

    result = {
        "schema": "mindforge-local-hf-prefetch-v1",
        "status": "PASS",
        "model_id": config.model.id,
        "revision": config.model.revision,
        "snapshot_path_tail": snapshot.name,
        "snapshot_path_tail_matches_revision": snapshot.name == config.model.revision,
        "allow_patterns": ALLOW_PATTERNS,
        "attempts": attempts,
        "file_count": len(files),
        "snapshot_manifest_hash": sha256_object(files),
        "files": files,
    }
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["snapshot_path_tail_matches_revision"] and files else 3


if __name__ == "__main__":
    raise SystemExit(main())
