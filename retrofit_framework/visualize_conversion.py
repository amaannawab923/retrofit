"""
Visualization script for Layout A warehouse conversion.
Generates before/after PNG images showing the retrofit transformation.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import numpy as np
from pathlib import Path


def load_conversion_output(filepath: str) -> dict:
    """Load the conversion output JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def draw_warehouse_base(ax, width: float, height: float, title: str):
    """Draw the warehouse floor outline."""
    ax.set_xlim(-2, width + 2)
    ax.set_ylim(-2, height + 2)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel('X (meters)', fontsize=10)
    ax.set_ylabel('Y (meters)', fontsize=10)

    # Draw warehouse boundary
    warehouse = patches.Rectangle(
        (0, 0), width, height,
        linewidth=3, edgecolor='#2c3e50', facecolor='#ecf0f1',
        label='Warehouse Floor'
    )
    ax.add_patch(warehouse)

    # Add grid
    ax.grid(True, linestyle='--', alpha=0.3, color='gray')

    return ax


def draw_aisles(ax, rack_positions: list, aisle_width: float, aisle_height: float):
    """Draw the storage aisles/racks."""
    for i, pos in enumerate(rack_positions):
        rack = patches.Rectangle(
            (pos['x'] - aisle_width/2, pos['y']),
            aisle_width, aisle_height,
            linewidth=1.5, edgecolor='#8e44ad', facecolor='#d5a6e6',
            alpha=0.7, label='Storage Aisle' if i == 0 else None
        )
        ax.add_patch(rack)

        # Add aisle number
        ax.text(
            pos['x'], pos['y'] + aisle_height/2,
            f'A{i+1}', fontsize=8, ha='center', va='center',
            fontweight='bold', color='#4a235a'
        )


def draw_zones(ax, pickup_dock: dict, shipping_area: dict):
    """Draw pickup and drop zones."""
    # Pickup zone (loading dock)
    pickup = patches.Rectangle(
        (0, 0), 5, 5,
        linewidth=2, edgecolor='#27ae60', facecolor='#82e0aa',
        alpha=0.8, label='Pickup Zone'
    )
    ax.add_patch(pickup)
    ax.text(2.5, 2.5, 'PICKUP', fontsize=9, ha='center', va='center',
            fontweight='bold', color='#1e8449')

    # Drop zone (shipping area)
    drop = patches.Rectangle(
        (shipping_area['x'], shipping_area['y']),
        shipping_area['width'], shipping_area['height'],
        linewidth=2, edgecolor='#e74c3c', facecolor='#f5b7b1',
        alpha=0.8, label='Drop Zone'
    )
    ax.add_patch(drop)
    ax.text(
        shipping_area['x'] + shipping_area['width']/2,
        shipping_area['y'] + shipping_area['height']/2,
        'DROP', fontsize=9, ha='center', va='center',
        fontweight='bold', color='#922b21'
    )


def draw_navigation_nodes(ax, nodes: list):
    """Draw navigation graph nodes."""
    node_colors = {
        'pickup': '#27ae60',
        'drop': '#e74c3c',
        'aisle_entry': '#3498db',
        'waypoint': '#f39c12',
        'aisle_exit': '#9b59b6'
    }

    for node in nodes:
        color = node_colors.get(node['type'], '#95a5a6')
        size = 120 if node['type'] in ['pickup', 'drop'] else 80

        ax.scatter(
            node['x'], node['y'],
            s=size, c=color, edgecolors='white',
            linewidth=1.5, zorder=5,
            label=f"{node['type'].replace('_', ' ').title()}" if node == nodes[0] else None
        )

        # Add node label
        ax.annotate(
            node['id'].replace('node_', '').replace('aisle_', 'A'),
            (node['x'], node['y']),
            textcoords="offset points", xytext=(0, 8),
            ha='center', fontsize=6, color='#2c3e50'
        )


def draw_navigation_edges(ax, edges: list, nodes: list):
    """Draw navigation graph edges."""
    # Create node lookup
    node_lookup = {n['id']: (n['x'], n['y']) for n in nodes}

    for edge in edges:
        from_pos = node_lookup.get(edge['from'])
        to_pos = node_lookup.get(edge['to'])

        if from_pos and to_pos:
            # Draw edge line
            ax.plot(
                [from_pos[0], to_pos[0]],
                [from_pos[1], to_pos[1]],
                color='#3498db', linewidth=1.5, alpha=0.6,
                zorder=3
            )

            # Add distance label at midpoint
            mid_x = (from_pos[0] + to_pos[0]) / 2
            mid_y = (from_pos[1] + to_pos[1]) / 2

            # Only show distance for longer edges
            if edge['distance'] > 5:
                ax.text(
                    mid_x, mid_y,
                    f"{edge['distance']:.1f}m",
                    fontsize=5, ha='center', va='center',
                    color='#2980b9', alpha=0.8,
                    bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.7)
                )


def draw_charging_stations(ax, stations: list):
    """Draw charging station locations."""
    for i, station in enumerate(stations):
        # Draw charging station icon
        charging = patches.Circle(
            (station['x'], station['y']), 1.2,
            linewidth=2, edgecolor='#f39c12', facecolor='#fdebd0',
            zorder=6, label='Charging Station' if i == 0 else None
        )
        ax.add_patch(charging)

        # Add lightning bolt symbol
        ax.text(
            station['x'], station['y'],
            '⚡', fontsize=10, ha='center', va='center',
            zorder=7
        )


def draw_traffic_rules(ax, traffic_rules: dict, nodes: list):
    """Draw traffic rule indicators."""
    # Draw one-way aisle arrows
    one_way = traffic_rules.get('one_way_aisles', [])

    # Create node lookup
    node_lookup = {n['id']: (n['x'], n['y'], n['type']) for n in nodes}

    # Find aisle positions and draw direction arrows
    aisle_entries = [n for n in nodes if n['type'] == 'aisle_entry']
    aisle_exits = [n for n in nodes if n['type'] == 'aisle_exit']

    for i, (entry, exit_node) in enumerate(zip(aisle_entries, aisle_exits)):
        # Determine direction from traffic rules
        direction = "north" if i % 2 == 0 else "south"

        # Draw arrow alongside the aisle
        if direction == "north":
            ax.annotate(
                '', xy=(entry['x'] + 0.5, exit_node['y'] - 5),
                xytext=(entry['x'] + 0.5, entry['y'] + 5),
                arrowprops=dict(arrowstyle='->', color='#16a085', lw=2),
                zorder=4
            )
        else:
            ax.annotate(
                '', xy=(entry['x'] + 0.5, entry['y'] + 5),
                xytext=(entry['x'] + 0.5, exit_node['y'] - 5),
                arrowprops=dict(arrowstyle='->', color='#c0392b', lw=2),
                zorder=4
            )

    # Draw priority zones
    priority_zones = traffic_rules.get('priority_zones', [])
    for zone in priority_zones:
        priority_rect = patches.Rectangle(
            (zone['x'], zone['y']), zone['width'], zone['height'],
            linewidth=2, edgecolor='#e67e22', facecolor='none',
            linestyle='--', zorder=4
        )
        ax.add_patch(priority_rect)

    # Draw no-stopping zones
    no_stop_zones = traffic_rules.get('no_stopping_zones', [])
    for zone in no_stop_zones:
        no_stop = patches.Rectangle(
            (zone['x'], zone['y']), zone['width'], zone['height'],
            linewidth=1.5, edgecolor='#c0392b', facecolor='#fadbd8',
            alpha=0.5, linestyle=':', zorder=2
        )
        ax.add_patch(no_stop)


def create_before_image(data: dict, output_path: str):
    """Create the 'before conversion' warehouse image."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 16))

    original = data['original_warehouse']
    dims = original['warehouse_dimensions']

    # Draw base
    draw_warehouse_base(ax, dims['width'], dims['height'],
                       'Layout A - BEFORE Conversion\n(Legacy Warehouse)')

    # Draw aisles
    draw_aisles(ax, original['racks']['positions'],
                original['racks']['width'], original['racks']['height'])

    # Draw zones
    draw_zones(ax, original['loading_docks'][0], original['shipping_area'])

    # Add legend
    ax.legend(loc='upper left', fontsize=8, framealpha=0.9)

    # Add info box
    info_text = (
        f"Warehouse: 20m x 60m\n"
        f"Aisles: 5 (3m wide, 50m long)\n"
        f"Pickup Zone: 5m x 5m\n"
        f"Drop Zone: 5m x 5m\n"
        f"\n[No Navigation Graph]\n"
        f"[No Charging Stations]\n"
        f"[No Traffic Rules]"
    )
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
    ax.text(0.98, 0.02, info_text, transform=ax.transAxes, fontsize=8,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=props, family='monospace')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"✓ Saved: {output_path}")


def create_after_image(data: dict, output_path: str):
    """Create the 'after conversion' warehouse image."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 16))

    robotic = data['robotic_warehouse']
    dims = robotic['warehouse_dimensions']
    nav = data['navigation_graph']
    traffic = data['traffic_rules']
    summary = data['summary']

    # Draw base
    draw_warehouse_base(ax, dims['width'], dims['height'],
                       'Layout A - AFTER Conversion\n(Robotic-Accommodated Warehouse)')

    # Draw aisles
    draw_aisles(ax, robotic['racks']['positions'],
                robotic['racks']['width'], robotic['racks']['height'])

    # Draw zones
    draw_zones(ax, robotic['loading_docks'][0], robotic['shipping_area'])

    # Draw navigation edges (before nodes so nodes are on top)
    draw_navigation_edges(ax, nav['edges'], nav['nodes'])

    # Draw navigation nodes
    draw_navigation_nodes(ax, nav['nodes'])

    # Draw charging stations
    draw_charging_stations(ax, robotic['charging_stations'])

    # Draw traffic rules
    draw_traffic_rules(ax, traffic, nav['nodes'])

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(),
              loc='upper left', fontsize=7, framealpha=0.9, ncol=2)

    # Add info box
    info_text = (
        f"Warehouse: 20m x 60m\n"
        f"Aisles: 5 (3m wide, 50m long)\n"
        f"\n"
        f"Navigation Graph:\n"
        f"  • Nodes: {summary['total_nodes']}\n"
        f"  • Edges: {summary['total_edges']}\n"
        f"\n"
        f"Charging Stations: {summary['charging_stations_count']}\n"
        f"\n"
        f"Traffic Rules:\n"
        f"  • One-way aisles: 5\n"
        f"  • Priority zones: 2\n"
        f"  • No-stop zones: 2\n"
        f"\n"
        f"Feasibility Score: {summary['feasibility_score']}/10"
    )
    props = dict(boxstyle='round', facecolor='lightgreen', alpha=0.9)
    ax.text(0.98, 0.02, info_text, transform=ax.transAxes, fontsize=8,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=props, family='monospace')

    # Add traffic legend
    traffic_legend = (
        "Traffic Flow:\n"
        "→ Green: Northbound\n"
        "→ Red: Southbound"
    )
    ax.text(0.02, 0.98, traffic_legend, transform=ax.transAxes, fontsize=7,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"✓ Saved: {output_path}")


def create_comparison_image(data: dict, output_path: str):
    """Create a side-by-side comparison image."""
    fig, axes = plt.subplots(1, 2, figsize=(24, 16))

    original = data['original_warehouse']
    robotic = data['robotic_warehouse']
    nav = data['navigation_graph']
    traffic = data['traffic_rules']
    summary = data['summary']

    # === LEFT: Before ===
    ax1 = axes[0]
    dims = original['warehouse_dimensions']

    draw_warehouse_base(ax1, dims['width'], dims['height'],
                       'BEFORE: Legacy Warehouse')
    draw_aisles(ax1, original['racks']['positions'],
                original['racks']['width'], original['racks']['height'])
    draw_zones(ax1, original['loading_docks'][0], original['shipping_area'])

    # Add "LEGACY" watermark
    ax1.text(dims['width']/2, dims['height']/2, 'LEGACY',
             fontsize=40, ha='center', va='center',
             alpha=0.1, fontweight='bold', color='red', rotation=30)

    # === RIGHT: After ===
    ax2 = axes[1]
    dims = robotic['warehouse_dimensions']

    draw_warehouse_base(ax2, dims['width'], dims['height'],
                       'AFTER: Robotic Warehouse')
    draw_aisles(ax2, robotic['racks']['positions'],
                robotic['racks']['width'], robotic['racks']['height'])
    draw_zones(ax2, robotic['loading_docks'][0], robotic['shipping_area'])
    draw_navigation_edges(ax2, nav['edges'], nav['nodes'])
    draw_navigation_nodes(ax2, nav['nodes'])
    draw_charging_stations(ax2, robotic['charging_stations'])
    draw_traffic_rules(ax2, traffic, nav['nodes'])

    # Add "ROBOTIC" watermark
    ax2.text(dims['width']/2, dims['height']/2, 'ROBOTIC',
             fontsize=40, ha='center', va='center',
             alpha=0.1, fontweight='bold', color='green', rotation=30)

    # Add conversion arrow between images
    fig.text(0.5, 0.5, '➔', fontsize=60, ha='center', va='center',
             transform=fig.transFigure, color='#2ecc71', fontweight='bold')

    # Add title
    fig.suptitle('Layout A Warehouse Retrofit Conversion',
                 fontsize=18, fontweight='bold', y=0.98)

    # Add summary at bottom
    summary_text = (
        f"Conversion Summary: {summary['total_nodes']} nodes | "
        f"{summary['total_edges']} edges | "
        f"{summary['charging_stations_count']} charging stations | "
        f"Feasibility: {summary['feasibility_score']}/10"
    )
    fig.text(0.5, 0.02, summary_text, ha='center', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"✓ Saved: {output_path}")


def main():
    """Main function to generate all visualization images."""
    print("=" * 60)
    print("Layout A Conversion Visualization Generator")
    print("=" * 60)

    # Paths
    base_path = Path(__file__).parent
    input_file = base_path / "output" / "layout_a_conversion_output.json"
    output_dir = base_path / "output" / "images"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"\nLoading: {input_file}")
    data = load_conversion_output(str(input_file))
    print("✓ Data loaded successfully")

    # Generate images
    print("\nGenerating images...")

    # 1. Before conversion
    create_before_image(data, str(output_dir / "layout_a_before.png"))

    # 2. After conversion
    create_after_image(data, str(output_dir / "layout_a_after.png"))

    # 3. Side-by-side comparison
    create_comparison_image(data, str(output_dir / "layout_a_comparison.png"))

    print("\n" + "=" * 60)
    print("All images generated successfully!")
    print(f"Output directory: {output_dir}")
    print("=" * 60)

    # List generated files
    print("\nGenerated files:")
    for f in output_dir.glob("*.png"):
        size_kb = f.stat().st_size / 1024
        print(f"  • {f.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
