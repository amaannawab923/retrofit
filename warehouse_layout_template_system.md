# Warehouse Layout Template System
## Framework for Converting Legacy Warehouses to Robot-Ready Facilities

---

## Table of Contents

1. [Zone Classification Schema](#1-zone-classification-schema)
2. [Grid Overlay System](#2-grid-overlay-system)
3. [Sample Layout Templates](#3-sample-layout-templates)
4. [Layout Conversion Checklist](#4-layout-conversion-checklist)
5. [Visual Conventions](#5-visual-conventions)
6. [ASCII Art Layout Example](#6-ascii-art-layout-example)

---

## 1. Zone Classification Schema

This section defines the standard zones required for any AGV-enabled warehouse facility. Each zone is characterized by its function, recommended dimensions, AGV accessibility requirements, and optimal node density for navigation.

### 1.1 Storage Zones

#### 1.1.1 Rack Storage Areas

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Pallet storage in multi-tier racking systems |
| **Recommended Dimensions** | Aisle width: 3.0-3.5m (standard AGV), 2.4-2.8m (narrow aisle AGV) |
| **Minimum Height Clearance** | 4.5-12m depending on rack configuration |
| **AGV Accessibility** | Requires straight approach paths, perpendicular to rack faces |
| **Node Density** | 1 node per rack bay (typically every 2.4-3.0m along aisle) |
| **Special Requirements** | Floor flatness: max 2mm deviation per meter |

**Node Placement Pattern:**
```
[RACK] [RACK] [RACK] [RACK] [RACK]
  N1     N2     N3     N4     N5    <- Nodes at each bay
======= AISLE (3.0m width) ========
  N6     N7     N8     N9    N10
[RACK] [RACK] [RACK] [RACK] [RACK]
```

#### 1.1.2 Bulk Storage Areas

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Floor-level storage for large/heavy items or overflow |
| **Recommended Dimensions** | Minimum 100 sqm blocks, aisle width: 4.0-5.0m |
| **AGV Accessibility** | Wide approach paths for maneuvering |
| **Node Density** | 1 node per 25 sqm (5m x 5m grid) |
| **Special Requirements** | Floor load capacity: min 5 tons/sqm |

#### 1.1.3 Cold Storage Areas

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Temperature-controlled storage (frozen/refrigerated) |
| **Recommended Dimensions** | Typically 10-20% of total facility; aisle width: 3.5m minimum |
| **Temperature Range** | Refrigerated: 2-8 C, Frozen: -18 to -25 C |
| **AGV Accessibility** | AGVs must be rated for temperature range; condensation-resistant sensors |
| **Node Density** | Same as rack storage, with thermal transition nodes at entry/exit |
| **Special Requirements** | Thermal curtains/doors, AGV battery performance considerations |

---

### 1.2 Operational Zones

#### 1.2.1 Picking Zones

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Order picking and consolidation activities |
| **Recommended Dimensions** | 5-15% of warehouse area; aisle width: 2.5-3.0m |
| **AGV Accessibility** | Goods-to-person or person-to-goods configurations |
| **Node Density** | High density - 1 node per 2m along pick faces |
| **Special Requirements** | Ergonomic workstation positioning, light curtain integration |

**Configuration Options:**
- **Zone Picking:** Dedicated areas by product category
- **Wave Picking:** Time-batched order fulfillment
- **Goods-to-Person:** AGVs deliver to stationary pickers

#### 1.2.2 Packing Zones

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Order packaging and labeling |
| **Recommended Dimensions** | 3-8% of warehouse area; workstation depth: 2.5m |
| **AGV Accessibility** | Inbound/outbound queue lanes required |
| **Node Density** | 1 node per packing station + queue positions |
| **Special Requirements** | Integration with conveyor systems, scale interfaces |

**Packing Station Layout:**
```
AGV INBOUND QUEUE      WORKSTATION      AGV OUTBOUND QUEUE
   [N1] [N2]     -->   [PACK STN]  -->    [N3] [N4]
```

#### 1.2.3 Staging Zones

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Temporary holding before shipping or processing |
| **Recommended Dimensions** | 5-10% of warehouse area; lane width: 1.5-2.0m per pallet |
| **AGV Accessibility** | Grid pattern for multi-deep staging |
| **Node Density** | 1 node per staging position (typically pallet-sized) |
| **Special Requirements** | Clear lane marking, FIFO/LIFO path designation |

---

### 1.3 Movement Zones

#### 1.3.1 Main Aisles

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Primary traffic arteries for AGV movement |
| **Recommended Dimensions** | Width: 4.0-6.0m for bidirectional traffic |
| **AGV Accessibility** | Two-way traffic with passing capability |
| **Node Density** | Nodes every 10-15m + at all intersections |
| **Special Requirements** | Priority routing, speed zones (typically 1.5-2.0 m/s) |

#### 1.3.2 Cross Aisles

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Perpendicular connectors between main aisles |
| **Recommended Dimensions** | Width: 3.0-4.0m |
| **AGV Accessibility** | Intersection management critical |
| **Node Density** | Nodes at each intersection + midpoint for long cross aisles |
| **Special Requirements** | Turn radius accommodation (min 1.5m for standard AGV) |

#### 1.3.3 Buffer Lanes

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Temporary AGV waiting/queuing areas |
| **Recommended Dimensions** | Width: 1.5-2.0m; Length: 2-5 AGV lengths |
| **AGV Accessibility** | Linear queue formation |
| **Node Density** | 1 node per AGV position in queue |
| **Special Requirements** | Non-blocking placement relative to main traffic |

---

### 1.4 Infrastructure Zones

#### 1.4.1 Charging Stations

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | AGV battery charging/swapping locations |
| **Recommended Dimensions** | Per station: 3m x 4m minimum |
| **Quantity** | 1 charger per 3-5 AGVs (opportunity charging), 1 per AGV (dedicated) |
| **AGV Accessibility** | Approach path with alignment aids |
| **Node Density** | 1 node per charging position + approach node |
| **Special Requirements** | Power infrastructure (480V typical), fire suppression |

**Placement Guidelines:**
- Distribute across facility to minimize travel to charge
- Avoid blocking main aisles
- Consider opportunity charging at staging areas

#### 1.4.2 Maintenance Areas

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | AGV repair, inspection, and servicing |
| **Recommended Dimensions** | Minimum 50 sqm for small fleet, 150+ sqm for large fleet |
| **AGV Accessibility** | Wide access for towing disabled AGVs |
| **Node Density** | Entry/exit nodes only (manual operation inside) |
| **Special Requirements** | Tool storage, parts inventory, lift equipment |

#### 1.4.3 Safety Zones

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Emergency stops, fire exits, human-only areas |
| **Recommended Dimensions** | Variable per local regulations |
| **AGV Accessibility** | Prohibited or restricted access |
| **Node Density** | Boundary nodes only for geofencing |
| **Special Requirements** | Emergency stop triggers, visual/audio alarms |

---

### 1.5 Interface Zones

#### 1.5.1 Dock Doors

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Truck loading/unloading points |
| **Recommended Dimensions** | Door width: 3.0-3.5m; Approach depth: 15-20m |
| **AGV Accessibility** | Sequential queuing, integration with dock levelers |
| **Node Density** | 1 node per dock position + queue nodes |
| **Special Requirements** | Dock scheduling integration, trailer detection |

#### 1.5.2 Receiving Areas

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Inbound goods inspection and processing |
| **Recommended Dimensions** | 5-10% of warehouse area |
| **AGV Accessibility** | Integration with receiving stations and conveyor |
| **Node Density** | 1 node per inspection station + staging nodes |
| **Special Requirements** | Barcode/RFID scanning integration |

#### 1.5.3 Shipping Areas

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Outbound order consolidation and truck loading |
| **Recommended Dimensions** | 5-10% of warehouse area |
| **AGV Accessibility** | Lane-based staging with load sequencing |
| **Node Density** | 1 node per lane position + loading nodes |
| **Special Requirements** | Manifest verification, weight capture |

---

## 2. Grid Overlay System

This section describes how to overlay a navigation grid on existing warehouse floor plans to enable AGV pathfinding and control.

### 2.1 Grid Cell Size Selection Criteria

The navigation grid cell size determines the resolution of AGV positioning and path planning. Selection depends on multiple factors:

| Factor | Small Cells (0.5-1.0m) | Medium Cells (1.0-2.0m) | Large Cells (2.0-5.0m) |
|--------|----------------------|------------------------|---------------------|
| **Best For** | High-density picking, narrow aisles | General warehouse operations | Wide aisles, bulk storage |
| **AGV Positioning** | Precise (cm accuracy) | Standard (dm accuracy) | Coarse (m accuracy) |
| **Computation Load** | High | Medium | Low |
| **Node Count** | Very high | Moderate | Low |
| **Path Flexibility** | Maximum | Good | Limited |

**Recommended Selection Process:**

1. **Measure smallest AGV in fleet** - Cell size should not exceed AGV width
2. **Identify narrowest aisle** - Ensure 2+ cells fit across aisle width
3. **Consider pick position precision** - Match cell size to required stop accuracy
4. **Balance computation** - Larger facilities may need coarser grids

**Formula for Cell Size:**
```
Cell Size = min(
    Narrowest Aisle Width / 3,
    Smallest AGV Width,
    Required Position Accuracy * 2
)
```

### 2.2 Node Placement Rules

Nodes are discrete positions where AGVs can stop, turn, or make routing decisions. They form the vertices of the navigation graph.

#### 2.2.1 Mandatory Node Locations

| Location | Rationale |
|----------|-----------|
| All aisle intersections | Routing decision points |
| Rack bay positions | Pick/put locations |
| Charging station positions | Battery management |
| Dock door positions | Loading/unloading |
| Zone entry/exit points | Zone transition control |
| Queue positions | Wait management |
| Emergency stop points | Safety compliance |

#### 2.2.2 Node Spacing Guidelines

| Zone Type | Recommended Spacing |
|-----------|-------------------|
| Storage aisles | 2.4-3.0m (match rack bay pitch) |
| Main aisles | 10-15m + all intersections |
| Cross aisles | At intersections + midpoints if >15m |
| Staging areas | 1.2-1.5m (pallet pitch) |
| Buffer lanes | AGV length + 0.5m safety margin |

#### 2.2.3 Node Naming Convention

Use a hierarchical naming scheme for clear identification:

```
Format: [Zone][Row]-[Position]

Examples:
  SA01-15   = Storage Area 01, position 15
  MA-N-07   = Main Aisle North, position 07
  CH-03     = Charging station 03
  DK-12     = Dock door 12
  PK-A-22   = Picking zone A, position 22
```

### 2.3 Edge (Path) Definition Rules

Edges connect nodes and define allowable AGV travel paths. Each edge has associated properties.

#### 2.3.1 Edge Properties

| Property | Description | Typical Values |
|----------|-------------|----------------|
| Distance | Physical path length | Measured in meters |
| Direction | One-way or bidirectional | UNI / BI |
| Speed Limit | Maximum AGV velocity | 0.5-2.0 m/s |
| Weight/Cost | Path preference factor | 1.0 = standard |
| Capacity | Simultaneous AGV limit | 1-3 typically |
| Type | Path classification | MAIN / CROSS / STORAGE |

#### 2.3.2 Edge Creation Guidelines

1. **Direct line of travel** - Edges should represent actual clear paths
2. **No diagonal edges in rack aisles** - AGVs travel perpendicular to racks
3. **Intersection handling** - Create explicit turn nodes, not direct diagonals
4. **Minimum edge length** - Should exceed AGV stopping distance
5. **Maximum edge length** - Should not exceed 50m without intermediate nodes

**Edge Definition Format:**
```
EDGE: [StartNode] -> [EndNode]
  Distance: 12.5m
  Direction: BI
  Speed: 1.5 m/s
  Type: MAIN_AISLE
```

### 2.4 Obstacle Marking Conventions

Obstacles must be mapped to prevent collisions and enable path planning around fixed and dynamic obstructions.

#### 2.4.1 Fixed Obstacle Types

| Obstacle Type | Symbol | Buffer Distance |
|--------------|--------|----------------|
| Structural columns | Square/Circle | 0.5m all sides |
| Walls | Solid line | 0.3m |
| Fixed equipment | Rectangle | 0.5m all sides |
| Fire suppression | Triangle | 1.0m keep-clear |
| Electrical panels | Rectangle + X | 1.0m front, 0.5m sides |

#### 2.4.2 Obstacle Mapping Process

1. **Survey all fixed elements** - Columns, walls, equipment
2. **Measure positions precisely** - Use CAD coordinates or laser measurement
3. **Apply safety buffers** - Add clearance to obstacle boundaries
4. **Create exclusion zones** - Mark as non-traversable in grid
5. **Verify sight lines** - Ensure AGV sensors can detect edges

#### 2.4.3 Dynamic Obstacle Considerations

| Element | Handling Approach |
|---------|-------------------|
| Pedestrians | Real-time sensor detection, not mapped |
| Forklifts | Zone-based restrictions or sensor detection |
| Temporary staging | Marked as soft obstacles, updatable |
| Seasonal storage | Configurable zone boundaries |

### 2.5 One-Way vs Two-Way Path Designation

Traffic flow patterns significantly impact throughput and safety.

#### 2.5.1 Decision Criteria

| Factor | Favor One-Way | Favor Two-Way |
|--------|--------------|---------------|
| Aisle width | < 3.5m | > 4.0m |
| Traffic volume | High | Low to moderate |
| Path alternatives | Multiple parallel paths | Single path available |
| AGV fleet size | Large (>10) | Small (<5) |
| Complexity tolerance | Higher | Lower |

#### 2.5.2 One-Way Path Guidelines

**Advantages:**
- Eliminates head-on conflicts
- Predictable traffic flow
- Higher effective throughput in narrow aisles

**Implementation Rules:**
- Create complementary return paths
- Mark clearly with arrows at entry points
- Ensure no dead-ends (circular flow)
- Plan for exception handling (emergency reverse)

#### 2.5.3 Two-Way Path Guidelines

**Advantages:**
- Simpler path planning
- Shorter routes in low-traffic scenarios
- Easier to understand and maintain

**Implementation Rules:**
- Ensure adequate width for passing (min 4.0m)
- Implement priority rules at intersections
- Create passing bays for long straight sections
- Use reservation systems to prevent deadlock

#### 2.5.4 Hybrid Approach (Recommended)

```
Main Aisles:     Two-way (wide, lower frequency)
Storage Aisles:  One-way (narrow, high frequency)
Cross Aisles:    Two-way with intersection control
Dock Areas:      One-way loops for efficiency
```

---

## 3. Sample Layout Templates

Three standard templates for different warehouse sizes, designed as starting points for retrofit planning.

---

### Template A: Small Warehouse (< 5,000 sqm)

#### Overview

| Attribute | Specification |
|-----------|--------------|
| **Target Area** | 2,000 - 5,000 sqm |
| **Typical Dimensions** | 50m x 60m (3,000 sqm example) |
| **Operations Profile** | Light manufacturing support, e-commerce fulfillment |
| **Throughput Range** | 100-500 pallets/day |

#### Zone Allocation

| Zone | Percentage | Area (3,000 sqm example) |
|------|-----------|-------------------------|
| Storage (Rack) | 45% | 1,350 sqm |
| Storage (Bulk) | 10% | 300 sqm |
| Picking/Packing | 15% | 450 sqm |
| Movement (Aisles) | 15% | 450 sqm |
| Receiving/Shipping | 10% | 300 sqm |
| Infrastructure | 5% | 150 sqm |

#### Layout Configuration

```
Dimensions: 50m (W) x 60m (L)
Orientation: Dock doors on short side (50m)

+--------------------------------------------------+
|  RECEIVING                    SHIPPING           |
|  [DK1][DK2]                  [DK3][DK4]          |  <- Dock Doors
+--------------------------------------------------+
|              STAGING AREA (5m depth)             |
+--------------------------------------------------+
|     |                                    |       |
|     |         MAIN AISLE (5m)            |       |
|     |                                    |       |
+-----+------------------------------------+-------+
|RACK |                                    | BULK  |
|AREA |    RACK STORAGE (3m aisles)        | STORE |
| L   |    5 double-deep rack rows         |       |
+-----+------------------------------------+-------+
|     |                                    |       |
|     |       CROSS AISLE (4m)             |       |
+-----+------------------------------------+-------+
|RACK |                                    | PICK  |
|AREA |    RACK STORAGE (3m aisles)        | PACK  |
| R   |    5 double-deep rack rows         | AREA  |
+-----+------------------------------------+-------+
|              MAIN AISLE (5m)             |       |
+------------------------------------------+-------+
| CHARGING (3 stations)  |  MAINT  |  OFFICE      |
+--------------------------------------------------+
```

#### Node Configuration

| Category | Count | Placement |
|----------|-------|-----------|
| Dock nodes | 8 | 2 per dock door |
| Staging nodes | 20 | 5x4 grid pattern |
| Main aisle nodes | 12 | Every 10m |
| Storage nodes | 100 | Per rack bay (50 bays x 2 sides) |
| Cross aisle nodes | 8 | At intersections |
| Pick/pack nodes | 15 | Per workstation + queue |
| Charging nodes | 6 | 2 per station (position + approach) |
| **Total Nodes** | **~170** | |

#### AGV Fleet Recommendation

| Fleet Size | Configuration | Use Case |
|------------|--------------|----------|
| 2-3 AGVs | 2 pallet trucks, 1 tugger | Low volume, single shift |
| 4-5 AGVs | 3 pallet trucks, 2 tuggers | Medium volume, dual shift |
| 6-8 AGVs | Mixed fleet | High volume, 24/7 operation |

**Charging Strategy:** Opportunity charging with 3 stations (1:2 ratio minimum)

---

### Template B: Medium Warehouse (5,000 - 15,000 sqm)

#### Overview

| Attribute | Specification |
|-----------|--------------|
| **Target Area** | 5,000 - 15,000 sqm |
| **Typical Dimensions** | 100m x 100m (10,000 sqm example) |
| **Operations Profile** | Distribution center, retail fulfillment |
| **Throughput Range** | 500-2,000 pallets/day |

#### Zone Allocation

| Zone | Percentage | Area (10,000 sqm example) |
|------|-----------|--------------------------|
| Storage (Rack) | 40% | 4,000 sqm |
| Storage (Bulk/Cold) | 12% | 1,200 sqm |
| Picking | 12% | 1,200 sqm |
| Packing | 6% | 600 sqm |
| Movement (Aisles) | 15% | 1,500 sqm |
| Receiving | 5% | 500 sqm |
| Shipping | 5% | 500 sqm |
| Infrastructure | 5% | 500 sqm |

#### Layout Configuration

```
Dimensions: 100m (W) x 100m (L)
Orientation: Dock doors on long side (100m)

+--------------------------------------------------------------------+
|[DK1][DK2][DK3][DK4]  RECEIVING BAY  [DK5][DK6][DK7][DK8] SHIPPING   |
+--------------------------------------------------------------------+
|   RECEIVING STAGING (6m)      |        SHIPPING STAGING (6m)       |
+-------------------------------+------------------------------------+
|              |                                        |            |
| BULK         |            MAIN AISLE NORTH (6m)       |   COLD     |
| STORAGE      |                                        |   STORAGE  |
+-------------------------------+------------------------------------+
|    |    |    |    |    |    | |    |    |    |    |    |    |    | |
|    | R  | A  | I  | S  | L  | |    | R  | A  | I  | S  | L  | E  | |
|    | A  | C  | K  |    |    | |    | A  | C  | K  |    |    |    | |
| C  |    |    |    |    |    | | C  |    |    |    |    |    |    | |
| R  |ZONE|ZONE|ZONE|ZONE|ZONE| | R  |ZONE|ZONE|ZONE|ZONE|ZONE|ZONE| |
| O  | A  | B  | C  | D  | E  | | O  | F  | G  | H  | I  | J  | K  | |
| S  |    |    |    |    |    | | S  |    |    |    |    |    |    | |
| S  +----+----+----+----+----+ | S  +----+----+----+----+----+----+ |
|    |                         | |    |                         |    |
| A  |      CENTER AISLE       | | A  |     CENTER AISLE        |    |
| I  |         (5m)            | | I  |        (5m)             |    |
| S  +----+----+----+----+----+ | S  +----+----+----+----+----+ |    |
| L  |ZONE|ZONE|ZONE|ZONE|ZONE| | L  |ZONE|ZONE|ZONE|ZONE|ZONE| |    |
| E  | L  | M  | N  | O  | P  | | E  | Q  | R  | S  | T  | U  | |    |
|    |    |    |    |    |    | |    |    |    |    |    |    | |    |
+----+----+----+----+----+----+-+----+----+----+----+----+----+-+----+
|              |                                        |            |
|   PICKING    |          MAIN AISLE SOUTH (6m)         |  PACKING   |
|   ZONE       |                                        |  ZONE      |
+-------------------------------+------------------------------------+
| CHARGING BANK    |    MAINT BAY    |    CONTROL ROOM    | OFFICE  |
+--------------------------------------------------------------------+
```

#### Node Configuration

| Category | Count | Placement |
|----------|-------|-----------|
| Dock nodes | 16 | 2 per dock door |
| Staging nodes | 60 | Grid pattern in staging areas |
| Main aisle nodes | 24 | Every 12m along main aisles |
| Cross aisle nodes | 20 | At all intersections |
| Storage nodes | 400 | Per rack bay across 20 zones |
| Picking nodes | 40 | Per pick position |
| Packing nodes | 20 | Per workstation + queues |
| Cold storage nodes | 30 | Dedicated cold zone |
| Bulk storage nodes | 25 | Grid pattern |
| Charging nodes | 16 | 2 per station (8 stations) |
| **Total Nodes** | **~650** | |

#### AGV Fleet Recommendation

| Fleet Size | Configuration | Use Case |
|------------|--------------|----------|
| 8-10 AGVs | 6 pallet trucks, 4 tuggers | Standard operation |
| 12-15 AGVs | Mixed with specialty units | High throughput |
| 15-20 AGVs | Full fleet diversity | Peak season / 24-7 |

**Fleet Composition Recommendation:**
- 50% Counterbalance/Pallet trucks (storage operations)
- 30% Tuggers (bulk transport, dock-to-staging)
- 20% Specialty (narrow aisle, cold storage rated)

**Charging Strategy:** Mix of opportunity charging (6 stations) and dedicated charging area (2 stations) with battery swap capability

---

### Template C: Large Warehouse (> 15,000 sqm)

#### Overview

| Attribute | Specification |
|-----------|--------------|
| **Target Area** | 15,000 - 50,000+ sqm |
| **Typical Dimensions** | 200m x 150m (30,000 sqm example) |
| **Operations Profile** | Regional distribution hub, fulfillment mega-center |
| **Throughput Range** | 2,000-10,000+ pallets/day |

#### Zone Allocation

| Zone | Percentage | Area (30,000 sqm example) |
|------|-----------|--------------------------|
| Storage (Rack - Ambient) | 35% | 10,500 sqm |
| Storage (Rack - Cold) | 8% | 2,400 sqm |
| Storage (Bulk) | 7% | 2,100 sqm |
| Picking (Multiple zones) | 10% | 3,000 sqm |
| Packing/VAS | 8% | 2,400 sqm |
| Movement (Aisles) | 14% | 4,200 sqm |
| Receiving | 5% | 1,500 sqm |
| Shipping | 5% | 1,500 sqm |
| Staging (Both ends) | 4% | 1,200 sqm |
| Infrastructure | 4% | 1,200 sqm |

#### Multi-Zone Architecture

Large warehouses require subdivision into operational zones for:
- Traffic management and congestion control
- Zone-specific AGV assignment
- Failure isolation
- Scalable expansion

**Zone Division Strategy:**
```
+------------------------------------------------------------------+
|                           ZONE NORTH                              |
|   (Receiving Focus: Inbound processing, QC, put-away)            |
+---------------------------+--------------------------------------+
|                           |                                      |
|        ZONE WEST          |           ZONE EAST                  |
|   (Ambient Storage)       |      (Cold Chain + Specialty)        |
|   Primary rack storage    |      Temperature controlled          |
|   Bulk storage            |      Hazmat compliant area           |
|                           |                                      |
+---------------------------+--------------------------------------+
|                           ZONE SOUTH                              |
|   (Shipping Focus: Picking, packing, outbound staging)           |
+------------------------------------------------------------------+
|                      ZONE INFRASTRUCTURE                          |
|   (Charging, maintenance, control center, offices)               |
+------------------------------------------------------------------+
```

#### Layout Configuration (30,000 sqm Example)

```
Dimensions: 200m (W) x 150m (L)
Dock doors: 16 receiving (North), 20 shipping (South)

+================================================================================+
|| DK DK DK DK DK DK DK DK |  RECEIVING  | DK DK DK DK DK DK DK DK ||            |
||  1  2  3  4  5  6  7  8 |   OFFICE    |  9 10 11 12 13 14 15 16 || GUARD      |
|+-------------------------+--------------+--------------------------+| HOUSE     |
||                    RECEIVING STAGING AREA (8m depth)              ||           |
|+===================================================================++===========+
||              |                                          |                     |
|| BULK         |         MAIN AISLE NORTH (7m)            |   CROSS-DOCK       |
|| RECEIVING    |                                          |   AREA             |
|+--------------+------------------------------------------+---------------------+
||    |    |    |    |    |    |    |    |    |    |    |    |    |    |   |   |
||    |    |    |    |    |    |    |    |    |    |    |    |    |    |   |   |
|| STORAGE ZONE A       | STORAGE ZONE B        | STORAGE ZONE C     | C |   |
|| (High velocity)      | (Medium velocity)     | (Low velocity)     | O |   |
|| Narrow aisle VNA     | Standard aisle        | Deep lane          | L |   |
|| 12 aisles            | 10 aisles             | 6 aisles           | D |   |
||                      |                       |                    |   |   |
||    |    |    |    |    |    |    |    |    |    |    |    |    |    | Z |   |
|+--------------------+------------------------+--------------------+ O |   |
||              |                                          |         | N |   |
|| CROSS        |          CENTER SPINE (8m)               |         | E |   |
|| AISLE        |     (Main traffic corridor)              |         |   |   |
|+--------------------+------------------------+--------------------+---+   |
||    |    |    |    |    |    |    |    |    |    |    |    |    |    |   |   |
|| STORAGE ZONE D       | PICKING ZONE          | VAS / PACKING      |   |   |
|| (Overflow/seasonal)  | (Goods-to-person)     | (Value-add svc)    |   |   |
|| Bulk + floor stack   | 20 pick stations      | 15 pack stations   |   |   |
||                      | Conveyor integration  | Conveyor to ship   |   |   |
||    |    |    |    |    |    |    |    |    |    |    |    |    |    |   |   |
|+--------------------+------------------------+--------------------+---+---+
||              |                                          |                 |
|| BUFFER       |         MAIN AISLE SOUTH (7m)            |   RETURNS       |
|| LANES        |                                          |   PROCESSING    |
|+--------------+------------------------------------------+-----------------+
||                     SHIPPING STAGING AREA (10m depth)                     |
|+===========================================================================+
||DK DK DK DK DK DK DK DK DK DK | SHIPPING | DK DK DK DK DK DK DK DK DK DK  |
|| 1  2  3  4  5  6  7  8  9 10 |  OFFICE  | 11 12 13 14 15 16 17 18 19 20  |
|+------------------------------+----------+--------------------------------+
|                                                                            |
|  +--------+    +--------+    +--------+    +--------+    +---------+      |
|  |CHARGING|    |CHARGING|    | MAINT  |    |CONTROL |    |BATTERY  |      |
|  | BANK A |    | BANK B |    |  BAY   |    | CENTER |    | SWAP    |      |
|  +--------+    +--------+    +--------+    +--------+    +---------+      |
+============================================================================+
```

#### Node Configuration

| Category | Count | Placement |
|----------|-------|-----------|
| Receiving dock nodes | 32 | 2 per dock |
| Shipping dock nodes | 40 | 2 per dock |
| Receiving staging | 80 | Grid pattern |
| Shipping staging | 120 | Grid pattern |
| Main aisle nodes | 60 | Every 15m |
| Center spine nodes | 30 | Every 10m (high traffic) |
| Cross aisle nodes | 80 | All intersections |
| Storage Zone A nodes | 250 | Per rack bay, VNA |
| Storage Zone B nodes | 200 | Per rack bay |
| Storage Zone C nodes | 120 | Per lane position |
| Storage Zone D nodes | 100 | Grid pattern bulk |
| Cold zone nodes | 80 | Dedicated cold area |
| Picking station nodes | 80 | Per station + queues |
| Packing station nodes | 60 | Per station + queues |
| Charging nodes | 32 | 2 per position (16 positions) |
| Zone boundary nodes | 40 | Entry/exit points |
| **Total Nodes** | **~1,400** | |

#### Multi-Zone Considerations

**1. Zone Boundary Management**
| Concern | Solution |
|---------|----------|
| Traffic bottlenecks at zone transitions | Multiple entry/exit points per zone boundary |
| Mixed AGV types between zones | Zone-compatible fleet assignment |
| Zone-specific scheduling | Independent zone dispatchers with coordination |
| Emergency isolation | Zone-specific E-stop capability |

**2. Hierarchical Control Architecture**
```
                    +------------------+
                    | Central WMS/WCS  |
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
+-------v------+    +--------v-------+    +-------v------+
| Zone North   |    |  Zone Central  |    | Zone South   |
| Controller   |    |   Controller   |    | Controller   |
+--------------+    +----------------+    +--------------+
     |                    |                    |
+----v---+           +----v---+           +----v---+
|AGV 1-8 |           |AGV 9-20|           |AGV21-35|
+--------+           +--------+           +--------+
```

**3. Inter-Zone Traffic Management**
- Dedicated transfer aisles between zones
- Handoff nodes at zone boundaries
- Priority scheduling for inter-zone transport
- Buffer lanes to prevent zone blocking

#### AGV Fleet Recommendation

| Fleet Size | Configuration | Use Case |
|------------|--------------|----------|
| 20-25 AGVs | Zone-assigned mixed fleet | Standard operation |
| 30-40 AGVs | Full automation coverage | High throughput, dual shift |
| 45-60 AGVs | Maximum automation | Peak / 24-7 / future growth |

**Fleet Composition for 35 AGVs (Recommended Baseline):**

| AGV Type | Quantity | Zone Assignment |
|----------|----------|-----------------|
| VNA trucks | 8 | Zone A (narrow aisle) |
| Counterbalance | 10 | Zones B, C, D (standard storage) |
| Cold-rated pallet trucks | 4 | Cold Zone |
| Tuggers | 6 | Dock-to-staging routes |
| Goods-to-person bots | 5 | Picking zone |
| Conveyor interface AGVs | 2 | Packing/shipping |

**Charging Strategy:**
- Opportunity charging: 12 stations distributed across facility
- Dedicated charging bank: 4 positions for overnight/deep charge
- Battery swap station: 1 facility for rapid turnaround

---

## 4. Layout Conversion Checklist

A step-by-step checklist for converting legacy warehouse floor plans to AGV-ready navigation maps.

### Phase 1: Data Collection

- [ ] **1.1 Obtain accurate floor plan**
  - [ ] Acquire CAD drawings (DWG/DXF format preferred)
  - [ ] If no CAD: commission laser scanning survey
  - [ ] If no survey possible: manual measurement with verification
  - [ ] Verify scale and dimensions against physical measurements
  - [ ] Document coordinate system and origin point
  - [ ] Note drawing revision date and any recent modifications

- [ ] **1.2 Identify fixed obstacles**
  - [ ] Mark all structural columns (note dimensions and positions)
  - [ ] Identify permanent equipment (conveyors, mezzanines, fixed racking)
  - [ ] Document wall positions and thicknesses
  - [ ] Note door locations and swing directions
  - [ ] Identify fire suppression equipment (sprinkler drops, extinguishers)
  - [ ] Mark electrical panels and keep-clear zones

- [ ] **1.3 Mark load-bearing elements**
  - [ ] Consult structural drawings for column load capacities
  - [ ] Identify load-bearing walls vs. partitions
  - [ ] Note floor load capacity by zone (important for AGV + payload weight)
  - [ ] Document any floor penetrations or weak spots
  - [ ] Identify mezzanine support columns

### Phase 2: Zone Definition

- [ ] **2.1 Define zone boundaries**
  - [ ] Overlay zone types from Section 1 onto floor plan
  - [ ] Ensure adequate aisle widths between zones (min 3.5m for AGV)
  - [ ] Verify zone sizes match operational requirements
  - [ ] Mark zone entry/exit points
  - [ ] Document zone-specific requirements (temperature, cleanliness, security)

- [ ] **2.2 Validate operational flow**
  - [ ] Map material flow from receiving to shipping
  - [ ] Identify high-traffic corridors
  - [ ] Note cross-traffic points requiring intersection management
  - [ ] Verify emergency egress paths remain clear
  - [ ] Confirm human/AGV interaction zones are properly separated

- [ ] **2.3 Confirm infrastructure placement**
  - [ ] Position charging stations (near high-traffic areas but off main paths)
  - [ ] Locate maintenance area (accessible but not blocking flow)
  - [ ] Identify control room/monitoring station location
  - [ ] Verify network/power infrastructure availability for AGV system

### Phase 3: Grid Overlay

- [ ] **3.1 Overlay navigation grid**
  - [ ] Select appropriate cell size per Section 2.1 criteria
  - [ ] Align grid to building structure (parallel to main walls)
  - [ ] Extend grid to cover all traversable areas
  - [ ] Document grid origin point and orientation
  - [ ] Create grid reference system (alphanumeric coordinates)

- [ ] **3.2 Place nodes at decision points**
  - [ ] Mark nodes at all aisle intersections
  - [ ] Place nodes at each rack bay position
  - [ ] Add nodes at zone entry/exit points
  - [ ] Position nodes at dock doors and staging positions
  - [ ] Mark charging station approach and docking nodes
  - [ ] Add queue position nodes where AGVs may wait
  - [ ] Place nodes at pick/pack workstation interfaces

- [ ] **3.3 Assign node identifiers**
  - [ ] Apply consistent naming convention (see Section 2.2.3)
  - [ ] Create node registry with coordinates
  - [ ] Document node type (storage, transit, charging, etc.)
  - [ ] Note any special node properties (priority, restricted access)

### Phase 4: Path Definition

- [ ] **4.1 Define edges with distances**
  - [ ] Connect adjacent nodes with edges
  - [ ] Measure and record actual travel distance for each edge
  - [ ] Verify path clearance for largest AGV in fleet
  - [ ] Document any height restrictions along paths
  - [ ] Note floor surface conditions affecting travel

- [ ] **4.2 Designate path directions**
  - [ ] Mark one-way paths in storage aisles (if applicable)
  - [ ] Confirm two-way paths have adequate width
  - [ ] Document priority rules at intersections
  - [ ] Create traffic flow diagrams for main routes

- [ ] **4.3 Set path properties**
  - [ ] Assign speed limits to each edge
  - [ ] Set path weights/costs for routing optimization
  - [ ] Define path capacities (simultaneous AGV limits)
  - [ ] Mark path types (main, cross, storage, dock)

### Phase 5: Special Area Designation

- [ ] **5.1 Mark restricted areas**
  - [ ] Define no-go zones for AGVs (offices, break rooms, etc.)
  - [ ] Mark pedestrian-only areas
  - [ ] Identify time-based restrictions (e.g., dock scheduling)
  - [ ] Document emergency stop trigger zones
  - [ ] Note any security-restricted areas

- [ ] **5.2 Designate charging locations**
  - [ ] Confirm electrical infrastructure at each charging point
  - [ ] Document charger specifications and compatibility
  - [ ] Mark approach paths for docking alignment
  - [ ] Define charging queue positions
  - [ ] Set charging zone boundaries

- [ ] **5.3 Define pickup/drop-off points (PDP)**
  - [ ] Mark all load transfer positions
  - [ ] Document load specifications at each PDP (pallet size, weight)
  - [ ] Define approach requirements (orientation, alignment)
  - [ ] Note any sensor or verification requirements
  - [ ] Specify handling equipment at each PDP (conveyor, lift table, etc.)

### Phase 6: Validation

- [ ] **6.1 Path connectivity check**
  - [ ] Verify all zones are reachable from all other zones
  - [ ] Confirm no dead-ends exist (or are intentional)
  - [ ] Test routing from each charging station to all work areas
  - [ ] Validate emergency exit paths remain unblocked

- [ ] **6.2 Capacity verification**
  - [ ] Calculate total node count vs. expected AGV fleet
  - [ ] Verify buffer areas can handle peak traffic
  - [ ] Check intersection capacity for expected throughput
  - [ ] Confirm charging station count supports fleet

- [ ] **6.3 Safety compliance**
  - [ ] Verify aisle widths meet local fire codes
  - [ ] Confirm emergency stop coverage
  - [ ] Check pedestrian crossing point safety measures
  - [ ] Validate clearances around fire exits

- [ ] **6.4 Documentation completion**
  - [ ] Create final layout drawing with all markings
  - [ ] Generate node database export
  - [ ] Produce edge/path database export
  - [ ] Document all assumptions and exceptions
  - [ ] Obtain stakeholder sign-off

---

## 5. Visual Conventions

Standardized legend for layout diagrams to ensure consistent interpretation across all documentation.

### 5.1 Color Codes for Zones

| Zone Type | Color Code | Hex Value | Usage |
|-----------|------------|-----------|-------|
| Storage - Rack | Light Blue | #ADD8E6 | Standard rack storage areas |
| Storage - Bulk | Tan/Beige | #D2B48C | Floor-level bulk storage |
| Storage - Cold | Light Cyan | #E0FFFF | Temperature-controlled areas |
| Picking | Light Green | #90EE90 | Order picking zones |
| Packing | Yellow-Green | #ADFF2F | Packing and VAS areas |
| Staging | Light Yellow | #FFFFE0 | Temporary holding areas |
| Movement - Main Aisle | White | #FFFFFF | Primary traffic corridors |
| Movement - Cross Aisle | Light Gray | #D3D3D3 | Secondary corridors |
| Receiving | Light Orange | #FFDAB9 | Inbound processing |
| Shipping | Light Pink | #FFB6C1 | Outbound processing |
| Charging | Green | #00FF00 | AGV charging stations |
| Maintenance | Purple | #DDA0DD | Service and repair areas |
| Restricted | Red | #FF6B6B | No-go zones |
| Office/Human Only | Gray | #808080 | Non-AGV areas |

### 5.2 Symbols

#### 5.2.1 Node Symbols

```
Standard Symbols (monochrome line drawings):

Navigation Node (standard):       O       (open circle, ~5mm diameter)

Navigation Node (with ID):        O       (circle with adjacent label)
                                 N42

Storage Position Node:            [ ]     (square, ~5mm)

Pick/Pack Station Node:           [P]     (square with P inside)

Charging Node:                    [+]     (square with + inside)
                                  or
                                  (+)     (circle with + inside)

Dock Door Node:                   [D]     (square with D inside)

Queue/Buffer Node:                [=]     (square with = inside)

Intersection Node:                (*)     (circle with asterisk)

Zone Boundary Node:               [Z]     (square with Z inside)

Emergency Stop Node:              [!]     (square with ! inside)
```

#### 5.2.2 Infrastructure Symbols

```
Charging Station:          +-----+
                           | CHG |
                           |  1  |
                           +-----+

Maintenance Bay:           +-------+
                           | MAINT |
                           +-------+

Control Room:              +-------+
                           | CTRL  |
                           +-------+

Dock Door:                 /_____\      (trapezoid indicating door)
                             DK1

Fire Extinguisher:         (FE)         (circle with FE)

Emergency Stop Button:     [E-STOP]     (rectangle, red fill)

Column/Pillar:             [#]          (square with #, filled)
                           or
                           (@)          (circle with @, filled)

Wall:                      =========    (double line)

Partition:                 ---------    (single line)

Conveyor:                  >>>>>>>>>>   (arrows indicating direction)
```

#### 5.2.3 Obstacle Symbols

```
Fixed Obstacle:            [XXX]        (rectangle with X fill)

Temporary Obstacle:        [///]        (rectangle with diagonal lines)

No-Go Zone:                +-----+
                           |/////|      (area with diagonal hatching)
                           |/////|
                           +-----+

Height Restriction:        [^3.5m^]     (with height noted)

Floor Hazard:              [~~~]        (wavy lines)
```

### 5.3 Line Types for Paths

```
Main Aisle (two-way):
====================       Double solid line, thick (2pt)

Main Aisle (one-way):
===================>       Double solid line with arrow

Cross Aisle (two-way):
--------------------       Single dashed line, medium (1.5pt)

Cross Aisle (one-way):
------------------->       Single dashed line with arrow

Storage Aisle (two-way):
....................       Dotted line, thin (1pt)

Storage Aisle (one-way):
...................>       Dotted line with arrow

Restricted Path:
xxxxxxxxxxxxxxxx           X pattern line (limited access)

Emergency Path Only:
!!!!!!!!!!!!!!!!!          Exclamation pattern (emergency use only)

Pedestrian Crossing:
=  =  =  =  =  =           Segmented double line (crosswalk style)
```

### 5.4 Path Direction Indicators

```
One-Way Arrow:              ->          (single arrow at path end)
                           --->         (emphasized arrow)

Two-Way Indicator:          <->         (double arrow)
                           <--->        (emphasized double arrow)

Priority Direction:         =>          (thick arrow = priority)
                           ->           (thin arrow = yield)

Turn Indicator:             ,--->       (curved approach with arrow)
                           '

Merge Point:                --->
                               \
                                --->    (converging paths)
                               /
                           --->

Diverge Point:                  /--->
                           ---<
                                \--->   (diverging paths)
```

### 5.5 Annotation Standards

#### 5.5.1 Text Formatting

| Element | Font Style | Size | Example |
|---------|-----------|------|---------|
| Zone labels | Bold, ALL CAPS | 12pt | STORAGE ZONE A |
| Node IDs | Regular | 8pt | N42, SA01-15 |
| Dimensions | Italic | 10pt | *50.0m* |
| Warnings | Bold, Red | 10pt | **NO AGV ACCESS** |
| Notes | Regular | 8pt | Floor load: 5t/sqm |

#### 5.5.2 Dimension Annotations

```
Horizontal Dimension:
<-------- 25.0m -------->

Vertical Dimension:
^
|
| 12.5m
|
v

Aisle Width:
|<- 3.5m ->|
```

#### 5.5.3 Reference Annotations

```
Grid Reference:          A  B  C  D  E  F  (columns)
                      1  +--+--+--+--+--+
                      2  |  |  |  |  |  |
                      3  +--+--+--+--+--+  (rows)

North Arrow:               ^
                           |
                           N

Scale Bar:            |----|----|----|----|
                      0   5   10   15   20m

Revision Block:       Rev: 1.2
                      Date: 2026-01-11
                      Author: Layout Team
```

### 5.6 Complete Legend Template

```
+==============================================================================+
|                           LAYOUT LEGEND                                       |
+==============================================================================+
|                                                                               |
|  ZONES                          |  PATHS                                      |
|  +-----------+                  |  ==================  Main Aisle (2-way)     |
|  | Light Blue| Rack Storage     |  =================>  Main Aisle (1-way)     |
|  +-----------+                  |  ------------------  Cross Aisle (2-way)    |
|  |    Tan    | Bulk Storage     |  ----------------->  Cross Aisle (1-way)    |
|  +-----------+                  |  ..................  Storage Aisle (2-way)  |
|  |Light Green| Picking          |  .................>  Storage Aisle (1-way)  |
|  +-----------+                  |                                             |
|  |  Yellow   | Staging          |  DIRECTION ARROWS                           |
|  +-----------+                  |  ->   One-way        <->  Two-way           |
|  |   White   | Main Aisle       |  =>   Priority       <=>  Bi-priority       |
|  +-----------+                  |                                             |
|  |   Green   | Charging         +---------------------------------------------+
|  +-----------+                  |  OBSTACLES                                  |
|  |   Red     | Restricted       |  [#] Column          [XXX] Fixed obstacle   |
|  +-----------+                  |  === Wall            [///] Temporary        |
|                                 |                                             |
+-----------------------------+---+---------------------------------------------+
|  NODES                      |   |  INFRASTRUCTURE                             |
|  O    Navigation            |   |  [CHG] Charging Station                     |
|  [ ]  Storage Position      |   |  [DK]  Dock Door                            |
|  [P]  Pick/Pack Station     |   |  (FE)  Fire Extinguisher                    |
|  [+]  Charging Position     |   |  [CTRL] Control Room                        |
|  [D]  Dock Position         |   |  >>>   Conveyor (direction shown)           |
|  (*)  Intersection          |   |                                             |
|  [Z]  Zone Boundary         |   |                                             |
|  [!]  Emergency Stop        |   |                                             |
+-----------------------------+---+---------------------------------------------+
|  SCALE: |----|----|----|----|   |  NOTES:                                     |
|         0   5   10   15   20m   |  All dimensions in meters                   |
|                                 |  Grid cell size: 2.0m                       |
|         ^                       |  Revision: 1.0                              |
|         N                       |  Date: 2026-01-11                           |
+-----------------------------+---+---------------------------------------------+
```

---

## 6. ASCII Art Layout Example

A complete ASCII representation of a small retrofitted warehouse (Template A size) showing all key elements.

### 6.1 Complete Layout View

```
+===================================================================================+
||                          RETROFIT WAREHOUSE LAYOUT                              ||
||                           Template A: Small (3,000 sqm)                         ||
||                              Dimensions: 50m x 60m                              ||
+===================================================================================+

NORTH
  ^                           SCALE: Each = is ~2m
  |
  +-- 50m --+

+============================ DOCK WALL ==============================+
|  DK1    DK2           [RECV OFFICE]           DK3    DK4           |  <- Dock Doors
| /_|_\  /_|_\                                 /_|_\  /_|_\          |
+----+----+----+----+----+----+----+----+----+----+----+----+----+---+
| D1 . D2 | D3 . D4 |         STAGING         | D5 . D6 | D7 . D8   |  <- Dock Nodes
|====.====|====.====|    AREA (5m depth)      |====.====|====.====  |
| S1 . S2 | S3 . S4 |  [S5][S6][S7][S8][S9]   | S10.S11 | S12.S13   |  <- Staging Nodes
+----+----+----+----+----+----+----+----+----+----+----+----+----+---+
|    .    .    .    .    .    .    .    .    .    .    .    .    .  |
|    .    .    .    . MAIN . AISLE . NORTH .    .    .    .    .    |  <- Main Aisle (5m)
|====*====*====*====*====*====*====*====*====*====*====*====*====*==|
| MA1    MA2    MA3    MA4    MA5    MA6    MA7    MA8    MA9   MA10|  <- Main Aisle Nodes
+====+========+========+========+========+========+========+====+===+
|    |[R1.01].|[R1.02].|[R1.03].|[R1.04].|[R1.05].|[R1.06].|    |   |
|    |........|........|........|........|........|........|    |   |
| B  |[R2.01].|[R2.02].|[R2.03].|[R2.04].|[R2.05].|[R2.06].|  B |   |
| U  |--------|--------|--------|--------|--------|--------|  U |   |  <- Storage Aisles
| L  |........|........|........|........|........|........|  L |   |     (3m width)
| K  |[R3.01].|[R3.02].|[R3.03].|[R3.04].|[R3.05].|[R3.06].|  K |   |
|    |........|........|........|........|........|........|    |   |
| S  |[R4.01].|[R4.02].|[R4.03].|[R4.04].|[R4.05].|[R4.06].|  S |   |
| T  |--------|--------|--------|--------|--------|--------|  T |   |
| O  |........|........|........|........|........|........|  O |   |
| R  |[R5.01].|[R5.02].|[R5.03].|[R5.04].|[R5.05].|[R5.06].|  R |   |
| E  |........|........|........|........|........|........|  E |   |
+====+========+========+========+========+========+========+====+===+
|    .    .    .    .    .    .    .    .    .    .    .    .   .   |
|====*====*====*====*==CROSS==*=AISLE==*====*====*====*====*===*===|  <- Cross Aisle (4m)
| CA1    CA2    CA3    CA4    CA5    CA6    CA7    CA8    CA9  CA10 |  <- Cross Aisle Nodes
+====+========+========+========+========+========+========+====+===+
|    |[R6.01].|[R6.02].|[R6.03].|[R6.04].|[R6.05].|[R6.06].|    |   |
|    |........|........|........|........|........|........|    |   |
| B  |[R7.01].|[R7.02].|[R7.03].|[R7.04].|[R7.05].|[R7.06].|  P |   |
| U  |--------|--------|--------|--------|--------|--------|  I |   |
| L  |........|........|........|........|........|........|  C |   |
| K  |[R8.01].|[R8.02].|[R8.03].|[R8.04].|[R8.05].|[R8.06].|  K |   |
|    |........|........|........|........|........|........|  / |   |
| S  |[R9.01].|[R9.02].|[R9.03].|[R9.04].|[R9.05].|[R9.06].|  P |   |
| T  |--------|--------|--------|--------|--------|--------|  A |   |
| O  |........|........|........|........|........|........|  C |   |
| R  |[R10.01]|[R10.02]|[R10.03]|[R10.04]|[R10.05]|[R10.06]|  K |   |
| E  |........|........|........|........|........|........|    |   |
+====+========+========+========+========+========+========+====+===+
|    .    .    .    .    .    .    .    .    .    .    .    .   .   |
|====*====*====*====*=MAIN==*=AISLE=*=SOUTH*====*====*====*===*====|  <- Main Aisle (5m)
|MA11   MA12   MA13   MA14   MA15   MA16   MA17   MA18   MA19  MA20 |  <- Main Aisle Nodes
+----+----+----+----+----+----+----+----+----+----+----+----+---+---+
|         |         |         |              |         |            |
| +-----+ | +-----+ | +-----+ |  [########]  | +-----+ |   +------+ |
| | CHG | | | CHG | | | CHG | |  [ MAINT  ]  | |CTRL | |   |OFFICE| |
| | [+] | | | [+] | | | [+] | |  [  BAY   ]  | |ROOM | |   |      | |
| | CH1 | | | CH2 | | | CH3 | |  [########]  | +-----+ |   +------+ |
| +-----+ | +-----+ | +-----+ |              |         |            |
+=========+=========+=========+==============+=========+============+

SOUTH

+===========================================================================+
|                              LEGEND                                        |
+===========================================================================+
| NODES:                    | PATHS:                    | ZONES:             |
| *  Intersection           | ==== Main Aisle (2-way)   | BULK = Bulk Store  |
| .  Path segment           | ---- Storage Aisle (1-way)| PICK = Picking     |
| [] Storage position       | .... Cross path           | PACK = Packing     |
| [+] Charging position     |                           |                    |
| /\ Dock door              | INFRASTRUCTURE:           | SYMBOLS:           |
|                           | CHG = Charging Station    | [#] = Obstacle     |
| NODE IDS:                 | DK  = Dock Door           | === = Wall         |
| MA = Main Aisle           | MAINT = Maintenance       |                    |
| CA = Cross Aisle          | CTRL = Control Room       |                    |
| R  = Rack position        |                           |                    |
| D  = Dock position        |                           |                    |
| S  = Staging position     |                           |                    |
| CH = Charging station     |                           |                    |
+===========================================================================+
```

### 6.2 Detailed Zone View: Storage Aisle

```
STORAGE AISLE DETAIL (One Aisle Section)
=========================================

Direction of travel: One-way (arrows show direction)

       RACK ROW (Left Side)                    RACK ROW (Right Side)
    +-----+-----+-----+-----+              +-----+-----+-----+-----+
    |Pallet|Pallet|Pallet|Pallet|              |Pallet|Pallet|Pallet|Pallet|
    |Pos  |Pos  |Pos  |Pos  |              |Pos  |Pos  |Pos  |Pos  |
    | L1  | L2  | L3  | L4  |              | R1  | R2  | R3  | R4  |
    +--+--+--+--+--+--+--+--+              +--+--+--+--+--+--+--+--+
       |     |     |     |                    |     |     |     |
       v     v     v     v                    v     v     v     v
    +--O--+--O--+--O--+--O--+--- 3.0m ---+--O--+--O--+--O--+--O--+
    |     |     |     |     |   AISLE    |     |     |     |     |
    | N1  | N2  | N3  | N4  |   WIDTH    | N5  | N6  | N7  | N8  |
    +--+--+--+--+--+--+--+--+============+--+--+--+--+--+--+--+--+
       |     |     |     |                    |     |     |     |
   ----+-----+-----+-----+---->  TRAVEL  <----+-----+-----+-----+---
       |     |     |     |     DIRECTION      |     |     |     |
    +--+--+--+--+--+--+--+--+            +--+--+--+--+--+--+--+--+
    |     |     |     |     |            |     |     |     |     |
    | N9  | N10 | N11 | N12 |            | N13 | N14 | N15 | N16 |
    +--O--+--O--+--O--+--O--+            +--O--+--O--+--O--+--O--+
       ^     ^     ^     ^                    ^     ^     ^     ^
       |     |     |     |                    |     |     |     |
    +-----+-----+-----+-----+              +-----+-----+-----+-----+
    |Pallet|Pallet|Pallet|Pallet|              |Pallet|Pallet|Pallet|Pallet|
    |Pos  |Pos  |Pos  |Pos  |              |Pos  |Pos  |Pos  |Pos  |
    | L5  | L6  | L7  | L8  |              | R5  | R6  | R7  | R8  |
    +-----+-----+-----+-----+              +-----+-----+-----+-----+

Node Spacing: 2.4m (matches pallet bay pitch)
Aisle Width:  3.0m (single AGV width + clearance)
```

### 6.3 Detailed Zone View: Intersection

```
INTERSECTION DETAIL (Main Aisle x Cross Aisle)
==============================================

                         |     |
                         |     |
        CROSS AISLE      | 4.0m|      CROSS AISLE
        (West)           |     |      (East)
                         |     |
    -----+-------+-------+-----+-------+-------+-----
         |       |       |     |       |       |
         |  [P1] | [P2]  |     | [P3]  | [P4]  |      Pre-intersection
         |   .   |   .   |     |   .   |   .   |      queue positions
    -----+---+---+---+---+-----+---+---+---+---+-----
         |   |       |   |     |   |       |   |
    =====v===v=======v===*=====*===v=======v===v=====
         |   |   ->      | (*) |      <-   |   |      MAIN AISLE
    =====^===^=======^===*=====*===^=======^===^=====  (5.0m width)
         |   |       |   |     |   |       |   |
    -----+---+---+---+---+-----+---+---+---+---+-----
         |  [P5] | [P6]  |     | [P7]  | [P8]  |      Post-intersection
         |   .   |   .   |     |   .   |   .   |      queue positions
         |       |       |     |       |       |
    -----+-------+-------+-----+-------+-------+-----
                         |     |
        CROSS AISLE      |     |      CROSS AISLE
        (continued)      | 4.0m|      (continued)
                         |     |
                         v     v

    (*) = Intersection Node (decision point)
    [Pn] = Queue/Buffer positions for traffic management

    Traffic Rules at this intersection:
    1. Main aisle has priority (North-South flow)
    2. Cross aisle traffic must yield
    3. Maximum 1 AGV in intersection at a time
    4. Queue positions hold waiting AGVs
```

### 6.4 Detailed Zone View: Charging Area

```
CHARGING STATION CLUSTER DETAIL
================================

    +===========================================================+
    |                    CHARGING ZONE                          |
    +===========================================================+
    |                                                           |
    |   APPROACH LANE                                           |
    |   ===================>                                    |
    |                                                           |
    |   +---+     +---+     +---+     +---+     +---+          |
    |   |APP|     |APP|     |APP|     |APP|     |APP|          |
    |   | 1 |     | 2 |     | 3 |     | 4 |     | 5 |  Approach |
    |   +---+     +---+     +---+     +---+     +---+  Nodes    |
    |     |         |         |         |         |             |
    |     v         v         v         v         v             |
    |   +---+     +---+     +---+     +---+     +---+           |
    |   |[+]|     |[+]|     |[+]|     |[+]|     |[+]|  Charge   |
    |   |CH1|     |CH2|     |CH3|     |CH4|     |CH5|  Nodes    |
    |   +---+     +---+     +---+     +---+     +---+           |
    |     |         |         |         |         |             |
    |   +===+     +===+     +===+     +===+     +===+           |
    |   |   |     |   |     |   |     |   |     |   |  Charger  |
    |   |CHG|     |CHG|     |CHG|     |CHG|     |CHG|  Units    |
    |   |   |     |   |     |   |     |   |     |   |           |
    |   +===+     +===+     +===+     +===+     +===+           |
    |     ^         ^         ^         ^         ^             |
    |     |         |         |         |         |             |
    |   +---+     +---+     +---+     +---+     +---+           |
    |   |DEP|     |DEP|     |DEP|     |DEP|     |DEP|  Depart   |
    |   | 1 |     | 2 |     | 3 |     | 4 |     | 5 |  Nodes    |
    |   +---+     +---+     +---+     +---+     +---+           |
    |     |         |         |         |         |             |
    |     v         v         v         v         v             |
    |   <===========================================            |
    |   DEPARTURE LANE                                          |
    |                                                           |
    +===========================================================+

    Station Spacing: 3.0m center-to-center
    Approach Lane Width: 2.5m
    Total Zone Depth: 8.0m

    Node Sequence for Charging:
    1. AGV approaches via approach lane
    2. Turns into APP node (approach position)
    3. Docks at CH node (charging position)
    4. After charge, backs to DEP node (departure position)
    5. Exits via departure lane
```

### 6.5 Grid Coordinate System Example

```
GRID COORDINATE SYSTEM
======================

    A     B     C     D     E     F     G     H     I     J
    |     |     |     |     |     |     |     |     |     |
1 --+-----+-----+-----+-----+-----+-----+-----+-----+-----+-- 1
    |     |     |     |     |     |     |     |     |     |
    |  DK1   DK2       STAGING AREA        DK3   DK4      |
    |     |     |     |     |     |     |     |     |     |
2 --+-----+-----+-----+-----+-----+-----+-----+-----+-----+-- 2
    |     |     |     |     |     |     |     |     |     |
    |     |     |   MAIN AISLE NORTH    |     |     |     |
    |     |     |     |     |     |     |     |     |     |
3 --+-----+=====+=====+=====+=====+=====+=====+=====+-----+-- 3
    |     ||    |     |     |     |     |     |    ||     |
    |BULK || RACK STORAGE ZONE A             |    ||BULK |
    |     ||    |     |     |     |     |     |    ||     |
4 --+-----+=====+=====+=====+=====+=====+=====+=====+-----+-- 4
    |     ||    |     |     |     |     |     |    ||     |
    |STOR.||    |     |     |     |     |     |    ||STOR.|
    |     ||    |     |     |     |     |     |    ||     |
5 --+-----+=====+=====+=====+=====+=====+=====+=====+-----+-- 5
    |     |     |     |     |     |     |     |     |     |
    |     |   CROSS AISLE                     |     |     |
    |     |     |     |     |     |     |     |     |     |
6 --+-----+=====+=====+=====+=====+=====+=====+=====+-----+-- 6
    |     ||    |     |     |     |     |     |    ||     |
    |BULK || RACK STORAGE ZONE B             |    ||PICK/|
    |     ||    |     |     |     |     |     |    ||PACK |
7 --+-----+=====+=====+=====+=====+=====+=====+=====+-----+-- 7
    |     ||    |     |     |     |     |     |    ||     |
    |STOR.||    |     |     |     |     |     |    ||     |
    |     ||    |     |     |     |     |     |    ||     |
8 --+-----+=====+=====+=====+=====+=====+=====+=====+-----+-- 8
    |     |     |     |     |     |     |     |     |     |
    |     |   MAIN AISLE SOUTH              |     |     |
    |     |     |     |     |     |     |     |     |     |
9 --+-----+-----+-----+-----+-----+-----+-----+-----+-----+-- 9
    |     |     |     |     |     |     |     |     |     |
    | CHG | CHG | CHG |  MAINTENANCE  | CTRL | OFFICE    |
    |     |     |     |     |     |     |     |     |     |
10--+-----+-----+-----+-----+-----+-----+-----+-----+-----+--10
    |     |     |     |     |     |     |     |     |     |
    A     B     C     D     E     F     G     H     I     J


COORDINATE EXAMPLES:
- Dock Door 1:     A1
- Main Aisle intersection at row 3: D3
- Storage position:  C4 (Rack Zone A, left side)
- Cross Aisle center: E5
- Charging Station 2: B9
- Pick/Pack Area:    J6-J7

GRID SPECIFICATIONS:
- Cell Size: 5m x 6m (50m / 10 columns, 60m / 10 rows)
- Total Cells: 100
- Node density: ~170 nodes across grid
```

---

## Appendix A: Quick Reference Card

```
+===========================================================================+
|              AGV WAREHOUSE LAYOUT - QUICK REFERENCE                       |
+===========================================================================+
|                                                                           |
| MINIMUM DIMENSIONS                | RECOMMENDED RATIOS                    |
| --------------------------------- | ------------------------------------- |
| Main Aisle Width:    4.0-6.0m     | Storage:        40-55% of floor area  |
| Cross Aisle Width:   3.0-4.0m     | Movement:       12-18% of floor area  |
| Storage Aisle:       2.4-3.5m     | Operations:     15-25% of floor area  |
| Charging Station:    3.0 x 4.0m   | Infrastructure: 4-8% of floor area    |
|                                   |                                       |
| NODE DENSITY GUIDELINES           | AGV FLEET SIZING                      |
| --------------------------------- | ------------------------------------- |
| Storage Aisle:  1 per 2.4-3.0m    | Small (<5,000sqm):   3-8 AGVs        |
| Main Aisle:     1 per 10-15m      | Medium (5-15k sqm):  8-20 AGVs       |
| Intersections:  1 per crossing    | Large (>15,000sqm):  20-60 AGVs      |
| Staging:        1 per position    |                                       |
|                                   | Charging ratio: 1 station : 3-5 AGVs  |
| SPEED LIMITS                      |                                       |
| --------------------------------- | PATH DESIGNATION                      |
| Main Aisle:     1.5-2.0 m/s       | ------------------------------------- |
| Cross Aisle:    1.0-1.5 m/s       | One-way: Aisles < 3.5m width         |
| Storage Aisle:  0.5-1.0 m/s       | Two-way: Aisles > 4.0m width         |
| Near humans:    0.3-0.5 m/s       | Priority: Main > Cross > Storage     |
|                                                                           |
+===========================================================================+
```

---

## Appendix B: Conversion Formulas

### Floor Area Calculations

```
Total Navigable Area = Total Floor Area - (Obstacles + Walls + Fixed Equipment)

Storage Capacity (pallets) = Storage Zone Area / (Pallet Footprint + Aisle Allowance)
    where Pallet Footprint = 1.2m x 1.0m (EUR pallet)
    and Aisle Allowance = 0.5 * Aisle Width * Pallet Depth

AGV Fleet Size (minimum) = (Peak Hourly Throughput * Avg Cycle Time) / 60
    where Cycle Time = Travel Time + Load/Unload Time + Queue Time
```

### Node Count Estimation

```
Total Nodes = Storage Nodes + Transit Nodes + Infrastructure Nodes

Storage Nodes = Number of Rack Bays * 2 (both sides of aisle)
Transit Nodes = (Main Aisle Length / 10m) + (Cross Aisles * Intersections) + Zone Boundaries
Infrastructure Nodes = (Charging Stations * 2) + (Dock Doors * 2) + (Workstations * 3)
```

### Charging Station Sizing

```
Minimum Charging Stations = Fleet Size / 3  (opportunity charging)
Recommended Charging Stations = Fleet Size / 2  (with buffer)

Charging Time Required = (Battery Capacity * Discharge Rate) / Charger Output
    where typical Discharge Rate = 15-20% per hour of operation
```

---

*Document Version: 1.0*
*Created: 2026-01-11*
*Framework for AGV Warehouse Retrofit Planning*
