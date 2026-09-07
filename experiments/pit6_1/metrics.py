def accuracy(preds):
    return sum(p==t for p,t in preds)/len(preds)

def rate(a,b): return a/b if b else 0
