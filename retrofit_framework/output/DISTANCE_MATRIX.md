# Distance Matrix - Layout A

## Floyd-Warshall Algorithm Output

This table shows the **shortest path distance (in meters)** between any two navigation nodes in the warehouse.

---

## Node Reference

| Short          | Full Name          | Type        | Coordinates  |
| -------------- | ------------------ | ----------- | ------------ |
| **PICK** | node_pickup        | Pickup      | (2.5, 2.5)   |
| **DROP** | node_drop          | Drop        | (17.5, 57.5) |
|                |                    |             |              |
| **A1E**  | node_aisle_1_entry | Aisle Entry | (8.3, 5.0)   |
| **A1M**  | node_aisle_1_mid   | Waypoint    | (8.3, 30.0)  |
| **A1X**  | node_aisle_1_exit  | Aisle Exit  | (8.3, 55.0)  |
| **A2E**  | node_aisle_2_entry | Aisle Entry | (10.7, 5.0)  |
| **A2M**  | node_aisle_2_mid   | Waypoint    | (10.7, 30.0) |
| **A2X**  | node_aisle_2_exit  | Aisle Exit  | (10.7, 55.0) |
| **A3E**  | node_aisle_3_entry | Aisle Entry | (13.0, 5.0)  |
| **A3M**  | node_aisle_3_mid   | Waypoint    | (13.0, 30.0) |
| **A3X**  | node_aisle_3_exit  | Aisle Exit  | (13.0, 55.0) |
| **A4E**  | node_aisle_4_entry | Aisle Entry | (15.3, 5.0)  |
| **A4M**  | node_aisle_4_mid   | Waypoint    | (15.3, 30.0) |
| **A4X**  | node_aisle_4_exit  | Aisle Exit  | (15.3, 55.0) |
| **A5E**  | node_aisle_5_entry | Aisle Entry | (17.7, 5.0)  |
| **A5M**  | node_aisle_5_mid   | Waypoint    | (17.7, 30.0) |
| **A5X**  | node_aisle_5_exit  | Aisle Exit  | (17.7, 55.0) |

---

## How to Read This Table

1. Find your **starting location** in the left column (rows)
2. Find your **destination** in the top row (columns)
3. The intersecting cell shows the **shortest path distance in meters**

**Example:** Robot at PICKUP wants to reach DROP → Find PICK row, DROP column → **68.18 meters**

---

## Distance Matrix (17 × 17)

| From \ To      | **PICK** | **DROP** | **A1E** | **A1M** | **A1X** | **A2E** | **A2M** | **A2X** | **A3E** | **A3M** | **A3X** | **A4E** | **A4M** | **A4X** | **A5E** | **A5M** | **A5X** |
| -------------- | -------------- | -------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| **PICK** | --             | 68.2           | 6.3           | 31.4          | 56.4          | 8.7           | 33.7          | 58.7          | 11.0          | 36.0          | 61.0          | 13.3          | 38.3          | 63.3          | 15.7          | 40.7          | 65.7          |
| **DROP** | 68.2           | --             | 61.8          | 36.8          | 11.8          | 59.5          | 34.5          | 9.5           | 57.2          | 32.2          | 7.2           | 54.8          | 29.8          | 4.8           | 52.5          | 27.5          | 2.5           |
| **A1E**  | 6.3            | 61.8           | --            | 25.0          | 50.0          | 2.3           | 27.3          | 52.3          | 4.7           | 29.7          | 54.7          | 7.0           | 32.0          | 57.0          | 9.3           | 34.3          | 59.3          |
| **A1M**  | 31.4           | 36.8           | 25.0          | --            | 25.0          | 27.3          | 2.3           | 27.3          | 29.7          | 4.7           | 29.7          | 32.0          | 7.0           | 32.0          | 34.3          | 9.3           | 34.3          |
| **A1X**  | 56.4           | 11.8           | 50.0          | 25.0          | --            | 52.3          | 27.3          | 2.3           | 54.7          | 29.7          | 4.7           | 57.0          | 32.0          | 7.0           | 59.3          | 34.3          | 9.3           |
| **A2E**  | 8.7            | 59.5           | 2.3           | 27.3          | 52.3          | --            | 25.0          | 50.0          | 2.3           | 27.3          | 52.3          | 4.7           | 29.7          | 54.7          | 7.0           | 32.0          | 57.0          |
| **A2M**  | 33.7           | 34.5           | 27.3          | 2.3           | 27.3          | 25.0          | --            | 25.0          | 27.3          | 2.3           | 27.3          | 29.7          | 4.7           | 29.7          | 32.0          | 7.0           | 32.0          |
| **A2X**  | 58.7           | 9.5            | 52.3          | 27.3          | 2.3           | 50.0          | 25.0          | --            | 52.3          | 27.3          | 2.3           | 54.7          | 29.7          | 4.7           | 57.0          | 32.0          | 7.0           |
| **A3E**  | 11.0           | 57.2           | 4.7           | 29.7          | 54.7          | 2.3           | 27.3          | 52.3          | --            | 25.0          | 50.0          | 2.3           | 27.3          | 52.3          | 4.7           | 29.7          | 54.7          |
| **A3M**  | 36.0           | 32.2           | 29.7          | 4.7           | 29.7          | 27.3          | 2.3           | 27.3          | 25.0          | --            | 25.0          | 27.3          | 2.3           | 27.3          | 29.7          | 4.7           | 29.7          |
| **A3X**  | 61.0           | 7.2            | 54.7          | 29.7          | 4.7           | 52.3          | 27.3          | 2.3           | 50.0          | 25.0          | --            | 52.3          | 27.3          | 2.3           | 54.7          | 29.7          | 4.7           |
| **A4E**  | 13.3           | 54.8           | 7.0           | 32.0          | 57.0          | 4.7           | 29.7          | 54.7          | 2.3           | 27.3          | 52.3          | --            | 25.0          | 50.0          | 2.3           | 27.3          | 52.3          |
| **A4M**  | 38.3           | 29.8           | 32.0          | 7.0           | 32.0          | 29.7          | 4.7           | 29.7          | 27.3          | 2.3           | 27.3          | 25.0          | --            | 25.0          | 27.3          | 2.3           | 27.3          |
| **A4X**  | 63.3           | 4.8            | 57.0          | 32.0          | 7.0           | 54.7          | 29.7          | 4.7           | 52.3          | 27.3          | 2.3           | 50.0          | 25.0          | --            | 52.3          | 27.3          | 2.3           |
| **A5E**  | 15.7           | 52.5           | 9.3           | 34.3          | 59.3          | 7.0           | 32.0          | 57.0          | 4.7           | 29.7          | 54.7          | 2.3           | 27.3          | 52.3          | --            | 25.0          | 50.0          |
| **A5M**  | 40.7           | 27.5           | 34.3          | 9.3           | 34.3          | 32.0          | 7.0           | 32.0          | 29.7          | 4.7           | 29.7          | 27.3          | 2.3           | 27.3          | 25.0          | --            | 25.0          |
| **A5X**  | 65.7           | 2.5            | 59.3          | 34.3          | 9.3           | 57.0          | 32.0          | 7.0           | 54.7          | 29.7          | 4.7           | 52.3          | 27.3          | 2.3           | 50.0          | 25.0          | --            |

---

## Key Distances

| Route        | Distance | Description                        |
| ------------ | -------- | ---------------------------------- |
| PICK → DROP | 68.18m   | Maximum journey (corner to corner) |
| PICK → A1E  | 6.35m    | Pickup to nearest aisle            |
| DROP → A5X  | 2.51m    | Drop zone to nearest aisle exit    |
| A1E → A1X   | 50.0m    | Full aisle traversal               |
| A1E → A2E   | 2.33m    | Between adjacent aisle entries     |
| A1M → A2M   | 2.33m    | Between adjacent aisle midpoints   |

---

## Algorithm Details

**Algorithm Used:** Floyd-Warshall (All-Pairs Shortest Path)

**Time Complexity:** O(n³) where n = 17 nodes

**What it does:**

- Considers every possible intermediate node
- Finds the absolute shortest path between every pair of nodes
- Pre-computes all 17 × 17 = 289 possible distances

**Why it matters:**

- Robots get instant answers (O(1) lookup)
- No real-time path calculation needed
- Saves battery and processing power

---

*Generated from Layout A Conversion Output*
*Floyd-Warshall Algorithm Implementation*
