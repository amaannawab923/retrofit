"""
Simple Output Module Example

A minimal example showing the most common usage patterns
of the output module.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.warehouse import (
    Node,
    Edge,
    NodeType,
    ZoneType,
    RoboticWarehouse,
)
from output import (
    generate_ascii_layout,
    generate_summary_stats,
    save_warehouse_json,
)


def main():
    """Simple demonstration of output module."""

    # Create a minimal warehouse
    nodes = [
        Node(id="N01", x=5.0, y=10.0, zone_type=ZoneType.CROSSOVER, node_type=NodeType.INTERSECTION),
        Node(id="P01", x=2.5, y=2.5, zone_type=ZoneType.PICKUP, node_type=NodeType.PICKUP),
        Node(id="D01", x=17.5, y=57.5, zone_type=ZoneType.DROP, node_type=NodeType.DROP),
        Node(id="CHG1", x=17.5, y=2.5, zone_type=ZoneType.CHARGING, node_type=NodeType.CHARGING),
    ]

    edges = [
        Edge(id="E01", from_node="P01", to_node="N01", distance=7.5, bidirectional=True),
        Edge(id="E02", from_node="N01", to_node="D01", distance=48.0, badirectional=True),
        Edge(id="E03", from_node="N01", to_node="CHG1", distance=13.0, bidirectional=True),
    ]

    warehouse = RoboticWarehouse(
        name="Simple Warehouse",
        width=20.0,
        length=60.0,
        aisles=3,
        aisle_width=1.5,
        aisle_length=50.0,
        nodes=nodes,
        edges=edges,
        charging_stations=[nodes[3]],  # CHG1
    )

    # 1. Display ASCII visualization
    print("\n" + "=" * 80)
    print("WAREHOUSE VISUALIZATION")
    print("=" * 80 + "\n")

    ascii_layout = generate_ascii_layout(warehouse)
    print(ascii_layout)

    # 2. Display summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80 + "\n")

    stats = generate_summary_stats(warehouse)

    print(f"Warehouse: {stats['warehouse_name']}")
    print(f"Dimensions: {stats['dimensions']['width_m']}m x {stats['dimensions']['length_m']}m")
    print(f"Total Area: {stats['dimensions']['total_area_m2']:.0f} m²")
    print(f"\nTotal Nodes: {stats['total_nodes']}")
    print(f"Total Edges: {stats['total_edges']}")
    print(f"Charging Stations: {stats['charging_stations']}")
    print(f"\nNode Density: {stats['node_density_per_m2']:.4f} nodes/m²")
    print(f"Avg Connections: {stats['avg_connections_per_node']:.2f}")

    print("\nNodes by Type:")
    for node_type, count in stats['nodes_by_type'].items():
        print(f"  - {node_type.title()}: {count}")

    # 3. Export to JSON
    print("\n" + "=" * 80)
    print("JSON EXPORT")
    print("=" * 80 + "\n")

    output_file = Path(__file__).parent / "output_warehouse.json"
    save_warehouse_json(warehouse, str(output_file))
    print(f"Warehouse exported to: {output_file}")
    print(f"File size: {output_file.stat().st_size} bytes")

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
