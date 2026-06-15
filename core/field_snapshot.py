from dataclasses import dataclass, field
from typing import Dict, List
from .modality_evidence import ModalityEvidence
from .contradiction_edge import ContradictionEdge
from .stabilizer_action import StabilizerAction
import time

@dataclass
class FieldSnapshot:
    U: float = 0.5
    D: float = 0.0
    A: float = 0.0
    H: float = 0.5
    lambdas: Dict[str, float] = field(default_factory=lambda: {"U":0.4,"D":0.3,"A":0.3})
    tau: float = 1.0
    contradictions: List[ContradictionEdge] = field(default_factory=list)
    evidences: List[ModalityEvidence] = field(default_factory=list)
    actions: List[StabilizerAction] = field(default_factory=list)
    timestamp: float = 0.0
    system_state: str = "NORMAL"

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
