"""
Distance matrix calculations and travel time estimation for robotic warehouses.

This module provides functions to calculate distances between nodes, build
distance matrices, and estimate travel times for AGVs.
"""

from typing import Dict, List, Tuple
import numpy as np
from .graph_builder import NavigationNode, NavigationGraph


def calculate_manhattan_distance(node_a: NavigationNode, node_b: NavigationNode) -> float:
    """
    Calculate Manhattan (L1) distance between two nodes.

    Manhattan distance is the sum of absolute differences in coordinates,
    representing the distance traveled along grid lines (only horizontal
    and vertical movement).

    Args:
        node_a: First navigation node
        node_b: Second navigation node

    Returns:
        Manhattan distance in meters

    Formula:
        d = |x₁ - x₂| + |y₁ - y₂|

    Example:
        >>> node_a = NavigationNode(1, 0, 0)
        >>> node_b = NavigationNode(2, 3, 4)
        >>> distance = calculate_manhattan_distance(node_a, node_b)
        >>> print(f"Manhattan distance: {distance}m")  # Output: 7.0m
    """
    return abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)


def calculate_euclidean_distance(node_a: NavigationNode, node_b: NavigationNode) -> float:
    """
    Calculate Euclidean (L2) distance between two nodes.

    Euclidean distance is the straight-line distance between two points,
    representing the shortest possible path.

    Args:
        node_a: First navigation node
        node_b: Second navigation node

    Returns:
        Euclidean distance in meters

    Formula:
        d = √[(x₁ - x₂)² + (y₁ - y₂)²]

    Example:
        >>> node_a = NavigationNode(1, 0, 0)
        >>> node_b = NavigationNode(2, 3, 4)
        >>> distance = calculate_euclidean_distance(node_a, node_b)
        >>> print(f"Euclidean distance: {distance:.2f}m")  # Output: 5.00m
    """
    return np.sqrt((node_a.x - node_b.x) ** 2 + (node_a.y - node_b.y) ** 2)


def build_distance_matrix(
    nodes: Dict[int, NavigationNode],
    distance_type: str = 'euclidean'
) -> np.ndarray:
    """
    Build an NxN distance matrix for all nodes.

    The distance matrix D[i,j] contains the distance from node i to node j.
    This matrix is used for quick distance lookups in path planning algorithms.

    Args:
        nodes: Dictionary of node_id -> NavigationNode
        distance_type: Type of distance metric ('euclidean' or 'manhattan')

    Returns:
        NxN numpy array where D[i,j] is the distance from node i to node j

    Properties:
        - D[i,i] = 0 (distance from node to itself is zero)
        - D[i,j] = D[j,i] (symmetric for both distance types)
        - All values are non-negative

    Example:
        >>> nodes = {0: NavigationNode(0, 0, 0), 1: NavigationNode(1, 3, 4)}
        >>> matrix = build_distance_matrix(nodes)
        >>> print(matrix)
        [[0.  5. ]
         [5.  0. ]]
    """
    n_nodes = len(nodes)
    node_ids = sorted(nodes.keys())
    distance_matrix = np.zeros((n_nodes, n_nodes), dtype=np.float32)

    # Select distance function
    if distance_type == 'manhattan':
        dist_func = calculate_manhattan_distance
    else:
        dist_func = calculate_euclidean_distance

    # Calculate distances for all node pairs
    for i, node_id_a in enumerate(node_ids):
        for j, node_id_b in enumerate(node_ids):
            if i == j:
                distance_matrix[i, j] = 0.0
            else:
                distance = dist_func(nodes[node_id_a], nodes[node_id_b])
                distance_matrix[i, j] = distance

    return distance_matrix


def calculate_travel_time(
    distance: float,
    speed: float = 1.5,
    turns: int = 0,
    turn_delay: float = 2.0
) -> float:
    """
    Calculate AGV travel time considering distance, speed, and turns.

    The travel time includes both straight-line movement time and delays
    for turns at intersections. This is crucial for accurate task scheduling.

    Args:
        distance: Travel distance in meters
        speed: AGV speed in meters/second (default: 1.5 m/s)
        turns: Number of 90-degree turns in the path
        turn_delay: Time delay per turn in seconds (default: 2.0s)

    Returns:
        Total travel time in seconds

    Formula:
        t = (distance / speed) + (turns × turn_delay)

    Example:
        >>> distance = 15.0  # 15 meters
        >>> speed = 1.5  # 1.5 m/s
        >>> turns = 2  # Two 90-degree turns
        >>> time = calculate_travel_time(distance, speed, turns)
        >>> print(f"Travel time: {time:.1f}s")  # Output: 14.0s

    Notes:
        - Default AGV speed of 1.5 m/s is typical for warehouse robots
        - Turn delay accounts for deceleration, turning, and acceleration
        - For paths with curves, approximate with equivalent 90-degree turns
    """
    if speed <= 0:
        raise ValueError("Speed must be positive")
    if distance < 0:
        raise ValueError("Distance cannot be negative")
    if turns < 0:
        raise ValueError("Number of turns cannot be negative")

    straight_time = distance / speed
    turn_time = turns * turn_delay
    total_time = straight_time + turn_time

    return total_time


def calculate_path_distance(
    path: List[int],
    distance_matrix: np.ndarray
) -> float:
    """
    Calculate total distance for a path through multiple nodes.

    Args:
        path: List of node IDs representing the path
        distance_matrix: NxN distance matrix

    Returns:
        Total path distance in meters

    Example:
        >>> path = [0, 5, 12, 8]
        >>> total_distance = calculate_path_distance(path, distance_matrix)
    """
    if len(path) < 2:
        return 0.0

    total_distance = 0.0
    for i in range(len(path) - 1):
        total_distance += distance_matrix[path[i], path[i + 1]]

    return total_distance


def count_turns_in_path(
    path: List[int],
    nodes: Dict[int, NavigationNode],
    angle_threshold: float = 45.0
) -> int:
    """
    Count the number of significant turns in a path.

    A turn is counted when the angle between consecutive path segments
    exceeds the angle_threshold (typically 45 degrees).

    Args:
        path: List of node IDs representing the path
        nodes: Dictionary of node_id -> NavigationNode
        angle_threshold: Minimum angle to count as a turn (degrees)

    Returns:
        Number of turns in the path

    Example:
        >>> path = [0, 1, 2, 3]
        >>> turns = count_turns_in_path(path, nodes)
    """
    if len(path) < 3:
        return 0

    turns = 0
    angle_threshold_rad = np.radians(angle_threshold)

    for i in range(1, len(path) - 1):
        prev_node = nodes[path[i - 1]]
        curr_node = nodes[path[i]]
        next_node = nodes[path[i + 1]]

        # Calculate vectors
        vec1 = np.array([curr_node.x - prev_node.x, curr_node.y - prev_node.y])
        vec2 = np.array([next_node.x - curr_node.x, next_node.y - curr_node.y])

        # Normalize vectors
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)

        # Calculate angle between vectors
        dot_product = np.clip(np.dot(vec1_norm, vec2_norm), -1.0, 1.0)
        angle = np.arccos(dot_product)

        # Count as turn if angle exceeds threshold
        if angle >= angle_threshold_rad:
            turns += 1

    return turns


def build_time_matrix(
    distance_matrix: np.ndarray,
    speed: float = 1.5,
    average_turns_per_unit_distance: float = 0.1,
    turn_delay: float = 2.0
) -> np.ndarray:
    """
    Build a time matrix from a distance matrix.

    Converts distances to estimated travel times, accounting for AGV speed
    and estimated turn delays.

    Args:
        distance_matrix: NxN distance matrix in meters
        speed: AGV speed in meters/second
        average_turns_per_unit_distance: Expected turns per meter of travel
        turn_delay: Time delay per turn in seconds

    Returns:
        NxN numpy array of travel times in seconds

    Example:
        >>> time_matrix = build_time_matrix(distance_matrix, speed=1.5)
    """
    n = distance_matrix.shape[0]
    time_matrix = np.zeros((n, n), dtype=np.float32)

    for i in range(n):
        for j in range(n):
            if i == j:
                time_matrix[i, j] = 0.0
            else:
                distance = distance_matrix[i, j]
                estimated_turns = int(distance * average_turns_per_unit_distance)
                time = calculate_travel_time(distance, speed, estimated_turns, turn_delay)
                time_matrix[i, j] = time

    return time_matrix


def get_closest_nodes(
    target_x: float,
    target_y: float,
    nodes: Dict[int, NavigationNode],
    k: int = 5
) -> List[Tuple[int, float]]:
    """
    Find the k closest nodes to a target position.

    Useful for finding nearby navigation nodes when placing new elements
    (charging stations, task locations, etc.) in the warehouse.

    Args:
        target_x: X-coordinate of target position
        target_y: Y-coordinate of target position
        nodes: Dictionary of node_id -> NavigationNode
        k: Number of closest nodes to return

    Returns:
        List of tuples (node_id, distance) sorted by distance

    Example:
        >>> closest = get_closest_nodes(25.0, 15.0, nodes, k=3)
        >>> for node_id, distance in closest:
        ...     print(f"Node {node_id}: {distance:.2f}m away")
    """
    distances = []

    for node_id, node in nodes.items():
        distance = np.sqrt((node.x - target_x) ** 2 + (node.y - target_y) ** 2)
        distances.append((node_id, distance))

    # Sort by distance and return top k
    distances.sort(key=lambda x: x[1])
    return distances[:k]


def calculate_centroid(nodes: List[NavigationNode]) -> Tuple[float, float]:
    """
    Calculate the geometric centroid of a set of nodes.

    Args:
        nodes: List of NavigationNode objects

    Returns:
        Tuple of (x, y) coordinates of the centroid

    Example:
        >>> nodes = [NavigationNode(1, 0, 0), NavigationNode(2, 10, 10)]
        >>> cx, cy = calculate_centroid(nodes)
        >>> print(f"Centroid: ({cx}, {cy})")  # Output: (5.0, 5.0)
    """
    if not nodes:
        return 0.0, 0.0

    x_coords = [node.x for node in nodes]
    y_coords = [node.y for node in nodes]

    centroid_x = np.mean(x_coords)
    centroid_y = np.mean(y_coords)

    return centroid_x, centroid_y
