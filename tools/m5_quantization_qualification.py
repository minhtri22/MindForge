"""One-shot Q8_0 / Q4_K_M qualification from the closed F16 parent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pipeline.canonical import sha256_object
from pipeline.io import atomic_write_json
from pipeline.loader import load_experiment_config
from pipeline.m5 import run_m5_qualification, single_file_gguf_identity


EXPECTED_TARGETS = ("q8_0", "q4_k_m")


def exact_adjudicated_target_membership(value: Any) -> bool:
    """Ignore canonical JSON key order but reject missing/extra target IDs."""
    return (
        isinstance(value, dict)
        and len(value) == len(EXPECTED_TARGETS)
        and set(value.keys()) == set(EXPECTED_TARGETS)
    )


def read_obj(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


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

    root = Path(args.workspace).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (root / config_path).resolve()

    qlock = read_obj(
        root / "docs/model-training-pipeline/quantization/m5_quantization.lock.json"
    )
    parent = qlock["parent"]
    closure = read_obj(root / parent["closure_evidence_path"])
    boundary = closure["boundary_after_closure"]

    if closure.get("verdict") != "PASS":
        raise RuntimeError("F16 parent closure is not PASS")
    if closure["result"]["result_hash"] != parent["result_hash"]:
        raise RuntimeError("F16 parent result hash drift")
    if boundary.get("q8_q4_qualification_may_open") is not True:
        raise RuntimeError("F16 parent does not authorize quantization qualification")
    if boundary.get("m6_authorized") is not False:
        raise RuntimeError("M6 must remain closed")
    if boundary.get("bulk_training_authorized") is not False:
        raise RuntimeError("bulk training must remain closed")

    config = load_experiment_config(config_path, root)
    targets = tuple(str(x).lower() for x in config.export["gguf"].get("quantize", []))
    if targets != EXPECTED_TARGETS:
        raise RuntimeError(f"target set drifted: {targets}")

    result = run_m5_qualification(
        config_path,
        root,
        args.runs_root,
        llama_source=args.llama_source,
        llama_cli=args.llama_cli,
        llama_quantize=args.llama_quantize,
        converter_python=args.converter_python,
        build_manifest=args.build_manifest,
        expected_high_fidelity_identity=parent["f16"],
    )

    m5_dir = result.run_dir / "m5"
    adjudication = read_obj(m5_dir / "m5_adjudication.json")
    quant = adjudication.get("quantized_targets", {})
    if not exact_adjudicated_target_membership(quant):
        observed = tuple(quant.keys()) if isinstance(quant, dict) else type(quant).__name__
        raise RuntimeError(f"adjudicated target set drifted: {observed}")

    identities: dict[str, dict[str, Any]] = {}
    for target in EXPECTED_TARGETS:
        identity = single_file_gguf_identity(quant[target]["artifact_manifest"])
        if identity is None:
            raise RuntimeError(f"{target} did not produce one GGUF artifact")
        identities[target] = identity

    f16 = parent["f16"]
    compression_ordering = (
        int(identities["q4_k_m"]["size"])
        < int(identities["q8_0"]["size"])
        < int(f16["size"])
    )
    distinct_hashes = len(
        {
            str(f16["sha256"]),
            str(identities["q8_0"]["sha256"]),
            str(identities["q4_k_m"]["sha256"]),
        }
    ) == 3

    gates = {
        "closed_f16_parent": closure.get("verdict") == "PASS",
        "exact_f16_parent_identity": adjudication["gates"][
            "high_fidelity_parent_identity"
        ]["pass"],
        "q8_0_real_runtime_preservation": quant["q8_0"]["parity"]["pass"],
        "q4_k_m_real_runtime_preservation": quant["q4_k_m"]["parity"]["pass"],
        "strict_compression_ordering": compression_ordering,
        "distinct_artifact_hashes": distinct_hashes,
        "bulk_training_not_started": adjudication["public_bulk_download_started"] is False,
        "m6_remains_closed": True,
    }
    failed = [name for name, passed in gates.items() if not passed]
    passed = not failed

    summary = {
        "schema": "mindforge-model-pipeline-m5-quantization-qualification-v1",
        "status": "PASS" if passed else "FAIL",
        "parent": {
            "closure_commit": parent["closure_commit"],
            "qualified_scientific_commit": parent["qualified_scientific_commit"],
            "result_hash": parent["result_hash"],
            "f16": f16,
        },
        "run_id": result.run_id,
        "llama_cpp_commit": result.llama_cpp_commit,
        "targets": {
            target: {
                "artifact_identity": identities[target],
                "parity": quant[target]["parity"],
            }
            for target in EXPECTED_TARGETS
        },
        "gates": {
            name: {"required": True, "pass": bool(value)}
            for name, value in gates.items()
        },
        "failed_required_gates": failed,
        "quantization_executed": True,
        "quantization_qualified": passed,
        "absolute_capability_claimed": False,
        "m6_authorized": False,
        "bulk_training_authorized": False,
        "next_action": (
            "POST_QUANTIZATION_GOVERNANCE_DECISION"
            if passed
            else "DECOMPOSE_FAILED_REQUIRED_GATE_NO_RESCUE"
        ),
    }
    summary["result_hash"] = sha256_object(summary)
    atomic_write_json(m5_dir / "M5_QUANTIZATION_QUALIFICATION_RESULT.json", summary)

    for path in (
        m5_dir / "gguf/model-f16.gguf",
        m5_dir / "gguf/model-q8_0.gguf",
        m5_dir / "gguf/model-q4_k_m.gguf",
    ):
        if path.exists():
            path.unlink()

    if args.as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"M5 quantization qualification: {summary['status']}")
        print(f"result_hash={summary['result_hash']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
