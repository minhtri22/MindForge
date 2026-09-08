"""
Benchmark baselines package init.
"""

from .b0 import B0_ERM
from .b1 import B1_DomainGeneralization
from .b2 import B2_EncoderRepresentation
from .b3 import B3_InvariantOnly
from .b4 import B4_OIR_PPV
from .b5 import B5_OracleInvariant

__all__ = [
    "B0_ERM",
    "B1_DomainGeneralization",
    "B2_EncoderRepresentation",
    "B3_InvariantOnly",
    "B4_OIR_PPV",
    "B5_OracleInvariant",
]

BASELINE_MAP = {
    "B0": B0_ERM,
    "B1": B1_DomainGeneralization,
    "B2": B2_EncoderRepresentation,
    "B3": B3_InvariantOnly,
    "B4": B4_OIR_PPV,
    "B5": B5_OracleInvariant,
}