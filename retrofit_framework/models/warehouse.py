"""Warehouse data models for legacy and robotic warehouses."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ZoneType(str, Enum):
    """Types of zones in a warehouse."""

    PICKUP = "pickup"
    DROP = "drop"
    STORAGE = "storage"
    CHARGING = "charging"
    AISLE = "aisle"
    CROSSOVER = "crossover"


class NodeType(str, Enum):
    """Types of nodes in the navigation graph."""

    PICKUP = "pickup"
    DROP = "drop"
    INTERSECTION = "intersection"
    AISLE_ENTRY = "aisle_entry"
    AISLE_EXIT = "aisle_exit"
    CHARGING = "charging"
    WAYPOINT = "waypoint"
    STAGING = "staging"
    MAINTENANCE = "maintenance"


class Node(BaseModel):
    """Represents a node in the warehouse navigation graph."""

    id: str = Field(..., description="Unique identifier for the node")
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    zone_type: ZoneType = Field(..., description="Type of zone this node belongs to")
    node_type: NodeType = Field(..., description="Type of node for navigation")

    @field_validator("x", "y")
    @classmethod
    def validate_coordinates(cls, v: float) -> float:
        """Ensure coordinates are non-negative."""
        if v < 0:
            raise ValueError("Coordinates must be non-negative")
        return v

    def distance_to(self, other: "Node") -> float:
        """Calculate Euclidean distance to another node."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Edge(BaseModel):
    """Represents an edge connecting two nodes in the navigation graph."""

    id: str = Field(..., description="Unique identifier for the edge")
    from_node: str = Field(..., description="ID of the source node")
    to_node: str = Field(..., description="ID of the destination node")
    distance: float = Field(..., description="Distance in meters", gt=0)
    bidirectional: bool = Field(
        default=True, description="Whether the edge can be traversed in both directions"
    )


class Zone(BaseModel):
    """Represents a zone in the warehouse."""

    id: str = Field(..., description="Unique identifier for the zone")
    name: str = Field(..., description="Human-readable name for the zone")
    x: float = Field(..., description="X coordinate of zone origin (bottom-left)")
    y: float = Field(..., description="Y coordinate of zone origin (bottom-left)")
    width: float = Field(..., description="Width of the zone in meters", gt=0)
    height: float = Field(..., description="Height of the zone in meters", gt=0)
    zone_type: ZoneType = Field(..., description="Type of zone")

    @field_validator("x", "y")
    @classmethod
    def validate_coordinates(cls, v: float) -> float:
        """Ensure coordinates are non-negative."""
        if v < 0:
            raise ValueError("Coordinates must be non-negative")
        return v


class LegacyWarehouse(BaseModel):
    """Represents a traditional warehouse layout."""

    name: str = Field(..., description="Name of the warehouse")
    width: float = Field(..., description="Total width of the warehouse in meters", gt=0)
    length: float = Field(..., description="Total length of the warehouse in meters", gt=0)
    aisles: int = Field(..., description="Number of aisles", gt=0)
    aisle_width: float = Field(..., description="Width of each aisle in meters", gt=0)
    aisle_length: float = Field(..., description="Length of each aisle in meters", gt=0)
    zones: list[Zone] = Field(default_factory=list, description="List of zones in the warehouse")
    nodes: list[Node] = Field(default_factory=list, description="List of navigation nodes")
    edges: list[Edge] = Field(default_factory=list, description="List of edges connecting nodes")

    @field_validator("zones")
    @classmethod
    def validate_unique_zone_ids(cls, v: list[Zone]) -> list[Zone]:
        """Ensure all zone IDs are unique."""
        zone_ids = [zone.id for zone in v]
        if len(zone_ids) != len(set(zone_ids)):
            raise ValueError("Zone IDs must be unique")
        return v

    @field_validator("nodes")
    @classmethod
    def validate_unique_node_ids(cls, v: list[Node]) -> list[Node]:
        """Ensure all node IDs are unique."""
        node_ids = [node.id for node in v]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Node IDs must be unique")
        return v

    @field_validator("edges")
    @classmethod
    def validate_unique_edge_ids(cls, v: list[Edge]) -> list[Edge]:
        """Ensure all edge IDs are unique."""
        edge_ids = [edge.id for edge in v]
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("Edge IDs must be unique")
        return v

    @property
    def total_area(self) -> float:
        """Total warehouse floor area in square meters."""
        return self.width * self.length

    @property
    def storage_area(self) -> float:
        """Approximate storage area in square meters."""
        return self.aisles * self.aisle_length * self.aisle_width

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_nodes_by_type(self, node_type: NodeType) -> list[Node]:
        """Get all nodes of a specific type."""
        return [node for node in self.nodes if node.node_type == node_type]


class TrafficRule(BaseModel):
    """Represents a traffic rule for AGV navigation."""

    rule_id: str = Field(..., description="Unique identifier for the rule")
    rule_type: str = Field(..., description="Type of traffic rule (e.g., 'one_way', 'priority')")
    applies_to: list[str] = Field(..., description="List of edge IDs this rule applies to")
    description: Optional[str] = Field(None, description="Human-readable description of the rule")


class RoboticWarehouse(LegacyWarehouse):
    """Represents a warehouse retrofitted with robotic systems."""

    charging_stations: list[Node] = Field(
        default_factory=list, description="List of charging station nodes"
    )
    navigation_graph: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Adjacency list representation of the navigation graph",
    )
    distance_matrix: dict[str, dict[str, float]] = Field(
        default_factory=dict,
        description="Pre-computed distance matrix for path planning",
    )
    traffic_rules: list[TrafficRule] = Field(
        default_factory=list, description="Traffic rules for AGV navigation"
    )
    feasibility_score: float = Field(
        default=0.0, description="Feasibility score for robotic conversion (0-10)"
    )
    conversion_notes: list[str] = Field(
        default_factory=list, description="Notes and recommendations from conversion"
    )

    @field_validator("charging_stations")
    @classmethod
    def validate_charging_station_types(cls, v: list[Node]) -> list[Node]:
        """Ensure all charging stations have the correct node type."""
        for station in v:
            if station.node_type != NodeType.CHARGING:
                raise ValueError("All charging stations must have node_type='charging'")
        return v

    @property
    def num_nodes(self) -> int:
        """Total number of navigation nodes."""
        return len(self.nodes)

    @property
    def num_edges(self) -> int:
        """Total number of edges."""
        return len(self.edges)
