"""
Visualization 6: N/ST Ratio Analysis

This visualization demonstrates why the N/ST ratio outperforms nitrogen alone
for fertilization timing decisions. It shows:
1. Normalized comparison for recent period (Aug 2023 - Aug 2024)
2. Dual-axis view showing actual values

Author: Data Science Visualization Course Project
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime

# Add shared config to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import (
    HTML_STYLE, NPK_DATASET_PATH
)

# Colors for the three metrics
N_COLOR = '#2980b9'       # Strong blue
ST_COLOR = '#27ae60'      # Strong green
RATIO_COLOR = '#e74c3c'   # Strong red/orange

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

    # Filter to Sep 2023 - Aug 2024 (full phenological cycle)
    start_date = pd.Timestamp('2023-09-01')
    end_date = pd.Timestamp('2024-08-31')
    df = df[(df['parsed_date'] >= start_date) & (df['parsed_date'] <= end_date)]

    print(f"Loaded {len(df)} NPK samples (Sep 2023 - Aug 2024)")
    return df


def get_monthly_averages(df):
    """Calculate monthly averages for N, ST, and N/ST ratio."""
    df_copy = df.copy()
    df_copy['normalized_date'] = df_copy['parsed_date'].apply(lambda d: d.replace(day=15))

    monthly_avg = df_copy.groupby('normalized_date').agg({
        'N_Value': 'mean',
        'ST_Value': 'mean'
    }).reset_index()
    monthly_avg = monthly_avg.sort_values('normalized_date')
    monthly_avg['N_ST_Ratio'] = monthly_avg['N_Value'] / monthly_avg['ST_Value']

    return monthly_avg


def normalize(series):
    """Normalize series to 0-100 range."""
    if series.max() == series.min():
        return series * 0 + 50
    return (series - series.min()) / (series.max() - series.min()) * 100


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_normalized_chart(df):
    """Create clean normalized view for phenological cycle (Sep 2023 - Aug 2024).

    Simplified design with prominent N/ST Ratio curve as the main visual focus.
    Shows three fertilization windows matching citrus phenology.
    """
    monthly_avg = get_monthly_averages(df)

    # Normalize
    monthly_avg['N_norm'] = normalize(monthly_avg['N_Value'])
    monthly_avg['ST_norm'] = normalize(monthly_avg['ST_Value'])
    monthly_avg['Ratio_norm'] = normalize(monthly_avg['N_ST_Ratio'])

    fig = go.Figure()

    # Add three fertilization windows based on citrus phenology
    # Window 1: December (winter dormancy break)
    fig.add_vrect(
        x0='2023-11-15', x1='2024-01-15',
        fillcolor='rgba(135, 206, 250, 0.2)',
        layer='below',
        line_width=0
    )
    fig.add_annotation(
        x='2023-12-15', y=108,
        text="Winter Window",
        showarrow=False,
        font=dict(size=10, color='#4682B4')
    )

    # Window 2: April (spring flush)
    fig.add_vrect(
        x0='2024-03-15', x1='2024-05-15',
        fillcolor='rgba(255, 215, 0, 0.2)',
        layer='below',
        line_width=0
    )
    fig.add_annotation(
        x='2024-04-15', y=108,
        text="Spring Window",
        showarrow=False,
        font=dict(size=10, color='#8B6914')
    )

    # Window 3: August (summer growth)
    fig.add_vrect(
        x0='2024-07-15', x1='2024-09-15',
        fillcolor='rgba(255, 160, 122, 0.2)',
        layer='below',
        line_width=0
    )
    fig.add_annotation(
        x='2024-08-15', y=108,
        text="Summer Window",
        showarrow=False,
        font=dict(size=10, color='#CD5C5C')
    )

    # N Value (normalized) - subtle/thin
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['N_norm'],
        mode='lines+markers',
        name='N Value (%)',
        line=dict(color=N_COLOR, width=2, dash='dot'),
        marker=dict(size=5),
        opacity=0.7,
        hovertemplate='N: %{customdata:.2f}%<extra></extra>',
        customdata=monthly_avg['N_Value']
    ))

    # ST Value (normalized) - subtle/thin
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['ST_norm'],
        mode='lines+markers',
        name='ST Value (mg/g)',
        line=dict(color=ST_COLOR, width=2, dash='dot'),
        marker=dict(size=5),
        opacity=0.7,
        hovertemplate='ST: %{customdata:.1f} mg/g<extra></extra>',
        customdata=monthly_avg['ST_Value']
    ))

    # N/ST Ratio (normalized) - THE PROMINENT CURVE
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['Ratio_norm'],
        mode='lines+markers',
        name='N/ST Ratio ★',
        line=dict(color=RATIO_COLOR, width=5),
        marker=dict(size=14, symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate='<b>N/ST Ratio: %{customdata:.4f}</b><extra></extra>',
        customdata=monthly_avg['N_ST_Ratio']
    ))

    fig.update_layout(
        title=dict(
            text="N/ST Ratio: Key Indicator for Phenological Fertilization Timing<br><sup>Three fertilization windows match citrus growth phases: Winter (Dec), Spring (Apr), Summer (Aug)</sup>",
            font=dict(size=16)
        ),
        xaxis=dict(
            title='Date',
            tickformat='%b %Y',
            dtick='M1',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title='Normalized Value (%)',
            range=[-5, 115],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        height=550,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=13),
            bgcolor='rgba(255,255,255,0.8)'
        ),
        hovermode='x unified',
        plot_bgcolor='white'
    )

    return fig


def create_dual_axis_chart(df):
    """Create dual-axis view showing actual values."""
    monthly_avg = get_monthly_averages(df)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add fertilization window shading
    fig.add_vrect(
        x0='2024-04-01', x1='2024-07-31',
        fillcolor='rgba(255, 200, 100, 0.3)',
        layer='below',
        line_width=0,
    )

    # N Value (left y-axis)
    fig.add_trace(
        go.Scatter(
            x=monthly_avg['normalized_date'],
            y=monthly_avg['N_Value'],
            mode='lines+markers',
            name='N Value (%)',
            line=dict(color=N_COLOR, width=3),
            marker=dict(size=8),
            hovertemplate='N: %{y:.2f}%<extra></extra>'
        ),
        secondary_y=False
    )

    # ST Value (right y-axis)
    fig.add_trace(
        go.Scatter(
            x=monthly_avg['normalized_date'],
            y=monthly_avg['ST_Value'],
            mode='lines+markers',
            name='ST Value (mg/g)',
            line=dict(color=ST_COLOR, width=3),
            marker=dict(size=8),
            hovertemplate='ST: %{y:.1f} mg/g<extra></extra>'
        ),
        secondary_y=True
    )

    # N/ST Ratio as bar chart overlay (scaled to fit)
    ratio_scaled = monthly_avg['N_ST_Ratio'] * 100  # Scale for visibility
    fig.add_trace(
        go.Bar(
            x=monthly_avg['normalized_date'],
            y=ratio_scaled,
            name='N/ST Ratio (×100)',
            marker=dict(color=RATIO_COLOR, opacity=0.4),
            hovertemplate='N/ST: %{customdata:.4f}<extra></extra>',
            customdata=monthly_avg['N_ST_Ratio'],
            width=1000000000 * 20  # Width in milliseconds for monthly bars
        ),
        secondary_y=False
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text="6.2 Actual Values: N% and ST Follow Different Seasonal Patterns<br><sup>Left axis: N% and N/ST ratio (×100) | Right axis: ST (mg/g) | Yellow zone = fertilization window</sup>",
            font=dict(size=16)
        ),
        xaxis=dict(title='Date', tickformat='%b %Y', dtick='M1'),
        height=500,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        barmode='overlay'
    )

    # Update y-axes
    fig.update_yaxes(title_text="N Value (%) / N÷ST Ratio (×100)", secondary_y=False, color=N_COLOR)
    fig.update_yaxes(title_text="ST Value (mg/g)", secondary_y=True, color=ST_COLOR)

    return fig


# =============================================================================
# HTML REPORT GENERATION
# =============================================================================

def generate_html_report(df):
    """Generate the complete HTML report with single clean visualization."""
    print("Generating visualizations...")

    # Create single clean figure
    fig_normalized = create_normalized_chart(df)

    # Convert to HTML
    plot_normalized = fig_normalized.to_html(full_html=False, include_plotlyjs='cdn')

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 6: N/ST Ratio Analysis</title>
    {HTML_STYLE}
</head>
<body>
    <h1>N/ST Ratio: Phenology-Based Fertilization Indicator</h1>
    <p class="subtitle">Three fertilization windows aligned with citrus growth phases: December (dormancy break), April (spring flush), August (summer growth)</p>

    <div class="analysis-section">
        <div class="insight-box" style="margin-bottom: 20px; padding: 15px; background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-left: 4px solid #e74c3c; border-radius: 4px;">
            <strong style="color: #c0392b;">Key Insight:</strong> The N/ST ratio responds to phenological stages rather than calendar seasons. Local maxima in the ratio align with citrus growth phases, identifying optimal fertilization windows in December (post-dormancy), April (spring flush), and August (fruit development).
        </div>
        {plot_normalized}
    </div>
</body>
</html>"""

    return html_content


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Generating Visualization 6: N/ST Ratio Analysis")
    print("=" * 70)

    # Load data
    df = load_npk_data()

    # Generate report
    html_content = generate_html_report(df)

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'nst_ratio_analysis.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nSaved to: {output_path}")
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
