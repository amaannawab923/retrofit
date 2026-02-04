# Warehouse Retrofit Framework - Demo Script

This document provides a comprehensive step-by-step guide for demonstrating the Warehouse Retrofit Framework, including detailed explanations of the conversion process, mathematical formulas, and decision logic.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Source Data](#step-1-source-data---layout-a-warehouse-configuration)
3. [Step 2: API Health Check](#step-2-api-health-check)
4. [Step 3: Conversion Summary](#step-3-conversion-summary)
5. [Step 4: Charging Stations](#step-4-charging-stations)
6. [Step 5: Traffic Rules](#step-5-traffic-rules)
7. [Step 6: ASCII Layout](#step-6-ascii-layout-visualization)
8. [Step 7: Visualization Images](#step-7-generate-visualization-images)
9. [Key Talking Points](#key-talking-points-for-demo)

---

## Prerequisites

Before starting the demo, ensure:
1. Repository is cloned: `git clone https://github.com/amaannawab923/retrofit.git`
2. Dependencies installed: `make install`
3. Server running in Terminal 1: `make run`
4. Terminal 2 ready for demo commands

---

## Step 1: Source Data - Layout A Warehouse Configuration

### What is it?
The source data represents a **legacy warehouse layout** (Layout A) - a traditional 5-aisle warehouse that we want to retrofit for robotic operations.

### Where is it located?
```
retrofit_framework/data/layout_a.py
```

### Key Configuration Values:
| Parameter | Value | Description |
|-----------|-------|-------------|
| Width | 20 meters | Warehouse width |
| Length | 60 meters | Warehouse length |
| Total Area | 1,200 sq.m | Total floor space |
| Number of Aisles | 5 | Parallel storage aisles |
| Aisle Width | 3 meters | Width of each aisle |
| Aisle Length | 50 meters | Length of each aisle |

### Zones Defined:
- **Pickup Zone**: (0, 0) - 5m x 5m - Where robots pick up items
- **Drop Zone**: (15, 55) - 5m x 5m - Where robots deliver items
- **5 Aisles**: Storage aisles running north-south

### Command to view raw data:
```bash
cat retrofit_framework/data/layout_a.py
```

---

## Step 2: API Health Check

### Command:
```bash
make api-test
```

### What it does:
Verifies that the FastAPI server is running and all endpoints are responding.

### Expected Output:
```
Root: 200
Health: 200
Convert: 200
All endpoints responding!
```

### What this conveys:
- The API server is healthy and ready
- All three main endpoints are accessible
- HTTP 200 = Success

---

## Step 3: Conversion Summary

### Command:
```bash
make api-summary
```

### What it does:
Calls the conversion API and extracts the summary statistics showing what the retrofit process produced.

### Expected Output:
```json
{
  "total_nodes": 17,
  "total_edges": 24,
  "charging_stations_count": 3,
  "feasibility_score": 8.0,
  "aisle_width_adequate": true,
  "recommendations": [
    "Aisle width meets minimum requirements for robot operation",
    "Regular grid layout is ideal for autonomous navigation",
    "Total of 3 charging stations placed strategically",
    "Warehouse is highly suitable for robotic retrofit"
  ]
}
```

---

## How the Conversion Actually Works

### The 6-Step Conversion Pipeline

The `RetrofitConverter` class (`retrofit_framework/core/converter.py`) performs the conversion through these steps:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONVERSION PIPELINE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Step 1: VALIDATE WAREHOUSE                                          │
│     └── Check aisle width against minimum requirements               │
│                                                                      │
│  Step 2: BUILD NAVIGATION GRAPH                                      │
│     └── Create nodes and edges for robot pathfinding                 │
│                                                                      │
│  Step 3: COMPUTE DISTANCE MATRIX                                     │
│     └── Calculate all-pairs shortest paths (Floyd-Warshall)          │
│                                                                      │
│  Step 4: PLACE CHARGING STATIONS                                     │
│     └── Strategic placement along walls near high-traffic areas      │
│                                                                      │
│  Step 5: GENERATE TRAFFIC RULES                                      │
│     └── One-way aisles, priority zones, no-stopping zones            │
│                                                                      │
│  Step 6: CALCULATE FEASIBILITY SCORE                                 │
│     └── Multi-factor scoring (aisle width, layout, space, access)    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Mathematical Formulas Used

### 1. Distance Calculations

**File:** `retrofit_framework/core/distance_calculator.py`

#### Manhattan Distance (Grid-based movement)
Used for warehouse AGVs that move along grid lines (only horizontal and vertical):

```
d(A,B) = |x_A - x_B| + |y_A - y_B|
```

**Example:** From node (2.5, 2.5) to (8.3, 5.0):
```
d = |2.5 - 8.3| + |2.5 - 5.0| = 5.8 + 2.5 = 8.3 meters
```

#### Euclidean Distance (Straight-line)
Used for open areas where robots can move diagonally:

```
d(A,B) = √[(x_A - x_B)² + (y_A - y_B)²]
```

**Example:** From (0, 0) to (3, 4):
```
d = √[(3)² + (4)²] = √[9 + 16] = √25 = 5 meters
```

### 2. Floyd-Warshall Algorithm (All-Pairs Shortest Path)

**File:** `retrofit_framework/core/converter.py` (lines 137-189)

This algorithm computes the shortest path between ALL pairs of nodes simultaneously.

```
For each intermediate node k:
    For each source node i:
        For each destination node j:
            If dist[i][k] + dist[k][j] < dist[i][j]:
                dist[i][j] = dist[i][k] + dist[k][j]
```

**Why Floyd-Warshall?**
- Creates a complete 17×17 distance matrix (289 distances)
- O(n³) complexity, but only needs to run once
- Enables instant lookup for any route planning

**Result:** A matrix where `distance_matrix[from_node][to_node]` gives the shortest path distance.

### 3. Travel Time Calculation

**File:** `mathematical_foundations/warehouse_math_foundations.py`

```
T_travel = d/v + n_turns × t_turn + t_accel + t_decel + T_queue
```

Where:
- `d` = distance (meters)
- `v` = cruise speed (1.5 m/s default)
- `n_turns` = number of 90-degree turns
- `t_turn` = time per turn (2.0 seconds default)
- `t_accel` = acceleration time
- `t_decel` = deceleration time
- `T_queue` = queue waiting time

**Example:** 50m path with 2 turns:
```
Cruise time = 50 / 1.5 = 33.3 seconds
Turn time = 2 × 2.0 = 4.0 seconds
Total ≈ 37.3 seconds (plus accel/decel)
```

---

## How Feasibility Score is Calculated

**File:** `retrofit_framework/core/converter.py` (lines 303-372)

The feasibility score (0-10 scale) is a **weighted multi-factor assessment**:

### Scoring Formula:

```
Feasibility Score = Aisle Score + Layout Score + Space Score + Accessibility Score
```

### Factor Breakdown:

| Factor | Weight | Max Points | Calculation |
|--------|--------|------------|-------------|
| Aisle Width | 40% | 4.0 | Based on width thresholds |
| Layout Regularity | 25% | 2.5 | Grid-based = full points |
| Space Utilization | 20% | 2.0 | Optimal: 30-50% aisle coverage |
| Accessibility | 15% | 1.5 | Pickup/drop zone placement |

### Aisle Width Scoring (40% weight):

| Aisle Width | Score | Assessment |
|-------------|-------|------------|
| ≥ 3.5m (optimal) | 4.0 | Excellent - allows bidirectional traffic |
| ≥ 3.0m (minimum) | 3.0 | Good - meets robot requirements |
| ≥ 2.5m | 2.0 | Marginal - may limit speed |
| ≥ 2.0m | 1.0 | Poor - single direction only |
| < 2.0m | 0.0 | Inadequate - robots cannot operate |

### Space Utilization Scoring (20% weight):

```
Utilization = (Aisles × Aisle Width × Aisle Length) / (Warehouse Width × Length)

For Layout A:
Utilization = (5 × 3 × 50) / (20 × 60) = 750 / 1200 = 62.5%
```

| Utilization Range | Score |
|-------------------|-------|
| 30% - 50% | 2.0 (optimal balance) |
| 20% - 30% or 50% - 60% | 1.5 |
| Other | 1.0 |

### Layout A Calculation:

```
Aisle Width Score:     3.0  (3.0m ≥ minimum 3.0m)
Layout Regularity:     2.5  (regular grid layout)
Space Utilization:     1.5  (62.5% - slightly high but acceptable)
Accessibility:         1.5  (both pickup and drop zones at edges)
─────────────────────────────
TOTAL:                 8.0 / 10.0
```

---

## How "Aisle Width Adequate" is Determined

**Threshold Values:**

```python
MIN_AISLE_WIDTH = 3.0      # Minimum for robot operation
OPTIMAL_AISLE_WIDTH = 3.5  # Recommended for efficiency
```

**Logic:**
```python
aisle_width_adequate = warehouse.aisle_width >= MIN_AISLE_WIDTH
# For Layout A: 3.0 >= 3.0 → TRUE
```

**Why 3.0 meters minimum?**

The formula for unidirectional aisle width:
```
W_min = W_agv + 2 × d_safety + clearance

Where:
- W_agv = 0.8m (typical AGV width)
- d_safety = 0.5m (safety buffer on each side)
- clearance = 0.2m (sensor clearance)

W_min = 0.8 + 2(0.5) + 0.2 = 2.0m (absolute minimum)
```

**But 3.0m is recommended because:**
- Allows for slight navigation errors
- Provides room for emergency stops
- Accommodates varying AGV sizes
- Enables faster travel speeds

---

## How Recommendations are Generated

Recommendations are generated based on conditional logic evaluating the conversion results:

### Recommendation Logic:

```python
# Recommendation 1: Aisle Width Assessment
if aisle_width >= 3.0m:
    "Aisle width meets minimum requirements for robot operation"
else:
    "Consider widening aisles from {current}m to at least 3.0m"

# Recommendation 2: Layout Assessment
"Regular grid layout is ideal for autonomous navigation"

# Recommendation 3: Charging Stations
"Total of {count} charging stations placed strategically"

# Recommendation 4: Overall Feasibility
if feasibility_score >= 8.0:
    "Warehouse is highly suitable for robotic retrofit"
elif feasibility_score >= 6.0:
    "Warehouse is moderately suitable for robotic retrofit"
else:
    "Warehouse requires significant modifications for robotic operation"
```

---

## Step 4: Charging Stations

### Command:
```bash
make api-charging
```

### Expected Output:
```json
[
  { "x": 1.5, "y": 8.0 },
  { "x": 1.5, "y": 30.0 },
  { "x": 18.5, "y": 52.0 }
]
```

---

## How Charging Station Locations are Determined

**File:** `retrofit_framework/core/converter.py` (lines 191-250)

### Placement Strategy:

```
┌────────────────────────────────────────────────────────────────────┐
│                    CHARGING STATION STRATEGY                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  RULE 1: Place ALONG WALLS - never in aisle areas                   │
│     └── Avoids blocking robot traffic                               │
│                                                                     │
│  RULE 2: Distribute to MINIMIZE MAXIMUM DISTANCE                    │
│     └── No point should be too far from a charger                   │
│                                                                     │
│  RULE 3: Position near HIGH-TRAFFIC AREAS but OUT OF THE WAY        │
│     └── Near pickup/drop zones for opportunistic charging           │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Placement Algorithm:

```python
# Station 1: Left wall, near pickup zone
x = 1.5                    # Against left wall (0 + buffer)
y = 8.0                    # Just above pickup zone (0-5m)
# Purpose: Robots can charge while waiting for pickup tasks

# Station 2: Left wall, middle section
x = 1.5                    # Against left wall
y = warehouse.length / 2   # 60 / 2 = 30m (center)
# Purpose: Mid-route charging opportunity

# Station 3: Right wall, near drop zone
x = warehouse.width - 1.5  # 20 - 1.5 = 18.5m (against right wall)
y = warehouse.length - 8.0 # 60 - 8 = 52m (near drop zone at 55m)
# Purpose: Charge after completing deliveries
```

### Visual Layout:

```
    0m                              20m
    ┌────────────────────────────────┐
60m │                          [DROP]│
    │                     ⚡Station 3│ (18.5, 52)
    │    ╔════╗╔════╗╔════╗╔════╗╔════╗
    │    ║ A1 ║║ A2 ║║ A3 ║║ A4 ║║ A5 ║
30m │⚡   ║    ║║    ║║    ║║    ║║    ║ Station 2 (1.5, 30)
    │    ║    ║║    ║║    ║║    ║║    ║
    │    ╚════╝╚════╝╚════╝╚════╝╚════╝
    │⚡Station 1                      │ (1.5, 8)
 0m │[PICKUP]                         │
    └────────────────────────────────┘
```

### Battery Constraint Formula:

From Layout A research:
```
bl_k ≤ λ^r_ku ≤ bh_k

Where:
- bl_k = low battery threshold (20%)
- bh_k = high battery threshold (95%)
- λ^r_ku = battery level of robot k at time u
```

**Charging Decision Logic:**
```python
if battery_level <= low_threshold (20%):
    MUST charge before next task
elif battery_level <= 40%:
    OPPORTUNISTIC charging if passing a station
else:
    Continue operations
```

---

## Step 5: Traffic Rules

### Command:
```bash
make api-traffic
```

### Expected Output:
```json
{
  "one_way_aisles": [...],
  "priority_zones": [...],
  "no_stopping_zones": [...]
}
```

---

## How Traffic Rules are Generated

**File:** `retrofit_framework/core/converter.py` (lines 252-301)

### Rule Generation Algorithm:

```python
# One-Way Aisles: Alternating pattern for flow efficiency
for i, aisle in enumerate(aisle_zones):
    direction = "north" if i % 2 == 0 else "south"

# Result:
# Aisle 1: ↑ Northbound
# Aisle 2: ↓ Southbound
# Aisle 3: ↑ Northbound
# Aisle 4: ↓ Southbound
# Aisle 5: ↑ Northbound
```

### Traffic Rule Types:

| Rule Type | Purpose | Implementation |
|-----------|---------|----------------|
| **One-Way Aisles** | Prevent head-on collisions | Alternating N/S pattern |
| **Priority Zones** | Ensure task completion | Pickup/Drop get priority |
| **No-Stopping Zones** | Prevent bottlenecks | Entry/exit corridors |

### Why Alternating One-Way Pattern?

```
Without one-way rules:          With alternating pattern:
    ↕ ↕ ↕ ↕ ↕                      ↑ ↓ ↑ ↓ ↑
    Collisions!                    Smooth flow!
    Deadlocks!                     No conflicts!
```

---

## Step 6: ASCII Layout Visualization

### Command:
```bash
make viz-ascii
```

### What it shows:
- Physical warehouse layout in terminal
- All 17 navigation nodes with positions
- 5 parallel aisles
- Pickup zone (bottom-left) and drop zone (top-right)

### Key Symbols:
| Symbol | Meaning |
|--------|---------|
| `P` | Pickup Zone |
| `D` | Drop Zone |
| `\|` | Aisle (storage area) |
| `@` | Pickup Node |
| `#` | Drop Node |
| `▼` | Aisle Entry Point |
| `▲` | Aisle Exit Point |
| `•` | Waypoint (mid-aisle) |

---

## Step 7: Generate Visualization Images

### Command:
```bash
make viz-images
```

### Where images are stored:
```
retrofit_framework/output/images/
├── layout_a_before.png      # Legacy warehouse (before retrofit)
├── layout_a_after.png       # Robotic warehouse (after retrofit)
└── layout_a_comparison.png  # Side-by-side comparison
```

### How to open images:
```bash
# macOS
open retrofit_framework/output/images/layout_a_comparison.png

# Linux
xdg-open retrofit_framework/output/images/layout_a_comparison.png
```

---

## Summary: The Complete Conversion Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INPUT                                           │
│  Legacy Warehouse Configuration (layout_a.py)                           │
│  - Dimensions: 20m × 60m                                                │
│  - 5 aisles, 3m wide, 50m long                                          │
│  - Pickup zone, Drop zone                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      CONVERSION ENGINE                                   │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Validate   │→ │   Build     │→ │  Compute    │→ │   Place     │    │
│  │   Aisle     │  │   Graph     │  │  Distance   │  │  Charging   │    │
│  │   Width     │  │  (Nodes +   │  │   Matrix    │  │  Stations   │    │
│  │             │  │   Edges)    │  │ (Floyd-W)   │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│         │                                                    │          │
│         ▼                                                    ▼          │
│  ┌─────────────┐                                    ┌─────────────┐    │
│  │  Generate   │                                    │  Calculate  │    │
│  │  Traffic    │                                    │ Feasibility │    │
│  │   Rules     │                                    │   Score     │    │
│  └─────────────┘                                    └─────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          OUTPUT                                          │
│                                                                          │
│  ✓ 17 Navigation Nodes (pickup, drop, entries, exits, waypoints)        │
│  ✓ 24 Edges (bidirectional pathways)                                    │
│  ✓ 17×17 Distance Matrix (Floyd-Warshall)                               │
│  ✓ 3 Charging Stations (strategically placed)                           │
│  ✓ Traffic Rules (one-way aisles, priority zones)                       │
│  ✓ Feasibility Score: 8.0/10 (highly suitable)                          │
│  ✓ Recommendations (4 actionable items)                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Talking Points for Demo

1. **Input**: A traditional 5-aisle warehouse (20m × 60m, 1200 sq.m)

2. **Process**:
   - Navigation graph with 17 nodes and 24 edges
   - Floyd-Warshall algorithm for distance matrix (O(n³))
   - Multi-factor feasibility scoring

3. **Output**:
   - Complete robotic warehouse specification
   - Ready for integration with robot fleet management

4. **Feasibility**:
   - Score of 8.0/10 = highly suitable
   - Breakdown: Aisle (3.0) + Layout (2.5) + Space (1.5) + Access (1.5)

5. **Key Formulas**:
   - Distance: `d = |x₁-x₂| + |y₁-y₂|` (Manhattan)
   - Travel time: `T = d/v + turns × t_turn`
   - Feasibility: Weighted sum of 4 factors

6. **Deliverables**:
   - JSON data export
   - PNG visualizations
   - API for integration

---

## Files Referenced in This Demo

| File | Description |
|------|-------------|
| `retrofit_framework/data/layout_a.py` | Source warehouse configuration |
| `retrofit_framework/core/converter.py` | Retrofit conversion logic |
| `retrofit_framework/core/distance_calculator.py` | Distance formulas |
| `mathematical_foundations/warehouse_math_foundations.py` | All mathematical models |
| `retrofit_framework/api/routes.py` | API endpoint definitions |
| `retrofit_framework/output/images/*.png` | Generated visualization images |
| `output/conversion_result.json` | Full conversion data export |
| `Makefile` | All demo commands |

---

## Quick Reference: All Demo Commands

```bash
# Setup (one-time)
make install

# Start server (Terminal 1)
make run

# Demo commands (Terminal 2)
make api-test        # Health check
make api-summary     # Conversion summary
make api-charging    # Charging stations
make api-traffic     # Traffic rules
make viz-ascii       # ASCII layout
make viz-images      # Generate PNGs

# Or run everything at once
make demo
```

---

## Swagger Documentation

For interactive API exploration:
```
http://localhost:8000/docs
```
