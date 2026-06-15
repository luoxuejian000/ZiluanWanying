import networkx as nx
from typing import List, Tuple, Dict
from core.message import Message

class RelationGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_taction(self, sender: str, receiver: str, weight: float = 1.0):
        if self.graph.has_edge(sender, receiver):
            self.graph[sender][receiver]['weight'] += weight
        else:
            self.graph.add_edge(sender, receiver, weight=weight, relation='taction')

    def add_entwinement(self, node_a: str, node_b: str, weight: float = 1.0):
        self.graph.add_edge(node_a, node_b, weight=weight, relation='entwinement')
        self.graph.add_edge(node_b, node_a, weight=weight, relation='entwinement')

    def get_neighbors(self, node_id: str) -> List[str]:
        return list(self.graph.neighbors(node_id))

    def get_contradiction_score(self, node_a: str, node_b: str) -> float:
        edges = []
        if self.graph.has_edge(node_a, node_b):
            edges.append(self.graph[node_a][node_b]['weight'])
        if self.graph.has_edge(node_b, node_a):
            edges.append(self.graph[node_b][node_a]['weight'])
        if edges:
            return sum(edges) / len(edges)
        return 0.0
