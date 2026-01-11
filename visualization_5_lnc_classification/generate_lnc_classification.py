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
    """Create UC Davis thresholds table with corrected colors."""
    table_html = '''
    <table class="treatment-table" style="width: 80%; margin: 20px auto;">
        <tr>
            <th>LNC Category</th>
            <th>October Threshold</th>
            <th>Description</th>
            <th>Agronomic Implication</th>
        </tr>
        <tr style="background: rgba(30, 144, 255, 0.3);">
            <td style="font-weight: bold; color: #1E90FF;">Deficient</td>
            <td>&lt; 2.64%</td>
            <td>Severe nitrogen deficiency</td>
            <td>Immediate fertilization required</td>
        </tr>
        <tr style="background: rgba(135, 206, 250, 0.3);">
            <td style="font-weight: bold; color: #87CEEB;">Low</td>
            <td>2.64 - 2.88%</td>
            <td>Suboptimal nitrogen levels</td>
            <td>Consider supplemental fertilization</td>
        </tr>
        <tr style="background: rgba(78, 205, 196, 0.3);">
            <td style="font-weight: bold; color: #4ECDC4;">Optimum</td>
            <td>2.88 - 3.24%</td>
            <td>Ideal range for citrus</td>
            <td>Maintain current program</td>
        </tr>
        <tr style="background: rgba(255, 165, 0, 0.3);">
            <td style="font-weight: bold; color: #FFA500;">High</td>
            <td>3.24 - 3.48%</td>
            <td>Above optimal</td>
            <td>Monitor, may reduce fertilization</td>
        </tr>
        <tr style="background: rgba(255, 107, 107, 0.3);">
            <td style="font-weight: bold; color: #FF6B6B;">Excess</td>
            <td>&gt; 3.48%</td>
            <td>Excessive nitrogen</td>
            <td>Reduce fertilization to avoid waste</td>
        </tr>
    </table>
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

    BOUNDARY_LINE_COLOR = 'rgba(60, 60, 60, 0.7)'
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
        mode='lines', name='Deficient (< 2.64%)',
        line=dict(color=BOUNDARY_LINE_COLOR, width=1.5, shape=LINE_SHAPE),
        fill='tonexty', fillcolor=LNC_BAND_COLORS['Deficient'],
        hovertemplate='Deficient/Low boundary: %{y:.2f}%<extra></extra>'
    ))

    # Low band
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=t2_values,
        mode='lines', name='Low (2.64-2.88%)',
        line=dict(color=BOUNDARY_LINE_COLOR, width=1.5, shape=LINE_SHAPE),
        fill='tonexty', fillcolor=LNC_BAND_COLORS['Low'],
        hovertemplate='Low/Optimum boundary: %{y:.2f}%<extra></extra>'
    ))

    # Optimum band
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=t3_values,
        mode='lines', name='Optimum (2.88-3.24%)',
        line=dict(color=BOUNDARY_LINE_COLOR, width=1.5, shape=LINE_SHAPE),
        fill='tonexty', fillcolor=LNC_BAND_COLORS['Optimum'],
        hovertemplate='Optimum/High boundary: %{y:.2f}%<extra></extra>'
    ))

    # High band
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=t4_values,
        mode='lines', name='High (3.24-3.48%)',
        line=dict(color=BOUNDARY_LINE_COLOR, width=1.5, shape=LINE_SHAPE),
        fill='tonexty', fillcolor=LNC_BAND_COLORS['High'],
        hovertemplate='High/Excess boundary: %{y:.2f}%<extra></extra>'
    ))

    # Excess band (ceiling)
    fig.add_trace(go.Scatter(
        x=monthly_dates, y=[4.2] * len(monthly_dates),
        mode='lines', name='Excess (> 3.48%)',
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
            text="5.2 LNC Status Classification (Aug 2022 - Aug 2024)<br><sup>UC Davis October thresholds scaled by seasonal pattern | Actual observations shown</sup>",
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
    seasonal_table = create_seasonal_factors_table()
    fig_classification = create_lnc_classification_chart(df)

    # Convert to HTML
    plot_classification = fig_classification.to_html(full_html=False, include_plotlyjs='cdn')

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 5: LNC Status Classification</title>
    {HTML_STYLE}
</head>
<body>
    <h1>LNC Status Classification</h1>
    <p class="subtitle">Leaf Nitrogen Content assessment using UC Davis thresholds</p>

    <div class="intro-box">
        <h3 style="margin-top: 0; border: none; padding-left: 0;">Understanding LNC Classification</h3>
        <p><strong>Leaf Nitrogen Content (LNC)</strong> is the standard measure for assessing plant nitrogen status.
        The University of California, Davis has established reference thresholds for citrus based on
        extensive research and field trials.</p>

        <p>These thresholds vary seasonally due to:</p>
        <ul>
            <li><strong>Dilution effect:</strong> Rapid leaf growth in spring dilutes nitrogen concentration</li>
            <li><strong>Concentration effect:</strong> Slower growth in winter concentrates nitrogen</li>
            <li><strong>Phenological timing:</strong> Nitrogen demand varies with growth stages</li>
        </ul>
    </div>

    <h2>5.1 UC Davis Thresholds</h2>

    <div class="analysis-section">
        <p>The following thresholds are based on October reference values (when seasonal variation is minimal):</p>
        {thresholds_table}

        <div class="methodology">
            <h4>Color Coding Rationale</h4>
            <ul>
                <li><span style="color: #1E90FF; font-weight: bold;">Blue = Deficient/Low</span> - Cold colors indicate deficiency, signaling need for action</li>
                <li><span style="color: #4ECDC4; font-weight: bold;">Teal = Optimum</span> - Calm, balanced color for ideal status</li>
                <li><span style="color: #FFA500; font-weight: bold;">Orange = High</span> - Warm colors indicate excess</li>
                <li><span style="color: #FF6B6B; font-weight: bold;">Red = Excess</span> - Alert color for over-fertilization</li>
            </ul>
        </div>
    </div>

    <h3>Seasonal Adjustment Factors</h3>

    <div class="analysis-section">
        <p>Thresholds are adjusted monthly based on seasonal nitrogen dynamics:</p>
        {seasonal_table}

        <div class="key-observations">
            <h4>Seasonal Pattern</h4>
            <ul>
                <li><strong>Winter (Dec-Feb):</strong> Factors ~1.08-1.12 (higher thresholds)</li>
                <li><strong>Spring (Mar-May):</strong> Factors ~0.91-1.02 (lower thresholds, especially May)</li>
                <li><strong>Summer (Jun-Aug):</strong> Factors ~0.92-1.02 (variable)</li>
                <li><strong>Fall (Sep-Nov):</strong> Factors ~1.00-1.09 (returning to baseline)</li>
            </ul>
        </div>
    </div>

    <h2>5.2 LNC Status Classification</h2>

    <div class="analysis-section">
        <p>The following visualization shows how each treatment group's nitrogen levels compare
        against the seasonally-adjusted UC Davis thresholds:</p>
        {plot_classification}

        <div class="key-observations">
            <h4>Key Observations</h4>
            <ul>
                <li><strong>Ceiling Effect:</strong> High-N treatments (N100, N150) cluster together in the Excess zone,
                suggesting a physiological upper limit to nitrogen accumulation in leaves regardless of fertilization rate</li>
                <li><strong>Treatment Separation:</strong> Lower treatments (N10, N40, N60) show clearer differentiation,
                with N10 occasionally dropping into the Low/Optimum zones during spring months</li>
                <li><strong>Seasonal Wave:</strong> All treatments follow the same seasonal wave pattern - higher in winter,
                lower in spring/early summer - validating the seasonal adjustment approach</li>
                <li><strong>Optimum Range:</strong> N60 (the agronomic optimum treatment) largely stays within or
                above the Optimum range throughout the year</li>
            </ul>
        </div>
    </div>

    <div class="warning-box">
        <h4>Limitation of LNC-Only Assessment</h4>
        <p>While LNC classification is valuable, it has an important limitation:</p>
        <p><strong>LNC peaks in winter</strong> when leaf growth slows, not necessarily when the plant
        needs fertilization. This "concentration effect" can be misleading for fertilization timing decisions.</p>
        <p>This is why we explore the <strong>N/ST ratio</strong> in the next visualization - it combines
        nitrogen status with starch reserves to provide a more complete picture of plant metabolic status.</p>
    </div>

    <div class="discovery-box">
        <h3>Summary: LNC Classification Insights</h3>
        <ul>
            <li><strong>UC Davis thresholds are reliable</strong> when adjusted for seasonal patterns</li>
            <li><strong>Treatment response is clear:</strong> Higher N fertilization → higher LNC (up to a ceiling)</li>
            <li><strong>Seasonal adjustment is essential:</strong> Raw LNC values without seasonal context can mislead</li>
            <li><strong>LNC alone is insufficient:</strong> For fertilization timing, we need additional metrics like the N/ST ratio</li>
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
