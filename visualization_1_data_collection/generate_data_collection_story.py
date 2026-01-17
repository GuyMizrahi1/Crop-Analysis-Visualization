"""
Visualization 1: Data Collection Story

This visualization tells the story of how and where data was collected for
the crop nitrogen status research. It includes:
1. Timeline of sample collection by crop
2. Seasonal distribution of samples
3. Geographic distribution on an Israel map

Author: Data Science Visualization Course Project
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import sys
import re
from datetime import datetime

# Add shared config to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import (
    CROP_COLORS, HTML_STYLE, MONTH_NAMES, MONTH_LABELS,
    UNIFIED_DATASET_PATH, ISRAEL_LOCATIONS_PATH
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_crop_from_id(id_str):
    """Extract crop type from sample ID."""
    id_lower = str(id_str).lower()
    if id_lower.startswith('alm'):
        return 'Almond'
    elif id_lower.startswith('cit'):
        return 'Citrus'
    elif id_lower.startswith('avo'):
        return 'Avocado'
    elif id_lower.startswith('vin'):
        return 'Vine'
    return None


def extract_location_from_id(id_str):
    """Extract location from sample ID."""
    id_lower = str(id_str).lower()
    if 'gil' in id_lower or 'glt' in id_lower:
        return 'Gilat'
    elif 'ked' in id_lower:
        return 'Kedma'
    elif 'kfa' in id_lower:
        return 'Kfar Menahem'
    elif 'kab' in id_lower or 'kbr' in id_lower:
        return 'Kabri'
    return 'Unknown'


def extract_date_from_id(id_str):
    """Extract date from sample ID."""
    match = re.search(r'(\d{8})', str(id_str))
    if match:
        date_str = match.group(1)
        try:
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            if 2000 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                return datetime(year, month, day)
        except:
            pass
    return None


def load_data():
    """Load and prepare the unified dataset."""
    print("Loading unified dataset...")
    df = pd.read_parquet(UNIFIED_DATASET_PATH)

    # Parse ID fields
    df['parsed_crop'] = df['ID'].apply(extract_crop_from_id)
    df['parsed_location'] = df['ID'].apply(extract_location_from_id)
    df['parsed_date'] = df['ID'].apply(extract_date_from_id)

    # Filter to known locations
    allowed_locations = ['Gilat', 'Kedma', 'Kabri', 'Kfar Menahem']
    df = df[df['parsed_location'].isin(allowed_locations)]

    print(f"Loaded {len(df)} samples from {allowed_locations}")
    return df


def load_israel_locations():
    """Load Israel location coordinates."""
    with open(ISRAEL_LOCATIONS_PATH, 'r') as f:
        return json.load(f)


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_timeline_chart(df):
    """Create timeline of sample collection by crop."""
    df_with_dates = df[df['parsed_date'].notna()].copy()
    df_with_dates['year_month'] = df_with_dates['parsed_date'].dt.to_period('M')

    timeline_data = df_with_dates.groupby(['year_month', 'parsed_crop']).size().reset_index(name='count')
    timeline_data['date'] = timeline_data['year_month'].dt.to_timestamp()

    fig = go.Figure()

    for crop in ['Citrus', 'Almond', 'Avocado', 'Vine']:
        crop_data = timeline_data[timeline_data['parsed_crop'] == crop]
        if len(crop_data) > 0:
            fig.add_trace(go.Bar(
                x=crop_data['date'],
                y=crop_data['count'],
                name=crop,
                marker_color=CROP_COLORS.get(crop, '#888888'),
                hovertemplate=f'{crop}<br>%{{x|%B %Y}}<br>Samples: %{{y}}<extra></extra>'
            ))

    fig.update_layout(
        title=dict(
            text="1.1 Sample Leaves Collection Timeline: Monthly counts by crop (2021-2024)",
            font=dict(size=16)
        ),
        xaxis_title='Collection Date',
        yaxis_title='Number of Samples',
        barmode='group',
        xaxis=dict(
            tickformat='%b %Y',
            dtick='M3',
            range=['2018-04-01', '2024-10-31'],
            tickangle=-45
        ),
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.35,
            xanchor='center',
            x=0.5,
            title='Crop Type'
        ),
        height=500,
        margin=dict(b=150),
        hovermode='x unified'
    )

    return fig


def create_seasonal_distribution(df):
    """Create seasonal (monthly) distribution chart with all crops in one graph."""
    df_with_dates = df[df['parsed_date'].notna()].copy()
    df_with_dates['month'] = df_with_dates['parsed_date'].dt.month
    df_with_dates['month_name'] = df_with_dates['parsed_date'].dt.month_name()

    crops = ['Citrus', 'Almond', 'Avocado', 'Vine']

    fig = go.Figure()

    for crop_name in crops:
        crop_df = df_with_dates[df_with_dates['parsed_crop'] == crop_name]

        if len(crop_df) > 0:
            monthly_counts = crop_df.groupby('month_name').size().reset_index(name='count')
            all_months = pd.DataFrame({'month_name': MONTH_NAMES})
            monthly_counts = all_months.merge(monthly_counts, on='month_name', how='left')
            monthly_counts['count'] = monthly_counts['count'].fillna(0).astype(int)

            fig.add_trace(
                go.Bar(
                    x=monthly_counts['month_name'],
                    y=monthly_counts['count'],
                    name=crop_name,
                    marker_color=CROP_COLORS.get(crop_name, '#888888'),
                    hovertemplate=f'{crop_name}<br>%{{x}}<br>Samples: %{{y}}<extra></extra>'
                )
            )

    fig.update_xaxes(tickangle=-45, categoryorder='array', categoryarray=MONTH_NAMES)

    fig.update_layout(
        title=dict(
            text="1.2 Seasonal Distribution (DOY): Aggregated by Day-of-Year to reveal seasonal patterns<br><sup>Citrus has full 12-month coverage (150+ samples/month) --> Primary focus for subsequent analysis</sup>",
            font=dict(size=16)
        ),
        xaxis_title='Month',
        yaxis_title='Number of Samples',
        yaxis=dict(range=[0, 600]),
        barmode='group',
        height=500,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.35,
            xanchor='center',
            x=0.5,
            title='Crop Type'
        ),
        margin=dict(b=150),
        hovermode='x unified'
    )

    return fig


def create_israel_map_html(df):
    """Create geographic distribution map of Israel with circles sized by sample count.

    Labels are positioned OUTSIDE circles with arrows pointing to them.
    Circles have high transparency to show overlapping.
    """
    locations_data = load_israel_locations()

    # Get total counts per location
    location_totals = df.groupby('parsed_location').size().reset_index(name='total')

    # Location totals for labels
    loc_totals = {}
    for _, row in location_totals.iterrows():
        loc_totals[row['parsed_location']] = row['total']

    # Get crop distribution per location for pie charts
    crop_distribution = df.groupby(['parsed_location', 'parsed_crop']).size().unstack(fill_value=0)
    crop_dist_dict = {}
    for loc in crop_distribution.index:
        crop_dist_dict[loc] = {}
        for crop in ['Citrus', 'Almond', 'Avocado', 'Vine']:
            if crop in crop_distribution.columns:
                crop_dist_dict[loc][crop] = int(crop_distribution.loc[loc, crop])
            else:
                crop_dist_dict[loc][crop] = 0

    # Generate JavaScript data
    locations_js = json.dumps(locations_data['locations'])
    loc_totals_js = json.dumps(loc_totals)
    crop_dist_js = json.dumps(crop_dist_dict)

    # Label offsets for each location (to position labels outside circles)
    # Format: {location: {x_offset, y_offset, arrow_direction, padding, zIndex, latOffset, lonOffset, rotation}}
    # Padding is customized based on city name length
    # zIndex controls stacking order (higher = on top)
    # latOffset/lonOffset shift the pie chart position (positive lat = north)
    # rotation: degrees to rotate pie chart (negative = counter-clockwise)
    label_offsets = {
        'Kabri': {'x': 100, 'y': -15, 'arrow': 'left', 'padding': '8px 14px', 'zIndex': 100, 'latOffset': 0, 'lonOffset': 0, 'rotation': 0},
        'Kfar Menahem': {'x': -220, 'y': -20, 'arrow': 'right', 'padding': '8px 20px', 'zIndex': 300, 'latOffset': 0.02, 'lonOffset': 0, 'rotation': 0},
        'Kedma': {'x': 110, 'y': -15, 'arrow': 'left', 'padding': '8px 14px', 'zIndex': 200, 'latOffset': -0.06, 'lonOffset': 0, 'rotation': 0},
        'Gilat': {'x': -180, 'y': -15, 'arrow': 'right', 'padding': '8px 14px', 'zIndex': 100, 'latOffset': -0.06, 'lonOffset': 0, 'rotation': -60}
    }
    label_offsets_js = json.dumps(label_offsets)

    map_html = f'''
    <style>
        .count-label-single {{ pointer-events: none !important; }}
        .count-label-single * {{ pointer-events: none !important; }}
    </style>
    <div id="israel-map" style="height: 550px; width: 550px; border-radius: 8px; margin: 0;"></div>
    <div id="crop-info-panel" style="display: none; position: absolute; top: 50px; left: -320px; background: rgba(255,255,255,0.98); padding: 15px; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.2); z-index: 1000; min-width: 200px;"></div>
    <div style="display: flex; justify-content: center; gap: 25px; margin-top: 15px; font-size: 14px;">
        <span><span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: #E69F00; margin-right: 6px; vertical-align: middle;"></span>Citrus</span>
        <span><span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: #8B4513; margin-right: 6px; vertical-align: middle;"></span>Almond</span>
        <span><span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: #009E73; margin-right: 6px; vertical-align: middle;"></span>Avocado</span>
        <span><span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: #CC79A7; margin-right: 6px; vertical-align: middle;"></span>Vine</span>
    </div>

    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <script>
        (function() {{
            const locationsData = {locations_js};
            const locTotals = {loc_totals_js};
            const cropDist = {crop_dist_js};
            const labelOffsets = {label_offsets_js};

            // Crop colors matching the project color scheme
            const cropColors = {{
                'Citrus': '#E69F00',
                'Almond': '#8B4513',
                'Avocado': '#009E73',
                'Vine': '#CC79A7'
            }};

            // State: track which locations are showing detailed view
            const locationStates = {{}};
            Object.keys(locationsData).forEach(loc => locationStates[loc] = 'total');

            // Store references to markers for updating
            const pieMarkers = {{}};
            const countMarkers = {{}};

            // Function to create SVG pie chart with clickable segments
            function createPieChartSvg(cropData, radius, locName, showLabels = false) {{
                const total = Object.values(cropData).reduce((a, b) => a + b, 0);
                if (total === 0) return '';

                const cx = radius;
                const cy = radius;
                // Apply rotation offset for this location (default -60 = start from top)
                const rotationOffset = labelOffsets[locName]?.rotation || 0;
                let startAngle = -60 + rotationOffset;

                let svg = `<svg width="${{radius*2}}" height="${{radius*2}}" viewBox="0 0 ${{radius*2}} ${{radius*2}}" style="display: block; cursor: pointer;">`;
                svg += `<circle cx="${{cx}}" cy="${{cy}}" r="${{radius-1}}" fill="white" stroke="white" stroke-width="2"/>`;

                const crops = ['Citrus', 'Almond', 'Avocado', 'Vine'];
                const activeCrops = crops.filter(crop => (cropData[crop] || 0) > 0);

                if (activeCrops.length === 1) {{
                    const crop = activeCrops[0];
                    const count = cropData[crop];
                    svg += `<circle cx="${{cx}}" cy="${{cy}}" r="${{radius-2}}" fill="${{cropColors[crop]}}" stroke="white" stroke-width="0.5"
                            data-crop="${{crop}}" data-location="${{locName}}" class="pie-segment" style="cursor: pointer;"/>`;
                    if (showLabels) {{
                        svg += `<text x="${{cx}}" y="${{cy}}" text-anchor="middle" dominant-baseline="middle"
                                fill="white" font-size="14" font-weight="bold" style="text-shadow: 1px 1px 2px rgba(0,0,0,0.8); pointer-events: none;">${{count}}</text>`;
                    }}
                }} else {{
                    const labelPositions = [];
                    crops.forEach(crop => {{
                        const count = cropData[crop] || 0;
                        if (count > 0) {{
                            const angle = (count / total) * 360;
                            const endAngle = startAngle + angle;
                            const startRad = (startAngle * Math.PI) / 180;
                            const endRad = (endAngle * Math.PI) / 180;
                            const x1 = cx + (radius - 2) * Math.cos(startRad);
                            const y1 = cy + (radius - 2) * Math.sin(startRad);
                            const x2 = cx + (radius - 2) * Math.cos(endRad);
                            const y2 = cy + (radius - 2) * Math.sin(endRad);
                            const largeArc = angle > 180 ? 1 : 0;
                            const path = `M ${{cx}} ${{cy}} L ${{x1}} ${{y1}} A ${{radius-2}} ${{radius-2}} 0 ${{largeArc}} 1 ${{x2}} ${{y2}} Z`;
                            svg += `<path d="${{path}}" fill="${{cropColors[crop]}}" stroke="white" stroke-width="0.5"
                                    data-crop="${{crop}}" data-location="${{locName}}" class="pie-segment" style="cursor: pointer;"/>`;

                            if (showLabels) {{
                                const midAngle = (startAngle + angle / 2) * Math.PI / 180;
                                const labelR = radius * 0.6;
                                const lx = cx + labelR * Math.cos(midAngle);
                                const ly = cy + labelR * Math.sin(midAngle);
                                labelPositions.push({{ x: lx, y: ly, count: count }});
                            }}
                            startAngle = endAngle;
                        }}
                    }});

                    if (showLabels) {{
                        labelPositions.forEach(pos => {{
                            svg += `<text x="${{pos.x}}" y="${{pos.y}}" text-anchor="middle" dominant-baseline="middle"
                                    fill="white" font-size="14" font-weight="bold" style="text-shadow: 1px 1px 2px rgba(0,0,0,0.9); pointer-events: none;">${{pos.count}}</text>`;
                        }});
                    }}
                }}

                svg += `<circle cx="${{cx}}" cy="${{cy}}" r="${{radius-1}}" fill="none" stroke="white" stroke-width="2"/>`;
                svg += '</svg>';
                return svg;
            }}

            // Function to show crop info panel
            function showCropInfoPanel(cropName) {{
                const panel = document.getElementById('crop-info-panel');
                let html = `<div style="font-weight: bold; font-size: 14px; color: ${{cropColors[cropName]}}; margin-bottom: 10px; border-bottom: 2px solid ${{cropColors[cropName]}}; padding-bottom: 5px;">
                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: ${{cropColors[cropName]}}; margin-right: 8px;"></span>${{cropName}}
                </div>`;

                let grandTotal = 0;
                const locations = ['Kabri', 'Kfar Menahem', 'Kedma', 'Gilat'];
                locations.forEach(loc => {{
                    const count = cropDist[loc] ? (cropDist[loc][cropName] || 0) : 0;
                    grandTotal += count;
                    if (count > 0) {{
                        html += `<div style="padding: 4px 0; font-size: 13px;"><strong>${{loc}}:</strong> ${{count}} samples</div>`;
                    }}
                }});

                html += `<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #ddd; font-weight: bold; font-size: 13px;">Total: ${{grandTotal}} samples</div>`;
                html += `<div style="margin-top: 10px; font-size: 11px; color: #666; cursor: pointer;" onclick="document.getElementById('crop-info-panel').style.display='none';">Click to close</div>`;

                panel.innerHTML = html;
                panel.style.display = 'block';
            }}

            // Function to toggle location display mode
            function toggleLocationView(locName) {{
                // Check if location has only one crop - don't toggle if so
                const crops = cropDist[locName] || {{}};
                const activeCrops = Object.entries(crops).filter(([crop, count]) => count > 0);
                if (activeCrops.length <= 1) {{
                    // Single-crop location - do nothing on text label click
                    // (clicking on pie chart shows info panel instead)
                    return;
                }}

                const currentState = locationStates[locName];
                locationStates[locName] = currentState === 'total' ? 'detailed' : 'total';
                updatePieChart(locName);
            }}

            // Function to update pie chart and label
            function updatePieChart(locName) {{
                const showLabels = locationStates[locName] === 'detailed';
                const crops = cropDist[locName] || {{}};
                const total = locTotals[locName] || 0;
                const maxCount = Math.max(...Object.values(locTotals));
                const minRadius = 25;
                const maxRadius = 55;
                const radius = minRadius + (total / maxCount) * (maxRadius - minRadius);

                // Update pie chart
                if (pieMarkers[locName]) {{
                    const newSvg = createPieChartSvg(crops, radius, locName, showLabels);
                    pieMarkers[locName].getElement().querySelector('div').innerHTML = newSvg;
                    attachPieClickHandlers();
                }}

                // Update count label - hide if showing detailed
                if (countMarkers[locName]) {{
                    const countEl = countMarkers[locName].getElement();
                    if (countEl) {{
                        countEl.style.display = showLabels ? 'none' : 'block';
                    }}
                }}
            }}

            // Attach click handlers to pie segments
            function attachPieClickHandlers() {{
                document.querySelectorAll('.pie-segment').forEach(segment => {{
                    segment.onclick = function(e) {{
                        e.stopPropagation();
                        const crop = this.getAttribute('data-crop');
                        if (crop) showCropInfoPanel(crop);
                    }};
                }});
            }}

            // Initialize map
            const map = L.map('israel-map', {{
                center: [32.2, 35.0],
                zoom: 8,
                zoomControl: false,
                dragging: false,
                touchZoom: false,
                doubleClickZoom: false,
                scrollWheelZoom: false,
                boxZoom: false,
                keyboard: false
            }});

            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 20
            }}).addTo(map);

            const maxCount = Math.max(...Object.values(locTotals));
            const minRadius = 25;
            const maxRadius = 55;

            // Add pie chart circles for each location
            Object.keys(locationsData).forEach(locName => {{
                const loc = locationsData[locName];
                const total = locTotals[locName] || 0;
                const crops = cropDist[locName] || {{}};
                const offset = labelOffsets[locName] || {{x: 0, y: -60, arrow: 'down'}};
                const radius = minRadius + (total / maxCount) * (maxRadius - minRadius);
                const latOffset = offset.latOffset || 0;
                const lonOffset = offset.lonOffset || 0;
                const adjustedLat = loc.lat + latOffset;
                const adjustedLon = loc.lon + lonOffset;
                const pieChartSvg = createPieChartSvg(crops, radius, locName, false);
                const zIndex = offset.zIndex || 100;

                // Pie chart marker
                const pieMarker = L.marker([adjustedLat, adjustedLon], {{
                    icon: L.divIcon({{
                        className: 'pie-chart-marker',
                        html: `<div>${{pieChartSvg}}</div>`,
                        iconSize: [radius * 2, radius * 2],
                        iconAnchor: [radius, radius]
                    }}),
                    zIndexOffset: zIndex
                }}).addTo(map);
                pieMarkers[locName] = pieMarker;

                // Add click handler to pie marker for single-crop locations
                const activeCrops = Object.entries(crops).filter(([crop, count]) => count > 0);
                if (activeCrops.length === 1) {{
                    pieMarker.on('click', function(e) {{
                        L.DomEvent.stopPropagation(e);
                        showCropInfoPanel(activeCrops[0][0]);
                    }});
                }} else {{
                    // Multi-crop locations toggle view on marker click
                    pieMarker.on('click', function(e) {{
                        L.DomEvent.stopPropagation(e);
                        toggleLocationView(locName);
                    }});
                }}

                // Count label marker
                // For single-crop locations, use different className so CSS disables pointer-events on Leaflet wrapper
                const countClassName = activeCrops.length === 1 ? 'count-label-single' : 'count-label';
                const pointerStyle = activeCrops.length === 1 ? 'pointer-events: none;' : 'cursor: pointer;';
                const countMarker = L.marker([adjustedLat, adjustedLon], {{
                    icon: L.divIcon({{
                        className: countClassName,
                        html: `<div style="
                            color: white; font-size: 13px; font-weight: bold;
                            text-shadow: 1px 1px 3px rgba(0,0,0,0.9), -1px -1px 2px rgba(0,0,0,0.5);
                            text-align: center; width: ${{radius * 2}}px; line-height: ${{radius * 2}}px;
                            ${{pointerStyle}}
                        ">${{total}}</div>`,
                        iconSize: [radius * 2, radius * 2],
                        iconAnchor: [radius, radius]
                    }}),
                    zIndexOffset: zIndex + 10
                }}).addTo(map);
                countMarkers[locName] = countMarker;

                // Add click handler to count marker for multi-crop locations only
                if (activeCrops.length > 1) {{
                    countMarker.on('click', function(e) {{
                        L.DomEvent.stopPropagation(e);
                        toggleLocationView(locName);
                    }});
                }}

                // Arrow SVG
                const arrowSvg = offset.arrow === 'left'
                    ? `<svg width="60" height="20" style="position: absolute; left: -65px; top: 50%; transform: translateY(-50%);">
                        <line x1="55" y1="10" x2="5" y2="10" stroke="#1B5E20" stroke-width="2"/>
                        <polygon points="5,10 12,6 12,14" fill="#1B5E20"/>
                       </svg>`
                    : `<svg width="60" height="20" style="position: absolute; right: -65px; top: 50%; transform: translateY(-50%);">
                        <line x1="5" y1="10" x2="55" y2="10" stroke="#1B5E20" stroke-width="2"/>
                        <polygon points="55,10 48,6 48,14" fill="#1B5E20"/>
                       </svg>`;

                // Location label with click handler
                const labelPadding = offset.padding || '8px 14px';
                const labelMarker = L.marker([adjustedLat, adjustedLon], {{
                    icon: L.divIcon({{
                        className: 'location-label',
                        html: `<div class="loc-label" data-location="${{locName}}" style="
                            position: relative; display: inline-block; cursor: pointer;
                            background: rgba(27, 94, 32, 0.95); color: white;
                            padding: ${{labelPadding}}; border-radius: 4px;
                            font-size: 12px; font-weight: bold; white-space: nowrap;
                            text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                            transform: translate(${{offset.x}}px, ${{offset.y}}px);
                        ">${{locName}}${{arrowSvg}}</div>`,
                        iconSize: [0, 0],
                        iconAnchor: [0, 0]
                    }}),
                    zIndexOffset: zIndex + 20
                }}).addTo(map);
            }});

            // Attach click handlers after markers are added
            setTimeout(() => {{
                attachPieClickHandlers();

                // Attach click handlers to location labels
                document.querySelectorAll('.loc-label').forEach(label => {{
                    label.onclick = function(e) {{
                        e.stopPropagation();
                        const locName = this.getAttribute('data-location');
                        if (locName) toggleLocationView(locName);
                    }};
                }});
            }}, 100);

            // Close info panel when clicking elsewhere on map
            map.on('click', function() {{
                document.getElementById('crop-info-panel').style.display = 'none';
            }});
        }})();
    </script>
    '''

    return map_html


def create_location_crop_table(df):
    """Create a table showing crop breakdown by location."""
    # Calculate sample counts per location and crop
    location_crop_counts = df.groupby(['parsed_location', 'parsed_crop']).size().reset_index(name='count')

    # Pivot to get locations as rows, crops as columns
    pivot_df = location_crop_counts.pivot(index='parsed_location', columns='parsed_crop', values='count').fillna(0).astype(int)

    # Define location order (north to south)
    location_order = ['Kabri', 'Kfar Menahem', 'Kedma', 'Gilat']
    crop_order = ['Citrus', 'Almond', 'Avocado', 'Vine']

    # Build HTML table
    table_html = '''
    <table style="border-collapse: collapse; font-size: 13px; width: 100%;">
        <tr style="background: linear-gradient(180deg, #e8f5e9, #c8e6c9);">
            <th style="border: 1px solid #ddd; padding: 8px 12px; text-align: left;">Location</th>
    '''

    # Add crop headers with colored indicators
    for crop in crop_order:
        color = CROP_COLORS.get(crop, '#888')
        table_html += f'''
            <th style="border: 1px solid #ddd; padding: 8px 10px; text-align: center;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: {color}; margin-right: 5px;"></span>{crop}
            </th>
        '''

    table_html += '<th style="border: 1px solid #ddd; padding: 8px 10px; text-align: center; font-weight: bold;">Total</th></tr>'

    # Add rows for each location
    for loc in location_order:
        if loc in pivot_df.index:
            row_total = 0
            table_html += f'<tr><td style="border: 1px solid #ddd; padding: 8px 12px; font-weight: bold;">{loc}</td>'

            for crop in crop_order:
                count = pivot_df.loc[loc, crop] if crop in pivot_df.columns else 0
                row_total += count
                # Highlight cells with data
                bg_color = 'rgba(76, 175, 80, 0.1)' if count > 0 else 'transparent'
                table_html += f'<td style="border: 1px solid #ddd; padding: 8px 10px; text-align: center; background: {bg_color};">{count if count > 0 else "-"}</td>'

            table_html += f'<td style="border: 1px solid #ddd; padding: 8px 10px; text-align: center; font-weight: bold; background: rgba(27, 94, 32, 0.1);">{row_total}</td></tr>'

    # Add totals row
    table_html += '<tr style="background: rgba(27, 94, 32, 0.15);"><td style="border: 1px solid #ddd; padding: 8px 12px; font-weight: bold;">Total</td>'
    grand_total = 0
    for crop in crop_order:
        if crop in pivot_df.columns:
            crop_total = pivot_df[crop].sum()
            grand_total += crop_total
            table_html += f'<td style="border: 1px solid #ddd; padding: 8px 10px; text-align: center; font-weight: bold;">{crop_total}</td>'
        else:
            table_html += '<td style="border: 1px solid #ddd; padding: 8px 10px; text-align: center;">-</td>'

    table_html += f'<td style="border: 1px solid #ddd; padding: 8px 10px; text-align: center; font-weight: bold;">{grand_total}</td></tr>'
    table_html += '</table>'

    return table_html


def create_summary_table(df):
    """Create a summary statistics table (without Locations column - shown in map)."""
    df_with_dates = df[df['parsed_date'].notna()].copy()

    summary_data = []
    for crop_name in ['Citrus', 'Almond', 'Avocado', 'Vine']:
        crop_df = df[df['parsed_crop'] == crop_name]
        crop_df_dates = df_with_dates[df_with_dates['parsed_crop'] == crop_name]

        if len(crop_df) == 0:
            continue

        sample_count = len(crop_df)

        if len(crop_df_dates) > 0:
            date_range = f"{crop_df_dates['parsed_date'].min().strftime('%b %Y')} - {crop_df_dates['parsed_date'].max().strftime('%b %Y')}"
            unique_dates = crop_df_dates['parsed_date'].dt.date.nunique()
        else:
            date_range = "N/A"
            unique_dates = 0

        summary_data.append({
            'Crop': crop_name,
            'Total Samples': sample_count,
            'Date Range': date_range,
            'Unique Dates': unique_dates
        })

    summary_df = pd.DataFrame(summary_data)

    # Create HTML table
    table_html = '<table class="treatment-table" style="width: 100%;">'
    table_html += '<tr>'
    for col in summary_df.columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr>'

    for _, row in summary_df.iterrows():
        table_html += '<tr>'
        for col in summary_df.columns:
            if col == 'Crop':
                color = CROP_COLORS.get(row[col], '#333')
                table_html += f'<td style="color: {color}; font-weight: bold;">{row[col]}</td>'
            else:
                table_html += f'<td>{row[col]}</td>'
        table_html += '</tr>'

    table_html += '</table>'

    return table_html


# =============================================================================
# HTML REPORT GENERATION
# =============================================================================

def generate_html_report(df):
    """Generate the complete HTML report."""
    print("Generating visualizations...")

    # Create all figures
    fig_timeline = create_timeline_chart(df)
    fig_seasonal = create_seasonal_distribution(df)
    map_html = create_israel_map_html(df)
    location_crop_table = create_location_crop_table(df)
    summary_table = create_summary_table(df)

    # Convert to HTML
    plot_timeline = fig_timeline.to_html(full_html=False, include_plotlyjs='cdn')
    plot_seasonal = fig_seasonal.to_html(full_html=False, include_plotlyjs=False)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 1: Data Collection Overview</title>
    {HTML_STYLE}
</head>
<body>
    <h1>NIR (Near Infrared) Spectroscopy Dataset: 4 Crops, 4 Locations, 7,500+ Samples</h1>
    <p class="subtitle">Leaf samples with 1,557 spectral wavelengths and chemical values: N (Nitrogen), ST (Starch), SC (Soluble Carbohydrates) | 2021-2024</p>

    <div class="analysis-section">
        {summary_table}
        {plot_timeline}
    </div>

    <div class="analysis-section">
        {plot_seasonal}
    </div>

    <div class="analysis-section">
        <h3 style="color: #1B5E20; margin-bottom: 5px;">1.3 Geographic Distribution: 4 Research Sites Across Israel (North to South)</h3>
        <p style="font-size: 13px; color: #555; margin-bottom: 15px;">Pie charts show crop distribution per location. Circle size reflects total sample count. <span style="color: #888;"><br>(Click city name to show sample counts per crop, click pie segment to see crop distribution across all sites)</span></p>
        <div style="display: flex; justify-content: center; align-items: flex-start; gap: 0; position: relative;">
            <div style="position: relative;">
                {map_html}
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_content


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Generating Visualization 1: Data Collection Story")
    print("=" * 70)

    # Load data
    df = load_data()

    # Generate report
    html_content = generate_html_report(df)

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'data_collection_story.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nSaved to: {output_path}")
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
