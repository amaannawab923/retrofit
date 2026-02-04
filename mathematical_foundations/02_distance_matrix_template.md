# Distance Matrix Template
## Sample Warehouse Configuration (12+ Nodes)

---

## 1. Warehouse Layout Definition

### 1.1 Node Configuration

**Sample Legacy Warehouse: 12-Node Configuration**

```
    [N01]----[N02]----[N03]----[N04]
      |        |        |        |
    [N05]----[N06]----[N07]----[N08]
      |        |        |        |
    [N09]----[N10]----[N11]----[N12]

Legend:
  N01-N04: Receiving Zone (Row 1)
  N05-N08: Storage Zone (Row 2)
  N09-N12: Shipping Zone (Row 3)
```

### 1.2 Node Definitions Table

| Node ID | X Coord | Y Coord | Zone Type | Description |
|---------|---------|---------|-----------|-------------|
| N01 | 0 | 20 | Receiving | Dock Door 1 |
| N02 | 10 | 20 | Receiving | Dock Door 2 |
| N03 | 20 | 20 | Receiving | Dock Door 3 |
| N04 | 30 | 20 | Receiving | Dock Door 4 |
| N05 | 0 | 10 | Storage | Aisle A Start |
| N06 | 10 | 10 | Storage | Aisle B Start |
| N07 | 20 | 10 | Storage | Aisle C Start |
| N08 | 30 | 10 | Storage | Aisle D Start |
| N09 | 0 | 0 | Shipping | Outbound 1 |
| N10 | 10 | 0 | Shipping | Outbound 2 |
| N11 | 20 | 0 | Shipping | Outbound 3 |
| N12 | 30 | 0 | Shipping | Outbound 4 |

---

## 2. Node-to-Node Distance Matrix

### 2.1 Manhattan Distance Matrix (meters)

|     | N01 | N02 | N03 | N04 | N05 | N06 | N07 | N08 | N09 | N10 | N11 | N12 |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| N01 | 0   | 10  | 20  | 30  | 10  | 20  | 30  | 40  | 20  | 30  | 40  | 50  |
| N02 | 10  | 0   | 10  | 20  | 20  | 10  | 20  | 30  | 30  | 20  | 30  | 40  |
| N03 | 20  | 10  | 0   | 10  | 30  | 20  | 10  | 20  | 40  | 30  | 20  | 30  |
| N04 | 30  | 20  | 10  | 0   | 40  | 30  | 20  | 10  | 50  | 40  | 30  | 20  |
| N05 | 10  | 20  | 30  | 40  | 0   | 10  | 20  | 30  | 10  | 20  | 30  | 40  |
| N06 | 20  | 10  | 20  | 30  | 10  | 0   | 10  | 20  | 20  | 10  | 20  | 30  |
| N07 | 30  | 20  | 10  | 20  | 20  | 10  | 0   | 10  | 30  | 20  | 10  | 20  |
| N08 | 40  | 30  | 20  | 10  | 30  | 20  | 10  | 0   | 40  | 30  | 20  | 10  |
| N09 | 20  | 30  | 40  | 50  | 10  | 20  | 30  | 40  | 0   | 10  | 20  | 30  |
| N10 | 30  | 20  | 30  | 40  | 20  | 10  | 20  | 30  | 10  | 0   | 10  | 20  |
| N11 | 40  | 30  | 20  | 30  | 30  | 20  | 10  | 20  | 20  | 10  | 0   | 10  |
| N12 | 50  | 40  | 30  | 20  | 40  | 30  | 20  | 10  | 30  | 20  | 10  | 0   |

### 2.2 Python Implementation for Distance Matrix

```python
import numpy as np
import pandas as pd

class WarehouseDistanceMatrix:
    """
    Generates and manages distance matrices for warehouse layout.
    """

    def __init__(self, nodes: dict):
        """
        Initialize with node definitions.

        Args:
            nodes: Dictionary mapping node_id -> (x, y, zone_type)
        """
        self.nodes = nodes
        self.node_ids = list(nodes.keys())
        self.n_nodes = len(self.node_ids)
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
                matrix[i, j] = abs(x_i - x_j) + abs(y_i - y_j)
        self.manhattan_matrix = matrix
        return matrix

    def calculate_euclidean_matrix(self) -> np.ndarray:
        """Calculate Euclidean distance matrix."""
        matrix = np.zeros((self.n_nodes, self.n_nodes))
        for i, id_i in enumerate(self.node_ids):
            for j, id_j in enumerate(self.node_ids):
                x_i, y_i, _ = self.nodes[id_i]
                x_j, y_j, _ = self.nodes[id_j]
                matrix[i, j] = np.sqrt((x_i - x_j)**2 + (y_i - y_j)**2)
        self.euclidean_matrix = matrix
        return matrix

    def calculate_weighted_matrix(self, zone_weights: dict) -> np.ndarray:
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
                # Average weight of origin and destination zones
                avg_weight = (zone_weights.get(zone_i, 1.0) +
                             zone_weights.get(zone_j, 1.0)) / 2
                matrix[i, j] = self.manhattan_matrix[i, j] * avg_weight
        self.weighted_matrix = matrix
        return matrix

    def to_dataframe(self, matrix: np.ndarray) -> pd.DataFrame:
        """Convert matrix to pandas DataFrame for export."""
        return pd.DataFrame(matrix, index=self.node_ids, columns=self.node_ids)

    def export_to_csv(self, matrix: np.ndarray, filepath: str):
        """Export distance matrix to CSV file."""
        df = self.to_dataframe(matrix)
        df.to_csv(filepath)

    def export_to_excel(self, filepath: str):
        """Export all matrices to Excel workbook."""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if self.manhattan_matrix is not None:
                self.to_dataframe(self.manhattan_matrix).to_excel(
                    writer, sheet_name='Manhattan')
            if self.euclidean_matrix is not None:
                self.to_dataframe(self.euclidean_matrix).to_excel(
                    writer, sheet_name='Euclidean')
            if self.weighted_matrix is not None:
                self.to_dataframe(self.weighted_matrix).to_excel(
                    writer, sheet_name='Weighted')


# Example Usage
if __name__ == "__main__":
    # Define 12-node warehouse
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
        'Receiving': 1.2,  # Busy dock area
        'Storage': 1.0,    # Standard aisles
        'Shipping': 1.3,   # High activity
    }

    warehouse = WarehouseDistanceMatrix(nodes)
    manhattan = warehouse.calculate_manhattan_matrix()
    euclidean = warehouse.calculate_euclidean_matrix()
    weighted = warehouse.calculate_weighted_matrix(zone_weights)

    print("Manhattan Distance Matrix:")
    print(warehouse.to_dataframe(manhattan))
```

---

## 3. Zone-to-Zone Aggregated Distances

### 3.1 Zone Aggregation Formula

```
D_zone(Z_i, Z_j) = (1/|Z_i| * |Z_j|) * sum_{a in Z_i} sum_{b in Z_j} d(a, b)
```

### 3.2 Zone-to-Zone Distance Matrix

| Origin Zone | Receiving | Storage | Shipping |
|-------------|-----------|---------|----------|
| Receiving   | 15.0      | 22.5    | 35.0     |
| Storage     | 22.5      | 15.0    | 22.5     |
| Shipping    | 35.0      | 22.5    | 15.0     |

### 3.3 Python Implementation

```python
def calculate_zone_aggregated_distances(
    nodes: dict,
    distance_matrix: np.ndarray,
    node_ids: list
) -> pd.DataFrame:
    """
    Calculate zone-to-zone aggregated distance matrix.

    Args:
        nodes: Dictionary mapping node_id -> (x, y, zone_type)
        distance_matrix: Node-to-node distance matrix
        node_ids: Ordered list of node IDs matching matrix indices

    Returns:
        DataFrame with zone-to-zone average distances
    """
    # Group nodes by zone
    zones = {}
    for node_id, (x, y, zone) in nodes.items():
        if zone not in zones:
            zones[zone] = []
        zones[zone].append(node_ids.index(node_id))

    zone_names = list(zones.keys())
    n_zones = len(zone_names)
    zone_matrix = np.zeros((n_zones, n_zones))

    for i, zone_i in enumerate(zone_names):
        for j, zone_j in enumerate(zone_names):
            indices_i = zones[zone_i]
            indices_j = zones[zone_j]
            total = 0.0
            count = 0
            for idx_i in indices_i:
                for idx_j in indices_j:
                    total += distance_matrix[idx_i, idx_j]
                    count += 1
            zone_matrix[i, j] = total / count if count > 0 else 0.0

    return pd.DataFrame(zone_matrix, index=zone_names, columns=zone_names)
```

---

## 4. Critical Path Identification

### 4.1 Critical Path Criteria

A path is considered critical if:
1. **High Frequency**: Used by > 20% of all tasks
2. **Single Point of Failure**: No alternative routes available
3. **Bottleneck Potential**: Capacity < average demand

### 4.2 Critical Path Analysis Table

| Path | From | To | Distance | Daily Trips | Congestion Risk | Alternatives |
|------|------|----|----------|-------------|-----------------|--------------|
| P01 | N01 | N06 | 20m | 85 | HIGH | P02, P03 |
| P02 | N02 | N06 | 10m | 120 | CRITICAL | None |
| P03 | N06 | N10 | 10m | 150 | CRITICAL | P04 |
| P04 | N06 | N11 | 20m | 45 | MEDIUM | P03, P05 |
| P05 | N03 | N07 | 10m | 95 | HIGH | P06 |
| P06 | N07 | N11 | 10m | 110 | HIGH | P05 |

### 4.3 Critical Path Detection Algorithm

```python
def identify_critical_paths(
    distance_matrix: np.ndarray,
    task_frequency: dict,
    path_capacity: dict,
    threshold_frequency: float = 0.2,
    threshold_utilization: float = 0.8
) -> list:
    """
    Identify critical paths in the warehouse.

    Args:
        distance_matrix: Node-to-node distances
        task_frequency: Dict mapping (origin, dest) -> task count
        path_capacity: Dict mapping (origin, dest) -> max throughput
        threshold_frequency: Fraction of total tasks to be considered high-frequency
        threshold_utilization: Utilization ratio to be considered bottleneck

    Returns:
        List of critical path tuples with analysis
    """
    total_tasks = sum(task_frequency.values())
    critical_paths = []

    for (origin, dest), count in task_frequency.items():
        frequency_ratio = count / total_tasks
        capacity = path_capacity.get((origin, dest), float('inf'))
        utilization = count / capacity if capacity > 0 else float('inf')

        is_high_frequency = frequency_ratio >= threshold_frequency
        is_bottleneck = utilization >= threshold_utilization

        if is_high_frequency or is_bottleneck:
            critical_paths.append({
                'path': (origin, dest),
                'distance': distance_matrix[origin, dest],
                'daily_trips': count,
                'frequency_ratio': frequency_ratio,
                'utilization': utilization,
                'risk_level': 'CRITICAL' if (is_high_frequency and is_bottleneck)
                              else 'HIGH' if is_bottleneck else 'MEDIUM'
            })

    return sorted(critical_paths, key=lambda x: x['utilization'], reverse=True)
```

---

## 5. Excel Template Structure

### 5.1 Node Definition Sheet

```
| A        | B       | C       | D          | E           |
|----------|---------|---------|------------|-------------|
| Node_ID  | X_Coord | Y_Coord | Zone_Type  | Description |
| N01      | 0       | 20      | Receiving  | Dock Door 1 |
| N02      | 10      | 20      | Receiving  | Dock Door 2 |
| ...      | ...     | ...     | ...        | ...         |
```

### 5.2 Distance Matrix Sheet

```
| A      | B    | C    | D    | ... |
|--------|------|------|------|-----|
|        | N01  | N02  | N03  | ... |
| N01    | 0    | =ABS($B2-C$1)+ABS($C2-C$2) | ... |
| N02    | =... | 0    | ...  | ... |
```

### 5.3 Zone Matrix Sheet (Excel Formulas)

```
=AVERAGEIFS(DistanceMatrix!$B$2:$M$13,
            NodeDef!$D$2:$D$13, A2,
            NodeDef!$D$2:$D$13, B$1)
```

---

## 6. Multigraph Representation

Based on Layout A's multigraph G = (N, E):

### 6.1 Edge Definition

```python
class WarehouseMultigraph:
    """
    Multigraph representation allowing multiple edges between nodes.
    """

    def __init__(self):
        self.nodes = {}  # node_id -> node_attributes
        self.edges = {}  # edge_id -> edge_attributes

    def add_node(self, node_id: str, x: float, y: float, zone: str):
        """Add a node to the graph."""
        self.nodes[node_id] = {
            'x': x,
            'y': y,
            'zone': zone
        }

    def add_edge(self, edge_id: str, from_node: str, to_node: str,
                 edge_type: str, capacity: int, bidirectional: bool = True):
        """
        Add an edge to the graph.

        Args:
            edge_id: Unique edge identifier
            from_node: Origin node ID
            to_node: Destination node ID
            edge_type: 'aisle', 'cross_aisle', 'open_area'
            capacity: Maximum AGVs allowed on edge
            bidirectional: Whether edge allows travel in both directions
        """
        from_coords = (self.nodes[from_node]['x'], self.nodes[from_node]['y'])
        to_coords = (self.nodes[to_node]['x'], self.nodes[to_node]['y'])
        length = abs(from_coords[0] - to_coords[0]) + abs(from_coords[1] - to_coords[1])

        self.edges[edge_id] = {
            'from': from_node,
            'to': to_node,
            'type': edge_type,
            'length': length,
            'capacity': capacity,
            'bidirectional': bidirectional,
            'current_agvs': 0
        }
```
