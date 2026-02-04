# Constraint Equations
## Legacy Warehouse Limitations for AGV Retrofit

---

## 1. Physical Space Constraints

### 1.1 Aisle Width Constraint

**Minimum Aisle Width for AGV Passage:**

```
W_aisle >= W_agv + 2 * d_safety + W_clearance
```

Where:
- `W_aisle` = Aisle width (meters)
- `W_agv` = AGV width (meters)
- `d_safety` = Safety buffer on each side (meters)
- `W_clearance` = Additional clearance for sensor operation (meters)

**For Bidirectional Traffic:**
```
W_aisle >= 2 * W_agv + 3 * d_safety
```

**Example Calculation:**
- AGV width: 0.8m
- Safety buffer: 0.3m
- Sensor clearance: 0.2m
- Minimum aisle (unidirectional): 0.8 + 2(0.3) + 0.2 = 1.6m
- Minimum aisle (bidirectional): 2(0.8) + 3(0.3) = 2.5m

**Python Implementation:**
```python
def check_aisle_width_constraint(
    aisle_width: float,
    agv_width: float,
    safety_buffer: float,
    sensor_clearance: float = 0.2,
    bidirectional: bool = False
) -> Dict:
    """
    Check if aisle width meets AGV requirements.

    Returns:
        Dictionary with constraint status and details
    """
    if bidirectional:
        min_width = 2 * agv_width + 3 * safety_buffer
        traffic_type = "bidirectional"
    else:
        min_width = agv_width + 2 * safety_buffer + sensor_clearance
        traffic_type = "unidirectional"

    satisfied = aisle_width >= min_width
    margin = aisle_width - min_width

    return {
        'satisfied': satisfied,
        'aisle_width': aisle_width,
        'minimum_required': min_width,
        'margin': margin,
        'traffic_type': traffic_type,
        'recommendation': f"{'OK' if satisfied else f'Increase aisle width by {-margin:.2f}m'}"
    }
```

### 1.2 Turning Radius Constraint

**Minimum Turning Space:**
```
R_turn >= L_agv / (2 * sin(theta_max/2))
```

Where:
- `R_turn` = Minimum turning radius
- `L_agv` = AGV length
- `theta_max` = Maximum steering angle

**Intersection Size Requirement:**
```
A_intersection >= (2 * R_turn + W_agv)^2
```

For 90-degree turns at intersections.

---

## 2. Weight and Load Constraints

### 2.1 Floor Load Capacity

**Static Load Constraint:**
```
P_static = (M_agv + M_payload) * g / A_contact <= P_floor_max
```

Where:
- `P_static` = Static pressure on floor (N/m^2 or Pa)
- `M_agv` = AGV mass (kg)
- `M_payload` = Maximum payload mass (kg)
- `g` = Gravitational acceleration (9.81 m/s^2)
- `A_contact` = Wheel contact area (m^2)
- `P_floor_max` = Maximum floor load capacity (Pa)

**Dynamic Load Factor:**
```
P_dynamic = P_static * (1 + a/g)
```

Accounts for acceleration forces.

**Zone-Based Capacity:**
```
sum_{k in Z} (M_agv_k + M_payload_k) <= W_zone_max
```

Total weight of all AGVs in a zone must not exceed zone capacity.

**Python Implementation:**
```python
def check_floor_load_constraint(
    agv_mass: float,
    payload_mass: float,
    wheel_contact_area: float,
    floor_capacity: float,
    acceleration: float = 0.5,
    num_wheels: int = 4
) -> Dict:
    """
    Check floor load capacity constraints.

    Args:
        agv_mass: AGV mass in kg
        payload_mass: Maximum payload in kg
        wheel_contact_area: Contact area per wheel in m^2
        floor_capacity: Maximum floor load in Pa (N/m^2)
        acceleration: Maximum AGV acceleration in m/s^2
        num_wheels: Number of load-bearing wheels

    Returns:
        Constraint check results
    """
    g = 9.81
    total_mass = agv_mass + payload_mass
    total_contact_area = wheel_contact_area * num_wheels

    # Static pressure
    static_pressure = (total_mass * g) / total_contact_area

    # Dynamic pressure (with acceleration)
    dynamic_factor = 1 + acceleration / g
    dynamic_pressure = static_pressure * dynamic_factor

    return {
        'satisfied': dynamic_pressure <= floor_capacity,
        'static_pressure_pa': static_pressure,
        'dynamic_pressure_pa': dynamic_pressure,
        'floor_capacity_pa': floor_capacity,
        'utilization_pct': (dynamic_pressure / floor_capacity) * 100,
        'safety_margin_pct': ((floor_capacity - dynamic_pressure) / floor_capacity) * 100
    }


def check_zone_weight_constraint(
    agv_weights: List[float],
    payload_weights: List[float],
    zone_capacity: float
) -> Dict:
    """
    Check total weight constraint for a zone.

    Args:
        agv_weights: List of AGV masses in the zone
        payload_weights: List of payload masses in the zone
        zone_capacity: Maximum total weight for zone in kg

    Returns:
        Constraint check results
    """
    total_weight = sum(agv_weights) + sum(payload_weights)

    return {
        'satisfied': total_weight <= zone_capacity,
        'total_weight_kg': total_weight,
        'zone_capacity_kg': zone_capacity,
        'num_agvs': len(agv_weights),
        'utilization_pct': (total_weight / zone_capacity) * 100,
        'remaining_capacity_kg': zone_capacity - total_weight
    }
```

---

## 3. Traffic and Congestion Constraints

### 3.1 Maximum AGVs per Aisle

**Congestion Prevention:**
```
n_agv(aisle_i) <= C_aisle_i  for all i in Aisles
```

Where:
- `n_agv(aisle_i)` = Number of AGVs currently in aisle i
- `C_aisle_i` = Capacity of aisle i

**Capacity Calculation:**
```
C_aisle = floor(L_aisle / (L_agv + d_following))
```

Where:
- `L_aisle` = Length of aisle
- `L_agv` = Length of AGV
- `d_following` = Minimum following distance

**Python Implementation:**
```python
def calculate_aisle_capacity(
    aisle_length: float,
    agv_length: float,
    following_distance: float,
    bidirectional: bool = False
) -> int:
    """
    Calculate maximum AGVs allowed in an aisle.

    Args:
        aisle_length: Length of aisle in meters
        agv_length: Length of AGV in meters
        following_distance: Minimum safe following distance in meters
        bidirectional: Whether aisle supports two-way traffic

    Returns:
        Maximum number of AGVs
    """
    space_per_agv = agv_length + following_distance

    if bidirectional:
        # Each direction gets half the conceptual capacity, but physical is same
        capacity = int(aisle_length / space_per_agv)
        # For bidirectional, we want to limit to prevent head-on conflicts
        return max(1, capacity // 2)
    else:
        return max(1, int(aisle_length / space_per_agv))


class AisleCapacityConstraint:
    """Monitor and enforce aisle capacity constraints."""

    def __init__(self, aisle_capacities: Dict[str, int]):
        """
        Initialize with aisle capacity definitions.

        Args:
            aisle_capacities: Dict mapping aisle_id -> max_capacity
        """
        self.capacities = aisle_capacities
        self.current_counts = {aisle: 0 for aisle in aisle_capacities}

    def can_enter(self, aisle_id: str) -> bool:
        """Check if an AGV can enter the aisle."""
        if aisle_id not in self.capacities:
            return True
        return self.current_counts[aisle_id] < self.capacities[aisle_id]

    def enter_aisle(self, aisle_id: str) -> bool:
        """Record AGV entering aisle. Returns success status."""
        if not self.can_enter(aisle_id):
            return False
        self.current_counts[aisle_id] += 1
        return True

    def exit_aisle(self, aisle_id: str):
        """Record AGV exiting aisle."""
        if aisle_id in self.current_counts:
            self.current_counts[aisle_id] = max(0, self.current_counts[aisle_id] - 1)

    def get_utilization(self) -> Dict[str, float]:
        """Get current utilization of all aisles."""
        return {
            aisle: self.current_counts[aisle] / self.capacities[aisle]
            for aisle in self.capacities
        }
```

### 3.2 Intersection Capacity Constraint

**Single-Occupancy Intersection:**
```
n_agv(intersection_j) <= 1  for all j in Intersections
```

**Time-Based Reservation:**
```
reservation(agv_k, intersection_j, t) =>
    no other reservation(agv_m, intersection_j, t')
    where |t - t'| < T_crossing
```

---

## 4. Battery Constraints

Based on Layout A's battery model: `bl_k <= lambda^r_ku <= bh_k`

### 4.1 Battery State of Charge

**Discharge Model:**
```
B(t+dt) = B(t) - r(state) * dt
```

Where r(state) depends on AGV activity:
- Idle: `r_idle`
- Moving empty: `r_move`
- Moving loaded: `r_load`

**Continuous Constraint:**
```
B(t) >= B_low  for all t
```

### 4.2 Range Constraint

**Maximum Distance Before Recharge:**
```
D_max = (B_current - B_low) / (r_move / v_cruise)
```

**Task Feasibility Check:**
```
d_task + d_to_charger <= D_max
```

An AGV should only accept a task if it can complete the task AND reach a charging station.

**Python Implementation:**
```python
class BatteryConstraints:
    """
    Battery depletion model and constraints.

    Based on: bl_k <= lambda^r_ku <= bh_k
    """

    def __init__(
        self,
        capacity: float = 100.0,  # Total capacity (%)
        low_threshold: float = 20.0,  # bl_k
        high_threshold: float = 95.0,  # bh_k
        idle_rate: float = 0.5,  # %/hr
        move_rate: float = 2.0,  # %/hr
        load_rate: float = 3.5,  # %/hr
        charge_rate: float = 10.0  # %/hr
    ):
        self.capacity = capacity
        self.bl_k = low_threshold  # Battery low threshold
        self.bh_k = high_threshold  # Battery high threshold
        self.rates = {
            'idle': idle_rate,
            'moving': move_rate,
            'loaded': load_rate,
            'charging': -charge_rate  # Negative = gaining charge
        }

    def update_battery(
        self,
        current_level: float,
        state: str,
        duration_hours: float
    ) -> float:
        """
        Update battery level based on activity.

        Args:
            current_level: Current battery percentage
            state: 'idle', 'moving', 'loaded', or 'charging'
            duration_hours: Time in state (hours)

        Returns:
            New battery level (bounded by 0 and bh_k)
        """
        rate = self.rates.get(state, self.rates['idle'])
        new_level = current_level - rate * duration_hours

        # Apply bounds: bl_k <= lambda^r_ku <= bh_k
        return max(0, min(self.bh_k, new_level))

    def check_task_feasibility(
        self,
        current_level: float,
        task_distance: float,
        distance_to_charger: float,
        speed: float
    ) -> Dict:
        """
        Check if AGV has enough battery for task + reaching charger.

        Constraint: d_task + d_to_charger <= D_max
        """
        # Calculate time requirements
        task_time_hours = task_distance / (speed * 3600)
        charger_time_hours = distance_to_charger / (speed * 3600)

        # Battery consumed
        task_consumption = self.rates['loaded'] * task_time_hours
        charger_consumption = self.rates['moving'] * charger_time_hours
        total_consumption = task_consumption + charger_consumption

        # Available battery (above low threshold)
        available = current_level - self.bl_k

        feasible = total_consumption <= available

        return {
            'feasible': feasible,
            'current_level': current_level,
            'available_charge': available,
            'required_charge': total_consumption,
            'remaining_after': available - total_consumption if feasible else None,
            'recommendation': 'PROCEED' if feasible else 'CHARGE_FIRST'
        }

    def estimate_range(
        self,
        current_level: float,
        speed: float,
        loaded: bool = False
    ) -> float:
        """
        Estimate maximum distance before reaching low threshold.

        D_max = (B_current - B_low) / (r / v)
        """
        available = current_level - self.bl_k
        rate = self.rates['loaded'] if loaded else self.rates['moving']

        # Convert rate from %/hr to %/m
        rate_per_meter = rate / (speed * 3600)

        if rate_per_meter <= 0:
            return float('inf')

        return available / rate_per_meter

    def time_to_charge(self, current_level: float, target_level: float = None) -> float:
        """
        Calculate time needed to charge to target level.

        Args:
            current_level: Current battery percentage
            target_level: Target level (default: bh_k)

        Returns:
            Charging time in hours
        """
        if target_level is None:
            target_level = self.bh_k

        charge_needed = target_level - current_level
        if charge_needed <= 0:
            return 0

        return charge_needed / abs(self.rates['charging'])

    def should_charge(self, current_level: float, next_task_distance: float = 0) -> bool:
        """
        Determine if AGV should go to charging station.

        Decision based on:
        1. Below low threshold -> must charge
        2. Cannot complete next task + reach charger -> should charge
        """
        if current_level <= self.bl_k:
            return True

        # If next task known, check feasibility
        if next_task_distance > 0:
            # Assume worst case: task + 50m to charger
            feasibility = self.check_task_feasibility(
                current_level, next_task_distance, 50, 1.5
            )
            return not feasibility['feasible']

        return False
```

---

## 5. Operational Constraints

### 5.1 Task Timing Constraints

**Task Completion Deadline:**
```
t_complete(task_i) <= t_deadline(task_i)
```

**Task Sequence Constraint:**
```
t_start(task_j) >= t_complete(task_i)  if task_i precedes task_j
```

### 5.2 Zone Restrictions

**No-Go Zones:**
```
position(agv_k, t) not in NoGoZones  for all k, t
```

**Time-Based Restrictions:**
```
position(agv_k, t) not in RestrictedZone(t)
    if t in restricted_hours
```

**Python Implementation:**
```python
from dataclasses import dataclass
from typing import Set, Tuple, Optional

@dataclass
class Zone:
    zone_id: str
    boundary: List[Tuple[float, float]]  # Polygon vertices
    zone_type: str  # 'normal', 'no_go', 'restricted'
    restricted_hours: Optional[Tuple[float, float]] = None  # (start, end) hours

class ZoneConstraints:
    """Manage zone-based movement constraints."""

    def __init__(self, zones: List[Zone]):
        self.zones = {z.zone_id: z for z in zones}
        self.no_go_zones = {z.zone_id for z in zones if z.zone_type == 'no_go'}
        self.restricted_zones = {z.zone_id: z for z in zones
                                 if z.zone_type == 'restricted'}

    def point_in_polygon(self, point: Tuple[float, float],
                         polygon: List[Tuple[float, float]]) -> bool:
        """Check if point is inside polygon (ray casting algorithm)."""
        x, y = point
        n = len(polygon)
        inside = False

        j = n - 1
        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[j]

            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i

        return inside

    def get_zone_at_position(self, position: Tuple[float, float]) -> Optional[str]:
        """Find which zone contains the given position."""
        for zone_id, zone in self.zones.items():
            if self.point_in_polygon(position, zone.boundary):
                return zone_id
        return None

    def can_access(self, position: Tuple[float, float], current_hour: float) -> Dict:
        """
        Check if AGV can access the given position at current time.

        Returns:
            Dict with access status and reason
        """
        zone_id = self.get_zone_at_position(position)

        if zone_id is None:
            return {'allowed': True, 'reason': 'Outside defined zones'}

        # Check no-go zones
        if zone_id in self.no_go_zones:
            return {
                'allowed': False,
                'reason': f'No-go zone: {zone_id}',
                'zone_id': zone_id
            }

        # Check time-restricted zones
        if zone_id in self.restricted_zones:
            zone = self.restricted_zones[zone_id]
            if zone.restricted_hours:
                start, end = zone.restricted_hours
                if start <= current_hour <= end:
                    return {
                        'allowed': False,
                        'reason': f'Time-restricted zone {zone_id} ({start:.1f}-{end:.1f}h)',
                        'zone_id': zone_id,
                        'restriction_ends': end
                    }

        return {'allowed': True, 'zone_id': zone_id}

    def find_alternative_path(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        current_hour: float,
        pathfinder
    ) -> Optional[List]:
        """
        Find path avoiding restricted zones.

        Args:
            start: Starting position
            end: Ending position
            current_hour: Current time for time-based restrictions
            pathfinder: Pathfinding algorithm instance

        Returns:
            Valid path or None if no path exists
        """
        # Get currently blocked zones
        blocked = set(self.no_go_zones)
        for zone_id, zone in self.restricted_zones.items():
            if zone.restricted_hours:
                start_h, end_h = zone.restricted_hours
                if start_h <= current_hour <= end_h:
                    blocked.add(zone_id)

        # Use pathfinder with blocked zones
        return pathfinder.find_path(start, end, blocked_zones=blocked)
```

---

## 6. Summary Constraint Matrix

| Constraint Type | Mathematical Form | Default Limit | Priority |
|-----------------|-------------------|---------------|----------|
| Aisle Width | W >= W_agv + 2*d_safety | 2.5m | Critical |
| Floor Load | P <= P_max | 5000 Pa | Critical |
| AGVs per Aisle | n <= C_aisle | 2 AGVs | High |
| Battery Level | B >= bl_k | 20% | Critical |
| Task Deadline | t_complete <= t_deadline | Task-specific | Medium |
| Zone Access | pos not in NoGo | Zone-specific | Critical |
| Intersection | n <= 1 | 1 AGV | High |
| Following Distance | d >= d_min | 2m | High |
| Turning Radius | R >= R_min | 1.5m | Critical |
| Weight per Zone | W_total <= W_zone | 5000 kg | High |

---

## 7. Excel Constraint Validation

### Aisle Width Check
```excel
=IF(B2 >= (C2 + 2*D2 + E2), "PASS", "FAIL: Need "&(C2+2*D2+E2-B2)&"m more")
```

### Floor Load Check
```excel
=IF(((B2+C2)*9.81)/D2 <= E2, "PASS", "FAIL: Overweight by "&(((B2+C2)*9.81)/D2 - E2)&" Pa")
```

### Battery Range Check
```excel
=IF((B2-C2)/(D2/E2) >= F2+G2, "FEASIBLE", "CHARGE REQUIRED")
```

Where:
- B2 = Current battery %
- C2 = Low threshold %
- D2 = Discharge rate %/hr
- E2 = Speed m/s (converted to m/hr)
- F2 = Task distance
- G2 = Distance to charger
