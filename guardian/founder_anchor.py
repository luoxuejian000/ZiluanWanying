"""
家族锚点与家族节点定义。
基于晶脉哲学关系本体论的身份定义。
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
import hashlib

@dataclass
class FamilyNode:
    """
    家族节点：代表家族中的一个成员。
    
    身份不是由生物特征或密码定义的，
    而是由其在家族关系场域中的位置定义的。
    """
    node_id: str
    name: str
    role: str = "descendant"  # "founder", "descendant", "spouse", "relative"
    birth_date: str = ""
    birth_place: str = ""
    relationships: Dict[str, str] = field(default_factory=dict)  # node_id -> relation_type
    is_active: bool = True
    last_contact: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def get_family_position(self) -> str:
        """获取该成员在家族关系场域中的位置"""
        if self.role == "founder":
            return "founder"
        elif "spouse" in self.role:
            return "spouse"
        else:
            return "descendant"
    
    def get_connection_hash(self) -> str:
        """生成该成员的关系连接哈希（用于身份验证）"""
        rel_str = "|".join(f"{k}:{v}" for k, v in sorted(self.relationships.items()))
        return hashlib.sha256(f"{self.node_id}:{rel_str}".encode()).hexdigest()[:16]


@dataclass
class FounderAnchor:
    """
    创始人锚点：家族的起点。
    
    创始人是一切的起源，通过其关系向外辐射，
    形成完整的家族关系场域。
    """
    founder: FamilyNode = None
    family_nodes: Dict[str, FamilyNode] = field(default_factory=dict)
    family_tree: Dict[str, List[str]] = field(default_factory=dict)
    total_members: int = 0
    relationships: List[tuple] = field(default_factory=list)
    
    def __post_init__(self):
        if self.founder:
            self.founder.role = "founder"
            self.founder.last_contact = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.family_nodes[self.founder.node_id] = self.founder
            self.family_tree[self.founder.node_id] = []
    
    def add_member(self, member: FamilyNode, parent_id: Optional[str] = None) -> bool:
        """
        添加新的家族成员。
        如果提供了 parent_id，则建立代际关联。
        """
        if member.node_id in self.family_nodes:
            return False
        
        self.family_nodes[member.node_id] = member
        self.total_members += 1
        
        if parent_id and parent_id in self.family_tree:
            self.family_tree[parent_id].append(member.node_id)
        
        return True
    
    def add_relationship(self, from_node: str, to_node: str, relation_type: str):
        """
        添加家族关系边。
        """
        self.relationships.append((from_node, to_node, relation_type))
        if from_node in self.family_nodes and to_node in self.family_nodes:
            if to_node not in self.family_nodes[from_node].relationships:
                self.family_nodes[from_node].relationships[to_node] = relation_type
            if from_node not in self.family_nodes[to_node].relationships:
                reverse_type = "child" if relation_type == "parent_child" else \
                              "spouse" if relation_type == "spouse" else relation_type
                self.family_nodes[to_node].relationships[from_node] = reverse_type
    
    def get_descendants(self, node_id: str) -> List[str]:
        """获取某节点的所有后代"""
        descendants = []
        if node_id not in self.family_tree:
            return descendants
        
        children = self.family_tree[node_id]
        for child_id in children:
            descendants.append(child_id)
            descendants.extend(self.get_descendants(child_id))
        
        return descendants
    
    def get_ancestors(self, node_id: str) -> List[str]:
        """获取某节点的所有祖先"""
        ancestors = []
        if node_id not in self.family_nodes:
            return ancestors
        
        member = self.family_nodes[node_id]
        for parent_id, relation in member.relationships.items():
            if "parent" in relation or "founder" in relation:
                ancestors.append(parent_id)
                ancestors.extend(self.get_ancestors(parent_id))
        
        return ancestors
    
    def calculate_field_harmony(self) -> float:
        """
        计算家族关系场域的健康度（H值）。
        
        H值由以下因素决定：
        - U（统一性）：家族成员之间的连接紧密度
        - D（发展性）：家族信息的更新频率
        - A（对抗性）：关系冲突和缺失连接的比例
        """
        if not self.family_nodes:
            return 0.0
        
        # 计算统一性
        total_relations = sum(len(m.relationships) for m in self.family_nodes.values())
        max_relations = self.total_members * (self.total_members - 1)
        U = total_relations / max_relations if max_relations > 0 else 0.0
        
        # 计算发展性（活跃成员比例）
        active_count = sum(1 for m in self.family_nodes.values() if m.is_active)
        D = active_count / self.total_members if self.total_members > 0 else 0.0
        
        # 计算对抗性（长期未联系的成员比例）
        inactive_count = sum(1 for m in self.family_nodes.values() if not m.is_active)
        A = inactive_count / self.total_members if self.total_members > 0 else 0.0
        
        # 计算H值
        H = 0.4 * U + 0.3 * D - 0.3 * A
        
        return max(0.0, min(1.0, H))
    
    def get_family_statistics(self) -> Dict:
        """获取家族统计信息"""
        return {
            "total_members": self.total_members,
            "active_members": sum(1 for m in self.family_nodes.values() if m.is_active),
            "field_harmony": self.calculate_field_harmony(),
            "generations": len(set(m.role for m in self.family_nodes.values())),
        }
    
    def anchor_founder_family(self):
        """
        锚定创始家族关系场域（关系本体论：身份由在场域中的位置定义）。
        
        创始人：李广好，安徽省合肥市长丰县水湖镇人，庄墓镇人民政府工作。
        核心家庭成员：母亲陶仁义，妻子王艳，子女李玉妍、李甜爱。
        """
        founder = FamilyNode(
            node_id="FOUNDER-0001",
            name="李广好",
            role="founder",
            birth_date="1980-01-01",
            birth_place="中国安徽省合肥市长丰县水湖镇",
            is_active=True
        )
        self.founder = founder
        self.family_nodes[founder.node_id] = founder
        self.family_tree[founder.node_id] = []
        self.total_members = 1

        mother = FamilyNode(
            node_id="FAMILY-0002",
            name="陶仁义",
            role="mother_of_founder",
            birth_date="1955-01-01",
            birth_place="中国安徽省合肥市长丰县",
            is_active=True
        )
        self.family_nodes[mother.node_id] = mother
        self.total_members += 1
        self.add_relationship(founder.node_id, mother.node_id, "parent_child")

        spouse = FamilyNode(
            node_id="FAMILY-0003",
            name="王艳",
            role="spouse_of_founder",
            birth_date="1982-01-01",
            birth_place="中国安徽省合肥市长丰县",
            is_active=True
        )
        self.family_nodes[spouse.node_id] = spouse
        self.total_members += 1
        self.add_relationship(founder.node_id, spouse.node_id, "spouse")

        child1 = FamilyNode(
            node_id="FAMILY-0004",
            name="李玉妍",
            role="descendant",
            birth_date="2010-01-01",
            birth_place="中国安徽省合肥市长丰县",
            is_active=True
        )
        self.family_nodes[child1.node_id] = child1
        self.total_members += 1
        self.add_relationship(founder.node_id, child1.node_id, "parent_child")
        self.add_relationship(spouse.node_id, child1.node_id, "parent_child")

        child2 = FamilyNode(
            node_id="FAMILY-0005",
            name="李甜爱",
            role="descendant",
            birth_date="2015-01-01",
            birth_place="中国安徽省合肥市长丰县",
            is_active=True
        )
        self.family_nodes[child2.node_id] = child2
        self.total_members += 1
        self.add_relationship(founder.node_id, child2.node_id, "parent_child")
        self.add_relationship(spouse.node_id, child2.node_id, "parent_child")

        return len(self.family_nodes)
    
    def compute_field_harmony(self) -> float:
        """计算家族关系场域的健康度（H值）"""
        return self.calculate_field_harmony()
