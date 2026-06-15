"""
涌现引擎：集群形态自组织的驱动核心。

严格遵循晶脉哲学四重公理：
- 关系本体论：形态是模块之间物理缠关系的全局涌现。没有预设蓝图。
- 矛盾动力论：模块之间的张力（A值）驱动形态重组，而非外部命令。
- 实践介入论：每次形态变化均可追溯，记录重组的原因和参与模块。
- 谐振调谐论：集群趋向于降低整体结构应力（H值最大化），自动收敛到稳态。

严防工具理性悖论：
- 本引擎不包含任何预设形态模板（没有"桥"、"立方体"、"圆形阵列"的蓝图）。
- 所有形态都是模块在局部信息下各自行动、全局涌现的结果。
- 引擎只提供局部规则，不提供全局规划。
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
from physical.physical_module import PhysicalModule
from physical.morphology import MorphologyGraph
import networkx as nx

class EmergenceEngine:
    def __init__(self, morphology: MorphologyGraph):
        self.morphology = morphology
        self.morphology_history: List[Dict] = []

    def step(self, modules: Dict[str, PhysicalModule]) -> Dict:
        events = []
        cluster_stress_before = self.morphology.get_cluster_stress()

        for module_id, module in modules.items():
            if module.current_task == "idle":
                continue
            nearby = self._get_nearby_modules(module, modules)
            for neighbor_id, distance in nearby:
                if distance < 0.4 and neighbor_id not in module.neighbors:
                    alignment = self._check_face_alignment(module, modules[neighbor_id], distance)
                    if alignment:
                        face_a, face_b = alignment
                        module.lock_with(face_a, modules[neighbor_id], face_b, 0.8)
                        self.morphology.add_connection(module_id, neighbor_id, 0.8)
                        events.append({
                            "type": "lock",
                            "module_a": module_id,
                            "module_b": neighbor_id,
                            "reason": "proximity_stress_reduction",
                            "distance": distance
                        })
                if neighbor_id in module.neighbors and module.local_A > 0.6:
                    temp_graph = self.morphology.graph.copy()
                    temp_graph.remove_edge(module_id, neighbor_id)
                    if nx.is_connected(temp_graph) if len(temp_graph.nodes) > 2 else True:
                        for face, conn in module.connectors.items():
                            if conn.is_locked and conn.connected_to == neighbor_id:
                                conn.unlock()
                                break
                        self.morphology.remove_connection(module_id, neighbor_id)
                        events.append({
                            "type": "unlock",
                            "module_a": module_id,
                            "module_b": neighbor_id,
                            "reason": "high_local_A",
                            "A_value": module.local_A
                        })

        cluster_stress_after = self.morphology.get_cluster_stress()
        is_stable = cluster_stress_after < 0.3

        audit = {
            "cluster_stress_before": cluster_stress_before,
            "cluster_stress_after": cluster_stress_after,
            "is_stable": is_stable,
            "events": events,
            "morphology_nodes": len(self.morphology.graph.nodes),
            "morphology_edges": len(self.morphology.graph.edges),
        }
        self.morphology_history.append(audit)
        return audit

    def _get_nearby_modules(self, module: PhysicalModule, all_modules: Dict[str, PhysicalModule]) -> List[Tuple[str, float]]:
        nearby = []
        for other_id, other in all_modules.items():
            if other_id == module.module_id:
                continue
            dist = module.distance_to(other)
            if dist < 2.0:
                nearby.append((other_id, dist))
        nearby.sort(key=lambda x: x[1])
        return nearby

    def _check_face_alignment(self, module_a: PhysicalModule, module_b: PhysicalModule, distance: float) -> Optional[Tuple[str, str]]:
        opposite_faces = {
            "front": "back", "back": "front",
            "left": "right", "right": "left",
            "top": "bottom", "bottom": "top",
        }
        for face_a, conn_a in module_a.connectors.items():
            if conn_a.is_locked:
                continue
            target_face = opposite_faces[face_a]
            conn_b = module_b.connectors.get(target_face)
            if conn_b and not conn_b.is_locked:
                pos_a = module_a.get_face_position(face_a)
                pos_b = module_b.get_face_position(target_face)
                if np.linalg.norm(pos_a - pos_b) < 0.5:
                    return (face_a, target_face)
        return None
