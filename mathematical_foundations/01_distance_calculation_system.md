# Grid-Based Distance Calculation System
## Mathematical Foundations for Legacy Warehouse Robotics Retrofit

---

## 1. Core Distance Formulas

### 1.1 Manhattan Distance (Grid-Based Movement)

For AGVs constrained to orthogonal movement along aisles:

```
d_manhattan(A, B) = |x_A - x_B| + |y_A - y_B|
```

**Implementation (Python):**
```python
def manhattan_distance(node_a: tuple, node_b: tuple) -> float:
    """
    Calculate Manhattan distance between two nodes.

    Args:
        node_a: (x, y) coordinates of starting node
        node_b: (x, y) coordinates of ending node

    Returns:
        Manhattan distance in grid units
    """
    return abs(node_a[0] - node_b[0]) + abs(node_a[1] - node_b[1])
```

### 1.2 Euclidean Distance (Open Areas)

For AGVs in open staging areas or intersections where diagonal movement is possible:

```
d_euclidean(A, B) = sqrt((x_A - x_B)^2 + (y_A - y_B)^2)
```

**Implementation (Python):**
```python
import math

def euclidean_distance(node_a: tuple, node_b: tuple) -> float:
    """
    Calculate Euclidean distance between two nodes.

    Args:
        node_a: (x, y) coordinates of starting node
        node_b: (x, y) coordinates of ending node

    Returns:
        Euclidean distance in grid units
    """
    return math.sqrt((node_a[0] - node_b[0])**2 + (node_a[1] - node_b[1])**2)
```

### 1.3 Weighted Distance (Congestion-Adjusted)

Accounts for variable traversal costs due to congestion, floor conditions, or obstacles:

```
d_weighted(A, B) = sum_{e in path(A,B)} w_e * l_e
```

Where:
- `w_e` = weight factor for edge e (congestion multiplier)
- `l_e` = length of edge e

**Congestion Weight Formula:**
```
w_e = 1 + alpha * (n_agv_e / C_e)
```

Where:
- `alpha` = congestion sensitivity parameter (typical: 0.5 - 2.0)
- `n_agv_e` = current number of AGVs on edge e
- `C_e` = capacity of edge e (max AGVs before severe congestion)

**Implementation (Python):**
```python
def weighted_distance(path_edges: list, edge_weights: dict, edge_lengths: dict) -> float:
    """
    Calculate weighted distance along a path.

    Args:
        path_edges: List of edge identifiers in the path
        edge_weights: Dictionary mapping edge_id -> weight factor
        edge_lengths: Dictionary mapping edge_id -> physical length

    Returns:
        Total weighted distance
    """
    total = 0.0
    for edge in path_edges:
        weight = edge_weights.get(edge, 1.0)
        length = edge_lengths.get(edge, 0.0)
        total += weight * length
    return total


def calculate_congestion_weight(n_agv: int, capacity: int, alpha: float = 1.0) -> float:
    """
    Calculate congestion weight for an edge.

    Args:
        n_agv: Current number of AGVs on the edge
        capacity: Maximum capacity of the edge
        alpha: Congestion sensitivity parameter

    Returns:
        Congestion weight multiplier (>= 1.0)
    """
    if capacity <= 0:
        return float('inf')
    return 1.0 + alpha * (n_agv / capacity)
```

---

## 2. Travel Time Formula

### 2.1 Complete Travel Time Model

```
T_travel(A, B) = T_base + T_turns + T_acceleration + T_deceleration + T_wait
```

**Expanded Form:**
```
T_travel = d(A,B)/v_cruise + n_turns * t_turn + t_accel + t_decel + T_queue
```

Where:
- `d(A,B)` = distance between nodes A and B
- `v_cruise` = cruising velocity (m/s)
- `n_turns` = number of turns in the path
- `t_turn` = time penalty per turn (seconds)
- `t_accel` = acceleration time to reach cruise speed
- `t_decel` = deceleration time from cruise speed
- `T_queue` = waiting time at congested zones

### 2.2 Acceleration/Deceleration Time

Assuming constant acceleration:
```
t_accel = v_cruise / a
t_decel = v_cruise / a
```

Distance covered during acceleration:
```
d_accel = 0.5 * a * t_accel^2 = v_cruise^2 / (2 * a)
```

### 2.3 Adjusted Cruise Distance

If total distance is sufficient for full acceleration:
```
d_cruise = d_total - 2 * d_accel    (if d_total >= 2 * d_accel)
```

For short distances where cruise speed cannot be reached:
```
v_max_achievable = sqrt(a * d_total)    (if d_total < 2 * d_accel)
```

**Implementation (Python):**
```python
import math

def calculate_travel_time(
    distance: float,
    cruise_speed: float,
    acceleration: float,
    n_turns: int,
    turn_time: float,
    queue_wait: float = 0.0
) -> dict:
    """
    Calculate total travel time with all components.

    Args:
        distance: Total path distance (meters)
        cruise_speed: Nominal cruising speed (m/s)
        acceleration: Acceleration/deceleration rate (m/s^2)
        n_turns: Number of turns in path
        turn_time: Time penalty per turn (seconds)
        queue_wait: Expected queue waiting time (seconds)

    Returns:
        Dictionary with time breakdown
    """
    # Acceleration distance
    d_accel = (cruise_speed ** 2) / (2 * acceleration)

    if distance >= 2 * d_accel:
        # Full acceleration profile achieved
        t_accel = cruise_speed / acceleration
        t_decel = cruise_speed / acceleration
        d_cruise = distance - 2 * d_accel
        t_cruise = d_cruise / cruise_speed
        actual_max_speed = cruise_speed
    else:
        # Short distance - cannot reach cruise speed
        actual_max_speed = math.sqrt(acceleration * distance)
        t_accel = actual_max_speed / acceleration
        t_decel = t_accel
        t_cruise = 0.0

    t_turns = n_turns * turn_time
    t_total = t_accel + t_cruise + t_decel + t_turns + queue_wait

    return {
        'total_time': t_total,
        'acceleration_time': t_accel,
        'cruise_time': t_cruise if distance >= 2 * d_accel else 0.0,
        'deceleration_time': t_decel,
        'turn_time': t_turns,
        'queue_time': queue_wait,
        'actual_max_speed': actual_max_speed,
        'distance': distance
    }
```

---

## 3. Zone-Based Distance Modifiers

### 3.1 Zone Categories

| Zone Type | Weight Factor | Description |
|-----------|---------------|-------------|
| Open Floor | 1.0 | Standard traversal |
| Narrow Aisle | 1.3 | Reduced speed required |
| High-Traffic | 1.5 - 2.0 | Dynamic congestion |
| Charging Area | 0.8 | Priority access |
| Loading Dock | 1.2 | Pedestrian hazard zones |
| Cold Storage | 1.4 | Environmental constraints |

### 3.2 Time-of-Day Multiplier

```
w_time(t) = 1 + beta * sin^2(pi * (t - t_peak) / T_period)
```

Where:
- `beta` = peak-hour intensity factor (typical: 0.3 - 0.8)
- `t_peak` = peak activity time
- `T_period` = shift duration

**Implementation (Python):**
```python
import math

def time_of_day_multiplier(current_time: float, peak_time: float,
                            period: float, beta: float = 0.5) -> float:
    """
    Calculate time-of-day congestion multiplier.

    Args:
        current_time: Current time (hours since shift start)
        peak_time: Peak activity time (hours since shift start)
        period: Full period duration (hours)
        beta: Peak intensity factor

    Returns:
        Multiplier for travel time (>= 1.0)
    """
    phase = math.pi * (current_time - peak_time) / period
    return 1.0 + beta * (math.sin(phase) ** 2)
```

---

## 4. Path Selection Algorithm

### 4.1 Optimal Path Cost Function

Based on Layout A's transportation cost formulation:

```
f = min sum_{k in K} c_k * (z^e_ku - z^s_kd)
```

Adapted for legacy retrofit:

```
C_path(P) = sum_{e in P} [d_e * w_e + T_conflict(e) * lambda]
```

Where:
- `P` = path from origin to destination
- `d_e` = distance of edge e
- `w_e` = weight of edge e
- `T_conflict(e)` = expected conflict delay on edge e
- `lambda` = conflict penalty weight

### 4.2 Multi-Objective Path Selection

```
minimize: alpha_1 * D_total + alpha_2 * T_total + alpha_3 * E_battery
subject to:
    battery_level >= b_min at all nodes
    aisle_capacity not exceeded
    priority_tasks have precedence
```

---

## 5. Excel Formula Templates

### 5.1 Manhattan Distance (Excel)
```excel
=ABS(B2-D2)+ABS(C2-E2)
```
Where B2,C2 = origin (x,y) and D2,E2 = destination (x,y)

### 5.2 Euclidean Distance (Excel)
```excel
=SQRT((B2-D2)^2+(C2-E2)^2)
```

### 5.3 Weighted Distance (Excel)
```excel
=F2*G2
```
Where F2 = weight factor, G2 = base distance

### 5.4 Travel Time (Excel)
```excel
=G2/H2+I2*J2+K2
```
Where:
- G2 = distance
- H2 = speed
- I2 = number of turns
- J2 = turn time
- K2 = queue time
