import random
from schema import Experience

def generate(seed=42, n=75):
    random.seed(seed)
    prefs=["A","B"]
    data=[]
    for i in range(n):
        pref=prefs[0] if i < n*0.6 else prefs[1]
        if i in (10,35): pref="B" if pref=="A" else "A"
        data.append(Experience(i,"decision",pref,1.0 if pref=="A" else 0.0,"feedback",i))
    return data
