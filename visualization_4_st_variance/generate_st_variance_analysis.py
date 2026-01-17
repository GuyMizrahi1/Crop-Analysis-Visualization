"""
Visualization 4: ST Variance Analysis

This visualization investigates the high variance observed in starch (ST) values
and leads to the discovery that year/climate effects dominate over treatment effects.

Includes:
1. Monthly ST Variance Overview - box plots showing high within-month variance
2. ST Timeline by Treatment - all treatments follow the same pattern
3. ST Values by Treatment and Year - year effect confirmed

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
    TREATMENT_COLORS, TREATMENT_ORDER, YEAR_COLORS, YEAR_ORDER,
    MONTH_LABELS, HTML_STYLE, NPK_DATASET_PATH
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

    print(f"Loaded {len(df)} NPK samples")
    return df


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_monthly_variance(df):
    """Create monthly ST variance violin plots."""
    fig = go.Figure()

    for month in range(1, 13):
        month_data = df[df['month'] == month]['ST_Value']
        if len(month_data) > 0:
            fig.add_trace(go.Violin(
                y=month_data,
                name=MONTH_LABELS[month-1],
                line_color='#2ECC71',
                fillcolor='rgba(46, 204, 113, 0.5)',
                meanline_visible=True,
                box_visible=True,
                width=0.9,  # Make violins wider
                points=False,  # Hide individual points for cleaner look
                span=[0, None],  # Clip at 0 (no negative values), auto for max
                spanmode='hard',  # Hard clip - no extrapolation beyond data range
                hovertemplate=f'{MONTH_LABELS[month-1]}<br>ST: %{{y:.1f}} mg/g<extra></extra>'
            ))

    # Calculate and add mean line
    monthly_means = df.groupby('month')['ST_Value'].mean()
    fig.add_trace(go.Scatter(
        x=MONTH_LABELS,
        y=[monthly_means.get(m, np.nan) for m in range(1, 13)],
        mode='lines+markers',
        name='Monthly Mean',
        line=dict(color='#006400', width=3),
        marker=dict(size=10, color='#006400'),
        hovertemplate='Mean ST: %{y:.1f} mg/g<extra></extra>'
    ))

    # Add critical zone below 50 mg/g
    fig.add_hrect(
        y0=0, y1=50,
        fillcolor='rgba(255, 100, 100, 0.15)',
        layer='below',
        line_width=0
    )
    fig.add_annotation(
        x=2.5, y=15,  # numeric position between Mar(2) and Apr(3)
        text="Abnormally low zone (<50 mg/g)",
        showarrow=False,
        font=dict(size=10, color='#c0392b')
    )

    fig.update_layout(
        title=dict(
            text="4.1 Monthly ST Distribution (Trimmed Violins)<br><sup>Bimodal patterns visible --> Variance not explained by seasonal behavior | Curve connects monthly means | June extremely low</sup>",
            font=dict(size=16)
        ),
        xaxis_title='Month',
        yaxis_title='ST Value (mg/g)',
        height=500,
        showlegend=False,
        yaxis=dict(range=[0, 230]),
        violinmode='group'
    )

    return fig


def create_st_timeline_by_treatment(df):
    """Create ST timeline showing all treatments follow the same pattern."""
    monthly_data = df.groupby(['year', 'month', 'treatment'])['ST_Value'].mean().reset_index()
    monthly_data['date'] = pd.to_datetime(
        monthly_data['year'].astype(str) + '-' + monthly_data['month'].astype(str) + '-15'
    )
    monthly_data = monthly_data.sort_values('date')

    overall_mean = df['ST_Value'].mean()

    fig = go.Figure()

    for treatment in TREATMENT_ORDER:
        trt_data = monthly_data[monthly_data['treatment'] == treatment]
        if len(trt_data) > 0:
            fig.add_trace(go.Scatter(
                x=trt_data['date'],
                y=trt_data['ST_Value'],
                mode='lines+markers',
                name=treatment,
                line=dict(color=TREATMENT_COLORS[treatment], width=2),
                marker=dict(size=6),
                hovertemplate=f'{treatment}<br>%{{x|%B %Y}}<br>ST: %{{y:.1f}} mg/g<extra></extra>'
            ))

    # Add critical zone below 50 mg/g
    fig.add_hrect(
        y0=0, y1=50,
        fillcolor='rgba(255, 100, 100, 0.2)',
        layer='below',
        line_width=0
    )
    fig.add_annotation(
        x='2022-01-15', y=25,
        text="Abnormally low zone (<50 mg/g)",
        showarrow=False,
        font=dict(size=10, color='#c0392b')
    )

    # Add depleted period highlight
    fig.add_vrect(
        x0='2022-05-01', x1='2023-03-31',
        fillcolor='rgba(46, 204, 113, 0.15)',
        layer='below',
        line_width=0,
        annotation_text='May 2022 - Mar 2023: Depleted Period',
        annotation_position='top left'
    )

    fig.update_layout(
        title=dict(
            text="4.2 ST Timeline: Year effect dominates treatment effect<br><sup>All 5 treatments follow identical pattern | Values <50 mg/g indicate critical depletion</sup>",
            font=dict(size=16)
        ),
        xaxis_title='Date',
        yaxis_title='Mean ST Value (mg/g)',
        height=500,
        yaxis=dict(range=[0, 200]),
        xaxis=dict(tickformat='%b %Y', dtick='M2'),
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
        margin=dict(b=100)
    )

    return fig


def create_st_by_year(df):
    """Create ST values by treatment and year - showing year dominates."""
    # Filter out 2021 (only 1 month of data)
    years = sorted([y for y in df['year'].unique() if y in YEAR_ORDER and y >= 2022])

    fig = make_subplots(
        rows=1, cols=len(years),
        subplot_titles=[str(y) for y in years],
        shared_yaxes=True,
        horizontal_spacing=0.05
    )

    for col, year in enumerate(years, 1):
        year_df = df[df['year'] == year]
        for treatment in TREATMENT_ORDER:
            trt_data = year_df[year_df['treatment'] == treatment]['ST_Value']
            if len(trt_data) > 0:
                fig.add_trace(go.Box(
                    y=trt_data,
                    name=treatment,
                    marker_color=TREATMENT_COLORS[treatment],
                    showlegend=(col == 1),
                    legendgroup=treatment,
                    boxmean=True
                ), row=1, col=col)

    fig.update_layout(
        title=dict(
            text="4.3 Treatment vs Year: Year effect explains the variance<br><sup>No significant ST difference between treatments within same year</sup>",
            font=dict(size=16)
        ),
        height=500,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.12,
            xanchor='center',
            x=0.5
        )
    )

    fig.update_yaxes(title_text='ST Value (mg/g)', row=1, col=1)
    fig.update_yaxes(range=[0, 230])

    return fig


def create_year_statistics_table(df):
    """Create statistics table showing year effect."""
    stats = []

    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        stats.append({
            'Year': year,
            'Samples': len(year_df),
            'Mean ST': f"{year_df['ST_Value'].mean():.1f}",
            'Std ST': f"{year_df['ST_Value'].std():.1f}",
            'Min ST': f"{year_df['ST_Value'].min():.1f}",
            'Max ST': f"{year_df['ST_Value'].max():.1f}"
        })

    stats_df = pd.DataFrame(stats)

    table_html = '<table class="treatment-table" style="width: 100%;">'
    table_html += '<tr>'
    for col in stats_df.columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr>'

    for _, row in stats_df.iterrows():
        # Highlight 2022 as depleted year
        if row['Year'] == 2022:
            table_html += '<tr style="background-color: rgba(173, 216, 230, 0.3);">'
        else:
            table_html += '<tr>'

        for col in stats_df.columns:
            if col == 'Year':
                color = YEAR_COLORS.get(row[col], '#333')
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
    fig_monthly = create_monthly_variance(df)
    fig_timeline = create_st_timeline_by_treatment(df)
    fig_by_year = create_st_by_year(df)

    # Convert to HTML
    plot_monthly = fig_monthly.to_html(full_html=False, include_plotlyjs='cdn')
    plot_timeline = fig_timeline.to_html(full_html=False, include_plotlyjs=False)
    plot_by_year = fig_by_year.to_html(full_html=False, include_plotlyjs=False)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 4: Year Effect on Starch</title>
    {HTML_STYLE}
</head>
<body>
    <h1>Starch Variance: Inter-Annual Climate Effect Dominates Treatment Effect</h1>
    <p class="subtitle">2022: Depleted (~50-80 mg/g) | 2023-24: Recovered (~120-160 mg/g) | N treatment effect not significant</p>

    <div class="analysis-section">
        {plot_monthly}
    </div>

    <div class="analysis-section">
        {plot_timeline}
    </div>

    <div class="analysis-section">
        {plot_by_year}
    </div>
</body>
</html>"""

    return html_content


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("Generating Visualization 4: ST Variance Analysis")
    print("=" * 70)

    # Load data
    df = load_npk_data()

    # Generate report
    html_content = generate_html_report(df)

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'st_variance_analysis.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nSaved to: {output_path}")
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
