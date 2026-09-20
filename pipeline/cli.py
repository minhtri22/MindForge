"""Command line entry point for the evidence-governed model pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .errors import PipelineError
from .loader import load_experiment_config, load_model_profile
from .m1 import run_m1_qualification
from .preflight import run_preflight
from .semantic import validate_semantics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pipeline", description="Evidence-governed model pipeline")
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

    m2 = sub.add_parser("trainer-qualify", help="M2 real-model trainer/checkpoint qualification")
    _common_config_args(m2)
    m2.add_argument("--runs-root", default="runs")
    m2.add_argument("--json", action="store_true", dest="as_json")

    status = sub.add_parser("status", help="read the latest M0/M1/M2 qualification result")
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

        if args.command == "trainer-qualify":
            # Lazy import preserves the zero-ML-dependency M0/M1 boundary.
            from .m2 import run_m2_qualification

            result = run_m2_qualification(args.config, args.workspace, args.runs_root)
            if args.as_json:
                print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
            else:
                print(f"PASS: M2 {result.run_id}")
                print(f"run_dir={result.run_dir}")
                print(f"exact_resume_phases={result.exact_resume_phases}")
                print(f"canonical_directory_hash={result.canonical_directory_hash}")
                print(f"adjudication_hash={result.adjudication_hash}")
            return 0

        if args.command == "status":
            run_dir = Path(args.run_dir)
            candidates = [
                run_dir / "m2/m2_result.json",
                run_dir / "m1/m1_result.json",
                run_dir / "preflight_result.json",
            ]
            path = next((candidate for candidate in candidates if candidate.is_file()), candidates[-1])
            print(path.read_text(encoding="utf-8"), end="")
            return 0

    except PipelineError as error:
        print(f"FAIL [{error.code}]: {error}", file=sys.stderr)
        return 2
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL [UNEXPECTED_INPUT]: {error}", file=sys.stderr)
        return 3
    return 1
