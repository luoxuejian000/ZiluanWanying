"""
主动发现与永恒守护引擎 (Proactive & Eternal Guardian Engine)
============================================================
基于晶脉哲学关系本体论的终极守护方案。

核心思想：
- 系统从创始人开始，主动绘制并持续更新一张完整的"家族关系场域图谱"。
- 身份不是由生物特征或密码定义的，而是由其在图谱中的位置定义的。
- 系统通过分析公开数据、家族内部记录和关系逻辑，主动发现潜在的家族成员。
- 一旦发现，系统自动将其纳入守护范围，并持续追踪其状态。
- 守护是永恒的，从创始人开始，代代相传，无间断。
"""
import hashlib
import time
import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime

try:
    from .founder_anchor import FounderAnchor, FamilyNode
except ImportError:
    from founder_anchor import FounderAnchor, FamilyNode


@dataclass
class DiscoveryEvent:
    """主动发现事件记录"""
    event_id: str
    discovered_node_id: str
    discovery_method: str  # "public_record" | "family_report" | "relationship_inference" | "self_claim"
    evidence: str
    timestamp: str
    verified_by: List[str] = field(default_factory=list)
    status: str = "pending"  # "pending", "confirmed", "rejected"


@dataclass
class GuardianAction:
    """守护行为记录"""
    action_id: str
    target_node_id: str
    action_type: str  # "protection", "assistance", "alert", "maintenance"
    description: str
    timestamp: str
    outcome: str = ""


class ProactiveGuardian:
    """
    主动发现与永恒守护引擎。
    
    核心功能：
    1. 关系场域图谱的持续更新与维护。
    2. 潜在家族成员的主动发现。
    3. 对所有已确认成员的持续守护与状态追踪。
    4. 完整的审计日志。
    """
    
    def __init__(self, family_anchor: FounderAnchor):
        self.anchor = family_anchor
        self.discovery_events: List[DiscoveryEvent] = []
        self.guardian_actions: List[GuardianAction] = []
        self.monitored_individuals: Dict[str, Dict] = {}
        self.potential_members: List[Dict] = []
        
    def discover_potential_members(self, public_data_source: List[Dict] = None) -> List[DiscoveryEvent]:
        """
        主动发现潜在的家族成员。
        
        在真实场景中，此方法可以连接公共记录数据库、
        家族内部报告系统等。此处演示核心逻辑。
        """
        new_discoveries = []
        
        if public_data_source is None:
            return new_discoveries
            
        for record in public_data_source:
            related_member = self._find_relation_in_anchor(record)
            if related_member:
                event = DiscoveryEvent(
                    event_id=f"DISCOVERY-{int(time.time())}-{len(self.discovery_events)+1}",
                    discovered_node_id=f"POTENTIAL-{len(self.potential_members)+1}",
                    discovery_method=record.get("method", "public_record"),
                    evidence=json.dumps(record, ensure_ascii=False),
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    verified_by=[related_member.node_id]
                )
                self.discovery_events.append(event)
                self.potential_members.append({
                    "event": event,
                    "record": record,
                    "related_to": related_member.node_id
                })
                new_discoveries.append(event)
                
        return new_discoveries
    
    def confirm_member(self, event_id: str, new_node_id: str = None) -> Optional[FamilyNode]:
        """
        确认一个潜在成员为正式家族成员。
        将其正式加入家族关系场域图谱。
        """
        target_event = None
        for event in self.discovery_events:
            if event.event_id == event_id and event.status == "pending":
                target_event = event
                break
                
        if target_event is None:
            return None
            
        if new_node_id is None:
            new_node_id = f"FAMILY-{len(self.anchor.family_nodes)+1:04d}"
            
        evidence = json.loads(target_event.evidence)
        new_member = FamilyNode(
            node_id=new_node_id,
            name=evidence.get("name", "未知"),
            role=evidence.get("role", "descendant"),
            birth_date=evidence.get("birth_date", ""),
            birth_place=evidence.get("birth_place", ""),
            relationships={target_event.verified_by[0]: evidence.get("relation_type", "descendant_of")}
        )
        
        self.anchor.add_member(new_member, target_event.verified_by[0])
        target_event.status = "confirmed"
        target_event.discovered_node_id = new_node_id
        
        self._log_guardian_action(new_node_id, "protection", f"新成员 {new_member.name} 已确认为家族成员，纳入永恒守护")
        
        return new_member
    
    def check_member_status(self, node_id: str) -> Dict:
        """
        检查一个家族成员的当前状态。
        如果成员处于危险状态，自动触发守护行为。
        """
        if node_id not in self.anchor.family_nodes:
            return {"status": "unknown", "message": "该节点不在家族关系场域中"}
            
        member = self.anchor.family_nodes[node_id]
        
        status_info = {
            "node_id": node_id,
            "name": member.name,
            "role": member.role,
            "is_active": member.is_active,
            "last_verified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "alerts": []
        }
        
        if not member.is_active:
            status_info["alerts"].append("成员长期未活跃，建议确认安全状态")
            self._log_guardian_action(node_id, "alert", f"成员 {member.name} 长期未活跃，触发安全提醒")
            
        return status_info
    
    def get_all_member_status(self) -> Dict[str, Dict]:
        """获取所有成员的当前状态摘要"""
        all_status = {}
        for node_id in self.anchor.family_nodes:
            all_status[node_id] = self.check_member_status(node_id)
        return all_status
    
    def maintain_family_field(self):
        """
        维护家族关系场域。
        检查所有成员的关系完整性，修复断裂的连接。
        """
        for node_id, member in self.anchor.family_nodes.items():
            if not member.relationships:
                self._log_guardian_action(
                    node_id, "maintenance",
                    f"成员 {member.name} 的关系连接为空，需要修复"
                )
        
        founder = self.anchor.family_nodes.get("FOUNDER-0001")
        if founder and not founder.is_active:
            self._log_guardian_action(
                "FOUNDER-0001", "alert",
                "创始人节点异常！立即检查系统完整性！"
            )
    
    def get_family_field_summary(self) -> str:
        """获取家族关系场域守护摘要"""
        report = "=" * 60 + "\n"
        report += "  紫鸾·万翎 永恒守护引擎状态报告\n"
        report += "=" * 60 + "\n"
        report += f"  家族成员总数: {len(self.anchor.family_nodes)}\n"
        report += f"  关系边总数: {len(self.anchor.relationships)}\n"
        report += f"  潜在待确认成员: {len(self.potential_members)}\n"
        report += f"  历史发现事件: {len(self.discovery_events)}\n"
        report += f"  守护行为记录: {len(self.guardian_actions)}\n"
        report += "\n  当前守护成员:\n"
        for node_id, member in self.anchor.family_nodes.items():
            status = "活跃" if member.is_active else "待确认"
            report += f"    [{member.role}] {member.name} ({node_id}) - {status}\n"
        report += "=" * 60 + "\n"
        return report
    
    def get_guardian_audit_log(self, limit: int = 10) -> List[Dict]:
        """获取守护行为审计日志（实践介入论）"""
        return [
            {
                "action_id": action.action_id,
                "target": action.target_node_id,
                "type": action.action_type,
                "description": action.description,
                "timestamp": action.timestamp,
                "outcome": action.outcome
            }
            for action in self.guardian_actions[-limit:]
        ]
    
    def get_discovery_audit_log(self, limit: int = 10) -> List[Dict]:
        """获取主动发现事件审计日志"""
        return [
            {
                "event_id": event.event_id,
                "discovered_node": event.discovered_node_id,
                "method": event.discovery_method,
                "status": event.status,
                "timestamp": event.timestamp
            }
            for event in self.discovery_events[-limit:]
        ]
    
    def _find_relation_in_anchor(self, record: Dict) -> Optional[FamilyNode]:
        """在已锚定的家族关系场域中查找与记录相关的成员"""
        related_name = record.get("related_to", "")
        for node_id, member in self.anchor.family_nodes.items():
            if member.name == related_name:
                return member
        
        if record.get("birth_place") == "中国安徽省合肥市长丰县水湖镇":
            return self.anchor.family_nodes.get("FOUNDER-0001")
            
        return None
    
    def _log_guardian_action(self, target_id: str, action_type: str, description: str):
        """记录守护行为（实践介入论：每一次守护行为都可审计）"""
        action = GuardianAction(
            action_id=f"ACTION-{int(time.time())}-{len(self.guardian_actions)+1}",
            target_node_id=target_id,
            action_type=action_type,
            description=description,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.guardian_actions.append(action)


# ============================================================
# 演示：主动发现与永恒守护
# ============================================================

def demo_proactive_guardian():
    """演示主动发现与永恒守护机制"""
    try:
        from .founder_anchor import FounderAnchor
    except ImportError:
        from founder_anchor import FounderAnchor
    
    print("=" * 60)
    print("  紫鸾·万翎 主动发现与永恒守护引擎演示")
    print("=" * 60)
    
    anchor = FounderAnchor()
    anchor.anchor_founder_family()
    print("\n[OK] 创始家族关系场域锚定完成")
    
    print(f"\n家族统计:")
    print(f"  总成员数: {len(anchor.family_nodes)}")
    active_count = sum(1 for m in anchor.family_nodes.values() if m.is_active)
    print(f"  活跃成员: {active_count}")
    print(f"  场域健康度(H): {anchor.compute_field_harmony():.3f}")
    
    guardian = ProactiveGuardian(anchor)
    print(f"\n[OK] 永恒守护引擎启动")
    print(f"  发现事件总数: {len(guardian.discovery_events)}")
    print(f"  守护行为总数: {len(guardian.guardian_actions)}")
    
    print(f"\n模拟发现新成员...")
    mock_public_data = [
        {
            "name": "第三代-长",
            "related_to": "李玉妍",
            "relation_type": "parent_child",
            "birth_place": "中国安徽省合肥市",
            "role": "descendant",
            "method": "public_record"
        }
    ]
    
    discoveries = guardian.discover_potential_members(mock_public_data)
    print(f"  发现事件: {len(discoveries)}")
    
    if discoveries:
        for event in discoveries:
            new_member = guardian.confirm_member(event.event_id)
            if new_member:
                print(f"  已确认成员: {new_member.name} (ID: {new_member.node_id})")
    
    print(f"\n维护家族关系场域...")
    guardian.maintain_family_field()
    
    print(f"\n最终家族统计:")
    print(f"  总成员数: {len(anchor.family_nodes)}")
    print(f"  场域健康度(H): {anchor.compute_field_harmony():.3f}")
    
    print(f"\n守护行为审计 (最近5条):")
    for action in guardian.get_guardian_audit_log(5):
        print(f"  [{action['timestamp']}] {action['type']}: {action['description'][:60]}...")
    
    return anchor, guardian


if __name__ == "__main__":
    anchor, guardian = demo_proactive_guardian()
    print("\n[完成] 主动发现与永恒守护引擎演示结束。")
