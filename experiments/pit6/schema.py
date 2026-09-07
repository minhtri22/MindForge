from dataclasses import dataclass

@dataclass
class Experience:
    id: int; context: str; action: str; outcome: float; feedback: str; timestamp: int

@dataclass
class Pattern:
    description: str; evidence: list; confidence: float

@dataclass
class TeachingSignal:
    observed_pattern: str; evidence: list; recommendation: str; confidence: float; uncertainty: float

@dataclass
class DecisionCase:
    context: str; choices: list; expected_outcome: str
