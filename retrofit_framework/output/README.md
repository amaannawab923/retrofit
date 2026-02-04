# Output Module

The output module provides comprehensive visualization, reporting, and export functionality for the retrofit framework.

## Features

### 1. ASCII Visualization (`visualizer.py`)

Generate ASCII art and text-based visualizations of warehouse layouts:

```python
from output.visualizer import generate_ascii_layout, generate_node_map, format_distance_matrix

# Generate ASCII layout
ascii_art = generate_ascii_layout(warehouse)
print(ascii_art)

# Generate node map
node_map = generate_node_map(warehouse.nodes)
print(node_map)

# Format distance matrix
formatted_matrix = format_distance_matrix(warehouse.distance_matrix)
print(formatted_matrix)
```

### 2. Report Generation (`report_generator.py`)

Create comprehensive reports for warehouse analysis:

```python
from output.report_generator import (
    generate_conversion_report,
    generate_summary_stats,
    compare_layouts
)

# Full conversion report
report = generate_conversion_report(legacy_warehouse, robotic_warehouse)
print(report)

# Summary statistics
stats = generate_summary_stats(robotic_warehouse)
print(f"Total nodes: {stats['total_nodes']}")

# Layout comparison
comparison = compare_layouts(legacy_warehouse, robotic_warehouse, detailed=True)
print(comparison)
```

### 3. JSON Export (`json_exporter.py`)

Export warehouse data to JSON format:

```python
from output.json_exporter import (
    export_warehouse_json,
    export_navigation_graph,
    export_distance_matrix,
    save_warehouse_json
)

# Export to JSON string
json_data = export_warehouse_json(warehouse)

# Save to file
save_warehouse_json(warehouse, 'warehouse.json')

# Export navigation graph only
graph_json = export_navigation_graph(warehouse.nodes, warehouse.edges)

# Export distance matrix
matrix_json = export_distance_matrix(warehouse.distance_matrix)
```

## Functions Reference

### visualizer.py

- **`generate_ascii_layout(warehouse)`**: Creates ASCII art visualization of the warehouse
- **`generate_node_map(nodes)`**: Shows all nodes with positions and types
- **`format_distance_matrix(matrix, node_ids, max_nodes)`**: Formats distance matrix as table
- **`generate_simple_layout(warehouse)`**: Simple text representation

### report_generator.py

- **`generate_conversion_report(legacy, robotic, include_nodes, include_metrics)`**: Comprehensive conversion report
- **`generate_summary_stats(robotic_warehouse)`**: Statistics dictionary
- **`compare_layouts(legacy, robotic, detailed)`**: Side-by-side comparison
- **`generate_node_summary_report(nodes, title)`**: Node summary report

### json_exporter.py

- **`export_warehouse_json(warehouse, include_metadata, pretty)`**: Full warehouse to JSON
- **`export_navigation_graph(nodes, edges, include_positions)`**: Graph structure only
- **`export_distance_matrix(matrix, node_ids, format_type)`**: Distance matrix export
- **`save_warehouse_json(warehouse, filepath, include_metadata)`**: Save to file
- **`load_warehouse_json(filepath)`**: Load from file
- **`export_legacy_warehouse_json(warehouse, pretty)`**: Legacy warehouse export

## Example ASCII Output

```
+------------------------------------------------------------+
|                                              D             |
|  P----+----+----+----+----+                                |
|  |    |    |    |    |    |                                |
|  |    |    |    |    |    |                                |
|  +----+----+----+----+----+                                |
|                                                            |
|                                           C    C           |
+------------------------------------------------------------+
  Width: 20.0m    Length: 60.0m
  Nodes: 12    Edges: 17

  Legend: C=Charging  P=Pickup  D=Drop  +=Intersection  S=Staging  M=Maintenance  N=Node
```

## Integration

The output module integrates seamlessly with the retrofit framework's data models:

- Works with `RoboticWarehouse` and `LegacyWarehouse` Pydantic models
- Supports all `NodeType` and `ZoneType` enumerations
- Compatible with the framework's navigation graph structure
- Handles distance matrices in nested dict format

## Error Handling

All functions include proper error handling and will:
- Return empty/default values for missing data
- Validate input parameters
- Provide clear error messages for invalid inputs
- Handle both relative and absolute imports for flexibility
