from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Mapping

CONTRACT_VERSION = "mindforge-owrq-runtime-adapter-v1"


class AdapterError(RuntimeError):
    pass


def atomic_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def http_json(method: str, url: str, body: Mapping[str, Any] | None = None, timeout: int = 30) -> Dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return json.loads(raw.decode("utf-8"))


def probe_tags(host: str, timeout: int = 2) -> Dict[str, Any] | None:
    try:
        return http_json("GET", f"http://{host}/api/tags", timeout=timeout)
    except Exception:
        return None


def model_names(tags: Mapping[str, Any] | None) -> list[str]:
    if not tags:
        return []
    return sorted({str(m.get("name", "")) for m in tags.get("models", []) if m.get("name")})


def find_model(tags: Mapping[str, Any], requested: str) -> Dict[str, Any] | None:
    for model in tags.get("models", []):
        name = str(model.get("name", ""))
        if name == requested or name == requested + ":latest":
            return dict(model)
    return None


def child_environment(host: str, kv_cache_type: str) -> Dict[str, str]:
    env = dict(os.environ)
    env["OLLAMA_HOST"] = host
    env["OLLAMA_KV_CACHE_TYPE"] = kv_cache_type
    # Deliberately do not set or remove OLLAMA_FLASH_ATTENTION.
    return env


def start_server(ollama_exe: Path, host: str, evidence_dir: Path, kv_cache_type: str = "f16") -> Dict[str, Any]:
    if probe_tags(host) is not None:
        raise AdapterError(f"qualification/study host already occupied: {host}")

    evidence_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = evidence_dir / "ollama-serve.stdout.log"
    stderr_path = evidence_dir / "ollama-serve.stderr.log"
    stdout_f = stdout_path.open("ab", buffering=0)
    stderr_f = stderr_path.open("ab", buffering=0)
    env = child_environment(host, kv_cache_type)

    proc = subprocess.Popen(
        [str(ollama_exe), "serve"],
        stdout=stdout_f,
        stderr=stderr_f,
        stdin=subprocess.DEVNULL,
        env=env,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    stdout_f.close()
    stderr_f.close()

    for _ in range(60):
        tags = probe_tags(host)
        if tags is not None:
            return {
                "server_pid": proc.pid,
                "host": host,
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
                "OLLAMA_KV_CACHE_TYPE": kv_cache_type,
                "OLLAMA_FLASH_ATTENTION_observed_value": os.environ.get("OLLAMA_FLASH_ATTENTION"),
            }
        if proc.poll() is not None:
            raise AdapterError(f"ollama serve exited rc={proc.returncode}")
        time.sleep(1)

    terminate_server(proc.pid)
    raise AdapterError("ollama serve did not become healthy")


def terminate_server(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        try:
            os.kill(pid, 15)
        except ProcessLookupError:
            pass


def run_ollama_cli(
    ollama_exe: Path,
    host: str,
    args: list[str],
    cwd: Path | None,
    stdout_path: Path,
    stderr_path: Path,
    kv_cache_type: str = "f16",
) -> int:
    env = child_environment(host, kv_cache_type)
    with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
        cp = subprocess.run(
            [str(ollama_exe), *args],
            cwd=None if cwd is None else str(cwd),
            stdout=out,
            stderr=err,
            env=env,
            check=False,
        )
    return int(cp.returncode)


def load_qualified_scope(path: Path) -> Dict[str, Any]:
    scope = json.loads(path.read_text(encoding="utf-8"))
    if scope.get("schema") != "mindforge-owrq-qualified-runtime-scope-v1":
        raise AdapterError("invalid qualified runtime schema")
    if scope.get("status") != "QUALIFIED_RUNTIME_SCOPE":
        raise AdapterError("runtime scope is not qualified")
    adapter = scope.get("adapter", {})
    if adapter.get("contract_version") != CONTRACT_VERSION:
        raise AdapterError("adapter contract mismatch")
    return scope


def session_open(args: argparse.Namespace) -> int:
    scope = load_qualified_scope(Path(args.qualified_runtime))
    runtime = scope["runtime"]
    env_contract = scope["runtime_environment"]
    api = scope["api_contract"]

    ollama_exe = Path(runtime["ollama_executable_path"])
    if not ollama_exe.is_file():
        raise AdapterError("qualified ollama executable missing")
    if sha256_file(ollama_exe) != runtime["ollama_executable_sha256"]:
        raise AdapterError("qualified ollama executable SHA256 drift")
    if env_contract.get("OLLAMA_KV_CACHE_TYPE") != "f16":
        raise AdapterError("qualified KV-cache contract drift")
    if env_contract.get("OLLAMA_FLASH_ATTENTION_forced") is not False:
        raise AdapterError("qualified scope forces flash attention")

    evidence_dir = Path(args.evidence_dir)
    server = start_server(ollama_exe, api["host"], evidence_dir, "f16")
    tags = probe_tags(api["host"])
    initial_names = model_names(tags)
    rendered = {args.model_name, args.model_name + ":latest"}
    if any(n in rendered for n in initial_names):
        terminate_server(server["server_pid"])
        raise AdapterError("owned model namespace collision")

    package_dir = Path(args.modelfile_path).parent
    create_out = evidence_dir / "ollama-create.stdout.log"
    create_err = evidence_dir / "ollama-create.stderr.log"
    rc = run_ollama_cli(
        ollama_exe,
        api["host"],
        ["create", args.model_name, "-f", Path(args.modelfile_path).name],
        package_dir,
        create_out,
        create_err,
    )
    if rc != 0:
        terminate_server(server["server_pid"])
        raise AdapterError(f"ollama create failed rc={rc}")

    try:
        show = http_json("POST", f"http://{api['host']}/api/show", {"model": args.model_name}, timeout=30)
    except Exception:
        run_ollama_cli(
            ollama_exe,
            api["host"],
            ["rm", args.model_name],
            None,
            evidence_dir / "ollama-rm-after-show-failure.stdout.log",
            evidence_dir / "ollama-rm-after-show-failure.stderr.log",
        )
        terminate_server(server["server_pid"])
        raise

    session = {
        "schema": "mindforge-owrq-runtime-adapter-session-v1",
        "status": "READY",
        "contract_version": CONTRACT_VERSION,
        "host": api["host"],
        "server_pid": server["server_pid"],
        "ollama_executable_path": str(ollama_exe),
        "ollama_executable_sha256": runtime["ollama_executable_sha256"],
        "model_name": args.model_name,
        "initial_model_names": initial_names,
        "evidence_dir": str(evidence_dir),
        "kv_cache_type": "f16",
        "show_model": show.get("model_info", {}),
        "owned_model_created": True,
    }
    atomic_json(Path(args.session_out), session)
    return 0


def diagnostic_from_logs(session: Mapping[str, Any]) -> Dict[str, Any]:
    evidence_dir = Path(session["evidence_dir"])
    text = ""
    for name in ("ollama-serve.stdout.log", "ollama-serve.stderr.log"):
        p = evidence_dir / name
        if p.exists():
            text += p.read_text(encoding="utf-8", errors="replace") + "\n"
    patterns = [
        "quantized V cache requires flash_attn",
        "error starting llama-server",
        "Load failed",
        "exit status 1",
        "out of memory",
        "failed to allocate",
    ]
    hits = [p for p in patterns if p.lower() in text.lower()]
    return {"positive_infra_failure": bool(hits), "diagnostic_hits": hits}


def chat(args: argparse.Namespace) -> int:
    session = json.loads(Path(args.session_file).read_text(encoding="utf-8"))
    request = json.loads(Path(args.request_file).read_text(encoding="utf-8"))
    request["model"] = session["model_name"]
    transport_path = Path(args.transport_evidence_file)
    response_path = Path(args.response_file)

    try:
        response = http_json("POST", f"http://{session['host']}/api/chat", request, timeout=300)
        atomic_json(response_path, response)
        atomic_json(
            transport_path,
            {
                "schema": "mindforge-owrq-runtime-adapter-transport-v1",
                "status": "RESPONSE_RECEIVED",
                "positive_infra_failure": False,
            },
        )
        return 0
    except urllib.error.HTTPError as e:
        diag = diagnostic_from_logs(session)
        body = e.read().decode("utf-8", errors="replace")
        atomic_json(
            transport_path,
            {
                "schema": "mindforge-owrq-runtime-adapter-transport-v1",
                "status": "HTTP_ERROR",
                "http_status": e.code,
                "http_body": body,
                **diag,
            },
        )
        return 2
    except Exception as e:
        diag = diagnostic_from_logs(session)
        atomic_json(
            transport_path,
            {
                "schema": "mindforge-owrq-runtime-adapter-transport-v1",
                "status": "TRANSPORT_ERROR",
                "error_type": type(e).__name__,
                "error": str(e),
                **diag,
            },
        )
        return 2


def session_close(args: argparse.Namespace) -> int:
    session_path = Path(args.session_file)
    session = json.loads(session_path.read_text(encoding="utf-8"))
    evidence_dir = Path(session["evidence_dir"])
    ollama_exe = Path(session["ollama_executable_path"])
    cleanup = {
        "schema": "mindforge-owrq-runtime-adapter-cleanup-v1",
        "owned_cleanup_pass": False,
        "initial_final_model_sets_match": False,
        "owned_model_remove_return_code": None,
    }

    try:
        if session.get("owned_model_created"):
            rc = run_ollama_cli(
                ollama_exe,
                session["host"],
                ["rm", session["model_name"]],
                None,
                evidence_dir / "ollama-rm.stdout.log",
                evidence_dir / "ollama-rm.stderr.log",
            )
            cleanup["owned_model_remove_return_code"] = rc
            cleanup["owned_cleanup_pass"] = rc == 0
        else:
            cleanup["owned_cleanup_pass"] = True

        tags = probe_tags(session["host"], timeout=5)
        final_names = model_names(tags)
        cleanup["final_model_names"] = final_names
        cleanup["initial_final_model_sets_match"] = final_names == list(session["initial_model_names"])
    finally:
        terminate_server(int(session["server_pid"]))
        atomic_json(Path(args.cleanup_out), cleanup)

    return 0 if cleanup["owned_cleanup_pass"] and cleanup["initial_final_model_sets_match"] else 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    op = sub.add_parser("session-open")
    op.add_argument("--qualified-runtime", required=True)
    op.add_argument("--q4-path", required=True)
    op.add_argument("--modelfile-path", required=True)
    op.add_argument("--model-name", required=True)
    op.add_argument("--evidence-dir", required=True)
    op.add_argument("--session-out", required=True)

    ch = sub.add_parser("chat")
    ch.add_argument("--session-file", required=True)
    ch.add_argument("--request-file", required=True)
    ch.add_argument("--response-file", required=True)
    ch.add_argument("--transport-evidence-file", required=True)

    cl = sub.add_parser("session-close")
    cl.add_argument("--session-file", required=True)
    cl.add_argument("--cleanup-out", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.cmd == "session-open":
        return session_open(args)
    if args.cmd == "chat":
        return chat(args)
    if args.cmd == "session-close":
        return session_close(args)
    raise AdapterError("unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
