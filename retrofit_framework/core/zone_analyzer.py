"""
Zone analysis algorithms for warehouse retrofit conversion.

This module provides functions to analyze storage zones, calculate accessibility,
and identify critical paths for AGV traffic optimization.
"""

from typing import Any, Dict, List, Tuple, Set
import numpy as np
from collections import defaultdict
from .graph_builder import NavigationNode, NavigationGraph
from .distance_calculator import calculate_euclidean_distance, get_closest_nodes


class ZoneMetrics:
    """Metrics for a storage zone in the warehouse."""

    def __init__(self, zone_id: str):
        """
        Initialize zone metrics.

        Args:
            zone_id: Unique identifier for the zone
        """
        self.zone_id = zone_id
        self.area: float = 0.0
        self.capacity: int = 0
        self.entry_nodes: List[int] = []
        self.avg_distance_to_shipping: float = 0.0
        self.avg_distance_to_receiving: float = 0.0
        self.accessibility_score: float = 0.0
        self.traffic_density: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'zone_id': self.zone_id,
            'area': self.area,
            'capacity': self.capacity,
            'entry_nodes': self.entry_nodes,
            'avg_distance_to_shipping': self.avg_distance_to_shipping,
            'avg_distance_to_receiving': self.avg_distance_to_receiving,
            'accessibility_score': self.accessibility_score,
            'traffic_density': self.traffic_density,
        }


class CriticalPath:
    """Represents a critical path in the warehouse."""

    def __init__(
        self,
        path_id: str,
        nodes: List[int],
        traffic_volume: float,
        bottleneck_score: float
    ):
        """
        Initialize critical path.

        Args:
            path_id: Unique identifier for the path
            nodes: List of node IDs in the path
            traffic_volume: Expected traffic volume (trips per hour)
            bottleneck_score: Bottleneck severity score (0-1)
        """
        self.path_id = path_id
        self.nodes = nodes
        self.traffic_volume = traffic_volume
        self.bottleneck_score = bottleneck_score

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'path_id': self.path_id,
            'nodes': self.nodes,
            'traffic_volume': self.traffic_volume,
            'bottleneck_score': self.bottleneck_score,
        }


def analyze_zones(warehouse: Any) -> Dict[str, ZoneMetrics]:
    """
    Analyze all storage zones in the warehouse.

    Calculates comprehensive metrics for each zone including area, capacity,
    accessibility, and traffic patterns.

    Args:
        warehouse: Warehouse object with zones and layout information

    Returns:
        Dictionary mapping zone_id to ZoneMetrics

    Analysis includes:
        - Physical dimensions (area, capacity)
        - Entry/exit point identification
        - Distance to shipping/receiving areas
        - Accessibility scoring
        - Expected traffic density

    Example:
        >>> metrics = analyze_zones(warehouse)
        >>> for zone_id, metric in metrics.items():
        ...     print(f"Zone {zone_id}: {metric.accessibility_score:.2f}")
    """
    zones = getattr(warehouse, 'zones', [])
    zone_metrics = {}

    for zone in zones:
        zone_id = getattr(zone, 'zone_id', str(id(zone)))
        metrics = ZoneMetrics(zone_id)

        # Calculate zone area
        width = getattr(zone, 'width', 0)
        height = getattr(zone, 'height', 0)
        metrics.area = width * height

        # Get zone capacity
        metrics.capacity = getattr(zone, 'capacity', 0)

        # Store zone metrics
        zone_metrics[zone_id] = metrics

    return zone_metrics


def calculate_zone_accessibility(
    zones: List[Any],
    nodes: Dict[int, NavigationNode],
    shipping_location: Tuple[float, float] | None = None,
    receiving_location: Tuple[float, float] | None = None
) -> Dict[str, float]:
    """
    Calculate accessibility scores for all zones.

    Accessibility is measured by how easily AGVs can reach a zone from
    key locations (shipping, receiving, charging stations).

    Args:
        zones: List of zone objects
        nodes: Dictionary of node_id -> NavigationNode
        shipping_location: (x, y) coordinates of shipping area
        receiving_location: (x, y) coordinates of receiving area

    Returns:
        Dictionary mapping zone_id to accessibility score (0-1, higher is better)

    Algorithm:
        1. Find entry nodes for each zone
        2. Calculate average distance to shipping/receiving
        3. Count number of accessible paths
        4. Compute weighted accessibility score

    Accessibility Score Formula:
        score = w1 * (1/avg_distance) + w2 * (entry_points/max_entry_points)
        where w1=0.6, w2=0.4 (weights)
    """
    accessibility_scores = {}

    # Default locations if not provided
    if shipping_location is None:
        shipping_location = (0.0, 0.0)
    if receiving_location is None:
        receiving_location = (0.0, 0.0)

    # Create temporary nodes for shipping and receiving
    ship_node = NavigationNode(-1, shipping_location[0], shipping_location[1])
    recv_node = NavigationNode(-2, receiving_location[0], receiving_location[1])

    for zone in zones:
        zone_id = getattr(zone, 'zone_id', str(id(zone)))

        # Get zone center
        zone_x = getattr(zone, 'x', 0) + getattr(zone, 'width', 0) / 2
        zone_y = getattr(zone, 'y', 0) + getattr(zone, 'height', 0) / 2

        # Find closest nodes to zone
        zone_center_node = NavigationNode(-3, zone_x, zone_y)
        closest_nodes = get_closest_nodes(zone_x, zone_y, nodes, k=5)

        if not closest_nodes:
            accessibility_scores[zone_id] = 0.0
            continue

        # Calculate average distance to shipping
        avg_dist_shipping = np.mean([
            calculate_euclidean_distance(nodes[nid], ship_node)
            for nid, _ in closest_nodes
        ])

        # Calculate average distance to receiving
        avg_dist_receiving = np.mean([
            calculate_euclidean_distance(nodes[nid], recv_node)
            for nid, _ in closest_nodes
        ])

        # Number of entry points (more is better)
        num_entry_points = len(closest_nodes)
        max_entry_points = 5

        # Calculate accessibility score
        # Lower distance = higher score
        distance_score = 1.0 / (1.0 + (avg_dist_shipping + avg_dist_receiving) / 100.0)
        entry_score = num_entry_points / max_entry_points

        # Weighted combination
        accessibility_score = 0.6 * distance_score + 0.4 * entry_score
        accessibility_scores[zone_id] = min(1.0, accessibility_score)

    return accessibility_scores


def identify_critical_paths(
    distance_matrix: np.ndarray,
    zones: List[Any],
    nodes: Dict[int, NavigationNode],
    traffic_data: Dict[str, float] | None = None
) -> List[CriticalPath]:
    """
    Identify high-traffic critical paths that may become bottlenecks.

    Critical paths are routes that experience high traffic volume and
    may require special attention for traffic management (one-way rules,
    priority lanes, etc.).

    Args:
        distance_matrix: NxN distance matrix between nodes
        zones: List of zone objects
        nodes: Dictionary of node_id -> NavigationNode
        traffic_data: Optional dict of route -> expected traffic volume

    Returns:
        List of CriticalPath objects sorted by importance

    Algorithm:
        1. Identify main corridors (long straight paths)
        2. Calculate expected traffic based on zone activity
        3. Identify potential bottlenecks (narrow passages, intersections)
        4. Score paths by traffic volume and bottleneck risk

    Bottleneck Score:
        Considers: traffic volume, path width, intersection count, alternatives
    """
    critical_paths = []
    path_id_counter = 0

    # Find main shipping/receiving corridors
    shipping_nodes = [
        nid for nid, node in nodes.items()
        if node.node_type == 'shipping'
    ]
    receiving_nodes = [
        nid for nid, node in nodes.items()
        if node.node_type == 'receiving'
    ]

    # Identify high-traffic zone entry points
    high_traffic_nodes = []
    for zone in zones:
        zone_id = getattr(zone, 'zone_id', '')
        zone_x = getattr(zone, 'x', 0) + getattr(zone, 'width', 0) / 2
        zone_y = getattr(zone, 'y', 0) + getattr(zone, 'height', 0) / 2

        # Find closest nodes to zone
        closest = get_closest_nodes(zone_x, zone_y, nodes, k=2)
        high_traffic_nodes.extend([nid for nid, _ in closest])

    # Create paths between key points
    key_pairs = []

    # Shipping to receiving
    for ship_node in shipping_nodes:
        for recv_node in receiving_nodes:
            key_pairs.append((ship_node, recv_node, 'shipping_to_receiving'))

    # Shipping to zones
    for ship_node in shipping_nodes:
        for zone_node in high_traffic_nodes:
            key_pairs.append((ship_node, zone_node, 'shipping_to_zone'))

    # Receiving to zones
    for recv_node in receiving_nodes:
        for zone_node in high_traffic_nodes:
            key_pairs.append((recv_node, zone_node, 'receiving_to_zone'))

    # Analyze each key path
    for start_node, end_node, path_type in key_pairs:
        if start_node not in nodes or end_node not in nodes:
            continue

        # Simple path (direct nodes)
        path_nodes = [start_node, end_node]

        # Estimate traffic volume based on path type
        if path_type == 'shipping_to_receiving':
            traffic_volume = 50.0  # High traffic
        elif path_type == 'shipping_to_zone':
            traffic_volume = 30.0  # Medium-high traffic
        else:
            traffic_volume = 20.0  # Medium traffic

        # Use provided traffic data if available
        if traffic_data:
            path_key = f"{start_node}_{end_node}"
            traffic_volume = traffic_data.get(path_key, traffic_volume)

        # Calculate bottleneck score
        # Higher score = more likely to be bottleneck
        distance = distance_matrix[start_node, end_node] if distance_matrix.size > 0 else 0.0
        bottleneck_score = _calculate_bottleneck_score(
            path_nodes,
            nodes,
            traffic_volume,
            distance
        )

        # Create critical path if score is significant
        if bottleneck_score > 0.3:  # Threshold for criticality
            critical_path = CriticalPath(
                path_id=f"path_{path_id_counter}",
                nodes=path_nodes,
                traffic_volume=traffic_volume,
                bottleneck_score=bottleneck_score
            )
            critical_paths.append(critical_path)
            path_id_counter += 1

    # Sort by bottleneck score (most critical first)
    critical_paths.sort(key=lambda p: p.bottleneck_score, reverse=True)

    return critical_paths


def identify_congestion_zones(
    nodes: Dict[int, NavigationNode],
    critical_paths: List[CriticalPath]
) -> List[Tuple[int, float]]:
    """
    Identify nodes that are likely to experience congestion.

    Args:
        nodes: Dictionary of node_id -> NavigationNode
        critical_paths: List of critical paths

    Returns:
        List of tuples (node_id, congestion_score) sorted by score

    Congestion Score:
        Number of critical paths passing through node × average traffic volume
    """
    congestion_scores = defaultdict(float)

    # Count how many critical paths pass through each node
    for path in critical_paths:
        for node_id in path.nodes:
            if node_id in nodes:
                # Weight by traffic volume and bottleneck score
                weight = path.traffic_volume * path.bottleneck_score
                congestion_scores[node_id] += weight

    # Convert to sorted list
    congestion_list = [
        (node_id, score)
        for node_id, score in congestion_scores.items()
    ]
    congestion_list.sort(key=lambda x: x[1], reverse=True)

    return congestion_list


def calculate_zone_distances(
    zones: List[Any],
    nodes: Dict[int, NavigationNode]
) -> Dict[Tuple[str, str], float]:
    """
    Calculate inter-zone distances for all zone pairs.

    Args:
        zones: List of zone objects
        nodes: Dictionary of node_id -> NavigationNode

    Returns:
        Dictionary mapping (zone_id_1, zone_id_2) to distance in meters

    Example:
        >>> distances = calculate_zone_distances(zones, nodes)
        >>> dist = distances[('A1', 'B2')]
        >>> print(f"Distance from A1 to B2: {dist:.2f}m")
    """
    zone_distances = {}

    for i, zone_a in enumerate(zones):
        zone_a_id = getattr(zone_a, 'zone_id', str(i))
        zone_a_x = getattr(zone_a, 'x', 0) + getattr(zone_a, 'width', 0) / 2
        zone_a_y = getattr(zone_a, 'y', 0) + getattr(zone_a, 'height', 0) / 2

        for j, zone_b in enumerate(zones):
            if i >= j:
                continue

            zone_b_id = getattr(zone_b, 'zone_id', str(j))
            zone_b_x = getattr(zone_b, 'x', 0) + getattr(zone_b, 'width', 0) / 2
            zone_b_y = getattr(zone_b, 'y', 0) + getattr(zone_b, 'height', 0) / 2

            # Calculate Euclidean distance between zone centers
            distance = np.sqrt(
                (zone_a_x - zone_b_x) ** 2 +
                (zone_a_y - zone_b_y) ** 2
            )

            zone_distances[(zone_a_id, zone_b_id)] = distance
            zone_distances[(zone_b_id, zone_a_id)] = distance

    return zone_distances


def _calculate_bottleneck_score(
    path_nodes: List[int],
    nodes: Dict[int, NavigationNode],
    traffic_volume: float,
    distance: float
) -> float:
    """
    Calculate bottleneck score for a path.

    Args:
        path_nodes: List of node IDs in the path
        nodes: Dictionary of node_id -> NavigationNode
        traffic_volume: Expected traffic volume (trips/hour)
        distance: Path distance in meters

    Returns:
        Bottleneck score (0-1, higher means more likely to bottleneck)

    Factors:
        - High traffic volume increases score
        - Long distance increases score
        - Intersections along path increase score
        - Narrow paths increase score
    """
    if not path_nodes or traffic_volume <= 0:
        return 0.0

    # Traffic volume component (normalize to 0-1)
    # Assume max traffic of 100 trips/hour
    traffic_score = min(1.0, traffic_volume / 100.0)

    # Distance component (longer paths more critical)
    # Normalize by typical warehouse dimension (50m)
    distance_score = min(1.0, distance / 50.0)

    # Intersection component
    intersection_count = sum(
        1 for nid in path_nodes
        if nid in nodes and nodes[nid].is_intersection
    )
    intersection_score = min(1.0, intersection_count / 3.0)

    # Weighted combination
    bottleneck_score = (
        0.5 * traffic_score +
        0.3 * intersection_score +
        0.2 * distance_score
    )

    return min(1.0, bottleneck_score)


def recommend_zone_improvements(
    zone_metrics: Dict[str, ZoneMetrics],
    accessibility_threshold: float = 0.5
) -> Dict[str, List[str]]:
    """
    Recommend improvements for zones with low accessibility.

    Args:
        zone_metrics: Dictionary of zone_id -> ZoneMetrics
        accessibility_threshold: Minimum acceptable accessibility score

    Returns:
        Dictionary mapping zone_id to list of recommended improvements

    Example:
        >>> recommendations = recommend_zone_improvements(zone_metrics)
        >>> for zone_id, improvements in recommendations.items():
        ...     print(f"Zone {zone_id}: {improvements}")
    """
    recommendations = {}

    for zone_id, metrics in zone_metrics.items():
        zone_recommendations = []

        # Check accessibility
        if metrics.accessibility_score < accessibility_threshold:
            zone_recommendations.append(
                f"Low accessibility score ({metrics.accessibility_score:.2f}). "
                "Consider adding more entry/exit points."
            )

        # Check distance to shipping
        if metrics.avg_distance_to_shipping > 30.0:
            zone_recommendations.append(
                f"High distance to shipping ({metrics.avg_distance_to_shipping:.1f}m). "
                "Consider relocating fast-moving items."
            )

        # Check traffic density
        if metrics.traffic_density > 0.8:
            zone_recommendations.append(
                f"High traffic density ({metrics.traffic_density:.2f}). "
                "Consider implementing one-way traffic rules."
            )

        if zone_recommendations:
            recommendations[zone_id] = zone_recommendations

    return recommendations
