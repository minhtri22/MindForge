#!/usr/bin/env python3
"""Audit interrupted V4 evidence, then run held-out once on the same server.

No resume or retry is supported for held-out. A start marker is created before
the first request; an existing marker prevents a second evaluation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import psutil

from run_qwen38_vulkan_isolation_retry import (
    Runner, PROMPT_SHA256, read_jsonl, sha256_file, write_json,
)
from run_qwen38_track_a_reference_eval import parse_prediction, prompt_for

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'runs/track-a-qwen38-reference-v1-vulkan-retry'
BENCH = ROOT / 'benchmarks/track-a-capability-v1'


def load(name):
    return json.loads((OUT / name).read_text(encoding='utf-8-sig'))


def audit_v4():
    phases = [load(n) for n in ['v0-smoke.json', 'v1-sequential-10.json',
                               'v2-calibration-20.json', 'v3-determinism.json']]
    assert all(d['pass'] and d['pid'] == 28096 and d['pid_unchanged'] for d in phases)
    prefix = [phases[0]['result']] + phases[1]['rows'] + phases[2]['rows']
    prefix += phases[3]['pass1'] + phases[3]['pass2']
    lines = (OUT / 'server.stderr.log').read_text(encoding='utf-8').splitlines()
    messages = [json.loads(l.split('D Parsed message: ', 1)[1]) for l in lines
                if 'D Parsed message: ' in l]
    assert len(messages) == 491, 'Unexpected pre-heldout log response count'
    assert all(a['content'] == b['raw_output'] for a, b in zip(messages[:71], prefix))
    cancels = [i for i, l in enumerate(lines) if 'cancel task' in l]
    assert len(cancels) == 1
    assert sum('D Parsed message: ' in l for l in lines[:cancels[0]]) == 328
    resumed = read_jsonl(OUT / 'v4-development-resume-258.jsonl')
    checkpoint = load('v4-development-resume-258.json')
    dev = read_jsonl(BENCH / 'development.jsonl')
    assert len(dev) == 420 and len(resumed) == 163
    assert checkpoint['pass'] and checkpoint['pid'] == 28096 and checkpoint['pid_unchanged']
    assert [r['case_id'] for r in resumed] == [c['case_id'] for c in dev[257:]]
    assert all(r['status'] == 'ok' and r['server_alive_after'] for r in resumed)
    assert all(m['content'] == r['raw_output'] for m, r in zip(messages[-163:], resumed))
    recovered = []
    for case, message in zip(dev[:257], messages[71:328]):
        pred, status = parse_prediction(message['content'])
        recovered.append({'case_id': case['case_id'], 'raw_output': message['content'],
                          'prediction': pred, 'parse_status': status,
                          'evidence_source': 'server_log_order_reconstruction',
                          'http_status': None, 'elapsed_seconds': None})
    # These are server-side completions, not reconstructed HTTP/client measurements.
    result = {'phase': 'V4', 'pass': True, 'pid': 28096,
              'total_expected': 420, 'completed_cases': 420,
              'client_rows_available': 163, 'server_log_recovered_rows': 257,
              'client_interrupted_attempts': 1, 'server_restarts': 0,
              'transport_success_user_attested': 420,
              'transport_success_direct_client_evidence': 163,
              'transport_errors_full_run': None,
              'concurrency': 1, 'pid_unchanged': True,
              'qualification_basis': 'User confirmed full completion; 491 ordered server responses corroborate 71 pre-V4 plus 420 V4 completions, same server lifetime.',
              'caveat': 'Client interrupted case 258 before completion; resumed at 258 on the same PID. Original 257 HTTP records were not checkpointed. Do not claim zero total interrupted requests.',
              'parsed': sum(r['parse_status'].startswith('json') for r in recovered + resumed),
              'rows': recovered + resumed,
              'resume_summary': checkpoint['summary']}
    write_json(OUT / 'v4-development.json', result)
    write_json(OUT / 'vulkan-isolation-verdict.json', {
        'v0': 'PASS', 'v1': 'PASS', 'v2': 'PASS', 'v3': 'PASS', 'v4': 'PASS',
        'vulkan_verdict': 'STABLE UNDER ISOLATION',
        'heldout': 'NOT RUN', 'reference_verdict': 'NOT EVALUATED',
        'v4_client_interruption_disclosed': True,
        'v4_evidence_caveat': result['caveat']})


def check_isolation(pid, created):
    proc = psutil.Process(pid)
    assert proc.create_time() == created and proc.is_running(), 'Server lifetime changed'
    found = []
    for p in psutil.process_iter(['pid', 'name']):
        n = (p.info['name'] or '').lower()
        if any(s in n for s in ['ollama', 'llama', 'lmstudio', 'kobold']):
            found.append(p.info['pid'])
    assert found == [pid], f'Isolation violation: {found}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--execute', action='store_true')
    a = ap.parse_args()
    if (OUT / 'heldout-start.json').exists():
        raise SystemExit('Held-out start marker exists: rerun forbidden')
    audit_v4()
    print('V0-V4 evidence audited; V4 client interruption explicitly disclosed.', flush=True)
    if not a.execute:
        return
    cfg = load('server-config.json')
    pid = cfg['server_pid']
    proc = psutil.Process(pid)
    created = proc.create_time()
    check_isolation(pid, created)
    prompt = ROOT / 'runs/track-a-qwen38-reference-v1/prompt-template.txt'
    assert sha256_file(prompt) == PROMPT_SHA256
    hashes = json.loads((BENCH / 'manifest.json').read_text(encoding='utf-8'))['hashes']
    for name, expected in hashes.items():
        assert sha256_file(BENCH / name) == expected, name
    model = load('model-check.json')
    assert sha256_file(Path(model['path'])) == model['expected_sha256']
    cases = read_jsonl(BENCH / 'test.jsonl')
    assert len(cases) == 700 and len({c['case_id'] for c in cases}) == 700
    # Validate prompt construction for every case before sending any held-out request.
    for c in cases:
        prompt_for(c)
    freeze = {'pid': pid, 'server_create_time': created, 'command': proc.cmdline(),
              'model_sha256': model['expected_sha256'], 'prompt_sha256': PROMPT_SHA256,
              'binary_sha256': sha256_file(Path(proc.exe())), 'benchmark_hashes': hashes,
              'temperature': 0, 'seed': 20260904, 'max_tokens': 128,
              'timeout_seconds': 300, 'concurrency': 1, 'context': 8192,
              'gpu_layers': 10, 'cache_k': 'f16', 'cache_v': 'f16',
              'started_epoch': time.time(), 'retry_allowed': False,
              'source_hashes': {n: sha256_file(ROOT / 'scripts' / n) for n in
                               ['run_qwen38_track_a_reference_eval.py',
                                'run_qwen38_vulkan_isolation_retry.py', 'score_track_a_v1.py']}}
    with (OUT / 'heldout-start.json').open('x', encoding='utf-8', newline='\n') as f:
        json.dump(freeze, f, indent=2)
    args = argparse.Namespace(pid=pid, outdir=OUT, base_url='http://127.0.0.1:8080',
                              timeout=300, max_tokens=128)
    runner = Runner(args)
    runner.monitor.start()
    rows = []
    failure = None
    try:
        with (OUT / 'heldout-predictions.jsonl').open('x', encoding='utf-8', newline='\n') as f:
            for index, case in enumerate(cases, 1):
                check_isolation(pid, created)
                row = runner.benchmark_row(case)
                row.update(index=index, pid=pid, recorded_epoch=time.time())
                f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
                f.flush()
                os.fsync(f.fileno())
                rows.append(row)
                write_json(OUT / 'heldout-progress.json', {
                    'completed': len(rows), 'expected': 700, 'last_case': case['case_id'],
                    'pid': pid, 'server_alive': runner.server_alive(),
                    'summary': Runner.summary_stats(rows), 'state': 'RUNNING'})
                print(json.dumps({'done': index, 'case_id': case['case_id'],
                                  'status': row['status']}), flush=True)
                if row['status'] != 'ok' or not row['server_alive_after']:
                    raise RuntimeError('Transport/server gate failed; no retry')
    except BaseException as exc:
        failure = repr(exc)
    finally:
        write_json(OUT / 'resource-summary-heldout.json', runner.monitor.stop())
    complete = len(rows) == 700 and failure is None and runner.server_alive()
    verdict = 'NOT EVALUATED'
    score = None
    if complete:
        # Invoke the canonical scorer, unchanged.
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        output = subprocess.check_output([sys.executable, str(ROOT/'scripts/score_track_a_v1.py'),
            '--cases', str(BENCH/'test.jsonl'), '--predictions', str(OUT/'heldout-predictions.jsonl')], env=env)
        score = json.loads(output)
        write_json(OUT/'heldout-score.json', score)
        verdict = 'ADMIT_STRONG_REFERENCE' if score['TUE_PASS'] else (
            'ADMIT_LIMITED_REFERENCE' if score['RVE_PASS'] else 'REJECT_AS_QUALITY_REFERENCE')
    write_json(OUT/'qualification-verdict.json', {
        'heldout': '700/700 COMPLETE' if complete else 'INVALID / INCOMPLETE',
        'completed': len(rows), 'reference_verdict': verdict, 'failure': failure,
        'pid': pid, 'server_alive': runner.server_alive(), 'summary': Runner.summary_stats(rows),
        'scope': {'ollama_used': False, 'benchmark_truth_changed': False,
                  'scorer_changed': False, 'model_kernel_changed': False,
                  'ppf_changed': False, 'n4_started': False, 'distillation_started': False}})
    print('FINAL ' + verdict, flush=True)
    if not complete:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
