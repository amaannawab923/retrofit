# Warehouse Retrofit Framework - Demo Script

This document provides a step-by-step guide for demonstrating the Warehouse Retrofit Framework to colleagues or stakeholders.

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

### What each field means:

| Field | Value | Explanation |
|-------|-------|-------------|
| `total_nodes` | 17 | Navigation points created for robots (intersections, docks, waypoints) |
| `total_edges` | 24 | Pathways connecting the nodes (robot travel routes) |
| `charging_stations_count` | 3 | Number of charging stations placed |
| `feasibility_score` | 8.0/10 | How suitable the warehouse is for robotic retrofit |
| `aisle_width_adequate` | true | 3m aisles are wide enough for robots (minimum 3m required) |
| `recommendations` | list | AI-generated suggestions for the retrofit |

### Key Insight:
A feasibility score of **8.0/10** indicates this warehouse is **highly suitable** for robotic retrofit with minimal modifications needed.

---

## Step 4: Charging Stations

### Command:
```bash
make api-charging
```

### What it does:
Shows the strategically placed charging station locations.

### Expected Output:
```json
[
  { "x": 1.5, "y": 8.0 },
  { "x": 1.5, "y": 30.0 },
  { "x": 18.5, "y": 52.0 }
]
```

### What this conveys:

| Station | Location | Strategic Purpose |
|---------|----------|-------------------|
| Station 1 | (1.5, 8.0) | Near pickup zone - robots can charge while waiting for tasks |
| Station 2 | (1.5, 30.0) | Middle of warehouse - mid-route charging opportunity |
| Station 3 | (18.5, 52.0) | Near drop zone - charge after completing deliveries |

### Placement Strategy:
- Stations are distributed to **minimize robot downtime**
- Located at **low-traffic areas** to avoid blocking
- Cover all regions of the warehouse for **maximum accessibility**

---

## Step 5: Traffic Rules

### Command:
```bash
make api-traffic
```

### What it does:
Shows the traffic management rules for robot navigation.

### Expected Output:
```json
{
  "one_way_aisles": [
    { "aisle": "one_way_aisle_1", "direction": "forward", "description": "Aisle 1: northbound traffic only" },
    { "aisle": "one_way_aisle_2", "direction": "forward", "description": "Aisle 2: southbound traffic only" },
    { "aisle": "one_way_aisle_3", "direction": "forward", "description": "Aisle 3: northbound traffic only" },
    { "aisle": "one_way_aisle_4", "direction": "forward", "description": "Aisle 4: southbound traffic only" },
    { "aisle": "one_way_aisle_5", "direction": "forward", "description": "Aisle 5: northbound traffic only" }
  ],
  "priority_zones": [
    { "name": "pickup_zone", "x": 0.0, "y": 0.0, "width": 5.0, "height": 5.0, "priority": "high" },
    { "name": "drop_zone", "x": 15.0, "y": 55.0, "width": 5.0, "height": 5.0, "priority": "high" }
  ],
  "no_stopping_zones": [
    { "x": 2.5, "y": 5.0, "width": 15.0, "height": 2.0 },
    { "x": 2.5, "y": 53.0, "width": 15.0, "height": 2.0 }
  ]
}
```

### What each rule type means:

#### One-Way Aisles
| Aisle | Direction | Purpose |
|-------|-----------|---------|
| Aisle 1 | Northbound ↑ | Prevents head-on collisions |
| Aisle 2 | Southbound ↓ | Alternating pattern for flow |
| Aisle 3 | Northbound ↑ | Robots always know which way to go |
| Aisle 4 | Southbound ↓ | Reduces traffic conflicts |
| Aisle 5 | Northbound ↑ | Efficient circulation pattern |

#### Priority Zones
- **Pickup Zone** (High Priority): Robots loading items get priority
- **Drop Zone** (High Priority): Robots unloading get priority
- Other robots must yield in these areas

#### No-Stopping Zones
- **Entry corridor** (y=5.0): Intersection where aisles begin - no stopping allowed
- **Exit corridor** (y=53.0): Intersection where aisles end - no stopping allowed
- These prevent **bottlenecks** at critical intersections

---

## Step 6: ASCII Layout Visualization

### Command:
```bash
make viz-ascii
```

### What it does:
Generates a text-based visual representation of the warehouse layout in the terminal.

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

### What this conveys:
- Visual representation of the **physical warehouse layout**
- Shows all **17 navigation nodes** and their positions
- Displays the **5 parallel aisles** running north-south
- Shows **pickup zone** (bottom-left) and **drop zone** (top-right)

---

## Step 7: Generate Visualization Images

### Command:
```bash
make viz-images
```

### What it does:
Generates three PNG images showing the warehouse before and after retrofit.

### Where images are stored:
```
retrofit_framework/output/images/
├── layout_a_before.png      # Legacy warehouse (before retrofit)
├── layout_a_after.png       # Robotic warehouse (after retrofit)
└── layout_a_comparison.png  # Side-by-side comparison
```

### Image Descriptions:

#### 1. layout_a_before.png (~106 KB)
**Shows:** Original legacy warehouse layout
- Warehouse dimensions and zones
- Aisle positions
- Basic structure without robotic infrastructure

#### 2. layout_a_after.png (~175 KB)
**Shows:** Retrofitted robotic warehouse
- All 17 navigation nodes plotted
- 24 edges (pathways) connecting nodes
- 3 charging stations marked
- Traffic flow indicators

#### 3. layout_a_comparison.png (~207 KB)
**Shows:** Side-by-side before/after comparison
- Left panel: Legacy warehouse
- Right panel: Robotic warehouse
- Visual demonstration of the transformation

### How to open images:
```bash
# macOS
open retrofit_framework/output/images/layout_a_comparison.png

# Linux
xdg-open retrofit_framework/output/images/layout_a_comparison.png

# Windows
start retrofit_framework/output/images/layout_a_comparison.png
```

---

## Step 8: Save Full Conversion Data

### Command:
```bash
make api-save
```

### What it does:
Saves the complete conversion response to a JSON file.

### Where it's saved:
```
output/conversion_result.json
```

### File Contents:
- Complete original warehouse specification
- Complete robotic warehouse specification
- Full navigation graph (all 17 nodes, 24 edges)
- Distance matrix (17x17 = 289 distance values)
- All traffic rules
- Conversion summary

### Use Cases:
- Import into simulation software
- Feed into robot fleet management systems
- Documentation and record-keeping
- Further analysis and optimization

---

## Complete Demo Flow (Single Command)

### Command:
```bash
make demo
```

### This runs all steps automatically:
1. ✓ API health check
2. ✓ Conversion summary
3. ✓ Charging stations
4. ✓ Traffic rules
5. ✓ ASCII layout
6. ✓ PNG image generation
7. ✓ Save to JSON

---

## Summary Table

| Step | Command | Output | Purpose |
|------|---------|--------|---------|
| 1 | (view source) | `data/layout_a.py` | Understand input data |
| 2 | `make api-test` | HTTP status codes | Verify server health |
| 3 | `make api-summary` | JSON summary | Key retrofit metrics |
| 4 | `make api-charging` | Coordinates | Charging station placement |
| 5 | `make api-traffic` | Rules JSON | Traffic management |
| 6 | `make viz-ascii` | Terminal art | Visual warehouse layout |
| 7 | `make viz-images` | PNG files | Professional visualizations |
| 8 | `make api-save` | JSON file | Complete data export |

---

## Key Talking Points for Demo

1. **Input**: A traditional 5-aisle warehouse (20m x 60m)
2. **Process**: API-based conversion using Floyd-Warshall algorithm for distance calculations
3. **Output**: Complete robotic warehouse specification with:
   - 17 navigation nodes
   - 24 pathways
   - 3 strategically placed charging stations
   - Traffic rules to prevent collisions
4. **Feasibility**: Score of 8.0/10 - highly suitable for retrofit
5. **Deliverables**: JSON data + PNG visualizations ready for implementation

---

## Files Referenced in This Demo

| File | Description |
|------|-------------|
| `retrofit_framework/data/layout_a.py` | Source warehouse configuration |
| `retrofit_framework/core/converter.py` | Retrofit conversion logic |
| `retrofit_framework/api/routes.py` | API endpoint definitions |
| `retrofit_framework/output/images/*.png` | Generated visualization images |
| `output/conversion_result.json` | Full conversion data export |
| `Makefile` | All demo commands |

---

## Swagger Documentation

For interactive API exploration, open in browser:
```
http://localhost:8000/docs
```

This provides a web UI to:
- View all API endpoints
- Test API calls directly
- See request/response schemas
