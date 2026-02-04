"""
Output Module Demonstration

This script demonstrates the usage of the output module for
visualization, reporting, and JSON export functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.warehouse import (
    Node,
    Edge,
    Zone,
    NodeType,
    ZoneType,
    LegacyWarehouse,
    RoboticWarehouse,
)
from output.visualizer import (
    generate_ascii_layout,
    generate_node_map,
    format_distance_matrix,
    generate_simple_layout,
)
from output.report_generator import (
    generate_conversion_report,
    generate_summary_stats,
    compare_layouts,
    generate_node_summary_report,
)
from output.json_exporter import (
    export_warehouse_json,
    export_navigation_graph,
    export_distance_matrix,
)


def create_sample_warehouse() -> tuple[LegacyWarehouse, RoboticWarehouse]:
    """Create sample warehouses for demonstration."""

    # Create legacy warehouse
    legacy = LegacyWarehouse(
        name="Legacy Warehouse A",
        width=20.0,
        length=60.0,
        aisles=5,
        aisle_width=1.5,
        aisle_length=50.0,
    )

    # Create zones
    pickup_zone = Zone(
        id="PICKUP_01",
        name="Pickup Zone",
        x=0.0,
        y=0.0,
        width=5.0,
        height=5.0,
        zone_type=ZoneType.PICKUP,
    )

    drop_zone = Zone(
        id="DROP_01",
        name="Drop Zone",
        x=15.0,
        y=55.0,
        width=5.0,
        height=5.0,
        zone_type=ZoneType.DROP,
    )

    charging_zone = Zone(
        id="CHARGE_01",
        name="Charging Area",
        x=15.0,
        y=0.0,
        width=5.0,
        height=5.0,
        zone_type=ZoneType.CHARGING,
    )

    # Create nodes
    nodes = [
        # Pickup nodes
        Node(id="P01", x=2.5, y=2.5, zone_type=ZoneType.PICKUP, node_type=NodeType.PICKUP),
        # Intersection nodes along the main corridor
        Node(id="N01", x=5.0, y=10.0, zone_type=ZoneType.CROSSOVER, node_type=NodeType.INTERSECTION),
        Node(id="N02", x=5.0, y=20.0, zone_type=ZoneType.CROSSOVER, node_type=NodeType.INTERSECTION),
        Node(id="N03", x=5.0, y=30.0, zone_type=ZoneType.CROSSOVER, node_type=NodeType.INTERSECTION),
        Node(id="N04", x=5.0, y=40.0, zone_type=ZoneType.CROSSOVER, node_type=NodeType.INTERSECTION),
        Node(id="N05", x=5.0, y=50.0, zone_type=ZoneType.CROSSOVER, node_type=NodeType.INTERSECTION),
        # Drop node
        Node(id="D01", x=17.5, y=57.5, zone_type=ZoneType.DROP, node_type=NodeType.DROP),
        # Charging stations
        Node(id="CHG1", x=17.5, y=2.5, zone_type=ZoneType.CHARGING, node_type=NodeType.CHARGING),
        Node(id="CHG2", x=17.5, y=5.0, zone_type=ZoneType.CHARGING, node_type=NodeType.CHARGING),
    ]

    # Create edges
    edges = [
        Edge(id="E01", from_node="P01", to_node="N01", distance=7.5, bidirectional=True),
        Edge(id="E02", from_node="N01", to_node="N02", distance=10.0, bidirectional=True),
        Edge(id="E03", from_node="N02", to_node="N03", distance=10.0, bidirectional=True),
        Edge(id="E04", from_node="N03", to_node="N04", distance=10.0, bidirectional=True),
        Edge(id="E05", from_node="N04", to_node="N05", distance=10.0, bidirectional=True),
        Edge(id="E06", from_node="N05", to_node="D01", distance=13.0, bidirectional=True),
        Edge(id="E07", from_node="N01", to_node="CHG1", distance=13.0, bidirectional=True),
        Edge(id="E08", from_node="CHG1", to_node="CHG2", distance=2.5, bidirectional=True),
    ]

    # Create robotic warehouse
    robotic = RoboticWarehouse(
        name="Robotic Warehouse A",
        width=20.0,
        length=60.0,
        aisles=5,
        aisle_width=1.5,
        aisle_length=50.0,
        zones=[pickup_zone, drop_zone, charging_zone],
        nodes=nodes,
        edges=edges,
        charging_stations=[
            nodes[7],  # CHG1
            nodes[8],  # CHG2
        ],
    )

    # Build distance matrix
    distance_matrix = {}
    for edge in edges:
        if edge.from_node not in distance_matrix:
            distance_matrix[edge.from_node] = {}
        distance_matrix[edge.from_node][edge.to_node] = edge.distance

        if edge.bidirectional:
            if edge.to_node not in distance_matrix:
                distance_matrix[edge.to_node] = {}
            distance_matrix[edge.to_node][edge.from_node] = edge.distance

    robotic.distance_matrix = distance_matrix

    # Build navigation graph (adjacency list)
    nav_graph = {}
    for edge in edges:
        if edge.from_node not in nav_graph:
            nav_graph[edge.from_node] = []
        nav_graph[edge.from_node].append(edge.to_node)

        if edge.bidirectional:
            if edge.to_node not in nav_graph:
                nav_graph[edge.to_node] = []
            nav_graph[edge.to_node].append(edge.from_node)

    robotic.navigation_graph = nav_graph

    return legacy, robotic


def demo_visualizer():
    """Demonstrate visualizer functions."""
    print("\n" + "=" * 80)
    print("VISUALIZER DEMONSTRATION")
    print("=" * 80 + "\n")

    legacy, robotic = create_sample_warehouse()

    # ASCII layout
    print("1. ASCII Layout Visualization:")
    print("-" * 80)
    ascii_layout = generate_ascii_layout(robotic)
    print(ascii_layout)
    print("\n")

    # Simple layout
    print("2. Simple Layout:")
    print("-" * 80)
    simple_layout = generate_simple_layout(robotic)
    print(simple_layout)
    print("\n")

    # Node map
    print("3. Node Map:")
    print("-" * 80)
    node_map = generate_node_map(robotic.nodes)
    print(node_map)
    print("\n")

    # Distance matrix
    print("4. Distance Matrix:")
    print("-" * 80)
    matrix = format_distance_matrix(robotic.distance_matrix, max_nodes=6)
    print(matrix)
    print("\n")


def demo_reports():
    """Demonstrate report generation functions."""
    print("\n" + "=" * 80)
    print("REPORT GENERATION DEMONSTRATION")
    print("=" * 80 + "\n")

    legacy, robotic = create_sample_warehouse()

    # Conversion report
    print("1. Conversion Report:")
    print("-" * 80)
    conversion_report = generate_conversion_report(
        legacy, robotic, include_nodes=True, include_metrics=True
    )
    print(conversion_report)
    print("\n")

    # Summary statistics
    print("2. Summary Statistics:")
    print("-" * 80)
    stats = generate_summary_stats(robotic)
    print(f"Warehouse: {stats['warehouse_name']}")
    print(f"Total Nodes: {stats['total_nodes']}")
    print(f"Total Edges: {stats['total_edges']}")
    print(f"Node Density: {stats['node_density_per_m2']:.4f} nodes/m²")
    print(f"Avg Connections: {stats['avg_connections_per_node']:.2f}")
    print("\nNodes by Type:")
    for node_type, count in stats['nodes_by_type'].items():
        print(f"  - {node_type}: {count}")
    print("\n")

    # Layout comparison
    print("3. Layout Comparison:")
    print("-" * 80)
    comparison = compare_layouts(legacy, robotic, detailed=True)
    print(comparison)
    print("\n")

    # Node summary
    print("4. Node Summary Report:")
    print("-" * 80)
    node_summary = generate_node_summary_report(robotic.nodes, "Navigation Nodes")
    print(node_summary)
    print("\n")


def demo_json_export():
    """Demonstrate JSON export functions."""
    print("\n" + "=" * 80)
    print("JSON EXPORT DEMONSTRATION")
    print("=" * 80 + "\n")

    legacy, robotic = create_sample_warehouse()

    # Full warehouse export
    print("1. Full Warehouse JSON Export:")
    print("-" * 80)
    warehouse_json = export_warehouse_json(robotic, include_metadata=True, pretty=True)
    print(warehouse_json[:1000] + "\n... (truncated)\n")

    # Navigation graph export
    print("2. Navigation Graph Export:")
    print("-" * 80)
    graph_json = export_navigation_graph(
        robotic.nodes, robotic.edges, include_positions=True
    )
    print(graph_json[:800] + "\n... (truncated)\n")

    # Distance matrix export (nested format)
    print("3. Distance Matrix Export (Nested Format):")
    print("-" * 80)
    matrix_nested = export_distance_matrix(
        robotic.distance_matrix, format_type='nested'
    )
    print(matrix_nested[:600] + "\n... (truncated)\n")

    # Distance matrix export (flat format)
    print("4. Distance Matrix Export (Flat Format):")
    print("-" * 80)
    matrix_flat = export_distance_matrix(
        robotic.distance_matrix, format_type='flat'
    )
    print(matrix_flat[:600] + "\n... (truncated)\n")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "OUTPUT MODULE DEMONSTRATION" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")

    demo_visualizer()
    demo_reports()
    demo_json_export()

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
