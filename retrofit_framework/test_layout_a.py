#!/usr/bin/env python3
"""Test script to validate Layout A configuration."""

from data.layout_a import LAYOUT_A_CONFIG, create_layout_a_warehouse
from models import Node, Edge, Zone, LegacyWarehouse


def test_layout_a():
    """Test the Layout A warehouse creation."""
    print("=" * 60)
    print("Testing Layout A Warehouse Configuration")
    print("=" * 60)

    # Test configuration
    print("\n1. Testing LAYOUT_A_CONFIG:")
    print(f"   Name: {LAYOUT_A_CONFIG['name']}")
    print(f"   Dimensions: {LAYOUT_A_CONFIG['width']}m x {LAYOUT_A_CONFIG['length']}m")
    print(f"   Aisles: {LAYOUT_A_CONFIG['aisles']}")
    print(f"   Aisle Width: {LAYOUT_A_CONFIG['aisle_width']}m")
    print(f"   Aisle Length: {LAYOUT_A_CONFIG['aisle_length']}m")

    # Create warehouse
    print("\n2. Creating warehouse object...")
    warehouse = create_layout_a_warehouse()

    # Validate warehouse
    print("\n3. Warehouse details:")
    print(f"   Name: {warehouse.name}")
    print(f"   Dimensions: {warehouse.width}m x {warehouse.length}m")
    print(f"   Total Area: {warehouse.total_area:.2f} sq.m")
    print(f"   Storage Area: {warehouse.storage_area:.2f} sq.m")
    print(f"   Number of Aisles: {warehouse.aisles}")

    # Validate zones
    print(f"\n4. Zones ({len(warehouse.zones)} total):")
    for zone in warehouse.zones:
        print(f"   - {zone.name} ({zone.zone_type.value})")
        print(f"     Location: ({zone.x}, {zone.y})")
        print(f"     Size: {zone.width}m x {zone.height}m")

    # Validate nodes
    print(f"\n5. Nodes ({len(warehouse.nodes)} total):")
    node_types = {}
    for node in warehouse.nodes:
        node_types[node.node_type.value] = node_types.get(node.node_type.value, 0) + 1
    for node_type, count in sorted(node_types.items()):
        print(f"   - {node_type}: {count}")

    # Validate edges
    print(f"\n6. Edges ({len(warehouse.edges)} total):")
    total_distance = sum(edge.distance for edge in warehouse.edges)
    print(f"   Total network distance: {total_distance:.2f}m")
    bidirectional = sum(1 for edge in warehouse.edges if edge.bidirectional)
    print(f"   Bidirectional edges: {bidirectional}/{len(warehouse.edges)}")

    # Test node lookup
    print("\n7. Testing node lookup methods:")
    pickup_node = warehouse.get_node("node_pickup")
    if pickup_node:
        print(f"   Found pickup node: {pickup_node.id} at ({pickup_node.x}, {pickup_node.y})")

    pickup_nodes = warehouse.get_nodes_by_type(warehouse.nodes[0].node_type.__class__.PICKUP)
    print(f"   Pickup nodes found: {len(pickup_nodes)}")

    # Test Pydantic validation
    print("\n8. Testing Pydantic model validation:")
    try:
        # This should work
        test_node = Node(
            id="test_node",
            x=10.0,
            y=20.0,
            zone_type="aisle",
            node_type="waypoint"
        )
        print(f"   Created test node: {test_node.id}")
    except Exception as e:
        print(f"   Error creating node: {e}")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

    return warehouse


if __name__ == "__main__":
    warehouse = test_layout_a()
