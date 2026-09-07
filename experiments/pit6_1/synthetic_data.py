from schema import Experience

def generate(seed=42):
    cases=[]
    scenarios=["drift","conflict","exception","correction","insufficient"]
    for i in range(150):
        s=scenarios[i%5]
        if s=="drift": p,a="old_to_new","B"
        elif s=="conflict": p,a="conditional","B"
        elif s=="exception": p,a="exception","B"
        elif s=="correction": p,a="updated","B"
        else: p,a="unknown","ABSTAIN"
        cases.append(Experience(i,s,p,a,"success",s=="correction"))
    return cases
