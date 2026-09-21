"""One-shot Q8_0 execution entry point for the M5Q program."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline.m5q import run_q8_qualification


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--runs-root", required=True)
    parser.add_argument("--llama-source", required=True)
    parser.add_argument("--llama-cli", required=True)
    parser.add_argument("--llama-quantize", required=True)
    parser.add_argument("--converter-python", required=True)
    parser.add_argument("--build-manifest", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = run_q8_qualification(
        args.config,
        Path(args.workspace),
        args.runs_root,
        llama_source=args.llama_source,
        llama_cli=args.llama_cli,
        llama_quantize=args.llama_quantize,
        converter_python=args.converter_python,
        build_manifest=args.build_manifest,
    )

    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"M5Q Q8_0 qualification: {result['status']}")
        print(f"result_hash={result['result_hash']}")

    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
