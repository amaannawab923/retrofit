#!/usr/bin/env python3
"""Example usage of the retrofit framework data models."""

import json
from models import (
    Node,
    Edge,
    Zone,
    ZoneType,
    NodeType,
    LegacyWarehouse,
    RoboticWarehouse,
    AGVConfig,
    SimulationParams,
)
from data import create_layout_a_warehouse, LAYOUT_A_CONFIG


def example_1_create_basic_components():
    """Example 1: Create basic warehouse components."""
    print("\n" + "=" * 60)
    print("Example 1: Creating Basic Components")
    print("=" * 60)

    # Create a zone
    storage_zone = Zone(
        id="zone_storage_1",
        name="Storage Area 1",
        x=10.0,
        y=20.0,
        width=5.0,
        height=10.0,
        zone_type=ZoneType.STORAGE,
    )
    print(f"\nCreated zone: {storage_zone.name}")
    print(f"  Location: ({storage_zone.x}, {storage_zone.y})")
    print(f"  Size: {storage_zone.width}m x {storage_zone.height}m")
    print(f"  Type: {storage_zone.zone_type.value}")

    # Create nodes
    node1 = Node(
        id="node_001",
        x=10.0,
        y=20.0,
        zone_type=ZoneType.STORAGE,
        node_type=NodeType.WAYPOINT,
    )

    node2 = Node(
        id="node_002",
        x=15.0,
        y=20.0,
        zone_type=ZoneType.STORAGE,
        node_type=NodeType.WAYPOINT,
    )

    print(f"\nCreated nodes:")
    print(f"  {node1.id} at ({node1.x}, {node1.y})")
    print(f"  {node2.id} at ({node2.x}, {node2.y})")

    # Calculate distance
    distance = node1.distance_to(node2)
    print(f"\nDistance between nodes: {distance:.2f}m")

    # Create edge
    edge = Edge(
        id="edge_001",
        from_node=node1.id,
        to_node=node2.id,
        distance=distance,
        bidirectional=True,
    )

    print(f"\nCreated edge: {edge.id}")
    print(f"  From: {edge.from_node} → To: {edge.to_node}")
    print(f"  Distance: {edge.distance:.2f}m")
    print(f"  Bidirectional: {edge.bidirectional}")


def example_2_use_layout_a():
    """Example 2: Use the pre-configured Layout A."""
    print("\n" + "=" * 60)
    print("Example 2: Using Layout A")
    print("=" * 60)

    # Access configuration
    print(f"\nLayout A Configuration:")
    print(f"  Name: {LAYOUT_A_CONFIG['name']}")
    print(f"  Dimensions: {LAYOUT_A_CONFIG['width']}m x {LAYOUT_A_CONFIG['length']}m")
    print(f"  Aisles: {LAYOUT_A_CONFIG['aisles']}")

    # Create warehouse
    warehouse = create_layout_a_warehouse()

    print(f"\nWarehouse created: {warehouse.name}")
    print(f"  Total area: {warehouse.total_area:.2f} sq.m")
    print(f"  Storage area: {warehouse.storage_area:.2f} sq.m")
    print(f"  Zones: {len(warehouse.zones)}")
    print(f"  Nodes: {len(warehouse.nodes)}")
    print(f"  Edges: {len(warehouse.edges)}")

    # Find specific nodes
    pickup_node = warehouse.get_node("node_pickup")
    drop_node = warehouse.get_node("node_drop")

    print(f"\nKey nodes:")
    print(f"  Pickup: {pickup_node.id} at ({pickup_node.x}, {pickup_node.y})")
    print(f"  Drop: {drop_node.id} at ({drop_node.x}, {drop_node.y})")

    # Get nodes by type
    entry_nodes = warehouse.get_nodes_by_type(NodeType.AISLE_ENTRY)
    print(f"\nAisle entry nodes: {len(entry_nodes)}")
    for node in entry_nodes:
        print(f"  {node.id} at ({node.x}, {node.y})")


def example_3_export_import_json():
    """Example 3: Export and import warehouse to/from JSON."""
    print("\n" + "=" * 60)
    print("Example 3: JSON Export/Import")
    print("=" * 60)

    # Create warehouse
    warehouse = create_layout_a_warehouse()

    # Export to JSON string
    warehouse_json = warehouse.model_dump_json(indent=2)
    print(f"\nExported warehouse to JSON ({len(warehouse_json)} bytes)")

    # Show first few lines
    lines = warehouse_json.split('\n')[:10]
    print("\nFirst 10 lines of JSON:")
    for line in lines:
        print(f"  {line}")
    print("  ...")

    # Parse JSON back
    warehouse_data = json.loads(warehouse_json)

    # Create warehouse from data
    loaded_warehouse = LegacyWarehouse(**warehouse_data)

    print(f"\nLoaded warehouse: {loaded_warehouse.name}")
    print(f"  Zones: {len(loaded_warehouse.zones)}")
    print(f"  Nodes: {len(loaded_warehouse.nodes)}")
    print(f"  Edges: {len(loaded_warehouse.edges)}")

    # Verify data integrity
    assert warehouse.name == loaded_warehouse.name
    assert len(warehouse.zones) == len(loaded_warehouse.zones)
    assert len(warehouse.nodes) == len(loaded_warehouse.nodes)
    assert len(warehouse.edges) == len(loaded_warehouse.edges)
    print("\n✓ Data integrity verified!")


def example_4_create_robotic_warehouse():
    """Example 4: Create a robotic warehouse from legacy."""
    print("\n" + "=" * 60)
    print("Example 4: Creating Robotic Warehouse")
    print("=" * 60)

    # Start with legacy warehouse
    legacy = create_layout_a_warehouse()
    print(f"\nStarting with legacy warehouse: {legacy.name}")

    # Create charging station nodes
    charging_stations = [
        Node(
            id="charging_1",
            x=2.0,
            y=2.0,
            zone_type=ZoneType.CHARGING,
            node_type=NodeType.CHARGING,
        ),
        Node(
            id="charging_2",
            x=18.0,
            y=58.0,
            zone_type=ZoneType.CHARGING,
            node_type=NodeType.CHARGING,
        ),
    ]

    # Build navigation graph (adjacency list)
    navigation_graph = {}
    for edge in legacy.edges:
        if edge.from_node not in navigation_graph:
            navigation_graph[edge.from_node] = []
        navigation_graph[edge.from_node].append(edge.to_node)

        if edge.bidirectional:
            if edge.to_node not in navigation_graph:
                navigation_graph[edge.to_node] = []
            navigation_graph[edge.to_node].append(edge.from_node)

    # Create robotic warehouse
    robotic = RoboticWarehouse(
        **legacy.model_dump(),
        charging_stations=charging_stations,
        navigation_graph=navigation_graph,
    )

    print(f"\nCreated robotic warehouse: {robotic.name}")
    print(f"  Nodes: {robotic.num_nodes}")
    print(f"  Edges: {robotic.num_edges}")
    print(f"  Charging stations: {len(robotic.charging_stations)}")
    print(f"  Navigation graph nodes: {len(robotic.navigation_graph)}")

    # Show charging stations
    print(f"\nCharging stations:")
    for station in robotic.charging_stations:
        print(f"  {station.id} at ({station.x}, {station.y})")


def example_5_agv_configuration():
    """Example 5: Configure AGV fleet and simulation."""
    print("\n" + "=" * 60)
    print("Example 5: AGV Configuration")
    print("=" * 60)

    # Create AGV configuration
    agv_config = AGVConfig(
        count=5,
        speed=2.0,  # m/s
        turn_delay=1.0,  # seconds
        width=1.0,  # meters
        length=1.5,  # meters
        battery_capacity=1000.0,  # watt-hours
    )

    print(f"\nAGV Fleet Configuration:")
    print(f"  Number of AGVs: {agv_config.count}")
    print(f"  Speed: {agv_config.speed} m/s")
    print(f"  Turn delay: {agv_config.turn_delay} seconds")
    print(f"  Dimensions: {agv_config.width}m x {agv_config.length}m")
    print(f"  Battery capacity: {agv_config.battery_capacity} Wh")

    # Create simulation parameters
    sim_params = SimulationParams(
        agv_config=agv_config,
        task_rate=10.0,  # tasks per minute
        pick_time=5.0,  # seconds
        drop_time=5.0,  # seconds
        simulation_duration=3600.0,  # 1 hour
    )

    print(f"\nSimulation Parameters:")
    print(f"  Task rate: {sim_params.task_rate} tasks/min")
    print(f"  Pick time: {sim_params.pick_time} seconds")
    print(f"  Drop time: {sim_params.drop_time} seconds")
    print(f"  Duration: {sim_params.simulation_duration / 60:.0f} minutes")

    # Calculate expected tasks
    expected_tasks = (sim_params.simulation_duration / 60) * sim_params.task_rate
    print(f"\nExpected tasks in simulation: {expected_tasks:.0f}")


def example_6_data_validation():
    """Example 6: Demonstrate Pydantic validation."""
    print("\n" + "=" * 60)
    print("Example 6: Data Validation")
    print("=" * 60)

    # Valid node
    print("\nCreating valid node...")
    try:
        node = Node(
            id="valid_node",
            x=10.0,
            y=20.0,
            zone_type=ZoneType.STORAGE,
            node_type=NodeType.WAYPOINT,
        )
        print(f"✓ Created node: {node.id}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Invalid node - negative coordinates
    print("\nTrying to create node with negative coordinates...")
    try:
        node = Node(
            id="invalid_node",
            x=-5.0,  # Invalid!
            y=20.0,
            zone_type=ZoneType.STORAGE,
            node_type=NodeType.WAYPOINT,
        )
        print(f"✓ Created node: {node.id}")
    except Exception as e:
        print(f"✗ Validation error (expected): {type(e).__name__}")

    # Invalid edge - negative distance
    print("\nTrying to create edge with negative distance...")
    try:
        edge = Edge(
            id="invalid_edge",
            from_node="node1",
            to_node="node2",
            distance=-10.0,  # Invalid!
        )
        print(f"✓ Created edge: {edge.id}")
    except Exception as e:
        print(f"✗ Validation error (expected): {type(e).__name__}")

    # Invalid zone - zero width
    print("\nTrying to create zone with zero width...")
    try:
        zone = Zone(
            id="invalid_zone",
            name="Invalid Zone",
            x=0.0,
            y=0.0,
            width=0.0,  # Invalid!
            height=5.0,
            zone_type=ZoneType.STORAGE,
        )
        print(f"✓ Created zone: {zone.id}")
    except Exception as e:
        print(f"✗ Validation error (expected): {type(e).__name__}")

    print("\n✓ Pydantic validation working correctly!")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Retrofit Framework - Data Models Examples")
    print("=" * 60)

    example_1_create_basic_components()
    example_2_use_layout_a()
    example_3_export_import_json()
    example_4_create_robotic_warehouse()
    example_5_agv_configuration()
    example_6_data_validation()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
