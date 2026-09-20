from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from pipeline.canonical import sha256_file, sha256_object
from pipeline.data_manifest import validate_data_manifest
from pipeline.data_policy import (
    ProcessedDocument,
    apply_contamination,
    apply_policy,
    assign_splits,
    contamination_terms,
    exact_dedup,
    near_dedup,
    normalize_documents,
)
from pipeline.data_source import acquire_local_dataset, plan_source
from pipeline.errors import DataIntegrityError
from pipeline.loader import load_experiment_config
from pipeline.m1 import run_m1_qualification
from pipeline.models import RunClass
from pipeline.resolver import ResolverContext
from pipeline.token_stream import QualificationByteTokenizer, build_phase_stream, simulate_resume

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/model-training-pipeline"
SMOKE = DOCS / "examples/end_to_end_small.yaml"


def _config(path: Path = SMOKE):
    return load_experiment_config(path, ROOT)


def _doc(document_id: str, content: str, *, dataset: str = "x", license: str = "CC0-1.0"):
    acquired = type("D", (), {})()
    acquired.dataset_id = dataset
    acquired.document_id = document_id
    acquired.content = content
    acquired.license = license
    acquired.metadata = {"kind": "test"}
    return acquired


def test_public_source_plans_are_immutable():
    wiki = _config(DOCS / "examples/train_wikipedia_cpt.yaml")
    code = _config(DOCS / "examples/train_code_cpt.yaml")
    wiki_plan = plan_source(next(iter(wiki.datasets.values())))
    code_plan = plan_source(next(iter(code.datasets.values())))
    assert wiki_plan["snapshot"] == "enwiki-20260301-pages-articles-multistream"
    assert "latest" not in wiki_plan["snapshot"].lower()
    assert code_plan["revision"] == "35a59fb025bc0a102f7d96eac09d145b896d487b"
    assert len(code_plan["source_identity_hash"]) == 64


def test_local_acquisition_hashes_raw_fixture():
    config = _config()
    dataset = config.datasets["wiki_mini"]
    snapshot = acquire_local_dataset(dataset, ROOT)
    assert snapshot.content_sha256 == sha256_file(ROOT / dataset.raw["path"])
    assert len(snapshot.documents) == 3
    assert all(doc.license == "CC0-1.0" for doc in snapshot.documents)


def test_normalization_is_stable_and_unicode_nfc():
    docs = normalize_documents([_doc("a", "Cafe\u0301\r\nline  \x00")])
    assert docs[0].content == "Café\nline"
    assert docs[0].content_hash == sha256_object(docs[0].content) or len(docs[0].content_hash) == 64


def test_secret_scanner_quarantines_without_echoing_secret():
    secret = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
    docs = normalize_documents([_doc("a", f"token = {secret}", dataset="code")])
    accepted, findings = apply_policy(docs, RunClass.DEVELOPMENT)
    assert accepted == []
    payload = json.dumps([finding.to_dict() for finding in findings])
    assert secret not in payload
    assert any(finding.stage == "secret" and finding.action == "quarantine" for finding in findings)


def test_unknown_license_is_reported_in_development_and_quarantined_in_release():
    docs = normalize_documents([_doc("a", "clean text", license="UNKNOWN")])
    dev, dev_findings = apply_policy(docs, RunClass.DEVELOPMENT)
    rel, rel_findings = apply_policy(docs, RunClass.RELEASE)
    assert len(dev) == 1
    assert rel == []
    assert dev_findings[0].action == "report"
    assert rel_findings[0].action == "quarantine"


def test_exact_dedup_is_deterministic():
    docs = normalize_documents([_doc("b", "same"), _doc("a", "same"), _doc("c", "other")])
    kept, findings = exact_dedup(docs)
    assert [doc.document_id for doc in kept] == ["a", "c"]
    assert len(findings) == 1
    assert findings[0].action == "drop"


def test_near_dedup_drops_high_similarity_document():
    base = " ".join(f"token{i}" for i in range(80))
    almost = base + " extra"
    docs = normalize_documents([_doc("a", base), _doc("b", almost)])
    kept, findings = near_dedup(docs, shingle_size=5, threshold=0.90)
    assert [doc.document_id for doc in kept] == ["a"]
    assert len(findings) == 1
    assert findings[0].stage == "near_dedup"


def test_contamination_is_report_only_for_smoke_and_quarantine_for_release():
    terms = contamination_terms("tests/fixtures/eval_v1", ROOT)
    docs = normalize_documents([_doc("a", "Question: What is 17 + 25? Answer carefully.")])
    smoke, smoke_findings = apply_contamination(docs, terms, RunClass.SMOKE)
    release, release_findings = apply_contamination(docs, terms, RunClass.RELEASE)
    assert len(smoke) == 1
    assert release == []
    assert smoke_findings[0].action == "report"
    assert release_findings[0].action == "quarantine"


def test_split_is_stable_under_input_order():
    docs = normalize_documents([_doc("a", "one"), _doc("b", "two"), _doc("c", "three")])
    first, contract_a = assign_splits(docs, 12345)
    second, contract_b = assign_splits(reversed(docs), 12345)
    assert [(d.identity, d.split) for d in first] == [(d.identity, d.split) for d in second]
    assert contract_a == contract_b


def test_phase_scoped_pack_contracts_differ_between_cpt_and_reasoning():
    config = _config()
    snapshots = [acquire_local_dataset(ds, ROOT) for ds in config.datasets.values()]
    documents = normalize_documents(doc for snapshot in snapshots for doc in snapshot.documents)
    documents, _ = apply_policy(documents, config.run_class)
    documents, _ = exact_dedup(documents)
    documents, _ = near_dedup(documents)
    documents, _ = apply_contamination(documents, contamination_terms(config.fixture_set, ROOT), config.run_class)
    seed = int(sha256_object({"experiment_id": config.experiment_id, "contract": "m1-split-v1"})[:8], 16)
    assigned = []
    by_dataset = {name: [] for name in config.datasets}
    for document in documents:
        by_dataset[document.dataset_id].append(document)
    for name, values in by_dataset.items():
        split_docs, _ = assign_splits(values, seed)
        assigned.extend(split_docs)

    tokenizer = QualificationByteTokenizer()
    domain, domain_contract = build_phase_stream(config.phases[0], assigned, tokenizer)
    reasoning, reasoning_contract = build_phase_stream(config.phases[1], assigned, tokenizer)
    assert domain_contract["packing"]["cross_document"] is True
    assert reasoning_contract["packing"]["cross_document"] is False
    assert domain_contract["stream_hash"] != reasoning_contract["stream_hash"]
    assert domain and reasoning


def test_resume_cursor_simulation_is_exact():
    result = run_m1_qualification(
        SMOKE,
        ROOT,
        ROOT / ".tmp-m1-test-resume",
        context=ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32"),
    )
    resume = json.loads((result.run_dir / "m1/resume_simulation.json").read_text(encoding="utf-8"))
    assert all(item["suffix_match"] for item in resume.values())
    assert all(item["cursor"]["resume_fidelity"] == "exact" for item in resume.values())


def test_m1_manifest_validates_schema_and_self_hash(tmp_path: Path):
    result = run_m1_qualification(
        SMOKE,
        ROOT,
        tmp_path,
        context=ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32"),
    )
    manifest = json.loads((result.run_dir / "frozen/data_manifest.json").read_text(encoding="utf-8"))
    validate_data_manifest(manifest, ROOT)
    payload = dict(manifest)
    expected = payload.pop("manifest_hash")
    assert sha256_object(payload) == expected


def test_m1_qualification_is_idempotent(tmp_path: Path):
    context = ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32")
    first = run_m1_qualification(SMOKE, ROOT, tmp_path, context=context)
    second = run_m1_qualification(SMOKE, ROOT, tmp_path, context=context)
    assert first.run_id == second.run_id
    assert first.data_manifest_hash == second.data_manifest_hash
    assert first.resume_exact is True


def test_m1_qualification_preserves_zero_training_boundary(tmp_path: Path):
    result = run_m1_qualification(
        SMOKE,
        ROOT,
        tmp_path,
        context=ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32"),
    )
    assert result.status == "PASS"
    assert result.source_count == 3
    assert result.phase_count == 2
    assert result.model_weights_loaded is False
    assert result.training_backend_initialized is False
    assert (result.run_dir / "m1/m1_result.json").is_file()
    assert (result.run_dir / "frozen/data_manifest.json").is_file()


def test_public_bulk_config_is_planned_but_not_materialized_by_m1(tmp_path: Path):
    with pytest.raises(DataIntegrityError, match="public-source plan only"):
        run_m1_qualification(
            DOCS / "examples/train_wikipedia_cpt.yaml",
            ROOT,
            tmp_path,
            context=ResolverContext(backend="pytest", device_class="cpu", auto_precision="fp32"),
        )
