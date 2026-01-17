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


def hex_to_rgba(hex_color, opacity):
    """Convert hex color to rgba string."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {opacity})'


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


def sample_individual_spectra(df, wavelength_cols, wavelengths, max_samples_per_crop=100):
    """Sample individual spectra for the 'all samples' view."""
    sampled = {}

    # Find column closest to 4000nm for avocado outlier filtering
    wavelengths_arr = np.array(wavelengths)
    idx_4000 = np.argmin(np.abs(wavelengths_arr - 4000))
    col_4000 = wavelength_cols[idx_4000]

    for crop in ['Citrus', 'Almond', 'Avocado', 'Vine']:
        crop_df = df[df['parsed_crop'] == crop].copy()

        # Remove avocado outliers (values > 0.8 at ~4000nm)
        if crop == 'Avocado':
            crop_df = crop_df[crop_df[col_4000] <= 0.8]
            print(f"  {crop}: filtered outliers, {len(crop_df)} samples remaining")

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
    individual_spectra = sample_individual_spectra(df, wavelength_cols, wavelengths, max_samples_per_crop=50)

    fig = go.Figure()

    # Track trace indices for visibility toggling
    mean_traces = []
    individual_traces = []

    # Order crops so Citrus is drawn last (on top) to avoid being covered by Almond
    crops = ['Almond', 'Avocado', 'Vine', 'Citrus']

    # Add mean spectra traces (hidden by default - switch to "Mean ± SD" to view)
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
                visible=False,
                hovertemplate=f'{crop}: %{{y:.3f}}<extra></extra>'
            ))
            mean_traces.append(len(fig.data) - 1)

            # Standard deviation band - upper and lower boundary lines with transparent fill
            upper = mean_spectra[crop] + std_spectra[crop]
            lower = mean_spectra[crop] - std_spectra[crop]

            # Upper boundary line (invisible - just for fill reference)
            fig.add_trace(go.Scatter(
                x=wavelengths,
                y=upper,
                mode='lines',
                line=dict(color='rgba(0,0,0,0)', width=0),
                legendgroup=crop,
                showlegend=False,
                visible=False,
                hoverinfo='skip'
            ))
            mean_traces.append(len(fig.data) - 1)

            # Lower boundary line with fill to upper (invisible boundary)
            fig.add_trace(go.Scatter(
                x=wavelengths,
                y=lower,
                mode='lines',
                fill='tonexty',
                fillcolor=hex_to_rgba(CROP_COLORS[crop], 0.2),
                line=dict(color='rgba(0,0,0,0)', width=0),
                name=f'{crop} (\u00b11 SD)',
                legendgroup=crop,
                showlegend=False,
                visible=False,
                hoverinfo='skip'
            ))
            mean_traces.append(len(fig.data) - 1)

    # Add individual spectra traces (visible by default - "All Samples" is default view)
    for crop in crops:
        if crop in individual_spectra:
            for i, spectrum in enumerate(individual_spectra[crop]):
                # All samples have same styling - no misleading "mean-like" thick line
                is_first = (i == 0)
                fig.add_trace(go.Scatter(
                    x=wavelengths,
                    y=spectrum,
                    mode='lines',
                    name=crop if is_first else None,
                    line=dict(color=CROP_COLORS[crop], width=1.0),
                    opacity=0.3,
                    legendgroup=crop,
                    showlegend=is_first,
                    visible=True,
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

    # Add dropdown menu for view toggle (default to "All Samples")
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
                        label="All Samples",
                        method="update",
                        args=[{"visible": individual_visibility}]
                    ),
                    dict(
                        label="Mean &plusmn; SD",
                        method="update",
                        args=[{"visible": mean_visibility}]
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
            text="2.1 NIR Absorption Spectrum: Each crop has a distinct biochemical signature",
            font=dict(size=16),
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
    <title>Visualization 2: NIR Spectral Signatures</title>
    {HTML_STYLE}
</head>
<body>
    <h1>NIR (Near Infrared) Spectral Signatures: Unique Fingerprint per Crop Type</h1>
    <p class="subtitle">{len(wavelengths):,} wavelengths (3,999-10,001 nm) | Spectral signatures enable prediction of chemical values (N%, ST, SC)</p>

    <div class="analysis-section">
        {plot_html}
    </div>
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
