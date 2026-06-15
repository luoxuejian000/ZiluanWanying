"""
连接器：模块之间的物理接口。
每个模块有六个面（前、后、左、右、上、下），每个面有一个Connector。
两个模块通过互锁各自的Connector形成刚性连接（缠的物理实现）。
"""
from dataclasses import dataclass, field
from typing import Optional
import uuid

@dataclass
class Connector:
    face: str  # "front" | "back" | "left" | "right" | "top" | "bottom"
    is_locked: bool = False
    connected_to: Optional[str] = None
    connected_face: Optional[str] = None
    lock_strength: float = 0.0
    max_strength: float = 1.0
    connector_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def lock(self, target_module_id: str, target_face: str, strength: float = 1.0):
        self.is_locked = True
        self.connected_to = target_module_id
        self.connected_face = target_face
        self.lock_strength = strength

    def unlock(self):
        self.is_locked = False
        self.connected_to = None
        self.connected_face = None
        self.lock_strength = 0.0
