# Performance Metrics Formulas
## Key Performance Indicators for Legacy Warehouse Robotics Simulation

---

## 1. Throughput Metrics

### 1.1 Task Throughput

**Definition:** Number of completed tasks per unit time

```
Throughput = N_completed / T_period
```

**Variants:**

| Metric | Formula | Unit |
|--------|---------|------|
| Hourly Throughput | N_completed / T_hours | tasks/hr |
| Per-AGV Throughput | N_completed / (N_agv * T_hours) | tasks/agv-hr |
| Peak Throughput | max(N_interval) for all intervals | tasks/hr |
| Sustained Throughput | median(N_interval) | tasks/hr |

**Python Implementation:**
```python
from typing import List, Dict
from datetime import datetime, timedelta
import numpy as np

class ThroughputMetrics:
    """Calculate throughput-related performance metrics."""

    def __init__(self, task_completions: List[Dict]):
        """
        Initialize with task completion records.

        Args:
            task_completions: List of dicts with 'task_id', 'start_time',
                            'end_time', 'agv_id'
        """
        self.completions = task_completions

    def hourly_throughput(self, start_time: float, end_time: float) -> float:
        """Calculate tasks completed per hour."""
        completed = [t for t in self.completions
                    if start_time <= t['end_time'] <= end_time]
        hours = (end_time - start_time) / 3600
        return len(completed) / hours if hours > 0 else 0

    def per_agv_throughput(self, agv_id: str, period_hours: float) -> float:
        """Calculate throughput for a specific AGV."""
        agv_tasks = [t for t in self.completions if t['agv_id'] == agv_id]
        return len(agv_tasks) / period_hours if period_hours > 0 else 0

    def interval_throughput(self, interval_seconds: float = 3600) -> List[float]:
        """Calculate throughput for each time interval."""
        if not self.completions:
            return []

        min_time = min(t['end_time'] for t in self.completions)
        max_time = max(t['end_time'] for t in self.completions)

        intervals = []
        current = min_time
        while current < max_time:
            next_time = current + interval_seconds
            count = sum(1 for t in self.completions
                       if current <= t['end_time'] < next_time)
            intervals.append(count * (3600 / interval_seconds))  # Normalize to hourly
            current = next_time
        return intervals

    def peak_throughput(self, interval_seconds: float = 3600) -> float:
        """Find maximum throughput across intervals."""
        intervals = self.interval_throughput(interval_seconds)
        return max(intervals) if intervals else 0

    def sustained_throughput(self, interval_seconds: float = 3600) -> float:
        """Find median throughput (sustained performance)."""
        intervals = self.interval_throughput(interval_seconds)
        return np.median(intervals) if intervals else 0
```

---

## 2. AGV Utilization Metrics

### 2.1 Time-Based Utilization

```
Utilization = T_active / T_total
```

Where:
- `T_active` = Time spent on productive activities (traveling with load, picking, dropping)
- `T_total` = Total available time

**State Breakdown:**

| State | Symbol | Description | Productive? |
|-------|--------|-------------|-------------|
| Traveling (loaded) | T_travel_load | Moving with payload | Yes |
| Traveling (empty) | T_travel_empty | Moving without payload | Partial |
| Picking | T_pick | Loading item | Yes |
| Dropping | T_drop | Unloading item | Yes |
| Waiting | T_wait | Queued or blocked | No |
| Charging | T_charge | At charging station | No |
| Idle | T_idle | No assigned task | No |

**Utilization Categories:**

```
Productive Utilization = (T_travel_load + T_pick + T_drop) / T_total

Operational Utilization = (T_travel_load + T_travel_empty + T_pick + T_drop) / T_total

Availability = (T_total - T_charge - T_maintenance) / T_total
```

**Python Implementation:**
```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

class AGVState(Enum):
    TRAVELING_LOADED = "traveling_loaded"
    TRAVELING_EMPTY = "traveling_empty"
    PICKING = "picking"
    DROPPING = "dropping"
    WAITING = "waiting"
    CHARGING = "charging"
    IDLE = "idle"

@dataclass
class StateRecord:
    agv_id: str
    state: AGVState
    start_time: float
    end_time: float

class UtilizationMetrics:
    """Calculate AGV utilization metrics."""

    PRODUCTIVE_STATES = {
        AGVState.TRAVELING_LOADED,
        AGVState.PICKING,
        AGVState.DROPPING
    }

    OPERATIONAL_STATES = {
        AGVState.TRAVELING_LOADED,
        AGVState.TRAVELING_EMPTY,
        AGVState.PICKING,
        AGVState.DROPPING
    }

    def __init__(self, state_records: List[StateRecord]):
        self.records = state_records

    def calculate_state_times(self, agv_id: str = None) -> Dict[AGVState, float]:
        """Calculate total time in each state."""
        records = self.records
        if agv_id:
            records = [r for r in records if r.agv_id == agv_id]

        state_times = {state: 0.0 for state in AGVState}
        for record in records:
            duration = record.end_time - record.start_time
            state_times[record.state] += duration
        return state_times

    def productive_utilization(self, agv_id: str = None) -> float:
        """Calculate productive utilization ratio."""
        state_times = self.calculate_state_times(agv_id)
        total_time = sum(state_times.values())
        productive_time = sum(state_times[s] for s in self.PRODUCTIVE_STATES)
        return productive_time / total_time if total_time > 0 else 0

    def operational_utilization(self, agv_id: str = None) -> float:
        """Calculate operational utilization ratio."""
        state_times = self.calculate_state_times(agv_id)
        total_time = sum(state_times.values())
        operational_time = sum(state_times[s] for s in self.OPERATIONAL_STATES)
        return operational_time / total_time if total_time > 0 else 0

    def idle_percentage(self, agv_id: str = None) -> float:
        """Calculate percentage of time spent idle."""
        state_times = self.calculate_state_times(agv_id)
        total_time = sum(state_times.values())
        idle_time = state_times[AGVState.IDLE] + state_times[AGVState.WAITING]
        return (idle_time / total_time * 100) if total_time > 0 else 0

    def fleet_utilization_summary(self, agv_ids: List[str]) -> Dict:
        """Generate utilization summary for entire fleet."""
        summary = {
            'individual': {},
            'fleet_average': {}
        }

        for agv_id in agv_ids:
            summary['individual'][agv_id] = {
                'productive': self.productive_utilization(agv_id),
                'operational': self.operational_utilization(agv_id),
                'idle_pct': self.idle_percentage(agv_id)
            }

        # Fleet averages
        summary['fleet_average'] = {
            'productive': np.mean([s['productive']
                                  for s in summary['individual'].values()]),
            'operational': np.mean([s['operational']
                                   for s in summary['individual'].values()]),
            'idle_pct': np.mean([s['idle_pct']
                                for s in summary['individual'].values()])
        }
        return summary
```

---

## 3. Distance and Travel Metrics

### 3.1 Average Travel Distance per Task

```
D_avg = sum(d_task_i) / N_tasks
```

**Breakdown:**
```
D_avg_loaded = sum(d_loaded_i) / N_tasks    # Distance with payload
D_avg_empty = sum(d_empty_i) / N_tasks      # Distance without payload (repositioning)
Empty_ratio = D_avg_empty / D_avg_total     # Efficiency indicator
```

### 3.2 Travel Efficiency

```
Efficiency = D_direct / D_actual
```

Where:
- `D_direct` = Shortest possible distance (Manhattan or Euclidean)
- `D_actual` = Actual distance traveled (including detours)

**Python Implementation:**
```python
@dataclass
class TravelRecord:
    task_id: str
    agv_id: str
    origin: tuple
    destination: tuple
    distance_loaded: float
    distance_empty: float
    actual_distance: float
    direct_distance: float

class DistanceMetrics:
    """Calculate distance and travel efficiency metrics."""

    def __init__(self, travel_records: List[TravelRecord]):
        self.records = travel_records

    def average_distance_per_task(self) -> Dict[str, float]:
        """Calculate average distances per task."""
        if not self.records:
            return {'loaded': 0, 'empty': 0, 'total': 0}

        total_loaded = sum(r.distance_loaded for r in self.records)
        total_empty = sum(r.distance_empty for r in self.records)
        n_tasks = len(self.records)

        return {
            'loaded': total_loaded / n_tasks,
            'empty': total_empty / n_tasks,
            'total': (total_loaded + total_empty) / n_tasks
        }

    def empty_travel_ratio(self) -> float:
        """Calculate ratio of empty travel to total travel."""
        total_loaded = sum(r.distance_loaded for r in self.records)
        total_empty = sum(r.distance_empty for r in self.records)
        total = total_loaded + total_empty
        return total_empty / total if total > 0 else 0

    def travel_efficiency(self) -> float:
        """Calculate overall travel efficiency (direct vs actual)."""
        total_direct = sum(r.direct_distance for r in self.records)
        total_actual = sum(r.actual_distance for r in self.records)
        return total_direct / total_actual if total_actual > 0 else 0

    def distance_by_agv(self) -> Dict[str, float]:
        """Calculate total distance traveled by each AGV."""
        distances = {}
        for record in self.records:
            if record.agv_id not in distances:
                distances[record.agv_id] = 0
            distances[record.agv_id] += record.actual_distance
        return distances

    def workload_balance(self) -> Dict[str, float]:
        """Calculate workload distribution across AGVs."""
        distances = self.distance_by_agv()
        if not distances:
            return {'mean': 0, 'std': 0, 'cv': 0, 'max_min_ratio': 0}

        values = list(distances.values())
        mean_dist = np.mean(values)
        std_dist = np.std(values)

        return {
            'mean': mean_dist,
            'std': std_dist,
            'cv': std_dist / mean_dist if mean_dist > 0 else 0,  # Coefficient of variation
            'max_min_ratio': max(values) / min(values) if min(values) > 0 else float('inf')
        }
```

---

## 4. Conflict and Wait Time Metrics

### 4.1 Conflict Frequency

```
Conflict_rate = N_conflicts / T_period
Conflicts_per_task = N_conflicts / N_tasks
```

**Conflict Types:**

| Type | Description | Severity |
|------|-------------|----------|
| Head-on | AGVs approaching each other | High |
| Intersection | Multiple AGVs at junction | Medium |
| Following | AGV blocked by slower AGV | Low |
| Deadlock | Circular waiting | Critical |

### 4.2 Queue Wait Time

```
W_avg = sum(t_wait_i) / N_waiting_events
W_max = max(t_wait_i)
Queue_pct = (N_tasks_queued / N_tasks_total) * 100
```

**Python Implementation:**
```python
@dataclass
class ConflictRecord:
    timestamp: float
    agv_ids: List[str]
    conflict_type: str
    location: tuple
    resolution_time: float

@dataclass
class WaitRecord:
    task_id: str
    agv_id: str
    wait_start: float
    wait_end: float
    wait_reason: str  # 'conflict', 'queue', 'charging', 'blocked'

class ConflictMetrics:
    """Calculate conflict and congestion metrics."""

    def __init__(self, conflicts: List[ConflictRecord], waits: List[WaitRecord]):
        self.conflicts = conflicts
        self.waits = waits

    def conflict_frequency(self, period_hours: float) -> float:
        """Calculate conflicts per hour."""
        return len(self.conflicts) / period_hours if period_hours > 0 else 0

    def conflicts_per_task(self, total_tasks: int) -> float:
        """Calculate average conflicts per task."""
        return len(self.conflicts) / total_tasks if total_tasks > 0 else 0

    def conflict_by_type(self) -> Dict[str, int]:
        """Count conflicts by type."""
        counts = {}
        for conflict in self.conflicts:
            ctype = conflict.conflict_type
            counts[ctype] = counts.get(ctype, 0) + 1
        return counts

    def average_resolution_time(self) -> float:
        """Calculate average time to resolve conflicts."""
        if not self.conflicts:
            return 0
        return np.mean([c.resolution_time for c in self.conflicts])

    def average_wait_time(self) -> float:
        """Calculate average wait time across all events."""
        if not self.waits:
            return 0
        durations = [w.wait_end - w.wait_start for w in self.waits]
        return np.mean(durations)

    def max_wait_time(self) -> float:
        """Find maximum wait time."""
        if not self.waits:
            return 0
        durations = [w.wait_end - w.wait_start for w in self.waits]
        return max(durations)

    def wait_time_by_reason(self) -> Dict[str, Dict]:
        """Analyze wait times by reason."""
        reasons = {}
        for wait in self.waits:
            if wait.wait_reason not in reasons:
                reasons[wait.wait_reason] = []
            reasons[wait.wait_reason].append(wait.wait_end - wait.wait_start)

        return {
            reason: {
                'count': len(times),
                'mean': np.mean(times),
                'max': max(times),
                'total': sum(times)
            }
            for reason, times in reasons.items()
        }

    def congestion_hotspots(self, top_n: int = 5) -> List[Dict]:
        """Identify locations with most conflicts."""
        locations = {}
        for conflict in self.conflicts:
            loc = conflict.location
            if loc not in locations:
                locations[loc] = 0
            locations[loc] += 1

        sorted_locs = sorted(locations.items(), key=lambda x: x[1], reverse=True)
        return [
            {'location': loc, 'conflict_count': count}
            for loc, count in sorted_locs[:top_n]
        ]
```

---

## 5. Summary KPI Dashboard

### 5.1 Executive Summary Metrics

| KPI | Formula | Target | Warning | Critical |
|-----|---------|--------|---------|----------|
| Task Throughput | tasks/hour | >50 | 30-50 | <30 |
| Fleet Utilization | T_active/T_total | >75% | 50-75% | <50% |
| Avg Task Time | T_total/N_tasks | <300s | 300-600s | >600s |
| On-Time Rate | N_ontime/N_total | >95% | 85-95% | <85% |
| Empty Travel % | D_empty/D_total | <25% | 25-40% | >40% |
| Conflict Rate | conflicts/hour | <5 | 5-15 | >15 |
| Avg Wait Time | T_wait_avg | <30s | 30-60s | >60s |
| Battery Efficiency | tasks/charge | >20 | 10-20 | <10 |

### 5.2 Python KPI Dashboard

```python
class KPIDashboard:
    """Comprehensive KPI calculation and reporting."""

    def __init__(
        self,
        throughput_metrics: ThroughputMetrics,
        utilization_metrics: UtilizationMetrics,
        distance_metrics: DistanceMetrics,
        conflict_metrics: ConflictMetrics
    ):
        self.throughput = throughput_metrics
        self.utilization = utilization_metrics
        self.distance = distance_metrics
        self.conflicts = conflict_metrics

    def generate_summary(self, period_hours: float, total_tasks: int) -> Dict:
        """Generate comprehensive KPI summary."""
        return {
            'throughput': {
                'hourly': self.throughput.hourly_throughput(0, period_hours * 3600),
                'peak': self.throughput.peak_throughput(),
                'sustained': self.throughput.sustained_throughput()
            },
            'utilization': {
                'productive': self.utilization.productive_utilization(),
                'operational': self.utilization.operational_utilization(),
                'idle_pct': self.utilization.idle_percentage()
            },
            'distance': {
                'avg_per_task': self.distance.average_distance_per_task(),
                'empty_ratio': self.distance.empty_travel_ratio(),
                'efficiency': self.distance.travel_efficiency(),
                'workload_balance': self.distance.workload_balance()
            },
            'conflicts': {
                'frequency': self.conflicts.conflict_frequency(period_hours),
                'per_task': self.conflicts.conflicts_per_task(total_tasks),
                'by_type': self.conflicts.conflict_by_type(),
                'avg_wait': self.conflicts.average_wait_time(),
                'max_wait': self.conflicts.max_wait_time(),
                'hotspots': self.conflicts.congestion_hotspots()
            }
        }

    def evaluate_performance(self, summary: Dict) -> Dict[str, str]:
        """Evaluate KPIs against thresholds."""
        evaluations = {}

        # Throughput evaluation
        hourly = summary['throughput']['hourly']
        if hourly >= 50:
            evaluations['throughput'] = 'GOOD'
        elif hourly >= 30:
            evaluations['throughput'] = 'WARNING'
        else:
            evaluations['throughput'] = 'CRITICAL'

        # Utilization evaluation
        util = summary['utilization']['productive']
        if util >= 0.75:
            evaluations['utilization'] = 'GOOD'
        elif util >= 0.50:
            evaluations['utilization'] = 'WARNING'
        else:
            evaluations['utilization'] = 'CRITICAL'

        # Empty travel evaluation
        empty = summary['distance']['empty_ratio']
        if empty <= 0.25:
            evaluations['empty_travel'] = 'GOOD'
        elif empty <= 0.40:
            evaluations['empty_travel'] = 'WARNING'
        else:
            evaluations['empty_travel'] = 'CRITICAL'

        # Conflict evaluation
        conflict_rate = summary['conflicts']['frequency']
        if conflict_rate <= 5:
            evaluations['conflicts'] = 'GOOD'
        elif conflict_rate <= 15:
            evaluations['conflicts'] = 'WARNING'
        else:
            evaluations['conflicts'] = 'CRITICAL'

        return evaluations
```

---

## 6. Excel Formulas for Metrics

### Throughput
```excel
=COUNTIF(CompletionTimes, "<="&EndTime) / (EndTime/3600)
```

### Utilization
```excel
=SUMIF(StateLog, "active", DurationCol) / SUM(DurationCol)
```

### Idle Percentage
```excel
=(SUMIFS(Duration, State, "idle") + SUMIFS(Duration, State, "waiting")) / SUM(Duration) * 100
```

### Conflict Rate
```excel
=COUNTIF(EventType, "conflict") / (TotalHours)
```

### Average Wait Time
```excel
=AVERAGEIF(WaitReason, "<>", WaitDuration)
```
