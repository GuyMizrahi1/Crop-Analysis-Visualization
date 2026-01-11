"""
Visualization 2: Spectral Data Explorer

This visualization provides an interactive exploration of spectral signatures
across different crop types. It features:
1. Mean spectrum per crop (clean view)
2. All individual samples with transparency (detailed view)
3. Toggle button to switch between views
4. Interactive legend to filter crops

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
    CROP_COLORS, HTML_STYLE,
    DATA_DIR
)

SPECTRAL_DATA_PATH = os.path.join(DATA_DIR, 'spectral_data.csv')

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


def load_spectral_data():
    """Load and prepare spectral data."""
    print("Loading spectral data...")
    df = pd.read_csv(SPECTRAL_DATA_PATH)

    # Parse crop from ID
    df['parsed_crop'] = df['ID'].apply(extract_crop_from_id)

    # Remove rows without valid crop
    df = df[df['parsed_crop'].notna()]

    print(f"Loaded {len(df)} samples")

    # Get wavelength columns (numeric column names)
    all_columns = df.columns.tolist()
    wavelength_cols = []
    wavelengths = []

    for col in all_columns:
        try:
            wl = float(col)
            if 3000 < wl < 11000:  # Valid wavelength range
                wavelength_cols.append(col)
                wavelengths.append(wl)
        except ValueError:
            continue

    print(f"Found {len(wavelength_cols)} wavelength columns")

    return df, wavelength_cols, wavelengths


def calculate_mean_spectra(df, wavelength_cols):
    """Calculate mean spectrum for each crop."""
    mean_spectra = {}
    std_spectra = {}

    for crop in ['Citrus', 'Almond', 'Avocado', 'Vine']:
        crop_df = df[df['parsed_crop'] == crop]
        if len(crop_df) > 0:
            mean_spectra[crop] = crop_df[wavelength_cols].mean().values
            std_spectra[crop] = crop_df[wavelength_cols].std().values
            print(f"  {crop}: {len(crop_df)} samples")

    return mean_spectra, std_spectra


def sample_individual_spectra(df, wavelength_cols, max_samples_per_crop=100):
    """Sample individual spectra for the 'all samples' view."""
    sampled = {}

    for crop in ['Citrus', 'Almond', 'Avocado', 'Vine']:
        crop_df = df[df['parsed_crop'] == crop]
        if len(crop_df) > max_samples_per_crop:
            crop_df = crop_df.sample(n=max_samples_per_crop, random_state=42)
        sampled[crop] = crop_df[wavelength_cols].values
        print(f"  {crop}: sampled {len(crop_df)} spectra")

    return sampled


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_spectral_explorer(df, wavelength_cols, wavelengths):
    """Create the interactive spectral explorer with dual view."""
    print("\nCalculating mean spectra...")
    mean_spectra, std_spectra = calculate_mean_spectra(df, wavelength_cols)

    print("\nSampling individual spectra...")
    individual_spectra = sample_individual_spectra(df, wavelength_cols, max_samples_per_crop=50)

    fig = go.Figure()

    # Track trace indices for visibility toggling
    mean_traces = []
    individual_traces = []

    # Order crops so Citrus is drawn last (on top) to avoid being covered by Almond
    crops = ['Almond', 'Avocado', 'Vine', 'Citrus']

    # Add mean spectra traces (visible by default)
    for crop in crops:
        if crop in mean_spectra:
            # Main mean line - thin line for clarity
            fig.add_trace(go.Scatter(
                x=wavelengths,
                y=mean_spectra[crop],
                mode='lines',
                name=f'{crop}',
                line=dict(color=CROP_COLORS[crop], width=1.5),
                legendgroup=crop,
                hovertemplate=f'{crop}: %{{y:.3f}}<extra></extra>'
            ))
            mean_traces.append(len(fig.data) - 1)

            # Standard deviation band - lighter fill
            upper = mean_spectra[crop] + std_spectra[crop]
            lower = mean_spectra[crop] - std_spectra[crop]

            fig.add_trace(go.Scatter(
                x=list(wavelengths) + list(wavelengths)[::-1],
                y=list(upper) + list(lower)[::-1],
                fill='toself',
                fillcolor=CROP_COLORS[crop].replace(')', ', 0.1)').replace('rgb', 'rgba'),
                line=dict(color='rgba(0,0,0,0)'),
                name=f'{crop} (±1 SD)',
                legendgroup=crop,
                showlegend=False,
                hoverinfo='skip'
            ))
            mean_traces.append(len(fig.data) - 1)

    # Add individual spectra traces (hidden by default)
    for crop in crops:
        if crop in individual_spectra:
            for i, spectrum in enumerate(individual_spectra[crop]):
                # For the first sample of each crop, use a thicker line for better legend visibility
                is_first = (i == 0)
                fig.add_trace(go.Scatter(
                    x=wavelengths,
                    y=spectrum,
                    mode='lines',
                    name=crop if is_first else None,
                    line=dict(color=CROP_COLORS[crop], width=3.0 if is_first else 1.0),
                    opacity=0.8 if is_first else 0.25,
                    legendgroup=crop,
                    showlegend=is_first,
                    visible=False,
                    hoverinfo='skip'  # Disable hover for individual samples to reduce clutter
                ))
                individual_traces.append(len(fig.data) - 1)

    # Create visibility arrays for toggles
    total_traces = len(fig.data)

    # Mean view: show mean traces, hide individual
    mean_visibility = [False] * total_traces
    for idx in mean_traces:
        mean_visibility[idx] = True

    # Individual view: show individual traces, hide mean
    individual_visibility = [False] * total_traces
    for idx in individual_traces:
        individual_visibility[idx] = True

    # Add dropdown menu for view toggle
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=0.5,
                y=1.02,
                xanchor="center",
                buttons=[
                    dict(
                        label="Mean Spectrum",
                        method="update",
                        args=[{"visible": mean_visibility}]
                    ),
                    dict(
                        label="All Samples",
                        method="update",
                        args=[{"visible": individual_visibility}]
                    )
                ],
                bgcolor='white',
                bordercolor='#228B22',
                font=dict(color='#1b5e20')
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Spectral Signatures by Crop Type<br><sup>Toggle between Mean Spectrum and All Samples views using the buttons above</sup>",
            font=dict(size=18),
            y=0.95
        ),
        xaxis=dict(
            title="Wavelength (nm)",
            tickformat=".0f",
            dtick=500,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            title="Spectral Value (Reflectance/Absorbance)",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5,
            title='Click to toggle crops:'
        ),
        height=650,
        hovermode='x unified',
        plot_bgcolor='white'
    )

    return fig


def create_wavelength_regions_annotation():
    """Create HTML annotation explaining spectral regions."""
    return """
    <div class="methodology">
        <h4>Spectral Region Interpretation</h4>
        <p>The near-infrared (NIR) spectrum reveals chemical composition through molecular absorption:</p>
        <ul>
            <li><strong>4,000-5,000 nm:</strong> C-H stretching - lipids, carbohydrates</li>
            <li><strong>5,000-6,000 nm:</strong> C=O stretching - proteins, organic acids</li>
            <li><strong>6,000-7,500 nm:</strong> N-H bending - proteins, amino acids (nitrogen indicator)</li>
            <li><strong>7,500-10,000 nm:</strong> C-O stretching - carbohydrates, starch</li>
        </ul>
        <p>Differences in spectral signatures between crops reflect their unique biochemical composition.</p>
    </div>
    """


# =============================================================================
# HTML REPORT GENERATION
# =============================================================================

def generate_html_report(df, wavelength_cols, wavelengths):
    """Generate the complete HTML report."""
    print("\nGenerating spectral explorer visualization...")

    fig = create_spectral_explorer(df, wavelength_cols, wavelengths)
    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # Calculate some statistics
    crop_counts = df['parsed_crop'].value_counts().to_dict()
    stats_html = '<ul>'
    for crop in ['Citrus', 'Almond', 'Avocado', 'Vine']:
        count = crop_counts.get(crop, 0)
        stats_html += f'<li><span style="color: {CROP_COLORS[crop]}; font-weight: bold;">{crop}</span>: {count:,} samples</li>'
    stats_html += '</ul>'

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Visualization 2: Spectral Data Explorer</title>
    {HTML_STYLE}
    <style>
        .spectral-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #228B22;
        }}
        @media (max-width: 768px) {{
            .spectral-info {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <h1>Spectral Data Explorer</h1>
    <p class="subtitle">Interactive exploration of near-infrared spectral signatures across crop types</p>

    <div class="intro-box">
        <h3 style="margin-top: 0; border: none; padding-left: 0;">Understanding Spectral Data</h3>
        <p><strong>Near-infrared (NIR) spectroscopy</strong> is a non-destructive technique that measures
        how plant tissues absorb and reflect light at different wavelengths. Each crop has a unique
        "spectral fingerprint" determined by its biochemical composition.</p>

        <div class="spectral-info">
            <div class="info-card">
                <h4 style="margin-top: 0;">Wavelength Range</h4>
                <p><strong>3,999 - 10,001 nm</strong><br>
                Mid-infrared region sensitive to organic compounds</p>
            </div>
            <div class="info-card">
                <h4 style="margin-top: 0;">Total Measurements</h4>
                <p><strong>{len(wavelengths):,} wavelengths</strong><br>
                High-resolution spectral data per sample</p>
            </div>
        </div>
    </div>

    <h2>Interactive Spectral Visualization</h2>

    <div class="analysis-section">
        <p><strong>Instructions:</strong></p>
        <ul>
            <li>Use the <strong>Mean Spectrum / All Samples</strong> buttons to switch views</li>
            <li>Click on crop names in the legend to <strong>show/hide</strong> specific crops</li>
            <li>Hover over the chart to see exact wavelength and value</li>
            <li>Use the toolbar to zoom, pan, or download the figure</li>
        </ul>

        {plot_html}

        {create_wavelength_regions_annotation()}
    </div>

    <h2>Dataset Summary</h2>

    <div class="analysis-section">
        <h4>Samples per Crop Type</h4>
        {stats_html}

        <div class="key-observations">
            <h4>Key Spectral Observations</h4>
            <ul>
                <li><strong>Distinct Signatures:</strong> Each crop shows a unique spectral pattern,
                reflecting differences in leaf structure and chemical composition</li>
                <li><strong>Common Absorption Bands:</strong> All crops show absorption features at similar
                wavelengths (water, chlorophyll, cellulose), but with varying intensities</li>
                <li><strong>Nitrogen Sensitivity:</strong> The 6,000-7,500 nm region is particularly sensitive
                to nitrogen-containing compounds, making it valuable for N status prediction</li>
                <li><strong>Carbohydrate Features:</strong> Starch and sugar content influence the
                7,500-10,000 nm region, relevant for our N/ST ratio analysis</li>
            </ul>
        </div>
    </div>

    <div class="discovery-box">
        <h3>From Spectra to Predictions</h3>
        <p>This spectral data forms the foundation of our machine learning models:</p>
        <ul>
            <li><strong>PLSR (Partial Least Squares Regression):</strong> Reduces 1,557 wavelengths to key components</li>
            <li><strong>Random Forest & XGBoost:</strong> Predict N, SC, and ST values from spectral features</li>
            <li><strong>N/ST Ratio Prediction:</strong> Enables fertilization timing recommendations without destructive sampling</li>
        </ul>
        <p>The ability to predict chemical composition from spectral data enables rapid, non-destructive
        assessment of crop nitrogen status in the field.</p>
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
    print("Generating Visualization 2: Spectral Data Explorer")
    print("=" * 70)

    # Load data
    df, wavelength_cols, wavelengths = load_spectral_data()

    # Generate report
    html_content = generate_html_report(df, wavelength_cols, wavelengths)

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'spectral_explorer.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nSaved to: {output_path}")
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
