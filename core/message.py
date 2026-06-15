from dataclasses import dataclass, field
from typing import Any, Optional
import time

@dataclass
class Message:
    sender_id: str
    receiver_id: Optional[str] = None
    msg_type: str = "info"
    content: Any = None
    timestamp: float = field(default_factory=time.time)
    action_strength: float = 1.0
