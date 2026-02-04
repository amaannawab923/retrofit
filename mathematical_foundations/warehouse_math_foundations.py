"""
Mathematical Foundations for Legacy Warehouse Robotics Retrofit Simulation

Based on Layout A Research:
- Transportation cost: f = min sum_{k in K} c_k (z^e_ku - z^s_kd)
- Multigraph: G = (N, E)
- Battery constraints: bl_k <= lambda^r_ku <= bh_k

This module provides complete mathematical implementations for:
1. Distance calculations (Manhattan, Euclidean, Weighted)
2. Travel time modeling
3. Distance matrix generation
4. Simulation parameters
5. Performance metrics
6. Constraint checking
7. Optimization objective functions

Author: Data Science Team
Version: 1.0.0
"""

import math
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import json
from datetime import datetime


# =============================================================================
# SECTION 1: DISTANCE CALCULATION SYSTEM
# =============================================================================

class DistanceCalculator:
    """
    Grid-based distance calculation for warehouse AGV navigation.

    Supports:
    - Manhattan distance (grid-constrained movement)
    - Euclidean distance (open areas)
    - Weighted distance (congestion-adjusted)
    """

    @staticmethod
    def manhattan(node_a: Tuple[float, float], node_b: Tuple[float, float]) -> float:
        """
        Calculate Manhattan distance: d(A,B) = |x_A - x_B| + |y_A - y_B|

        Args:
            node_a: (x, y) coordinates of starting node
            node_b: (x, y) coordinates of ending node

        Returns:
            Manhattan distance in grid units (meters)
        """
        return abs(node_a[0] - node_b[0]) + abs(node_a[1] - node_b[1])

    @staticmethod
    def euclidean(node_a: Tuple[float, float], node_b: Tuple[float, float]) -> float:
        """
        Calculate Euclidean distance: d(A,B) = sqrt((x_A-x_B)^2 + (y_A-y_B)^2)

        Args:
            node_a: (x, y) coordinates of starting node
            node_b: (x, y) coordinates of ending node

        Returns:
            Euclidean distance in meters
        """
        return math.sqrt((node_a[0] - node_b[0])**2 + (node_a[1] - node_b[1])**2)

    @staticmethod
    def weighted(
        path_edges: List[str],
        edge_weights: Dict[str, float],
        edge_lengths: Dict[str, float]
    ) -> float:
        """
        Calculate weighted distance: d_weighted = sum_{e in path} w_e * l_e

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

    @staticmethod
    def congestion_weight(n_agv: int, capacity: int, alpha: float = 1.0) -> float:
        """
        Calculate congestion weight: w_e = 1 + alpha * (n_agv / C_e)

        Args:
            n_agv: Current number of AGVs on the edge
            capacity: Maximum capacity of the edge
            alpha: Congestion sensitivity parameter (0.5-2.0 typical)

        Returns:
            Congestion weight multiplier (>= 1.0)
        """
        if capacity <= 0:
            return float('inf')
        return 1.0 + alpha * (n_agv / capacity)


class TravelTimeCalculator:
    """
    Complete travel time model with acceleration, turns, and waiting.

    Formula: T_travel = d/v + n_turns*t_turn + t_accel + t_decel + T_queue
    """

    def __init__(
        self,
        cruise_speed: float = 1.5,
        acceleration: float = 0.5,
        turn_time: float = 2.0
    ):
        """
        Initialize travel time calculator.

        Args:
            cruise_speed: Nominal cruising speed (m/s)
            acceleration: Acceleration/deceleration rate (m/s^2)
            turn_time: Time penalty per 90-degree turn (seconds)
        """
        self.v_cruise = cruise_speed
        self.acceleration = acceleration
        self.t_turn = turn_time

    def calculate(
        self,
        distance: float,
        n_turns: int = 0,
        queue_wait: float = 0.0
    ) -> Dict:
        """
        Calculate total travel time with all components.

        Args:
            distance: Total path distance (meters)
            n_turns: Number of turns in path
            queue_wait: Expected queue waiting time (seconds)

        Returns:
            Dictionary with time breakdown
        """
        # Acceleration distance: d_accel = v^2 / (2*a)
        d_accel = (self.v_cruise ** 2) / (2 * self.acceleration)

        if distance >= 2 * d_accel:
            # Full acceleration profile achieved
            t_accel = self.v_cruise / self.acceleration
            t_decel = self.v_cruise / self.acceleration
            d_cruise = distance - 2 * d_accel
            t_cruise = d_cruise / self.v_cruise
            actual_max_speed = self.v_cruise
        else:
            # Short distance - cannot reach cruise speed
            # v_max = sqrt(a * d)
            actual_max_speed = math.sqrt(self.acceleration * distance)
            t_accel = actual_max_speed / self.acceleration
            t_decel = t_accel
            t_cruise = 0.0

        t_turns = n_turns * self.t_turn
        t_total = t_accel + t_cruise + t_decel + t_turns + queue_wait

        return {
            'total_time': t_total,
            'acceleration_time': t_accel,
            'cruise_time': t_cruise,
            'deceleration_time': t_decel,
            'turn_time': t_turns,
            'queue_time': queue_wait,
            'actual_max_speed': actual_max_speed,
            'distance': distance
        }

    def time_of_day_multiplier(
        self,
        current_time: float,
        peak_time: float,
        period: float,
        beta: float = 0.5
    ) -> float:
        """
        Calculate time-of-day congestion multiplier.

        Formula: w_time(t) = 1 + beta * sin^2(pi*(t-t_peak)/T)

        Args:
            current_time: Current time (hours since shift start)
            peak_time: Peak activity time (hours since shift start)
            period: Full period duration (hours)
            beta: Peak intensity factor (0.3-0.8 typical)

        Returns:
            Multiplier for travel time (>= 1.0)
        """
        phase = math.pi * (current_time - peak_time) / period
        return 1.0 + beta * (math.sin(phase) ** 2)


# =============================================================================
# SECTION 2: DISTANCE MATRIX TEMPLATE
# =============================================================================

class WarehouseDistanceMatrix:
    """
    Generate and manage distance matrices for warehouse layout.

    Supports:
    - Node-to-node distance matrices
    - Zone-to-zone aggregated distances
    - Multiple distance metrics
    """

    def __init__(self, nodes: Dict[str, Tuple[float, float, str]]):
        """
        Initialize with node definitions.

        Args:
            nodes: Dictionary mapping node_id -> (x, y, zone_type)
        """
        self.nodes = nodes
        self.node_ids = list(nodes.keys())
        self.n_nodes = len(self.node_ids)
        self.calculator = DistanceCalculator()

        self.manhattan_matrix = None
        self.euclidean_matrix = None
        self.weighted_matrix = None

    def calculate_manhattan_matrix(self) -> np.ndarray:
        """Calculate Manhattan distance matrix."""
        matrix = np.zeros((self.n_nodes, self.n_nodes))
        for i, id_i in enumerate(self.node_ids):
            for j, id_j in enumerate(self.node_ids):
                x_i, y_i, _ = self.nodes[id_i]
                x_j, y_j, _ = self.nodes[id_j]
                matrix[i, j] = self.calculator.manhattan((x_i, y_i), (x_j, y_j))
        self.manhattan_matrix = matrix
        return matrix

    def calculate_euclidean_matrix(self) -> np.ndarray:
        """Calculate Euclidean distance matrix."""
        matrix = np.zeros((self.n_nodes, self.n_nodes))
        for i, id_i in enumerate(self.node_ids):
            for j, id_j in enumerate(self.node_ids):
                x_i, y_i, _ = self.nodes[id_i]
                x_j, y_j, _ = self.nodes[id_j]
                matrix[i, j] = self.calculator.euclidean((x_i, y_i), (x_j, y_j))
        self.euclidean_matrix = matrix
        return matrix

    def calculate_weighted_matrix(self, zone_weights: Dict[str, float]) -> np.ndarray:
        """
        Calculate weighted distance matrix based on zone types.

        Args:
            zone_weights: Dictionary mapping zone_type -> weight_factor
        """
        if self.manhattan_matrix is None:
            self.calculate_manhattan_matrix()

        matrix = np.zeros((self.n_nodes, self.n_nodes))
        for i, id_i in enumerate(self.node_ids):
            for j, id_j in enumerate(self.node_ids):
                _, _, zone_i = self.nodes[id_i]
                _, _, zone_j = self.nodes[id_j]
                avg_weight = (zone_weights.get(zone_i, 1.0) +
                             zone_weights.get(zone_j, 1.0)) / 2
                matrix[i, j] = self.manhattan_matrix[i, j] * avg_weight
        self.weighted_matrix = matrix
        return matrix

    def calculate_zone_aggregated(self) -> pd.DataFrame:
        """
        Calculate zone-to-zone aggregated distances.

        Formula: D_zone(Z_i, Z_j) = avg(d(a,b)) for all a in Z_i, b in Z_j
        """
        if self.manhattan_matrix is None:
            self.calculate_manhattan_matrix()

        # Group nodes by zone
        zones = {}
        for node_id, (x, y, zone) in self.nodes.items():
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(self.node_ids.index(node_id))

        zone_names = list(zones.keys())
        n_zones = len(zone_names)
        zone_matrix = np.zeros((n_zones, n_zones))

        for i, zone_i in enumerate(zone_names):
            for j, zone_j in enumerate(zone_names):
                indices_i = zones[zone_i]
                indices_j = zones[zone_j]
                total = sum(
                    self.manhattan_matrix[idx_i, idx_j]
                    for idx_i in indices_i
                    for idx_j in indices_j
                )
                count = len(indices_i) * len(indices_j)
                zone_matrix[i, j] = total / count if count > 0 else 0.0

        return pd.DataFrame(zone_matrix, index=zone_names, columns=zone_names)

    def to_dataframe(self, matrix: np.ndarray) -> pd.DataFrame:
        """Convert matrix to pandas DataFrame."""
        return pd.DataFrame(matrix, index=self.node_ids, columns=self.node_ids)

    def export_to_excel(self, filepath: str):
        """Export all matrices to Excel workbook."""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Node definitions
            node_df = pd.DataFrame([
                {'Node_ID': nid, 'X': x, 'Y': y, 'Zone': z}
                for nid, (x, y, z) in self.nodes.items()
            ])
            node_df.to_excel(writer, sheet_name='Nodes', index=False)

            # Distance matrices
            if self.manhattan_matrix is not None:
                self.to_dataframe(self.manhattan_matrix).to_excel(
                    writer, sheet_name='Manhattan')
            if self.euclidean_matrix is not None:
                self.to_dataframe(self.euclidean_matrix).to_excel(
                    writer, sheet_name='Euclidean')
            if self.weighted_matrix is not None:
                self.to_dataframe(self.weighted_matrix).to_excel(
                    writer, sheet_name='Weighted')

            # Zone aggregated
            zone_df = self.calculate_zone_aggregated()
            zone_df.to_excel(writer, sheet_name='Zone_Aggregated')


# =============================================================================
# SECTION 3: SIMULATION PARAMETERS
# =============================================================================

@dataclass
class AGVParameters:
    """AGV fleet configuration parameters."""
    count: int = 5
    cruise_speed: float = 1.5      # m/s
    acceleration: float = 0.5      # m/s^2
    deceleration: float = 0.5      # m/s^2
    turn_speed: float = 0.3        # m/s
    turn_delay: float = 2.0        # seconds
    length: float = 1.2            # meters
    width: float = 0.8             # meters
    payload_capacity: float = 500  # kg
    safety_buffer: float = 0.5     # meters


@dataclass
class BatteryParameters:
    """
    Battery and charging configuration.

    Based on Layout A: bl_k <= lambda^r_ku <= bh_k
    """
    capacity: float = 100          # kWh (total)
    low_threshold: float = 20      # bl_k (%)
    high_threshold: float = 95     # bh_k (%)
    idle_discharge_rate: float = 0.5   # %/hr
    moving_discharge_rate: float = 2.0 # %/hr
    loaded_discharge_rate: float = 3.5 # %/hr
    charging_rate: float = 10      # %/hr
    fast_charging_rate: float = 25 # %/hr
    charging_stations: int = 2
    charging_queue_capacity: int = 3


@dataclass
class TaskParameters:
    """Task and workflow configuration."""
    arrival_rate: float = 0.5      # tasks/min (lambda)
    pick_time: float = 15          # seconds
    drop_time: float = 10          # seconds
    priority_levels: int = 3
    timeout: float = 300           # seconds
    batch_size: int = 1
    shift_duration: float = 8      # hours
    peak_hour_factor: float = 1.5


@dataclass
class LayoutParameters:
    """Warehouse layout configuration."""
    aisle_width: float = 2.5       # meters
    aisle_length: float = 30       # meters
    cross_aisle_width: float = 3.0 # meters
    num_aisles: int = 8
    rack_height: float = 6         # meters
    storage_density: float = 0.7
    grid_resolution: float = 0.5   # meters
    zone_count: int = 4


@dataclass
class TrafficParameters:
    """Traffic and congestion configuration."""
    max_agvs_per_aisle: int = 2
    intersection_capacity: int = 1
    congestion_weight: float = 1.0  # alpha
    deadlock_timeout: float = 30    # seconds
    reservation_window: float = 10  # seconds
    lookahead_distance: float = 5   # meters
    conflict_resolution: str = "FCFS"


@dataclass
class SimulationParameters:
    """Simulation control configuration."""
    time_step: float = 0.1         # seconds (delta_t)
    reporting_interval: float = 60 # seconds
    warmup_period: float = 300     # seconds
    duration: float = 28800        # seconds (8 hours)
    random_seed: int = 42
    log_level: str = "INFO"


@dataclass
class LegacyConstraints:
    """Legacy warehouse constraints."""
    floor_load_capacity: float = 5000  # kg/m^2
    door_width: float = 3.0            # meters
    ceiling_height: float = 8          # meters
    column_spacing: float = 10         # meters
    ramp_grade: float = 5              # degrees
    legacy_equipment_zones: int = 2
    human_worker_zones: int = 3


@dataclass
class SimulationConfig:
    """Complete simulation configuration."""
    agv: AGVParameters = field(default_factory=AGVParameters)
    battery: BatteryParameters = field(default_factory=BatteryParameters)
    task: TaskParameters = field(default_factory=TaskParameters)
    layout: LayoutParameters = field(default_factory=LayoutParameters)
    traffic: TrafficParameters = field(default_factory=TrafficParameters)
    simulation: SimulationParameters = field(default_factory=SimulationParameters)
    legacy: LegacyConstraints = field(default_factory=LegacyConstraints)

    def to_json(self) -> str:
        """Export configuration to JSON."""
        return json.dumps(self.__dict__, default=lambda o: o.__dict__, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'SimulationConfig':
        """Load configuration from JSON."""
        data = json.loads(json_str)
        return cls(
            agv=AGVParameters(**data.get('agv', {})),
            battery=BatteryParameters(**data.get('battery', {})),
            task=TaskParameters(**data.get('task', {})),
            layout=LayoutParameters(**data.get('layout', {})),
            traffic=TrafficParameters(**data.get('traffic', {})),
            simulation=SimulationParameters(**data.get('simulation', {})),
            legacy=LegacyConstraints(**data.get('legacy', {}))
        )

    def validate(self) -> List[str]:
        """Validate parameter constraints and return warnings."""
        warnings = []

        if self.agv.cruise_speed > 3.0:
            warnings.append("AGV cruise speed exceeds safe limit (3.0 m/s)")
        if self.agv.width >= self.layout.aisle_width - 2 * self.agv.safety_buffer:
            warnings.append("AGV width too large for aisle with safety buffer")
        if self.battery.low_threshold >= self.battery.high_threshold:
            warnings.append("Battery low threshold must be < high threshold")
        if self.traffic.max_agvs_per_aisle > self.agv.count:
            warnings.append("Max AGVs per aisle exceeds fleet size")

        return warnings

    def to_parameter_table(self) -> pd.DataFrame:
        """Generate parameter table for documentation."""
        rows = []
        for category, params in [
            ('AGV', self.agv),
            ('Battery', self.battery),
            ('Task', self.task),
            ('Layout', self.layout),
            ('Traffic', self.traffic),
            ('Simulation', self.simulation),
            ('Legacy', self.legacy)
        ]:
            for field_name, value in params.__dict__.items():
                rows.append({
                    'Category': category,
                    'Parameter': field_name,
                    'Value': value,
                    'Type': type(value).__name__
                })
        return pd.DataFrame(rows)


# =============================================================================
# SECTION 4: PERFORMANCE METRICS
# =============================================================================

class AGVState(Enum):
    """AGV operational states."""
    TRAVELING_LOADED = "traveling_loaded"
    TRAVELING_EMPTY = "traveling_empty"
    PICKING = "picking"
    DROPPING = "dropping"
    WAITING = "waiting"
    CHARGING = "charging"
    IDLE = "idle"


@dataclass
class TaskCompletion:
    """Record of completed task."""
    task_id: str
    agv_id: str
    start_time: float
    end_time: float
    origin: str
    destination: str
    distance: float


@dataclass
class StateRecord:
    """Record of AGV state duration."""
    agv_id: str
    state: AGVState
    start_time: float
    end_time: float


@dataclass
class ConflictRecord:
    """Record of conflict event."""
    timestamp: float
    agv_ids: List[str]
    conflict_type: str
    location: Tuple[float, float]
    resolution_time: float


class PerformanceMetrics:
    """
    Calculate all performance metrics for simulation.

    Metrics:
    - Throughput (tasks/hour)
    - AGV utilization
    - Average travel distance
    - Idle time percentage
    - Conflict frequency
    - Queue wait time
    """

    def __init__(
        self,
        completions: List[TaskCompletion],
        state_records: List[StateRecord],
        conflicts: List[ConflictRecord]
    ):
        self.completions = completions
        self.state_records = state_records
        self.conflicts = conflicts

    # Throughput Metrics
    def hourly_throughput(self, start_time: float, end_time: float) -> float:
        """Throughput = N_completed / T_hours"""
        completed = [t for t in self.completions
                    if start_time <= t.end_time <= end_time]
        hours = (end_time - start_time) / 3600
        return len(completed) / hours if hours > 0 else 0

    def per_agv_throughput(self, period_hours: float) -> Dict[str, float]:
        """Throughput per AGV."""
        agv_counts = {}
        for t in self.completions:
            agv_counts[t.agv_id] = agv_counts.get(t.agv_id, 0) + 1
        return {agv: count / period_hours for agv, count in agv_counts.items()}

    # Utilization Metrics
    def calculate_state_times(self, agv_id: str = None) -> Dict[AGVState, float]:
        """Calculate total time in each state."""
        records = self.state_records
        if agv_id:
            records = [r for r in records if r.agv_id == agv_id]

        state_times = {state: 0.0 for state in AGVState}
        for record in records:
            duration = record.end_time - record.start_time
            state_times[record.state] += duration
        return state_times

    def productive_utilization(self, agv_id: str = None) -> float:
        """
        Productive utilization = T_active / T_total

        Active = traveling_loaded + picking + dropping
        """
        productive_states = {
            AGVState.TRAVELING_LOADED,
            AGVState.PICKING,
            AGVState.DROPPING
        }
        state_times = self.calculate_state_times(agv_id)
        total_time = sum(state_times.values())
        productive_time = sum(state_times[s] for s in productive_states)
        return productive_time / total_time if total_time > 0 else 0

    def operational_utilization(self, agv_id: str = None) -> float:
        """Operational utilization including empty travel."""
        operational_states = {
            AGVState.TRAVELING_LOADED,
            AGVState.TRAVELING_EMPTY,
            AGVState.PICKING,
            AGVState.DROPPING
        }
        state_times = self.calculate_state_times(agv_id)
        total_time = sum(state_times.values())
        operational_time = sum(state_times[s] for s in operational_states)
        return operational_time / total_time if total_time > 0 else 0

    def idle_percentage(self, agv_id: str = None) -> float:
        """Idle % = (T_idle + T_waiting) / T_total * 100"""
        state_times = self.calculate_state_times(agv_id)
        total_time = sum(state_times.values())
        idle_time = state_times[AGVState.IDLE] + state_times[AGVState.WAITING]
        return (idle_time / total_time * 100) if total_time > 0 else 0

    # Distance Metrics
    def average_distance_per_task(self) -> float:
        """D_avg = sum(d_task) / N_tasks"""
        if not self.completions:
            return 0
        total_dist = sum(t.distance for t in self.completions)
        return total_dist / len(self.completions)

    def distance_by_agv(self) -> Dict[str, float]:
        """Total distance traveled by each AGV."""
        distances = {}
        for t in self.completions:
            distances[t.agv_id] = distances.get(t.agv_id, 0) + t.distance
        return distances

    def workload_balance(self) -> Dict[str, float]:
        """Calculate workload distribution metrics."""
        distances = self.distance_by_agv()
        if not distances:
            return {'mean': 0, 'std': 0, 'cv': 0}

        values = list(distances.values())
        mean_dist = np.mean(values)
        std_dist = np.std(values)

        return {
            'mean': mean_dist,
            'std': std_dist,
            'cv': std_dist / mean_dist if mean_dist > 0 else 0
        }

    # Conflict Metrics
    def conflict_frequency(self, period_hours: float) -> float:
        """Conflicts per hour."""
        return len(self.conflicts) / period_hours if period_hours > 0 else 0

    def conflicts_per_task(self) -> float:
        """Average conflicts per task."""
        if not self.completions:
            return 0
        return len(self.conflicts) / len(self.completions)

    def conflict_by_type(self) -> Dict[str, int]:
        """Count conflicts by type."""
        counts = {}
        for c in self.conflicts:
            counts[c.conflict_type] = counts.get(c.conflict_type, 0) + 1
        return counts

    def average_resolution_time(self) -> float:
        """Average time to resolve conflicts."""
        if not self.conflicts:
            return 0
        return np.mean([c.resolution_time for c in self.conflicts])

    # Summary Report
    def generate_summary(self, period_hours: float) -> Dict:
        """Generate comprehensive metrics summary."""
        return {
            'throughput': {
                'hourly': self.hourly_throughput(0, period_hours * 3600),
                'per_agv': self.per_agv_throughput(period_hours),
                'total_tasks': len(self.completions)
            },
            'utilization': {
                'productive': self.productive_utilization(),
                'operational': self.operational_utilization(),
                'idle_pct': self.idle_percentage()
            },
            'distance': {
                'avg_per_task': self.average_distance_per_task(),
                'by_agv': self.distance_by_agv(),
                'balance': self.workload_balance()
            },
            'conflicts': {
                'frequency': self.conflict_frequency(period_hours),
                'per_task': self.conflicts_per_task(),
                'by_type': self.conflict_by_type(),
                'avg_resolution': self.average_resolution_time()
            }
        }


# =============================================================================
# SECTION 5: CONSTRAINT EQUATIONS
# =============================================================================

class ConstraintChecker:
    """
    Check all constraints for legacy warehouse retrofit.

    Constraints:
    - Aisle width (W >= W_agv + 2*d_safety)
    - Floor load (P <= P_max)
    - AGVs per aisle (n <= C_aisle)
    - Battery (bl_k <= lambda <= bh_k)
    """

    @staticmethod
    def check_aisle_width(
        aisle_width: float,
        agv_width: float,
        safety_buffer: float,
        sensor_clearance: float = 0.2,
        bidirectional: bool = False
    ) -> Dict:
        """
        Check aisle width constraint.

        Unidirectional: W >= W_agv + 2*d_safety + clearance
        Bidirectional: W >= 2*W_agv + 3*d_safety
        """
        if bidirectional:
            min_width = 2 * agv_width + 3 * safety_buffer
        else:
            min_width = agv_width + 2 * safety_buffer + sensor_clearance

        satisfied = aisle_width >= min_width
        return {
            'satisfied': satisfied,
            'aisle_width': aisle_width,
            'minimum_required': min_width,
            'margin': aisle_width - min_width,
            'bidirectional': bidirectional
        }

    @staticmethod
    def check_floor_load(
        agv_mass: float,
        payload_mass: float,
        wheel_contact_area: float,
        floor_capacity: float,
        acceleration: float = 0.5,
        num_wheels: int = 4
    ) -> Dict:
        """
        Check floor load capacity.

        P_static = (M_agv + M_payload) * g / A_contact
        P_dynamic = P_static * (1 + a/g)
        """
        g = 9.81
        total_mass = agv_mass + payload_mass
        total_contact_area = wheel_contact_area * num_wheels

        static_pressure = (total_mass * g) / total_contact_area
        dynamic_factor = 1 + acceleration / g
        dynamic_pressure = static_pressure * dynamic_factor

        return {
            'satisfied': dynamic_pressure <= floor_capacity,
            'static_pressure_pa': static_pressure,
            'dynamic_pressure_pa': dynamic_pressure,
            'floor_capacity_pa': floor_capacity,
            'utilization_pct': (dynamic_pressure / floor_capacity) * 100
        }

    @staticmethod
    def calculate_aisle_capacity(
        aisle_length: float,
        agv_length: float,
        following_distance: float,
        bidirectional: bool = False
    ) -> int:
        """
        Calculate maximum AGVs per aisle.

        C_aisle = floor(L_aisle / (L_agv + d_following))
        """
        space_per_agv = agv_length + following_distance
        capacity = int(aisle_length / space_per_agv)

        if bidirectional:
            return max(1, capacity // 2)
        return max(1, capacity)


class BatteryConstraints:
    """
    Battery depletion model and constraints.

    Based on Layout A: bl_k <= lambda^r_ku <= bh_k
    """

    def __init__(
        self,
        capacity: float = 100.0,
        low_threshold: float = 20.0,      # bl_k
        high_threshold: float = 95.0,     # bh_k
        idle_rate: float = 0.5,
        move_rate: float = 2.0,
        load_rate: float = 3.5,
        charge_rate: float = 10.0
    ):
        self.capacity = capacity
        self.bl_k = low_threshold
        self.bh_k = high_threshold
        self.rates = {
            'idle': idle_rate,
            'moving': move_rate,
            'loaded': load_rate,
            'charging': -charge_rate
        }

    def update_battery(
        self,
        current_level: float,
        state: str,
        duration_hours: float
    ) -> float:
        """Update battery level based on activity."""
        rate = self.rates.get(state, self.rates['idle'])
        new_level = current_level - rate * duration_hours
        return max(0, min(self.bh_k, new_level))

    def check_task_feasibility(
        self,
        current_level: float,
        task_distance: float,
        distance_to_charger: float,
        speed: float
    ) -> Dict:
        """
        Check if AGV can complete task and reach charger.

        Constraint: d_task + d_to_charger <= D_max
        """
        task_time_hours = task_distance / (speed * 3600)
        charger_time_hours = distance_to_charger / (speed * 3600)

        task_consumption = self.rates['loaded'] * task_time_hours
        charger_consumption = self.rates['moving'] * charger_time_hours
        total_consumption = task_consumption + charger_consumption

        available = current_level - self.bl_k
        feasible = total_consumption <= available

        return {
            'feasible': feasible,
            'current_level': current_level,
            'available_charge': available,
            'required_charge': total_consumption,
            'recommendation': 'PROCEED' if feasible else 'CHARGE_FIRST'
        }

    def estimate_range(
        self,
        current_level: float,
        speed: float,
        loaded: bool = False
    ) -> float:
        """
        Estimate maximum distance before low threshold.

        D_max = (B_current - bl_k) / (r / v)
        """
        available = current_level - self.bl_k
        rate = self.rates['loaded'] if loaded else self.rates['moving']
        rate_per_meter = rate / (speed * 3600)

        if rate_per_meter <= 0:
            return float('inf')
        return available / rate_per_meter

    def time_to_charge(self, current_level: float, target: float = None) -> float:
        """Calculate time to charge to target level."""
        if target is None:
            target = self.bh_k
        charge_needed = target - current_level
        if charge_needed <= 0:
            return 0
        return charge_needed / abs(self.rates['charging'])


# =============================================================================
# SECTION 6: OPTIMIZATION OBJECTIVE FUNCTION
# =============================================================================

@dataclass
class OptimizationWeights:
    """
    Weights for multi-objective optimization.

    Must sum to 1.0.
    """
    travel: float = 0.35      # alpha_1
    time: float = 0.30        # alpha_2
    energy: float = 0.20      # alpha_3
    conflict: float = 0.15    # alpha_4

    def validate(self):
        """Ensure weights sum to 1.0."""
        total = self.travel + self.time + self.energy + self.conflict
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")


class ObjectiveFunction:
    """
    Multi-objective optimization for AGV scheduling.

    Based on Layout A: f = min sum_{k in K} c_k (z^e_ku - z^s_kd)

    Adapted objective:
    Z = alpha_1*Z_travel + alpha_2*Z_time + alpha_3*Z_energy + alpha_4*Z_conflict
    """

    def __init__(
        self,
        weights: OptimizationWeights,
        distance_matrix: np.ndarray,
        node_ids: List[str],
        cost_per_meter: float = 0.01,
        cost_per_second: float = 0.005,
        cost_per_battery_pct: float = 0.1,
        cost_per_conflict: float = 5.0
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
        """Get distance between nodes."""
        i = self.node_to_idx[from_node]
        j = self.node_to_idx[to_node]
        return self.distance_matrix[i, j]

    def calculate_travel_cost(self, paths: Dict[str, List[str]]) -> float:
        """Z_travel = sum_k sum_(i,j) d_ij"""
        total = 0.0
        for agv_id, path in paths.items():
            for i in range(len(path) - 1):
                total += self.get_distance(path[i], path[i+1])
        return total * self.c_distance

    def calculate_time_cost(
        self,
        travel_times: Dict[str, float],
        wait_times: Dict[str, float],
        service_times: Dict[str, float]
    ) -> float:
        """Z_time = sum_k (T_travel + T_wait + T_service)"""
        total = sum(travel_times.values()) + sum(wait_times.values()) + sum(service_times.values())
        return total * self.c_time

    def calculate_energy_cost(self, battery_consumption: Dict[str, float]) -> float:
        """Z_energy = sum_k (B_start - B_end)"""
        return sum(battery_consumption.values()) * self.c_battery

    def calculate_conflict_cost(self, conflicts: List) -> float:
        """Z_conflict = N_conflicts * c_conflict"""
        return len(conflicts) * self.c_conflict

    def evaluate(
        self,
        paths: Dict[str, List[str]],
        travel_times: Dict[str, float],
        wait_times: Dict[str, float],
        service_times: Dict[str, float],
        battery_consumption: Dict[str, float],
        conflicts: List
    ) -> Dict:
        """
        Evaluate complete objective function.

        Z = alpha_1*Z_travel + alpha_2*Z_time + alpha_3*Z_energy + alpha_4*Z_conflict
        """
        z_travel = self.calculate_travel_cost(paths)
        z_time = self.calculate_time_cost(travel_times, wait_times, service_times)
        z_energy = self.calculate_energy_cost(battery_consumption)
        z_conflict = self.calculate_conflict_cost(conflicts)

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


# =============================================================================
# SECTION 7: SAMPLE WAREHOUSE CONFIGURATION
# =============================================================================

def create_sample_warehouse() -> Dict:
    """
    Create sample 12-node warehouse configuration.

        [N01]----[N02]----[N03]----[N04]
          |        |        |        |
        [N05]----[N06]----[N07]----[N08]
          |        |        |        |
        [N09]----[N10]----[N11]----[N12]
    """
    nodes = {
        'N01': (0, 20, 'Receiving'),
        'N02': (10, 20, 'Receiving'),
        'N03': (20, 20, 'Receiving'),
        'N04': (30, 20, 'Receiving'),
        'N05': (0, 10, 'Storage'),
        'N06': (10, 10, 'Storage'),
        'N07': (20, 10, 'Storage'),
        'N08': (30, 10, 'Storage'),
        'N09': (0, 0, 'Shipping'),
        'N10': (10, 0, 'Shipping'),
        'N11': (20, 0, 'Shipping'),
        'N12': (30, 0, 'Shipping'),
    }

    zone_weights = {
        'Receiving': 1.2,
        'Storage': 1.0,
        'Shipping': 1.3,
    }

    return {
        'nodes': nodes,
        'zone_weights': zone_weights
    }


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MATHEMATICAL FOUNDATIONS FOR LEGACY WAREHOUSE ROBOTICS RETROFIT")
    print("=" * 70)

    # 1. Create sample warehouse
    print("\n1. Creating sample warehouse configuration...")
    warehouse_config = create_sample_warehouse()
    nodes = warehouse_config['nodes']
    zone_weights = warehouse_config['zone_weights']

    # 2. Generate distance matrices
    print("\n2. Generating distance matrices...")
    dist_matrix = WarehouseDistanceMatrix(nodes)
    manhattan = dist_matrix.calculate_manhattan_matrix()
    euclidean = dist_matrix.calculate_euclidean_matrix()
    weighted = dist_matrix.calculate_weighted_matrix(zone_weights)

    print("\nManhattan Distance Matrix (sample):")
    print(dist_matrix.to_dataframe(manhattan).iloc[:4, :4])

    print("\nZone-to-Zone Aggregated Distances:")
    print(dist_matrix.calculate_zone_aggregated())

    # 3. Configuration parameters
    print("\n3. Loading simulation parameters...")
    config = SimulationConfig()
    config.agv.count = 5
    config.task.arrival_rate = 0.5
    warnings = config.validate()
    if warnings:
        print("Warnings:", warnings)
    else:
        print("All parameters validated successfully.")

    # 4. Travel time calculation
    print("\n4. Travel time calculation example...")
    travel_calc = TravelTimeCalculator(
        cruise_speed=config.agv.cruise_speed,
        acceleration=config.agv.acceleration,
        turn_time=config.agv.turn_delay
    )
    travel_result = travel_calc.calculate(distance=50, n_turns=2, queue_wait=5)
    print(f"Distance: 50m, Turns: 2, Queue: 5s")
    print(f"Total travel time: {travel_result['total_time']:.2f}s")

    # 5. Constraint checking
    print("\n5. Constraint checking...")
    aisle_check = ConstraintChecker.check_aisle_width(
        aisle_width=config.layout.aisle_width,
        agv_width=config.agv.width,
        safety_buffer=config.agv.safety_buffer,
        bidirectional=False
    )
    print(f"Aisle width constraint: {'PASS' if aisle_check['satisfied'] else 'FAIL'}")
    print(f"  Required: {aisle_check['minimum_required']:.2f}m, Available: {aisle_check['aisle_width']:.2f}m")

    # 6. Battery constraint
    print("\n6. Battery constraint check...")
    battery = BatteryConstraints(
        low_threshold=config.battery.low_threshold,
        high_threshold=config.battery.high_threshold
    )
    feasibility = battery.check_task_feasibility(
        current_level=50,
        task_distance=100,
        distance_to_charger=30,
        speed=config.agv.cruise_speed
    )
    print(f"Task feasibility (50% battery, 100m task): {feasibility['recommendation']}")

    # 7. Objective function
    print("\n7. Optimization objective function...")
    weights = OptimizationWeights(travel=0.35, time=0.30, energy=0.20, conflict=0.15)
    obj_func = ObjectiveFunction(weights, manhattan, list(nodes.keys()))

    result = obj_func.evaluate(
        paths={'AGV1': ['N01', 'N02', 'N06', 'N10'], 'AGV2': ['N04', 'N08', 'N11']},
        travel_times={'AGV1': 60, 'AGV2': 45},
        wait_times={'AGV1': 5, 'AGV2': 3},
        service_times={'AGV1': 25, 'AGV2': 25},
        battery_consumption={'AGV1': 3.0, 'AGV2': 2.5},
        conflicts=[{'type': 'intersection'}]
    )
    print(f"Total objective cost: ${result['total_cost']:.2f}")
    print("Component breakdown:")
    for comp, val in result['weighted_components'].items():
        print(f"  {comp}: ${val:.2f}")

    print("\n" + "=" * 70)
    print("Mathematical foundations ready for implementation.")
    print("=" * 70)
