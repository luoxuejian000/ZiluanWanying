from dataclasses import dataclass

@dataclass
class ContradictionEdge:
    modality_a: str
    modality_b: str
    conflict_type: str
    strength: float = 0.0
    description: str = ""
