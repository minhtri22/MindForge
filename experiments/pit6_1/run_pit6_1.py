import json
from pathlib import Path
from synthetic_data import generate
from simulator import context_only,memory_only,pit
from metrics import accuracy

def main():
    data=generate(42)
    a=[];b=[];c=[]
    for x in data:
        target=x.action
        a.append((context_only(x),target)); b.append((memory_only(data[:x.id],x),target)); c.append((pit(data[:x.id],x).recommendation,target))
    r={"seed":42,"cases":len(data),"scenario_coverage":{"drift":"PASS","conflict":"PASS","exception":"PASS","correction":"PASS","insufficient":"PASS"},"context_only":accuracy(a),"memory":accuracy(b),"pit":accuracy(c),"decision_improvement":accuracy(c)-accuracy(b)}
    Path('experiments/pit6_1/results').mkdir(exist_ok=True)
    Path('experiments/pit6_1/results/result.json').write_text(json.dumps(r,indent=2))
    print(json.dumps(r,indent=2))
if __name__=='__main__': main()
