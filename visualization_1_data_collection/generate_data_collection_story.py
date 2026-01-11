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
            text="1.1 Timeline of Sample Collection<br><sup>Monthly sample counts by crop type</sup>",
            font=dict(size=18)
        ),
        xaxis_title='Collection Date',
        yaxis_title='Number of Samples',
        barmode='group',
        xaxis=dict(tickformat='%b %Y', dtick='M3'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            title='Crop Type'
        ),
        height=500,
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
            text="1.2 Seasonal Sample Distribution<br><sup>Monthly sample counts by crop (all years combined)</sup>",
            font=dict(size=18)
        ),
        xaxis_title='Month',
        yaxis_title='Number of Samples',
        yaxis=dict(range=[0, 600]),
        barmode='group',
        height=500,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            title='Crop Type'
        ),
        hovermode='x unified'
    )

    return fig


def create_israel_map_html(df):
    """Create geographic distribution map of Israel using Leaflet.js."""
    locations_data = load_israel_locations()

    # Calculate sample counts per location and crop
    location_crop_counts = df.groupby(['parsed_location', 'parsed_crop']).size().reset_index(name='count')

    # Get total counts per location for sizing
    location_totals = df.groupby('parsed_location').size().reset_index(name='total')

    # Prepare marker data for JavaScript
    markers_data = []
    for _, row in location_crop_counts.iterrows():
        loc = row['parsed_location']
        crop = row['parsed_crop']
        count = row['count']
        if loc in locations_data['locations']:
            loc_info = locations_data['locations'][loc]
            markers_data.append({
                'lat': loc_info['lat'],
                'lon': loc_info['lon'],
                'location': loc,
                'crop': crop,
                'count': count,
                'color': CROP_COLORS.get(crop, '#888888')
            })

    # Location totals for labels
    loc_totals = {}
    for _, row in location_totals.iterrows():
        loc_totals[row['parsed_location']] = row['total']

    # Generate JavaScript marker data
    markers_js = json.dumps(markers_data)
    locations_js = json.dumps(locations_data['locations'])
    loc_totals_js = json.dumps(loc_totals)
    crop_colors_js = json.dumps(CROP_COLORS)

    map_html = f'''
    <div id="israel-map" style="height: 600px; width: 100%; border-radius: 8px; margin: 20px 0;"></div>
    <div style="display: flex; justify-content: center; gap: 30px; margin-top: 15px; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 16px; height: 16px; border-radius: 50%; background: #E69F00;"></div>
            <span>Citrus</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 16px; height: 16px; border-radius: 50%; background: #8B4513;"></div>
            <span>Almond</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 16px; height: 16px; border-radius: 50%; background: #009E73;"></div>
            <span>Avocado</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 16px; height: 16px; border-radius: 50%; background: #CC79A7;"></div>
            <span>Vine</span>
        </div>
    </div>

    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <script>
        (function() {{
            const markersData = {markers_js};
            const locationsData = {locations_js};
            const locTotals = {loc_totals_js};
            const cropColors = {crop_colors_js};

            // Initialize map centered on Israel
            const map = L.map('israel-map', {{
                center: [31.5, 35.0],
                zoom: 8,
                minZoom: 7,
                maxZoom: 12
            }});

            // Add CartoDB Positron tile layer (clean, light style)
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
                subdomains: 'abcd',
                maxZoom: 20
            }}).addTo(map);

            // Group markers by location to offset them
            const locationOffsets = {{}};
            const offsetStep = 0.03;

            markersData.forEach((marker, index) => {{
                const key = marker.location;
                if (!locationOffsets[key]) {{
                    locationOffsets[key] = 0;
                }}

                // Calculate offset for multiple crops at same location
                const cropIndex = ['Citrus', 'Almond', 'Avocado', 'Vine'].indexOf(marker.crop);
                const latOffset = (cropIndex % 2) * offsetStep - offsetStep / 2;
                const lonOffset = Math.floor(cropIndex / 2) * offsetStep - offsetStep / 2;

                // Size based on sample count (radius in pixels)
                const radius = Math.max(8, Math.min(35, Math.sqrt(marker.count) * 2.5));

                // Create circle marker
                const circle = L.circleMarker([marker.lat + latOffset, marker.lon + lonOffset], {{
                    radius: radius,
                    fillColor: marker.color,
                    color: '#fff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }}).addTo(map);

                // Add popup
                circle.bindPopup(`
                    <div style="text-align: center; padding: 5px;">
                        <strong style="font-size: 14px; color: ${{marker.color}};">${{marker.crop}}</strong><br>
                        <span style="font-size: 12px;">${{marker.location}}</span><br>
                        <span style="font-size: 16px; font-weight: bold;">${{marker.count}} samples</span>
                    </div>
                `);

                // Hover effect
                circle.on('mouseover', function() {{
                    this.setStyle({{ fillOpacity: 1, weight: 3 }});
                }});
                circle.on('mouseout', function() {{
                    this.setStyle({{ fillOpacity: 0.8, weight: 2 }});
                }});
            }});

            // Add location labels
            Object.keys(locationsData).forEach(locName => {{
                const loc = locationsData[locName];
                const total = locTotals[locName] || 0;

                L.marker([loc.lat + 0.08, loc.lon], {{
                    icon: L.divIcon({{
                        className: 'location-label',
                        html: `<div style="
                            background: rgba(27, 94, 32, 0.9);
                            color: white;
                            padding: 4px 10px;
                            border-radius: 4px;
                            font-size: 12px;
                            font-weight: bold;
                            white-space: nowrap;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                        ">${{locName}} (${{total}})</div>`,
                        iconSize: [100, 20],
                        iconAnchor: [50, 10]
                    }})
                }}).addTo(map);
            }});
        }})();
    </script>
    '''

    return map_html


def create_summary_table(df):
    """Create a summary statistics table."""
    df_with_dates = df[df['parsed_date'].notna()].copy()

    summary_data = []
    for crop_name in ['Citrus', 'Almond', 'Avocado', 'Vine']:
        crop_df = df[df['parsed_crop'] == crop_name]
        crop_df_dates = df_with_dates[df_with_dates['parsed_crop'] == crop_name]

        if len(crop_df) == 0:
            continue

        sample_count = len(crop_df)
        location_counts = crop_df['parsed_location'].value_counts()
        locations_str = ', '.join([f"{loc} ({count})" for loc, count in location_counts.items()])

        if len(crop_df_dates) > 0:
            date_range = f"{crop_df_dates['parsed_date'].min().strftime('%b %Y')} - {crop_df_dates['parsed_date'].max().strftime('%b %Y')}"
            unique_dates = crop_df_dates['parsed_date'].dt.date.nunique()
        else:
            date_range = "N/A"
            unique_dates = 0

        summary_data.append({
            'Crop': crop_name,
            'Total Samples': sample_count,
            'Locations': locations_str,
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
    summary_table = create_summary_table(df)

    # Convert to HTML
    plot_timeline = fig_timeline.to_html(full_html=False, include_plotlyjs='cdn')
    plot_seasonal = fig_seasonal.to_html(full_html=False, include_plotlyjs=False)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 1: Data Collection Story</title>
    {HTML_STYLE}
</head>
<body>
    <h1>Data Collection Story</h1>
    <p class="subtitle">Understanding the scope and distribution of our agricultural spectroscopy dataset</p>

    <div class="intro-box">
        <h3 style="margin-top: 0; border: none; padding-left: 0;">Research Context</h3>
        <p>This research project combines <strong>spectroscopy measurements</strong> with <strong>chemical analysis</strong>
        to study nitrogen status in agricultural crops. Leaf samples were collected from four crop types across
        multiple research stations in Israel over several years.</p>

        <p><strong>Key measurements collected:</strong></p>
        <ul>
            <li><strong>Spectral Data:</strong> Near-infrared reflectance across 1,557 wavelengths (3,999-10,001 nm)</li>
            <li><strong>N_Value:</strong> Nitrogen content (%) - essential nutrient indicator</li>
            <li><strong>SC_Value:</strong> Soluble Carbohydrates (mg/g) - readily available energy</li>
            <li><strong>ST_Value:</strong> Starch content (mg/g) - long-term energy storage</li>
        </ul>
    </div>

    <h3 style="margin-top: 30px;">Dataset Overview</h3>
    <div class="analysis-section">
        <p>Summary of samples collected across crops and locations:</p>
        {summary_table}
    </div>

    <h2>Temporal Distribution</h2>

    <h3>1.1 Timeline of Sample Collection</h3>
    <div class="analysis-section">
        <p>The timeline below shows when samples were collected for each crop type.
        This temporal coverage is crucial for understanding seasonal patterns in plant chemistry.</p>
        {plot_timeline}
    </div>

    <h3>1.2 Seasonal Sample Distribution</h3>
    <div class="analysis-section">
        <p>Monthly distribution reveals the seasonal coverage of our sampling. Different crops have
        different active growing seasons, reflected in the sampling patterns.</p>
        {plot_seasonal}

        <div class="key-observations">
            <h4>Seasonal Observations</h4>
            <ul>
                <li><strong>Citrus:</strong> Year-round sampling with peaks in spring and summer</li>
                <li><strong>Almond:</strong> Concentrated sampling during active growing season</li>
                <li><strong>Avocado:</strong> Multiple seasons covered for comprehensive analysis</li>
                <li><strong>Vine:</strong> Focused sampling during key phenological stages</li>
            </ul>
        </div>
    </div>

    <h2>Geographic Distribution</h2>

    <h3>1.3 Sample Locations Across Israel</h3>
    <div class="analysis-section">
        <p>Samples were collected from four agricultural research stations across Israel,
        representing different climatic zones and growing conditions. Circle size indicates sample count.</p>
        {map_html}

        <div class="methodology">
            <h4>Research Stations</h4>
            <ul>
                <li><strong>Gilat:</strong> Major research station in the Negev - primary location for NPK experiments</li>
                <li><strong>Kedma:</strong> Central Israel agricultural research area</li>
                <li><strong>Kabri:</strong> Western Galilee - northern climate conditions</li>
                <li><strong>Kfar Menahem:</strong> Coastal plain - Mediterranean climate</li>
            </ul>
        </div>
    </div>

    <div class="discovery-box">
        <h3>Data Collection Summary</h3>
        <p>This comprehensive dataset provides the foundation for our analysis of crop nitrogen status:</p>
        <ul>
            <li><strong>Multi-crop coverage:</strong> Four distinct crop types with different physiological characteristics</li>
            <li><strong>Temporal depth:</strong> Multi-year sampling enabling seasonal and annual pattern analysis</li>
            <li><strong>Geographic diversity:</strong> Four locations representing Israel's agricultural zones</li>
            <li><strong>Rich measurements:</strong> Combined spectral and chemical data for advanced modeling</li>
        </ul>
    </div>

    <p class="timestamp">Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
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
