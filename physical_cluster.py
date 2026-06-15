"""
物理集群管理器：管理一万个紫鸾模块的生命周期、形态演化和任务分配。
"""
import time
import numpy as np
from typing import Dict, List
from physical.physical_module import PhysicalModule
from physical.morphology import MorphologyGraph
from emergence.emergence_engine import EmergenceEngine

class PhysicalCluster:
    def __init__(self, num_modules: int = 1000):
        self.modules: Dict[str, PhysicalModule] = {}
        self.morphology = MorphologyGraph()
        self.engine = EmergenceEngine(self.morphology)
        self._init_modules(num_modules)

    def _init_modules(self, num: int):
        for i in range(num):
            module_id = f"PM-{i:04d}"
            position = np.random.uniform(-5, 5, 3)
            orientation = np.array([1.0, 0.0, 0.0, 0.0])
            module = PhysicalModule(
                module_id=module_id,
                position=position,
                orientation=orientation,
                thrust_available=np.random.uniform(50, 100),
                current_task="assemble"
            )
            self.modules[module_id] = module
            self.morphology.add_module(module)

    def step(self) -> dict:
        for module in self.modules.values():
            if module.current_task == "assemble":
                nearby_count = len(self.engine._get_nearby_modules(module, self.modules))
                module.local_U = min(1.0, 0.5 + nearby_count * 0.1)
                module.local_A = max(0.0, 0.5 - nearby_count * 0.05)
                module.local_D = 0.3 if nearby_count < 3 else 0.1
                module.local_H = 0.4 * module.local_U + 0.3 * module.local_D - 0.3 * module.local_A
        audit = self.engine.step(self.modules)
        return audit

    def run_demo(self, steps: int = 100):
        print("=" * 60)
        print("  紫鸾·万翎 物理集群形态演化演示")
        print("  模块数量:", len(self.modules))
        print("  初始状态: 随机分布")
        print("  目标: 自组织组装为刚性结构")
        print("=" * 60)
        for step in range(steps):
            audit = self.step()
            connected_ratio = audit["morphology_edges"] / max(1, len(self.modules) * 3)
            status = "稳定" if audit["is_stable"] else "演化中"
            print(f"Step {step+1:03d} | 应力: {audit['cluster_stress_before']:.3f}→{audit['cluster_stress_after']:.3f} | "
                  f"连接: {audit['morphology_edges']}边 | 状态: {status} | 事件: {len(audit['events'])}")
            if audit["is_stable"] and step > 20:
                print(f"  >> 集群在第{step+1}步达到稳态，形态自组织完成")
                break
            time.sleep(0.05)
