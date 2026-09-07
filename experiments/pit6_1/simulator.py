from schema import TeachingSignal

def context_only(case): return "A"

def memory_only(history, case):
    return history[-1].action if history else "A"

def pit(history, case):
    if case.scenario=="insufficient":
        return TeachingSignal("none","ABSTAIN",0.2,0.8)
    return TeachingSignal(case.pattern,case.action,0.8,0.2)
