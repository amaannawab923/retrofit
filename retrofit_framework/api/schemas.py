"""
Pydantic schemas for API request and response models.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NodeResponse(BaseModel):
    """Navigation node response schema."""

    id: str = Field(..., description="Unique node identifier")
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    type: str = Field(..., description="Node type (intersection, dock, charging, etc.)")


class EdgeResponse(BaseModel):
    """Navigation edge response schema."""

    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Destination node ID")
    distance: float = Field(..., description="Edge distance in meters")
    bidirectional: bool = Field(..., description="Whether edge is bidirectional")

    class Config:
        populate_by_name = True


class NavigationGraphResponse(BaseModel):
    """Navigation graph response schema."""

    nodes: List[NodeResponse] = Field(..., description="List of navigation nodes")
    edges: List[EdgeResponse] = Field(..., description="List of navigation edges")


class WarehouseDimensions(BaseModel):
    """Warehouse dimensions."""

    width: float = Field(..., description="Warehouse width in meters")
    height: float = Field(..., description="Warehouse height in meters")


class RackInfo(BaseModel):
    """Rack information."""

    count: int = Field(..., description="Number of racks")
    width: float = Field(..., description="Rack width in meters")
    height: float = Field(..., description="Rack height in meters")
    positions: List[Dict[str, float]] = Field(..., description="Rack positions")


class ZoneInfo(BaseModel):
    """Zone information."""

    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    width: float = Field(..., description="Width in meters")
    height: float = Field(..., description="Height in meters")


class OriginalWarehouseResponse(BaseModel):
    """Original warehouse specification."""

    warehouse_dimensions: WarehouseDimensions
    racks: RackInfo
    aisle_width: float = Field(..., description="Aisle width in meters")
    loading_docks: List[Dict[str, float]] = Field(..., description="Loading dock positions")
    shipping_area: ZoneInfo


class ChargingStation(BaseModel):
    """Charging station location."""

    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")


class TrafficRule(BaseModel):
    """Traffic rule information."""

    aisle: str = Field(..., description="Aisle identifier")
    direction: str = Field(..., description="Direction (north, south, east, west)")
    description: Optional[str] = Field(None, description="Rule description")


class PriorityZone(BaseModel):
    """Priority zone configuration."""

    name: str = Field(..., description="Zone name")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    width: float = Field(..., description="Width in meters")
    height: float = Field(..., description="Height in meters")
    priority: str = Field(..., description="Priority level (high, medium, low)")


class NoStoppingZone(BaseModel):
    """No-stopping zone."""

    x: float
    y: float
    width: float
    height: float


class TrafficRulesResponse(BaseModel):
    """Traffic rules configuration."""

    one_way_aisles: List[TrafficRule]
    priority_zones: List[PriorityZone]
    no_stopping_zones: List[NoStoppingZone]


class RoboticWarehouseResponse(BaseModel):
    """Robotic warehouse specification."""

    warehouse_dimensions: WarehouseDimensions
    racks: RackInfo
    aisle_width: float
    loading_docks: List[Dict[str, float]]
    shipping_area: ZoneInfo
    charging_stations: List[ChargingStation]
    conversion_notes: List[str] = Field(..., description="Conversion notes and recommendations")
    feasibility_score: float = Field(..., description="Feasibility score (0-10)")


class ConversionSummary(BaseModel):
    """Summary of the conversion process."""

    total_nodes: int = Field(..., description="Total navigation nodes")
    total_edges: int = Field(..., description="Total navigation edges")
    charging_stations_count: int = Field(..., description="Number of charging stations")
    feasibility_score: float = Field(..., description="Overall feasibility score")
    aisle_width_adequate: bool = Field(..., description="Whether aisle width is adequate")
    recommendations: List[str] = Field(..., description="List of recommendations")


class ConversionResponse(BaseModel):
    """Complete conversion API response."""

    original_warehouse: OriginalWarehouseResponse = Field(
        ..., description="Original legacy warehouse specification"
    )
    robotic_warehouse: RoboticWarehouseResponse = Field(
        ..., description="Converted robotic warehouse specification"
    )
    navigation_graph: NavigationGraphResponse = Field(
        ..., description="Navigation graph with nodes and edges"
    )
    distance_matrix: List[List[float]] = Field(
        ..., description="All-pairs shortest path distance matrix"
    )
    traffic_rules: TrafficRulesResponse = Field(
        ..., description="Traffic management rules"
    )
    summary: ConversionSummary = Field(
        ..., description="Conversion summary and statistics"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "original_warehouse": {
                    "warehouse_dimensions": {"width": 50.0, "height": 30.0},
                    "racks": {
                        "count": 12,
                        "width": 4.0,
                        "height": 8.0,
                        "positions": [{"x": 5.0, "y": 5.0}]
                    },
                    "aisle_width": 2.5,
                    "loading_docks": [{"x": 1.0, "y": 8.0}],
                    "shipping_area": {"x": 40.0, "y": 22.0, "width": 8.0, "height": 6.0}
                },
                "summary": {
                    "total_nodes": 27,
                    "total_edges": 48,
                    "charging_stations_count": 3,
                    "feasibility_score": 8.6,
                    "aisle_width_adequate": False,
                    "recommendations": ["Consider widening aisles to 3.0m"]
                }
            }
        }
