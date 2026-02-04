"""
JSON Export Utilities

Provides functions to export warehouse data, navigation graphs,
and distance matrices to JSON format for integration with other systems.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from ..models.warehouse import (
        RoboticWarehouse,
        LegacyWarehouse,
        Node,
        Edge,
        NodeType,
        ZoneType,
    )
except ImportError:
    # Fallback for different import structures
    from models.warehouse import (
        RoboticWarehouse,
        LegacyWarehouse,
        Node,
        Edge,
        NodeType,
        ZoneType,
    )


def export_warehouse_json(
    warehouse: RoboticWarehouse,
    include_metadata: bool = True,
    pretty: bool = True
) -> str:
    """
    Export complete warehouse configuration to JSON.

    Args:
        warehouse: RoboticWarehouse instance to export
        include_metadata: Whether to include metadata and timestamps
        pretty: Whether to format JSON with indentation

    Returns:
        JSON string representation of the warehouse

    Example:
        >>> json_str = export_warehouse_json(warehouse)
        >>> with open('warehouse.json', 'w') as f:
        ...     f.write(json_str)
    """
    data = {
        'warehouse': {
            'name': warehouse.name,
            'dimensions': {
                'width_m': warehouse.width,
                'length_m': warehouse.length,
                'total_area_m2': warehouse.total_area,
            },
            'legacy_config': {
                'aisles': warehouse.aisles,
                'aisle_width': warehouse.aisle_width,
                'aisle_length': warehouse.aisle_length,
                'storage_area_m2': warehouse.storage_area,
            },
        },
        'zones': [_zone_to_dict(zone) for zone in warehouse.zones],
        'nodes': [_node_to_dict(node) for node in warehouse.nodes],
        'edges': [_edge_to_dict(edge) for edge in warehouse.edges],
        'charging_stations': [_node_to_dict(station) for station in warehouse.charging_stations],
        'navigation_graph': warehouse.navigation_graph,
        'distance_matrix': warehouse.distance_matrix,
        'traffic_rules': [_traffic_rule_to_dict(rule) for rule in warehouse.traffic_rules],
        'statistics': {
            'total_nodes': warehouse.num_nodes,
            'total_edges': warehouse.num_edges,
            'nodes_by_type': _count_nodes_by_type(warehouse.nodes),
            'zones_by_type': _count_zones_by_type(warehouse.zones),
        },
    }

    if include_metadata:
        data['metadata'] = {
            'export_timestamp': datetime.now().isoformat(),
            'format_version': '1.0',
            'exporter': 'retrofit_framework.output.json_exporter',
        }

    indent = 2 if pretty else None
    return json.dumps(data, indent=indent, ensure_ascii=False)


def export_navigation_graph(
    nodes: List[Node],
    edges: List[Edge],
    include_positions: bool = True
) -> str:
    """
    Export navigation graph (nodes and edges) to JSON.

    Args:
        nodes: List of Node instances
        edges: List of Edge instances
        include_positions: Whether to include node position data

    Returns:
        JSON string representation of the navigation graph

    Example:
        >>> graph_json = export_navigation_graph(warehouse.nodes, warehouse.edges)
        >>> print(graph_json)
    """
    graph_data = {
        'nodes': [],
        'edges': [],
        'statistics': {
            'node_count': len(nodes),
            'edge_count': len(edges),
        },
    }

    # Export nodes
    for node in nodes:
        node_data = {
            'id': node.id,
            'node_type': node.node_type.value,
            'zone_type': node.zone_type.value,
        }
        if include_positions:
            node_data['position'] = {
                'x': node.x,
                'y': node.y,
            }
        graph_data['nodes'].append(node_data)

    # Export edges
    for edge in edges:
        edge_data = {
            'id': edge.id,
            'from_node': edge.from_node,
            'to_node': edge.to_node,
            'distance': edge.distance,
            'bidirectional': edge.bidirectional,
        }
        graph_data['edges'].append(edge_data)

    # Build adjacency list
    adjacency = {}
    for edge in edges:
        if edge.from_node not in adjacency:
            adjacency[edge.from_node] = []
        adjacency[edge.from_node].append(edge.to_node)

        if edge.bidirectional:
            if edge.to_node not in adjacency:
                adjacency[edge.to_node] = []
            adjacency[edge.to_node].append(edge.from_node)

    graph_data['adjacency_list'] = adjacency

    return json.dumps(graph_data, indent=2, ensure_ascii=False)


def export_distance_matrix(
    matrix: Dict[str, Dict[str, float]],
    node_ids: Optional[List[str]] = None,
    format_type: str = 'nested'
) -> str:
    """
    Export distance matrix to JSON.

    Args:
        matrix: Distance matrix as nested dict {from_node: {to_node: distance}}
        node_ids: Optional list of node IDs to include (default: all)
        format_type: 'nested' for dict of dicts, 'flat' for list of entries

    Returns:
        JSON string representation of the distance matrix

    Example:
        >>> matrix_json = export_distance_matrix(warehouse.distance_matrix)
        >>> print(matrix_json)
    """
    if format_type == 'nested':
        # Export as nested dictionary
        if node_ids:
            filtered_matrix = {
                from_node: {
                    to_node: dist
                    for to_node, dist in destinations.items()
                    if to_node in node_ids
                }
                for from_node, destinations in matrix.items()
                if from_node in node_ids
            }
        else:
            filtered_matrix = matrix

        data = {
            'distance_matrix': filtered_matrix,
            'format': 'nested_dict',
            'units': 'meters',
        }

    elif format_type == 'flat':
        # Export as flat list of {from, to, distance} entries
        entries = []
        for from_node, destinations in matrix.items():
            if node_ids and from_node not in node_ids:
                continue
            for to_node, distance in destinations.items():
                if node_ids and to_node not in node_ids:
                    continue
                entries.append({
                    'from': from_node,
                    'to': to_node,
                    'distance': distance,
                })

        data = {
            'distances': entries,
            'format': 'flat_list',
            'units': 'meters',
        }

    else:
        raise ValueError(f"Unknown format_type: {format_type}. Use 'nested' or 'flat'")

    # Add statistics
    if format_type == 'nested':
        all_distances = [
            dist
            for destinations in data['distance_matrix'].values()
            for dist in destinations.values()
            if dist > 0
        ]
    else:
        all_distances = [e['distance'] for e in data['distances'] if e['distance'] > 0]

    if all_distances:
        data['statistics'] = {
            'total_connections': len(all_distances),
            'min_distance': min(all_distances),
            'max_distance': max(all_distances),
            'avg_distance': sum(all_distances) / len(all_distances),
        }

    return json.dumps(data, indent=2, ensure_ascii=False)


def save_warehouse_json(
    warehouse: RoboticWarehouse,
    filepath: str,
    include_metadata: bool = True
) -> None:
    """
    Save warehouse configuration to a JSON file.

    Args:
        warehouse: RoboticWarehouse instance
        filepath: Path to output JSON file
        include_metadata: Whether to include metadata

    Example:
        >>> save_warehouse_json(warehouse, '/path/to/warehouse.json')
    """
    json_str = export_warehouse_json(warehouse, include_metadata, pretty=True)
    Path(filepath).write_text(json_str, encoding='utf-8')


def load_warehouse_json(filepath: str) -> Dict[str, Any]:
    """
    Load warehouse configuration from a JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Dictionary containing warehouse data

    Example:
        >>> data = load_warehouse_json('/path/to/warehouse.json')
        >>> print(data['warehouse']['name'])
    """
    return json.loads(Path(filepath).read_text(encoding='utf-8'))


def export_legacy_warehouse_json(warehouse: LegacyWarehouse, pretty: bool = True) -> str:
    """
    Export legacy warehouse configuration to JSON.

    Args:
        warehouse: LegacyWarehouse instance
        pretty: Whether to format JSON with indentation

    Returns:
        JSON string representation
    """
    data = {
        'warehouse': {
            'name': warehouse.name,
            'type': 'legacy',
            'dimensions': {
                'width_m': warehouse.width,
                'length_m': warehouse.length,
                'total_area_m2': warehouse.total_area,
            },
            'configuration': {
                'aisles': warehouse.aisles,
                'aisle_width': warehouse.aisle_width,
                'aisle_length': warehouse.aisle_length,
                'storage_area_m2': warehouse.storage_area,
            },
        },
        'zones': [_zone_to_dict(zone) for zone in warehouse.zones],
        'nodes': [_node_to_dict(node) for node in warehouse.nodes],
        'edges': [_edge_to_dict(edge) for edge in warehouse.edges],
    }

    indent = 2 if pretty else None
    return json.dumps(data, indent=indent, ensure_ascii=False)


# Helper functions

def _node_to_dict(node: Node) -> Dict[str, Any]:
    """Convert Node to dictionary."""
    return {
        'id': node.id,
        'x': node.x,
        'y': node.y,
        'zone_type': node.zone_type.value,
        'node_type': node.node_type.value,
    }


def _edge_to_dict(edge: Edge) -> Dict[str, Any]:
    """Convert Edge to dictionary."""
    return {
        'id': edge.id,
        'from_node': edge.from_node,
        'to_node': edge.to_node,
        'distance': edge.distance,
        'bidirectional': edge.bidirectional,
    }


def _zone_to_dict(zone) -> Dict[str, Any]:
    """Convert Zone to dictionary."""
    return {
        'id': zone.id,
        'name': zone.name,
        'x': zone.x,
        'y': zone.y,
        'width': zone.width,
        'height': zone.height,
        'zone_type': zone.zone_type.value,
    }


def _traffic_rule_to_dict(rule) -> Dict[str, Any]:
    """Convert TrafficRule to dictionary."""
    data = {
        'rule_id': rule.rule_id,
        'rule_type': rule.rule_type,
        'applies_to': rule.applies_to,
    }
    if rule.description:
        data['description'] = rule.description
    return data


def _count_nodes_by_type(nodes: List[Node]) -> Dict[str, int]:
    """Count nodes by type."""
    counts = {}
    for node in nodes:
        node_type = node.node_type.value
        counts[node_type] = counts.get(node_type, 0) + 1
    return counts


def _count_zones_by_type(zones: List) -> Dict[str, int]:
    """Count zones by type."""
    counts = {}
    for zone in zones:
        zone_type = zone.zone_type.value
        counts[zone_type] = counts.get(zone_type, 0) + 1
    return counts
