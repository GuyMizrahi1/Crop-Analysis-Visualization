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

# Colors for the three metrics (Gray + Green Accent - matches theme)
N_COLOR = '#BDBDBD'       # Light gray - subtle background
ST_COLOR = '#424242'      # Dark gray - higher contrast from N
RATIO_COLOR = '#228B22'   # Forest green - matches theme title color

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
        x0='2023-12-05', x1='2024-01-23',
        fillcolor='rgba(135, 206, 250, 0.2)',
        layer='below',
        line_width=0
    )
    fig.add_annotation(
        x='2024-01-01', y=108,
        text="Winter Window",
        showarrow=False,
        font=dict(size=10, color='#4682B4')
    )

    # Window 2: April (spring flush)
    fig.add_vrect(
        x0='2024-04-01', x1='2024-06-01',
        fillcolor='rgba(255, 215, 0, 0.2)',
        layer='below',
        line_width=0
    )
    fig.add_annotation(
        x='2024-05-01', y=108,
        text="Spring Window",
        showarrow=False,
        font=dict(size=10, color='#8B6914')
    )

    # Window 3: August (summer growth)
    fig.add_vrect(
        x0='2024-07-29', x1='2024-08-25',
        fillcolor='rgba(255, 160, 122, 0.2)',
        layer='below',
        line_width=0
    )
    fig.add_annotation(
        x='2024-08-11', y=108,
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
        name='N/ST Ratio',
        line=dict(color=RATIO_COLOR, width=5),
        marker=dict(size=14, symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate='<b>N/ST Ratio: %{customdata:.4f}</b><extra></extra>',
        customdata=monthly_avg['N_ST_Ratio']
    ))

    fig.update_layout(
        title=dict(
            text="N/ST Ratio: Key Indicator for Phenological Fertilization Timing<br><sup>Three fertilization windows match citrus growth phases: Winter (Dec-Jan), Spring (Apr-May), Summer (Aug)</sup>",
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
            yanchor='top',
            y=-0.12,
            xanchor='center',
            x=0.5,
            font=dict(size=13),
            bgcolor='rgba(255,255,255,0.8)'
        ),
        margin=dict(b=80),
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


def create_triple_axis_chart(df):
    """Create triple y-axis chart with actual (non-normalized) values.

    - Left y-axis: N Value (%)
    - Right y-axis 1: ST Value (mg/g)
    - Right y-axis 2: N/ST Ratio
    """
    monthly_avg = get_monthly_averages(df)

    fig = go.Figure()

    # N Value (left y-axis)
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['N_Value'],
        mode='lines+markers',
        name='N Value (%)',
        line=dict(color=N_COLOR, width=3),
        marker=dict(size=10),
        yaxis='y1',
        hovertemplate='N: %{y:.2f}%<extra></extra>'
    ))

    # ST Value (right y-axis 1)
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['ST_Value'],
        mode='lines+markers',
        name='ST Value (mg/g)',
        line=dict(color=ST_COLOR, width=3),
        marker=dict(size=10),
        yaxis='y2',
        hovertemplate='ST: %{y:.1f} mg/g<extra></extra>'
    ))

    # N/ST Ratio (right y-axis 2)
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['N_ST_Ratio'],
        mode='lines+markers',
        name='N/ST Ratio \u2605',
        line=dict(color=RATIO_COLOR, width=4),
        marker=dict(size=14, symbol='diamond', line=dict(width=2, color='white')),
        yaxis='y3',
        hovertemplate='<b>N/ST: %{y:.4f}</b><extra></extra>'
    ))

    # Find and mark peaks in N/ST ratio
    ratio_values = monthly_avg['N_ST_Ratio'].values
    dates = monthly_avg['normalized_date'].values
    for i in range(1, len(ratio_values) - 1):
        if ratio_values[i] > ratio_values[i-1] and ratio_values[i] > ratio_values[i+1]:
            fig.add_annotation(
                x=dates[i],
                y=ratio_values[i],
                yref='y3',
                text=f"\u25B2 Peak",
                showarrow=True,
                arrowhead=2,
                arrowcolor=RATIO_COLOR,
                font=dict(size=10, color=RATIO_COLOR),
                yshift=15
            )

    fig.update_layout(
        title=dict(
            text="6.2 Triple Y-Axis: Actual Values (Non-Normalized)<br><sup>Each metric on its own scale | Peaks marked on N/ST ratio</sup>",
            font=dict(size=16)
        ),
        xaxis=dict(
            title='Date',
            tickformat='%b %Y',
            dtick='M1',
            domain=[0.1, 0.85]
        ),
        yaxis=dict(
            title=dict(text='N Value (%)', font=dict(color=N_COLOR)),
            tickfont=dict(color=N_COLOR),
            side='left',
            position=0.05
        ),
        yaxis2=dict(
            title=dict(text='ST Value (mg/g)', font=dict(color=ST_COLOR)),
            tickfont=dict(color=ST_COLOR),
            overlaying='y',
            side='right',
            position=0.9
        ),
        yaxis3=dict(
            title=dict(text='N/ST Ratio', font=dict(color=RATIO_COLOR)),
            tickfont=dict(color=RATIO_COLOR),
            overlaying='y',
            side='right',
            position=0.97
        ),
        height=550,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.12,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        margin=dict(r=100, b=100)
    )

    return fig


def create_peak_annotated_chart(df):
    """Create chart highlighting N/ST ratio peaks with gradient direction arrows."""
    monthly_avg = get_monthly_averages(df)

    # Normalize for comparison
    monthly_avg['N_norm'] = normalize(monthly_avg['N_Value'])
    monthly_avg['ST_norm'] = normalize(monthly_avg['ST_Value'])
    monthly_avg['Ratio_norm'] = normalize(monthly_avg['N_ST_Ratio'])

    fig = go.Figure()

    # Add shaded regions where N_norm > ST_norm (indicating high ratio periods)
    dates = monthly_avg['normalized_date'].tolist()
    n_norm = monthly_avg['N_norm'].tolist()
    st_norm = monthly_avg['ST_norm'].tolist()

    # Find crossover regions
    for i in range(len(dates) - 1):
        if n_norm[i] > st_norm[i]:
            fig.add_vrect(
                x0=dates[i],
                x1=dates[i+1] if i+1 < len(dates) else dates[i],
                fillcolor='rgba(231, 76, 60, 0.15)',
                layer='below',
                line_width=0
            )

    # N Value (normalized)
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['N_norm'],
        mode='lines+markers',
        name='N Value (normalized)',
        line=dict(color=N_COLOR, width=2, dash='dot'),
        marker=dict(size=6),
        opacity=0.8,
        hovertemplate='N: %{customdata:.2f}%<extra></extra>',
        customdata=monthly_avg['N_Value']
    ))

    # ST Value (normalized)
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['ST_norm'],
        mode='lines+markers',
        name='ST Value (normalized)',
        line=dict(color=ST_COLOR, width=2, dash='dot'),
        marker=dict(size=6),
        opacity=0.8,
        hovertemplate='ST: %{customdata:.1f} mg/g<extra></extra>',
        customdata=monthly_avg['ST_Value']
    ))

    # N/ST Ratio (normalized) - prominent
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['Ratio_norm'],
        mode='lines+markers',
        name='N/ST Ratio \u2605',
        line=dict(color=RATIO_COLOR, width=5),
        marker=dict(size=14, symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate='<b>N/ST: %{customdata:.4f}</b><extra></extra>',
        customdata=monthly_avg['N_ST_Ratio']
    ))

    # Find and annotate peaks with actual ratio values
    ratio_norm = monthly_avg['Ratio_norm'].values
    ratio_actual = monthly_avg['N_ST_Ratio'].values
    dates = monthly_avg['normalized_date'].values

    for i in range(1, len(ratio_norm) - 1):
        if ratio_norm[i] > ratio_norm[i-1] and ratio_norm[i] > ratio_norm[i+1]:
            month_name = pd.Timestamp(dates[i]).strftime('%b')
            fig.add_annotation(
                x=dates[i],
                y=ratio_norm[i],
                text=f"<b>PEAK</b><br>{month_name}<br>N/ST={ratio_actual[i]:.3f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=RATIO_COLOR,
                font=dict(size=11, color=RATIO_COLOR),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor=RATIO_COLOR,
                borderwidth=1,
                yshift=30
            )

    fig.update_layout(
        title=dict(
            text="6.3 Peak Detection: When N/ST Ratio Reaches Maximum<br><sup>Red shaded = N higher than ST (normalized) | Peak annotations show actual ratio values</sup>",
            font=dict(size=16)
        ),
        xaxis=dict(
            title='Date',
            tickformat='%b %Y',
            dtick='M1'
        ),
        yaxis=dict(
            title='Normalized Value (%)',
            range=[-5, 130]
        ),
        height=550,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.12,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        margin=dict(b=100)
    )

    return fig


def create_ratio_focused_chart(df):
    """Create chart focused on N/ST ratio with N and ST as context lines."""
    monthly_avg = get_monthly_averages(df)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # N/ST Ratio as main focus (left y-axis) - as area fill
    fig.add_trace(
        go.Scatter(
            x=monthly_avg['normalized_date'],
            y=monthly_avg['N_ST_Ratio'],
            mode='lines',
            name='N/ST Ratio',
            line=dict(color=RATIO_COLOR, width=4),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.3)',
            hovertemplate='<b>N/ST: %{y:.4f}</b><extra></extra>'
        ),
        secondary_y=False
    )

    # Add peak markers
    ratio_values = monthly_avg['N_ST_Ratio'].values
    dates = monthly_avg['normalized_date'].values
    peak_dates = []
    peak_values = []

    for i in range(1, len(ratio_values) - 1):
        if ratio_values[i] > ratio_values[i-1] and ratio_values[i] > ratio_values[i+1]:
            peak_dates.append(dates[i])
            peak_values.append(ratio_values[i])

    fig.add_trace(
        go.Scatter(
            x=peak_dates,
            y=peak_values,
            mode='markers+text',
            name='Ratio Peaks',
            marker=dict(size=20, color=RATIO_COLOR, symbol='star', line=dict(width=2, color='white')),
            text=[f'{v:.3f}' for v in peak_values],
            textposition='top center',
            textfont=dict(size=12, color=RATIO_COLOR),
            hovertemplate='<b>PEAK: %{y:.4f}</b><extra></extra>'
        ),
        secondary_y=False
    )

    # N Value (right y-axis) - subtle context
    fig.add_trace(
        go.Scatter(
            x=monthly_avg['normalized_date'],
            y=monthly_avg['N_Value'],
            mode='lines+markers',
            name='N Value (%)',
            line=dict(color=N_COLOR, width=2, dash='dot'),
            marker=dict(size=6),
            opacity=0.6,
            hovertemplate='N: %{y:.2f}%<extra></extra>'
        ),
        secondary_y=True
    )

    # ST Value (right y-axis, scaled) - subtle context
    st_scaled = monthly_avg['ST_Value'] / 50  # Scale to fit with N%
    fig.add_trace(
        go.Scatter(
            x=monthly_avg['normalized_date'],
            y=st_scaled,
            mode='lines+markers',
            name='ST Value (\u00f750)',
            line=dict(color=ST_COLOR, width=2, dash='dot'),
            marker=dict(size=6),
            opacity=0.6,
            customdata=monthly_avg['ST_Value'],
            hovertemplate='ST: %{customdata:.1f} mg/g<extra></extra>'
        ),
        secondary_y=True
    )

    fig.update_layout(
        title=dict(
            text="6.4 N/ST Ratio Focus: Peak Identification<br><sup>Area shows ratio magnitude | Stars mark local maxima | Dotted lines show N and ST context</sup>",
            font=dict(size=16)
        ),
        xaxis=dict(title='Date', tickformat='%b %Y', dtick='M1'),
        height=550,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.12,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        margin=dict(b=100)
    )

    fig.update_yaxes(title_text="N/ST Ratio", secondary_y=False, color=RATIO_COLOR)
    fig.update_yaxes(title_text="N (%) / ST (\u00f750)", secondary_y=True, color='gray')

    return fig


# =============================================================================
# HTML REPORT GENERATION
# =============================================================================

def generate_html_report(df):
    """Generate the complete HTML report with single visualization and detailed explanations."""
    print("Generating visualizations...")

    # Create single normalized chart
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
    <p class="subtitle">Fertilize at ratio peaks (gradient changes + &rarr; -) | Peaks = high Nitrogen relative to depleted Starch</p>

    <div class="analysis-section">
        <div class="insight-box" style="margin-bottom: 15px; padding: 12px; background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-left: 4px solid #e74c3c; border-radius: 4px;">
            <strong style="color: #c0392b;">Why Fertilize at Peaks?</strong><br>
            Ratio peaks indicate starch depletion relative to nitrogen - the tree is investing reserves in growth.<br>
            Fertilizing now replenishes nutrients when uptake is most efficient.
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px; font-size: 0.85em;">
            <div style="background: rgba(135, 206, 250, 0.2); padding: 8px; border-radius: 6px; border-left: 3px solid #4682B4;">
                <strong style="color: #4682B4;">Winter (Dec-Jan)</strong><br>
                N &uarr; (remobilization) | ST &darr; &rarr; Ratio rises
            </div>
            <div style="background: rgba(255, 215, 0, 0.2); padding: 8px; border-radius: 6px; border-left: 3px solid #8B6914;">
                <strong style="color: #8B6914;">Spring (Apr-May) - Peak</strong><br>
                N &darr; | ST &darr;&darr; (flowering) &rarr; Highest peak
            </div>
            <div style="background: rgba(255, 160, 122, 0.2); padding: 8px; border-radius: 6px; border-left: 3px solid #CD5C5C;">
                <strong style="color: #CD5C5C;">Summer (Aug)</strong><br>
                N &uarr; (uptake) | ST low &rarr; Ratio rises
            </div>
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
