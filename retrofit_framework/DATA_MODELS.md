# Data Models Documentation

This document describes the data models and pre-configured layouts for the retrofit framework.

## Table of Contents

1. [Warehouse Models](#warehouse-models)
2. [AGV Models](#agv-models)
3. [Layout A Configuration](#layout-a-configuration)
4. [Usage Examples](#usage-examples)

---

## Warehouse Models

Located in `/Users/amaannawab/muzammil_layout/retrofit_framework/models/warehouse.py`

### Core Components

#### `ZoneType` (Enum)
Defines the types of zones in a warehouse:
- `PICKUP` - Pickup/staging zone
- `DROP` - Drop-off zone
- `STORAGE` - Storage area
- `CHARGING` - AGV charging station area
- `AISLE` - Storage aisle
- `CROSSOVER` - Cross-aisle for navigation

#### `NodeType` (Enum)
Defines the types of navigation nodes:
- `PICKUP` - Pickup point
- `DROP` - Drop-off point
- `INTERSECTION` - Path intersection
- `AISLE_ENTRY` - Aisle entrance
- `AISLE_EXIT` - Aisle exit
- `CHARGING` - Charging station
- `WAYPOINT` - Navigation waypoint
- `STAGING` - Staging area
- `MAINTENANCE` - Maintenance area

#### `Node` (Pydantic Model)
Represents a navigation node in the warehouse.

**Fields:**
- `id: str` - Unique identifier
- `x: float` - X coordinate in meters (non-negative)
- `y: float` - Y coordinate in meters (non-negative)
- `zone_type: ZoneType` - Type of zone this node belongs to
- `node_type: NodeType` - Type of node for navigation

**Methods:**
- `distance_to(other: Node) -> float` - Calculate Euclidean distance to another node

#### `Edge` (Pydantic Model)
Represents a connection between two nodes.

**Fields:**
- `id: str` - Unique identifier
- `from_node: str` - Source node ID
- `to_node: str` - Destination node ID
- `distance: float` - Distance in meters (must be > 0)
- `bidirectional: bool` - Whether edge can be traversed both ways (default: True)

#### `Zone` (Pydantic Model)
Represents a physical zone in the warehouse.

**Fields:**
- `id: str` - Unique identifier
- `name: str` - Human-readable name
- `x: float` - X coordinate of origin (bottom-left, non-negative)
- `y: float` - Y coordinate of origin (bottom-left, non-negative)
- `width: float` - Width in meters (must be > 0)
- `height: float` - Height in meters (must be > 0)
- `zone_type: ZoneType` - Type of zone

#### `LegacyWarehouse` (Pydantic Model)
Represents a traditional warehouse layout.

**Fields:**
- `name: str` - Warehouse name
- `width: float` - Total width in meters (must be > 0)
- `length: float` - Total length in meters (must be > 0)
- `aisles: int` - Number of aisles (must be > 0)
- `aisle_width: float` - Width of each aisle in meters (must be > 0)
- `aisle_length: float` - Length of each aisle in meters (must be > 0)
- `zones: list[Zone]` - List of zones (default: empty list)
- `nodes: list[Node]` - List of navigation nodes (default: empty list)
- `edges: list[Edge]` - List of edges (default: empty list)

**Properties:**
- `total_area: float` - Total warehouse floor area in square meters
- `storage_area: float` - Approximate storage area in square meters

**Methods:**
- `get_node(node_id: str) -> Optional[Node]` - Get node by ID
- `get_nodes_by_type(node_type: NodeType) -> list[Node]` - Get all nodes of a specific type

**Validators:**
- Ensures all zone IDs are unique
- Ensures all node IDs are unique
- Ensures all edge IDs are unique

#### `TrafficRule` (Pydantic Model)
Represents a traffic rule for AGV navigation.

**Fields:**
- `rule_id: str` - Unique identifier
- `rule_type: str` - Type of rule (e.g., "one_way", "priority")
- `applies_to: list[str]` - List of edge IDs this rule applies to
- `description: Optional[str]` - Human-readable description

#### `RoboticWarehouse` (Pydantic Model)
Extends `LegacyWarehouse` with robotic system features.

**Additional Fields:**
- `charging_stations: list[Node]` - List of charging station nodes
- `navigation_graph: dict[str, list[str]]` - Adjacency list for navigation
- `distance_matrix: dict[str, dict[str, float]]` - Pre-computed distances
- `traffic_rules: list[TrafficRule]` - Traffic rules for AGV navigation

**Additional Properties:**
- `num_nodes: int` - Total number of navigation nodes
- `num_edges: int` - Total number of edges

**Validators:**
- Ensures charging stations have `node_type='charging'`

---

## AGV Models

Located in `/Users/amaannawab/muzammil_layout/retrofit_framework/models/agv.py`

#### `AGVConfig` (Pydantic Model)
Configuration for AGV fleet.

**Fields:**
- `count: int` - Number of AGVs (must be > 0)
- `speed: float` - Maximum speed in m/s (must be > 0)
- `turn_delay: float` - Turn delay in seconds (must be >= 0)
- `width: float` - AGV width in meters (must be > 0)
- `length: float` - AGV length in meters (must be > 0)
- `battery_capacity: float` - Battery capacity in watt-hours (must be > 0)

#### `SimulationParams` (Pydantic Model)
Parameters for warehouse simulation.

**Fields:**
- `agv_config: AGVConfig` - AGV fleet configuration
- `task_rate: float` - Task generation rate (tasks/min, must be > 0)
- `pick_time: float` - Pick-up time in seconds (must be > 0)
- `drop_time: float` - Drop-off time in seconds (must be > 0)
- `simulation_duration: float` - Total duration in seconds (must be > 0)

---

## Layout A Configuration

Located in `/Users/amaannawab/muzammil_layout/retrofit_framework/data/layout_a.py`

### Specifications

```python
LAYOUT_A_CONFIG = {
    "name": "Layout A - Traditional 5-Aisle Warehouse",
    "width": 20.0,          # meters
    "length": 60.0,         # meters
    "aisles": 5,
    "aisle_width": 3.0,     # meters
    "aisle_length": 50.0,   # meters
    "pickup_zone": {
        "x": 0.0,
        "y": 0.0,
        "width": 5.0,
        "height": 5.0,
    },
    "drop_zone": {
        "x": 15.0,
        "y": 55.0,
        "width": 5.0,
        "height": 5.0,
    },
}
```

### Layout Description

**Layout A** is a traditional warehouse with:
- **5 parallel aisles** for storage
- **Pickup zone** (5m x 5m) in bottom-left corner
- **Drop zone** (5m x 5m) in top-right corner
- **Total dimensions:** 20m width x 60m length
- **Aisle configuration:** Each aisle is 3m wide and 50m long

### Node Network

The layout includes:
- **2 zone nodes** (pickup and drop)
- **15 aisle nodes** (entry, midpoint, exit for each of 5 aisles)
- **Total: 17 nodes**

### Edge Network

The navigation graph includes:
- Vertical edges within each aisle (entry-mid-exit)
- Horizontal edges between adjacent aisles at three levels (entry, mid, exit)
- Connections from pickup zone to first aisle
- Connections from last aisle to drop zone
- **All edges are bidirectional**

### Creating Layout A

```python
from data.layout_a import create_layout_a_warehouse

# Create the warehouse object
warehouse = create_layout_a_warehouse()

# Access warehouse properties
print(f"Name: {warehouse.name}")
print(f"Dimensions: {warehouse.width}m x {warehouse.length}m")
print(f"Total area: {warehouse.total_area} sq.m")
print(f"Zones: {len(warehouse.zones)}")
print(f"Nodes: {len(warehouse.nodes)}")
print(f"Edges: {len(warehouse.edges)}")
```

---

## Usage Examples

### Example 1: Create and Validate Layout A

```python
from data.layout_a import create_layout_a_warehouse
from models import NodeType

# Create warehouse
warehouse = create_layout_a_warehouse()

# Get all pickup nodes
pickup_nodes = warehouse.get_nodes_by_type(NodeType.PICKUP)
print(f"Found {len(pickup_nodes)} pickup nodes")

# Get specific node
node = warehouse.get_node("node_pickup")
if node:
    print(f"Pickup node at: ({node.x}, {node.y})")
```

### Example 2: Create Custom Zone

```python
from models import Zone, ZoneType

zone = Zone(
    id="zone_custom_1",
    name="Custom Storage Zone",
    x=10.0,
    y=20.0,
    width=5.0,
    height=8.0,
    zone_type=ZoneType.STORAGE
)
```

### Example 3: Create Navigation Graph

```python
from models import Node, Edge, NodeType, ZoneType

# Create nodes
node1 = Node(
    id="node_1",
    x=0.0,
    y=0.0,
    zone_type=ZoneType.AISLE,
    node_type=NodeType.WAYPOINT
)

node2 = Node(
    id="node_2",
    x=10.0,
    y=0.0,
    zone_type=ZoneType.AISLE,
    node_type=NodeType.WAYPOINT
)

# Create edge
edge = Edge(
    id="edge_1",
    from_node="node_1",
    to_node="node_2",
    distance=10.0,
    bidirectional=True
)

# Calculate distance
distance = node1.distance_to(node2)
print(f"Distance: {distance:.2f}m")
```

### Example 4: Create AGV Configuration

```python
from models import AGVConfig, SimulationParams

# Configure AGV fleet
agv_config = AGVConfig(
    count=5,
    speed=2.0,              # m/s
    turn_delay=1.0,         # seconds
    width=1.0,              # meters
    length=1.5,             # meters
    battery_capacity=1000.0 # watt-hours
)

# Configure simulation
sim_params = SimulationParams(
    agv_config=agv_config,
    task_rate=10.0,         # tasks/min
    pick_time=5.0,          # seconds
    drop_time=5.0,          # seconds
    simulation_duration=3600.0  # 1 hour
)
```

### Example 5: Create Robotic Warehouse

```python
from models import RoboticWarehouse, Node, NodeType, ZoneType
from data.layout_a import create_layout_a_warehouse

# Start with legacy warehouse
legacy = create_layout_a_warehouse()

# Convert to robotic warehouse
robotic = RoboticWarehouse(
    **legacy.model_dump(),
    charging_stations=[
        Node(
            id="charging_1",
            x=2.0,
            y=2.0,
            zone_type=ZoneType.CHARGING,
            node_type=NodeType.CHARGING
        )
    ]
)

print(f"Robotic warehouse with {robotic.num_nodes} nodes")
```

### Example 6: Export to JSON

```python
from data.layout_a import create_layout_a_warehouse
import json

warehouse = create_layout_a_warehouse()

# Export to JSON
warehouse_json = warehouse.model_dump_json(indent=2)
print(warehouse_json)

# Save to file
with open("layout_a.json", "w") as f:
    f.write(warehouse_json)
```

### Example 7: Load from JSON

```python
from models import LegacyWarehouse
import json

# Load from file
with open("layout_a.json", "r") as f:
    warehouse_data = json.load(f)

# Create warehouse from JSON data
warehouse = LegacyWarehouse(**warehouse_data)
print(f"Loaded warehouse: {warehouse.name}")
```

---

## File Structure

```
retrofit_framework/
├── models/
│   ├── __init__.py           # Package exports
│   ├── warehouse.py          # Warehouse data models
│   ├── agv.py               # AGV and simulation models
│   └── nodes.py             # Legacy node models (deprecated)
├── data/
│   ├── __init__.py          # Package exports
│   └── layout_a.py          # Layout A configuration
├── test_layout_a.py         # Test script for Layout A
└── DATA_MODELS.md           # This documentation
```

---

## Notes

- All models use **Pydantic v2** for data validation
- Coordinates use a **bottom-left origin** (0, 0)
- All distances are in **meters**
- All times are in **seconds**
- All models are **immutable by default** (use `model_copy()` to create modified copies)
- Models include automatic validation for:
  - Non-negative coordinates
  - Positive dimensions
  - Unique IDs
  - Valid enum values
