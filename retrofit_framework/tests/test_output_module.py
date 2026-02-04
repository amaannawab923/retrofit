"""
Tests for the output module

Basic tests to verify the output module functions work correctly.
"""

import pytest
from models.warehouse import (
    Node,
    Edge,
    Zone,
    NodeType,
    ZoneType,
    LegacyWarehouse,
    RoboticWarehouse,
)
from output.visualizer import (
    generate_ascii_layout,
    generate_node_map,
    format_distance_matrix,
    generate_simple_layout,
)
from output.report_generator import (
    generate_conversion_report,
    generate_summary_stats,
    compare_layouts,
)
from output.json_exporter import (
    export_warehouse_json,
    export_navigation_graph,
    export_distance_matrix,
)


@pytest.fixture
def sample_nodes():
    """Create sample nodes for testing."""
    return [
        Node(
            id="N01",
            x=0.0,
            y=0.0,
            zone_type=ZoneType.CROSSOVER,
            node_type=NodeType.INTERSECTION,
        ),
        Node(
            id="P01",
            x=5.0,
            y=5.0,
            zone_type=ZoneType.PICKUP,
            node_type=NodeType.PICKUP,
        ),
        Node(
            id="CHG1",
            x=10.0,
            y=10.0,
            zone_type=ZoneType.CHARGING,
            node_type=NodeType.CHARGING,
        ),
    ]


@pytest.fixture
def sample_edges():
    """Create sample edges for testing."""
    return [
        Edge(id="E01", from_node="N01", to_node="P01", distance=7.07, bidirectional=True),
        Edge(id="E02", from_node="P01", to_node="CHG1", distance=7.07, bidirectional=True),
    ]


@pytest.fixture
def sample_legacy_warehouse():
    """Create a sample legacy warehouse."""
    return LegacyWarehouse(
        name="Test Legacy",
        width=20.0,
        length=30.0,
        aisles=3,
        aisle_width=1.5,
        aisle_length=25.0,
    )


@pytest.fixture
def sample_robotic_warehouse(sample_nodes, sample_edges):
    """Create a sample robotic warehouse."""
    charging_node = sample_nodes[2]  # CHG1

    warehouse = RoboticWarehouse(
        name="Test Robotic",
        width=20.0,
        length=30.0,
        aisles=3,
        aisle_width=1.5,
        aisle_length=25.0,
        nodes=sample_nodes,
        edges=sample_edges,
        charging_stations=[charging_node],
        distance_matrix={
            "N01": {"P01": 7.07},
            "P01": {"N01": 7.07, "CHG1": 7.07},
            "CHG1": {"P01": 7.07},
        },
    )

    return warehouse


class TestVisualizer:
    """Test visualizer functions."""

    def test_generate_ascii_layout(self, sample_robotic_warehouse):
        """Test ASCII layout generation."""
        result = generate_ascii_layout(sample_robotic_warehouse)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Width:" in result
        assert "Nodes:" in result

    def test_generate_node_map(self, sample_nodes):
        """Test node map generation."""
        result = generate_node_map(sample_nodes)
        assert isinstance(result, str)
        assert "NODE MAP" in result
        assert "N01" in result
        assert "P01" in result
        assert "CHG1" in result

    def test_generate_simple_layout(self, sample_robotic_warehouse):
        """Test simple layout generation."""
        result = generate_simple_layout(sample_robotic_warehouse)
        assert isinstance(result, str)
        assert "Test Robotic" in result
        assert "Dimensions:" in result

    def test_format_distance_matrix(self):
        """Test distance matrix formatting."""
        matrix = {
            "N01": {"N02": 10.0, "N03": 15.0},
            "N02": {"N01": 10.0, "N03": 12.0},
            "N03": {"N01": 15.0, "N02": 12.0},
        }
        result = format_distance_matrix(matrix)
        assert isinstance(result, str)
        assert "DISTANCE MATRIX" in result
        assert "N01" in result


class TestReportGenerator:
    """Test report generator functions."""

    def test_generate_conversion_report(
        self, sample_legacy_warehouse, sample_robotic_warehouse
    ):
        """Test conversion report generation."""
        result = generate_conversion_report(
            sample_legacy_warehouse, sample_robotic_warehouse
        )
        assert isinstance(result, str)
        assert "WAREHOUSE RETROFIT CONVERSION REPORT" in result
        assert "LEGACY WAREHOUSE CONFIGURATION" in result
        assert "ROBOTIC WAREHOUSE CONFIGURATION" in result

    def test_generate_summary_stats(self, sample_robotic_warehouse):
        """Test summary statistics generation."""
        result = generate_summary_stats(sample_robotic_warehouse)
        assert isinstance(result, dict)
        assert "warehouse_name" in result
        assert result["warehouse_name"] == "Test Robotic"
        assert result["total_nodes"] == 3
        assert result["total_edges"] == 2

    def test_compare_layouts(
        self, sample_legacy_warehouse, sample_robotic_warehouse
    ):
        """Test layout comparison."""
        result = compare_layouts(sample_legacy_warehouse, sample_robotic_warehouse)
        assert isinstance(result, str)
        assert "LAYOUT COMPARISON" in result
        assert "Legacy" in result
        assert "Robotic" in result


class TestJSONExporter:
    """Test JSON exporter functions."""

    def test_export_warehouse_json(self, sample_robotic_warehouse):
        """Test warehouse JSON export."""
        result = export_warehouse_json(sample_robotic_warehouse)
        assert isinstance(result, str)
        assert "warehouse" in result
        assert "nodes" in result
        assert "edges" in result

    def test_export_navigation_graph(self, sample_nodes, sample_edges):
        """Test navigation graph export."""
        result = export_navigation_graph(sample_nodes, sample_edges)
        assert isinstance(result, str)
        assert "nodes" in result
        assert "edges" in result
        assert "adjacency_list" in result

    def test_export_distance_matrix_nested(self):
        """Test distance matrix export in nested format."""
        matrix = {
            "N01": {"N02": 10.0},
            "N02": {"N01": 10.0},
        }
        result = export_distance_matrix(matrix, format_type='nested')
        assert isinstance(result, str)
        assert "distance_matrix" in result
        assert "nested_dict" in result

    def test_export_distance_matrix_flat(self):
        """Test distance matrix export in flat format."""
        matrix = {
            "N01": {"N02": 10.0},
            "N02": {"N01": 10.0},
        }
        result = export_distance_matrix(matrix, format_type='flat')
        assert isinstance(result, str)
        assert "distances" in result
        assert "flat_list" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
