import time
from core.agent_state import AgentState
from core.field_snapshot import FieldSnapshot
from core.modality_evidence import ModalityEvidence
from core.contradiction_edge import ContradictionEdge
from core.message import Message

try:
    from cprc.fusion.multimodal_fuser import MultimodalFuser
    from cprc.detection.flip_point_detector import FlipPointDetector
    from cprc.stabilizer.decision_engine import decide_stabilization
    from cprc.stabilizer.action_executor import ActionExecutor
except ImportError:
    class MultimodalFuser:
        def fuse(self, evidences):
            return {"fused": evidences}
    
    class FlipPointDetector:
        def detect(self, field_snapshot):
            return None
    
    def decide_stabilization(field_snapshot):
        return None
    
    class ActionExecutor:
        def __init__(self, config):
            self.config = config
        def execute(self, action):
            pass

class ZiluanAgent:
    def __init__(self, agent_id: str, role: str, bus, relation_graph):
        self.agent_id = agent_id
        self.state = AgentState(agent_id=agent_id, role=role)
        self.bus = bus
        self.relation_graph = relation_graph
        self.fuser = MultimodalFuser()
        self.detector = FlipPointDetector()
        self.executor = ActionExecutor({"llm_params": {"temperature": 1.0, "top_p": 1.0}})
        self.inbox = []
        self.bus.subscribe(agent_id, self.receive_message)

    def receive_message(self, message: Message):
        self.inbox.append(message)
        self.relation_graph.add_taction(message.sender_id, self.agent_id, message.action_strength)
        self.relation_graph.add_entwinement(self.agent_id, message.sender_id, 0.5)

    def sense_environment(self) -> list:
        return []

    def think_and_act(self):
        external_evidences = self.sense_environment()
        for msg in self.inbox:
            external_evidences.append(ModalityEvidence(
                modality=f"msg_from_{msg.sender_id}",
                raw_features={"importance": msg.action_strength},
                timestamp=msg.timestamp
            ))
        self.inbox.clear()
        snap = self.fuser.fuse(external_evidences)
        self.state.harmony_snapshot = snap
        warning = self.detector.feed(snap)
        trends = {"dH_dt": 0.0, "dA_dt": 0.0}
        if len(self.fuser.history) >= 2:
            prev = self.fuser.history[-2]
            dt = snap.timestamp - prev.timestamp
            if dt > 0.001:
                trends["dH_dt"] = (snap.H - prev.H) / dt
                trends["dA_dt"] = (snap.A - prev.A) / dt
        recent_H = [s.H for s in self.fuser.history[-10:]]
        action = decide_stabilization(snap, trends["dH_dt"], trends["dA_dt"], recent_H)
        self.executor.execute(action)
        self.state.tau = self.fuser.tau
        if snap.system_state != "NORMAL":
            self.state.status = "alert"
        else:
            self.state.status = "idle"
        status_msg = Message(
            sender_id=self.agent_id,
            receiver_id=None,
            msg_type="state_update",
            content={"U": snap.U, "D": snap.D, "A": snap.A, "H": snap.H, "tau": self.state.tau, "action": action.kind}
        )
        self.bus.publish(status_msg)
        return snap
