"""
GeoSlide - Dataset Analytics Page
====================================
UI redesign: matches the shared design system (`frontend/assets/
design_system.css` — the same tokens + `.ds-*` classes Home.py and the
current Prediction page already use). Every visual value below is a
`.ds-*` class or a `var(--ds-*)` token (or a small rgba refinement of
one), the same approach used to bring Prediction onto this system.

NOTE ON APP-WIDE CONSISTENCY: as of this redesign, Home.py and the
Prediction page are on this shared light `design_system.css`. The SHAP
Analysis and Historical Map pages are still on the older page-scoped
dark theme (`--gs-bg: #0F172A`) and have not been migrated yet. This
page is brought in line with Home/Prediction — the app's current,
up-to-date visual language — rather than the older dark theme, exactly
as was done for Prediction previously.

WHAT CHANGED vs. what did not
------------------------------
Changed (presentation only):
  - Full visual redesign: hero card with an analytics illustration, a
    KPI panel, chart cards with consistent headers, a Statistical
    Insights panel, a Data Preview card, and a Summary card.
  - CSS: replaced the page's old standalone dark-theme stylesheet with
    the shared design_system.css tokens/classes.
  - Section *order* changed to match the requested layout (Hero → KPIs
    → Visual Analytics → Statistical Insights → Data Preview →
    Summary). Because Streamlit renders top-to-bottom as the script
    executes, the `missing_values_total` / `missing_values_pct`
    calculation (needed by both Statistical Insights and Summary) was
    *moved earlier* in the script so it runs before those sections
    instead of after the old "Dataset Information" section. The
    formula itself is byte-for-byte the same
    (`dataset_df.isna().sum().sum()` / percentage of all cells) — only
    *when* it runs changed, not *what* it computes.
  - The old standalone "Dataset Information" section (name, source,
    target column, feature list) was folded into the new Summary
    section rather than dropped, so no existing information
    disappears from the page.

NOT changed (verified untouched):
  - Dataset loading (`load_dataset`, `_generate_placeholder_dataset`,
    `_find_column`, `CANDIDATE_DATASET_PATHS`) — byte-for-byte.
  - Every Plotly figure (target pie chart, rainfall/slope/soil-
    moisture histograms, correlation heatmap) uses the exact same
    px.* calls, same columns, same color sequences, same
    update_layout() calls, and the same `CHART_TEMPLATE`/
    `COLOR_SEQUENCE` constants as before.
  - All statistics (total_records, total_features, landslide_events,
    non_landslide_events, missing_values_total/pct, corr_matrix) are
    computed with the exact same pandas/numpy operations as before.
  - The dataset preview still shows `dataset_df.head(100)`.
  - The four existing "Insights" statements (_balance_insight,
    _missing_insight, feature count, target-column-present) are
    reused verbatim, just presented as individual cards instead of a
    bullet list.
  - Navigation, sidebar, and every other page's files.
"""

import glob
import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from components.sidebar import render_sidebar
from components.status_panel import render_status_panel
from utils.theme import load_styles


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Dataset Analytics | GeoSlide",
    page_icon="📊",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent.parent
DESIGN_SYSTEM_CSS_FILE = ROOT / "assets" / "design_system.css"
HERO_ILLUSTRATION_FILE = ROOT / "assets" / "images" / "dataset_analytics.png"


# ---------------------------------------------------------------------------
# Dataset Loading (UNCHANGED)
# ---------------------------------------------------------------------------

TARGET_COLUMN = "landslide"
DATASET_NAME = "GeoSlide Landslide Training Dataset"
DATASET_SOURCE = "GeoSlide processed training data (local project dataset)"

# Common candidate locations for the real training dataset. The first
# match found will be used.
CANDIDATE_DATASET_PATHS = [
    "datasets/wsn_landslide_data.csv",
    "../datasets/wsn_landslide_data.csv",
    "data/processed/landslide_dataset.csv",
    "data/landslide_dataset.csv",
    "data/train.csv",
    "../data/processed/landslide_dataset.csv",
    "../data/landslide_dataset.csv",
    "../data/train.csv",
    "backend/data/landslide_dataset.csv",
]

PLACEHOLDER_FEATURE_COLUMNS = [
    "rainfall", "rainfall_3d", "rainfall_7d", "temperature", "humidity",
    "slope_angle", "aspect", "elevation", "distance_to_road", "proximity_to_water",
    "soil_saturation", "soil_moisture", "soil_ph", "clay_content", "sand_content",
    "silt_content", "soil_erosion_rate", "soil_temperature", "pore_water_pressure",
    "ndvi_index", "vegetation_cover", "earthquake_activity", "historical_landslide_count",
    "microseismic_activity", "acoustic_emission", "soil_strain", "tdr_reflection_index",
]


def _generate_placeholder_dataset(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    """
    Generate a realistic, self-consistent placeholder dataset matching
    the GeoSlide feature schema, so every chart on this page has data
    to render even when the real training dataset is unavailable.
    """
    rng = np.random.default_rng(seed)

    data = {
        "rainfall": rng.gamma(2.0, 15.0, n).round(2),
        "rainfall_3d": rng.gamma(2.5, 40.0, n).round(2),
        "rainfall_7d": rng.gamma(3.0, 60.0, n).round(2),
        "temperature": rng.normal(22.0, 6.0, n).round(2),
        "humidity": np.clip(rng.normal(65.0, 15.0, n), 0, 100).round(2),
        "slope_angle": np.clip(rng.normal(28.0, 12.0, n), 0, 90).round(2),
        "aspect": rng.uniform(0, 360, n).round(1),
        "elevation": np.clip(rng.normal(900.0, 400.0, n), 0, None).round(1),
        "distance_to_road": np.clip(rng.exponential(300.0, n), 0, None).round(1),
        "proximity_to_water": np.clip(rng.exponential(200.0, n), 0, None).round(1),
        "soil_saturation": np.clip(rng.normal(55.0, 20.0, n), 0, 100).round(2),
        "soil_moisture": np.clip(rng.normal(35.0, 15.0, n), 0, 100).round(2),
        "soil_ph": np.clip(rng.normal(6.5, 0.8, n), 3.5, 9.5).round(2),
        "clay_content": np.clip(rng.normal(30.0, 10.0, n), 0, 100).round(2),
        "sand_content": np.clip(rng.normal(40.0, 12.0, n), 0, 100).round(2),
        "silt_content": np.clip(rng.normal(30.0, 10.0, n), 0, 100).round(2),
        "soil_erosion_rate": np.clip(rng.exponential(2.0, n), 0, None).round(2),
        "soil_temperature": rng.normal(18.0, 5.0, n).round(2),
        "pore_water_pressure": np.clip(rng.normal(20.0, 10.0, n), 0, None).round(2),
        "ndvi_index": np.clip(rng.normal(0.4, 0.2, n), -1, 1).round(3),
        "vegetation_cover": np.clip(rng.normal(50.0, 20.0, n), 0, 100).round(2),
        "earthquake_activity": np.clip(rng.exponential(1.5, n), 0, 10).round(2),
        "historical_landslide_count": rng.poisson(2.0, n),
        "microseismic_activity": np.clip(rng.exponential(0.4, n), 0, None).round(3),
        "acoustic_emission": np.clip(rng.exponential(15.0, n), 0, None).round(2),
        "soil_strain": np.clip(rng.exponential(0.1, n), 0, None).round(3),
        "tdr_reflection_index": np.clip(rng.normal(1.5, 0.5, n), 0, None).round(3),
    }

    df = pd.DataFrame(data)

    # Construct a target label loosely correlated with several key
    # drivers, so the correlation heatmap and distributions look
    # realistic rather than pure noise.
    risk_score = (
        0.35 * (df["soil_saturation"] / 100.0)
        + 0.25 * (df["rainfall_7d"] / df["rainfall_7d"].max())
        + 0.20 * (df["slope_angle"] / 90.0)
        + 0.15 * (df["pore_water_pressure"] / max(df["pore_water_pressure"].max(), 1))
        - 0.15 * (df["vegetation_cover"] / 100.0)
        + rng.normal(0, 0.08, n)
    )
    threshold = np.quantile(risk_score, 0.55)
    df[TARGET_COLUMN] = (risk_score >= threshold).astype(int)

    # Introduce a small amount of realistic missingness.
    for col in rng.choice(PLACEHOLDER_FEATURE_COLUMNS, size=5, replace=False):
        missing_idx = rng.choice(n, size=int(n * 0.02), replace=False)
        df.loc[missing_idx, col] = np.nan

    return df


@st.cache_data(show_spinner=False)
def load_dataset() -> tuple[pd.DataFrame, bool, str]:
    """
    Attempt to load the real GeoSlide training dataset from a set of
    likely local paths. Falls back to a generated placeholder dataset
    if none can be found or loaded.

    Returns:
        (dataframe, is_real_data, source_description)
    """
    for path in CANDIDATE_DATASET_PATHS:
        matches = glob.glob(path)
        for match in matches:
            try:
                if os.path.getsize(match) == 0:
                    continue
                df = pd.read_csv(match)
                if df.empty or df.shape[1] < 2:
                    continue
                return df, True, match
            except Exception:
                continue

    return _generate_placeholder_dataset(), False, "Generated placeholder data"


dataset_df, is_real_dataset, dataset_source = load_dataset()

# Resolve the target column: use TARGET_COLUMN if present, otherwise
# fall back to the last column (common convention) so the page still
# works against an unknown real dataset schema.
if TARGET_COLUMN not in dataset_df.columns:
    likely_target_matches = [
        c for c in dataset_df.columns if c.lower() in ("landslide", "target", "label", "risk")
    ]
    resolved_target_column = likely_target_matches[0] if likely_target_matches else dataset_df.columns[-1]
else:
    resolved_target_column = TARGET_COLUMN


def _find_column(candidates: list) -> str:
    """Find the first matching column name (case-insensitive, partial match)."""
    lower_map = {c.lower(): c for c in dataset_df.columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    for candidate in candidates:
        for col_lower, col_original in lower_map.items():
            if candidate.lower() in col_lower:
                return col_original
    return None


rainfall_col = _find_column(["rainfall", "rain"])
slope_col = _find_column(["slope_angle", "slope"])
soil_moisture_col = _find_column(["soil_moisture", "moisture"])


# ---------------------------------------------------------------------------
# Dataset Overview statistics (UNCHANGED formulas — same as before, just
# grouped together near the top of the script since both the KPI cards
# and the later Statistical Insights / Summary sections need them).
# ---------------------------------------------------------------------------

total_records = len(dataset_df)
total_features = max(dataset_df.shape[1] - 1, 0)

if resolved_target_column in dataset_df.columns:
    target_series = dataset_df[resolved_target_column]
    landslide_events = int((target_series == 1).sum()) if target_series.dropna().isin([0, 1]).all() \
        else int((target_series.astype(str).str.lower().isin(["1", "true", "yes", "landslide"])).sum())
    non_landslide_events = total_records - landslide_events
else:
    landslide_events = 0
    non_landslide_events = total_records

# Same formula previously computed later in the script (old "Dataset
# Information" section) — only its position moved earlier so the new
# Statistical Insights section (which now renders before Data Preview)
# can use it too.
missing_values_total = int(dataset_df.isna().sum().sum())
missing_values_pct = (
    round((missing_values_total / (dataset_df.shape[0] * dataset_df.shape[1])) * 100, 2)
    if dataset_df.size > 0
    else 0.0
)

dataset_name_display = DATASET_NAME if not is_real_dataset else os.path.basename(dataset_source)
source_display = dataset_source if is_real_dataset else DATASET_SOURCE


# ---------------------------------------------------------------------------
# Shared design system (same files Home.py / Prediction load)
# ---------------------------------------------------------------------------

st.markdown(f"<style>{load_styles()}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{DESIGN_SYSTEM_CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page wiring CSS — same approach as the Prediction page: soft
# card borders + layered elevation shadows, everything resolved
# through var(--ds-*) tokens. No layout/spacing changes.
# ---------------------------------------------------------------------------

ANALYTICS_WIRING_CSS = """
[data-testid="stAppViewContainer"] {
    background: var(--ds-bg) !important;
    --gs-border-soft: rgba(28, 35, 31, 0.07);
    --gs-border-soft-strong: rgba(28, 35, 31, 0.12);
    --gs-shadow-card: 0 1px 2px rgba(28, 35, 31, 0.04), 0 6px 16px rgba(28, 35, 31, 0.05);
    --gs-shadow-card-hover: 0 2px 6px rgba(28, 35, 31, 0.05), 0 16px 34px rgba(28, 35, 31, 0.09);
}

[data-testid="stAppViewContainer"] .block-container {
    padding: var(--ds-space-6) var(--ds-container-padding-desktop) var(--ds-space-10) !important;
    max-width: var(--ds-container-max);
}

.gs-section-spacer { height: var(--ds-space-6); }

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4 {
    color: var(--ds-text-primary) !important;
    letter-spacing: var(--ds-tracking-tight);
}

[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li,
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
    color: var(--ds-text-secondary) !important;
}

/* ============================================================
   BASELINE — every real bordered container starts here: soft
   border + layered shadow, elevation does the separating instead
   of a heavy outline.
   ============================================================ */
[data-testid="stAppViewContainer"] [data-testid="stLayoutWrapper"] {
    background: var(--ds-surface) !important;
    border: 1px solid var(--gs-border-soft) !important;
    border-style: solid !important;
    border-radius: var(--ds-radius-lg) !important;
    box-shadow: var(--gs-shadow-card) !important;
    outline: none !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base),
                border-color var(--ds-transition-base), background var(--ds-transition-base);
}
/* Clean-border safety net — neutralizes any legacy/duplicate default
   Streamlit border markup that would otherwise stack under the
   custom border above and read as a rough, doubled outline. Purely
   cosmetic: no size, spacing, or layout is touched. */
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stAppViewContainer"] [data-testid="stLayoutWrapper"] > div {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
[data-testid="stAppViewContainer"] button {
    outline: none !important;
    border-style: solid !important;
}
[data-testid="stAppViewContainer"] button:focus,
[data-testid="stAppViewContainer"] button:focus-visible {
    outline: none !important;
}

/* Recessed outer panels (KPI section, Statistical Insights, Data
   Preview, Summary) — a slightly recessed surface so panel -> inner
   card hierarchy reads clearly, same as Prediction's section panels. */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-"]) {
    background: var(--ds-bg-subtle) !important;
    border: 1px solid var(--gs-border-soft) !important;
    box-shadow: var(--ds-shadow-xs) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}

/* ============================================================
   SECTION 1 — HERO
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-hero"]) {
    background: var(--ds-surface) !important;
    box-shadow: var(--ds-shadow-md) !important;
    padding: var(--ds-space-8) !important;
}
.gs-hero-copy {
    max-width: 94%;
    font-size: 1.02rem !important;
    line-height: var(--ds-leading-loose) !important;
    color: var(--ds-text-secondary) !important;
    font-weight: var(--ds-weight-regular);
    margin-top: var(--ds-space-3);
}
.gs-display-md {
    font-size: 2.2rem !important;
    line-height: 1.15 !important;
    margin: var(--ds-space-3) 0 0 !important;
}
[class*="st-key-hero-illo-wrap"] {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 180px;
}
[class*="st-key-hero-illo-wrap"] img {
    width: 100%;
    max-width: 240px;
    height: auto;
    animation: gs-hero-float 7s ease-in-out infinite;
    filter: drop-shadow(0 18px 30px rgba(28, 35, 31, 0.12));
}
@keyframes gs-hero-float {
    0%, 100% { transform: translateY(0px); }
    50%      { transform: translateY(-10px); }
}
@media (prefers-reduced-motion: reduce) {
    [class*="st-key-hero-illo-wrap"] img { animation: none; }
}
.gs-hero-alert-wrap { margin-top: var(--ds-space-4); max-width: 94%; }

/* ============================================================
   SECTION 2 — KPI CARDS (same pattern as Home.py's KPI row)
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kpi-card-"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-5) !important;
    height: 148px;
    display: flex !important;
    flex-direction: column;
    justify-content: center;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kpi-card-"]):hover {
    transform: translateY(-3px);
    box-shadow: var(--gs-shadow-card-hover) !important;
    border-color: var(--gs-border-soft-strong) !important;
}
.gs-kpi-icon-row { display: flex; align-items: center; gap: var(--ds-space-3); margin-bottom: var(--ds-space-2); }
.gs-kpi-icon-row .ds-kpi-icon {
    width: 38px; height: 38px; border-radius: var(--ds-radius-sm);
    display: flex; align-items: center; justify-content: center;
    transition: transform var(--ds-transition-base);
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kpi-card-"]):hover .ds-kpi-icon { transform: scale(1.08); }
.gs-kpi-value { font-size: 1.85rem !important; letter-spacing: -0.01em; color: var(--ds-text-primary); font-weight: var(--ds-weight-extrabold); }
.gs-kpi-desc { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: 3px; }

/* ============================================================
   SECTION 3 — VISUAL ANALYTICS (chart cards)
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-chart-card-"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-6) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-chart-card-"]):hover {
    border-color: var(--gs-border-soft-strong) !important;
    box-shadow: var(--gs-shadow-card-hover) !important;
}
.gs-chart-card-header {
    display: flex;
    align-items: center;
    gap: var(--ds-space-3);
    margin-bottom: var(--ds-space-4);
}
.gs-chart-card-title { font-size: var(--ds-text-h3); font-weight: var(--ds-weight-semibold); color: var(--ds-text-primary); }
.gs-chart-card-desc { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: 1px; }
.gs-chart-caption { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: var(--ds-space-3); }

/* ============================================================
   SECTION 4 — STATISTICAL INSIGHTS
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-insight-card-"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-5) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-insight-card-"]):hover {
    transform: translateY(-2px);
    box-shadow: var(--gs-shadow-card-hover) !important;
}
.gs-insight-header { display: flex; align-items: center; gap: var(--ds-space-3); margin-bottom: var(--ds-space-2); }
.gs-insight-title { font-size: var(--ds-text-sm); font-weight: var(--ds-weight-bold); color: var(--ds-text-primary); }
.gs-insight-text { font-size: var(--ds-text-sm); color: var(--ds-text-secondary); line-height: var(--ds-leading-normal); }

/* ============================================================
   SECTION 5 — DATA PREVIEW
   ============================================================ */
[data-testid="stAppViewContainer"] [data-testid="stDataFrame"] {
    border-radius: var(--ds-radius-md) !important;
    overflow: hidden;
    border: 1px solid var(--gs-border-soft-strong) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stDataFrame"] [role="columnheader"] {
    position: sticky;
    top: 0;
    z-index: 1;
}

/* ============================================================
   SECTION 6 — SUMMARY
   ============================================================ */
.gs-summary-text {
    font-size: var(--ds-text-body-lg);
    color: var(--ds-text-primary);
    line-height: var(--ds-leading-loose);
}
.gs-summary-meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: var(--ds-space-3);
    margin-top: var(--ds-space-5);
}
.gs-summary-meta-item {
    background: var(--ds-surface);
    border: 1px solid var(--gs-border-soft-strong);
    border-radius: var(--ds-radius-sm);
    padding: var(--ds-space-3) var(--ds-space-4);
    box-shadow: var(--gs-shadow-card);
    flex: 1 1 220px;
}
.gs-summary-meta-label {
    font-size: var(--ds-text-xs); font-weight: var(--ds-weight-bold); text-transform: uppercase;
    letter-spacing: var(--ds-tracking-wide); color: var(--ds-text-tertiary);
}
.gs-summary-meta-value { font-size: var(--ds-text-sm); font-weight: var(--ds-weight-semibold); color: var(--ds-text-primary); margin-top: 2px; word-break: break-word; }
.gs-summary-meta-value code {
    background: var(--ds-bg-inset);
    color: var(--ds-brand-600);
    padding: 2px 8px;
    border-radius: var(--ds-radius-sm);
    font-size: var(--ds-text-xs);
}
[data-testid="stAppViewContainer"] [data-testid="stExpander"] {
    background: var(--ds-surface) !important;
    border: 1px solid var(--gs-border-soft-strong) !important;
    border-radius: var(--ds-radius-md) !important;
    box-shadow: none !important;
    margin-top: var(--ds-space-5);
}
[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary p {
    font-size: var(--ds-text-sm);
    font-weight: var(--ds-weight-semibold);
    color: var(--ds-text-primary) !important;
}
"""

st.markdown(f"<style>{ANALYTICS_WIRING_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar (shared, unmodified)
# ---------------------------------------------------------------------------

render_sidebar()


# ---------------------------------------------------------------------------
# Local icon set (page-scoped, same inline-SVG pattern Home.py /
# Prediction use — decorative only, no emoji, no external assets).
# ---------------------------------------------------------------------------

_ICON_PATHS = {
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.3-4.3"/>',
    "database": '<ellipse cx="12" cy="5.5" rx="8" ry="2.7"/><path d="M4 5.5v13c0 1.5 3.6 2.7 8 2.7s8-1.2 8-2.7v-13"/><path d="M4 12c0 1.5 3.6 2.7 8 2.7s8-1.2 8-2.7"/>',
    "layers": '<path d="m12 3 8 4.2-8 4.2-8-4.2Z"/><path d="m4 12 8 4.2 8-4.2"/><path d="m4 16.4 8 4.2 8-4.2"/>',
    "alert-triangle": '<path d="M12 3.2 2.3 20h19.4L12 3.2Z"/><line x1="12" y1="9.5" x2="12" y2="14"/><circle cx="12" cy="17" r="0.9" fill="currentColor"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8 12.3 2.6 2.6L16.2 9"/>',
    "pie-chart": '<circle cx="12" cy="12" r="9"/><path d="M12 3v9l7.8 4.5"/>',
    "cloud-rain": '<path d="M7 15.5a4.3 4.3 0 0 1 .6-8.6 5.7 5.7 0 0 1 10.6 2.6 3.8 3.8 0 0 1-.7 6H7Z"/><path d="M8 19v1.3M12 19v1.8M16 19v1.3"/>',
    "mountain": '<path d="m3.5 19 6-11 3.5 6 2.5-4 5 9Z"/>',
    "droplet": '<path d="M12 2.8s6.2 7 6.2 11.5A6.2 6.2 0 0 1 5.8 14.3C5.8 9.8 12 2.8 12 2.8Z"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "table": '<rect x="3" y="3" width="18" height="18" rx="1.5"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
    "file-text": '<rect x="5" y="3" width="14" height="18" rx="2"/><line x1="8" y1="8" x2="16" y2="8"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="8" y1="16" x2="12" y2="16"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5.2"/><circle cx="12" cy="12" r="1.4" fill="currentColor"/>',
    "scale": '<path d="M12 3v18M7 7l-4 8a4 4 0 0 0 8 0Z"/><path d="M17 7l-4 8a4 4 0 0 0 8 0Z"/><path d="M5 7h14"/>',
}


def _icon(name: str, size: int = 20, stroke_width: float = 1.8) -> str:
    """Inline Lucide-style SVG icon (no emoji)."""
    body = _ICON_PATHS.get(name, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" '
        f'stroke-linejoin="round" style="display:block;">{body}</svg>'
    )


def _hero_illustration() -> str:
    """Small decorative analytics illustration — bars + a trend line,
    built the same way Prediction's hero illustration is (inline SVG,
    design tokens for color, purely decorative)."""
    return (
        '<svg viewBox="0 0 220 200" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="110" cy="100" r="86" stroke="var(--ds-brand-200)" stroke-width="1.4" opacity="0.5"/>'
        '<rect x="38" y="120" width="22" height="50" rx="3" fill="var(--ds-brand-100)" stroke="var(--ds-brand-300)" stroke-width="1.5"/>'
        '<rect x="76" y="90" width="22" height="80" rx="3" fill="var(--ds-brand-100)" stroke="var(--ds-brand-300)" stroke-width="1.5"/>'
        '<rect x="114" y="60" width="22" height="110" rx="3" fill="var(--ds-brand-50)" stroke="var(--ds-brand-400)" stroke-width="1.5"/>'
        '<rect x="152" y="105" width="22" height="65" rx="3" fill="var(--ds-brand-100)" stroke="var(--ds-brand-300)" stroke-width="1.5"/>'
        '<polyline points="49,108 87,78 125,48 163,90" stroke="var(--ds-accent-500)" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="49" cy="108" r="4" fill="var(--ds-accent-500)"/>'
        '<circle cx="87" cy="78" r="4" fill="var(--ds-accent-500)"/>'
        '<circle cx="125" cy="48" r="4.5" fill="var(--ds-brand-600)"/>'
        '<circle cx="163" cy="90" r="4" fill="var(--ds-accent-500)"/>'
        '<line x1="30" y1="170" x2="182" y2="170" stroke="var(--ds-border-strong)" stroke-width="1.5"/>'
        '</svg>'
    )


def _kpi_card(icon: str, chip_class: str, label: str, value: str, desc: str, key: str) -> None:
    with st.container(border=True, key=key):
        st.markdown(
            f"""
            <div class="gs-kpi-icon-row">
                <div class="ds-kpi-icon {chip_class}" style="margin-bottom:0;">{_icon(icon, 18)}</div>
                <div class="ds-kpi-label" style="margin-top:1px;">{label}</div>
            </div>
            <div class="gs-kpi-value">{value}</div>
            <div class="gs-kpi-desc">{desc}</div>
            """,
            unsafe_allow_html=True,
        )


def _chart_card_header(icon: str, chip_class: str, title: str, desc: str) -> None:
    st.markdown(
        f"""
        <div class="gs-chart-card-header">
            <div class="ds-kpi-icon {chip_class}" style="width:40px;height:40px;margin-bottom:0;">{_icon(icon, 18)}</div>
            <div>
                <div class="gs-chart-card-title">{title}</div>
                <div class="gs-chart-card-desc">{desc}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _insight_card(icon: str, chip_class: str, title: str, text: str, key: str) -> None:
    with st.container(border=True, key=key):
        st.markdown(
            f"""
            <div class="gs-insight-header">
                <div class="ds-kpi-icon {chip_class}" style="width:36px;height:36px;margin-bottom:0;">{_icon(icon, 16)}</div>
                <div class="gs-insight-title">{title}</div>
            </div>
            <div class="gs-insight-text">{text}</div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SECTION 1 — HERO
# ============================================================

with st.container(border=True, key="section-hero"):
    left, right = st.columns([64, 36], gap="large")

    with left:
        st.markdown(
            f'<div class="ds-eyebrow">{_icon("search", 14, 2)}<span>&nbsp;DATASET ANALYTICS</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ds-display gs-display-md">Dataset Analytics Dashboard</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="ds-body-lg gs-hero-copy">
            Explore the complete landslide training dataset through interactive
            visualizations, statistical summaries, feature relationships, and
            quality analysis. Understand the data powering GeoSlide AI before
            prediction and model interpretation.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not is_real_dataset:
            st.markdown(
                f"""
                <div class="gs-hero-alert-wrap">
                    <div class="ds-alert ds-alert-warning">
                        {_icon("alert-triangle", 18)}
                        <div>The real training dataset could not be located. Displaying
                        generated placeholder data instead so every chart below still
                        renders correctly.</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        render_status_panel(
            _icon("database", 14, 2),
            [
                ("Dataset", "Loaded"),
                ("Statistical Analysis", "Ready"),
                ("Visualizations", "Active"),
                ("Correlation Engine", "Online"),
            ],
        )

    with right:
        with st.container(key="hero-illo-wrap"):
            st.image(str(HERO_ILLUSTRATION_FILE), use_container_width=True)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 2 — KPI CARDS (UNCHANGED statistics: total_records,
# total_features, landslide_events, non_landslide_events)
# ============================================================

with st.container(border=True, key="section-kpi"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("layers", 20)} Dataset Overview</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">Top-level metrics for the dataset currently loaded</div>',
        unsafe_allow_html=True,
    )

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4, gap="medium")
    with kpi_col1:
        _kpi_card("database", "ds-chip-brand", "Total Records", f"{total_records:,}", "Rows in the dataset", "kpi-card-0")
    with kpi_col2:
        _kpi_card("layers", "ds-chip-accent", "Features", f"{total_features:,}", "Input columns (excl. target)", "kpi-card-1")
    with kpi_col3:
        _kpi_card("alert-triangle", "ds-chip-amber", "Landslide Events", f"{landslide_events:,}", "Positive-class records", "kpi-card-2")
    with kpi_col4:
        _kpi_card("check-circle", "ds-chip-brand", "Non-Landslide Events", f"{non_landslide_events:,}", "Negative-class records", "kpi-card-3")

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 3 — VISUAL ANALYTICS (UNCHANGED chart generation, one
# premium card each, consistent titles/spacing)
# ============================================================

st.markdown(
    f'<div class="ds-section-title">{_icon("pie-chart", 20)} Visual Analytics</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="ds-section-subtitle">Distribution and correlation charts computed directly from the dataset</div>',
    unsafe_allow_html=True,
)

CHART_TEMPLATE = "plotly_white"
COLOR_SEQUENCE = ["#2E86AB", "#E67E22", "#27AE60", "#8E44AD", "#C0392B"]

chart_row1_col1, chart_row1_col2 = st.columns(2, gap="medium")

# 1. Target Distribution
with chart_row1_col1:
    with st.container(border=True, key="chart-card-target"):
        _chart_card_header("pie-chart", "ds-chip-brand", "Target Distribution", "Share of landslide vs. non-landslide records")
        if resolved_target_column in dataset_df.columns:
            target_counts = (
                dataset_df[resolved_target_column]
                .map({1: "Landslide", 0: "No Landslide"})
                .fillna(dataset_df[resolved_target_column])
                .value_counts()
                .reset_index()
            )
            target_counts.columns = ["Class", "Count"]
            fig_target = px.pie(
                target_counts,
                names="Class",
                values="Count",
                hole=0.45,
                color_discrete_sequence=COLOR_SEQUENCE,
                template=CHART_TEMPLATE,
            )
            fig_target.update_traces(textinfo="percent+label")
            fig_target.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_target)
        else:
            st.info("Target column not available in this dataset.")

# 2. Rainfall Distribution
with chart_row1_col2:
    with st.container(border=True, key="chart-card-rainfall"):
        _chart_card_header("cloud-rain", "ds-chip-accent", "Rainfall Distribution", "Frequency of recorded rainfall values")
        if rainfall_col:
            fig_rainfall = px.histogram(
                dataset_df,
                x=rainfall_col,
                nbins=40,
                color_discrete_sequence=[COLOR_SEQUENCE[0]],
                template=CHART_TEMPLATE,
            )
            fig_rainfall.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis_title="Rainfall",
                yaxis_title="Frequency",
            )
            st.plotly_chart(fig_rainfall)
        else:
            st.info("No rainfall column found in this dataset.")

chart_row2_col1, chart_row2_col2 = st.columns(2, gap="medium")

# 3. Slope Angle Distribution
with chart_row2_col1:
    with st.container(border=True, key="chart-card-slope"):
        _chart_card_header("mountain", "ds-chip-brand", "Slope Angle Distribution", "Distribution of terrain slope angles")
        if slope_col:
            fig_slope = px.histogram(
                dataset_df,
                x=slope_col,
                nbins=40,
                color_discrete_sequence=[COLOR_SEQUENCE[1]],
                template=CHART_TEMPLATE,
            )
            fig_slope.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis_title="Slope Angle (°)",
                yaxis_title="Frequency",
            )
            st.plotly_chart(fig_slope)
        else:
            st.info("No slope angle column found in this dataset.")

# 4. Soil Moisture Distribution
with chart_row2_col2:
    with st.container(border=True, key="chart-card-moisture"):
        _chart_card_header("droplet", "ds-chip-accent", "Soil Moisture Distribution", "Distribution of recorded soil moisture values")
        if soil_moisture_col:
            fig_moisture = px.histogram(
                dataset_df,
                x=soil_moisture_col,
                nbins=40,
                color_discrete_sequence=[COLOR_SEQUENCE[2]],
                template=CHART_TEMPLATE,
            )
            fig_moisture.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis_title="Soil Moisture (%)",
                yaxis_title="Frequency",
            )
            st.plotly_chart(fig_moisture)
        else:
            st.info("No soil moisture column found in this dataset.")

st.write("")

# 5. Correlation Heatmap (UNCHANGED calculation, larger standalone card)
with st.container(border=True, key="chart-card-heatmap"):
    _chart_card_header(
        "grid", "ds-chip-amber", "Correlation Heatmap",
        "Pairwise correlation between numeric features (capped to the first 20 numeric columns for readability)",
    )

    numeric_df = dataset_df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] >= 2:
        # Cap to a reasonable number of columns for a readable heatmap.
        corr_columns = list(numeric_df.columns[:20])
        corr_matrix = numeric_df[corr_columns].corr()

        fig_corr = px.imshow(
            corr_matrix,
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
            template=CHART_TEMPLATE,
        )
        fig_corr.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=600,
        )
        st.plotly_chart(fig_corr)
        st.markdown(
            '<div class="gs-chart-caption">Red indicates positive correlation. '
            "Blue indicates negative correlation.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Not enough numeric columns to compute a correlation heatmap.")

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 4 — STATISTICAL INSIGHTS
# (Reuses the exact same insight statements that were previously
# computed in the old "Insights" section — same logic, same values,
# just presented as individual cards instead of a bullet list.)
# ============================================================

_class_total = landslide_events + non_landslide_events
_minority_share = (min(landslide_events, non_landslide_events) / _class_total) if _class_total else 0.0
_balance_insight = (
    "Reasonably balanced target classes."
    if _minority_share >= 0.4
    else "Imbalanced target classes — the minority class makes up "
    f"{_minority_share * 100:.1f}% of records."
)
_missing_insight = (
    "No missing values anywhere in the dataset."
    if missing_values_total == 0
    else f"{missing_values_total:,} missing values ({missing_values_pct}% of all cells)."
)
_feature_insight = f"{total_features:,} engineered and raw features are available for modeling."
_target_insight = (
    f"A clear target column (\u201c{resolved_target_column}\u201d) is present, "
    "suitable for supervised learning."
)

with st.container(border=True, key="section-insights"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("target", 20)} Statistical Insights</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">What the charts and statistics above say about this dataset</div>',
        unsafe_allow_html=True,
    )

    insight_col1, insight_col2 = st.columns(2, gap="medium")
    with insight_col1:
        _insight_card("scale", "ds-chip-brand", "Class Balance", _balance_insight, "insight-card-balance")
    with insight_col2:
        _insight_card(
            "check-circle" if missing_values_total == 0 else "alert-triangle",
            "ds-chip-accent" if missing_values_total == 0 else "ds-chip-amber",
            "Data Completeness", _missing_insight, "insight-card-missing",
        )

    insight_col3, insight_col4 = st.columns(2, gap="medium")
    with insight_col3:
        _insight_card("layers", "ds-chip-amber", "Feature Space", _feature_insight, "insight-card-features")
    with insight_col4:
        _insight_card("target", "ds-chip-brand", "Target Suitability", _target_insight, "insight-card-target")

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 5 — DATA PREVIEW (UNCHANGED data: dataset_df.head(100))
# ============================================================

with st.container(border=True, key="section-preview"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("table", 20)} Data Preview</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">First rows of the training dataset, exactly as loaded</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(dataset_df.head(100), width="stretch", hide_index=True, height=420)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 6 — SUMMARY
# (Narrative composed only from statistics already computed above —
# no new calculations. Also folds in the old "Dataset Information"
# details — name, source, target column, feature list — so nothing
# that used to be on this page is lost.)
# ============================================================

_landslide_pct = (landslide_events / total_records * 100) if total_records else 0.0
_summary_quality_phrase = "very clean" if missing_values_total == 0 else "mostly clean, with a small amount of missing data"

_summary_text = (
    f"The {dataset_name_display} contains {total_records:,} records across "
    f"{total_features:,} features, with {landslide_events:,} landslide-positive "
    f"records ({_landslide_pct:.1f}%) and {non_landslide_events:,} negative "
    f"records. The data is {_summary_quality_phrase}"
    f"{'' if missing_values_total == 0 else f' ({missing_values_pct}% of all cells)'}, "
    f"and includes rainfall, terrain, soil, vegetation, and sensor-derived "
    f"features suitable for training the GeoSlide landslide risk model."
)

with st.container(border=True, key="section-summary"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("file-text", 20)} Summary</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="gs-summary-text">{_summary_text}</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="gs-summary-meta-row">
            <div class="gs-summary-meta-item">
                <div class="gs-summary-meta-label">Dataset Name</div>
                <div class="gs-summary-meta-value">{dataset_name_display}</div>
            </div>
            <div class="gs-summary-meta-item">
                <div class="gs-summary-meta-label">Target Column</div>
                <div class="gs-summary-meta-value"><code>{resolved_target_column}</code></div>
            </div>
            <div class="gs-summary-meta-item">
                <div class="gs-summary-meta-label">Source</div>
                <div class="gs-summary-meta-value">{source_display}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("View feature list", expanded=False):
        feature_cols = [c for c in dataset_df.columns if c != resolved_target_column]
        st.write(", ".join(feature_cols) if feature_cols else "No feature columns available.")