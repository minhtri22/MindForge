import json, pathlib, statistics
root=pathlib.Path('artifacts/learner_benchmark/EXP-LRN-001')
comp=json.load(open(root/'comparison_results.json',encoding='utf-8'))
rows=comp['rows']
print('ROW_KEYS', sorted(rows[0].keys()))
for lid in ['L0','L1','L2','L3','L4']:
    xs=[r for r in rows if r['learner_id']==lid]
    print('\n'+lid)
    for env in ['ENV-1','ENV-2','ENV-3','ENV-4']:
        es=[r for r in xs if r['environment_id']==env]
        def vals(k): return [r[k] for r in es if r.get(k) is not None]
        print(env, {
            'acc': round(statistics.mean(vals('accuracy')),4) if vals('accuracy') else None,
            'unseen': round(statistics.mean(vals('unseen_score')),4) if vals('unseen_score') else None,
            'gen_delta': round(statistics.mean(vals('generalization_delta')),4) if vals('generalization_delta') else None,
            'ctx_leaks': sum(bool(r.get('context_leakage')) for r in es),
            'nuis_leaks': sum(bool(r.get('nuisance_leakage')) for r in es),
            'doN': round(statistics.mean(vals('do_N_response')),4) if vals('do_N_response') else None,
            'doZ': round(statistics.mean(vals('do_Z_response')),4) if vals('do_Z_response') else None,
        })
terms=['counterfactual','do(A)','parameter_count','model_size','complexity','compression_ratio','raw_dim','invariant_dim']
for term in terms:
    hits=[]
    for p in [pathlib.Path('benchmark/M3_PROTOCOL.md'), pathlib.Path('theory.md'), pathlib.Path('PLAN.md')]:
        txt=p.read_text(encoding='utf-8',errors='ignore')
        if term.lower() in txt.lower(): hits.append(str(p))
    print('TERM',term,'docs',hits)
p=root/'full/L0-ENV-3-S42/results.json'
r=json.load(open(p,encoding='utf-8'))
print('ENV3 result top keys',list(r.keys()))
print('eval keys',list(r['evaluation'].keys()))
print('gen keys',list(r['evaluation']['generation_metrics'].keys()))
print('generalization keys',list(r['evaluation']['generalization'].keys()))
print('causal keys',list(r['causal_validation'].keys()))
