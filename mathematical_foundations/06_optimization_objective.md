# Optimization Objective Function
## Adapted from Layout A Research for Legacy Warehouse Retrofit

---

## 1. Original Layout A Formulation

Based on the research: **f = min sum_{k in K} c_k (z^e_ku - z^s_kd)**

This represents the transportation cost minimization where:
- `K` = Set of AGVs
- `c_k` = Cost coefficient for AGV k
- `z^e_ku` = End node u of edge e
- `z^s_kd` = Start node d of task

---

## 2. Adapted Multi-Objective Function for Legacy Retrofit

### 2.1 Primary Objective: Minimize Total Operational Cost

```
min Z = alpha_1 * Z_travel + alpha_2 * Z_time + alpha_3 * Z_energy + alpha_4 * Z_conflict
```

Where:
- `alpha_i` = Weight coefficients (sum to 1.0)
- `Z_travel` = Total travel distance cost
- `Z_time` = Total time cost (including waiting)
- `Z_energy` = Battery/energy consumption cost
- `Z_conflict` = Conflict and congestion cost

### 2.2 Component Formulations

**Travel Distance Component:**
```
Z_travel = sum_{k in K} sum_{(i,j) in path_k} d_ij * w_ij
```

**Time Component:**
```
Z_time = sum_{k in K} (T_travel_k + T_wait_k + T_service_k)
```

**Energy Component:**
```
Z_energy = sum_{k in K} (B_start_k - B_end_k) * c_energy
```

**Conflict Component:**
```
Z_conflict = sum_{conflicts} (T_resolution * c_conflict)
```

---

## 3. Detailed Optimization Model

### 3.1 Decision Variables

| Variable | Type | Description |
|----------|------|-------------|
| x_ijk | Binary | 1 if AGV k traverses edge (i,j) |
| y_mk | Binary | 1 if task m assigned to AGV k |
| t_ik | Continuous | Time AGV k arrives at node i |
| b_ik | Continuous | Battery level of AGV k at node i |
| s_mk | Continuous | Start time of task m on AGV k |

### 3.2 Complete Mathematical Model

```
MINIMIZE:
    Z = sum_{k in K} sum_{(i,j) in E} c_ij * d_ij * x_ijk          # Travel cost
      + sum_{k in K} sum_{m in M} (t_complete_mk - t_release_m) * c_time  # Tardiness
      + sum_{k in K} (b_start_k - b_end_k) * c_battery              # Battery cost
      + sum_{conflicts} T_conflict * c_conflict                     # Conflict penalty

SUBJECT TO:

    # Assignment constraints
    sum_{k in K} y_mk = 1                    for all m in M         (Each task assigned once)

    # Flow conservation
    sum_{j:(i,j) in E} x_ijk - sum_{j:(j,i) in E} x_jik = {
        1   if i = origin_k
        -1  if i = destination_k
        0   otherwise
    }                                        for all k in K, i in N

    # Time consistency
    t_jk >= t_ik + travel_time(i,j) + service_time(i) - M*(1-x_ijk)
                                            for all (i,j) in E, k in K

    # Battery constraints (from Layout A: bl_k <= lambda <= bh_k)
    b_jk = b_ik - consumption_rate * d_ij * x_ijk
    b_ik >= bl_k                            for all i in N, k in K
    b_ik <= bh_k                            for all i in N, k in K

    # Capacity constraints
    sum_{k: edge(i,j) active at time t} x_ijk <= C_ij  for all edges

    # Binary and bounds
    x_ijk in {0, 1}
    y_mk in {0, 1}
    t_ik >= 0
    0 <= b_ik <= B_max
```

---

## 4. Python Implementation

### 4.1 Objective Function Calculator

```python
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class OptimizationWeights:
    """Weights for multi-objective optimization."""
    travel: float = 0.35      # alpha_1: Distance weight
    time: float = 0.30        # alpha_2: Time weight
    energy: float = 0.20      # alpha_3: Energy weight
    conflict: float = 0.15    # alpha_4: Conflict weight

    def validate(self):
        """Ensure weights sum to 1.0."""
        total = self.travel + self.time + self.energy + self.conflict
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")


class ObjectiveFunction:
    """
    Multi-objective optimization function for AGV scheduling.

    Based on Layout A: f = min sum_{k in K} c_k (z^e_ku - z^s_kd)
    Adapted for legacy warehouse retrofit.
    """

    def __init__(
        self,
        weights: OptimizationWeights,
        distance_matrix: np.ndarray,
        node_ids: List[str],
        cost_per_meter: float = 0.01,      # $/m
        cost_per_second: float = 0.005,    # $/s
        cost_per_battery_pct: float = 0.1, # $/% battery
        cost_per_conflict: float = 5.0     # $/conflict
    ):
        self.weights = weights
        self.weights.validate()
        self.distance_matrix = distance_matrix
        self.node_ids = node_ids
        self.node_to_idx = {n: i for i, n in enumerate(node_ids)}

        self.c_distance = cost_per_meter
        self.c_time = cost_per_second
        self.c_battery = cost_per_battery_pct
        self.c_conflict = cost_per_conflict

    def get_distance(self, from_node: str, to_node: str) -> float:
        """Get distance between two nodes."""
        i = self.node_to_idx[from_node]
        j = self.node_to_idx[to_node]
        return self.distance_matrix[i, j]

    def calculate_travel_cost(self, paths: Dict[str, List[str]]) -> float:
        """
        Calculate total travel distance cost.

        Z_travel = sum_{k} sum_{(i,j) in path_k} d_ij

        Args:
            paths: Dict mapping agv_id -> list of node IDs in path

        Returns:
            Total travel cost
        """
        total_distance = 0.0
        for agv_id, path in paths.items():
            for i in range(len(path) - 1):
                total_distance += self.get_distance(path[i], path[i+1])
        return total_distance * self.c_distance

    def calculate_time_cost(
        self,
        travel_times: Dict[str, float],
        wait_times: Dict[str, float],
        service_times: Dict[str, float]
    ) -> float:
        """
        Calculate total time cost.

        Z_time = sum_{k} (T_travel_k + T_wait_k + T_service_k)

        Args:
            travel_times: Dict mapping agv_id -> travel time (seconds)
            wait_times: Dict mapping agv_id -> wait time (seconds)
            service_times: Dict mapping agv_id -> service time (seconds)

        Returns:
            Total time cost
        """
        total_time = 0.0
        for agv_id in travel_times:
            total_time += travel_times.get(agv_id, 0)
            total_time += wait_times.get(agv_id, 0)
            total_time += service_times.get(agv_id, 0)
        return total_time * self.c_time

    def calculate_energy_cost(
        self,
        battery_consumption: Dict[str, float]
    ) -> float:
        """
        Calculate battery/energy cost.

        Z_energy = sum_{k} (B_start_k - B_end_k)

        Args:
            battery_consumption: Dict mapping agv_id -> battery % used

        Returns:
            Total energy cost
        """
        total_consumption = sum(battery_consumption.values())
        return total_consumption * self.c_battery

    def calculate_conflict_cost(
        self,
        conflicts: List[Dict]
    ) -> float:
        """
        Calculate conflict penalty cost.

        Z_conflict = N_conflicts * c_conflict

        Args:
            conflicts: List of conflict records

        Returns:
            Total conflict cost
        """
        return len(conflicts) * self.c_conflict

    def evaluate(
        self,
        paths: Dict[str, List[str]],
        travel_times: Dict[str, float],
        wait_times: Dict[str, float],
        service_times: Dict[str, float],
        battery_consumption: Dict[str, float],
        conflicts: List[Dict]
    ) -> Dict:
        """
        Evaluate complete objective function.

        Z = alpha_1*Z_travel + alpha_2*Z_time + alpha_3*Z_energy + alpha_4*Z_conflict

        Returns:
            Dict with total cost and component breakdown
        """
        z_travel = self.calculate_travel_cost(paths)
        z_time = self.calculate_time_cost(travel_times, wait_times, service_times)
        z_energy = self.calculate_energy_cost(battery_consumption)
        z_conflict = self.calculate_conflict_cost(conflicts)

        # Normalize components (optional - for fair weighting)
        # Here we use raw costs; normalization can be added if needed

        z_total = (
            self.weights.travel * z_travel +
            self.weights.time * z_time +
            self.weights.energy * z_energy +
            self.weights.conflict * z_conflict
        )

        return {
            'total_cost': z_total,
            'travel_cost': z_travel,
            'time_cost': z_time,
            'energy_cost': z_energy,
            'conflict_cost': z_conflict,
            'weighted_components': {
                'travel': self.weights.travel * z_travel,
                'time': self.weights.time * z_time,
                'energy': self.weights.energy * z_energy,
                'conflict': self.weights.conflict * z_conflict
            }
        }


# Example usage
if __name__ == "__main__":
    # Sample distance matrix (simplified)
    distance_matrix = np.array([
        [0, 10, 20, 30],
        [10, 0, 10, 20],
        [20, 10, 0, 10],
        [30, 20, 10, 0]
    ])
    node_ids = ['N01', 'N02', 'N03', 'N04']

    weights = OptimizationWeights(travel=0.4, time=0.3, energy=0.2, conflict=0.1)
    obj_func = ObjectiveFunction(weights, distance_matrix, node_ids)

    # Evaluate a sample solution
    result = obj_func.evaluate(
        paths={'AGV1': ['N01', 'N02', 'N03'], 'AGV2': ['N04', 'N03', 'N02']},
        travel_times={'AGV1': 120, 'AGV2': 100},
        wait_times={'AGV1': 15, 'AGV2': 10},
        service_times={'AGV1': 30, 'AGV2': 30},
        battery_consumption={'AGV1': 5.0, 'AGV2': 4.5},
        conflicts=[{'type': 'intersection', 'time': 5}]
    )

    print(f"Total Cost: ${result['total_cost']:.2f}")
    print(f"Components: {result['weighted_components']}")
```

### 4.2 Task Assignment Optimizer

```python
from scipy.optimize import linear_sum_assignment
import numpy as np

class TaskAssignmentOptimizer:
    """
    Optimize task-to-AGV assignments.

    Uses Hungarian algorithm for optimal assignment.
    """

    def __init__(
        self,
        agv_positions: Dict[str, str],
        agv_battery_levels: Dict[str, float],
        distance_matrix: np.ndarray,
        node_to_idx: Dict[str, int],
        battery_constraints
    ):
        self.agv_positions = agv_positions
        self.agv_battery = agv_battery_levels
        self.distance_matrix = distance_matrix
        self.node_to_idx = node_to_idx
        self.battery = battery_constraints
        self.agv_ids = list(agv_positions.keys())

    def calculate_assignment_cost(
        self,
        agv_id: str,
        task_origin: str,
        task_destination: str
    ) -> float:
        """
        Calculate cost of assigning task to AGV.

        Cost = distance(agv_position, task_origin) + distance(task_origin, task_dest)
        """
        agv_pos = self.agv_positions[agv_id]
        idx_pos = self.node_to_idx[agv_pos]
        idx_origin = self.node_to_idx[task_origin]
        idx_dest = self.node_to_idx[task_destination]

        dist_to_task = self.distance_matrix[idx_pos, idx_origin]
        dist_task = self.distance_matrix[idx_origin, idx_dest]

        total_dist = dist_to_task + dist_task

        # Check battery feasibility
        battery_level = self.agv_battery[agv_id]
        if not self.battery.check_task_feasibility(
            battery_level, total_dist, 50, 1.5
        )['feasible']:
            return float('inf')  # Infeasible assignment

        return total_dist

    def optimize_assignments(
        self,
        tasks: List[Dict]
    ) -> Dict[str, str]:
        """
        Find optimal task-to-AGV assignments.

        Args:
            tasks: List of tasks with 'task_id', 'origin', 'destination'

        Returns:
            Dict mapping task_id -> agv_id
        """
        n_agvs = len(self.agv_ids)
        n_tasks = len(tasks)

        # Build cost matrix
        cost_matrix = np.zeros((n_agvs, n_tasks))
        for i, agv_id in enumerate(self.agv_ids):
            for j, task in enumerate(tasks):
                cost_matrix[i, j] = self.calculate_assignment_cost(
                    agv_id, task['origin'], task['destination']
                )

        # Handle case where tasks > AGVs
        if n_tasks > n_agvs:
            # Pad with dummy AGVs (high cost)
            padding = np.full((n_tasks - n_agvs, n_tasks), 1e6)
            cost_matrix = np.vstack([cost_matrix, padding])

        # Solve assignment problem
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        # Build assignments
        assignments = {}
        for i, j in zip(row_ind, col_ind):
            if i < n_agvs and cost_matrix[i, j] < float('inf'):
                assignments[tasks[j]['task_id']] = self.agv_ids[i]

        return assignments


class WorkloadBalancer:
    """
    Balance workload across AGV fleet.

    Objective: Minimize variance in workload distribution.
    """

    def __init__(self, agv_ids: List[str]):
        self.agv_ids = agv_ids
        self.workloads = {agv: 0.0 for agv in agv_ids}

    def update_workload(self, agv_id: str, work_amount: float):
        """Add work to an AGV's total."""
        self.workloads[agv_id] += work_amount

    def get_least_loaded_agv(self, available_agvs: List[str] = None) -> str:
        """Get AGV with minimum current workload."""
        candidates = available_agvs or self.agv_ids
        return min(candidates, key=lambda a: self.workloads.get(a, 0))

    def get_balance_metrics(self) -> Dict:
        """Calculate workload balance metrics."""
        loads = list(self.workloads.values())
        return {
            'mean': np.mean(loads),
            'std': np.std(loads),
            'cv': np.std(loads) / np.mean(loads) if np.mean(loads) > 0 else 0,
            'max_min_ratio': max(loads) / min(loads) if min(loads) > 0 else float('inf'),
            'by_agv': dict(self.workloads)
        }

    def suggest_rebalancing(self, threshold_cv: float = 0.3) -> List[str]:
        """
        Suggest AGVs that should receive more/fewer tasks.

        Returns:
            List of recommendations
        """
        metrics = self.get_balance_metrics()
        recommendations = []

        if metrics['cv'] > threshold_cv:
            mean_load = metrics['mean']
            for agv, load in self.workloads.items():
                if load > mean_load * 1.3:
                    recommendations.append(f"{agv}: Overloaded ({load:.1f} vs {mean_load:.1f} avg)")
                elif load < mean_load * 0.7:
                    recommendations.append(f"{agv}: Underutilized ({load:.1f} vs {mean_load:.1f} avg)")

        return recommendations
```

---

## 5. Optimization Scenarios

### 5.1 Minimize Total Travel Distance

```
min Z_distance = sum_{k in K} sum_{(i,j) in path_k} d_ij
```

**Use case:** Energy conservation, reduced wear

**Weight configuration:**
```python
weights = OptimizationWeights(travel=0.7, time=0.2, energy=0.1, conflict=0.0)
```

### 5.2 Minimize Conflicts

```
min Z_conflict = sum_{t} sum_{(k1,k2)} conflict(k1, k2, t)
```

**Use case:** Safety-critical environments, legacy aisles

**Weight configuration:**
```python
weights = OptimizationWeights(travel=0.2, time=0.2, energy=0.1, conflict=0.5)
```

### 5.3 Maximize Throughput

Equivalent to minimizing task completion time:
```
min Z_time = max_{m in M} t_complete_m - min_{m in M} t_release_m
```

**Use case:** High-volume operations, peak periods

**Weight configuration:**
```python
weights = OptimizationWeights(travel=0.1, time=0.6, energy=0.1, conflict=0.2)
```

### 5.4 Balance Workload

```
min Z_balance = variance({workload_k : k in K})
```

**Use case:** Even battery depletion, maintenance scheduling

```python
def workload_variance_objective(workloads: Dict[str, float]) -> float:
    """Calculate workload variance for balancing objective."""
    loads = list(workloads.values())
    mean_load = np.mean(loads)
    variance = np.sum((np.array(loads) - mean_load) ** 2) / len(loads)
    return variance
```

---

## 6. Constraint Handling in Optimization

### 6.1 Penalty Method

Convert constraints to penalty terms in objective:

```
Z_penalized = Z + sum_i lambda_i * max(0, g_i(x))^2
```

Where `g_i(x) <= 0` are constraint violations.

```python
def add_constraint_penalties(
    base_cost: float,
    battery_violations: List[float],
    capacity_violations: List[int],
    penalty_battery: float = 100.0,
    penalty_capacity: float = 50.0
) -> float:
    """
    Add penalty terms for constraint violations.

    Args:
        base_cost: Original objective value
        battery_violations: List of battery threshold violations (negative = violation)
        capacity_violations: List of over-capacity counts per edge
        penalty_battery: Penalty per % below threshold
        penalty_capacity: Penalty per AGV over capacity

    Returns:
        Penalized objective value
    """
    battery_penalty = sum(max(0, -v)**2 for v in battery_violations) * penalty_battery
    capacity_penalty = sum(max(0, v)**2 for v in capacity_violations) * penalty_capacity

    return base_cost + battery_penalty + capacity_penalty
```

---

## 7. Excel Optimization Template

### Objective Function Calculation (Excel)

```
| A | B | C | D | E | F |
|---|---|---|---|---|---|
| AGV | Travel_Dist | Travel_Time | Wait_Time | Battery_Used | Conflicts |
| AGV1 | 150 | 120 | 15 | 5.2 | 2 |
| AGV2 | 180 | 150 | 8 | 6.1 | 1 |
| ... | ... | ... | ... | ... | ... |

Weighted Objective (G2):
=($B2*$J$2*$J$6) + (($C2+$D2)*$J$3*$J$6) + ($E2*$J$4*$J$6) + ($F2*$J$5*$J$6)

Where:
J2 = Cost per meter ($0.01)
J3 = Cost per second ($0.005)
J4 = Cost per battery % ($0.10)
J5 = Cost per conflict ($5.00)
J6-J9 = Weights (alpha_1 to alpha_4)

Total Objective (J10):
=SUM(G2:G10)
```

### Weight Sensitivity Analysis (Excel)

```
| Weight Set | alpha_1 | alpha_2 | alpha_3 | alpha_4 | Total Cost |
|------------|---------|---------|---------|---------|------------|
| Distance Focus | 0.7 | 0.2 | 0.1 | 0.0 | =CALC... |
| Time Focus | 0.1 | 0.6 | 0.1 | 0.2 | =CALC... |
| Balanced | 0.25 | 0.25 | 0.25 | 0.25 | =CALC... |
| Safety Focus | 0.2 | 0.2 | 0.1 | 0.5 | =CALC... |
```

---

## 8. Summary

### Key Equations Reference

| Objective | Formula |
|-----------|---------|
| Layout A Original | f = min sum_k c_k(z^e_ku - z^s_kd) |
| Travel Cost | Z_travel = sum_k sum_(i,j) d_ij * x_ijk |
| Time Cost | Z_time = sum_k (T_travel + T_wait + T_service) |
| Energy Cost | Z_energy = sum_k (B_start - B_end) |
| Conflict Cost | Z_conflict = N_conflicts * c_conflict |
| Combined | Z = alpha_1*Z_travel + alpha_2*Z_time + alpha_3*Z_energy + alpha_4*Z_conflict |

### Recommended Weight Configurations

| Scenario | alpha_1 | alpha_2 | alpha_3 | alpha_4 |
|----------|---------|---------|---------|---------|
| Standard Operations | 0.35 | 0.30 | 0.20 | 0.15 |
| Energy Conservation | 0.25 | 0.20 | 0.45 | 0.10 |
| Maximum Throughput | 0.15 | 0.55 | 0.10 | 0.20 |
| Safety Priority | 0.20 | 0.20 | 0.10 | 0.50 |
| Legacy Retrofit | 0.30 | 0.25 | 0.15 | 0.30 |
