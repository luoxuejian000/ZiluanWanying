"""
物理模块：紫鸾的最小物理单元。
每个模块是一个边长30cm的立方体，内置推进器、传感器、计算核心、通信节点和可展开机械臂。
它在关系场域中的存在，由它与邻近模块的触（信号传递）和缠（物理连接）所界定。
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
from .connector import Connector

@dataclass
class PhysicalModule:
    module_id: str
    position: np.ndarray
    orientation: np.ndarray
    connectors: Dict[str, Connector] = field(default_factory=dict)
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    thrust_available: float = 100.0
    structural_integrity: float = 1.0
    local_U: float = 0.5
    local_D: float = 0.0
    local_A: float = 0.0
    local_H: float = 0.5
    local_tau: float = 1.0
    current_task: str = "idle"
    neighbors: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.connectors:
            faces = ["front", "back", "left", "right", "top", "bottom"]
            self.connectors = {face: Connector(face=face) for face in faces}

    def get_face_position(self, face: str) -> np.ndarray:
        half = 0.15
        offsets = {
            "front":  np.array([ half, 0, 0]),
            "back":   np.array([-half, 0, 0]),
            "right":  np.array([0,  half, 0]),
            "left":   np.array([0, -half, 0]),
            "top":    np.array([0, 0,  half]),
            "bottom": np.array([0, 0, -half]),
        }
        return self.position + offsets.get(face, np.zeros(3))

    def distance_to(self, other: "PhysicalModule") -> float:
        return float(np.linalg.norm(self.position - other.position))

    def lock_with(self, my_face: str, other: "PhysicalModule", other_face: str, strength: float = 1.0):
        self.connectors[my_face].lock(other.module_id, other_face, strength)
        other.connectors[other_face].lock(self.module_id, my_face, strength)
        if other.module_id not in self.neighbors:
            self.neighbors.append(other.module_id)
        if self.module_id not in other.neighbors:
            other.neighbors.append(self.module_id)

    def unlock_all(self):
        for face, conn in self.connectors.items():
            if conn.is_locked and conn.connected_to:
                conn.unlock()
        self.neighbors.clear()
