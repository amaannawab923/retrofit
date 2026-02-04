"""Layout A: Traditional warehouse configuration with 5 aisles.

Layout A Specifications:
- Aisle Width: 3.0 meters
- Aisle Length: 50 meters
- Number of Aisles: 5
- Pickup Zone: 5m x 5m in bottom-left corner
- Drop Zone: 5m x 5m in top-right corner
- Estimated dimensions: 20m width x 60m length
"""

import math

from models.warehouse import (
    Edge,
    LegacyWarehouse,
    Node,
    NodeType,
    Zone,
    ZoneType,
)

# Configuration dictionary for Layout A
LAYOUT_A_CONFIG = {
    "name": "Layout A - Traditional 5-Aisle Warehouse",
    "width": 20.0,  # meters
    "length": 60.0,  # meters
    "aisles": 5,
    "aisle_width": 3.0,  # meters
    "aisle_length": 50.0,  # meters
    "pickup_zone": {
        "x": 0.0,
        "y": 0.0,
        "width": 5.0,
        "height": 5.0,
    },
    "drop_zone": {
        "x": 15.0,
        "y": 55.0,
        "width": 5.0,
        "height": 5.0,
    },
}


def create_layout_a_warehouse() -> LegacyWarehouse:
    """Create a LegacyWarehouse object representing Layout A.

    This function generates a complete warehouse layout with:
    - Pickup and drop zones
    - 5 parallel aisles
    - Navigation nodes at strategic positions
    - Edges connecting nodes to form a navigation graph

    Returns:
        LegacyWarehouse: Fully configured warehouse object
    """
    # Extract configuration values
    config = LAYOUT_A_CONFIG
    width = config["width"]
    length = config["length"]
    num_aisles = config["aisles"]
    aisle_width = config["aisle_width"]
    aisle_length = config["aisle_length"]

    # Create zones
    zones = []

    # Pickup zone (bottom-left)
    pickup_zone = Zone(
        id="zone_pickup",
        name="Pickup Zone",
        x=config["pickup_zone"]["x"],
        y=config["pickup_zone"]["y"],
        width=config["pickup_zone"]["width"],
        height=config["pickup_zone"]["height"],
        zone_type=ZoneType.PICKUP,
    )
    zones.append(pickup_zone)

    # Drop zone (top-right)
    drop_zone = Zone(
        id="zone_drop",
        name="Drop Zone",
        x=config["drop_zone"]["x"],
        y=config["drop_zone"]["y"],
        width=config["drop_zone"]["width"],
        height=config["drop_zone"]["height"],
        zone_type=ZoneType.DROP,
    )
    zones.append(drop_zone)

    # Create aisle zones
    # Aisles are evenly distributed along the width
    # Starting from x=6.0 to leave space for pickup zone and cross-aisles
    aisle_start_y = 5.0  # Start after pickup zone
    aisle_spacing = (width - 6.0) / (num_aisles + 1)  # Spacing between aisles

    for i in range(num_aisles):
        aisle_x = 6.0 + (i + 1) * aisle_spacing - aisle_width / 2
        aisle_zone = Zone(
            id=f"zone_aisle_{i+1}",
            name=f"Aisle {i+1}",
            x=aisle_x,
            y=aisle_start_y,
            width=aisle_width,
            height=aisle_length,
            zone_type=ZoneType.AISLE,
        )
        zones.append(aisle_zone)

    # Create nodes for navigation
    nodes = []

    # Pickup zone node (center of pickup zone)
    pickup_node = Node(
        id="node_pickup",
        x=config["pickup_zone"]["x"] + config["pickup_zone"]["width"] / 2,
        y=config["pickup_zone"]["y"] + config["pickup_zone"]["height"] / 2,
        zone_type=ZoneType.PICKUP,
        node_type=NodeType.PICKUP,
    )
    nodes.append(pickup_node)

    # Drop zone node (center of drop zone)
    drop_node = Node(
        id="node_drop",
        x=config["drop_zone"]["x"] + config["drop_zone"]["width"] / 2,
        y=config["drop_zone"]["y"] + config["drop_zone"]["height"] / 2,
        zone_type=ZoneType.DROP,
        node_type=NodeType.DROP,
    )
    nodes.append(drop_node)

    # Create nodes at aisle entries, midpoints, and exits
    aisle_nodes = []
    for i in range(num_aisles):
        aisle_x = 6.0 + (i + 1) * aisle_spacing

        # Aisle entry (bottom)
        entry_node = Node(
            id=f"node_aisle_{i+1}_entry",
            x=aisle_x,
            y=aisle_start_y,
            zone_type=ZoneType.AISLE,
            node_type=NodeType.AISLE_ENTRY,
        )
        nodes.append(entry_node)
        aisle_nodes.append(entry_node)

        # Aisle midpoint
        mid_node = Node(
            id=f"node_aisle_{i+1}_mid",
            x=aisle_x,
            y=aisle_start_y + aisle_length / 2,
            zone_type=ZoneType.AISLE,
            node_type=NodeType.WAYPOINT,
        )
        nodes.append(mid_node)

        # Aisle exit (top)
        exit_node = Node(
            id=f"node_aisle_{i+1}_exit",
            x=aisle_x,
            y=aisle_start_y + aisle_length,
            zone_type=ZoneType.AISLE,
            node_type=NodeType.AISLE_EXIT,
        )
        nodes.append(exit_node)

    # Create crossover nodes (horizontal connections between aisles)
    # Bottom crossover (near pickup zone)
    bottom_crossover_y = aisle_start_y
    for i in range(num_aisles):
        crossover_x = 6.0 + (i + 1) * aisle_spacing
        if i > 0:  # Skip the first one to avoid duplication with aisle entry
            crossover_node = Node(
                id=f"node_crossover_bottom_{i+1}",
                x=crossover_x,
                y=bottom_crossover_y,
                zone_type=ZoneType.CROSSOVER,
                node_type=NodeType.INTERSECTION,
            )
            # This is already covered by aisle entry nodes
            pass

    # Top crossover (near drop zone)
    top_crossover_y = aisle_start_y + aisle_length
    for i in range(num_aisles):
        crossover_x = 6.0 + (i + 1) * aisle_spacing
        # This is already covered by aisle exit nodes
        pass

    # Create edges connecting nodes
    edges = []
    edge_id_counter = 1

    # Connect pickup to first aisle entry
    first_aisle_x = 6.0 + aisle_spacing
    distance = math.sqrt(
        (first_aisle_x - pickup_node.x) ** 2 + (aisle_start_y - pickup_node.y) ** 2
    )
    edges.append(
        Edge(
            id=f"edge_{edge_id_counter:03d}",
            from_node="node_pickup",
            to_node="node_aisle_1_entry",
            distance=round(distance, 2),
            bidirectional=True,
        )
    )
    edge_id_counter += 1

    # Connect last aisle exit to drop zone
    last_aisle_x = 6.0 + num_aisles * aisle_spacing
    distance = math.sqrt(
        (drop_node.x - last_aisle_x) ** 2
        + (drop_node.y - (aisle_start_y + aisle_length)) ** 2
    )
    edges.append(
        Edge(
            id=f"edge_{edge_id_counter:03d}",
            from_node=f"node_aisle_{num_aisles}_exit",
            to_node="node_drop",
            distance=round(distance, 2),
            bidirectional=True,
        )
    )
    edge_id_counter += 1

    # Connect nodes within each aisle (entry -> mid -> exit)
    for i in range(1, num_aisles + 1):
        # Entry to midpoint
        edges.append(
            Edge(
                id=f"edge_{edge_id_counter:03d}",
                from_node=f"node_aisle_{i}_entry",
                to_node=f"node_aisle_{i}_mid",
                distance=round(aisle_length / 2, 2),
                bidirectional=True,
            )
        )
        edge_id_counter += 1

        # Midpoint to exit
        edges.append(
            Edge(
                id=f"edge_{edge_id_counter:03d}",
                from_node=f"node_aisle_{i}_mid",
                to_node=f"node_aisle_{i}_exit",
                distance=round(aisle_length / 2, 2),
                bidirectional=True,
            )
        )
        edge_id_counter += 1

    # Connect adjacent aisles at entry level (bottom crossover)
    for i in range(1, num_aisles):
        distance = aisle_spacing
        edges.append(
            Edge(
                id=f"edge_{edge_id_counter:03d}",
                from_node=f"node_aisle_{i}_entry",
                to_node=f"node_aisle_{i+1}_entry",
                distance=round(distance, 2),
                bidirectional=True,
            )
        )
        edge_id_counter += 1

    # Connect adjacent aisles at midpoint level
    for i in range(1, num_aisles):
        distance = aisle_spacing
        edges.append(
            Edge(
                id=f"edge_{edge_id_counter:03d}",
                from_node=f"node_aisle_{i}_mid",
                to_node=f"node_aisle_{i+1}_mid",
                distance=round(distance, 2),
                bidirectional=True,
            )
        )
        edge_id_counter += 1

    # Connect adjacent aisles at exit level (top crossover)
    for i in range(1, num_aisles):
        distance = aisle_spacing
        edges.append(
            Edge(
                id=f"edge_{edge_id_counter:03d}",
                from_node=f"node_aisle_{i}_exit",
                to_node=f"node_aisle_{i+1}_exit",
                distance=round(distance, 2),
                bidirectional=True,
            )
        )
        edge_id_counter += 1

    # Create and return the LegacyWarehouse object
    warehouse = LegacyWarehouse(
        name=config["name"],
        width=width,
        length=length,
        aisles=num_aisles,
        aisle_width=aisle_width,
        aisle_length=aisle_length,
        zones=zones,
        nodes=nodes,
        edges=edges,
    )

    return warehouse


# Example usage and validation
if __name__ == "__main__":
    # Create warehouse
    warehouse = create_layout_a_warehouse()

    # Print summary
    print(f"Warehouse: {warehouse.name}")
    print(f"Dimensions: {warehouse.width}m x {warehouse.length}m")
    print(f"Number of zones: {len(warehouse.zones)}")
    print(f"Number of nodes: {len(warehouse.nodes)}")
    print(f"Number of edges: {len(warehouse.edges)}")
    print("\nZones:")
    for zone in warehouse.zones:
        print(f"  - {zone.name} ({zone.zone_type.value}): {zone.width}m x {zone.height}m")
    print(f"\nNode types:")
    node_types = {}
    for node in warehouse.nodes:
        node_types[node.node_type.value] = node_types.get(node.node_type.value, 0) + 1
    for node_type, count in sorted(node_types.items()):
        print(f"  - {node_type}: {count}")
