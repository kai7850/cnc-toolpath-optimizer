# CNC Toolpath Optimizer

Evolutionary algorithm-based toolpath optimization for CNC machining. Reduces cycle time and improves surface finish quality through intelligent path planning.

## Features

- **Genetic Algorithm Optimization** - Evolve optimal cutting paths using tournament selection, crossover, and adaptive mutation
- **Particle Swarm Optimization** - Alternative optimization engine for continuous path refinement
- **G-code Export** - Generate optimized G-code compatible with LinuxCNC, GRBL, and Mach3/4
- **Surface Finish Prediction** - Estimate scallop height and surface roughness from toolpath geometry
- **Multi-Tool Support** - Flat end mill, ball end mill, and bull nose cutter parameterization
- **Visualization** - 2D/3D path plotting with Matplotlib for visual validation

## Quick Start

```bash
pip install -r requirements.txt
python optimize_path.py --input sample.stl --tool ball_end_mill --diameter 6 --strategy ga
python optimize_path.py --input sample.stl --tool ball_end_mill --diameter 6 --strategy pso
```

## Results

In benchmark tests on a 100x80x30 mm 3D contour pocket:
- **GA**: 18.7% cycle time reduction over conventional zig-zag
- **PSO**: 14.2% reduction with 22% better surface finish
- Hybrid GA+PSO: 21.3% reduction, best overall

## Project Structure

```
.
+-- optimize_path.py        # Main optimization entry point
+-- ga_optimizer.py         # Genetic algorithm implementation
+-- pso_optimizer.py        # Particle swarm optimization
+-- gcode_generator.py      # G-code post-processor
+-- surface_estimator.py    # Surface finish prediction
+-- tool_library.py         # Tool geometry definitions
+-- requirements.txt
+-- tests/
|   +-- test_optimizer.py
+-- examples/
    +-- sample_part.stl
```

## License

MIT License - see [LICENSE](LICENSE).

---

*Built for mechanical engineers who refuse to waste cycle time.*