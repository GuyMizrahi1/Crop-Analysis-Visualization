"""
Visualization 6: N/ST Ratio Analysis

This visualization demonstrates why the N/ST ratio outperforms nitrogen alone
for fertilization timing decisions. It shows:
1. Normalized comparison (0-100%) for full period
2. Normalized comparison for recent period (excluding 2022 anomaly)
3. Key observations on timing patterns

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
    HTML_STYLE, NPK_DATASET_PATH
)

# Colors for the three metrics
N_COLOR = '#7fb3d5'       # Muted blue
ST_COLOR = '#82c982'      # Muted green
RATIO_COLOR = '#ff8c00'   # Bright orange

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

def create_normalized_full_period(df):
    """Create normalized view for full period (Aug 2022 - Aug 2024)."""
    monthly_avg = get_monthly_averages(df)

    # Normalize
    monthly_avg['N_norm'] = normalize(monthly_avg['N_Value'])
    monthly_avg['ST_norm'] = normalize(monthly_avg['ST_Value'])
    monthly_avg['Ratio_norm'] = normalize(monthly_avg['N_ST_Ratio'])

    fig = go.Figure()

    # N Value (normalized)
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['N_norm'],
        mode='lines+markers',
        name='N Value',
        line=dict(color=N_COLOR, width=2),
        marker=dict(size=6),
        hovertemplate='N: %{customdata:.2f}% (norm: %{y:.0f}%)<extra></extra>',
        customdata=monthly_avg['N_Value']
    ))

    # ST Value (normalized)
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['ST_norm'],
        mode='lines+markers',
        name='ST Value',
        line=dict(color=ST_COLOR, width=2),
        marker=dict(size=6),
        hovertemplate='ST: %{customdata:.1f} mg/g (norm: %{y:.0f}%)<extra></extra>',
        customdata=monthly_avg['ST_Value']
    ))

    # N/ST Ratio (normalized) - PROMINENT
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['Ratio_norm'],
        mode='lines+markers',
        name='N/ST Ratio',
        line=dict(color=RATIO_COLOR, width=4),
        marker=dict(size=9, symbol='diamond'),
        hovertemplate='N/ST: %{customdata:.4f} (norm: %{y:.0f}%)<extra></extra>',
        customdata=monthly_avg['N_ST_Ratio']
    ))

    # Add year boundary
    fig.add_shape(
        type="line",
        x0='2023-08-01', x1='2023-08-01',
        y0=0, y1=100,
        line=dict(color="black", width=1.5, dash="dash")
    )

    # Annotations
    n_peak_idx = monthly_avg['N_norm'].idxmax()
    ratio_peak_idx = monthly_avg['Ratio_norm'].idxmax()

    fig.add_annotation(
        x=monthly_avg.loc[n_peak_idx, 'normalized_date'],
        y=100,
        text="N peaks here",
        showarrow=True, arrowhead=2, ax=0, ay=20,
        font=dict(size=10, color=N_COLOR)
    )

    fig.add_annotation(
        x=monthly_avg.loc[ratio_peak_idx, 'normalized_date'],
        y=monthly_avg.loc[ratio_peak_idx, 'Ratio_norm'],
        text="Ratio peaks here →<br>Fertilization window",
        showarrow=True, arrowhead=2, ax=-60, ay=-30,
        font=dict(size=10, color=RATIO_COLOR)
    )

    fig.update_layout(
        title=dict(
            text="Normalized View - Full Period (Aug 2022 - Aug 2024)<br><sup>All curves scaled to 0-100% for direct timing comparison</sup>",
            font=dict(size=16)
        ),
        xaxis=dict(title='Date', tickformat='%b %Y', dtick='M2'),
        yaxis=dict(title='Normalized Value (%)', range=[0, 105]),
        height=550,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified'
    )

    return fig


def create_normalized_recent_period(df):
    """Create normalized view for recent period (Aug 2023 - Aug 2024)."""
    # Filter to recent period
    start_date = pd.Timestamp('2023-08-01')
    end_date = pd.Timestamp('2024-08-31')
    df_recent = df[(df['parsed_date'] >= start_date) & (df['parsed_date'] <= end_date)].copy()

    monthly_avg = get_monthly_averages(df_recent)

    # Normalize
    monthly_avg['N_norm'] = normalize(monthly_avg['N_Value'])
    monthly_avg['ST_norm'] = normalize(monthly_avg['ST_Value'])
    monthly_avg['Ratio_norm'] = normalize(monthly_avg['N_ST_Ratio'])

    fig = go.Figure()

    # N Value (normalized)
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['N_norm'],
        mode='lines+markers',
        name='N Value',
        line=dict(color=N_COLOR, width=2),
        marker=dict(size=6),
        hovertemplate='N: %{customdata:.2f}% (norm: %{y:.0f}%)<extra></extra>',
        customdata=monthly_avg['N_Value']
    ))

    # ST Value (normalized)
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['ST_norm'],
        mode='lines+markers',
        name='ST Value',
        line=dict(color=ST_COLOR, width=2),
        marker=dict(size=6),
        hovertemplate='ST: %{customdata:.1f} mg/g (norm: %{y:.0f}%)<extra></extra>',
        customdata=monthly_avg['ST_Value']
    ))

    # N/ST Ratio (normalized) - PROMINENT
    fig.add_trace(go.Scatter(
        x=monthly_avg['normalized_date'],
        y=monthly_avg['Ratio_norm'],
        mode='lines+markers',
        name='N/ST Ratio',
        line=dict(color=RATIO_COLOR, width=4),
        marker=dict(size=9, symbol='diamond'),
        hovertemplate='N/ST: %{customdata:.4f} (norm: %{y:.0f}%)<extra></extra>',
        customdata=monthly_avg['N_ST_Ratio']
    ))

    # Find peaks and troughs for annotations
    n_peak_idx = monthly_avg['N_norm'].idxmax()
    st_min_idx = monthly_avg['ST_norm'].idxmin()
    ratio_peak_idx = monthly_avg['Ratio_norm'].idxmax()

    fig.add_annotation(
        x=monthly_avg.loc[n_peak_idx, 'normalized_date'],
        y=monthly_avg.loc[n_peak_idx, 'N_norm'],
        text="N peaks (winter)",
        showarrow=True, arrowhead=2, ax=0, ay=-30,
        font=dict(size=10, color=N_COLOR)
    )

    fig.add_annotation(
        x=monthly_avg.loc[st_min_idx, 'normalized_date'],
        y=monthly_avg.loc[st_min_idx, 'ST_norm'],
        text="ST drops (spring)",
        showarrow=True, arrowhead=2, ax=0, ay=30,
        font=dict(size=10, color=ST_COLOR)
    )

    fig.add_annotation(
        x=monthly_avg.loc[ratio_peak_idx, 'normalized_date'],
        y=monthly_avg.loc[ratio_peak_idx, 'Ratio_norm'],
        text="Ratio rises →<br>Fertilization window",
        showarrow=True, arrowhead=2, ax=-70, ay=-20,
        font=dict(size=10, color=RATIO_COLOR)
    )

    fig.update_layout(
        title=dict(
            text="Normalized View - Recent Period (Aug 2023 - Aug 2024)<br><sup>Excludes 2022 depleted year for cleaner seasonal pattern</sup>",
            font=dict(size=16)
        ),
        xaxis=dict(title='Date', tickformat='%b %Y', dtick='M1'),
        yaxis=dict(title='Normalized Value (%)', range=[0, 105]),
        height=550,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
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

    # Create figures
    fig_full = create_normalized_full_period(df)
    fig_recent = create_normalized_recent_period(df)

    # Convert to HTML
    plot_full = fig_full.to_html(full_html=False, include_plotlyjs='cdn')
    plot_recent = fig_recent.to_html(full_html=False, include_plotlyjs=False)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 6: N/ST Ratio Analysis</title>
    {HTML_STYLE}
    <style>
        .ratio-highlight {{
            background: linear-gradient(135deg, #fff3e0, #ffe0b2);
            border: 3px solid #ff8c00;
            padding: 25px;
            border-radius: 10px;
            margin: 25px 0;
        }}
        .ratio-highlight h3 {{
            color: #e65100;
            margin-top: 0;
            border: none;
            padding-left: 0;
        }}
    </style>
</head>
<body>
    <h1>N/ST Ratio Analysis</h1>
    <p class="subtitle">Why the N/ST ratio outperforms nitrogen alone for fertilization timing</p>

    <div class="ratio-highlight">
        <h3>The Core Insight</h3>
        <p style="font-size: 1.1em;">Traditional fertilization timing relies on <strong>Leaf Nitrogen Content (LNC)</strong> alone.
        However, LNC peaks in winter when leaf growth slows - this is a <strong>concentration effect</strong>,
        not a signal that the plant needs fertilization.</p>

        <p style="font-size: 1.1em;">The <strong style="color: #ff8c00;">N/ST ratio</strong> solves this by combining:</p>
        <ul style="font-size: 1.1em;">
            <li><strong>N_Value:</strong> Nitrogen content - the nutrient supply</li>
            <li><strong>ST_Value:</strong> Starch content - the energy reserves</li>
        </ul>

        <p style="font-size: 1.1em; font-weight: bold; color: #e65100;">
        When ST drops (spring/summer growth), the ratio rises - correctly signaling fertilization need.
        </p>
    </div>

    <h2>Normalized Comparison</h2>

    <div class="methodology">
        <h4>Why Normalize?</h4>
        <p>N_Value (%), ST_Value (mg/g), and N/ST ratio have different units and scales.
        Normalizing each to 0-100% allows direct comparison of <strong>timing patterns</strong>
        rather than absolute values.</p>
    </div>

    <h3>Full Period: Aug 2022 - Aug 2024</h3>

    <div class="analysis-section">
        <p>All curves scaled to their min-max range. The <strong style="color: #ff8c00;">bright orange ratio line</strong>
        shows when fertilization is needed - it rises when ST drops, regardless of what N alone suggests.</p>
        {plot_full}
    </div>

    <h3>Recent Period: Aug 2023 - Aug 2024</h3>

    <div class="analysis-section">
        <p>Excludes the 2022 depleted year for a <strong>cleaner seasonal pattern</strong>.
        This period shows the typical annual cycle without the anomalous starch depletion event.</p>
        {plot_recent}
    </div>

    <div class="warning-box" style="background: #fff3cd; border-left: 4px solid #ff8c00;">
        <h4>The Critical Difference</h4>
        <ul>
            <li><strong style="color: {N_COLOR};">N Peaks in Winter:</strong> Nitrogen concentration reaches maximum
            values in Nov-Feb, but this reflects reduced leaf growth (concentration effect),
            <strong>NOT</strong> optimal fertilization timing.</li>

            <li><strong style="color: {ST_COLOR};">ST Drops in Spring/Summer:</strong> Starch reserves decline as trees
            mobilize carbohydrates for new growth - <strong>THIS</strong> signals actual fertilization need.</li>

            <li><strong style="color: {RATIO_COLOR};">N/ST Ratio Captures Both:</strong> The ratio rises when ST drops,
            correctly identifying the spring/summer fertilization window that N alone misses.</li>

            <li><strong style="color: {RATIO_COLOR};">Steady Rise = Increased Demand:</strong> A steady rise in N/ST ratio
            highlights the increased nitrogen demand during active growth and metabolic phases -
            this is when fertilization is most effective.</li>
        </ul>
    </div>

    <h2>Practical Implications</h2>

    <div class="analysis-section">
        <h4>For Agronomists and Growers</h4>
        <table class="treatment-table" style="width: 100%;">
            <tr>
                <th>Metric</th>
                <th>Peak Timing</th>
                <th>Implication for Fertilization</th>
            </tr>
            <tr>
                <td style="color: {N_COLOR}; font-weight: bold;">N_Value alone</td>
                <td>Winter (Nov-Feb)</td>
                <td style="background: rgba(255, 230, 109, 0.3);">
                    <strong>Misleading</strong> - High N in winter reflects concentration, not need
                </td>
            </tr>
            <tr>
                <td style="color: {ST_COLOR}; font-weight: bold;">ST_Value</td>
                <td>Fall (Sep-Nov)</td>
                <td>
                    Low ST in spring signals energy mobilization for growth
                </td>
            </tr>
            <tr>
                <td style="color: {RATIO_COLOR}; font-weight: bold;">N/ST Ratio</td>
                <td>Spring-Summer (Apr-Jul)</td>
                <td style="background: rgba(200, 230, 201, 0.3);">
                    <strong>Optimal</strong> - Rising ratio indicates true fertilization need
                </td>
            </tr>
        </table>
    </div>

    <div class="discovery-box">
        <h3>Summary: Research Insights</h3>
        <ul>
            <li><strong>Year Effect:</strong> Environmental factors (climate, water availability) dominate
            starch reserves, often overwhelming nitrogen treatment effects</li>

            <li><strong>LNC Classification:</strong> UC Davis thresholds provide reliable benchmarks for
            nitrogen status when adjusted for seasonal patterns</li>

            <li><strong>N/ST Ratio Advantage:</strong> Combining N and ST measurements reveals metabolic
            status and provides more accurate fertilization timing signals than N alone</li>

            <li><strong>Optimal Timing:</strong> The N/ST ratio correctly identifies <strong>spring/summer</strong>
            as the optimal fertilization window, which N alone would miss</li>
        </ul>
    </div>

    <div class="ratio-highlight">
        <h3>Conclusion</h3>
        <p style="font-size: 1.2em;">
        The N/ST ratio integrates nitrogen status with metabolic context, providing a more reliable
        indicator for fertilization timing decisions. By accounting for both the nutrient supply (N)
        and energy reserves (ST), this ratio reveals the plant's true physiological status and
        fertilization needs.
        </p>
        <p style="font-size: 1.1em; font-weight: bold; color: #e65100;">
        This finding has practical implications for precision agriculture: spectroscopy-based N/ST ratio
        predictions can guide site-specific fertilization timing, optimizing both yield and resource efficiency.
        </p>
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
