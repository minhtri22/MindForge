from dataclasses import dataclass

@dataclass
class Experience:
    id:int; scenario:str; pattern:str; action:str; outcome:str; corrected:bool=False

@dataclass
class TeachingSignal:
    pattern:str; recommendation:str; confidence:float; uncertainty:float
