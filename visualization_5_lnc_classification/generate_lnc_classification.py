"""
Visualization 5: LNC Status Classification

This visualization presents the Leaf Nitrogen Content (LNC) classification
based on UC Davis thresholds, with seasonal adjustment patterns.

Includes:
1. UC Davis thresholds table (with corrected colors: blue=low, red=high)
2. LNC status classification timeline with threshold bands

Author: Data Science Visualization Course Project
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys
from datetime import datetime

# Add shared config to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import (
    TREATMENT_COLORS, TREATMENT_ORDER,
    LNC_BAND_COLORS, LNC_OCT_THRESHOLDS, LNC_MONTHLY_FACTORS,
    HTML_STYLE, NPK_DATASET_PATH, get_threshold_for_date
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

    # Filter to Aug 2022 - Aug 2024
    start_date = pd.Timestamp('2022-08-01')
    end_date = pd.Timestamp('2024-08-31')
    df = df[(df['parsed_date'] >= start_date) & (df['parsed_date'] <= end_date)]

    print(f"Loaded {len(df)} NPK samples (Aug 2022 - Aug 2024)")
    return df


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_thresholds_table():
    """Create dynamic monthly thresholds table based on UC Davis October reference."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Calculate all 4 monthly thresholds
    monthly_deficient_low = [LNC_OCT_THRESHOLDS['deficient_low'] * LNC_MONTHLY_FACTORS[i] for i in range(1, 13)]
    monthly_low_optimum = [LNC_OCT_THRESHOLDS['low_optimum'] * LNC_MONTHLY_FACTORS[i] for i in range(1, 13)]
    monthly_optimum_high = [LNC_OCT_THRESHOLDS['optimum_high'] * LNC_MONTHLY_FACTORS[i] for i in range(1, 13)]
    monthly_high_excess = [LNC_OCT_THRESHOLDS['high_excess'] * LNC_MONTHLY_FACTORS[i] for i in range(1, 13)]

    table_html = '''
    <h3 style="color: #1B5E20; margin-bottom: 5px;">5.1 Dynamic Monthly LNC Thresholds<br><span style="font-size: 0.7em; font-weight: normal; color: #555;">All thresholds derived from UC Davis October reference &times; seasonal factor</span></h3>
    <p style="margin-bottom: 15px; color: #555;">UC Davis provides October reference values for citrus LNC classification.<br>This reference adapted into <strong>dynamic monthly thresholds</strong> using seasonal adjustment factors that account for natural nitrogen fluctuations throughout the year.</p>
    <table class="treatment-table" style="width: 100%; margin: 20px auto; font-size: 0.9em;">
        <tr>
            <th>Threshold</th>'''

    for m in months:
        is_oct = (m == 'Oct')
        style = ' style="background: rgba(76, 175, 80, 0.2);"' if is_oct else ''
        table_html += f'<th{style}>{m}</th>'
    table_html += '</tr>'

    # High/Excess boundary row (top - highest values)
    table_html += '<tr><td style="font-weight: bold; color: #388E3C;">High/Excess</td>'
    for i, val in enumerate(monthly_high_excess):
        is_oct = (i == 9)
        style = ' style="background: rgba(76, 175, 80, 0.2);"' if is_oct else ''
        table_html += f'<td{style}>{val:.2f}%</td>'
    table_html += '</tr>'

    # Optimum/High boundary row
    table_html += '<tr><td style="font-weight: bold; color: #4CAF50;">Optimum/High</td>'
    for i, val in enumerate(monthly_optimum_high):
        is_oct = (i == 9)
        style = ' style="background: rgba(76, 175, 80, 0.2);"' if is_oct else ''
        table_html += f'<td{style}>{val:.2f}%</td>'
    table_html += '</tr>'

    # Low/Optimum boundary row
    table_html += '<tr><td style="font-weight: bold; color: #81C784;">Low/Optimum</td>'
    for i, val in enumerate(monthly_low_optimum):
        is_oct = (i == 9)
        style = ' style="background: rgba(76, 175, 80, 0.2);"' if is_oct else ''
        table_html += f'<td{style}>{val:.2f}%</td>'
    table_html += '</tr>'

    # Deficient/Low boundary row (bottom - lowest values)
    table_html += '<tr><td style="font-weight: bold; color: #C8E6C9;">Deficient/Low</td>'
    for i, val in enumerate(monthly_deficient_low):
        is_oct = (i == 9)
        style = ' style="background: rgba(76, 175, 80, 0.2);"' if is_oct else ''
        table_html += f'<td{style}>{val:.2f}%</td>'
    table_html += '</tr>'

    # Seasonal factor row
    table_html += '<tr style="font-size: 0.85em; color: #666;"><td>Seasonal Factor</td>'
    for i in range(1, 13):
        factor = LNC_MONTHLY_FACTORS[i]
        is_oct = (i == 10)
        style = ' style="background: rgba(76, 175, 80, 0.2);"' if is_oct else ''
        table_html += f'<td{style}>{factor:.3f}</td>'
    table_html += '</tr>'

    table_html += '''
    </table>
    <p style="font-size: 0.85em; color: #666; margin-top: 10px;"><em>October (highlighted) = UC Davis reference month (factor = 1.000). Other months adjusted based on seasonal nitrogen patterns in citrus leaves.</em></p>
    '''
    return table_html


def create_seasonal_factors_table():
    """Create monthly seasonal adjustment factors table."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    table_html = '<table class="treatment-table" style="width: 100%; margin: 20px auto;">'
    table_html += '<tr><th>Month</th>'
    for m in months:
        table_html += f'<th>{m}</th>'
    table_html += '</tr>'

    table_html += '<tr><td style="font-weight: bold;">Factor</td>'
    for i in range(1, 13):
        factor = LNC_MONTHLY_FACTORS[i]
        # Color code based on factor
        if factor > 1.05:
            color = 'rgba(255, 107, 107, 0.3)'
        elif factor < 0.95:
            color = 'rgba(135, 206, 250, 0.3)'
        else:
            color = 'rgba(78, 205, 196, 0.3)'
        table_html += f'<td style="background: {color};">{factor:.3f}</td>'
    table_html += '</tr>'

    table_html += '<tr><td style="font-weight: bold;">Optimum Low</td>'
    for i in range(1, 13):
        threshold = LNC_OCT_THRESHOLDS['low_optimum'] * LNC_MONTHLY_FACTORS[i]
        table_html += f'<td>{threshold:.2f}%</td>'
    table_html += '</tr>'

    table_html += '<tr><td style="font-weight: bold;">Optimum High</td>'
    for i in range(1, 13):
        threshold = LNC_OCT_THRESHOLDS['optimum_high'] * LNC_MONTHLY_FACTORS[i]
        table_html += f'<td>{threshold:.2f}%</td>'
    table_html += '</tr>'

    table_html += '</table>'
    return table_html


def create_lnc_classification_chart(df):
    """Create LNC classification timeline with threshold bands."""
    min_date = df['parsed_date'].min()
    max_date = df['parsed_date'].max()

    # Create monthly date range for threshold curves
    start_threshold = pd.Timestamp('2022-07-01')
    end_threshold = pd.Timestamp('2024-09-01')
    monthly_dates = pd.date_range(start=start_threshold, end=end_threshold, freq='MS')
    monthly_dates = [d.replace(day=15) for d in monthly_dates]

    # Calculate threshold values
    t1_values = [get_threshold_for_date(d, 'deficient_low') for d in monthly_dates]
    t2_values = [get_threshold_for_date(d, 'low_optimum') for d in monthly_dates]
    t3_values = [get_threshold_for_date(d, 'optimum_high') for d in monthly_dates]
    t4_values = [get_threshold_for_date(d, 'high_excess') for d in monthly_dates]

    fig = go.Figure()

    BOUNDARY_LINE_COLOR = 'rgba(80, 80, 80, 0.5)'
    LINE_WIDTH = 0.5  # Very thin lines
    LINE_SHAPE = 'spline'

    # Add threshold bands (bottom to top)
    # Floor
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=[1.5] * len(monthly_dates),
        mode='lines', line=dict(width=0, shape=LINE_SHAPE),
        showlegend=False, hoverinfo='skip', name='_floor'
    ))

    # Deficient band
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=t1_values,
        mode='lines', name='Deficient',
        line=dict(color=BOUNDARY_LINE_COLOR, width=LINE_WIDTH, shape=LINE_SHAPE),
        fill='tonexty', fillcolor=LNC_BAND_COLORS['Deficient'],
        hovertemplate='Deficient/Low boundary: %{y:.2f}%<extra></extra>'
    ))

    # Low band
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=t2_values,
        mode='lines', name='Low',
        line=dict(color=BOUNDARY_LINE_COLOR, width=LINE_WIDTH, shape=LINE_SHAPE),
        fill='tonexty', fillcolor=LNC_BAND_COLORS['Low'],
        hovertemplate='Low/Optimum boundary: %{y:.2f}%<extra></extra>'
    ))

    # Optimum band
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=t3_values,
        mode='lines', name='Optimum',
        line=dict(color=BOUNDARY_LINE_COLOR, width=LINE_WIDTH, shape=LINE_SHAPE),
        fill='tonexty', fillcolor=LNC_BAND_COLORS['Optimum'],
        hovertemplate='Optimum/High boundary: %{y:.2f}%<extra></extra>'
    ))

    # High band
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=t4_values,
        mode='lines', name='High',
        line=dict(color=BOUNDARY_LINE_COLOR, width=LINE_WIDTH, shape=LINE_SHAPE),
        fill='tonexty', fillcolor=LNC_BAND_COLORS['High'],
        hovertemplate='High/Excess boundary: %{y:.2f}%<extra></extra>'
    ))

    # Excess band (ceiling)
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=[4.2] * len(monthly_dates),
        mode='lines', name='Excess',
        line=dict(width=0, shape=LINE_SHAPE),
        fill='tonexty', fillcolor=LNC_BAND_COLORS['Excess'],
        showlegend=True, hoverinfo='skip'
    ))

    # Add treatment observations
    for treatment in TREATMENT_ORDER:
        trt_df = df[df['treatment'] == treatment].copy()
        if len(trt_df) > 0:
            trt_df['normalized_date'] = trt_df['parsed_date'].apply(lambda d: d.replace(day=15))
            monthly_avg = trt_df.groupby('normalized_date')['N_Value'].mean().reset_index()
            monthly_avg = monthly_avg.sort_values('normalized_date')

            fig.add_trace(go.Scatter(
                x=monthly_avg['normalized_date'],
                y=monthly_avg['N_Value'],
                mode='lines+markers',
                name=treatment,
                line=dict(color=TREATMENT_COLORS[treatment], width=2),
                marker=dict(size=6),
                hovertemplate=f'{treatment}<br>%{{x|%B %Y}}<br>N: %{{y:.2f}}%<extra></extra>'
            ))

    # Add year boundary marker
    fig.add_shape(
        type="line",
        x0='2023-08-01', x1='2023-08-01',
        y0=1.5, y1=4.2,
        line=dict(color="black", width=1.5, dash="dash")
    )
    fig.add_annotation(
        x='2023-08-01', y=4.1,
        text="August 2023",
        showarrow=False,
        font=dict(size=10, color="black")
    )

    fig.update_layout(
        title=dict(
            text="5.2 LNC Timeline with Dynamic Thresholds: N60+ Treatments Remain in Optimum Band<br><sup>Threshold bands follow seasonal adjustment factors | N60, N100, N150 converge in green Optimum zone throughout 2 years</sup>",
            font=dict(size=16)
        ),
        xaxis=dict(
            title="Date",
            tickformat='%b %Y',
            dtick='M2',
            range=[min_date, max_date]
        ),
        yaxis=dict(
            title="N_Value (%)",
            range=[1.5, 4.2]
        ),
        height=700,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified'
    )

    return fig


# =============================================================================
# HTML REPORT GENERATION
# =============================================================================

def generate_html_report(df):
    """Generate the complete HTML report."""
    print("Generating visualizations...")

    # Create all components
    thresholds_table = create_thresholds_table()
    fig_classification = create_lnc_classification_chart(df)

    # Convert to HTML
    plot_classification = fig_classification.to_html(full_html=False, include_plotlyjs='cdn')

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 5: LNC Classification</title>
    {HTML_STYLE}
</head>
<body>
    <h1>LNC (Leaf Nitrogen Content) Classification:<br>Dynamic Thresholds Reveal All N60+ Treatments Stay Optimum</h1>
    <p class="subtitle">UC Davis October thresholds adapted to monthly values using seasonal adjustment factors | N60, N100, N150 all cluster in Optimum band</p>

    <div class="analysis-section">
        {thresholds_table}
    </div>

    <div class="analysis-section">
        {plot_classification}
    </div>
</body>
</html>"""

    return html_content


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Generating Visualization 5: LNC Status Classification")
    print("=" * 70)

    # Load data
    df = load_npk_data()

    # Generate report
    html_content = generate_html_report(df)

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'lnc_classification.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nSaved to: {output_path}")
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
