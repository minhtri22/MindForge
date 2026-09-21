# MK-1 Scientific Training Trigger v0.1

TRIGGER_MK1_SCIENTIFIC_TRAINING_v0.1

Authorization basis:

- MK1_SCIENTIFIC_TRAINING_EXECUTION_LOCK_PASS
- execution-lock PASS commit: 59362f5ccba352b8a632475574359c85a5bffd52
- pre-trigger HEAD: d049617281bd0f120e55c5ef11e592424ef3fec8
- locked workflow blob: c2fe4076c237002c7da54b0099d93906370455e6
- immutable training bundle:
  - run 35581007427
  - artifact 10629399106
  - SHA-256 56d8f5b9b185215ac744a8299184db666b6018b6fefa7b02488d11e1b2abf7af
- matrix exactly 5 seeds × {DIRECT, M1-Z}
- 5000 optimizer steps per job
- accumulation 8
- validation every 250 steps
- no early stopping
- no confirmatory access

Scientific seeds:

71001
71002
71003
71004
71005

This trigger authorizes the first scientific optimizer execution for MK-1 under the frozen execution lock.
