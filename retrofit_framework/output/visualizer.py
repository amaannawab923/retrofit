"""
ASCII and Text Visualization

Provides ASCII art and text-based visualization of warehouse layouts,
navigation graphs, and distance matrices.
"""

from typing import List, Dict, Tuple, Optional

try:
    from ..models.warehouse import RoboticWarehouse, Node, NodeType
except ImportError:
    from models.warehouse import RoboticWarehouse, Node, NodeType


def generate_ascii_layout(warehouse: RoboticWarehouse) -> str:
    """
    Generate ASCII art visualization of the warehouse layout.

    Args:
        warehouse: RoboticWarehouse instance to visualize

    Returns:
        ASCII art string representation of the warehouse

    Example:
        >>> ascii_output = generate_ascii_layout(warehouse)
        >>> print(ascii_output)
    """
    width = int(warehouse.width)
    length = int(warehouse.length)

    # Create a character grid for the warehouse
    # Scale factor: 1 character = 2 meters (adjustable)
    scale = 2.0
    grid_width = max(60, int(width / scale))
    grid_height = max(20, int(length / scale))

    # Initialize grid with spaces
    grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]

    # Place nodes on the grid
    node_positions = {}
    for node in warehouse.nodes:
        grid_x = int(node.x / scale)
        grid_y = int(node.y / scale)

        # Clamp to grid boundaries
        grid_x = max(1, min(grid_width - 2, grid_x))
        grid_y = max(1, min(grid_height - 2, grid_y))

        node_positions[node.id] = (grid_x, grid_y)

        # Place node marker based on type
        if node.node_type == NodeType.CHARGING:
            marker = 'C'
        elif node.node_type == NodeType.PICKUP:
            marker = 'P'
        elif node.node_type == NodeType.DROP:
            marker = 'D'
        elif node.node_type == NodeType.INTERSECTION:
            marker = '+'
        elif node.node_type == NodeType.STAGING:
            marker = 'S'
        elif node.node_type == NodeType.MAINTENANCE:
            marker = 'M'
        else:
            marker = 'N'

        grid[grid_y][grid_x] = marker

    # Draw edges between nodes
    for edge in warehouse.edges:
        from_pos = node_positions.get(edge.from_node)
        to_pos = node_positions.get(edge.to_node)

        if from_pos and to_pos:
            _draw_line(grid, from_pos, to_pos)

    # Build the ASCII output
    lines = []
    lines.append("+" + "-" * grid_width + "+")

    for row in grid:
        lines.append("|" + "".join(row) + "|")

    lines.append("+" + "-" * grid_width + "+")

    # Add legend and statistics
    lines.append(f"  Width: {warehouse.width}m    Length: {warehouse.length}m")
    lines.append(f"  Nodes: {warehouse.num_nodes}    Edges: {warehouse.num_edges}")
    lines.append("")
    lines.append("  Legend: C=Charging  P=Pickup  D=Drop  +=Intersection  S=Staging  M=Maintenance  N=Node")

    return "\n".join(lines)


def generate_node_map(nodes: List[Node]) -> str:
    """
    Generate a formatted text map showing all node positions and types.

    Args:
        nodes: List of Node instances

    Returns:
        Formatted string with node information

    Example:
        >>> node_map = generate_node_map(warehouse.nodes)
        >>> print(node_map)
    """
    lines = []
    lines.append("=" * 70)
    lines.append("NODE MAP")
    lines.append("=" * 70)
    lines.append("")

    # Group nodes by type
    nodes_by_type: Dict[NodeType, List[Node]] = {}
    for node in nodes:
        if node.node_type not in nodes_by_type:
            nodes_by_type[node.node_type] = []
        nodes_by_type[node.node_type].append(node)

    # Display nodes grouped by type
    for node_type in NodeType:
        if node_type in nodes_by_type:
            type_nodes = nodes_by_type[node_type]
            lines.append(f"{node_type.value.upper()} NODES ({len(type_nodes)}):")
            lines.append("-" * 70)

            for node in sorted(type_nodes, key=lambda n: n.id):
                zone_info = f" [Zone: {node.zone_type.value}]"
                lines.append(f"  {node.id:8} | Position: ({node.x:6.2f}m, {node.y:6.2f}m){zone_info}")

            lines.append("")

    # Summary statistics
    lines.append("=" * 70)
    lines.append(f"TOTAL NODES: {len(nodes)}")
    lines.append("=" * 70)

    return "\n".join(lines)


def format_distance_matrix(
    matrix: Dict[str, Dict[str, float]],
    node_ids: Optional[List[str]] = None,
    max_nodes: Optional[int] = None
) -> str:
    """
    Format a distance matrix as a readable table.

    Args:
        matrix: Dictionary mapping node_id -> {node_id: distance}
        node_ids: List of node IDs to include (default: all keys from matrix)
        max_nodes: Maximum number of nodes to display (default: all)

    Returns:
        Formatted distance matrix string

    Example:
        >>> formatted = format_distance_matrix(distances, ["N01", "N02", "N03"])
        >>> print(formatted)
    """
    # Get node IDs from matrix if not provided
    if node_ids is None:
        node_ids = sorted(matrix.keys())

    if max_nodes:
        node_ids = node_ids[:max_nodes]

    lines = []
    lines.append("=" * 80)
    lines.append("DISTANCE MATRIX (in meters)")
    lines.append("=" * 80)
    lines.append("")

    if not node_ids:
        lines.append("No nodes to display.")
        return "\n".join(lines)

    # Determine column width based on longest node ID
    col_width = max(8, max(len(node_id) for node_id in node_ids) + 2)

    # Header row
    header = " " * col_width + "|"
    for node_id in node_ids:
        header += f" {node_id:^{col_width-1}}|"
    lines.append(header)
    lines.append("-" * len(header))

    # Data rows
    for from_node in node_ids:
        row = f" {from_node:<{col_width-1}}|"
        for to_node in node_ids:
            if from_node == to_node:
                distance_str = "0.00"
            else:
                # Get distance from matrix
                distance = None
                if from_node in matrix and to_node in matrix[from_node]:
                    distance = matrix[from_node][to_node]
                elif to_node in matrix and from_node in matrix[to_node]:
                    distance = matrix[to_node][from_node]

                if distance is not None:
                    distance_str = f"{distance:.2f}"
                else:
                    distance_str = "---"

            row += f" {distance_str:^{col_width-1}}|"
        lines.append(row)

    lines.append("-" * len(header))
    lines.append("")

    # Statistics
    all_distances = []
    for from_node, destinations in matrix.items():
        for to_node, dist in destinations.items():
            if dist > 0:
                all_distances.append(dist)

    if all_distances:
        lines.append(f"Total connections: {len(all_distances)}")
        lines.append(f"Min distance: {min(all_distances):.2f}m")
        lines.append(f"Max distance: {max(all_distances):.2f}m")
        lines.append(f"Average distance: {sum(all_distances)/len(all_distances):.2f}m")

    lines.append("")
    if max_nodes and len(node_ids) >= max_nodes:
        lines.append(f"(Showing first {max_nodes} nodes only)")
        lines.append("")

    return "\n".join(lines)


def _draw_line(grid: List[List[str]], start: Tuple[int, int], end: Tuple[int, int]) -> None:
    """
    Draw a line between two points on the character grid using Bresenham's algorithm.

    Args:
        grid: 2D character grid
        start: Starting position (x, y)
        end: Ending position (x, y)
    """
    x0, y0 = start
    x1, y1 = end

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    err = dx - dy

    x, y = x0, y0

    while True:
        # Don't overwrite node markers
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]) and grid[y][x] == ' ':
            if dx > dy:
                grid[y][x] = '-'
            else:
                grid[y][x] = '|'

        if x == x1 and y == y1:
            break

        e2 = 2 * err

        if e2 > -dy:
            err -= dy
            x += sx

        if e2 < dx:
            err += dx
            y += sy


def generate_simple_layout(warehouse: RoboticWarehouse) -> str:
    """
    Generate a simplified text representation of the warehouse.

    Args:
        warehouse: RoboticWarehouse instance

    Returns:
        Simple text representation
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"WAREHOUSE LAYOUT: {warehouse.name}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Dimensions: {warehouse.width}m x {warehouse.length}m")
    lines.append(f"Total Area: {warehouse.total_area:.2f} m²")
    lines.append("")

    # Node summary by type
    lines.append("Node Summary:")
    for node_type in NodeType:
        type_nodes = warehouse.get_nodes_by_type(node_type)
        if type_nodes:
            lines.append(f"  - {node_type.value.title()}: {len(type_nodes)}")

    lines.append("")
    lines.append(f"Total Nodes: {warehouse.num_nodes}")
    lines.append(f"Total Edges: {warehouse.num_edges}")
    lines.append("")

    return "\n".join(lines)
