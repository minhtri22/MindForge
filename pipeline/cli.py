"""Command line entry point for the zero-training M0 foundation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .errors import PipelineError
from .loader import load_experiment_config, load_model_profile
from .preflight import run_preflight
from .m1 import run_m1_qualification
from .semantic import validate_semantics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pipeline", description="Evidence-governed model pipeline M0")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="schema + semantic validation only")
    _common_config_args(validate)

    preflight = sub.add_parser("preflight", help="zero-training canonical resolve/hash/freeze")
    _common_config_args(preflight)
    preflight.add_argument("--runs-root", default="runs")
    preflight.add_argument("--json", action="store_true", dest="as_json")

    m1 = sub.add_parser("data-qualify", help="M1 zero-training data-plane qualification")
    _common_config_args(m1)
    m1.add_argument("--runs-root", default="runs")
    m1.add_argument("--json", action="store_true", dest="as_json")

    status = sub.add_parser("status", help="read an M0/M1 qualification result")
    status.add_argument("run_dir")

    return parser


def _common_config_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-c", "--config", required=True)
    parser.add_argument("--workspace", default=".")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            root = Path(args.workspace).resolve()
            path = Path(args.config)
            if not path.is_absolute():
                path = root / path
            config = load_experiment_config(path, root)
            profile = load_model_profile(config, root)
            validate_semantics(config, profile, root)
            print("PASS: schema + semantic validation")
            return 0
        if args.command == "preflight":
            result = run_preflight(args.config, args.workspace, args.runs_root)
            if args.as_json:
                print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
            else:
                print(f"PASS: {result.run_id}")
                print(f"run_dir={result.run_dir}")
                print(f"config_hash={result.config_hash}")
                print(f"preflight_contract_hash={result.preflight_contract_hash}")
            return 0
        if args.command == "data-qualify":
            result = run_m1_qualification(args.config, args.workspace, args.runs_root)
            if args.as_json:
                print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
            else:
                print(f"PASS: M1 {result.run_id}")
                print(f"run_dir={result.run_dir}")
                print(f"data_manifest_hash={result.data_manifest_hash}")
                print(f"resume_exact={result.resume_exact}")
            return 0
        if args.command == "status":
            path = Path(args.run_dir) / "preflight_result.json"
            print(path.read_text(encoding="utf-8"), end="")
            return 0
    except PipelineError as error:
        print(f"FAIL [{error.code}]: {error}", file=sys.stderr)
        return 2
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL [UNEXPECTED_INPUT]: {error}", file=sys.stderr)
        return 3
    return 1
