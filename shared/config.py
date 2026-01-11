"""
Shared configuration for all visualizations.

This module provides consistent colors, styling, and constants
used across all 6 visualization reports.
"""

# =============================================================================
# COLOR CONFIGURATIONS
# =============================================================================

# Crop colors - consistent across all visualizations
CROP_COLORS = {
    'Citrus': '#E69F00',   # Orange
    'Almond': '#8B4513',   # Brown (Saddle Brown)
    'Avocado': '#009E73',  # Green (Teal)
    'Vine': '#CC79A7'      # Pink (Muted Magenta)
}

# Treatment colors for NPK experiment (N10 to N150)
TREATMENT_COLORS = {
    'N10': '#1f77b4',   # Blue - Very Low (10 kg N/ha)
    'N40': '#17becf',   # Cyan - Low (40 kg N/ha)
    'N60': '#2ca02c',   # Green - Optimal (60 kg N/ha)
    'N100': '#ff7f0e',  # Orange - Excessive (100 kg N/ha)
    'N150': '#d62728'   # Red - Very Excessive (150 kg N/ha)
}

TREATMENT_DESCRIPTIONS = {
    'N10': 'Very Low (10 kg N/ha)',
    'N40': 'Low (40 kg N/ha)',
    'N60': 'Optimal (60 kg N/ha)',
    'N100': 'Excessive (100 kg N/ha)',
    'N150': 'Very Excessive (150 kg N/ha)'
}

TREATMENT_ORDER = ['N10', 'N40', 'N60', 'N100', 'N150']

# NPK Treatment tree assignments
NPK_TREATMENTS = {
    'N10':  [3, 30, 42, 46, 63],
    'N40':  [5, 19, 44, 49, 67],
    'N60':  [12, 29, 43, 58, 61],
    'N100': [15, 18, 40, 47, 68],
    'N150': [13, 24, 35, 57, 74]
}

# Year colors for temporal analyses
YEAR_COLORS = {
    2021: '#90EE90',  # Light Green
    2022: '#32CD32',  # Lime Green
    2023: '#228B22',  # Forest Green
    2024: '#006400'   # Dark Green
}

YEAR_ORDER = [2021, 2022, 2023, 2024]

# LNC (Leaf Nitrogen Content) band colors
# Note: Colors are inverted from original - Blue for deficient, Red for excess
LNC_BAND_COLORS = {
    'Deficient': 'rgba(30, 144, 255, 0.25)',    # Blue (Dodger Blue)
    'Low': 'rgba(135, 206, 250, 0.25)',         # Light Blue (Light Sky Blue)
    'Optimum': 'rgba(78, 205, 196, 0.25)',      # Teal
    'High': 'rgba(255, 165, 0, 0.25)',          # Orange
    'Excess': 'rgba(255, 107, 107, 0.25)'       # Red (Salmon)
}

# UC Davis October reference thresholds for Citrus (scaled by 1.2)
LNC_OCT_THRESHOLDS = {
    'deficient_low': 2.64,   # Below = Deficient (was 2.2)
    'low_optimum': 2.88,     # Below = Low (was 2.4)
    'optimum_high': 3.24,    # Below = Optimum (was 2.7)
    'high_excess': 3.48      # Below = High, Above = Excess (was 2.9)
}

# Monthly scaling factors for LNC thresholds
LNC_MONTHLY_FACTORS = {
    1: 1.125, 2: 1.081, 3: 1.024, 4: 0.993, 5: 0.910, 6: 0.923,
    7: 0.973, 8: 1.024, 9: 1.024, 10: 1.000, 11: 1.088, 12: 1.125
}

# Month labels
MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# =============================================================================
# HTML STYLING
# =============================================================================

# Consistent CSS styles for all reports
HTML_STYLE = """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f5f5f5;
        color: #333;
    }
    h1 {
        text-align: center;
        color: #1b5e20;
        margin-bottom: 10px;
        font-size: 2.2em;
    }
    h2 {
        color: white;
        margin-top: 50px;
        padding: 15px;
        background: linear-gradient(90deg, #228B22, #32CD32);
        border-radius: 5px;
    }
    h3 {
        color: #1b5e20;
        margin-top: 30px;
        border-left: 4px solid #228B22;
        padding-left: 15px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .analysis-section {
        background: white;
        padding: 20px;
        margin: 20px 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .intro-box {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border: 2px solid #4CAF50;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
    }
    .discovery-box {
        background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
        border: 3px solid #2E7D32;
        padding: 25px;
        border-radius: 10px;
        margin: 25px 0;
    }
    .discovery-box h3 {
        color: #1b5e20;
        margin-top: 0;
        border: none;
        padding-left: 0;
    }
    .flow-arrow {
        text-align: center;
        font-size: 40px;
        color: #228B22;
        margin: 30px 0;
    }
    .methodology {
        background: #e8f4fd;
        border-left: 4px solid #1f77b4;
        padding: 15px 20px;
        margin-top: 15px;
        border-radius: 0 8px 8px 0;
    }
    .methodology h4 {
        margin: 0 0 10px 0;
        color: #333;
    }
    .key-observations {
        background: #f8f9fa;
        border-left: 4px solid #2ca02c;
        padding: 15px 20px;
        margin-top: 15px;
        border-radius: 0 8px 8px 0;
    }
    .key-observations h4 {
        margin: 0 0 10px 0;
        color: #333;
    }
    .key-observations ul {
        margin: 0;
        padding-left: 20px;
    }
    .key-observations li {
        margin-bottom: 8px;
        line-height: 1.5;
    }
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px 20px;
        margin-top: 15px;
        border-radius: 0 8px 8px 0;
    }
    table {
        border-collapse: collapse;
        margin: 15px auto;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px 12px;
        text-align: left;
    }
    th {
        background: linear-gradient(180deg, #e8f5e9, #c8e6c9);
        color: #1b5e20;
    }
    .treatment-table th {
        background: linear-gradient(180deg, #e8f5e9, #c8e6c9);
    }
    .timestamp {
        text-align: center;
        color: #666;
        margin-top: 40px;
        font-size: 0.9em;
    }
</style>
"""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_threshold_for_date(date, threshold_key):
    """Get the seasonally-adjusted LNC threshold for a specific date."""
    month = date.month
    factor = LNC_MONTHLY_FACTORS[month]
    return LNC_OCT_THRESHOLDS[threshold_key] * factor


def get_monthly_thresholds():
    """Generate monthly LNC thresholds based on seasonal patterns."""
    thresholds = {}
    for month in range(1, 13):
        factor = LNC_MONTHLY_FACTORS[month]
        thresholds[month] = {
            'deficient_low': LNC_OCT_THRESHOLDS['deficient_low'] * factor,
            'low_optimum': LNC_OCT_THRESHOLDS['low_optimum'] * factor,
            'optimum_high': LNC_OCT_THRESHOLDS['optimum_high'] * factor,
            'high_excess': LNC_OCT_THRESHOLDS['high_excess'] * factor
        }
    return thresholds


# =============================================================================
# DATA PATHS
# =============================================================================

import os

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# Dataset paths
UNIFIED_DATASET_PATH = os.path.join(DATA_DIR, 'unified_dataset.parquet')
NPK_DATASET_PATH = os.path.join(DATA_DIR, 'npk_5_treatments_samples.csv')
SPECTRAL_DATA_PATH = os.path.join(DATA_DIR, 'spectral_data.csv')
ISRAEL_LOCATIONS_PATH = os.path.join(DATA_DIR, 'israel_locations.json')
