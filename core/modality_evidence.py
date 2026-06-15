from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ModalityEvidence:
    modality: str
    raw_features: Dict[str, float] = field(default_factory=dict)
    confidence: float = 0.5
    timestamp: float = 0.0
