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
    """Create monthly ST variance box plots."""
    fig = go.Figure()

    for month in range(1, 13):
        month_data = df[df['month'] == month]['ST_Value']
        if len(month_data) > 0:
            fig.add_trace(go.Box(
                y=month_data,
                name=MONTH_LABELS[month-1],
                marker_color='#2ECC71',
                fillcolor='rgba(46, 204, 113, 0.5)',
                boxmean=True,
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

    fig.update_layout(
        title=dict(
            text="4.1 Monthly ST Value Distribution<br><sup>Notice the high variance in certain months - this led us to investigate further</sup>",
            font=dict(size=16)
        ),
        xaxis_title='Month',
        yaxis_title='ST Value (mg/g)',
        height=500,
        showlegend=False,
        yaxis=dict(range=[0, 230])
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

    # Add overall mean line
    fig.add_hline(
        y=overall_mean,
        line_dash="solid",
        line_color="#2980b9",
        line_width=2,
        annotation_text=f"Overall Mean: {overall_mean:.1f} mg/g",
        annotation_position="bottom right"
    )

    # Add depleted period highlight
    fig.add_vrect(
        x0='2022-05-01', x1='2023-04-30',
        fillcolor='rgba(173, 216, 230, 0.3)',
        layer='below',
        line_width=0,
        annotation_text='Depleted Period',
        annotation_position='top left'
    )

    fig.update_layout(
        title=dict(
            text="4.2 ST Timeline by Treatment<br><sup>All 5 treatments follow the SAME pattern - the year effect dominates</sup>",
            font=dict(size=16)
        ),
        xaxis_title='Date',
        yaxis_title='Mean ST Value (mg/g)',
        height=500,
        yaxis=dict(range=[0, 200]),
        xaxis=dict(tickformat='%b %Y', dtick='M2'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )

    return fig


def create_st_by_year(df):
    """Create ST values by treatment and year - showing year dominates."""
    years = sorted([y for y in df['year'].unique() if y in YEAR_ORDER])

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
            text="4.3 ST Values by Treatment Group and Year<br><sup>All treatments show the same pattern: LOW in 2022, RECOVERED in 2023-2024</sup>",
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
    year_stats = create_year_statistics_table(df)

    # Convert to HTML
    plot_monthly = fig_monthly.to_html(full_html=False, include_plotlyjs='cdn')
    plot_timeline = fig_timeline.to_html(full_html=False, include_plotlyjs=False)
    plot_by_year = fig_by_year.to_html(full_html=False, include_plotlyjs=False)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 4: ST Variance Analysis</title>
    {HTML_STYLE}
</head>
<body>
    <h1>ST Variance Analysis</h1>
    <p class="subtitle">Discovering why starch values show unexpectedly high variance</p>

    <div class="intro-box" style="background: linear-gradient(135deg, #fff8e1, #ffecb3); border-color: #FFA000;">
        <h3 style="margin-top: 0; border: none; padding-left: 0; color: #e65100;">The Problem</h3>
        <p>While analyzing the NPK experiment data, we observed something unexpected:</p>
        <ul>
            <li><strong>High variance</strong> in ST values within certain months</li>
            <li>Monthly ST averages were <strong>nearly identical</strong> across all 5 nitrogen treatments</li>
            <li>Treatment groups showed <strong>no clear differentiation</strong> in their starch values</li>
        </ul>
        <p style="font-weight: bold; color: #e65100;">
        Question: If nitrogen treatment isn't driving the ST variance, what is?
        </p>
    </div>

    <h2>4.1 Monthly ST Variance Overview</h2>

    <div class="analysis-section">
        <p>The box plots below show ST value distributions for each month. Notice the substantial
        variance in months like January, February, July, October, and November.</p>
        {plot_monthly}

        <div class="key-observations">
            <h4>Key Observations</h4>
            <ul>
                <li>Some months show ST ranges from 30-200 mg/g - a 6x difference!</li>
                <li>The green line shows the monthly mean, but high variance means this is less meaningful</li>
                <li>This variance cannot be explained by treatment differences alone</li>
            </ul>
        </div>
    </div>

    <h2>4.2 ST Timeline by Treatment</h2>

    <div class="analysis-section">
        <p>Plotting ST values over time for each treatment reveals a striking pattern:</p>
        {plot_timeline}

        <div class="methodology">
            <h4>Critical Finding</h4>
            <p>All 5 treatment groups follow the <strong>exact same trajectory</strong>. They all:</p>
            <ul>
                <li>Dip during May 2022 - March 2023 (the "Depleted Period" highlighted in blue)</li>
                <li>Recover together starting in mid-2023</li>
                <li>Maintain similar levels through 2024</li>
            </ul>
            <p>This synchronized behavior across all treatments suggests an <strong>external environmental factor</strong>
            is dominating the starch dynamics.</p>
        </div>
    </div>

    <h2>4.3 ST Values by Treatment and Year</h2>

    <div class="analysis-section">
        <p>The definitive proof - comparing treatment groups within each year:</p>
        {plot_by_year}

        <h4>Year-by-Year Statistics</h4>
        {year_stats}
        <p style="font-style: italic; color: #666;">* 2022 highlighted as the depleted year</p>
    </div>

    <div class="discovery-box">
        <h3>The Discovery: YEAR is the Dominant Factor</h3>
        <p><strong>2022 was a "starch-depleted" year</strong> where ALL trees (regardless of nitrogen treatment)
        showed dramatically lower ST values:</p>
        <ul>
            <li><strong>2022:</strong> Mean ST ~50-80 mg/g (depleted)</li>
            <li><strong>2023:</strong> Mean ST ~120-160 mg/g (recovered)</li>
            <li><strong>2024:</strong> Mean ST ~100-140 mg/g (stable)</li>
        </ul>
        <p>All 5 treatment groups followed the <em>same</em> pattern - the nitrogen treatment effect
        is <strong>overwhelmed by the year effect</strong>.</p>
    </div>

    <div class="warning-box">
        <h4>Implications for Analysis</h4>
        <p>This discovery has important implications:</p>
        <ul>
            <li><strong>Cannot ignore year:</strong> Any model predicting ST must account for inter-annual variability</li>
            <li><strong>Environmental factors matter:</strong> Drought, temperature, or other climate factors likely
            caused the 2022 depletion</li>
            <li><strong>N/ST ratio still valuable:</strong> Even though ST is affected by year, the <em>ratio</em>
            of N to ST can still indicate relative metabolic status and fertilization needs</li>
        </ul>
    </div>

    <div class="discovery-box" style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);">
        <h3>Bottom Line</h3>
        <p style="font-size: 1.2em; font-weight: bold; color: #1b5e20;">
        Year-to-year environmental variation is the dominant factor affecting starch reserves -
        not nitrogen treatment level.
        </p>
        <p>This must be accounted for in any predictive model, and it reinforces the value of the N/ST ratio
        as a relative indicator that accounts for both nitrogen status and energy reserves.</p>
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
