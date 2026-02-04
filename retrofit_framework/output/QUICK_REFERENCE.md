# Output Module - Quick Reference

## Import Statements

```python
# Import all functions
from output import (
    # Visualizer
    generate_ascii_layout,
    generate_node_map,
    format_distance_matrix,
    # Reports
    generate_conversion_report,
    generate_summary_stats,
    compare_layouts,
    # JSON Export
    export_warehouse_json,
    export_navigation_graph,
    export_distance_matrix,
)

# Or import from specific modules
from output.visualizer import generate_ascii_layout
from output.report_generator import generate_conversion_report
from output.json_exporter import save_warehouse_json
```

## Quick Function Reference

### Visualizer Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `generate_ascii_layout(warehouse)` | ASCII art of warehouse | str |
| `generate_node_map(nodes)` | Detailed node listing | str |
| `format_distance_matrix(matrix, node_ids, max_nodes)` | Formatted matrix table | str |
| `generate_simple_layout(warehouse)` | Simple text summary | str |

### Report Generator Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `generate_conversion_report(legacy, robotic, include_nodes, include_metrics)` | Full conversion report | str |
| `generate_summary_stats(robotic_warehouse)` | Statistics dictionary | dict |
| `compare_layouts(legacy, robotic, detailed)` | Side-by-side comparison | str |
| `generate_node_summary_report(nodes, title)` | Node summary | str |

### JSON Exporter Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `export_warehouse_json(warehouse, include_metadata, pretty)` | Complete JSON export | str |
| `export_navigation_graph(nodes, edges, include_positions)` | Graph JSON | str |
| `export_distance_matrix(matrix, node_ids, format_type)` | Matrix JSON | str |
| `save_warehouse_json(warehouse, filepath, include_metadata)` | Save to file | None |
| `load_warehouse_json(filepath)` | Load from file | dict |
| `export_legacy_warehouse_json(warehouse, pretty)` | Legacy warehouse JSON | str |

## Common Usage Patterns

### 1. Quick Visualization
```python
ascii_art = generate_ascii_layout(warehouse)
print(ascii_art)
```

### 2. Generate Full Report
```python
report = generate_conversion_report(
    legacy_warehouse,
    robotic_warehouse,
    include_nodes=True,
    include_metrics=True
)
print(report)
```

### 3. Get Statistics
```python
stats = generate_summary_stats(warehouse)
print(f"Nodes: {stats['total_nodes']}")
print(f"Edges: {stats['total_edges']}")
print(f"Node density: {stats['node_density_per_m2']:.3f} nodes/m²")
```

### 4. Export to JSON File
```python
save_warehouse_json(warehouse, 'output/warehouse.json')
```

### 5. Export Navigation Graph Only
```python
graph_json = export_navigation_graph(
    warehouse.nodes,
    warehouse.edges,
    include_positions=True
)
with open('nav_graph.json', 'w') as f:
    f.write(graph_json)
```

### 6. Compare Layouts
```python
comparison = compare_layouts(
    legacy_warehouse,
    robotic_warehouse,
    detailed=True
)
print(comparison)
```

### 7. Distance Matrix (Nested Format)
```python
matrix_json = export_distance_matrix(
    warehouse.distance_matrix,
    format_type='nested'
)
```

### 8. Distance Matrix (Flat Format)
```python
matrix_json = export_distance_matrix(
    warehouse.distance_matrix,
    format_type='flat'
)
```

## Parameter Reference

### visualizer.py

**`generate_ascii_layout(warehouse: RoboticWarehouse) -> str`**
- `warehouse`: RoboticWarehouse instance

**`generate_node_map(nodes: List[Node]) -> str`**
- `nodes`: List of Node instances

**`format_distance_matrix(matrix, node_ids, max_nodes) -> str`**
- `matrix`: Dict[str, Dict[str, float]] - Nested distance matrix
- `node_ids`: Optional[List[str]] - Nodes to include (default: all)
- `max_nodes`: Optional[int] - Max nodes to display (default: all)

### report_generator.py

**`generate_conversion_report(legacy, robotic, include_nodes, include_metrics) -> str`**
- `legacy`: LegacyWarehouse instance
- `robotic`: RoboticWarehouse instance
- `include_nodes`: bool = True - Include detailed node listing
- `include_metrics`: bool = True - Include conversion metrics

**`generate_summary_stats(robotic_warehouse) -> Dict[str, Any]`**
- `robotic_warehouse`: RoboticWarehouse instance

**`compare_layouts(legacy, robotic, detailed) -> str`**
- `legacy`: LegacyWarehouse instance
- `robotic`: RoboticWarehouse instance
- `detailed`: bool = False - Include detailed analysis

### json_exporter.py

**`export_warehouse_json(warehouse, include_metadata, pretty) -> str`**
- `warehouse`: RoboticWarehouse instance
- `include_metadata`: bool = True - Include export metadata
- `pretty`: bool = True - Format with indentation

**`export_navigation_graph(nodes, edges, include_positions) -> str`**
- `nodes`: List[Node]
- `edges`: List[Edge]
- `include_positions`: bool = True - Include node coordinates

**`export_distance_matrix(matrix, node_ids, format_type) -> str`**
- `matrix`: Dict[str, Dict[str, float]]
- `node_ids`: Optional[List[str]] - Filter specific nodes
- `format_type`: str = 'nested' - 'nested' or 'flat'

**`save_warehouse_json(warehouse, filepath, include_metadata) -> None`**
- `warehouse`: RoboticWarehouse instance
- `filepath`: str - Output file path
- `include_metadata`: bool = True

## Output Examples

### ASCII Layout
```
+------------------------------------------------------------+
|                                              D             |
|  P----+----+----+----+----+                                |
|  |    |    |    |    |    |                                |
|  +----+----+----+----+----+                                |
|                                           C    C           |
+------------------------------------------------------------+
  Width: 20.0m    Length: 60.0m
  Nodes: 12    Edges: 17
```

### Distance Matrix
```
================================================================================
DISTANCE MATRIX (in meters)
================================================================================

         | N01     | N02     | N03     | N04     |
---------------------------------------------------------
 N01     | 0.00    | 10.00   | 20.00   | ---     |
 N02     | 10.00   | 0.00    | 10.00   | 15.00   |
 N03     | 20.00   | 10.00   | 0.00    | 12.00   |
 N04     | ---     | 15.00   | 12.00   | 0.00    |
---------------------------------------------------------

Total connections: 6
Min distance: 10.00m
Max distance: 20.00m
Average distance: 14.50m
```

### Summary Stats Dictionary
```python
{
    'warehouse_name': 'Robotic Warehouse A',
    'dimensions': {
        'width_m': 20.0,
        'length_m': 60.0,
        'total_area_m2': 1200.0
    },
    'total_nodes': 12,
    'total_edges': 17,
    'charging_stations': 2,
    'nodes_by_type': {
        'pickup': 1,
        'drop': 1,
        'intersection': 6,
        'charging': 2
    },
    'node_density_per_m2': 0.01,
    'avg_connections_per_node': 2.83,
    'distance_stats': {
        'min_distance_m': 2.5,
        'max_distance_m': 13.0,
        'avg_distance_m': 8.9,
        'total_connections': 17
    }
}
```

## Tips & Best Practices

1. **Always check for empty data** before generating visualizations
2. **Use `max_nodes` parameter** for large distance matrices to limit output
3. **Export metadata** when saving JSON for version tracking
4. **Use flat format** for distance matrix when interfacing with databases
5. **Generate detailed reports** for documentation and analysis
6. **Use simple layout** for quick terminal output
7. **Save reports to files** for record-keeping
8. **Include positions** in graph export for visualization tools

## Error Handling

All functions handle common errors gracefully:
- Empty node/edge lists return sensible defaults
- Missing distance matrix entries show "---"
- Invalid node types are handled
- File I/O errors are reported clearly

## Performance Notes

- ASCII generation: Fast for warehouses up to 100 nodes
- Report generation: O(n) complexity, very fast
- JSON export: Fast, uses native json library
- Distance matrix formatting: O(n²), can be slow for large matrices (use `max_nodes`)
