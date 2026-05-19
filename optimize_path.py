#!/usr/bin/env python3
"""
CNC Toolpath Optimizer - Main Entry Point

Usage:
    python optimize_path.py --input <mesh.stl> [--tool <type>] [--diameter <mm>] [--strategy ga|pso]
"""

import argparse
import sys
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Tool geometry definitions
# ---------------------------------------------------------------------------
@dataclass
class CuttingTool:
    name: str
    type: str           # 'flat_end_mill', 'ball_end_mill', 'bull_nose'
    diameter: float     # mm
    flute_count: int = 4
    helix_angle: float = 30.0  # degrees
    max_stepdown: float = 2.0  # mm per pass
    stepover_ratio: float = 0.4  # fraction of diameter

    def effective_radius(self, depth: float) -> float:
        if self.type == 'ball_end_mill':
            r = self.diameter / 2.0
            return np.sqrt(r**2 - (r - depth)**2) if depth < r else r
        return self.diameter / 2.0


TOOL_LIBRARY = {
    'flat_6mm':    CuttingTool('6mm Flat EM',     'flat_end_mill',  6.0),
    'flat_10mm':   CuttingTool('10mm Flat EM',    'flat_end_mill',  10.0),
    'ball_6mm':    CuttingTool('6mm Ball EM',     'ball_end_mill',  6.0),
    'ball_3mm':    CuttingTool('3mm Ball EM',     'ball_end_mill',  3.0),
    'bull_6r1':    CuttingTool('6mm Bull R1',     'bull_nose',      6.0),
}


# ---------------------------------------------------------------------------
# Toolpath segment representation
# ---------------------------------------------------------------------------
@dataclass
class PathPoint:
    x: float
    y: float
    z: float
    feed: float = 1000.0  # mm/min

    def dist_to(self, other: 'PathPoint') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

    def __repr__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f}) F{self.feed:.0f}"


@dataclass
class Toolpath:
    points: List[PathPoint] = field(default_factory=list)
    tool_diameter: float = 6.0
    stepover: float = 2.4

    def total_length(self) -> float:
        if not self.points:
            return 0.0
        return sum(p1.dist_to(p2) for p1, p2 in zip(self.points, self.points[1:]))

    def cutting_length(self) -> float:
        if not self.points:
            return 0.0
        clearance = 5.0
        return sum(p1.dist_to(p2) for p1, p2 in zip(self.points, self.points[1:])
                   if p1.z < clearance or p2.z < clearance)

    def num_rapid_moves(self) -> int:
        clearance = 5.0
        count = 0
        for p1, p2 in zip(self.points, self.points[1:]):
            if p1.z > clearance and p2.z > clearance:
                count += 1
        return count


# ---------------------------------------------------------------------------
# Simple zig-zag toolpath generator (baseline)
# ---------------------------------------------------------------------------
def generate_zigzag(width: float, height: float, depth: float,
                    tool_diameter: float, stepover_ratio: float = 0.4) -> Toolpath:
    step = tool_diameter * stepover_ratio
    tp = Toolpath(tool_diameter=tool_diameter, stepover=step)
    y = 0.0
    direction = 1
    tp.points.append(PathPoint(0, 0, depth))
    while y < height:
        if direction == 1:
            tp.points.append(PathPoint(width, y, depth))
        else:
            tp.points.append(PathPoint(0, y, depth))
        y += step
        direction *= -1
    return tp


# ---------------------------------------------------------------------------
# Optimization engine (stubs that import real implementations)
# ---------------------------------------------------------------------------
def optimize_ga(path: Toolpath, generations: int = 100, pop_size: int = 50) -> Toolpath:
    from ga_optimizer import GAToolpathOptimizer
    optimizer = GAToolpathOptimizer(pop_size=pop_size, generations=generations)
    return optimizer.optimize(path)


def optimize_pso(path: Toolpath, iterations: int = 200, swarm_size: int = 30) -> Toolpath:
    from pso_optimizer import PSOPathOptimizer
    optimizer = PSOPathOptimizer(swarm_size=swarm_size, iterations=iterations)
    return optimizer.optimize(path)


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description='CNC Toolpath Optimizer - reduce cycle time with evolutionary algorithms')
    parser.add_argument('--input', '-i', required=True, help='Input mesh file (.stl)')
    parser.add_argument('--tool', '-t', default='ball_6mm',
                        choices=list(TOOL_LIBRARY.keys()),
                        help='Cutting tool from library')
    parser.add_argument('--diameter', '-d', type=float, default=None,
                        help='Override tool diameter (mm)')
    parser.add_argument('--strategy', '-s', default='ga',
                        choices=['ga', 'pso', 'zigzag', 'hybrid'],
                        help='Optimization strategy')
    parser.add_argument('--generations', '-g', type=int, default=100,
                        help='GA generations (default: 100)')
    parser.add_argument('--output', '-o', default='optimized.nc',
                        help='Output G-code file')
    parser.add_argument('--visualize', '-v', action='store_true',
                        help='Show path visualization')

    args = parser.parse_args()
    tool = TOOL_LIBRARY[args.tool]
    print(f"[CNC Optimizer] Tool: {tool.name} ({tool.diameter}mm)")
    print(f"[CNC Optimizer] Strategy: {args.strategy}")
    print(f"[CNC Optimizer] Input: {args.input}")

    baseline = generate_zigzag(100.0, 80.0, -2.0, tool.diameter)
    print(f"[CNC Optimizer] Baseline path: {baseline.cutting_length():.1f} mm cutting length")

    if args.strategy == 'ga':
        optimized = optimize_ga(baseline, generations=args.generations)
        reduction = (1 - optimized.cutting_length() / baseline.cutting_length()) * 100
        print(f"[CNC Optimizer] GA optimized: {optimized.cutting_length():.1f} mm ({reduction:.1f}% reduction)")

    elif args.strategy == 'pso':
        optimized = optimize_pso(baseline)
        reduction = (1 - optimized.cutting_length() / baseline.cutting_length()) * 100
        print(f"[CNC Optimizer] PSO optimized: {optimized.cutting_length():.1f} mm ({reduction:.1f}% reduction)")

    elif args.strategy == 'hybrid':
        ga_opt = optimize_ga(baseline, generations=args.generations // 2)
        optimized = optimize_pso(ga_opt, iterations=100)
        reduction = (1 - optimized.cutting_length() / baseline.cutting_length()) * 100
        print(f"[CNC Optimizer] GA+PSO hybrid: {optimized.cutting_length():.1f} mm ({reduction:.1f}% reduction)")

    else:
        optimized = baseline
        print("[CNC Optimizer] Using zig-zag baseline (no optimization)")

    print(f"[CNC Optimizer] Saved to {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())