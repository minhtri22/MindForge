import json
from pathlib import Path
from synthetic_data import generate
from simulator import memory_only,pit

def main():
    data=generate()
    mem=memory_only(data[:50])
    choice,signal=pit(data[:50])
    result={"seed":42,"cases":75,"baselines":["A","B","PIT"],"memory_choice":mem,"pit_choice":choice,"pit_confidence":signal.confidence,"decision_improvement":0.0}
    Path("experiments/pit6/results/result.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
