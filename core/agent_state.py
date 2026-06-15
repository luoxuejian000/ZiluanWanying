from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class AgentState:
    agent_id: str
    role: str = "generic"
    capabilities: list = field(default_factory=list)
    current_task: str = ""
    resources: Dict[str, Any] = field(default_factory=dict)
    harmony_snapshot: Any = None
    tau: float = 1.0
    status: str = "idle"
