#!/usr/bin/env python3
"""Visualize Layout A warehouse configuration as ASCII art."""

from data.layout_a import create_layout_a_warehouse


def visualize_layout_ascii(warehouse):
    """Create ASCII visualization of the warehouse layout."""
    # Scale factor (pixels per meter)
    scale = 2

    # Create grid
    width_cells = int(warehouse.width * scale)
    length_cells = int(warehouse.length * scale)

    # Initialize grid with spaces
    grid = [[' ' for _ in range(width_cells)] for _ in range(length_cells)]

    # Draw zones
    for zone in warehouse.zones:
        x_start = int(zone.x * scale)
        y_start = int(zone.y * scale)
        x_end = int((zone.x + zone.width) * scale)
        y_end = int((zone.y + zone.height) * scale)

        # Choose character based on zone type
        if zone.zone_type.value == 'pickup':
            char = 'P'
        elif zone.zone_type.value == 'drop':
            char = 'D'
        elif zone.zone_type.value == 'aisle':
            char = '|'
        else:
            char = '.'

        # Fill zone
        for y in range(y_start, min(y_end, length_cells)):
            for x in range(x_start, min(x_end, width_cells)):
                if y < length_cells and x < width_cells:
                    grid[y][x] = char

    # Draw nodes
    for node in warehouse.nodes:
        x = int(node.x * scale)
        y = int(node.y * scale)

        if 0 <= y < length_cells and 0 <= x < width_cells:
            if node.node_type.value == 'pickup':
                grid[y][x] = '@'
            elif node.node_type.value == 'drop':
                grid[y][x] = '#'
            elif 'entry' in node.node_type.value:
                grid[y][x] = '▼'
            elif 'exit' in node.node_type.value:
                grid[y][x] = '▲'
            else:
                grid[y][x] = '•'

    # Print grid (flip vertically to match coordinate system)
    print("\nLayout A Warehouse Visualization")
    print("=" * width_cells)
    print(f"Scale: 1 character = {1/scale:.1f}m")
    print(f"Legend: P=Pickup, D=Drop, |=Aisle, @=Pickup Node, #=Drop Node")
    print(f"        ▼=Entry, ▲=Exit, •=Waypoint")
    print("=" * width_cells)
    print()

    # Add Y-axis labels
    for y in range(length_cells - 1, -1, -1):
        if y % 10 == 0:
            print(f"{y//scale:3.0f}m |", end='')
        else:
            print("     |", end='')
        print(''.join(grid[y]))

    # Add X-axis
    print("     +" + "-" * width_cells)
    print("      ", end='')
    for x in range(0, width_cells, 10):
        print(f"{x//scale:<10.0f}", end='')
    print(" (meters)")
    print()


def print_warehouse_summary(warehouse):
    """Print detailed warehouse summary."""
    print("\nWarehouse Summary")
    print("=" * 60)
    print(f"Name: {warehouse.name}")
    print(f"Dimensions: {warehouse.width}m x {warehouse.length}m")
    print(f"Total Area: {warehouse.total_area:.2f} sq.m")
    print(f"Storage Area: {warehouse.storage_area:.2f} sq.m")
    print(f"Number of Aisles: {warehouse.aisles}")
    print(f"Aisle Dimensions: {warehouse.aisle_width}m x {warehouse.aisle_length}m")
    print()

    print("Zones:")
    for zone in warehouse.zones:
        print(f"  • {zone.name} ({zone.zone_type.value})")
        print(f"    Location: ({zone.x:.1f}, {zone.y:.1f})")
        print(f"    Size: {zone.width}m x {zone.height}m")
        print(f"    Area: {zone.width * zone.height:.2f} sq.m")
    print()

    print(f"Navigation Network:")
    print(f"  • Total Nodes: {len(warehouse.nodes)}")

    # Count node types
    node_counts = {}
    for node in warehouse.nodes:
        node_type = node.node_type.value
        node_counts[node_type] = node_counts.get(node_type, 0) + 1

    for node_type, count in sorted(node_counts.items()):
        print(f"    - {node_type}: {count}")

    print(f"  • Total Edges: {len(warehouse.edges)}")

    # Calculate total network distance
    total_distance = sum(edge.distance for edge in warehouse.edges)
    print(f"  • Network Distance: {total_distance:.2f}m")

    bidirectional = sum(1 for edge in warehouse.edges if edge.bidirectional)
    print(f"  • Bidirectional Edges: {bidirectional}/{len(warehouse.edges)}")
    print()


def print_node_connections(warehouse):
    """Print node connectivity information."""
    print("Node Connections:")
    print("=" * 60)

    # Build adjacency list
    adjacency = {}
    for edge in warehouse.edges:
        if edge.from_node not in adjacency:
            adjacency[edge.from_node] = []
        adjacency[edge.from_node].append((edge.to_node, edge.distance))

        if edge.bidirectional:
            if edge.to_node not in adjacency:
                adjacency[edge.to_node] = []
            adjacency[edge.to_node].append((edge.from_node, edge.distance))

    # Print key nodes and their connections
    key_nodes = ['node_pickup', 'node_drop', 'node_aisle_1_entry', 'node_aisle_5_exit']

    for node_id in key_nodes:
        if node_id in adjacency:
            node = warehouse.get_node(node_id)
            print(f"\n{node_id} ({node.node_type.value}):")
            print(f"  Location: ({node.x:.1f}, {node.y:.1f})")
            print(f"  Connected to:")
            for neighbor, distance in adjacency[node_id]:
                neighbor_node = warehouse.get_node(neighbor)
                print(f"    - {neighbor} ({neighbor_node.node_type.value}): {distance:.2f}m")


if __name__ == "__main__":
    # Create warehouse
    warehouse = create_layout_a_warehouse()

    # Print summary
    print_warehouse_summary(warehouse)

    # Visualize layout
    visualize_layout_ascii(warehouse)

    # Print connections
    print_node_connections(warehouse)

    print("\n" + "=" * 60)
    print("Visualization complete!")
    print("=" * 60)
