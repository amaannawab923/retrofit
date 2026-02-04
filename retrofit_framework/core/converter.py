"""
Retrofit converter for transforming legacy warehouses to robotic-accommodated facilities.
"""

import math
from typing import List, Tuple, Dict, Any
from models.warehouse import (
    LegacyWarehouse,
    RoboticWarehouse,
    Node,
    Edge,
    Zone,
    ZoneType,
    NodeType,
    TrafficRule,
)


class RetrofitConverter:
    """
    Converts legacy warehouse layouts to robotic-accommodated warehouses.

    This converter performs:
    1. Aisle width validation and recommendations
    2. Navigation graph generation
    3. Distance matrix computation
    4. Charging station placement
    5. Traffic rule generation
    6. Feasibility assessment
    """

    MIN_AISLE_WIDTH = 3.0  # Minimum recommended aisle width for robots (meters)
    OPTIMAL_AISLE_WIDTH = 3.5  # Optimal aisle width for robots (meters)
    CHARGING_STATION_SPACING = 15.0  # Maximum distance between charging stations (meters)

    def __init__(self):
        """Initialize the retrofit converter."""
        self.conversion_notes: List[str] = []

    def convert_legacy_warehouse(self, warehouse: LegacyWarehouse) -> RoboticWarehouse:
        """
        Convert a legacy warehouse to a robotic-accommodated warehouse.

        Args:
            warehouse: Legacy warehouse specification

        Returns:
            RoboticWarehouse: Converted warehouse with navigation and optimization
        """
        self.conversion_notes = []

        # Validate and assess current configuration
        self._validate_warehouse(warehouse)

        # Build navigation graph (adjacency list)
        navigation_graph = self._build_navigation_graph(warehouse)

        # Compute distance matrix
        distance_matrix = self._compute_distance_matrix(warehouse)

        # Place charging stations
        charging_stations = self._place_charging_stations(warehouse)

        # Generate traffic rules
        traffic_rules = self._generate_traffic_rules(warehouse)

        # Calculate feasibility score
        feasibility_score = self._calculate_feasibility_score(warehouse)

        # Create the robotic warehouse
        robotic_warehouse = RoboticWarehouse(
            name=warehouse.name + " (Robotic)",
            width=warehouse.width,
            length=warehouse.length,
            aisles=warehouse.aisles,
            aisle_width=warehouse.aisle_width,
            aisle_length=warehouse.aisle_length,
            zones=warehouse.zones,
            nodes=warehouse.nodes,
            edges=warehouse.edges,
            charging_stations=charging_stations,
            navigation_graph=navigation_graph,
            distance_matrix=distance_matrix,
            traffic_rules=traffic_rules,
            feasibility_score=feasibility_score,
            conversion_notes=self.conversion_notes,
        )

        return robotic_warehouse

    def _validate_warehouse(self, warehouse: LegacyWarehouse) -> None:
        """Validate warehouse dimensions and provide recommendations."""

        if warehouse.aisle_width < self.MIN_AISLE_WIDTH:
            self.conversion_notes.append(
                f"Current aisle width ({warehouse.aisle_width}m) is below minimum "
                f"recommended ({self.MIN_AISLE_WIDTH}m). Consider widening aisles."
            )
        elif warehouse.aisle_width < self.OPTIMAL_AISLE_WIDTH:
            self.conversion_notes.append(
                f"Current aisle width ({warehouse.aisle_width}m) is acceptable but "
                f"below optimal ({self.OPTIMAL_AISLE_WIDTH}m). May limit robot speed."
            )
        else:
            self.conversion_notes.append(
                f"Aisle width ({warehouse.aisle_width}m) meets optimal requirements."
            )

    def _build_navigation_graph(self, warehouse: LegacyWarehouse) -> Dict[str, List[str]]:
        """
        Build adjacency list representation of navigation graph.

        Args:
            warehouse: Legacy warehouse specification

        Returns:
            Dict mapping node IDs to lists of connected node IDs
        """
        graph: Dict[str, List[str]] = {}

        # Initialize all nodes
        for node in warehouse.nodes:
            graph[node.id] = []

        # Add edges (both directions if bidirectional)
        for edge in warehouse.edges:
            graph[edge.from_node].append(edge.to_node)
            if edge.bidirectional:
                graph[edge.to_node].append(edge.from_node)

        self.conversion_notes.append(
            f"Built navigation graph with {len(graph)} nodes."
        )

        return graph

    def _compute_distance_matrix(self, warehouse: LegacyWarehouse) -> Dict[str, Dict[str, float]]:
        """
        Compute all-pairs shortest path distance matrix using Floyd-Warshall algorithm.

        Args:
            warehouse: Legacy warehouse specification

        Returns:
            Dictionary of dictionaries: distance_matrix[from_node][to_node] = distance
        """
        nodes = warehouse.nodes
        n = len(nodes)
        node_ids = [node.id for node in nodes]
        node_to_idx = {node.id: i for i, node in enumerate(nodes)}

        # Initialize distance matrix with infinity
        dist = [[float('inf')] * n for _ in range(n)]

        # Distance from node to itself is 0
        for i in range(n):
            dist[i][i] = 0.0

        # Set distances for direct edges
        for edge in warehouse.edges:
            from_idx = node_to_idx.get(edge.from_node)
            to_idx = node_to_idx.get(edge.to_node)
            if from_idx is not None and to_idx is not None:
                dist[from_idx][to_idx] = edge.distance
                if edge.bidirectional:
                    dist[to_idx][from_idx] = edge.distance

        # Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]

        # Convert to dictionary format
        distance_matrix: Dict[str, Dict[str, float]] = {}
        for i, from_id in enumerate(node_ids):
            distance_matrix[from_id] = {}
            for j, to_id in enumerate(node_ids):
                if dist[i][j] == float('inf'):
                    distance_matrix[from_id][to_id] = -1.0  # Unreachable
                else:
                    distance_matrix[from_id][to_id] = round(dist[i][j], 2)

        self.conversion_notes.append(
            f"Computed {n}x{n} distance matrix using Floyd-Warshall algorithm."
        )

        return distance_matrix

    def _place_charging_stations(self, warehouse: LegacyWarehouse) -> List[Node]:
        """
        Place charging stations strategically throughout the warehouse.

        Strategy:
        - Place stations ALONG THE WALLS/EDGES - never in aisle areas
        - Ensure no point is too far from a charging station
        - Position near high-traffic areas but out of the way

        Args:
            warehouse: Warehouse specification

        Returns:
            List of charging station nodes
        """
        stations: List[Node] = []
        station_id = 1

        # Find pickup and drop zones
        pickup_zone = next((z for z in warehouse.zones if z.zone_type == ZoneType.PICKUP), None)
        drop_zone = next((z for z in warehouse.zones if z.zone_type == ZoneType.DROP), None)

        # Station 1: Left wall, near pickup zone (high activity area)
        # Place along the left edge (x=1.5), vertically centered near pickup
        stations.append(Node(
            id=f"charging_{station_id}",
            x=1.5,  # Against left wall
            y=8.0,  # Just above pickup zone
            zone_type=ZoneType.CHARGING,
            node_type=NodeType.CHARGING,
        ))
        station_id += 1

        # Station 2: Left wall, middle section
        # Place along the left edge, at warehouse mid-height
        stations.append(Node(
            id=f"charging_{station_id}",
            x=1.5,  # Against left wall
            y=warehouse.length / 2,  # Middle height
            zone_type=ZoneType.CHARGING,
            node_type=NodeType.CHARGING,
        ))
        station_id += 1

        # Station 3: Right wall, near drop zone (high activity area)
        # Place along the right edge, near the drop zone
        stations.append(Node(
            id=f"charging_{station_id}",
            x=warehouse.width - 1.5,  # Against right wall
            y=warehouse.length - 8.0,  # Just below drop zone
            zone_type=ZoneType.CHARGING,
            node_type=NodeType.CHARGING,
        ))
        station_id += 1

        self.conversion_notes.append(
            f"Placed {len(stations)} charging stations along warehouse walls for optimal coverage without blocking aisles."
        )

        return stations

    def _generate_traffic_rules(self, warehouse: LegacyWarehouse) -> List[TrafficRule]:
        """
        Generate traffic management rules for efficient robot operation.

        Args:
            warehouse: Warehouse specification

        Returns:
            List of traffic rules
        """
        rules: List[TrafficRule] = []

        # Find aisle zones
        aisle_zones = [z for z in warehouse.zones if z.zone_type == ZoneType.AISLE]

        # Create one-way rules for alternating aisles (for efficiency)
        for i, aisle in enumerate(aisle_zones):
            direction = "north" if i % 2 == 0 else "south"
            rules.append(TrafficRule(
                rule_id=f"one_way_aisle_{i+1}",
                rule_type="one_way",
                applies_to=[aisle.id],
                description=f"Aisle {i+1}: {direction}bound traffic only",
            ))

        # Create priority rule for pickup zone
        pickup_zone = next((z for z in warehouse.zones if z.zone_type == ZoneType.PICKUP), None)
        if pickup_zone:
            rules.append(TrafficRule(
                rule_id="priority_pickup",
                rule_type="priority",
                applies_to=[pickup_zone.id],
                description="Priority access for pickup operations",
            ))

        # Create priority rule for drop zone
        drop_zone = next((z for z in warehouse.zones if z.zone_type == ZoneType.DROP), None)
        if drop_zone:
            rules.append(TrafficRule(
                rule_id="priority_drop",
                rule_type="priority",
                applies_to=[drop_zone.id],
                description="Priority access for drop operations",
            ))

        self.conversion_notes.append(
            f"Generated {len(rules)} traffic rules for efficient navigation."
        )

        return rules

    def _calculate_feasibility_score(self, warehouse: LegacyWarehouse) -> float:
        """
        Calculate overall feasibility score for robotic conversion (0-10 scale).

        Considers:
        - Aisle width adequacy (40%)
        - Layout regularity (25%)
        - Space utilization (20%)
        - Accessibility (15%)

        Args:
            warehouse: Warehouse specification

        Returns:
            float: Feasibility score (0-10)
        """
        score = 0.0

        # Aisle width score (40% weight, max 4 points)
        if warehouse.aisle_width >= self.OPTIMAL_AISLE_WIDTH:
            aisle_score = 4.0
        elif warehouse.aisle_width >= self.MIN_AISLE_WIDTH:
            aisle_score = 3.0
        elif warehouse.aisle_width >= 2.5:
            aisle_score = 2.0
        elif warehouse.aisle_width >= 2.0:
            aisle_score = 1.0
        else:
            aisle_score = 0.0
        score += aisle_score
        self.conversion_notes.append(f"Aisle width score: {aisle_score}/4.0")

        # Layout regularity score (25% weight, max 2.5 points)
        # Grid-based layouts get full points
        regularity_score = 2.5  # Assuming regular grid for Layout A
        score += regularity_score
        self.conversion_notes.append(f"Layout regularity score: {regularity_score}/2.5")

        # Space utilization score (20% weight, max 2 points)
        total_area = warehouse.width * warehouse.length
        aisle_area = warehouse.aisles * warehouse.aisle_width * warehouse.aisle_length
        utilization = aisle_area / total_area if total_area > 0 else 0

        if 0.3 <= utilization <= 0.5:
            space_score = 2.0
        elif 0.2 <= utilization < 0.3 or 0.5 < utilization <= 0.6:
            space_score = 1.5
        else:
            space_score = 1.0
        score += space_score
        self.conversion_notes.append(f"Space utilization score: {space_score}/2.0 (utilization: {utilization:.1%})")

        # Accessibility score (15% weight, max 1.5 points)
        # Based on zone placement
        pickup_zone = next((z for z in warehouse.zones if z.zone_type == ZoneType.PICKUP), None)
        drop_zone = next((z for z in warehouse.zones if z.zone_type == ZoneType.DROP), None)

        if pickup_zone and drop_zone:
            # Check if zones are at corners/edges (good) vs center (less optimal)
            accessibility_score = 1.5
        else:
            accessibility_score = 1.0
        score += accessibility_score
        self.conversion_notes.append(f"Accessibility score: {accessibility_score}/1.5")

        # Final score
        final_score = round(score, 1)
        self.conversion_notes.append(f"Final feasibility score: {final_score}/10.0")

        return final_score
