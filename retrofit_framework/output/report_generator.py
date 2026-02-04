"""
Report Generation

Generates comprehensive reports for warehouse conversion analysis,
including comparison reports, statistics, and conversion summaries.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from ..models.warehouse import LegacyWarehouse, RoboticWarehouse, Node, NodeType
except ImportError:
    from models.warehouse import LegacyWarehouse, RoboticWarehouse, Node, NodeType


def generate_conversion_report(
    legacy: LegacyWarehouse,
    robotic: RoboticWarehouse,
    include_nodes: bool = True,
    include_metrics: bool = True
) -> str:
    """
    Generate a comprehensive conversion report from legacy to robotic warehouse.

    Args:
        legacy: LegacyWarehouse instance (before conversion)
        robotic: RoboticWarehouse instance (after conversion)
        include_nodes: Whether to include detailed node listing
        include_metrics: Whether to include performance metrics

    Returns:
        Formatted conversion report string

    Example:
        >>> report = generate_conversion_report(legacy_wh, robotic_wh)
        >>> print(report)
    """
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("WAREHOUSE RETROFIT CONVERSION REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Legacy warehouse section
    lines.append("-" * 80)
    lines.append("LEGACY WAREHOUSE CONFIGURATION")
    lines.append("-" * 80)
    lines.append(f"Name: {legacy.name}")
    lines.append(f"Dimensions: {legacy.width}m x {legacy.length}m")
    lines.append(f"Total Area: {legacy.total_area:.2f} m²")
    lines.append(f"Number of Aisles: {legacy.aisles}")
    lines.append(f"Aisle Length: {legacy.aisle_length}m")
    lines.append(f"Aisle Width: {legacy.aisle_width}m")
    lines.append(f"Storage Area: {legacy.storage_area:.2f} m²")
    lines.append("")

    # Robotic warehouse section
    lines.append("-" * 80)
    lines.append("ROBOTIC WAREHOUSE CONFIGURATION")
    lines.append("-" * 80)
    lines.append(f"Name: {robotic.name}")
    lines.append(f"Dimensions: {robotic.width}m x {robotic.length}m")
    lines.append(f"Total Area: {robotic.total_area:.2f} m²")
    lines.append(f"Navigation Nodes: {robotic.num_nodes}")
    lines.append(f"Navigation Edges: {robotic.num_edges}")
    lines.append(f"Charging Stations: {len(robotic.charging_stations)}")
    lines.append("")

    # Node breakdown by type
    lines.append("Node Type Breakdown:")
    for node_type in NodeType:
        type_nodes = robotic.get_nodes_by_type(node_type)
        if type_nodes:
            lines.append(f"  - {node_type.value.title()}: {len(type_nodes)}")
    lines.append("")

    # Conversion metrics
    if include_metrics:
        lines.append("-" * 80)
        lines.append("CONVERSION METRICS")
        lines.append("-" * 80)

        # Area efficiency
        if legacy.storage_area > 0:
            space_utilization = (robotic.total_area / legacy.total_area) * 100
            lines.append(f"Space Utilization: {space_utilization:.1f}%")

        # Node density
        node_density = robotic.num_nodes / robotic.total_area
        lines.append(f"Node Density: {node_density:.3f} nodes/m²")

        # Edge connectivity
        if robotic.num_nodes > 0:
            avg_connections = (robotic.num_edges * 2) / robotic.num_nodes
            lines.append(f"Average Connections per Node: {avg_connections:.2f}")

        lines.append("")

    # Detailed node listing
    if include_nodes and robotic.nodes:
        lines.append("-" * 80)
        lines.append("NAVIGATION NODE DETAILS")
        lines.append("-" * 80)

        for node_type in NodeType:
            type_nodes = robotic.get_nodes_by_type(node_type)
            if type_nodes:
                lines.append(f"\n{node_type.value.upper()} NODES:")
                for node in sorted(type_nodes, key=lambda n: n.id):
                    zone_str = f" [Zone: {node.zone_type.value}]"
                    lines.append(f"  {node.id}: ({node.x:.2f}m, {node.y:.2f}m){zone_str}")

        lines.append("")

    # Recommendations
    lines.append("-" * 80)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 80)
    lines.extend(_generate_recommendations(legacy, robotic))
    lines.append("")

    # Footer
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)

    return "\n".join(lines)


def generate_summary_stats(robotic_warehouse: RoboticWarehouse) -> Dict[str, Any]:
    """
    Generate summary statistics for a robotic warehouse.

    Args:
        robotic_warehouse: RoboticWarehouse instance

    Returns:
        Dictionary containing summary statistics

    Example:
        >>> stats = generate_summary_stats(warehouse)
        >>> print(f"Total nodes: {stats['total_nodes']}")
    """
    stats = {
        'warehouse_name': robotic_warehouse.name,
        'dimensions': {
            'width_m': robotic_warehouse.width,
            'length_m': robotic_warehouse.length,
            'total_area_m2': robotic_warehouse.total_area,
        },
        'total_nodes': robotic_warehouse.num_nodes,
        'total_edges': robotic_warehouse.num_edges,
        'charging_stations': len(robotic_warehouse.charging_stations),
        'nodes_by_type': {},
        'node_density_per_m2': robotic_warehouse.num_nodes / robotic_warehouse.total_area if robotic_warehouse.total_area > 0 else 0,
        'avg_connections_per_node': (robotic_warehouse.num_edges * 2) / robotic_warehouse.num_nodes if robotic_warehouse.num_nodes > 0 else 0,
    }

    # Count nodes by type
    for node_type in NodeType:
        type_nodes = robotic_warehouse.get_nodes_by_type(node_type)
        if type_nodes:
            stats['nodes_by_type'][node_type.value] = len(type_nodes)

    # Distance matrix statistics
    if robotic_warehouse.distance_matrix:
        all_distances = []
        for from_node, destinations in robotic_warehouse.distance_matrix.items():
            for to_node, dist in destinations.items():
                if dist > 0:
                    all_distances.append(dist)

        if all_distances:
            stats['distance_stats'] = {
                'min_distance_m': min(all_distances),
                'max_distance_m': max(all_distances),
                'avg_distance_m': sum(all_distances) / len(all_distances),
                'total_connections': len(all_distances),
            }

    return stats


def compare_layouts(
    legacy: LegacyWarehouse,
    robotic: RoboticWarehouse,
    detailed: bool = False
) -> str:
    """
    Generate a side-by-side comparison of legacy and robotic layouts.

    Args:
        legacy: LegacyWarehouse instance
        robotic: RoboticWarehouse instance
        detailed: Whether to include detailed comparison

    Returns:
        Formatted comparison string

    Example:
        >>> comparison = compare_layouts(legacy_wh, robotic_wh)
        >>> print(comparison)
    """
    lines = []

    lines.append("=" * 80)
    lines.append("LAYOUT COMPARISON: LEGACY vs ROBOTIC")
    lines.append("=" * 80)
    lines.append("")

    # Basic dimensions comparison
    lines.append(f"{'Metric':<30} | {'Legacy':<20} | {'Robotic':<20}")
    lines.append("-" * 80)
    lines.append(f"{'Width':<30} | {f'{legacy.width}m':<20} | {f'{robotic.width}m':<20}")
    lines.append(f"{'Length':<30} | {f'{legacy.length}m':<20} | {f'{robotic.length}m':<20}")
    lines.append(f"{'Total Area':<30} | {f'{legacy.total_area:.2f} m²':<20} | {f'{robotic.total_area:.2f} m²':<20}")
    lines.append("")

    # Legacy-specific metrics
    lines.append(f"{'Aisles':<30} | {f'{legacy.aisles}':<20} | {'N/A':<20}")
    lines.append(f"{'Storage Area':<30} | {f'{legacy.storage_area:.2f} m²':<20} | {'N/A':<20}")
    lines.append("")

    # Robotic-specific metrics
    lines.append(f"{'Navigation Nodes':<30} | {'N/A':<20} | {f'{robotic.num_nodes}':<20}")
    lines.append(f"{'Navigation Edges':<30} | {'N/A':<20} | {f'{robotic.num_edges}':<20}")
    lines.append(f"{'Charging Stations':<30} | {'N/A':<20} | {f'{len(robotic.charging_stations)}':<20}")

    # Node type breakdown
    for node_type in NodeType:
        type_nodes = robotic.get_nodes_by_type(node_type)
        if type_nodes:
            label = f"{node_type.value.title()} Nodes"
            lines.append(f"{label:<30} | {'N/A':<20} | {f'{len(type_nodes)}':<20}")

    lines.append("-" * 80)
    lines.append("")

    # Efficiency comparison
    if detailed:
        lines.append("EFFICIENCY ANALYSIS")
        lines.append("-" * 80)

        node_density = robotic.num_nodes / robotic.total_area if robotic.total_area > 0 else 0
        lines.append(f"Node Density: {node_density:.3f} nodes/m²")

        if robotic.num_nodes > 0:
            avg_connections = (robotic.num_edges * 2) / robotic.num_nodes
            lines.append(f"Average Node Connectivity: {avg_connections:.2f}")

        lines.append("")

        # Comparison notes
        lines.append("KEY DIFFERENCES:")
        lines.append(f"  - Legacy uses {legacy.aisles} fixed aisles for navigation")
        lines.append(f"  - Robotic uses {robotic.num_nodes} flexible navigation nodes")
        lines.append(f"  - Robotic system provides {robotic.num_edges} defined navigation paths")
        lines.append(f"  - Robotic includes {len(robotic.charging_stations)} charging stations")
        lines.append("")

    return "\n".join(lines)


def generate_node_summary_report(nodes: List[Node], title: str = "Node Summary") -> str:
    """
    Generate a summary report for a list of nodes.

    Args:
        nodes: List of Node instances
        title: Report title

    Returns:
        Formatted node summary report
    """
    lines = []
    lines.append("=" * 80)
    lines.append(title.upper())
    lines.append("=" * 80)
    lines.append("")

    if not nodes:
        lines.append("No nodes available.")
        return "\n".join(lines)

    # Group by type
    nodes_by_type = {}
    for node in nodes:
        if node.node_type not in nodes_by_type:
            nodes_by_type[node.node_type] = []
        nodes_by_type[node.node_type].append(node)

    # Summary by type
    lines.append("NODE TYPE SUMMARY:")
    lines.append("-" * 80)
    for node_type in NodeType:
        if node_type in nodes_by_type:
            count = len(nodes_by_type[node_type])
            lines.append(f"  {node_type.value.title():<20}: {count:>4} nodes")
    lines.append("")
    lines.append(f"  {'TOTAL':<20}: {len(nodes):>4} nodes")
    lines.append("")

    # Position statistics
    if nodes:
        x_coords = [n.x for n in nodes]
        y_coords = [n.y for n in nodes]

        lines.append("POSITION STATISTICS:")
        lines.append("-" * 80)
        lines.append(f"  X-axis range: {min(x_coords):.2f}m to {max(x_coords):.2f}m")
        lines.append(f"  Y-axis range: {min(y_coords):.2f}m to {max(y_coords):.2f}m")
        lines.append("")

    return "\n".join(lines)


def _generate_recommendations(legacy: LegacyWarehouse, robotic: RoboticWarehouse) -> List[str]:
    """
    Generate recommendations based on warehouse configuration.

    Args:
        legacy: LegacyWarehouse instance
        robotic: RoboticWarehouse instance

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Check node density
    node_density = robotic.num_nodes / robotic.total_area if robotic.total_area > 0 else 0
    if node_density < 0.01:
        recommendations.append("- Consider adding more navigation nodes for better coverage")
    elif node_density > 0.05:
        recommendations.append("- High node density detected; consider optimizing node placement")
    else:
        recommendations.append("- Node density is within optimal range")

    # Check connectivity
    if robotic.num_nodes > 0:
        avg_connections = (robotic.num_edges * 2) / robotic.num_nodes
        if avg_connections < 2:
            recommendations.append("- Low connectivity detected; consider adding more edges")
        elif avg_connections > 6:
            recommendations.append("- High connectivity may lead to complex routing; review edge necessity")
        else:
            recommendations.append("- Node connectivity is well-balanced")

    # Check charging stations
    charging_nodes = robotic.charging_stations
    if not charging_nodes:
        recommendations.append("- WARNING: No charging stations defined; add at least 2 charging nodes")
    elif len(charging_nodes) == 1:
        recommendations.append("- Consider adding additional charging stations for redundancy")
    else:
        recommendations.append(f"- {len(charging_nodes)} charging stations configured")

    # Check pickup/dropoff zones
    pickup_nodes = robotic.get_nodes_by_type(NodeType.PICKUP)
    dropoff_nodes = robotic.get_nodes_by_type(NodeType.DROP)

    if not pickup_nodes:
        recommendations.append("- WARNING: No pickup zones defined")
    if not dropoff_nodes:
        recommendations.append("- WARNING: No dropoff zones defined")

    # Overall assessment
    if robotic.num_nodes > 0 and robotic.num_edges > 0:
        recommendations.append("- Navigation graph is properly initialized")
    else:
        recommendations.append("- WARNING: Navigation graph incomplete")

    return recommendations
