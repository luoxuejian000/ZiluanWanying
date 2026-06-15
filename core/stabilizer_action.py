from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class StabilizerAction:
    kind: str
    reason: str
    evidence_refs: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
