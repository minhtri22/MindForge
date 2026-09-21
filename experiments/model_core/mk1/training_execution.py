"""Locked MK-1 scientific training execution wrapper."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from mindforge.tokenizer import sha256_file

from .trainer import load_paired_initialization, train_arm

BUNDLE_RUN_ID = 35_581_007_427
BUNDLE_ARTIFACT_ID = 10_629_399_106
BUNDLE_ARTIFACT_DIGEST = "56d8f5b9b185215ac744a8299184db666b6018b6fefa7b02488d11e1b2abf7af"

EXPECTED_FILES = {
    "train.jsonl": "5bf1b1b5a193ce46baee9aee97e7e03a1e8c2f66bee8216c30cf518a6fb1468a",
    "validation.jsonl": "8c1eed22186d43b3311c7bbb63edfce7ba13880a11c528529bc411b9062a1495",
    "mk1-tokenizer.json": "e91c26992c5eafbb33ca1f6c0d2f40b8c79361dc57c95d0a265123ca70974829",
    "paired_init_seed_71001.pt": "b74b7ab8a67a11c076a94f9df5325a616231acdb99639c3a94424d65382dd8e8",
    "paired_init_seed_71002.pt": "7b2dcc6ab1cd377fedc6a0eb32809719fcac911cfb4cbd235684f9b4f10b621e",
    "paired_init_seed_71003.pt": "774ad2e2e5f0dddac8bfd67ee04537854309c983043314c82d5841e7a82ca860",
    "paired_init_seed_71004.pt": "25a96874e33828d9e9dd5de85a98a12028632d138c40c6f3a70760e0ff0b3d32",
    "paired_init_seed_71005.pt": "76c427debc7e68012fe5be6b5bf409c8ac49fff9bc2346e6b022befdf37c3730",
    "schedule_seed_71001.jsonl": "18262d3bec5fde01ebdb43bac7afb8142c32dd2aecff8245800435202270eaac",
    "schedule_seed_71002.jsonl": "8de8516dd6802106d4cf7fe36745a8636e888d9c5c711d76c7870fc2582f64b3",
    "schedule_seed_71003.jsonl": "3e5eb4ba3dbb297ce2176361544773db54ca8a1c3e3ddb89aa1367049bd18077",
    "schedule_seed_71004.jsonl": "e4839585f54ad14f02bd8c029d3461b6cb25063f044408cc5eeee08a8d064c5e",
    "schedule_seed_71005.jsonl": "52b5ce49529db34761d093cc8aa5c0a04ae19e6224e5d80e8bcf998f8dc435d9",
}
MANIFEST_NAME = "TRAINING_BUNDLE_MANIFEST.json"

STATE_SHA256 = {
    71001: "c8a7fbf63e0df8a827ff7c9291d4955db9a59b14ad1d28387fffa00e0b7a2ad7",
    71002: "04cd00ce71965649281c618212c120c165d6283519eab2d9f13beb22110f674d",
    71003: "f3ffadfa63e011bf691ac2e0f86a67eb023606d19a875104b77ea40d35577beb",
    71004: "2f1d93bf7119ffb67c939e3c6235054232854d59ab4151e5b95ae6e2828d931d",
    71005: "e553c8aa984a7b7040e392776f5a35aa6925658dbb932bc5777a0e5f35d326ab",
}
SCHEDULE_SHA256 = {
    seed: EXPECTED_FILES[f"schedule_seed_{seed}.jsonl"]
    for seed in STATE_SHA256
}
EXPECTED_PROCESSED_TOKENS = 6_457_260


def _sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def expected_bundle_names() -> set[str]:
    return set(EXPECTED_FILES) | {MANIFEST_NAME}


def verify_bundle(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise FileNotFoundError(f"training bundle directory missing: {root}")
    actual = {path.name for path in root.iterdir() if path.is_file()}
    expected = expected_bundle_names()
    if actual != expected:
        raise ValueError(
            f"training bundle file-set mismatch missing={sorted(expected-actual)} "
            f"unexpected={sorted(actual-expected)}"
        )
    observed: dict[str, str] = {}
    for name, digest in EXPECTED_FILES.items():
        got = _sha256_path(root / name)
        if got != digest:
            raise ValueError(f"training bundle hash mismatch for {name}")
        observed[name] = got

    manifest = json.loads((root / MANIFEST_NAME).read_text(encoding="utf-8"))
    if manifest.get("schema") != "MK1-TRAINING-BUNDLE-v0.1":
        raise ValueError("training bundle manifest schema mismatch")
    manifest_files = manifest.get("files")
    if not isinstance(manifest_files, dict) or set(manifest_files) != set(EXPECTED_FILES):
        raise ValueError("training bundle manifest file set mismatch")
    for name, digest in EXPECTED_FILES.items():
        if manifest_files[name].get("sha256") != digest:
            raise ValueError(f"training bundle manifest hash mismatch for {name}")
    if manifest.get("scientific_training_executed") is not False:
        raise ValueError("training bundle provenance flag mismatch")

    return {
        "schema": manifest["schema"],
        "artifact_run_id": BUNDLE_RUN_ID,
        "artifact_id": BUNDLE_ARTIFACT_ID,
        "artifact_digest": BUNDLE_ARTIFACT_DIGEST,
        "file_count": len(actual),
        "verified_files": observed,
    }


def verify_seed_contract(root: Path, seed: int) -> dict[str, str]:
    if seed not in STATE_SHA256:
        raise ValueError("seed outside frozen scientific seed set")
    init_path = root / f"paired_init_seed_{seed}.pt"
    schedule_path = root / f"schedule_seed_{seed}.jsonl"
    init_file_sha = sha256_file(init_path)
    schedule_sha = sha256_file(schedule_path)
    if init_file_sha != EXPECTED_FILES[init_path.name]:
        raise ValueError("paired initialization file SHA-256 mismatch")
    if schedule_sha != SCHEDULE_SHA256[seed]:
        raise ValueError("schedule file SHA-256 mismatch")
    _state, state_sha = load_paired_initialization(init_path, seed)
    if state_sha != STATE_SHA256[seed]:
        raise ValueError("paired initialization state SHA-256 mismatch")
    return {
        "paired_init_file_sha256": init_file_sha,
        "paired_state_sha256": state_sha,
        "schedule_sha256": schedule_sha,
    }


def execute(
    *,
    arm: Literal["direct", "m1z"],
    seed: int,
    bundle_root: Path,
    run_dir: Path,
) -> dict[str, Any]:
    if arm not in ("direct", "m1z"):
        raise ValueError("arm must be direct or m1z")
    bundle = verify_bundle(bundle_root)
    seed_contract = verify_seed_contract(bundle_root, seed)
    result = train_arm(
        arm=arm,
        seed=seed,
        paired_initialization_path=bundle_root / f"paired_init_seed_{seed}.pt",
        tokenizer_path=bundle_root / "mk1-tokenizer.json",
        train_records_path=bundle_root / "train.jsonl",
        validation_records_path=bundle_root / "validation.jsonl",
        schedule_path=bundle_root / f"schedule_seed_{seed}.jsonl",
        expected_schedule_sha256=SCHEDULE_SHA256[seed],
        run_dir=run_dir,
    )
    if int(result["processed_input_tokens"]) != EXPECTED_PROCESSED_TOKENS:
        raise AssertionError("completed training token total disagrees with frozen budget")
    if result["schedule_sha256"] != SCHEDULE_SHA256[seed]:
        raise AssertionError("completed training schedule provenance mismatch")
    result["bundle"] = bundle
    result["seed_contract"] = seed_contract
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("direct", "m1z"))
    parser.add_argument("--seed", type=int)
    parser.add_argument("--bundle-root", required=True)
    parser.add_argument("--run-dir")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    root = Path(args.bundle_root)
    if args.verify_only:
        print(json.dumps(verify_bundle(root), indent=2, sort_keys=True))
        return 0

    if args.arm is None or args.seed is None or args.run_dir is None:
        parser.error("--arm, --seed and --run-dir are required unless --verify-only is used")
    result = execute(
        arm=args.arm,
        seed=args.seed,
        bundle_root=root,
        run_dir=Path(args.run_dir),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
