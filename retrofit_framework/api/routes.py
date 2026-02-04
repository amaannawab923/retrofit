"""
API routes for warehouse retrofit conversion.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict

from api.schemas import (
    ConversionResponse,
    ConversionSummary,
    NavigationGraphResponse,
    NodeResponse,
    EdgeResponse,
    OriginalWarehouseResponse,
    RoboticWarehouseResponse,
    WarehouseDimensions,
    RackInfo,
    ZoneInfo,
    ChargingStation,
    TrafficRulesResponse,
    TrafficRule,
    PriorityZone,
    NoStoppingZone,
)
from data.layout_a import create_layout_a_warehouse
from core.converter import RetrofitConverter

router = APIRouter()


@router.get(
    "/convert/layouta",
    response_model=ConversionResponse,
    summary="Convert Layout A to Robotic Warehouse",
    description="""
    Convert the pre-configured Layout A warehouse to a robotic-accommodated facility.

    This endpoint:
    - Loads the hard-coded Layout A warehouse configuration
    - Generates a navigation graph with nodes and edges
    - Computes all-pairs shortest path distance matrix
    - Places charging stations strategically
    - Defines traffic rules for efficient robot operation
    - Calculates feasibility score for the conversion

    Layout A is a traditional 5-aisle warehouse with:
    - Dimensions: 20m x 60m
    - 5 parallel aisles (3m wide, 50m long)
    - Pickup zone in bottom-left
    - Drop zone in top-right
    """,
    responses={
        200: {
            "description": "Successful conversion",
            "content": {
                "application/json": {
                    "example": {
                        "summary": {
                            "total_nodes": 17,
                            "total_edges": 24,
                            "charging_stations_count": 3,
                            "feasibility_score": 8.5,
                            "aisle_width_adequate": True,
                            "recommendations": [
                                "Aisle width meets optimal requirements",
                                "Regular grid layout is ideal for robots"
                            ]
                        }
                    }
                }
            }
        },
        500: {"description": "Internal server error during conversion"}
    }
)
async def convert_layout_a():
    """
    Convert Layout A warehouse to robotic-accommodated warehouse.

    Returns:
        ConversionResponse: Complete conversion data including original warehouse,
                           robotic warehouse, navigation graph, distance matrix,
                           traffic rules, and summary.
    """
    try:
        # Step 1: Load Layout A warehouse configuration
        legacy_warehouse = create_layout_a_warehouse()

        # Step 2: Convert to robotic warehouse using retrofit converter
        converter = RetrofitConverter()
        robotic_warehouse = converter.convert_legacy_warehouse(legacy_warehouse)

        # Step 3: Build response components

        # Original warehouse specification
        original_warehouse = _build_original_warehouse_response(legacy_warehouse)

        # Robotic warehouse specification
        robotic_spec = _build_robotic_warehouse_response(robotic_warehouse)

        # Navigation graph
        navigation_graph = _build_navigation_graph_response(robotic_warehouse)

        # Distance matrix - convert from dict to 2D list
        distance_matrix = _convert_distance_matrix_to_list(
            robotic_warehouse.distance_matrix,
            [node.id for node in robotic_warehouse.nodes]
        )

        # Traffic rules
        traffic_rules = _build_traffic_rules_response(robotic_warehouse)

        # Summary statistics
        summary = _build_conversion_summary(
            legacy_warehouse,
            robotic_warehouse,
            len(navigation_graph.nodes),
            len(navigation_graph.edges)
        )

        # Step 4: Return complete response
        return ConversionResponse(
            original_warehouse=original_warehouse,
            robotic_warehouse=robotic_spec,
            navigation_graph=navigation_graph,
            distance_matrix=distance_matrix,
            traffic_rules=traffic_rules,
            summary=summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error converting warehouse: {str(e)}"
        )


def _convert_distance_matrix_to_list(
    matrix_dict: Dict[str, Dict[str, float]],
    node_ids: List[str]
) -> List[List[float]]:
    """Convert dictionary distance matrix to 2D list format."""
    result = []
    for from_id in node_ids:
        row = []
        for to_id in node_ids:
            if from_id in matrix_dict and to_id in matrix_dict[from_id]:
                row.append(matrix_dict[from_id][to_id])
            else:
                row.append(-1.0)  # Unreachable
        result.append(row)
    return result


def _build_original_warehouse_response(warehouse) -> OriginalWarehouseResponse:
    """Build original warehouse response from LegacyWarehouse object."""

    # Get pickup and drop zones
    pickup_zone = next((z for z in warehouse.zones if z.zone_type.value == "pickup"), None)
    drop_zone = next((z for z in warehouse.zones if z.zone_type.value == "drop"), None)

    # Get aisle zones for rack information
    aisle_zones = [z for z in warehouse.zones if z.zone_type.value == "aisle"]

    return OriginalWarehouseResponse(
        warehouse_dimensions=WarehouseDimensions(
            width=warehouse.width,
            height=warehouse.length
        ),
        racks=RackInfo(
            count=warehouse.aisles,
            width=warehouse.aisle_width,
            height=warehouse.aisle_length,
            positions=[
                {"x": zone.x, "y": zone.y}
                for zone in aisle_zones
            ]
        ),
        aisle_width=warehouse.aisle_width,
        loading_docks=[
            {"x": pickup_zone.x + pickup_zone.width / 2, "y": pickup_zone.y + pickup_zone.height / 2}
        ] if pickup_zone else [],
        shipping_area=ZoneInfo(
            x=drop_zone.x if drop_zone else 0,
            y=drop_zone.y if drop_zone else 0,
            width=drop_zone.width if drop_zone else 0,
            height=drop_zone.height if drop_zone else 0
        )
    )


def _build_robotic_warehouse_response(robotic_warehouse) -> RoboticWarehouseResponse:
    """Build robotic warehouse response from RoboticWarehouse object."""

    # Get zones
    pickup_zone = next((z for z in robotic_warehouse.zones if z.zone_type.value == "pickup"), None)
    drop_zone = next((z for z in robotic_warehouse.zones if z.zone_type.value == "drop"), None)
    aisle_zones = [z for z in robotic_warehouse.zones if z.zone_type.value == "aisle"]

    return RoboticWarehouseResponse(
        warehouse_dimensions=WarehouseDimensions(
            width=robotic_warehouse.width,
            height=robotic_warehouse.length
        ),
        racks=RackInfo(
            count=robotic_warehouse.aisles,
            width=robotic_warehouse.aisle_width,
            height=robotic_warehouse.aisle_length,
            positions=[
                {"x": zone.x, "y": zone.y}
                for zone in aisle_zones
            ]
        ),
        aisle_width=robotic_warehouse.aisle_width,
        loading_docks=[
            {"x": pickup_zone.x + pickup_zone.width / 2, "y": pickup_zone.y + pickup_zone.height / 2}
        ] if pickup_zone else [],
        shipping_area=ZoneInfo(
            x=drop_zone.x if drop_zone else 0,
            y=drop_zone.y if drop_zone else 0,
            width=drop_zone.width if drop_zone else 0,
            height=drop_zone.height if drop_zone else 0
        ),
        charging_stations=[
            ChargingStation(x=station.x, y=station.y)
            for station in robotic_warehouse.charging_stations
        ],
        conversion_notes=getattr(robotic_warehouse, 'conversion_notes', []),
        feasibility_score=getattr(robotic_warehouse, 'feasibility_score', 8.5)
    )


def _build_navigation_graph_response(robotic_warehouse) -> NavigationGraphResponse:
    """Build navigation graph response from RoboticWarehouse object."""

    nodes = [
        NodeResponse(
            id=node.id,
            x=node.x,
            y=node.y,
            type=node.node_type.value
        )
        for node in robotic_warehouse.nodes
    ]

    edges = [
        EdgeResponse(
            from_node=edge.from_node,
            to_node=edge.to_node,
            distance=edge.distance,
            bidirectional=edge.bidirectional
        )
        for edge in robotic_warehouse.edges
    ]

    return NavigationGraphResponse(
        nodes=nodes,
        edges=edges
    )


def _build_traffic_rules_response(robotic_warehouse) -> TrafficRulesResponse:
    """Build traffic rules response from RoboticWarehouse object."""

    # Get traffic rules from warehouse
    traffic_rules = robotic_warehouse.traffic_rules

    one_way_aisles = [
        TrafficRule(
            aisle=rule.rule_id,
            direction="forward",
            description=rule.description
        )
        for rule in traffic_rules
        if rule.rule_type == "one_way"
    ]

    # Get pickup and drop zones for priority zones
    pickup_zone = next((z for z in robotic_warehouse.zones if z.zone_type.value == "pickup"), None)
    drop_zone = next((z for z in robotic_warehouse.zones if z.zone_type.value == "drop"), None)

    priority_zones = []
    if pickup_zone:
        priority_zones.append(PriorityZone(
            name="pickup_zone",
            x=pickup_zone.x,
            y=pickup_zone.y,
            width=pickup_zone.width,
            height=pickup_zone.height,
            priority="high"
        ))
    if drop_zone:
        priority_zones.append(PriorityZone(
            name="drop_zone",
            x=drop_zone.x,
            y=drop_zone.y,
            width=drop_zone.width,
            height=drop_zone.height,
            priority="high"
        ))

    # No-stopping zones at aisle intersections
    no_stopping_zones = [
        NoStoppingZone(x=2.5, y=5.0, width=15.0, height=2.0),
        NoStoppingZone(x=2.5, y=53.0, width=15.0, height=2.0),
    ]

    return TrafficRulesResponse(
        one_way_aisles=one_way_aisles,
        priority_zones=priority_zones,
        no_stopping_zones=no_stopping_zones
    )


def _build_conversion_summary(
    legacy_warehouse,
    robotic_warehouse,
    total_nodes: int,
    total_edges: int
) -> ConversionSummary:
    """Build conversion summary with statistics and recommendations."""

    # Calculate if aisle width is adequate (>= 3.0m)
    aisle_width_adequate = legacy_warehouse.aisle_width >= 3.0

    # Get feasibility score
    feasibility_score = getattr(robotic_warehouse, 'feasibility_score', 8.5)

    # Build recommendations based on conversion
    recommendations = []

    if aisle_width_adequate:
        recommendations.append("Aisle width meets minimum requirements for robot operation")
    else:
        recommendations.append(
            f"Consider widening aisles from {legacy_warehouse.aisle_width}m to at least 3.0m"
        )

    # Add general recommendations
    recommendations.append("Regular grid layout is ideal for autonomous navigation")
    recommendations.append(f"Total of {len(robotic_warehouse.charging_stations)} charging stations placed strategically")

    if feasibility_score >= 8.0:
        recommendations.append("Warehouse is highly suitable for robotic retrofit")
    elif feasibility_score >= 6.0:
        recommendations.append("Warehouse is moderately suitable for robotic retrofit")
    else:
        recommendations.append("Warehouse requires significant modifications for robotic operation")

    return ConversionSummary(
        total_nodes=total_nodes,
        total_edges=total_edges,
        charging_stations_count=len(robotic_warehouse.charging_stations),
        feasibility_score=feasibility_score,
        aisle_width_adequate=aisle_width_adequate,
        recommendations=recommendations
    )
