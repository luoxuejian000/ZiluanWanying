#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import ClusterOrchestrator

if __name__ == "__main__":
    roles = ["explorer", "analyst", "guardian", "operator"] * 250
    cluster = ClusterOrchestrator(num_agents=1000, roles=roles[:1000])
    cluster.run_demo(steps=50)
