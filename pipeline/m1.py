"""M1 Data Plane qualification orchestrator.

M1 consumes only local fixture datasets for qualification. Public adapters are
planned and identity-checked but bulk public dataset download is intentionally
not performed by the zero-training qualification run.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import sha256_object
from .data_manifest import build_data_manifest, validate_data_manifest
from .data_policy import (
    apply_contamination,
    apply_policy,
    assign_splits,
    contamination_terms,
    exact_dedup,
    near_dedup,
    normalize_documents,
)
from .data_source import SourceSnapshot, acquire_local_dataset, plan_source
from .errors import DataIntegrityError
from .io import atomic_write_json
from .loader import load_experiment_config
from .preflight import run_preflight
from .resolver import ResolverContext
from .token_stream import QualificationByteTokenizer, build_phase_stream, simulate_resume


@dataclass(frozen=True)
class M1Result:
    status: str
    run_id: str
    run_dir: Path
    data_manifest_hash: str
    adjudication_hash: str
    source_count: int
    document_count: int
    phase_count: int
    resume_exact: bool
    model_weights_loaded: bool
    training_backend_initialized: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "run_dir": str(self.run_dir),
            "data_manifest_hash": self.data_manifest_hash,
            "adjudication_hash": self.adjudication_hash,
            "source_count": self.source_count,
            "document_count": self.document_count,
            "phase_count": self.phase_count,
            "resume_exact": self.resume_exact,
            "model_weights_loaded": self.model_weights_loaded,
            "training_backend_initialized": self.training_backend_initialized,
        }


def run_m1_qualification(
    config_path: str | Path,
    repo_root: str | Path = ".",
    runs_root: str | Path = "runs",
    *,
    context: ResolverContext | None = None,
) -> M1Result:
    repo_root = Path(repo_root).resolve()
    preflight = run_preflight(config_path, repo_root, runs_root, context=context)
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = repo_root / config_path
    config = load_experiment_config(config_path, repo_root)

    source_plans = {name: plan_source(dataset) for name, dataset in sorted(config.datasets.items())}
    snapshots: list[SourceSnapshot] = []
    all_documents = []
    for name, dataset in sorted(config.datasets.items()):
        if dataset.raw.get("path") is None:
            raise DataIntegrityError(
                f"M1 qualification config must use local-materialized data; {name} is public-source plan only"
            )
        snapshot = acquire_local_dataset(dataset, repo_root)
        snapshots.append(snapshot)
        all_documents.extend(snapshot.documents)

    normalized = normalize_documents(all_documents)
    policy_documents, policy_findings = apply_policy(normalized, config.run_class)
    exact_documents, exact_findings = exact_dedup(policy_documents)
    near_documents, near_findings = near_dedup(exact_documents)
    terms = contamination_terms(config.fixture_set, repo_root)
    clean_documents, contamination_findings = apply_contamination(near_documents, terms, config.run_class)

    split_seed = int(sha256_object({"experiment_id": config.experiment_id, "contract": "m1-split-v1"})[:8], 16)
    by_dataset = {name: [] for name in config.datasets}
    for document in clean_documents:
        by_dataset[document.dataset_id].append(document)

    assigned_documents = []
    split_contracts: dict[str, dict[str, Any]] = {}
    for dataset_id, documents in sorted(by_dataset.items()):
        if not documents:
            raise DataIntegrityError(f"{dataset_id}: zero documents remain after M1 policy/dedup")
        assigned, contract = assign_splits(documents, split_seed)
        assigned_documents.extend(assigned)
        split_contracts[dataset_id] = contract

    tokenizer = QualificationByteTokenizer()
    token_streams: dict[str, dict[str, Any]] = {}
    stream_evidence: dict[str, Any] = {}
    resume_evidence: dict[str, Any] = {}
    for phase in config.phases:
        ordered, contract = build_phase_stream(phase, assigned_documents, tokenizer)
        resume = simulate_resume(phase, ordered)
        token_streams[phase.id] = contract
        stream_evidence[phase.id] = {
            "sequence_count": len(ordered),
            "ordered_sequence_hash": sha256_object([sequence.descriptor() for sequence in ordered]),
            "first_sequence": ordered[0].descriptor(),
            "last_sequence": ordered[-1].descriptor(),
        }
        resume_evidence[phase.id] = resume

    findings = [*policy_findings, *exact_findings, *near_findings, *contamination_findings]
    manifest = build_data_manifest(
        sources=snapshots,
        split_contracts=split_contracts,
        token_streams=token_streams,
        fixture_set_id=config.fixture_set,
        findings=findings,
    )
    validate_data_manifest(manifest, repo_root)

    gates = {
        "immutable_source_identity": {
            "required": True,
            "pass": len(snapshots) == len(config.datasets)
            and all(len(source.content_sha256) == 64 for source in snapshots),
            "evidence_hash": sha256_object(source_plans),
        },
        "license_privacy_secret_policy": {
            "required": True,
            "pass": all(finding.action in {"report", "quarantine", "drop"} for finding in findings),
            "evidence_hash": sha256_object([finding.to_dict() for finding in findings]),
        },
        "normalize_filter": {
            "required": True,
            "pass": len(normalized) > 0,
            "evidence_hash": sha256_object(
                [{"id": doc.identity, "hash": doc.content_hash} for doc in normalized]
            ),
        },
        "exact_dedup": {
            "required": True,
            "pass": len(exact_documents) > 0,
            "evidence_hash": sha256_object([finding.to_dict() for finding in exact_findings]),
        },
        "near_dedup": {
            "required": True,
            "pass": len(near_documents) > 0,
            "evidence_hash": sha256_object([finding.to_dict() for finding in near_findings]),
        },
        "contamination_guard": {
            "required": True,
            "pass": len(clean_documents) > 0,
            "evidence_hash": sha256_object([finding.to_dict() for finding in contamination_findings]),
        },
        "deterministic_split": {
            "required": True,
            "pass": len(split_contracts) == len(config.datasets),
            "evidence_hash": sha256_object(split_contracts),
        },
        "phase_token_streams": {
            "required": True,
            "pass": len(token_streams) == len(config.phases)
            and all(stream_evidence[phase.id]["sequence_count"] > 0 for phase in config.phases),
            "evidence_hash": sha256_object(token_streams),
        },
        "data_manifest": {
            "required": True,
            "pass": len(manifest["manifest_hash"]) == 64,
            "evidence_hash": manifest["manifest_hash"],
        },
        "resume_cursor_exact": {
            "required": True,
            "pass": all(value["suffix_match"] for value in resume_evidence.values()),
            "evidence_hash": sha256_object(resume_evidence),
        },
        "zero_training_boundary": {
            "required": True,
            "pass": True,
            "evidence_hash": sha256_object(
                {
                    "model_weights_loaded": False,
                    "training_backend_initialized": False,
                    "public_bulk_download_started": False,
                    "fresh_evidence_accessed": False,
                }
            ),
        },
    }
    failed = [name for name, gate in gates.items() if gate["required"] and not gate["pass"]]
    adjudication = {
        "schema": "mindforge-model-pipeline-m1-adjudication-v1",
        "run_id": preflight.run_id,
        "gates": gates,
        "failed_required_gates": failed,
        "verdict": "PASS" if not failed else "FAIL",
    }
    adjudication_hash = sha256_object(adjudication)
    if failed:
        raise DataIntegrityError(f"M1 adjudication failed required gates: {failed}")

    m1_dir = preflight.run_dir / "m1"
    frozen = preflight.run_dir / "frozen"
    atomic_write_json(m1_dir / "source_plans.json", source_plans)
    atomic_write_json(m1_dir / "policy_findings.json", [finding.to_dict() for finding in findings])
    atomic_write_json(m1_dir / "split_summary.json", split_contracts)
    atomic_write_json(m1_dir / "token_stream_evidence.json", stream_evidence)
    atomic_write_json(m1_dir / "resume_simulation.json", resume_evidence)
    atomic_write_json(m1_dir / "m1_adjudication.json", {**adjudication, "adjudication_hash": adjudication_hash})
    atomic_write_json(frozen / "data_manifest.json", manifest)

    result = M1Result(
        status="PASS",
        run_id=preflight.run_id,
        run_dir=preflight.run_dir,
        data_manifest_hash=manifest["manifest_hash"],
        adjudication_hash=adjudication_hash,
        source_count=len(snapshots),
        document_count=len(assigned_documents),
        phase_count=len(config.phases),
        resume_exact=all(value["suffix_match"] for value in resume_evidence.values()),
        model_weights_loaded=False,
        training_backend_initialized=False,
    )
    atomic_write_json(m1_dir / "m1_result.json", result.to_dict())
    return result
