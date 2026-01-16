"""
Visualization 3: NPK Experiment Analysis

This visualization presents the controlled NPK fertilization experiment
conducted on citrus trees at Gilat Research Station. It includes:
1. Treatment table with 5 nitrogen levels (with sample counts and date range)
2. Sample collection timeline by treatment
3. Combined scatter plot with centroids + ridgeline distributions for N and ST

Author: Data Science Visualization Course Project
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import os
import sys
from datetime import datetime

# Add shared config to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import (
    TREATMENT_COLORS, TREATMENT_DESCRIPTIONS, TREATMENT_ORDER, NPK_TREATMENTS,
    HTML_STYLE, NPK_DATASET_PATH
)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_npk_data():
    """Load and prepare NPK experiment data."""
    print("Loading NPK dataset...")
    df = pd.read_csv(NPK_DATASET_PATH)

    df['parsed_date'] = pd.to_datetime(df['parsed_date'])
    df['year'] = df['parsed_date'].dt.year
    df['month'] = df['parsed_date'].dt.month
    df['N_ST_Ratio'] = df['N_Value'] / df['ST_Value'].replace(0, np.nan)

    print(f"Loaded {len(df)} NPK samples")
    return df


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_treatment_table(df):
    """Create HTML table for NPK treatments with sample counts and date range."""
    table_html = '''
    <table class="treatment-table" style="width: 100%; margin: 20px auto;">
        <tr>
            <th>Treatment</th>
            <th>N Level (kg/ha)</th>
            <th>Description</th>
            <th>Tree IDs</th>
            <th>Total Samples</th>
            <th>Date Range</th>
        </tr>
    '''

    for treatment in TREATMENT_ORDER:
        color = TREATMENT_COLORS[treatment]
        desc = TREATMENT_DESCRIPTIONS[treatment]
        trees = NPK_TREATMENTS[treatment]
        n_level = treatment.replace('N', '')

        # Get sample count and date range for this treatment
        trt_df = df[df['treatment'] == treatment]
        sample_count = len(trt_df)
        if len(trt_df) > 0:
            date_min = trt_df['parsed_date'].min().strftime('%b %Y')
            date_max = trt_df['parsed_date'].max().strftime('%b %Y')
            date_range = f"{date_min} - {date_max}"
        else:
            date_range = "N/A"

        table_html += f'''
        <tr>
            <td style="color: {color}; font-weight: bold; font-size: 1.1em;">{treatment}</td>
            <td>{n_level}</td>
            <td>{desc}</td>
            <td>{', '.join(map(str, trees))}</td>
            <td>{sample_count}</td>
            <td>{date_range}</td>
        </tr>
        '''

    table_html += '</table>'
    return table_html


def create_timeline_chart(df):
    """Create sample collection timeline by treatment."""
    df['year_month'] = df['parsed_date'].dt.to_period('M')
    timeline_data = df.groupby(['year_month', 'treatment']).size().reset_index(name='count')
    timeline_data['date'] = timeline_data['year_month'].dt.to_timestamp()

    fig = go.Figure()

    for treatment in TREATMENT_ORDER:
        treatment_data = timeline_data[timeline_data['treatment'] == treatment]
        if len(treatment_data) > 0:
            fig.add_trace(go.Bar(
                x=treatment_data['date'],
                y=treatment_data['count'],
                name=treatment,
                marker_color=TREATMENT_COLORS[treatment],
                hovertemplate=f'{treatment}<br>%{{x|%B %Y}}<br>Samples: %{{y}}<extra></extra>'
            ))

    fig.update_layout(
        title=dict(
            text="3.1 Sample Collection Timeline by Treatment<br><sup>Monthly sample counts for each nitrogen treatment level</sup>",
            font=dict(size=16)
        ),
        xaxis_title='Collection Date',
        yaxis_title='Number of Samples',
        barmode='group',
        xaxis=dict(tickformat='%b %Y', dtick='M3', range=['2021-10-01', '2024-10-31']),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            title='Treatment'
        ),
        height=450,
        hovermode='x unified'
    )

    return fig


def hex_to_rgba(hex_color, opacity):
    """Convert hex color to rgba string."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {opacity})'


def create_combined_scatter_ridgeline(df):
    """Create combined visualization with scatter plot (centroids) and ridgeline distributions.

    Layout:
    - Top: N_Value ridgeline (horizontal KDE distributions) - INTERACTIVE
    - Center: Scatter plot of N_Value vs ST_Value with treatment centroids
    - Right: ST_Value ridgeline (vertical KDE distributions) - INTERACTIVE

    Interactivity:
    - Click on ridge to toggle centroid marker on the SCATTER PLOT
    - Multiple centroids can be shown simultaneously
    - All ridges have high transparency to see through them
    - Lower treatments (N10, N40) are drawn on top to show high distribution values
    """
    # Create subplots with custom layout
    fig = make_subplots(
        rows=2, cols=2,
        column_widths=[0.8, 0.2],
        row_heights=[0.28, 0.72],
        horizontal_spacing=0.02,
        vertical_spacing=0.02,
        specs=[
            [{"type": "xy"}, None],           # Top-left: N ridgeline, Top-right: empty
            [{"type": "xy"}, {"type": "xy"}]  # Bottom-left: Scatter, Bottom-right: ST ridgeline
        ]
    )

    n_points = 150

    # Get data ranges for consistent axes
    n_min, n_max = df['N_Value'].min(), df['N_Value'].max()
    st_min, st_max = df['ST_Value'].min(), df['ST_Value'].max()
    n_padding = (n_max - n_min) * 0.1
    st_padding = (st_max - st_min) * 0.1

    n_range_vals = np.linspace(n_min - n_padding, n_max + n_padding, n_points)
    st_range_vals = np.linspace(st_min - st_padding, st_max + st_padding, n_points)

    # Calculate centroids for each treatment
    centroids = {}
    for treatment in TREATMENT_ORDER:
        treatment_data = df[df['treatment'] == treatment]
        if len(treatment_data) > 0:
            centroids[treatment] = {
                'n_mean': treatment_data['N_Value'].mean(),
                'n_median': treatment_data['N_Value'].median(),
                'st_mean': treatment_data['ST_Value'].mean(),
                'st_median': treatment_data['ST_Value'].median()
            }

    # =========================================================================
    # SCATTER PLOT (bottom-left) - with hidden centroid markers
    # =========================================================================
    for treatment in TREATMENT_ORDER:
        treatment_data = df[df['treatment'] == treatment]
        if len(treatment_data) == 0:
            continue

        color = TREATMENT_COLORS[treatment]

        # Add scatter points
        fig.add_trace(
            go.Scatter(
                x=treatment_data['N_Value'],
                y=treatment_data['ST_Value'],
                mode='markers',
                name=treatment,
                marker=dict(color=color, size=8, opacity=0.6),
                hovertemplate=f'{treatment}<br>N: %{{x:.2f}}%<br>ST: %{{y:.1f}} mg/g<extra></extra>',
                legendgroup=treatment
            ),
            row=2, col=1
        )

    # Add centroid markers on scatter plot (initially hidden) - one for each treatment
    for treatment in TREATMENT_ORDER:
        if treatment not in centroids:
            continue
        color = TREATMENT_COLORS[treatment]
        n_mean = centroids[treatment]['n_mean']
        st_mean = centroids[treatment]['st_mean']

        # Centroid marker on scatter plot - diamond with label
        fig.add_trace(
            go.Scatter(
                x=[n_mean],
                y=[st_mean],
                mode='markers+text',
                marker=dict(symbol='diamond', size=18, color=color,
                           line=dict(color='white', width=2)),
                text=[f'{treatment}'],
                textposition='top center',
                textfont=dict(size=11, color=color, family='Arial Black'),
                showlegend=False,
                visible=False,
                name=f'centroid_scatter_{treatment}',
                hovertemplate=f'<b>{treatment} Centroid</b><br>N: {n_mean:.2f}%<br>ST: {st_mean:.1f} mg/g<extra></extra>'
            ),
            row=2, col=1
        )

    # =========================================================================
    # N_VALUE RIDGELINE (top - horizontal KDEs)
    # N10 closest to scatter (baseline=0), but drawn ON TOP of others
    # High transparency so you can see through overlapping distributions
    # =========================================================================
    ridge_height = 0.50  # Height of each ridge
    fill_opacity = 0.20  # High transparency to see through

    # Position map: N10 at baseline 0 (closest to scatter), N150 at highest baseline
    position_map = {t: i for i, t in enumerate(TREATMENT_ORDER)}

    # Draw in reversed order so N10 is drawn last (on top)
    draw_order = list(reversed(TREATMENT_ORDER))  # [N150, N100, N60, N30, N10]

    for treatment in draw_order:
        treatment_data = df[df['treatment'] == treatment]['N_Value'].dropna()
        if len(treatment_data) < 3:
            continue

        try:
            kde = stats.gaussian_kde(treatment_data)
            density = kde(n_range_vals)
            density = density / density.max() * ridge_height * 1.2
        except:
            continue

        # Baseline position based on treatment order (N10=0, N40=1, N60=2, N100=3, N150=4)
        pos = position_map[treatment]
        y_baseline = pos * (ridge_height * 0.9)
        y_values = y_baseline + density

        color = TREATMENT_COLORS[treatment]
        n_mean = centroids[treatment]['n_mean']

        # Fill area - clickable with treatment info
        fig.add_trace(
            go.Scatter(
                x=list(n_range_vals) + list(n_range_vals)[::-1],
                y=list(y_values) + [y_baseline] * len(n_range_vals),
                fill='toself',
                fillcolor=hex_to_rgba(color, fill_opacity),
                line=dict(color=color, width=1.5),
                showlegend=False,
                name=f'ridge_n_{treatment}',
                hovertemplate=f'<b>{treatment}</b><br>Mean N: {n_mean:.2f}%<br>Click to show centroid on scatter plot<extra></extra>',
                legendgroup=treatment,
                meta={'treatment': treatment, 'type': 'ridge_n'}
            ),
            row=1, col=1
        )

    # =========================================================================
    # ST_VALUE RIDGELINE (right - vertical KDEs, rotated 90 degrees)
    # Same logic: N10 closest to scatter, drawn on top
    # =========================================================================
    for treatment in draw_order:
        treatment_data = df[df['treatment'] == treatment]['ST_Value'].dropna()
        if len(treatment_data) < 3:
            continue

        try:
            kde = stats.gaussian_kde(treatment_data)
            density = kde(st_range_vals)
            density = density / density.max() * ridge_height
        except:
            continue

        # Baseline position based on treatment order
        pos = position_map[treatment]
        x_baseline = pos * (ridge_height * 0.9)
        x_values = x_baseline + density

        color = TREATMENT_COLORS[treatment]
        st_mean = centroids[treatment]['st_mean']

        # Fill area (x and y swapped for vertical orientation)
        fig.add_trace(
            go.Scatter(
                x=list(x_values) + [x_baseline] * len(st_range_vals),
                y=list(st_range_vals) + list(st_range_vals)[::-1],
                fill='toself',
                fillcolor=hex_to_rgba(color, fill_opacity),
                line=dict(color=color, width=1.5),
                showlegend=False,
                name=f'ridge_st_{treatment}',
                hovertemplate=f'<b>{treatment}</b><br>Mean ST: {st_mean:.1f} mg/g<br>Click to show centroid on scatter plot<extra></extra>',
                legendgroup=treatment,
                meta={'treatment': treatment, 'type': 'ridge_st'}
            ),
            row=2, col=2
        )

    # =========================================================================
    # LAYOUT UPDATES
    # =========================================================================
    # Scatter plot axes
    fig.update_xaxes(
        title_text="N_Value (%)",
        range=[n_min - n_padding, n_max + n_padding],
        showgrid=True,
        gridcolor='rgba(0,0,0,0.1)',
        row=2, col=1
    )
    fig.update_yaxes(
        title_text="ST_Value (mg/g)",
        range=[st_min - st_padding, st_max + st_padding],
        showgrid=True,
        gridcolor='rgba(0,0,0,0.1)',
        row=2, col=1
    )

    # N ridgeline axes (top)
    fig.update_xaxes(
        range=[n_min - n_padding, n_max + n_padding],
        showticklabels=False,
        showgrid=False,
        row=1, col=1
    )
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        row=1, col=1
    )

    # ST ridgeline axes (right)
    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        row=2, col=2
    )
    fig.update_yaxes(
        range=[st_min - st_padding, st_max + st_padding],
        showticklabels=False,
        showgrid=False,
        row=2, col=2
    )

    fig.update_layout(
        title=dict(
            text="3.2 Treatment Comparison: N_Value vs ST_Value with Distributions<br><sup>Scatter plot with marginal KDE distributions by treatment</sup>",
            font=dict(size=16)
        ),
        height=650,
        autosize=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.08,
            xanchor='center',
            x=0.5,
            title='Treatment'
        ),
        plot_bgcolor='white',
        showlegend=True,
        margin=dict(l=50, r=50, t=100, b=100)
    )

    return fig


def create_summary_stats(df):
    """Create summary statistics table."""
    stats_data = []

    for treatment in TREATMENT_ORDER:
        treatment_df = df[df['treatment'] == treatment]
        n_trees = len(NPK_TREATMENTS[treatment])
        n_samples = len(treatment_df)
        n_dates = treatment_df['parsed_date'].dt.date.nunique()

        stats_data.append({
            'Treatment': treatment,
            'N Level': TREATMENT_DESCRIPTIONS[treatment].split('(')[1].rstrip(')'),
            'Trees': n_trees,
            'Samples': n_samples,
            'Dates': n_dates,
            'N_Value (mean ± std)': f"{treatment_df['N_Value'].mean():.2f} ± {treatment_df['N_Value'].std():.2f}",
            'ST_Value (mean ± std)': f"{treatment_df['ST_Value'].mean():.1f} ± {treatment_df['ST_Value'].std():.1f}"
        })

    stats_df = pd.DataFrame(stats_data)

    # Create HTML table
    table_html = '<table class="treatment-table" style="width: 100%;">'
    table_html += '<tr>'
    for col in stats_df.columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr>'

    for _, row in stats_df.iterrows():
        table_html += '<tr>'
        for col in stats_df.columns:
            if col == 'Treatment':
                color = TREATMENT_COLORS.get(row[col], '#333')
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

    # Create all components
    treatment_table = create_treatment_table(df)
    fig_timeline = create_timeline_chart(df)
    fig_combined = create_combined_scatter_ridgeline(df)

    # Convert to HTML
    plot_timeline = fig_timeline.to_html(full_html=False, include_plotlyjs='cdn')
    plot_combined = fig_combined.to_html(full_html=False, include_plotlyjs=False)

    # JavaScript for interactive ridge plot - toggle centroids on scatter plot
    ridge_interactivity_js = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Wait for Plotly to render
        setTimeout(function() {
            // Find the combined plot div (second plotly graph)
            const plotDivs = document.querySelectorAll('.js-plotly-plot');
            if (plotDivs.length < 2) return;

            const plotDiv = plotDivs[1];
            const treatments = ['N10', 'N40', 'N60', 'N100', 'N150'];

            // Track which centroids are currently visible (toggle state)
            const centroidVisible = {};
            treatments.forEach(t => centroidVisible[t] = false);

            // Find trace indices for centroids on scatter plot
            const centroidIndices = {};
            plotDiv.data.forEach((trace, idx) => {
                const name = trace.name || '';
                treatments.forEach(t => {
                    if (name === 'centroid_scatter_' + t) {
                        centroidIndices[t] = idx;
                    }
                });
            });

            plotDiv.on('plotly_click', function(data) {
                const clickedTrace = data.points[0];
                const traceName = clickedTrace.data.name || '';

                // Check if clicked on a ridge (N or ST)
                let clickedTreatment = null;
                treatments.forEach(t => {
                    if (traceName.includes('ridge_') && traceName.includes(t)) {
                        clickedTreatment = t;
                    }
                });

                if (!clickedTreatment) return;

                // Toggle the centroid visibility for this treatment
                centroidVisible[clickedTreatment] = !centroidVisible[clickedTreatment];

                // Update visibility for the centroid on scatter plot
                const idx = centroidIndices[clickedTreatment];
                if (idx !== undefined) {
                    const visArray = new Array(plotDiv.data.length).fill(undefined);
                    visArray[idx] = centroidVisible[clickedTreatment];
                    Plotly.restyle(plotDiv, {visible: visArray});
                }
            });
        }, 500);
    });
    </script>
    """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 3: NPK Experiment</title>
    {HTML_STYLE}
</head>
<body>
    <h1>NPK Experiment: 5 Nitrogen Treatments on Citrus (Gilat Station)</h1>
    <p class="subtitle">N10-N150 kg/ha | 5 trees per treatment | Measuring N% and Starch response</p>

    <div class="analysis-section">
        {treatment_table}
        {plot_timeline}
    </div>

    <div class="analysis-section">
        <p style="font-size: 12px; color: #666; margin-bottom: 10px; text-align: center;">
            <em>Click on any ridge distribution to toggle its centroid (mean) on the scatter plot. Multiple centroids can be shown simultaneously.</em>
        </p>
        {plot_combined}
    </div>

    {ridge_interactivity_js}
</body>
</html>"""

    return html_content


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Generating Visualization 3: NPK Experiment Analysis")
    print("=" * 70)

    # Load data
    df = load_npk_data()

    # Generate report
    html_content = generate_html_report(df)

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'npk_experiment.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nSaved to: {output_path}")
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
