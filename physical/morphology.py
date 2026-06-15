"""
形态图：记录当前集群的物理拓扑。
这是一张动态的缠网络——节点是模块，边是物理连接（缠）。
形态的演化（重组）由局部张力驱动，而非中央规划。
"""
import networkx as nx
from typing import Dict, List, Tuple, Set
import numpy as np
from .physical_module import PhysicalModule

class MorphologyGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_module(self, module: PhysicalModule):
        self.graph.add_node(module.module_id, module=module)

    def remove_module(self, module_id: str):
        self.graph.remove_node(module_id)

    def add_connection(self, module_a: str, module_b: str, strength: float = 1.0):
        if self.graph.has_edge(module_a, module_b):
            self.graph[module_a][module_b]['strength'] += strength
        else:
            self.graph.add_edge(module_a, module_b, strength=strength, relation='entwinement')

    def remove_connection(self, module_a: str, module_b: str):
        if self.graph.has_edge(module_a, module_b):
            self.graph.remove_edge(module_a, module_b)

    def get_connected_component(self, module_id: str) -> Set[str]:
        if module_id not in self.graph:
            return set()
        visited = set()
        queue = [module_id]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend(self.graph.neighbors(node))
        return visited

    def get_cluster_stress(self) -> float:
        stresses = []
        for node in self.graph.nodes:
            module = self.graph.nodes[node].get('module')
            if module:
                stresses.append(module.local_A)
        return float(np.mean(stresses)) if stresses else 0.0

    def is_rigid(self) -> bool:
        if len(self.graph.nodes) == 0:
            return True
        first_node = list(self.graph.nodes)[0]
        return len(self.get_connected_component(first_node)) == len(self.graph.nodes)
