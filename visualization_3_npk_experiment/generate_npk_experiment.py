"""
Visualization 3: NPK Experiment Analysis

This visualization presents the controlled NPK fertilization experiment
conducted on citrus trees at Gilat Research Station. It includes:
1. Treatment table with 5 nitrogen levels
2. Sample collection timeline by treatment
3. N/ST ratio explanation and motivation
4. Treatment group comparison (scatter and box plots for N and ST)

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

def create_treatment_table():
    """Create HTML table for NPK treatments."""
    table_html = '''
    <table class="treatment-table" style="width: 100%; margin: 20px auto;">
        <tr>
            <th>Treatment</th>
            <th>N Level (kg/ha)</th>
            <th>Description</th>
            <th>Tree IDs</th>
            <th>Replicates</th>
        </tr>
    '''

    for treatment in TREATMENT_ORDER:
        color = TREATMENT_COLORS[treatment]
        desc = TREATMENT_DESCRIPTIONS[treatment]
        trees = NPK_TREATMENTS[treatment]
        n_level = treatment.replace('N', '')

        table_html += f'''
        <tr>
            <td style="color: {color}; font-weight: bold; font-size: 1.1em;">{treatment}</td>
            <td>{n_level}</td>
            <td>{desc}</td>
            <td>{', '.join(map(str, trees))}</td>
            <td>{len(trees)}</td>
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
            text="3.2 Sample Collection Timeline by Treatment<br><sup>Monthly sample counts for each nitrogen treatment level</sup>",
            font=dict(size=16)
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
            title='Treatment'
        ),
        height=450,
        hovermode='x unified'
    )

    return fig


def create_treatment_comparison(df):
    """Create treatment comparison with scatter plot and box plots."""
    df_valid = df.dropna(subset=['N_Value', 'ST_Value']).copy()

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"colspan": 2}, None], [{}, {}]],
        subplot_titles=[
            'N_Value vs ST_Value by Treatment',
            'N_Value Distribution',
            'ST_Value Distribution'
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # Scatter plot with centroids
    for treatment in TREATMENT_ORDER:
        treatment_data = df_valid[df_valid['treatment'] == treatment]
        if len(treatment_data) > 0:
            # Individual points
            fig.add_trace(go.Scatter(
                x=treatment_data['N_Value'],
                y=treatment_data['ST_Value'],
                mode='markers',
                name=f'{treatment} (n={len(treatment_data)})',
                marker=dict(
                    color=TREATMENT_COLORS[treatment],
                    size=6,
                    opacity=0.6
                ),
                legendgroup=treatment,
                hovertemplate=f'{treatment}<br>N: %{{x:.2f}}%<br>ST: %{{y:.1f}} mg/g<extra></extra>'
            ), row=1, col=1)

            # Centroid
            centroid_n = treatment_data['N_Value'].mean()
            centroid_st = treatment_data['ST_Value'].mean()
            fig.add_trace(go.Scatter(
                x=[centroid_n],
                y=[centroid_st],
                mode='markers',
                name=f'{treatment} centroid',
                marker=dict(
                    color=TREATMENT_COLORS[treatment],
                    size=18,
                    symbol='x',
                    line=dict(width=3, color='black')
                ),
                legendgroup=treatment,
                showlegend=False,
                hovertemplate=f'{treatment} Centroid<br>N: %{{x:.2f}}%<br>ST: %{{y:.1f}} mg/g<extra></extra>'
            ), row=1, col=1)

    # N_Value box plots
    for treatment in TREATMENT_ORDER:
        treatment_data = df[df['treatment'] == treatment]
        if len(treatment_data) > 0:
            fig.add_trace(go.Box(
                y=treatment_data['N_Value'],
                name=treatment,
                marker_color=TREATMENT_COLORS[treatment],
                legendgroup=treatment,
                showlegend=False,
                boxmean=True
            ), row=2, col=1)

    # ST_Value box plots
    for treatment in TREATMENT_ORDER:
        treatment_data = df[df['treatment'] == treatment]
        if len(treatment_data) > 0:
            fig.add_trace(go.Box(
                y=treatment_data['ST_Value'],
                name=treatment,
                marker_color=TREATMENT_COLORS[treatment],
                legendgroup=treatment,
                showlegend=False,
                boxmean=True
            ), row=2, col=2)

    fig.update_xaxes(title_text="N_Value (%)", row=1, col=1)
    fig.update_yaxes(title_text="ST_Value (mg/g)", row=1, col=1)
    fig.update_yaxes(title_text="N_Value (%)", row=2, col=1)
    fig.update_yaxes(title_text="ST_Value (mg/g)", row=2, col=2)

    fig.update_layout(
        title=dict(
            text="3.4 Treatment Group Comparison<br><sup>Scatter plot shows N vs ST relationship | Box plots show distributions | X markers indicate group centroids</sup>",
            font=dict(size=16)
        ),
        height=800,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.08,
            xanchor='center',
            x=0.5
        )
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
    treatment_table = create_treatment_table()
    fig_timeline = create_timeline_chart(df)
    fig_comparison = create_treatment_comparison(df)
    summary_stats = create_summary_stats(df)

    # Convert to HTML
    plot_timeline = fig_timeline.to_html(full_html=False, include_plotlyjs='cdn')
    plot_comparison = fig_comparison.to_html(full_html=False, include_plotlyjs=False)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 3: NPK Experiment Analysis</title>
    {HTML_STYLE}
</head>
<body>
    <h1>NPK Experiment Analysis</h1>
    <p class="subtitle">Controlled nitrogen fertilization study on citrus at Gilat Research Station</p>

    <div class="intro-box">
        <h3 style="margin-top: 0; border: none; padding-left: 0;">Experimental Design</h3>
        <p>The NPK experiment is a <strong>controlled fertilization study</strong> conducted at Gilat Research Station
        in the Negev region of Israel. Citrus trees were subjected to five different nitrogen (N) fertilization levels
        to study the relationship between nitrogen input and plant chemistry.</p>

        <p><strong>Research Objectives:</strong></p>
        <ul>
            <li>Quantify the effect of nitrogen fertilization on leaf chemistry</li>
            <li>Establish relationships between N input and measurable plant responses</li>
            <li>Develop spectroscopy-based methods for nitrogen status assessment</li>
            <li>Identify optimal fertilization timing using the N/ST ratio</li>
        </ul>
    </div>

    <h2>3.1 Treatment Groups</h2>

    <div class="analysis-section">
        <p>Five nitrogen treatment levels were established, ranging from severe deficiency (N10) to
        excessive application (N150). Each treatment is replicated across 5 trees.</p>
        {treatment_table}

        <div class="methodology">
            <h4>Treatment Assignment</h4>
            <p>Trees were randomly assigned to treatment groups to ensure statistical validity.
            The N60 treatment represents the <strong>agronomic optimum</strong> based on established
            citrus fertilization guidelines for the region.</p>
        </div>
    </div>

    <h2>3.2 Sample Collection</h2>

    <div class="analysis-section">
        <p>Samples were collected at regular intervals throughout the experimental period to capture
        seasonal variations in plant chemistry.</p>
        {plot_timeline}
    </div>

    <h3>Summary Statistics</h3>
    <div class="analysis-section">
        {summary_stats}
    </div>

    <h2>3.3 Why N/ST Ratio?</h2>

    <div class="intro-box" style="background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-color: #ff8c00;">
        <h3 style="margin-top: 0; border: none; padding-left: 0; color: #e65100;">The Rationale for N/ST Ratio</h3>

        <p>Traditional nitrogen status assessment relies solely on <strong>Leaf Nitrogen Content (LNC)</strong>.
        However, this approach has limitations:</p>

        <ul>
            <li><strong>Concentration Effect:</strong> LNC peaks in winter when leaf growth slows,
            not necessarily when the plant needs fertilization</li>
            <li><strong>Missing Metabolic Context:</strong> LNC doesn't account for the plant's energy
            reserves and metabolic state</li>
        </ul>

        <p>The <strong>N/ST ratio</strong> combines nitrogen status with starch reserves:</p>

        <ul>
            <li><strong>N_Value:</strong> Nitrogen content (%) - the nutrient supply</li>
            <li><strong>ST_Value:</strong> Starch content (mg/g) - the energy reserves</li>
            <li><strong>N/ST Ratio:</strong> When this ratio rises, it indicates either increasing N demand
            or depleting energy reserves - both signals for fertilization need</li>
        </ul>

        <p style="font-weight: bold; color: #e65100;">The following visualizations explore how N and ST
        respond to different fertilization levels, setting the stage for N/ST ratio analysis.</p>
    </div>

    <h2>3.4 Treatment Group Comparison</h2>

    <div class="analysis-section">
        <p>This visualization compares nitrogen (N_Value) and starch (ST_Value) across all treatment groups:</p>
        <ul>
            <li><strong>Scatter plot:</strong> Shows the relationship between N and ST for each treatment</li>
            <li><strong>Centroids (X markers):</strong> Indicate the mean position of each treatment group</li>
            <li><strong>Box plots:</strong> Show the distribution and variability within each treatment</li>
        </ul>

        {plot_comparison}

        <div class="key-observations">
            <h4>Key Observations</h4>
            <ul>
                <li><strong>N_Value Response:</strong> Higher nitrogen treatments (N100, N150) show elevated
                leaf nitrogen content, as expected</li>
                <li><strong>ST_Value Variance:</strong> Starch values show high variability across all treatments,
                suggesting factors beyond nitrogen input affect starch reserves</li>
                <li><strong>Treatment Overlap:</strong> Some overlap exists between treatment groups,
                indicating individual tree variation and environmental effects</li>
                <li><strong>Ceiling Effect:</strong> N100 and N150 show similar N_Value ranges,
                suggesting a physiological upper limit to nitrogen accumulation</li>
            </ul>
        </div>
    </div>

    <div class="discovery-box">
        <h3>Looking Ahead</h3>
        <p>The high variance in ST_Value despite controlled nitrogen treatments raises an important question:</p>
        <p style="font-size: 1.1em; font-weight: bold; color: #1b5e20;">
        "If nitrogen treatment isn't driving ST variance, what is?"
        </p>
        <p>This question leads us to the <strong>Year Effect Discovery</strong> in the next visualization,
        where we uncover that environmental factors dominate starch reserves more than fertilization treatment.</p>
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
