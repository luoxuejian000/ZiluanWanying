import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, deque
from dataclasses import dataclass, field
import hashlib


# ============================================================
# 核心数据结构
# ============================================================

@dataclass
class MemoryVector:
    """
    记忆向量：一段关键经验的场域投影。
    不是存储原始文本，而是存储其与场域核心概念的关系向量。
    """
    vector: np.ndarray
    context_hash: str
    core_concepts: List[str]
    resonance_signature: Dict[str, float]
    outcome: str
    timestamp: float
    activation_count: int = 0
    strength: float = 1.0
    ttl: float = 3600.0


@dataclass
class MemoryAuditEntry:
    """记忆操作审计记录（实践介入论）"""
    action: str
    memory_hash: str
    reason: str
    field_state_before: Dict[str, float]
    field_state_after: Optional[Dict[str, float]]
    timestamp: float


# ============================================================
# 记忆存储库 (MemoryStore) —— 关系本体论的工程实现
# ============================================================

class MemoryStore:
    """
    记忆存储库：管理所有记忆向量及其关系网络。
    """
    def __init__(self, max_memories: int = 10000, vector_dim: int = 384):
        self.memories: Dict[str, MemoryVector] = {}
        self.concept_index: Dict[str, List[str]] = {}
        self.max_memories = max_memories
        self.vector_dim = vector_dim
        self.audit_log: List[MemoryAuditEntry] = []

    def store(self, content: str, core_concepts: List[str],
              field_state: Dict[str, float], outcome: str = "pending") -> Optional[str]:
        context_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        if context_hash in self.memories:
            existing = self.memories[context_hash]
            existing.strength = min(1.0, existing.strength + 0.1)
            existing.activation_count += 1
            existing.ttl = max(existing.ttl, 3600.0)
            self._audit("reinforce", context_hash, f"强化已有记忆: {core_concepts[:3]}", field_state, None)
            return context_hash
        vector = self._encode(content)
        resonance_signature = {
            "U": field_state.get("U", 0.5),
            "D": field_state.get("D", 0.0),
            "A": field_state.get("A", 0.0),
            "H": field_state.get("H", 0.5)
        }
        memory = MemoryVector(
            vector=vector, context_hash=context_hash, core_concepts=core_concepts,
            resonance_signature=resonance_signature, outcome=outcome, timestamp=time.time()
        )
        self.memories[context_hash] = memory
        for concept in core_concepts:
            if concept not in self.concept_index:
                self.concept_index[concept] = []
            self.concept_index[concept].append(context_hash)
        if len(self.memories) > self.max_memories:
            self._evict_weakest()
        self._audit("store", context_hash, f"存储新记忆: {core_concepts[:3]}", field_state, None)
        return context_hash

    def retrieve(self, query_concepts: List[str], current_field: Dict[str, float],
                 top_k: int = 5) -> List[Tuple[MemoryVector, float]]:
        candidates = set()
        for concept in query_concepts:
            if concept in self.concept_index:
                candidates.update(self.concept_index[concept])
        if not candidates:
            return []
        scored = []
        current_vector = self._encode(" ".join(query_concepts))
        current_U = current_field.get("U", 0.5)
        current_A = current_field.get("A", 0.0)
        for mem_hash in candidates:
            memory = self.memories[mem_hash]
            sim = np.dot(current_vector, memory.vector) / (np.linalg.norm(current_vector) * np.linalg.norm(memory.vector) + 1e-8)
            resonance_match = 1.0 - abs(current_U - memory.resonance_signature["U"])
            contradiction_drive = current_A * 0.5
            strength_bonus = memory.strength
            score = (0.4 * sim + 0.3 * resonance_match + 0.2 * contradiction_drive + 0.1 * strength_bonus)
            scored.append((memory, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:top_k]
        if top:
            for memory, _ in top:
                memory.activation_count += 1
            self._audit("retrieve", top[0][0].context_hash, f"唤醒{len(top)}条记忆: {query_concepts[:3]}", current_field, None)
        return top

    def _encode(self, text: str) -> np.ndarray:
        np.random.seed(hash(text) % (2**32))
        vec = np.random.randn(self.vector_dim)
        vec = vec / (np.linalg.norm(vec) + 1e-8)
        return vec

    def _evict_weakest(self):
        if not self.memories:
            return
        weakest = min(self.memories.items(), key=lambda x: x[1].strength * x[1].ttl)
        self.memories.pop(weakest[0])
        for concept, mem_list in self.concept_index.items():
            if weakest[0] in mem_list:
                mem_list.remove(weakest[0])

    def _audit(self, action: str, mem_hash: str, reason: str,
               field_before: Dict[str, float], field_after: Optional[Dict[str, float]]):
        entry = MemoryAuditEntry(action=action, memory_hash=mem_hash, reason=reason,
                                 field_state_before=field_before, field_state_after=field_after, timestamp=time.time())
        self.audit_log.append(entry)
        if len(self.audit_log) > 10000:
            self.audit_log.pop(0)

    def evolve(self, memory_hash: str, new_outcome: str, new_field_state: Dict[str, float]):
        if memory_hash not in self.memories:
            return
        memory = self.memories[memory_hash]
        old_outcome = memory.outcome
        memory.outcome = new_outcome
        memory.strength = min(1.0, memory.strength + 0.15)
        self._audit("evolve", memory_hash, f"记忆进化: {old_outcome} -> {new_outcome}", {}, new_field_state)

    def get_audit_report(self) -> str:
        report = "=" * 60 + "\n"
        report += "  仿生记忆层审计报告\n"
        report += f"  总记忆数: {len(self.memories)}\n"
        report += f"  概念索引数: {len(self.concept_index)}\n"
        report += f"  审计记录数: {len(self.audit_log)}\n"
        report += "=" * 60 + "\n"
        for entry in self.audit_log[-10:]:
            report += f"  [{entry.action}] {entry.memory_hash}: {entry.reason}\n"
        return report


# ============================================================
# 记忆唤醒器 (MemoryAwakener) —— 矛盾动力论的工程实现
# ============================================================

class MemoryAwakener:
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        self.recent_concepts = deque(maxlen=50)
        self.last_wake_time = 0.0
        self.wake_cooldown = 2.0

    def observe_concepts(self, concepts: List[str]):
        self.recent_concepts.extend(concepts)

    def should_wake(self, field_state: Dict[str, float]) -> bool:
        A = field_state.get("A", 0.0)
        dA = field_state.get("dA", 0.0)
        if A > 0.3 and dA > 0.01:
            if time.time() - self.last_wake_time > self.wake_cooldown:
                return True
        return False

    def wake(self, field_state: Dict[str, float]) -> List[Tuple[MemoryVector, float]]:
        if not self.should_wake(field_state):
            return []
        self.last_wake_time = time.time()
        query_concepts = list(set(self.recent_concepts))[-10:]
        if not query_concepts:
            return []
        return self.memory_store.retrieve(query_concepts, field_state, top_k=3)


# ============================================================
# 记忆融合器 (MemoryIntegrator) —— 谐振调谐论的工程实现
# ============================================================

class MemoryIntegrator:
    def __init__(self):
        self.influence_history = deque(maxlen=20)

    def integrate(self, memories: List[Tuple[MemoryVector, float]],
                  field_state: Dict[str, float]) -> Dict[str, float]:
        if not memories:
            return field_state
        total_influence = 0.0
        for memory, score in memories:
            if memory.outcome == "success":
                field_state["H"] = min(1.0, field_state.get("H", 0.5) + score * 0.08)
                field_state["A"] = max(0.0, field_state.get("A", 0.0) - score * 0.05)
                total_influence += score
        if total_influence > 0:
            self.influence_history.append(total_influence)
        return field_state


# ============================================================
# 仿生记忆层 (BiomimeticMemoryLayer)
# ============================================================

class BiomimeticMemoryLayer:
    """
    仿生记忆层：将所有组件整合为一个完整的记忆系统。
    严格遵循晶脉哲学四重公理。
    """
    def __init__(self):
        self.store = MemoryStore()
        self.awakener = MemoryAwakener(self.store)
        self.integrator = MemoryIntegrator()

    def observe(self, concepts: List[str], field_state: Dict[str, float]):
        self.awakener.observe_concepts(concepts)

    def store_memory(self, content: str, core_concepts: List[str],
                     field_state: Dict[str, float], outcome: str = "pending"):
        return self.store.store(content, core_concepts, field_state, outcome)

    def process(self, field_state: Dict[str, float]) -> Dict[str, float]:
        if self.awakener.should_wake(field_state):
            memories = self.awakener.wake(field_state)
            if memories:
                field_state = self.integrator.integrate(memories, field_state)
                field_state["memory_active"] = True
            else:
                field_state["memory_active"] = False
        else:
            field_state["memory_active"] = False
        return field_state

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "memory_count": len(self.store.memories),
            "concept_count": len(self.store.concept_index),
            "audit_entries": len(self.store.audit_log),
            "influence_history": list(self.integrator.influence_history)
        }


# ============================================================
# 集群记忆管理器 (ClusterMemoryManager)
# ============================================================

class ClusterMemoryManager:
    """
    集群记忆管理器：协调多个节点的记忆共享与同步。
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.local_memory = BiomimeticMemoryLayer()
        self.shared_concepts: Dict[str, int] = defaultdict(int)
        self.sync_interval = 30.0
        self.last_sync_time = 0.0

    def sync_with_cluster(self, other_nodes: List['ClusterMemoryManager']):
        if time.time() - self.last_sync_time < self.sync_interval:
            return
        self.last_sync_time = time.time()
        
        for node in other_nodes:
            if node.node_id == self.node_id:
                continue
            for concept, count in node.local_memory.store.concept_index.items():
                self.shared_concepts[concept] += len(count)

    def broadcast_concepts(self, concepts: List[str]):
        for concept in concepts:
            self.shared_concepts[concept] += 1


# ============================================================
# 记忆与智能体集成
# ============================================================

def integrate_memory_to_agent(agent, memory_layer: BiomimeticMemoryLayer):
    """
    将仿生记忆层集成到智能体中。
    智能体需要具备 observe() 和 act() 方法。
    """
    original_act = agent.act
    
    def enhanced_act(field_state: Dict[str, float]) -> Dict[str, float]:
        memory_layer.observe(field_state.get("concepts", []), field_state)
        field_state = memory_layer.process(field_state)
        return original_act(field_state)
    
    agent.act = enhanced_act
    agent.memory_layer = memory_layer
    return agent


# ============================================================
# 扩展：BiomimeticMemoryLayer 完整功能
# ============================================================

class MemoryEvolver:
    """记忆演化器：管理记忆的衰减和进化"""
    def __init__(self, store: 'MemoryStore', decay_rate: float = 0.001):
        self.store = store
        self.decay_rate = decay_rate
    
    def maintain(self):
        """维护记忆：衰减旧记忆强度"""
        now = time.time()
        for memory in self.store.memories.values():
            age = now - memory.timestamp
            memory.strength = max(0.01, memory.strength * (1 - self.decay_rate * age / 3600))
            memory.ttl -= age

    def reinforce(self, memory_hash: str, success: bool):
        if memory_hash not in self.store.memories:
            return
        memory = self.store.memories[memory_hash]
        if success:
            memory.strength = min(1.0, memory.strength + 0.2)
            memory.ttl *= 1.5
        else:
            memory.strength = max(0.0, memory.strength - 0.1)
            memory.ttl *= 0.8
        if memory.strength < 0.1:
            self.store.memories.pop(memory_hash)
            for concept, mem_list in self.store.concept_index.items():
                if memory_hash in mem_list:
                    mem_list.remove(memory_hash)


class EnhancedBiomimeticMemoryLayer(BiomimeticMemoryLayer):
    """增强版仿生记忆层，包含完整的记忆管理功能"""
    def __init__(self, max_memories: int = 5000):
        super().__init__()
        self.store = MemoryStore(max_memories=max_memories)
        self.evolver = MemoryEvolver(self.store)
    
    def remember(self, content: str, core_concepts: List[str],
                 field_state: Dict[str, float], outcome: str = "pending") -> Optional[str]:
        """存储记忆（别名方法）"""
        return self.store.store(content, core_concepts, field_state, outcome)
    
    def recall(self, core_concepts: List[str], field_state: Dict[str, float],
               current_context: str = "", top_k: int = 5) -> List[Tuple[MemoryVector, float]]:
        """唤醒记忆（别名方法）"""
        return self.store.retrieve(core_concepts, field_state, top_k)
    
    def learn_from_outcome(self, memory_hash: str, success: bool):
        """从结果中学习"""
        outcome = "success" if success else "failure"
        self.store.evolve(memory_hash, outcome, {})
    
    def decay_memories(self):
        """定期衰减记忆强度"""
        self.evolver.maintain()
    
    def get_memory_context(self, field_state: Dict[str, float],
                           core_concepts: List[str]) -> Optional[str]:
        """获取最相关的记忆文本，用于注入上下文"""
        memories = self.recall(core_concepts, field_state, "", top_k=1)
        if not memories:
            return None
        top_memory, score = memories[0]
        concepts = ", ".join(top_memory.core_concepts[:5])
        return f"[记忆唤醒] 相关经验: {concepts} (相关度: {score:.2f})"
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        total_memories = len(self.store.memories)
        total_concepts = len(self.store.concept_index)
        avg_strength = np.mean([m.strength for m in self.store.memories.values()]) if self.store.memories else 0.0
        total_audit = len(self.store.audit_log)
        return {
            "total_memories": total_memories,
            "total_concepts": total_concepts,
            "average_strength": avg_strength,
            "total_audit_entries": total_audit,
            "max_capacity": self.store.max_memories
        }
    
    def get_audit_report(self) -> str:
        """获取审计报告"""
        if not self.store.audit_log:
            return "  审计日志为空\n"
        recent = self.store.audit_log[-10:]
        report = "  最近操作记录:\n"
        for entry in reversed(recent):
            ts = time.strftime("%H:%M:%S", time.localtime(entry.timestamp))
            report += f"    [{ts}] {entry.action}: {entry.reason}\n"
        return report


# ============================================================
# 集成接口：将仿生记忆层集成到紫鸾·万翎的 ZiluanAgent 中
# ============================================================

def integrate_memory_to_agent(agent, memory_layer: BiomimeticMemoryLayer):
    """
    将仿生记忆层集成到紫鸾·万翎的智能体节点中。
    
    使用方法：
        memory_layer = BiomimeticMemoryLayer(max_memories=5000)
        for agent in cluster.agents.values():
            integrate_memory_to_agent(agent, memory_layer)
    """
    agent.memory_layer = memory_layer
    
    original_think_and_act = agent.think_and_act
    
    def enhanced_think_and_act():
        """增强的思考与行动循环：在检测到失谐时自动唤醒记忆"""
        snap = original_think_and_act()
        
        if snap is None:
            return snap
        
        # 检查是否需要唤醒记忆（矛盾动力论：A值升高驱动记忆唤醒）
        if snap.A > 0.4 and snap.U < 0.45:
            task_concepts = agent.state.current_task.split("_") if agent.state.current_task else ["general"]
            
            memories = memory_layer.recall(
                core_concepts=task_concepts,
                field_state={"U": snap.U, "D": snap.D, "A": snap.A, "H": snap.H},
                current_context=agent.state.current_task or "idle",
                top_k=3
            )
            
            for memory, score in memories:
                if score > 0.5:
                    agent.state.resources["last_memory_context"] = {
                        "concepts": memory.core_concepts[:5],
                        "outcome": memory.outcome,
                        "score": score,
                        "timestamp": time.time()
                    }
                    if snap.H > 0.5:
                        memory_layer.learn_from_outcome(memory.context_hash, success=True)
        
        return snap
    
    agent.think_and_act = enhanced_think_and_act
    return agent


# ============================================================
# 集群级记忆管理器
# ============================================================

class ClusterMemoryManager:
    """
    集群级记忆管理器：管理整个紫鸾·万翎集群的集体记忆。
    
    核心功能：
    - 跨模块记忆共享：当一个模块学到成功经验，其他模块也能受益
    - 集群级记忆审计：完整记录整个集群的记忆演化历史
    - 记忆热区检测：识别集群中频繁唤醒的记忆，可能指示系统性问题
    """
    
    def __init__(self, memory_layer: BiomimeticMemoryLayer):
        self.memory_layer = memory_layer
        self.cluster_audit: List[Dict] = []
        self.hotspot_cache: Dict[str, int] = {}
    
    def share_memory(self, source_agent_id: str, content: str,
                     core_concepts: List[str], field_state: Dict[str, float],
                     outcome: str = "success"):
        """跨模块共享记忆：一个模块的成功经验，写入集体记忆"""
        mem_hash = self.memory_layer.remember(content, core_concepts, field_state, outcome)
        if mem_hash:
            self.cluster_audit.append({
                "action": "share",
                "source_agent": source_agent_id,
                "memory_hash": mem_hash,
                "concepts": core_concepts[:5],
                "timestamp": time.time()
            })
            for concept in core_concepts[:3]:
                self.hotspot_cache[concept] = self.hotspot_cache.get(concept, 0) + 1
        return mem_hash
    
    def get_cluster_hotspots(self, top_k: int = 10) -> List[Tuple[str, int]]:
        """获取集群记忆热区：最频繁被唤醒的概念"""
        sorted_hotspots = sorted(self.hotspot_cache.items(),
                                key=lambda x: x[1], reverse=True)
        return sorted_hotspots[:top_k]
    
    def get_cluster_audit_report(self) -> str:
        """获取集群级记忆审计报告"""
        stats = self.memory_layer.get_memory_statistics()
        hotspots = self.get_cluster_hotspots(5)
        
        report = "=" * 60 + "\n"
        report += "  紫鸾·万翎 集群记忆审计报告\n"
        report += "=" * 60 + "\n"
        report += f"  总记忆数: {stats['total_memories']}\n"
        report += f"  总概念数: {stats['total_concepts']}\n"
        report += f"  平均记忆强度: {stats['average_strength']:.2f}\n"
        report += f"  集群共享操作: {len(self.cluster_audit)}\n"
        report += f"  记忆热区 (Top 5):\n"
        for concept, count in hotspots:
            report += f"    - {concept}: {count}次\n"
        report += "=" * 60 + "\n"
        report += self.memory_layer.get_audit_report()
        return report


# ============================================================
# 完整的集成演示
# ============================================================

def demo_memory_integration():
    """
    演示仿生记忆层如何集成到紫鸾·万翎物理集群中。
    运行此函数可看到完整的记忆存储、唤醒、共享和审计流程。
    """
    print("=" * 60)
    print("  紫鸾·万翎 仿生记忆层集成演示")
    print("=" * 60)
    
    # 1. 初始化记忆层
    memory = EnhancedBiomimeticMemoryLayer(max_memories=5000)
    cluster_memory = ClusterMemoryManager(memory)
    
    # 2. 存储初始记忆
    print("\n1. 存储初始记忆...")
    
    memory.remember(
        content="网络攻击场景下，降低探索率可以提高系统稳定性",
        core_concepts=["网络攻击", "稳定性", "探索率"],
        field_state={"U": 0.3, "D": 0.7, "A": 0.6, "H": 0.4},
        outcome="success"
    )
    
    memory.remember(
        content="系统失谐时，等待观察比立即行动更有效",
        core_concepts=["失谐", "等待", "观察"],
        field_state={"U": 0.2, "D": 0.5, "A": 0.8, "H": 0.2},
        outcome="success"
    )
    
    # 3. 显示记忆统计
    print("\n2. 当前记忆统计:")
    stats = memory.get_memory_statistics()
    for k, v in stats.items():
        print(f"   {k}: {v}")
    
    # 4. 模拟失谐状态下唤醒记忆
    print("\n3. 模拟失谐状态下唤醒记忆...")
    field_state = {"U": 0.35, "D": 0.5, "A": 0.55, "H": 0.38}
    context = memory.get_memory_context(field_state, ["网络攻击", "失谐"])
    print(f"   记忆上下文: {context}")
    
    # 5. 跨模块共享记忆
    print("\n4. 跨模块共享记忆...")
    cluster_memory.share_memory(
        source_agent_id="agent_001",
        content="节点1发现的攻击模式",
        core_concepts=["攻击模式", "检测", "节点1"],
        field_state={"U": 0.4, "D": 0.6, "A": 0.5, "H": 0.45},
        outcome="success"
    )
    
    # 6. 显示集群审计报告
    print("\n5. 集群审计报告:")
    print(cluster_memory.get_cluster_audit_report())
    
    print("\n[OK] 演示完成！")


if __name__ == "__main__":
    demo_memory_integration()
