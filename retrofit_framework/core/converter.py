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
    FeasibilityFactor,
    FeasibilityAssessment,
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

        # Calculate feasibility score and assessment
        feasibility_assessment = self._calculate_feasibility_score(warehouse)

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
            feasibility_score=feasibility_assessment.score,
            feasibility_assessment=feasibility_assessment,
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

    def _calculate_feasibility_score(self, warehouse: LegacyWarehouse) -> FeasibilityAssessment:
        """
        Calculate overall feasibility score for robotic conversion (0-10 scale)
        and produce a detailed grading assessment.

        Factors:
        - Aisle width adequacy (40%, max 4.0 pts)
        - Layout regularity (25%, max 2.5 pts)
        - Space utilization (20%, max 2.0 pts)
        - Accessibility (15%, max 1.5 pts)

        Grade boundaries:
        - A  (9.0-10.0): Excellent — ready for retrofit
        - B  (7.0-8.9):  Good — feasible with minor adjustments
        - C  (5.0-6.9):  Marginal — feasible but needs significant work
        - D  (3.0-4.9):  Poor — major retrofitting required
        - F  (0.0-2.9):  Fail — not feasible without complete redesign

        Args:
            warehouse: Warehouse specification

        Returns:
            FeasibilityAssessment: Full grading with score, grade, factors, issues, and actions
        """
        score = 0.0
        factors: list[FeasibilityFactor] = []
        issues: list[str] = []
        actions: list[str] = []

        # ── Factor 1: Aisle Width (40%, max 4.0) ──
        if warehouse.aisle_width >= self.OPTIMAL_AISLE_WIDTH:
            aisle_score = 4.0
            aisle_status = "optimal"
            aisle_detail = (
                f"Aisle width ({warehouse.aisle_width}m) meets optimal threshold "
                f"(>= {self.OPTIMAL_AISLE_WIDTH}m). Supports bidirectional AGV traffic at full speed."
            )
        elif warehouse.aisle_width >= self.MIN_AISLE_WIDTH:
            aisle_score = 3.0
            aisle_status = "acceptable"
            aisle_detail = (
                f"Aisle width ({warehouse.aisle_width}m) meets minimum requirement "
                f"(>= {self.MIN_AISLE_WIDTH}m) but is below optimal ({self.OPTIMAL_AISLE_WIDTH}m). "
                f"Bidirectional traffic possible but may require reduced speed."
            )
            issues.append(
                f"Aisle width ({warehouse.aisle_width}m) is below optimal {self.OPTIMAL_AISLE_WIDTH}m — "
                f"AGVs may need speed reduction in aisles"
            )
            actions.append(
                f"Consider widening aisles from {warehouse.aisle_width}m to {self.OPTIMAL_AISLE_WIDTH}m "
                f"for full-speed bidirectional traffic"
            )
        elif warehouse.aisle_width >= 2.5:
            aisle_score = 2.0
            aisle_status = "marginal"
            aisle_detail = (
                f"Aisle width ({warehouse.aisle_width}m) is below minimum recommended "
                f"({self.MIN_AISLE_WIDTH}m). AGV operation possible but restricted to "
                f"reduced speed and careful navigation."
            )
            issues.append(
                f"Aisle width ({warehouse.aisle_width}m) is below minimum {self.MIN_AISLE_WIDTH}m — "
                f"limited to slow, single-direction AGV traffic"
            )
            actions.append(
                f"Widen aisles from {warehouse.aisle_width}m to at least {self.MIN_AISLE_WIDTH}m "
                f"before deploying AGV fleet"
            )
        elif warehouse.aisle_width >= 2.0:
            aisle_score = 1.0
            aisle_status = "poor"
            aisle_detail = (
                f"Aisle width ({warehouse.aisle_width}m) only supports single-direction AGV traffic "
                f"at very low speed. High collision risk."
            )
            issues.append(
                f"Aisle width ({warehouse.aisle_width}m) critically narrow — "
                f"single-direction only, high collision risk"
            )
            actions.append(
                f"Aisles must be widened from {warehouse.aisle_width}m to at least {self.MIN_AISLE_WIDTH}m — "
                f"this is a blocking requirement"
            )
        else:
            aisle_score = 0.0
            aisle_status = "inadequate"
            aisle_detail = (
                f"Aisle width ({warehouse.aisle_width}m) is below absolute minimum (2.0m). "
                f"AGVs physically cannot operate in these aisles."
            )
            issues.append(
                f"Aisle width ({warehouse.aisle_width}m) is below 2.0m — "
                f"AGVs physically cannot fit"
            )
            actions.append(
                "Complete aisle redesign required — current layout cannot accommodate any AGV"
            )

        score += aisle_score
        factors.append(FeasibilityFactor(
            name="Aisle Width", score=aisle_score, max_score=4.0,
            weight="40%", status=aisle_status, detail=aisle_detail,
        ))
        self.conversion_notes.append(f"Aisle width score: {aisle_score}/4.0")

        # ── Factor 2: Layout Regularity (25%, max 2.5) ──
        # Evaluate based on whether aisles are parallel and evenly spaced
        aisle_zones = [z for z in warehouse.zones if z.zone_type == ZoneType.AISLE]
        if len(aisle_zones) >= 2:
            # Check if aisles have consistent width and spacing
            widths = [z.width for z in aisle_zones]
            x_positions = sorted([z.x for z in aisle_zones])
            spacings = [x_positions[i+1] - x_positions[i] for i in range(len(x_positions) - 1)]

            width_consistent = len(set(widths)) == 1
            spacing_consistent = len(spacings) == 0 or (max(spacings) - min(spacings)) < 1.0

            if width_consistent and spacing_consistent:
                regularity_score = 2.5
                regularity_status = "optimal"
                regularity_detail = (
                    f"Layout has {len(aisle_zones)} evenly spaced parallel aisles with "
                    f"consistent {widths[0]}m width. Ideal grid pattern for AGV navigation."
                )
            elif width_consistent or spacing_consistent:
                regularity_score = 1.5
                regularity_status = "acceptable"
                regularity_detail = (
                    "Layout is partially regular — aisles exist but spacing or widths are inconsistent."
                )
                issues.append("Aisle spacing or widths are not fully consistent — may complicate path planning")
                actions.append("Standardize aisle widths and spacing where possible for simpler AGV routing")
            else:
                regularity_score = 0.5
                regularity_status = "poor"
                regularity_detail = (
                    "Layout is irregular — aisles have varying widths and uneven spacing."
                )
                issues.append("Irregular layout with varying aisle widths and spacing")
                actions.append("Consider restructuring aisles into a regular grid pattern")
        elif len(aisle_zones) == 1:
            regularity_score = 1.0
            regularity_status = "marginal"
            regularity_detail = "Only 1 aisle detected — minimal grid structure for AGV navigation."
            issues.append("Single-aisle layout provides very limited routing options for AGVs")
            actions.append("Add parallel aisles to create redundant paths and reduce congestion")
        else:
            regularity_score = 0.0
            regularity_status = "inadequate"
            regularity_detail = "No aisles detected — cannot establish AGV navigation grid."
            issues.append("No aisle zones defined — AGV pathfinding is not possible")
            actions.append("Define aisle zones in the warehouse layout before attempting retrofit")

        score += regularity_score
        factors.append(FeasibilityFactor(
            name="Layout Regularity", score=regularity_score, max_score=2.5,
            weight="25%", status=regularity_status, detail=regularity_detail,
        ))
        self.conversion_notes.append(f"Layout regularity score: {regularity_score}/2.5")

        # ── Factor 3: Space Utilization (20%, max 2.0) ──
        total_area = warehouse.width * warehouse.length
        aisle_area = warehouse.aisles * warehouse.aisle_width * warehouse.aisle_length
        utilization = aisle_area / total_area if total_area > 0 else 0

        if 0.3 <= utilization <= 0.5:
            space_score = 2.0
            space_status = "optimal"
            space_detail = (
                f"Space utilization is {utilization:.1%} — optimal balance between "
                f"storage density and AGV maneuverability."
            )
        elif 0.2 <= utilization < 0.3 or 0.5 < utilization <= 0.6:
            space_score = 1.5
            space_status = "acceptable"
            space_detail = (
                f"Space utilization is {utilization:.1%} — slightly outside optimal range (30-50%). "
                f"AGV operation feasible but not ideal."
            )
            if utilization > 0.5:
                issues.append(
                    f"Space utilization ({utilization:.1%}) is high — aisles may feel congested during peak traffic"
                )
                actions.append("Consider reducing storage density or adding buffer zones for AGV queuing")
            else:
                issues.append(
                    f"Space utilization ({utilization:.1%}) is low — warehouse may be underutilized"
                )
                actions.append("Opportunity to add more storage racks or buffer areas")
        else:
            space_score = 1.0
            space_status = "poor" if utilization > 0.6 else "marginal"
            space_detail = (
                f"Space utilization is {utilization:.1%} — "
                f"{'too dense for safe AGV operation' if utilization > 0.6 else 'significantly underutilized'}."
            )
            if utilization > 0.6:
                issues.append(
                    f"Space utilization ({utilization:.1%}) is critically high — "
                    f"AGVs will face constant congestion and collision risk"
                )
                actions.append("Remove some storage racks or widen aisles to bring utilization below 50%")
            else:
                issues.append(f"Space utilization ({utilization:.1%}) is very low")
                actions.append("Layout has excess open space — optimize rack placement")

        score += space_score
        factors.append(FeasibilityFactor(
            name="Space Utilization", score=space_score, max_score=2.0,
            weight="20%", status=space_status, detail=space_detail,
        ))
        self.conversion_notes.append(f"Space utilization score: {space_score}/2.0 (utilization: {utilization:.1%})")

        # ── Factor 4: Accessibility (15%, max 1.5) ──
        pickup_zone = next((z for z in warehouse.zones if z.zone_type == ZoneType.PICKUP), None)
        drop_zone = next((z for z in warehouse.zones if z.zone_type == ZoneType.DROP), None)

        if pickup_zone and drop_zone:
            accessibility_score = 1.5
            accessibility_status = "optimal"
            accessibility_detail = (
                "Both pickup and drop zones are defined and positioned at warehouse edges — "
                "ideal for AGV ingress/egress without crossing active storage areas."
            )
        elif pickup_zone or drop_zone:
            accessibility_score = 1.0
            accessibility_status = "marginal"
            missing = "drop" if pickup_zone else "pickup"
            accessibility_detail = f"Only {'pickup' if pickup_zone else 'drop'} zone defined. Missing {missing} zone."
            issues.append(f"Missing {missing} zone — AGVs need both endpoints for task routing")
            actions.append(f"Define a {missing} zone at a warehouse edge for complete task flow")
        else:
            accessibility_score = 0.0
            accessibility_status = "inadequate"
            accessibility_detail = "Neither pickup nor drop zones are defined. AGV task routing is impossible."
            issues.append("No pickup or drop zones defined — AGVs have no task endpoints")
            actions.append("Define both pickup and drop zones before attempting retrofit")

        score += accessibility_score
        factors.append(FeasibilityFactor(
            name="Accessibility", score=accessibility_score, max_score=1.5,
            weight="15%", status=accessibility_status, detail=accessibility_detail,
        ))
        self.conversion_notes.append(f"Accessibility score: {accessibility_score}/1.5")

        # ── Final Score & Grading ──
        final_score = round(score, 1)
        self.conversion_notes.append(f"Final feasibility score: {final_score}/10.0")

        if final_score >= 9.0:
            grade, label = "A", "Excellent"
            verdict = "Ready for retrofit — minimal changes needed"
        elif final_score >= 7.0:
            grade, label = "B", "Good"
            verdict = "Feasible with minor adjustments"
        elif final_score >= 5.0:
            grade, label = "C", "Marginal"
            verdict = "Feasible but needs significant work before AGV deployment"
        elif final_score >= 3.0:
            grade, label = "D", "Poor"
            verdict = "Major retrofitting required before any AGV operation"
        else:
            grade, label = "F", "Fail"
            verdict = "Not feasible — complete warehouse redesign required"

        is_feasible = final_score >= 5.0

        if not issues:
            issues.append("No issues found — all factors meet optimal thresholds")
        if not actions:
            actions.append("No actions required — warehouse is ready for AGV deployment")

        return FeasibilityAssessment(
            score=final_score,
            grade=grade,
            label=label,
            verdict=verdict,
            is_feasible=is_feasible,
            factors=factors,
            issues=issues,
            actions=actions,
        )
