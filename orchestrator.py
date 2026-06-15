import time
import numpy as np
from agents.ziluan_agent import ZiluanAgent
from network.message_bus import MessageBus
from network.relation_graph import RelationGraph
from core.message import Message

class ClusterOrchestrator:
    def __init__(self, num_agents: int, roles: list = None):
        self.bus = MessageBus()
        self.relation_graph = RelationGraph()
        self.agents = {}
        for i in range(num_agents):
            agent_id = f"Ziluan-{i:04d}"
            role = roles[i] if roles and i < len(roles) else "generic"
            agent = ZiluanAgent(agent_id, role, self.bus, self.relation_graph)
            self.agents[agent_id] = agent

    def step_all(self) -> dict:
        snaps = {}
        for agent_id, agent in self.agents.items():
            snap = agent.think_and_act()
            snaps[agent_id] = snap
        H_vals = [s.H for s in snaps.values()]
        U_vals = [s.U for s in snaps.values()]
        A_vals = [s.A for s in snaps.values()]
        cluster_H = np.mean(H_vals) if H_vals else 0.5
        cluster_U = np.mean(U_vals) if U_vals else 0.5
        cluster_A = np.mean(A_vals) if A_vals else 0.0
        cross_contradictions = 0
        for aid_a, agent_a in self.agents.items():
            for aid_b, agent_b in self.agents.items():
                if aid_a >= aid_b: continue
                if agent_a.state.status == "alert" and agent_b.state.status == "alert":
                    if self.relation_graph.graph.has_edge(aid_a, aid_b) or self.relation_graph.graph.has_edge(aid_b, aid_a):
                        cross_contradictions += 1
        cluster_A += 0.1 * cross_contradictions
        cluster_A = min(1.0, cluster_A)
        return {
            "cluster_H": cluster_H,
            "cluster_U": cluster_U,
            "cluster_A": cluster_A,
            "agent_count": len(self.agents),
            "cross_contradictions": cross_contradictions,
            "timestamp": time.time()
        }

    def run_demo(self, steps: int = 50):
        print("=" * 60)
        print("  紫鸾·万翎 集群演示")
        print("  智能体数量:", len(self.agents))
        print("=" * 60)
        for step in range(steps):
            metrics = self.step_all()
            print(f"Step {step+1:03d} | H={metrics['cluster_H']:.3f} U={metrics['cluster_U']:.3f} A={metrics['cluster_A']:.3f} | 跨智能体矛盾: {metrics['cross_contradictions']}")
            if step % 10 == 0 and step > 0:
                for agent in list(self.agents.values())[:2]:
                    agent.inbox.append(Message(
                        sender_id="environment",
                        receiver_id=agent.agent_id,
                        msg_type="contradict",
                        content={"order": "conflict"},
                        action_strength=0.9
                    ))
            time.sleep(0.1)
