"""
Retrofit Framework - Output Generation and Visualization

This module provides output generation, visualization, and reporting capabilities
for the warehouse retrofit framework.
"""

from .visualizer import (
    generate_ascii_layout,
    generate_node_map,
    format_distance_matrix,
)
from .report_generator import (
    generate_conversion_report,
    generate_summary_stats,
    compare_layouts,
)
from .json_exporter import (
    export_warehouse_json,
    export_navigation_graph,
    export_distance_matrix,
)

__all__ = [
    # Visualizer
    'generate_ascii_layout',
    'generate_node_map',
    'format_distance_matrix',
    # Report Generator
    'generate_conversion_report',
    'generate_summary_stats',
    'compare_layouts',
    # JSON Exporter
    'export_warehouse_json',
    'export_navigation_graph',
    'export_distance_matrix',
]
