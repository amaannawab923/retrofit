"""
Navigation graph construction algorithms for robotic warehouse conversion.

This module provides functions to build a navigation graph G=(N,E) from a warehouse layout,
where N represents navigation nodes and E represents edges (paths) between nodes.
"""

from typing import Any, Dict, List, Set, Tuple
import numpy as np
from collections import defaultdict


class NavigationNode:
    """Represents a navigation node in the warehouse graph."""

    def __init__(
        self,
        node_id: int,
        x: float,
        y: float,
        node_type: str = 'standard',
        zone_id: str | None = None
    ):
        """
        Initialize a navigation node.

        Args:
            node_id: Unique identifier for the node
            x: X-coordinate in meters
            y: Y-coordinate in meters
            node_type: Type of node ('standard', 'intersection', 'charging', 'zone_entry')
            zone_id: Associated zone identifier if applicable
        """
        self.node_id = node_id
        self.x = x
        self.y = y
        self.node_type = node_type
        self.zone_id = zone_id
        self.is_intersection = False

    def __repr__(self) -> str:
        return f"NavigationNode(id={self.node_id}, x={self.x:.2f}, y={self.y:.2f}, type={self.node_type})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            'node_id': self.node_id,
            'x': self.x,
            'y': self.y,
            'node_type': self.node_type,
            'zone_id': self.zone_id,
            'is_intersection': self.is_intersection,
        }


class NavigationEdge:
    """Represents an edge (path) between two navigation nodes."""

    def __init__(
        self,
        edge_id: int,
        from_node: int,
        to_node: int,
        weight: float,
        bidirectional: bool = True,
        max_width: float = 2.0
    ):
        """
        Initialize a navigation edge.

        Args:
            edge_id: Unique identifier for the edge
            from_node: Source node ID
            to_node: Destination node ID
            weight: Edge weight (typically distance in meters)
            bidirectional: Whether AGVs can travel in both directions
            max_width: Maximum width of the path in meters
        """
        self.edge_id = edge_id
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
        self.bidirectional = bidirectional
        self.max_width = max_width

    def __repr__(self) -> str:
        direction = '<->' if self.bidirectional else '->'
        return f"NavigationEdge({self.from_node} {direction} {self.to_node}, weight={self.weight:.2f}m)"

    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary representation."""
        return {
            'edge_id': self.edge_id,
            'from_node': self.from_node,
            'to_node': self.to_node,
            'weight': self.weight,
            'bidirectional': self.bidirectional,
            'max_width': self.max_width,
        }


class NavigationGraph:
    """Multi-graph representation of warehouse navigation network."""

    def __init__(self):
        """Initialize an empty navigation graph."""
        self.nodes: Dict[int, NavigationNode] = {}
        self.edges: Dict[int, NavigationEdge] = {}
        self.adjacency: Dict[int, List[int]] = defaultdict(list)

    def add_node(self, node: NavigationNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node
        if node.node_id not in self.adjacency:
            self.adjacency[node.node_id] = []

    def add_edge(self, edge: NavigationEdge) -> None:
        """Add an edge to the graph."""
        self.edges[edge.edge_id] = edge
        self.adjacency[edge.from_node].append(edge.to_node)
        if edge.bidirectional:
            self.adjacency[edge.to_node].append(edge.from_node)

    def get_neighbors(self, node_id: int) -> List[int]:
        """Get all neighboring node IDs for a given node."""
        return self.adjacency.get(node_id, [])

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            'nodes': {nid: node.to_dict() for nid, node in self.nodes.items()},
            'edges': {eid: edge.to_dict() for eid, edge in self.edges.items()},
            'adjacency': {nid: neighbors for nid, neighbors in self.adjacency.items()},
        }


def build_navigation_graph(warehouse: Any, grid_size: float = 1.0) -> NavigationGraph:
    """
    Create a complete navigation graph G=(N,E) from warehouse layout.

    This is the main function that orchestrates the graph building process:
    1. Place navigation nodes on a grid
    2. Connect adjacent nodes with edges
    3. Identify intersection nodes

    Args:
        warehouse: LegacyWarehouse object with layout information
        grid_size: Spacing between navigation nodes in meters (default: 1.0m)

    Returns:
        NavigationGraph: Complete navigation graph with nodes and edges

    Example:
        >>> warehouse = LegacyWarehouse(length=50, width=30)
        >>> graph = build_navigation_graph(warehouse, grid_size=1.0)
        >>> print(f"Graph has {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    """
    graph = NavigationGraph()

    # Step 1: Place nodes on grid
    nodes = place_nodes_on_grid(warehouse, grid_size)
    for node in nodes:
        graph.add_node(node)

    # Step 2: Connect nodes with edges
    edges = connect_nodes(nodes, grid_size)
    for edge in edges:
        graph.add_edge(edge)

    # Step 3: Identify intersections
    identify_intersections(graph.nodes, graph.adjacency)

    return graph


def place_nodes_on_grid(
    warehouse: Any,
    grid_size: float = 1.0
) -> List[NavigationNode]:
    """
    Place navigation nodes on a regular grid throughout the warehouse.

    The function creates a grid of navigation nodes spaced at grid_size intervals,
    avoiding obstacles and ensuring coverage of all accessible areas.

    Args:
        warehouse: LegacyWarehouse object with dimensions and obstacles
        grid_size: Spacing between nodes in meters (default: 1.0m)

    Returns:
        List of NavigationNode objects placed on the grid

    Algorithm:
        1. Create a regular grid based on warehouse dimensions
        2. Skip nodes that fall within obstacles (racks, walls)
        3. Add nodes near zone entry/exit points
        4. Add nodes near receiving/shipping docks
    """
    nodes = []
    node_id = 0

    # Get warehouse dimensions
    length = getattr(warehouse, 'length', 50.0)
    width = getattr(warehouse, 'width', 30.0)

    # Calculate grid points
    x_points = np.arange(0, length + grid_size, grid_size)
    y_points = np.arange(0, width + grid_size, grid_size)

    # Get obstacles (racks, walls, etc.)
    obstacles = getattr(warehouse, 'obstacles', [])
    zones = getattr(warehouse, 'zones', [])

    # Place nodes on grid, avoiding obstacles
    for x in x_points:
        for y in y_points:
            # Check if position is valid (not in obstacle)
            if _is_position_valid(x, y, obstacles):
                # Determine node type based on location
                node_type = 'standard'
                zone_id = None

                # Check if node is near a zone entry
                for zone in zones:
                    if _is_near_zone_entry(x, y, zone, threshold=grid_size * 2):
                        node_type = 'zone_entry'
                        zone_id = getattr(zone, 'zone_id', None)
                        break

                node = NavigationNode(
                    node_id=node_id,
                    x=x,
                    y=y,
                    node_type=node_type,
                    zone_id=zone_id
                )
                nodes.append(node)
                node_id += 1

    # Add special nodes for critical locations
    # Add nodes at receiving area
    receiving_area = getattr(warehouse, 'receiving_area', None)
    if receiving_area:
        rx = getattr(receiving_area, 'x', 0)
        ry = getattr(receiving_area, 'y', 0)
        nodes.append(NavigationNode(
            node_id=node_id,
            x=rx,
            y=ry,
            node_type='receiving',
            zone_id='receiving'
        ))
        node_id += 1

    # Add nodes at shipping area
    shipping_area = getattr(warehouse, 'shipping_area', None)
    if shipping_area:
        sx = getattr(shipping_area, 'x', length)
        sy = getattr(shipping_area, 'y', width)
        nodes.append(NavigationNode(
            node_id=node_id,
            x=sx,
            y=sy,
            node_type='shipping',
            zone_id='shipping'
        ))
        node_id += 1

    return nodes


def connect_nodes(
    nodes: List[NavigationNode],
    grid_size: float = 1.0,
    max_connection_distance: float = 1.5
) -> List[NavigationEdge]:
    """
    Create edges between adjacent navigation nodes.

    Connects nodes that are within max_connection_distance of each other,
    typically creating a grid network of paths.

    Args:
        nodes: List of NavigationNode objects to connect
        grid_size: Grid spacing used for node placement
        max_connection_distance: Maximum distance to create connections (default: 1.5 * grid_size)

    Returns:
        List of NavigationEdge objects representing connections

    Algorithm:
        1. For each node, find all nodes within max_connection_distance
        2. Create edges to adjacent nodes (typically 4-8 neighbors)
        3. Calculate edge weight as Euclidean distance
        4. Set bidirectional=True for two-way paths
    """
    edges = []
    edge_id = 0

    # Adjust max connection distance based on grid size
    max_dist = max_connection_distance * grid_size

    # Build a spatial index for efficient neighbor lookup
    node_positions = np.array([[node.x, node.y] for node in nodes])

    # Track created edges to avoid duplicates
    created_edges: Set[Tuple[int, int]] = set()

    for i, node_a in enumerate(nodes):
        # Calculate distances to all other nodes
        distances = np.sqrt(
            (node_positions[:, 0] - node_a.x) ** 2 +
            (node_positions[:, 1] - node_a.y) ** 2
        )

        # Find neighbors within max_dist
        neighbor_indices = np.where(
            (distances > 0) & (distances <= max_dist)
        )[0]

        for j in neighbor_indices:
            node_b = nodes[j]

            # Check if edge already exists
            edge_key = tuple(sorted([node_a.node_id, node_b.node_id]))
            if edge_key in created_edges:
                continue

            # Calculate edge weight (Euclidean distance)
            weight = distances[j]

            # Create bidirectional edge
            edge = NavigationEdge(
                edge_id=edge_id,
                from_node=node_a.node_id,
                to_node=node_b.node_id,
                weight=weight,
                bidirectional=True,
                max_width=2.0  # Default path width
            )

            edges.append(edge)
            created_edges.add(edge_key)
            edge_id += 1

    return edges


def identify_intersections(
    nodes: Dict[int, NavigationNode],
    adjacency: Dict[int, List[int]]
) -> None:
    """
    Mark nodes that are intersections (3+ connected paths).

    Intersections are critical for traffic management and path planning,
    as they represent decision points in the navigation graph.

    Args:
        nodes: Dictionary of node_id -> NavigationNode
        adjacency: Dictionary of node_id -> list of neighbor node_ids

    Side Effects:
        Modifies NavigationNode objects in-place, setting is_intersection=True
        and updating node_type to 'intersection' for nodes with 3+ neighbors

    Algorithm:
        1. Count neighbors for each node
        2. If neighbors >= 3, mark as intersection
        3. Update node type accordingly
    """
    for node_id, node in nodes.items():
        neighbor_count = len(adjacency.get(node_id, []))

        # Intersection: 3 or more connections
        if neighbor_count >= 3:
            node.is_intersection = True
            # Update type only if not a special type
            if node.node_type == 'standard':
                node.node_type = 'intersection'


def _is_position_valid(
    x: float,
    y: float,
    obstacles: List[Any],
    clearance: float = 0.5
) -> bool:
    """
    Check if a position is valid (not inside an obstacle).

    Args:
        x: X-coordinate to check
        y: Y-coordinate to check
        obstacles: List of obstacle objects with position and dimensions
        clearance: Minimum clearance from obstacles in meters

    Returns:
        True if position is valid, False if inside an obstacle
    """
    for obstacle in obstacles:
        # Get obstacle bounds
        ox = getattr(obstacle, 'x', 0)
        oy = getattr(obstacle, 'y', 0)
        owidth = getattr(obstacle, 'width', 0)
        oheight = getattr(obstacle, 'height', 0)

        # Check if point is inside obstacle (with clearance)
        if (ox - clearance <= x <= ox + owidth + clearance and
            oy - clearance <= y <= oy + oheight + clearance):
            return False

    return True


def _is_near_zone_entry(
    x: float,
    y: float,
    zone: Any,
    threshold: float = 2.0
) -> bool:
    """
    Check if a position is near a zone entry point.

    Args:
        x: X-coordinate to check
        y: Y-coordinate to check
        zone: Zone object with entry point information
        threshold: Distance threshold in meters

    Returns:
        True if position is within threshold distance of zone entry
    """
    entry_x = getattr(zone, 'entry_x', None)
    entry_y = getattr(zone, 'entry_y', None)

    if entry_x is None or entry_y is None:
        return False

    distance = np.sqrt((x - entry_x) ** 2 + (y - entry_y) ** 2)
    return distance <= threshold
