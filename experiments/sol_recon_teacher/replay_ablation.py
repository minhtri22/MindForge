from __future__ import annotations
import copy, json, random, time
from pathlib import Path
import torch
import torch.nn.functional as F
from mindforge import TransformerLM, ModelConfig, parameter_count
from experiments.sol_recon_teacher.sandbox_experiment import (
    ROOT, OUT, RULES, init_db, add_rules, build_train, evaluate, batchify, encode_example, train
)

REPORT=OUT/'replay_comparison.json'


def train_random(model, examples, steps, lr=1e-3, bs=8):
    model.train(); opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=.01); losses=[]; t=time.time()
    for _ in range(steps):
        x,y=batchify(examples,bs,model.config.max_context,'cpu'); logits=model(x)
        loss=F.cross_entropy(logits[:,:-1].reshape(-1,logits.size(-1)),y[:,1:].reshape(-1),ignore_index=-100)
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step(); losses.append(float(loss))
    return {'steps':steps,'loss_start':losses[0],'loss_end':losses[-1],'seconds':time.time()-t,'sampler':'random_all_10'}


def balanced_batch(old, new, bs, max_context, device):
    n_old=bs//2; n_new=bs-n_old
    chosen=random.sample(old,n_old)+random.sample(new,n_new); random.shuffle(chosen)
    xs=[]; ys=[]
    for q,l,a,_ in chosen:
        ids,lab=encode_example(q,l,a,max_context); xs.append(ids); ys.append(lab)
    L=max(map(len,xs)); x=torch.zeros((bs,L),dtype=torch.long); y=torch.full((bs,L),-100,dtype=torch.long)
    for i,(ids,lab) in enumerate(zip(xs,ys)):
        x[i,:len(ids)]=torch.tensor(ids); y[i,:len(lab)]=torch.tensor(lab)
    return x.to(device),y.to(device)


def train_replay(model, old, new, steps, lr=1e-3, bs=8):
    model.train(); opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=.01); losses=[]; t=time.time()
    for _ in range(steps):
        x,y=balanced_batch(old,new,bs,model.config.max_context,'cpu'); logits=model(x)
        loss=F.cross_entropy(logits[:,:-1].reshape(-1,logits.size(-1)),y[:,1:].reshape(-1),ignore_index=-100)
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step(); losses.append(float(loss))
    return {'steps':steps,'loss_start':losses[0],'loss_end':losses[-1],'seconds':time.time()-t,'sampler':'balanced_replay_4_old_4_new'}


def summary(ev):
    fam={}
    for row in ev['rows']:
        x=fam.setdefault(row['family'],[0,0]); x[1]+=1; x[0]+=int(row['pass'])
    old_ids=[r[0] for r in RULES[:5]]; new_ids=[r[0] for r in RULES[5:]]
    return {
        'overall':ev['score'],'passed':ev['passed'],'total':ev['total'],
        'old5_score':sum(v[0] for k,v in fam.items() if k in old_ids)/15,
        'new5_score':sum(v[0] for k,v in fam.items() if k in new_ids)/15,
        'families':{k:{'passed':v[0],'total':v[1],'score':v[0]/v[1]} for k,v in fam.items()}
    }


def main():
    torch.manual_seed(2026); random.seed(2026)
    cfg=ModelConfig(vocab_size=512,d_model=128,n_heads=4,n_layers=2,max_context=256,ff_mult=4,dropout=0.0)
    base=TransformerLM(cfg); con=init_db(True)
    n0=evaluate(base,con); add_rules(con,5); tr5=build_train(5,24)
    train5=train(base,tr5,180,lr=2e-3,bs=8); n5=evaluate(base,con)

    n5_state=copy.deepcopy(base.state_dict()); rng_state=random.getstate(); torch_rng=torch.random.get_rng_state()
    add_rules(con,10); all10=build_train(10,24)
    old5=[x for x in all10 if x[3] in [r[0] for r in RULES[:5]]]
    new5=[x for x in all10 if x[3] in [r[0] for r in RULES[5:]]]

    no_replay=TransformerLM(cfg); no_replay.load_state_dict(n5_state)
    random.setstate(rng_state); torch.random.set_rng_state(torch_rng)
    train_nr=train_random(no_replay,all10,300,lr=1e-3,bs=8); ev_nr=evaluate(no_replay,con)

    replay=TransformerLM(cfg); replay.load_state_dict(n5_state)
    random.setstate(rng_state); torch.random.set_rng_state(torch_rng)
    train_r=train_replay(replay,old5,new5,300,lr=1e-3,bs=8); ev_r=evaluate(replay,con)

    s0,s5,snr,sr=map(summary,[n0,n5,ev_nr,ev_r])
    report={
      'controlled_variables':{
        'seed':2026,'same_N5_checkpoint':True,'same_train_examples':True,'same_heldout':True,
        'same_N10_steps':300,'same_N10_lr':1e-3,'same_batch_size':8,
        'only_intended_change':'N10 sampling: random over all 10 families vs explicit 4-old/4-new rehearsal per batch'
      },
      'kernel':{'params':parameter_count(base),'config':cfg.__dict__},
      'N0':s0,'N5':s5,'N10_no_replay':snr,'N10_balanced_replay':sr,
      'delta_replay_vs_no_replay':{
        'overall_pp':(sr['overall']-snr['overall'])*100,
        'old5_retention_pp':(sr['old5_score']-snr['old5_score'])*100,
        'new5_learning_pp':(sr['new5_score']-snr['new5_score'])*100,
      },
      'train_N5':train5,'train_N10_no_replay':train_nr,'train_N10_replay':train_r,
      'rows_no_replay':ev_nr['rows'],'rows_replay':ev_r['rows']
    }
    REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    torch.save({'model':replay.state_dict(),'config':cfg.__dict__},OUT/'mindforge_teacher_n10_replay.pt')
    print(json.dumps({'N0':s0,'N5':s5,'N10_no_replay':snr,'N10_replay':sr,'delta':report['delta_replay_vs_no_replay']},indent=2))

if __name__=='__main__': main()
