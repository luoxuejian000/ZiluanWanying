import hashlib
import hmac
from typing import Dict, Optional


class SecureIdentityResolver:
    """安全身份解析器：将加密哈希映射为真实身份，仅在运行时内存中存在"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.identity_cache: Dict[str, str] = {}  # 运行时内存缓存
        
    def resolve(self, node_id: str, hash_value: str) -> Optional[str]:
        """解析加密哈希为真实身份"""
        if node_id in self.identity_cache:
            return self.identity_cache[node_id]
        
        identity = self._fetch_identity(node_id)
        if identity:
            expected_hash = self._compute_hash(identity)
            if hmac.compare_digest(expected_hash, hash_value):
                self.identity_cache[node_id] = identity
                return identity
        return None
    
    def _compute_hash(self, plain_text: str) -> str:
        return hmac.new(
            self.secret_key.encode(),
            plain_text.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _fetch_identity(self, node_id: str) -> Optional[str]:
        identity_map = {
            "FOUNDER-0001": "李广好",
            "FAMILY-0002": "陶仁义",
            "FAMILY-0003": "王艳",
            "FAMILY-0004": "李玉妍",
            "FAMILY-0005": "李甜爱",
        }
        return identity_map.get(node_id)
    
    def clear_cache(self):
        """清空内存缓存，消除运行时痕迹"""
        self.identity_cache.clear()


class EncryptedFamilyNode:
    """加密的家族节点：存储哈希值而非明文身份"""
    
    def __init__(self, node_id: str, name_hash: str, role: str, 
                 birth_date_hash: str = "", birth_place_hash: str = "", is_active: bool = True):
        self.node_id = node_id
        self.name_hash = name_hash
        self.role = role
        self.birth_date_hash = birth_date_hash
        self.birth_place_hash = birth_place_hash
        self.is_active = is_active
        self.relationships: Dict[str, str] = {}
    
    def get_display_name(self, resolver: SecureIdentityResolver) -> str:
        """通过安全解析器获取显示名称"""
        resolved = resolver.resolve(self.node_id, self.name_hash)
        return resolved if resolved else self.name_hash[:8]


class SecureFounderAnchor:
    """安全的创始人锚点：所有身份信息均以哈希形式存储"""
    
    def __init__(self, secret_key: str):
        self.resolver = SecureIdentityResolver(secret_key)
        self.family_nodes: Dict[str, EncryptedFamilyNode] = {}
        self.relationships: List[tuple] = []
        self.total_members = 0
    
    def _hash_name(self, name: str) -> str:
        return hmac.new(
            self.resolver.secret_key.encode(),
            name.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def anchor_founder_family(self):
        """锚定创始家族关系场域（所有身份信息均加密存储）"""
        founder = EncryptedFamilyNode(
            node_id="FOUNDER-0001",
            name_hash=self._hash_name("李广好"),
            role="founder",
            birth_date_hash=self._hash_name("1980-01-01"),
            birth_place_hash=self._hash_name("中国安徽省合肥市长丰县水湖镇"),
            is_active=True
        )
        self.family_nodes[founder.node_id] = founder
        self.total_members = 1

        mother = EncryptedFamilyNode(
            node_id="FAMILY-0002",
            name_hash=self._hash_name("陶仁义"),
            role="mother_of_founder",
            birth_date_hash=self._hash_name("1955-01-01"),
            birth_place_hash=self._hash_name("中国安徽省合肥市长丰县"),
            is_active=True
        )
        self.family_nodes[mother.node_id] = mother
        self.total_members += 1
        self._add_relationship(founder.node_id, mother.node_id, "parent_child")

        spouse = EncryptedFamilyNode(
            node_id="FAMILY-0003",
            name_hash=self._hash_name("王艳"),
            role="spouse_of_founder",
            birth_date_hash=self._hash_name("1982-01-01"),
            birth_place_hash=self._hash_name("中国安徽省合肥市长丰县"),
            is_active=True
        )
        self.family_nodes[spouse.node_id] = spouse
        self.total_members += 1
        self._add_relationship(founder.node_id, spouse.node_id, "spouse")

        child1 = EncryptedFamilyNode(
            node_id="FAMILY-0004",
            name_hash=self._hash_name("李玉妍"),
            role="descendant",
            birth_date_hash=self._hash_name("2010-01-01"),
            birth_place_hash=self._hash_name("中国安徽省合肥市长丰县"),
            is_active=True
        )
        self.family_nodes[child1.node_id] = child1
        self.total_members += 1
        self._add_relationship(founder.node_id, child1.node_id, "parent_child")
        self._add_relationship(spouse.node_id, child1.node_id, "parent_child")

        child2 = EncryptedFamilyNode(
            node_id="FAMILY-0005",
            name_hash=self._hash_name("李甜爱"),
            role="descendant",
            birth_date_hash=self._hash_name("2015-01-01"),
            birth_place_hash=self._hash_name("中国安徽省合肥市长丰县"),
            is_active=True
        )
        self.family_nodes[child2.node_id] = child2
        self.total_members += 1
        self._add_relationship(founder.node_id, child2.node_id, "parent_child")
        self._add_relationship(spouse.node_id, child2.node_id, "parent_child")

        return self.total_members
    
    def _add_relationship(self, from_node: str, to_node: str, relation_type: str):
        self.relationships.append((from_node, to_node, relation_type))
        if from_node in self.family_nodes:
            self.family_nodes[from_node].relationships[to_node] = relation_type
    
    def get_family_summary(self, show_real_names: bool = False) -> str:
        """获取家族摘要（可选择是否显示真实姓名）"""
        report = "=" * 60 + "\n"
        report += "  紫鸾·万翎 安全守护报告\n"
        report += "=" * 60 + "\n"
        report += f"  家族成员总数: {self.total_members}\n"
        report += f"  关系边总数: {len(self.relationships)}\n"
        report += "\n  当前守护成员:\n"
        
        for node_id, member in self.family_nodes.items():
            if show_real_names:
                display_name = member.get_display_name(self.resolver)
            else:
                display_name = member.name_hash[:8]
            report += f"    [{member.role}] {display_name} ({node_id})\n"
        
        report += "=" * 60 + "\n"
        return report
    
    def clear_all(self):
        """彻底清除所有内存中的身份信息"""
        self.resolver.clear_cache()


def demo_secure_guardian():
    """演示安全守护机制"""
    SECRET_KEY = "your-secret-key-here-keep-it-safe"
    
    print("=" * 60)
    print("  紫鸾·万翎 安全守护演示")
    print("=" * 60)
    
    anchor = SecureFounderAnchor(SECRET_KEY)
    anchor.anchor_founder_family()
    
    print("\n[状态1] 外部视角（无法解密）:")
    print(anchor.get_family_summary(show_real_names=False))
    
    print("\n[状态2] 内部视角（已解密）:")
    print(anchor.get_family_summary(show_real_names=True))
    
    print("\n[状态3] 清除缓存后（再次变为哈希）:")
    anchor.clear_all()
    print(anchor.get_family_summary(show_real_names=False))
    
    print("\n[完成] 安全守护演示结束")


if __name__ == "__main__":
    demo_secure_guardian()
