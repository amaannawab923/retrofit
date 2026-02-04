# Legacy Warehouse Retrofit Framework
## Backporting Robotic Automation to Traditional Warehouses

---

## Executive Summary

This framework provides a systematic approach for retrofitting legacy warehouses to accommodate robotic automation (AGVs/AMRs). Unlike modern facilities (Amazon, Nestle) designed ground-up for robotics, legacy warehouses require careful assessment, digital transformation, and phased implementation.

**Framework Foundation:**
- Layout A (Hu et al.): Multigraph modeling G=(N,E), heterogeneous AGV scheduling
- Layout B (Zhang et al.): Evolutionary layout optimization with fitness approximation
- Layout C (Jabrane & Borgemo): Real-world retrofit case study at Haldex

---

## Framework Overview

```
+------------------------------------------------------------------+
|                  LEGACY WAREHOUSE RETROFIT FRAMEWORK              |
+------------------------------------------------------------------+
|                                                                    |
|  PHASE 1          PHASE 2           PHASE 3          PHASE 4      |
|  --------         --------          --------         --------     |
|  Assessment  -->  Digital Twin  --> Pathfinding  --> AGV Design   |
|  & Audit          Creation          Infrastructure    Integration |
|                                                                    |
|                          |                                         |
|                          v                                         |
|                    PHASE 5                                         |
|                    --------                                        |
|                    Simulation                                      |
|                    & Validation                                    |
|                                                                    |
+------------------------------------------------------------------+
```

---

# Phase 1: Assessment & Audit

## 1.1 Objectives
- Collect comprehensive data about the legacy warehouse
- Identify physical constraints and limitations
- Analyze current workflows and material flows
- Document existing infrastructure

## 1.2 Data Collection Checklist

### Physical Measurements
| Item | Measurement | Notes |
|------|-------------|-------|
| Total floor area | ___ sqm | Include all levels |
| Aisle widths | ___ m (min/max) | Document variations |
| Ceiling height | ___ m | Check for low areas |
| Door dimensions | ___ m (W x H) | All access points |
| Ramp grades | ___ degrees | If multi-level |
| Floor load capacity | ___ kg/sqm | Structural limits |

### Structural Constraints
| Constraint Type | Location | Impact on AGV |
|-----------------|----------|---------------|
| Support columns | Grid: ___x___m | Navigation obstacles |
| Fixed equipment | ___ | Cannot relocate |
| Narrow passages | ___ m wide | May require one-way |
| Floor irregularities | ___ | May need repair |
| Electrical conduits | ___ | Height restrictions |

### Current Workflow Analysis
- [ ] Map all material flow paths
- [ ] Identify pickup points (origin nodes)
- [ ] Identify drop-off points (destination nodes)
- [ ] Document task frequency per path
- [ ] Measure average task duration
- [ ] Identify peak operation hours
- [ ] Document human worker zones

## 1.3 Deliverables
1. **Floor Plan Scan** - CAD or measured drawings
2. **Constraint Map** - All obstacles and limitations marked
3. **Flow Analysis Report** - Current material movement patterns
4. **Feasibility Assessment** - Go/no-go for retrofit

---

# Phase 2: Digital Twin Creation

## 2.1 Grid Overlay System

### Grid Cell Selection Criteria
| Warehouse Size | Recommended Grid | Node Density |
|----------------|------------------|--------------|
| < 5,000 sqm | 0.5m x 0.5m | High |
| 5,000-15,000 sqm | 1.0m x 1.0m | Medium |
| > 15,000 sqm | 2.0m x 2.0m | Low |

### Scaling Convention
```
1 grid cell = 1 meter (default)
Coordinate system: Origin at bottom-left corner
X-axis: East (positive)
Y-axis: North (positive)
```

## 2.2 Node Placement Strategy

Based on Layout A's multigraph approach G = (N, E):

### Node Types
| Node Type | Symbol | Placement Rule |
|-----------|--------|----------------|
| Intersection | N_int | Every aisle crossing |
| Pickup | N_pick | At storage rack locations |
| Drop-off | N_drop | At destination areas |
| Charging | N_chrg | Near power sources, away from traffic |
| Buffer | N_buf | Queue waiting areas |
| Decision | N_dec | Route choice points |

### Node Placement Rules
1. Place nodes at every aisle intersection
2. Add nodes at all pickup/drop-off locations
3. Include nodes at decision points (path splits)
4. Maximum spacing: 10m between consecutive nodes
5. Minimum spacing: 2m (AGV length + safety buffer)

## 2.3 Zone Definition

### Standard Zone Classification
```
+------------------------------------------------------------------+
|                         RECEIVING ZONE                            |
|    [N01]----[N02]----[N03]----[N04]     (Dock Doors)             |
+------------------------------------------------------------------+
|         |        |        |        |                              |
|    [N05]----[N06]----[N07]----[N08]     STORAGE ZONE             |
|         |        |        |        |     (Rack Aisles)           |
|    [N09]----[N10]----[N11]----[N12]                              |
|         |        |        |        |                              |
+------------------------------------------------------------------+
|    [N13]----[N14]----[N15]----[N16]     SHIPPING ZONE            |
|                                          (Outbound)               |
+------------------------------------------------------------------+
|    [CHG1]  [CHG2]                        CHARGING ZONE           |
+------------------------------------------------------------------+
```

### Zone Requirements
| Zone | Min Width | AGV Access | Node Density |
|------|-----------|------------|--------------|
| Receiving | 3.0m | Bidirectional | High |
| Storage | 2.5m | Bidirectional | Medium |
| Shipping | 3.0m | Bidirectional | High |
| Charging | 2.0m | One-way in | Low |
| Buffer | 4.0m | Queue space | Medium |

## 2.4 Deliverables
1. **Digital Floor Plan** - Scaled grid overlay
2. **Node Definition File** - CSV/JSON with coordinates
3. **Zone Map** - Classified areas with boundaries
4. **Edge Definition** - Connections between nodes

---

# Phase 3: Pathfinding Infrastructure

## 3.1 Navigation Graph Construction

### Converting Layout to Graph G = (N, E)
```python
# Node definition
nodes = {
    'N01': {'x': 0, 'y': 20, 'zone': 'receiving', 'type': 'dock'},
    'N02': {'x': 10, 'y': 20, 'zone': 'receiving', 'type': 'dock'},
    # ... additional nodes
}

# Edge definition
edges = {
    'E01': {'from': 'N01', 'to': 'N02', 'distance': 10, 'bidirectional': True},
    'E02': {'from': 'N01', 'to': 'N05', 'distance': 10, 'bidirectional': True},
    # ... additional edges
}
```

## 3.2 Distance Calculation Formulas

### Manhattan Distance (Grid-Based Movement)
```
d_manhattan(A, B) = |x_A - x_B| + |y_A - y_B|
```

### Euclidean Distance (Open Areas)
```
d_euclidean(A, B) = sqrt((x_A - x_B)^2 + (y_A - y_B)^2)
```

### Weighted Distance (Congestion-Aware)
```
d_weighted(A, B) = d_manhattan(A, B) * w_zone

where w_zone:
  - Receiving: 1.2 (high traffic)
  - Storage: 1.0 (standard)
  - Shipping: 1.3 (very high traffic)
  - Charging: 0.8 (low traffic)
```

### Travel Time Formula
```
t_travel = d/v + t_turn * n_turns + t_accel + t_decel

where:
  d = distance (meters)
  v = cruise speed (default: 1.0 m/s)
  t_turn = turn delay (default: 2.0 s per 90-degree turn)
  n_turns = number of turns on path
  t_accel = acceleration time
  t_decel = deceleration time
```

## 3.3 Distance Matrix Template

### Sample 12-Node Matrix (meters)
|     | N01 | N02 | N03 | N04 | N05 | N06 | N07 | N08 | N09 | N10 | N11 | N12 |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| N01 | 0   | 10  | 20  | 30  | 10  | 20  | 30  | 40  | 20  | 30  | 40  | 50  |
| N02 | 10  | 0   | 10  | 20  | 20  | 10  | 20  | 30  | 30  | 20  | 30  | 40  |
| N03 | 20  | 10  | 0   | 10  | 30  | 20  | 10  | 20  | 40  | 30  | 20  | 30  |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## 3.4 Conflict Point Identification

### Critical Path Criteria
A path is CRITICAL if:
- Used by > 20% of all tasks
- Has no alternative routes
- Utilization > 80% of capacity

### Conflict Resolution Strategies
1. **Time-based reservation** - Reserve path segments by time slot
2. **Priority-based** - Higher priority tasks get right-of-way
3. **FCFS** - First-Come-First-Served at intersections
4. **Deadlock prevention** - Detect and resolve circular waits

## 3.5 Deliverables
1. **Distance Matrix** - Node-to-node distances
2. **Travel Time Matrix** - Including turn penalties
3. **Conflict Map** - High-risk intersection identification
4. **Alternative Routes** - Backup paths for critical segments

---

# Phase 4: AGV Integration Design

## 4.1 Fleet Sizing Methodology

Based on Layout C's approach:

### Fleet Size Calculation
```
N_agv = ceiling(Total_daily_tasks * Avg_task_time / (Shift_duration * Utilization_target))

Example:
- Daily tasks: 500
- Avg task time: 3 minutes
- Shift duration: 8 hours = 480 minutes
- Target utilization: 70%

N_agv = ceiling(500 * 3 / (480 * 0.7)) = ceiling(4.46) = 5 AGVs
```

### Fleet Sizing Table
| Daily Tasks | Avg Task (min) | Recommended Fleet |
|-------------|----------------|-------------------|
| 100-200 | 3 | 2-3 AGVs |
| 200-400 | 3 | 3-5 AGVs |
| 400-600 | 3 | 5-7 AGVs |
| 600-1000 | 3 | 7-10 AGVs |

## 4.2 Charging Station Placement

### Placement Criteria
1. Near power infrastructure
2. Away from high-traffic paths
3. Accessible from multiple zones
4. Queue space for waiting AGVs

### Charging Station Ratio
```
N_charging = ceiling(N_agv / 3) + 1

Example: 5 AGVs -> ceiling(5/3) + 1 = 3 charging stations
```

## 4.3 Task Assignment Zones

### Zone-to-Zone Flow Matrix
| From \ To | Receiving | Storage | Shipping |
|-----------|-----------|---------|----------|
| Receiving | - | 80% | 5% |
| Storage | 10% | 20% | 70% |
| Shipping | 5% | 15% | - |

## 4.4 Safety Buffer Zones

### Human-AGV Interaction Zones
| Zone Type | Speed Limit | Warning Distance |
|-----------|-------------|------------------|
| Mixed traffic | 0.5 m/s | 3m |
| AGV-only | 1.5 m/s | 1m |
| Pedestrian crossing | 0.3 m/s | 5m |

## 4.5 Deliverables
1. **Fleet Sizing Report** - Recommended AGV count
2. **Charging Layout** - Station locations and capacity
3. **Task Zone Map** - Assignment boundaries
4. **Safety Protocol** - Human-AGV interaction rules

---

# Phase 5: Simulation & Validation

## 5.1 Simulation Parameters

### Default Configuration (from research)
| Parameter | Value | Unit |
|-----------|-------|------|
| AGV Count | 5 | vehicles |
| Cruise Speed | 1.0 | m/s |
| Turn Delay | 2.0 | seconds |
| Task Arrival Rate | 3 | tasks/minute |
| Pick Time | 15 | seconds |
| Drop Time | 10 | seconds |
| Battery Capacity | 100 | % |
| Low Battery Threshold | 20 | % |
| Charging Rate | 10 | %/hour |
| Simulation Duration | 8 | hours |

## 5.2 Performance Metrics

### Primary Metrics (from Layout A research)
| Metric | Formula | Target |
|--------|---------|--------|
| Throughput | tasks_completed / time_period | > 90% of demand |
| AGV Utilization | active_time / total_time | 60-80% |
| Avg Travel Distance | total_distance / total_tasks | Minimize |
| Avg Task Time | total_task_time / total_tasks | < 5 min |
| Idle Time % | idle_time / total_time | < 20% |
| Conflict Rate | conflicts / total_trips | < 5% |

### Expected Improvements (from research)
- Task completion time reduction: **13.62%**
- Delay time reduction: **76.69%**

## 5.3 Validation Criteria

### Go/No-Go Thresholds
| Metric | Minimum Acceptable | Target |
|--------|-------------------|--------|
| Throughput | 85% of demand | 95% |
| Utilization | 50% | 70% |
| Conflict Rate | < 10% | < 3% |
| Battery Events | < 5/shift | < 2/shift |

## 5.4 Simulation Tools

### Recommended Platforms
1. **FlexSim** - Digital twin (used in Layout A)
2. **AnyLogic** - Multi-method simulation
3. **Python + SimPy** - Custom discrete-event simulation
4. **MATLAB** - Mathematical modeling

## 5.5 Deliverables
1. **Simulation Model** - Working digital twin
2. **Performance Report** - Metrics analysis
3. **Validation Certificate** - Go/no-go decision
4. **Optimization Recommendations** - Improvement areas

---

# Implementation Roadmap

## Phased Implementation

```
Week 1-2:   Phase 1 - Assessment & Audit
Week 3-4:   Phase 2 - Digital Twin Creation
Week 5-6:   Phase 3 - Pathfinding Infrastructure
Week 7-8:   Phase 4 - AGV Integration Design
Week 9-12:  Phase 5 - Simulation & Validation
Week 13+:   Physical Implementation
```

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| Floor unsuitable | Assess load capacity early |
| Aisle too narrow | Identify before AGV selection |
| Power insufficient | Survey electrical capacity |
| Workflow disruption | Phased rollout with fallback |
| Employee resistance | Training and change management |

---

# Appendices

## Appendix A: Sample Layout Templates

### Template A: Small Warehouse (< 5,000 sqm)
- Dimensions: 50m x 80m
- Zones: 4 (Receiving, Storage, Shipping, Charging)
- Nodes: 25-40
- Recommended AGVs: 2-3

### Template B: Medium Warehouse (5,000-15,000 sqm)
- Dimensions: 100m x 120m
- Zones: 6 (add Buffer, Staging)
- Nodes: 50-100
- Recommended AGVs: 4-8

### Template C: Large Warehouse (> 15,000 sqm)
- Dimensions: 150m x 200m
- Zones: 8+ (multi-zone considerations)
- Nodes: 100-250
- Recommended AGVs: 10-20

## Appendix B: Related Documents

1. `mathematical_foundations/01_distance_calculation_system.md`
2. `mathematical_foundations/02_distance_matrix_template.md`
3. `mathematical_foundations/03_simulation_parameters.md`
4. `warehouse_layout_research_analysis.md`

## Appendix C: References

1. Hu, E., He, J., & Shen, S. (2023). A dynamic integrated scheduling method for heterogeneous AGV fleets. *Frontiers in Neurorobotics*, 16.

2. Zhang, H., et al. (2018). Layout Design for Intelligent Warehouse by Evolution with Fitness Approximation. *IEEE Access*, 7.

3. Jabrane, Z., & Borgemo, E. (2018). Evaluating Usage of AGVs with Respect to Warehouse Layout Changes. Lund University.

---

*Framework Version: 1.0*
*Last Updated: January 2026*
*Based on research analysis of Frontiers in Neurorobotics and related publications*
