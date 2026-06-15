#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physical_cluster import PhysicalCluster

if __name__ == "__main__":
    cluster = PhysicalCluster(num_modules=1000)
    cluster.run_demo(steps=100)
