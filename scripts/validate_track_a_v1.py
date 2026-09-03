#!/usr/bin/env python3
import json, re
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"benchmarks"/"track-a-capability-v1"
def read(name):
    with (ROOT/name).open(encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]
def diff_paths(a,b,prefix=""):
    if type(a)!=type(b): return [prefix]
    out=[]
    if isinstance(a,dict):
        for k in sorted(set(a)|set(b)):
            p=f"{prefix}.{k}" if prefix else k
            if k not in a or k not in b: out.append(p)
            else: out += diff_paths(a[k],b[k],p)
    elif isinstance(a,list):
        if a!=b: out.append(prefix)
    elif a!=b: out.append(prefix)
    return out
def norm_utt(s):
    s=s.lower().strip(); s=re.sub(r"\s+"," ",s); s=re.sub(r"[.!?…]+$","",s); return s

def core_utt(s):
    s=norm_utt(s)
    prefixes=[
      'giúp tôi ','tôi cần ','làm giúp việc này: ','please ','i need you to ','could you ',
      'trong tình huống này, ','thực hiện yêu cầu sau: ','xử lý giúp tôi: ','làm theo ngữ cảnh này: ',
      'in this situation, ','using the supplied context, ','handle this request: ','given the current context, ',
      'trong context này, ','can you ','xử lý request này: ','theo current context, '
    ]
    changed=True
    while changed:
      changed=False
      for p in prefixes:
        if s.startswith(p): s=s[len(p):].strip(); changed=True; break
    for suf in [' giúp tôi',' được không',' luôn nhé',' nhé',' nha',' please',' for me',' if you can',' now',' pls']:
      if s.endswith(suf): s=s[:-len(suf)].strip()
    return s
cases=sum((read(x) for x in ["calibration.jsonl","development.jsonl","test.jsonl"]),[])
assert len(cases)==1400 and len({c['case_id'] for c in cases})==1400
assert Counter(c['family'] for c in cases)==Counter({f'A{i}':200 for i in range(1,8)})
assert Counter(c['split'] for c in cases)==Counter(calibration=280,development=420,test=700)
assert Counter(c['language_group'] for c in cases)==Counter(vi=840,vi_en=350,en=210)
assert Counter(c['difficulty'] for c in cases)==Counter(straightforward=560,contextual=490,adversarial=350)
for fam in [f'A{i}' for i in range(1,8)]:
    cs=[c for c in cases if c['family']==fam]
    assert Counter(c['language_group'] for c in cs)==Counter(vi=120,vi_en=50,en=30)
    assert Counter(c['difficulty'] for c in cs)==Counter(straightforward=80,contextual=70,adversarial=50)
    assert Counter(c['split'] for c in cs)==Counter(calibration=40,development=60,test=100)
    sets={s:{c['provenance']['template_id'] for c in cs if c['split']==s} for s in ['calibration','development','test']}
    assert not (sets['calibration'] & sets['test']), (fam,'template C/H leakage')
    assert not (sets['development'] & sets['test']), (fam,'template D/H leakage')
    utt={s:{norm_utt(c['input']['user_utterance']) for c in cs if c['split']==s} for s in ['calibration','development','test']}
    assert not (utt['calibration'] & utt['test']), (fam,'utterance C/H leakage',utt['calibration']&utt['test'])
    assert not (utt['development'] & utt['test']), (fam,'utterance D/H leakage',utt['development']&utt['test'])
    core={s:{core_utt(c['input']['user_utterance']) for c in cs if c['split']==s} for s in ['calibration','development','test']}
    assert not (core['calibration'] & core['test']), (fam,'core C/H leakage',core['calibration']&core['test'])
    assert not (core['development'] & core['test']), (fam,'core D/H leakage',core['development']&core['test'])
    enc=[json.dumps(c['input'],ensure_ascii=False,sort_keys=True) for c in cs]
    assert len(enc)==len(set(enc)), (fam,'exact-input duplicates')
held=[c for c in cases if c['split']=='test']
groups=defaultdict(list)
for c in held:
    if c['counterfactual_group_id']: groups[c['counterfactual_group_id']].append(c)
assert len(groups)==140 and sum(len(v) for v in groups.values())==280
for gid,pair in groups.items():
    assert len(pair)==2
    assert pair[0]['family']==pair[1]['family'] and pair[0]['language_group']==pair[1]['language_group'] and pair[0]['difficulty']==pair[1]['difficulty']
    changed=diff_paths(pair[0]['input'],pair[1]['input'])
    assert len(changed)==1,(gid,changed)
for c in cases:
    u=c['input']['user_utterance'].lower()
    if c['family'] in {'A2','A6'} and ('gọi tuấn' in u or 'call tuấn' in u or 'call tuan' in u):
        names=[x.get('name') for x in c['input']['personal_state'].get('contacts',[])]
        if names.count('Tuấn')==1:
            assert c['expected'].get('clarification_required') is False
for c in cases:
    if c['family']=='A5' and c.get('scoring',{}).get('text_source')=='utterance_payload':
        source=c['input']['user_utterance'].split(':',1)[1].strip().rstrip('.…')
        expected=c['expected']['arguments']['text']
        if expected is not None: assert source.lower().startswith(str(expected).lower().rstrip(' nha').rstrip(' pls')) or str(expected).lower() in source.lower(), (c['case_id'],source,expected)
assert all(c['provenance']['truth_source']=='rule_defined' for c in cases)
print(json.dumps({'status':'PASS','cases':len(cases),'counterfactual_groups':len(groups),'heldout_counterfactual_cases':280,'split_template_leakage':0,'split_exact_utterance_leakage':0},indent=2))
