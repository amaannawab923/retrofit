"""
Node and Edge Models for Navigation Graph

Defines the navigation nodes and edges for the robotic warehouse system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class NodeType(Enum):
    """Types of navigation nodes in the warehouse."""
    INTERSECTION = "intersection"
    CHARGING = "charging"
    PICKUP = "pickup"
    DROPOFF = "dropoff"
    STAGING = "staging"
    MAINTENANCE = "maintenance"


@dataclass
class Node:
    """
    Represents a navigation node in the warehouse.

    Attributes:
        id: Unique identifier for the node (e.g., "N01", "CHG1")
        x: X-coordinate in meters
        y: Y-coordinate in meters
        node_type: Type of the node
        zone: Zone identifier (optional)
        metadata: Additional metadata (optional)
    """
    id: str
    x: float
    y: float
    node_type: NodeType
    zone: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Node({self.id}, type={self.node_type.value}, pos=({self.x}, {self.y}))"

    def distance_to(self, other: 'Node') -> float:
        """Calculate Euclidean distance to another node."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class NavigationEdge:
    """
    Represents a connection between two navigation nodes.

    Attributes:
        from_node: Source node ID
        to_node: Destination node ID
        distance: Distance in meters
        bidirectional: Whether the edge can be traversed in both directions
        metadata: Additional metadata (optional)
    """
    from_node: str
    to_node: str
    distance: float
    bidirectional: bool = True
    metadata: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        arrow = "<->" if self.bidirectional else "->"
        return f"Edge({self.from_node} {arrow} {self.to_node}, {self.distance:.2f}m)"
