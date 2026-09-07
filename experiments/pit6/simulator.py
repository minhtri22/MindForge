from schema import Pattern, TeachingSignal

def run(history, choice):
    return choice

def memory_only(history):
    a=sum(1 for x in history if x.action=="A")
    return "A" if a>=len(history)/2 else "B"

def pit(history):
    a=sum(1 for x in history if x.action=="A")
    confidence=a/len(history)
    signal=TeachingSignal("repeat preference",history,"A" if confidence>=0.5 else "B",confidence,1-confidence)
    return signal.recommendation, signal
