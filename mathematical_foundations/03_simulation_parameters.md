# Simulation Parameters Table
## Comprehensive Parameter Definitions for Legacy Warehouse Retrofit

---

## 1. AGV Fleet Parameters

| Parameter | Symbol | Default Value | Unit | Range | Description |
|-----------|--------|---------------|------|-------|-------------|
| AGV Count | N_agv | 5 | count | 1-50 | Total number of AGVs in fleet |
| Cruise Speed | v_cruise | 1.5 | m/s | 0.5-3.0 | Maximum travel velocity |
| Acceleration | a | 0.5 | m/s^2 | 0.2-1.0 | Rate of speed increase |
| Deceleration | a_dec | 0.5 | m/s^2 | 0.2-1.5 | Rate of speed decrease |
| Turn Speed | v_turn | 0.3 | m/s | 0.1-0.5 | Velocity during turns |
| Turn Delay | t_turn | 2.0 | s | 0.5-5.0 | Time penalty per 90-degree turn |
| AGV Length | L_agv | 1.2 | m | 0.8-2.5 | Physical length of AGV |
| AGV Width | W_agv | 0.8 | m | 0.5-1.5 | Physical width of AGV |
| Payload Capacity | M_payload | 500 | kg | 100-2000 | Maximum load weight |
| Safety Buffer | d_safety | 0.5 | m | 0.3-1.0 | Required clearance between AGVs |

---

## 2. Battery and Power Parameters

Based on Layout A's battery constraints: `bl_k <= lambda^r_ku <= bh_k`

| Parameter | Symbol | Default Value | Unit | Range | Description |
|-----------|--------|---------------|------|-------|-------------|
| Battery Capacity | B_cap | 100 | kWh | 20-200 | Total battery capacity |
| Battery Low Threshold | bl_k | 20 | % | 10-30 | Minimum charge before mandatory charging |
| Battery High Threshold | bh_k | 95 | % | 85-100 | Target charge level after charging |
| Discharge Rate (Idle) | r_idle | 0.5 | %/hr | 0.1-1.0 | Battery drain when stationary |
| Discharge Rate (Moving) | r_move | 2.0 | %/hr | 1.0-5.0 | Battery drain during travel |
| Discharge Rate (Loaded) | r_load | 3.5 | %/hr | 2.0-8.0 | Battery drain when carrying payload |
| Charging Rate | r_charge | 10 | %/hr | 5-50 | Battery replenishment rate |
| Fast Charging Rate | r_fast | 25 | %/hr | 15-80 | Rapid charge rate (if available) |
| Charging Stations | N_charge | 2 | count | 1-10 | Number of charging points |
| Charging Queue Capacity | Q_charge | 3 | count | 1-5 | AGVs that can wait at charging area |

---

## 3. Task and Workflow Parameters

| Parameter | Symbol | Default Value | Unit | Range | Description |
|-----------|--------|---------------|------|-------|-------------|
| Task Arrival Rate | lambda_task | 0.5 | tasks/min | 0.1-5.0 | Average rate of new task generation |
| Pick Time | t_pick | 15 | s | 5-60 | Time to pick up item at origin |
| Drop Time | t_drop | 10 | s | 3-30 | Time to deposit item at destination |
| Task Priority Levels | P_levels | 3 | count | 1-5 | Number of priority categories |
| Task Timeout | T_timeout | 300 | s | 60-900 | Maximum wait time before escalation |
| Batch Size | N_batch | 1 | count | 1-10 | Tasks grouped per AGV trip |
| Shift Duration | T_shift | 8 | hr | 4-12 | Working period length |
| Peak Hour Factor | phi_peak | 1.5 | ratio | 1.0-3.0 | Task rate multiplier during peak |

---

## 4. Warehouse Layout Parameters

| Parameter | Symbol | Default Value | Unit | Range | Description |
|-----------|--------|---------------|------|-------|-------------|
| Aisle Width | W_aisle | 2.5 | m | 1.5-4.0 | Width of travel corridors |
| Aisle Length | L_aisle | 30 | m | 10-100 | Length of storage aisles |
| Cross-Aisle Width | W_cross | 3.0 | m | 2.0-5.0 | Width of perpendicular corridors |
| Number of Aisles | N_aisle | 8 | count | 2-50 | Total storage aisles |
| Rack Height | H_rack | 6 | m | 2-15 | Maximum storage elevation |
| Storage Density | rho_storage | 0.7 | ratio | 0.5-0.9 | Percentage of space used for storage |
| Grid Resolution | delta_grid | 0.5 | m | 0.1-2.0 | Minimum movement increment |
| Zone Count | N_zone | 4 | count | 2-20 | Number of operational zones |

---

## 5. Traffic and Congestion Parameters

| Parameter | Symbol | Default Value | Unit | Range | Description |
|-----------|--------|---------------|------|-------|-------------|
| Max AGVs per Aisle | C_aisle | 2 | count | 1-5 | Congestion limit per aisle |
| Intersection Capacity | C_inter | 1 | count | 1-3 | AGVs allowed at intersection |
| Congestion Weight | alpha | 1.0 | ratio | 0.5-2.0 | Sensitivity to traffic density |
| Deadlock Timeout | T_deadlock | 30 | s | 10-120 | Time before deadlock resolution |
| Reservation Window | T_reserve | 10 | s | 5-60 | Time slot for path reservation |
| Look-ahead Distance | d_look | 5 | m | 2-20 | Distance for collision detection |
| Conflict Resolution Priority | - | FCFS | - | - | First-Come-First-Served or Priority |

---

## 6. Performance and Monitoring Parameters

| Parameter | Symbol | Default Value | Unit | Range | Description |
|-----------|--------|---------------|------|-------|-------------|
| Simulation Time Step | delta_t | 0.1 | s | 0.01-1.0 | Discrete time increment |
| Reporting Interval | T_report | 60 | s | 10-600 | Frequency of metric calculation |
| Warm-up Period | T_warmup | 300 | s | 0-900 | Initial stabilization time |
| Simulation Duration | T_sim | 28800 | s | 3600-86400 | Total simulation run time (8 hours) |
| Random Seed | seed | 42 | - | - | Reproducibility seed |
| Log Level | - | INFO | - | - | DEBUG, INFO, WARNING, ERROR |

---

## 7. Legacy Constraint Parameters

| Parameter | Symbol | Default Value | Unit | Range | Description |
|-----------|--------|---------------|------|-------|-------------|
| Floor Load Capacity | W_floor | 5000 | kg/m^2 | 1000-10000 | Maximum floor weight per area |
| Door Width | W_door | 3.0 | m | 2.0-5.0 | Minimum door opening for AGV |
| Ceiling Height | H_ceil | 8 | m | 3-15 | Overhead clearance |
| Column Spacing | d_column | 10 | m | 5-20 | Distance between support columns |
| Ramp Grade | theta_ramp | 5 | degrees | 0-10 | Maximum floor incline |
| Legacy Equipment Zones | N_legacy | 2 | count | 0-10 | Areas with non-AGV equipment |
| Human Worker Zones | N_human | 3 | count | 0-15 | Areas requiring human-AGV coordination |

---

## 8. Python Parameter Configuration Class

```python
from dataclasses import dataclass, field
from typing import Optional
import json

@dataclass
class AGVParameters:
    """AGV fleet configuration parameters."""
    count: int = 5
    cruise_speed: float = 1.5  # m/s
    acceleration: float = 0.5  # m/s^2
    deceleration: float = 0.5  # m/s^2
    turn_speed: float = 0.3    # m/s
    turn_delay: float = 2.0    # seconds
    length: float = 1.2        # meters
    width: float = 0.8         # meters
    payload_capacity: float = 500  # kg
    safety_buffer: float = 0.5     # meters


@dataclass
class BatteryParameters:
    """Battery and charging configuration."""
    capacity: float = 100      # kWh
    low_threshold: float = 20  # %
    high_threshold: float = 95 # %
    idle_discharge_rate: float = 0.5   # %/hr
    moving_discharge_rate: float = 2.0 # %/hr
    loaded_discharge_rate: float = 3.5 # %/hr
    charging_rate: float = 10  # %/hr
    fast_charging_rate: float = 25  # %/hr
    charging_stations: int = 2
    charging_queue_capacity: int = 3


@dataclass
class TaskParameters:
    """Task and workflow configuration."""
    arrival_rate: float = 0.5  # tasks/min
    pick_time: float = 15      # seconds
    drop_time: float = 10      # seconds
    priority_levels: int = 3
    timeout: float = 300       # seconds
    batch_size: int = 1
    shift_duration: float = 8  # hours
    peak_hour_factor: float = 1.5


@dataclass
class LayoutParameters:
    """Warehouse layout configuration."""
    aisle_width: float = 2.5   # meters
    aisle_length: float = 30   # meters
    cross_aisle_width: float = 3.0  # meters
    num_aisles: int = 8
    rack_height: float = 6     # meters
    storage_density: float = 0.7
    grid_resolution: float = 0.5  # meters
    zone_count: int = 4


@dataclass
class TrafficParameters:
    """Traffic and congestion configuration."""
    max_agvs_per_aisle: int = 2
    intersection_capacity: int = 1
    congestion_weight: float = 1.0
    deadlock_timeout: float = 30  # seconds
    reservation_window: float = 10  # seconds
    lookahead_distance: float = 5  # meters
    conflict_resolution: str = "FCFS"  # or "Priority"


@dataclass
class SimulationParameters:
    """Simulation control configuration."""
    time_step: float = 0.1     # seconds
    reporting_interval: float = 60  # seconds
    warmup_period: float = 300  # seconds
    duration: float = 28800    # seconds (8 hours)
    random_seed: int = 42
    log_level: str = "INFO"


@dataclass
class LegacyConstraints:
    """Legacy warehouse constraints."""
    floor_load_capacity: float = 5000  # kg/m^2
    door_width: float = 3.0    # meters
    ceiling_height: float = 8  # meters
    column_spacing: float = 10 # meters
    ramp_grade: float = 5      # degrees
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

    def validate(self) -> list:
        """Validate parameter constraints and return list of warnings."""
        warnings = []

        # AGV constraints
        if self.agv.cruise_speed > 3.0:
            warnings.append("AGV cruise speed exceeds safe limit (3.0 m/s)")
        if self.agv.width >= self.layout.aisle_width - 2 * self.agv.safety_buffer:
            warnings.append("AGV width too large for aisle width with safety buffer")

        # Battery constraints
        if self.battery.low_threshold >= self.battery.high_threshold:
            warnings.append("Battery low threshold must be less than high threshold")

        # Traffic constraints
        if self.traffic.max_agvs_per_aisle > self.agv.count:
            warnings.append("Max AGVs per aisle exceeds total fleet size")

        return warnings


# Example usage
if __name__ == "__main__":
    config = SimulationConfig()

    # Customize for specific scenario
    config.agv.count = 8
    config.task.arrival_rate = 0.8
    config.battery.charging_stations = 3

    # Validate
    warnings = config.validate()
    for w in warnings:
        print(f"Warning: {w}")

    # Export
    print(config.to_json())
```

---

## 9. Excel Parameter Template

### Sheet: Parameters

| Category | Parameter | Symbol | Value | Unit | Min | Max | Notes |
|----------|-----------|--------|-------|------|-----|-----|-------|
| AGV | Count | N_agv | 5 | count | 1 | 50 | Fleet size |
| AGV | Speed | v_cruise | 1.5 | m/s | 0.5 | 3.0 | Max velocity |
| Battery | Capacity | B_cap | 100 | kWh | 20 | 200 | Total charge |
| Battery | Low Threshold | bl_k | 20 | % | 10 | 30 | Charge warning |
| Task | Arrival Rate | lambda | 0.5 | /min | 0.1 | 5.0 | Task frequency |
| Layout | Aisle Width | W_aisle | 2.5 | m | 1.5 | 4.0 | Corridor width |
| Traffic | Max per Aisle | C_aisle | 2 | count | 1 | 5 | Congestion limit |

### Excel Validation Formula Example:
```excel
=IF(AND(B3>=E3, B3<=F3), "Valid", "Out of Range")
```
