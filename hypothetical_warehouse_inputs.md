# Hypothetical Warehouse Layout Inputs
## Sample Dimensions for Retrofit Framework Validation

---

## Overview

These are hypothetical warehouse dimensions designed to test the Legacy Warehouse Retrofit Framework across three distinct layout types:

| Layout | Type | Complexity | Use Case |
|--------|------|------------|----------|
| Layout A | Structured | Low | Modern distribution center |
| Layout B | Compact | Medium | High-density storage |
| Layout C | Retrofit | High | Legacy industrial facility |

---

## Layout A: Structured Layout

**Characteristics:** Wide aisles, regular spacing, optimal for AGV navigation

### Dimensions
| Parameter | Value | Unit |
|-----------|-------|------|
| Aisle Width | 3.0 | meters |
| Aisle Length | 50 | meters |
| Number of Aisles | 5 | count |
| Total Floor Area | ~1,000 | sqm (estimated) |

### Zones
| Zone | Dimensions | Location |
|------|------------|----------|
| Pickup Zone | 5m x 5m (25 sqm) | Bottom-left corner |
| Drop Zone | 5m x 5m (25 sqm) | Top-right corner |

### Layout Sketch
```
+--------------------------------------------------+
|                                          [DROP]  |
|  =========================================  5x5  |
|  =========================================       |
|  =========================================       |
|  =========================================       |
|  =========================================       |
|                                                  |
| [PICKUP]                                         |
|   5x5                                            |
+--------------------------------------------------+
     |<-------- 5 aisles x 50m long -------->|
```

---

## Layout B: Compact Layout

**Characteristics:** Narrow aisles, high density, center-positioned zones

### Dimensions
| Parameter | Value | Unit |
|-----------|-------|------|
| Aisle Width | 2.0 | meters |
| Aisle Length | 30 | meters |
| Number of Aisles | 8 | count |
| Total Floor Area | ~720 | sqm (estimated) |

### Zones
| Zone | Dimensions | Location |
|------|------------|----------|
| Pickup Zone | 4m x 4m (16 sqm) | Center |
| Drop Zone | 4m x 4m (16 sqm) | Opposite center |

### Layout Sketch
```
+----------------------------------------+
|  ====  ====  ====  ====  ====  ====   |
|  ====  ====  ====  ====  ====  ====   |
|  ====  ==== [PICKUP] ====  ====  ====  |
|  ====  ====   4x4   ====  ====  ====  |
|  ====  ====  ====  ====  ====  ====   |
|  ====  ====  ====  [DROP] ====  ====  |
|  ====  ====  ====   4x4  ====  ====   |
|  ====  ====  ====  ====  ====  ====   |
+----------------------------------------+
   |<-- 8 aisles x 30m, 2m wide -->|
```

---

## Layout C: Retrofit Layout (Legacy Industrial)

**Characteristics:** Irregular spacing, variable aisle lengths, near dock/production areas

### Dimensions
| Parameter | Value | Unit |
|-----------|-------|------|
| Aisle Width | 2.5 | meters |
| Aisle Length | 40-60 (variable) | meters |
| Number of Aisles | 6 | count |
| Aisle Spacing | Irregular | - |
| Total Floor Area | ~1,200 | sqm (estimated) |

### Zones
| Zone | Dimensions | Location |
|------|------------|----------|
| Pickup Zone | 6m x 6m (36 sqm) | Near loading dock |
| Drop Zone | 6m x 6m (36 sqm) | Near production area |

### Layout Sketch
```
+--------------------------------------------------------+
| [LOADING DOCK]                                          |
| [PICKUP 6x6]                                            |
|                                                         |
|  ============  (60m)                                    |
|  ==========    (50m)                                    |
|  ============  (55m)        [PRODUCTION AREA]          |
|  ========      (40m)              [DROP 6x6]           |
|  ==========    (50m)                                    |
|  ============  (60m)                                    |
|                                                         |
|  |<-- 6 aisles, irregular lengths, 2.5m wide -->|      |
+--------------------------------------------------------+
```

### Legacy Constraints (Typical)
- Support columns at irregular intervals
- Floor load variations
- Existing equipment that cannot be moved
- Mixed human/AGV traffic zones

---

## Comparative Summary

| Attribute | Layout A | Layout B | Layout C |
|-----------|----------|----------|----------|
| Aisle Width | 3.0m | 2.0m | 2.5m |
| Aisle Length | 50m (uniform) | 30m (uniform) | 40-60m (variable) |
| Aisles | 5 | 8 | 6 |
| Est. Area | ~1,000 sqm | ~720 sqm | ~1,200 sqm |
| Pickup Zone | 25 sqm | 16 sqm | 36 sqm |
| Drop Zone | 25 sqm | 16 sqm | 36 sqm |
| Complexity | Low | Medium | High |
| Regularity | High | High | Low |

---

## Simulation Parameters (Proposed)

Based on the framework defaults:

| Parameter | Value | Notes |
|-----------|-------|-------|
| AGV Count | 5 | Standard test fleet |
| AGV Speed | 1.0 m/s | Conservative speed |
| Turn Delay | 2.0 s | Per 90-degree turn |
| Task Rate | 1 per 20s | 3 tasks/minute |
| Pick Time | 15s | At pickup zone |
| Drop Time | 10s | At drop zone |

---

*Document created for retrofit framework validation*
*These are hypothetical dimensions for simulation purposes*
