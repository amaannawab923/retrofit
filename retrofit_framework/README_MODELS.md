# Data Models and Layout A - Quick Start Guide

## Overview

This guide provides a quick start for using the Pydantic v2 data models and the pre-configured Layout A warehouse in the retrofit framework.

## Quick Start

### 1. Import the Models

```python
from models import (
    Node, Edge, Zone,
    ZoneType, NodeType,
    LegacyWarehouse, RoboticWarehouse,
    AGVConfig, SimulationParams
)
from data import create_layout_a_warehouse, LAYOUT_A_CONFIG
```

### 2. Use Layout A

```python
# Create the pre-configured warehouse
warehouse = create_layout_a_warehouse()

print(f"Warehouse: {warehouse.name}")
print(f"Dimensions: {warehouse.width}m x {warehouse.length}m")
print(f"Total area: {warehouse.total_area} sq.m")
print(f"Zones: {len(warehouse.zones)}")
print(f"Nodes: {len(warehouse.nodes)}")
print(f"Edges: {len(warehouse.edges)}")
```

### 3. Access Warehouse Components

```python
# Get specific node
pickup_node = warehouse.get_node("node_pickup")
print(f"Pickup at: ({pickup_node.x}, {pickup_node.y})")

# Get nodes by type
from models import NodeType
entry_nodes = warehouse.get_nodes_by_type(NodeType.AISLE_ENTRY)
print(f"Aisle entries: {len(entry_nodes)}")

# Iterate over zones
for zone in warehouse.zones:
    print(f"{zone.name}: {zone.width}m x {zone.height}m")
```

## Layout A Specifications

### Dimensions
- **Total Size:** 20m width x 60m length (1,200 sq.m)
- **Aisles:** 5 parallel aisles
- **Aisle Size:** 3m wide x 50m long each
- **Pickup Zone:** 5m x 5m (bottom-left corner at 0,0)
- **Drop Zone:** 5m x 5m (top-right corner at 15,55)

### Navigation Network
- **Nodes:** 17 total
  - 1 pickup node
  - 1 drop node
  - 5 aisle entry nodes
  - 5 aisle exit nodes
  - 5 waypoint nodes (aisle midpoints)

- **Edges:** 22 total (all bidirectional)
  - Vertical: Within each aisle
  - Horizontal: Cross-aisle connections at entry, mid, and exit levels
  - Total network distance: ~335 meters

## File Locations

All files are in: `/Users/amaannawab/muzammil_layout/retrofit_framework/`

### Core Model Files
- `models/__init__.py` - Model package exports
- `models/warehouse.py` - Warehouse, Zone, Node, Edge models
- `models/agv.py` - AGV and simulation models

### Data Files
- `data/__init__.py` - Data package exports
- `data/layout_a.py` - Layout A configuration

### Test and Example Files
- `test_layout_a.py` - Test script
- `visualize_layout.py` - ASCII visualization
- `examples.py` - Usage examples

### Documentation
- `DATA_MODELS.md` - Complete model documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `README_MODELS.md` - This quick start guide

## Example Scripts

### Run Tests
```bash
cd /Users/amaannawab/muzammil_layout/retrofit_framework
python test_layout_a.py
```

### Run Visualization
```bash
python visualize_layout.py
```

### Run Examples
```bash
python examples.py
```

### Test Layout A Directly
```bash
python -m data.layout_a
```

## Common Use Cases

### 1. Export to JSON

```python
import json
from data import create_layout_a_warehouse

warehouse = create_layout_a_warehouse()

# Export to JSON
warehouse_json = warehouse.model_dump_json(indent=2)

# Save to file
with open("layout_a.json", "w") as f:
    f.write(warehouse_json)
```

### 2. Load from JSON

```python
import json
from models import LegacyWarehouse

# Load from file
with open("layout_a.json", "r") as f:
    data = json.load(f)

# Create warehouse
warehouse = LegacyWarehouse(**data)
```

### 3. Convert to Robotic Warehouse

```python
from models import RoboticWarehouse, Node, NodeType, ZoneType
from data import create_layout_a_warehouse

# Start with legacy
legacy = create_layout_a_warehouse()

# Add charging stations
charging_stations = [
    Node(
        id="charging_1",
        x=2.0, y=2.0,
        zone_type=ZoneType.CHARGING,
        node_type=NodeType.CHARGING
    )
]

# Build navigation graph
nav_graph = {}
for edge in legacy.edges:
    if edge.from_node not in nav_graph:
        nav_graph[edge.from_node] = []
    nav_graph[edge.from_node].append(edge.to_node)

    if edge.bidirectional:
        if edge.to_node not in nav_graph:
            nav_graph[edge.to_node] = []
        nav_graph[edge.to_node].append(edge.from_node)

# Create robotic warehouse
robotic = RoboticWarehouse(
    **legacy.model_dump(),
    charging_stations=charging_stations,
    navigation_graph=nav_graph
)
```

### 4. Configure AGV Fleet

```python
from models import AGVConfig, SimulationParams

# Configure AGVs
agv_config = AGVConfig(
    count=5,
    speed=2.0,              # m/s
    turn_delay=1.0,         # seconds
    width=1.0,              # meters
    length=1.5,             # meters
    battery_capacity=1000.0 # Wh
)

# Configure simulation
sim_params = SimulationParams(
    agv_config=agv_config,
    task_rate=10.0,         # tasks/min
    pick_time=5.0,          # seconds
    drop_time=5.0,          # seconds
    simulation_duration=3600.0  # seconds
)
```

### 5. Create Custom Components

```python
from models import Zone, Node, Edge, ZoneType, NodeType

# Create a zone
zone = Zone(
    id="zone_custom_1",
    name="Custom Storage",
    x=10.0, y=20.0,
    width=5.0, height=10.0,
    zone_type=ZoneType.STORAGE
)

# Create nodes
node1 = Node(
    id="node_1",
    x=10.0, y=20.0,
    zone_type=ZoneType.STORAGE,
    node_type=NodeType.WAYPOINT
)

node2 = Node(
    id="node_2",
    x=15.0, y=20.0,
    zone_type=ZoneType.STORAGE,
    node_type=NodeType.WAYPOINT
)

# Create edge
distance = node1.distance_to(node2)
edge = Edge(
    id="edge_1",
    from_node="node_1",
    to_node="node_2",
    distance=distance,
    bidirectional=True
)
```

## Model Features

### Pydantic v2 Validation
- Automatic type checking
- Field validation (ranges, constraints)
- Unique ID enforcement
- Custom business logic validation

### Type Safety
- Full type hints (Python 3.12+ compatible)
- Enum-based type systems
- Modern list/dict syntax

### Properties
- `total_area` - Total warehouse area
- `storage_area` - Storage space
- `num_nodes` - Node count
- `num_edges` - Edge count

### Methods
- `get_node(id)` - Find node by ID
- `get_nodes_by_type(type)` - Filter nodes
- `distance_to(node)` - Calculate distance

## Available Enums

### ZoneType
- `PICKUP` - Pickup/staging area
- `DROP` - Drop-off area
- `STORAGE` - Storage area
- `CHARGING` - Charging stations
- `AISLE` - Storage aisles
- `CROSSOVER` - Cross-aisles

### NodeType
- `PICKUP` - Pickup point
- `DROP` - Drop point
- `INTERSECTION` - Path intersection
- `AISLE_ENTRY` - Aisle entrance
- `AISLE_EXIT` - Aisle exit
- `CHARGING` - Charging station
- `WAYPOINT` - Navigation waypoint
- `STAGING` - Staging area
- `MAINTENANCE` - Maintenance area

## Validation Rules

### Coordinates
- Must be non-negative (>= 0)
- Type: float

### Dimensions
- Must be positive (> 0)
- Applies to: width, height, distance
- Type: float

### IDs
- Must be unique within collection
- Enforced for: zones, nodes, edges
- Type: string

### Counts
- Must be positive (> 0)
- Applies to: aisles, AGV count
- Type: int

## Tips and Best Practices

1. **Always use the factory function** for Layout A:
   ```python
   warehouse = create_layout_a_warehouse()
   ```

2. **Access the config dict** for layout parameters:
   ```python
   aisle_count = LAYOUT_A_CONFIG['aisles']
   ```

3. **Use type hints** for better IDE support:
   ```python
   def process_warehouse(warehouse: LegacyWarehouse) -> None:
       ...
   ```

4. **Validate with Pydantic** by letting exceptions propagate:
   ```python
   try:
       node = Node(id="n1", x=-5, y=10, ...)  # Will raise error
   except ValidationError as e:
       print(f"Validation failed: {e}")
   ```

5. **Use model_dump()** for serialization:
   ```python
   # To dict
   data = warehouse.model_dump()

   # To JSON
   json_str = warehouse.model_dump_json(indent=2)
   ```

6. **Chain operations** with method returns:
   ```python
   pickup = warehouse.get_node("node_pickup")
   if pickup:
       distance = pickup.distance_to(drop_node)
   ```

## Support and Documentation

- **Full API Docs:** See `DATA_MODELS.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Example Code:** See `examples.py`
- **Visual Guide:** Run `visualize_layout.py`

## Next Steps

1. Run the test script to verify everything works
2. Explore the examples to understand usage patterns
3. Read the full documentation for advanced features
4. Create your own custom layouts or extend existing ones

---

**Working Directory:** `/Users/amaannawab/muzammil_layout/retrofit_framework/`

All models are production-ready and follow modern Python 3.12+ best practices with Pydantic v2 validation.
