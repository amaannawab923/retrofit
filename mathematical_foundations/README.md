# Mathematical Foundations for Legacy Warehouse Robotics Retrofit Simulation

## Overview

This documentation provides complete mathematical foundations for simulating AGV (Automated Guided Vehicle) operations in legacy warehouse environments. The formulations are adapted from Layout A research and designed for practical implementation in Python and Excel.

## Research Foundation

Based on Layout A's research framework:
- **Transportation Cost**: `f = min sum_{k in K} c_k (z^e_ku - z^s_kd)`
- **Warehouse Representation**: Multigraph `G = (N, E)`
- **Battery Constraints**: `bl_k <= lambda^r_ku <= bh_k`

## Document Structure

### 1. Distance Calculation System (`01_distance_calculation_system.md`)
- Manhattan distance: `d(A,B) = |x_A - x_B| + |y_A - y_B|`
- Euclidean distance for open areas
- Weighted distance with congestion factors
- Travel time formula: `T = d/v + n_turns * t_turn + t_accel + t_decel + T_queue`

### 2. Distance Matrix Template (`02_distance_matrix_template.md`)
- 12-node sample warehouse layout
- Node-to-node distance matrix
- Zone-to-zone aggregated distances
- Critical path identification methodology

### 3. Simulation Parameters (`03_simulation_parameters.md`)
Complete parameter tables for:
- AGV fleet (count, speed, acceleration, dimensions)
- Battery (capacity, thresholds, discharge rates)
- Tasks (arrival rate, service times, priorities)
- Layout (aisle dimensions, zones)
- Traffic (capacity limits, congestion weights)

### 4. Performance Metrics (`04_performance_metrics.md`)
Formulas for:
- Throughput: `tasks_completed / time_period`
- AGV utilization: `active_time / total_time`
- Average travel distance per task
- Idle time percentage
- Conflict frequency and resolution time

### 5. Constraint Equations (`05_constraint_equations.md`)
Legacy warehouse limitations:
- Aisle width: `W >= W_agv + 2*d_safety`
- Floor load capacity
- Maximum AGVs per aisle
- Battery depletion model based on `bl_k <= lambda^r_ku <= bh_k`

### 6. Optimization Objective (`06_optimization_objective.md`)
Multi-objective function:
```
Z = alpha_1*Z_travel + alpha_2*Z_time + alpha_3*Z_energy + alpha_4*Z_conflict
```

With recommended weight configurations for different scenarios.

### 7. Excel Templates (`07_excel_templates.md`)
Ready-to-use Excel formulas for all calculations.

## Python Implementation

The complete Python implementation is in `warehouse_math_foundations.py`:

```python
from warehouse_math_foundations import (
    DistanceCalculator,
    TravelTimeCalculator,
    WarehouseDistanceMatrix,
    SimulationConfig,
    PerformanceMetrics,
    ConstraintChecker,
    BatteryConstraints,
    ObjectiveFunction,
    OptimizationWeights
)

# Create warehouse configuration
nodes = {
    'N01': (0, 20, 'Receiving'),
    'N02': (10, 20, 'Receiving'),
    # ... more nodes
}

# Generate distance matrices
dist_matrix = WarehouseDistanceMatrix(nodes)
manhattan = dist_matrix.calculate_manhattan_matrix()

# Configure simulation
config = SimulationConfig()
config.agv.count = 5
config.task.arrival_rate = 0.5

# Check constraints
aisle_check = ConstraintChecker.check_aisle_width(
    aisle_width=2.5,
    agv_width=0.8,
    safety_buffer=0.5
)

# Evaluate optimization objective
weights = OptimizationWeights(travel=0.35, time=0.30, energy=0.20, conflict=0.15)
obj_func = ObjectiveFunction(weights, manhattan, list(nodes.keys()))
result = obj_func.evaluate(paths, times, waits, services, battery, conflicts)
```

## Key Equations Reference

| Component | Formula |
|-----------|---------|
| Manhattan Distance | `d = \|x_A - x_B\| + \|y_A - y_B\|` |
| Travel Time | `T = d/v + n*t_turn + 2*v/a + T_queue` |
| Congestion Weight | `w = 1 + alpha * (n_agv / C)` |
| Throughput | `lambda = N_tasks / T_period` |
| Utilization | `U = T_active / T_total` |
| Battery Range | `D_max = (B - bl_k) / (r / v)` |
| Objective | `Z = sum_i alpha_i * Z_i` |

## Default Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| AGV Count | 5 | - |
| Cruise Speed | 1.5 | m/s |
| Acceleration | 0.5 | m/s^2 |
| Turn Delay | 2.0 | s |
| Battery Low (bl_k) | 20 | % |
| Battery High (bh_k) | 95 | % |
| Task Arrival Rate | 0.5 | /min |
| Aisle Width | 2.5 | m |
| Max AGVs/Aisle | 2 | - |

## Usage Notes

1. **Distance Calculations**: Use Manhattan for grid-constrained movement, Euclidean for open areas
2. **Travel Time**: Always account for acceleration profile on short distances
3. **Battery**: Ensure task feasibility check before assignment
4. **Constraints**: Validate all physical constraints before simulation
5. **Optimization**: Adjust weights based on operational priorities

## File Listing

```
mathematical_foundations/
├── README.md                           # This file
├── 01_distance_calculation_system.md   # Distance formulas
├── 02_distance_matrix_template.md      # Matrix templates
├── 03_simulation_parameters.md         # Parameter definitions
├── 04_performance_metrics.md           # KPI formulas
├── 05_constraint_equations.md          # Constraint models
├── 06_optimization_objective.md        # Objective function
├── 07_excel_templates.md               # Excel formulas
└── warehouse_math_foundations.py       # Python implementation
```

## Version

Version 1.0.0 - Initial mathematical foundations documentation.
