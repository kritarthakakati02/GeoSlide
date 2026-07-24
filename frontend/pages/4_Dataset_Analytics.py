"""
GeoSlide - Dataset Analytics Page
====================================
Phase 10.6: Dataset Analytics.

This page gives an analytical overview of the dataset used to train
the GeoSlide landslide prediction model: top-level summary metrics,
distribution charts for key features, a correlation heatmap, a raw
data preview, and dataset metadata.

NOTE: If the real training dataset cannot be located/loaded, this page
automatically falls back to a generated placeholder dataset (same
schema/shape) so every chart renders correctly and the page remains
fully demoable.

UI note: this file was redesigned into a professional "data
intelligence dashboard" (page-scoped dark theme, hover KPI cards, one
premium card per chart, a larger standalone correlation-heatmap card,
a modern dataset-preview card, a compact dataset-info card, and an
insights card). This mirrors the same redesign approach already used
on the Prediction, SHAP Analysis, and Historical Map pages for visual
consistency across the app.

Nothing about *what* is computed changed:
    - Dataset loading (`load_dataset`, `_generate_placeholder_dataset`,
      `_find_column`) is byte-for-byte unchanged.
    - Every Plotly figure (target pie chart, rainfall/slope/soil-
      moisture histograms, correlation heatmap) uses the exact same
      px.* calls, same columns, same color sequences, and same
      update_layout() calls as before.
    - All statistics (total_records, total_features, landslide_events,
      non_landslide_events, missing_values_total/pct, corr_matrix) are
      computed with the exact same pandas/numpy operations as before.
    - The dataset preview still shows `dataset_df.head(100)`.

Only layout, typography, spacing, and presentation were touched.
"""

import glob
import os

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from components.sidebar import render_sidebar


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Dataset Analytics | GeoSlide",
    page_icon="📊",
    layout="wide",
)


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
# Sidebar
# ---------------------------------------------------------------------------

render_sidebar()


# ---------------------------------------------------------------------------
# Page-scoped dark theme + layout CSS
# ---------------------------------------------------------------------------
# Same scoping approach and design tokens (--gs-*) as the Prediction, SHAP
# Analysis, and Historical Map pages: everything lives under
# [data-testid="stAppViewContainer"] and is only ever injected while this
# script is the active page, so it cannot leak into other pages.

ANALYTICS_CSS = """
:root {
    --gs-bg: #0F172A;
    --gs-card: #1E293B;
    --gs-primary: #10B981;
    --gs-accent: #3B82F6;
    --gs-danger: #EF4444;
    --gs-text: #E2E8F0;
    --gs-muted: #94A3B8;
    --gs-border: rgba(148, 163, 184, 0.14);
    --gs-radius: 18px;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 85% 0%, #132239 0%, var(--gs-bg) 45%) !important;
}

[data-testid="stAppViewContainer"] .block-container {
    padding: 1.6rem 2.6rem 2rem !important;
    max-width: 1500px;
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4 {
    color: #F1F5F9 !important;
    letter-spacing: -0.01em;
}

[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
    color: var(--gs-muted) !important;
}

[data-testid="stAppViewContainer"] hr {
    border-color: var(--gs-border) !important;
}

/* Cards (bordered containers: KPI cards, chart cards, heatmap card, preview card, info card, insight card) */
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--gs-card) !important;
    border: 1px solid var(--gs-border) !important;
    border-radius: var(--gs-radius) !important;
    box-shadow: 0 12px 28px rgba(2, 6, 23, 0.45) !important;
}

/* Expander (feature list) */
[data-testid="stAppViewContainer"] [data-testid="stExpander"] {
    background: var(--gs-card) !important;
    border: 1px solid var(--gs-border) !important;
    border-radius: var(--gs-radius) !important;
    box-shadow: 0 10px 24px rgba(2, 6, 23, 0.35) !important;
    overflow: hidden;
}

[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary p {
    font-size: 0.98rem;
    font-weight: 700;
    color: #F1F5F9 !important;
}

.gs-hero-subtitle {
    font-size: 0.98rem;
    color: var(--gs-muted);
    margin-top: -6px;
    margin-bottom: 4px;
    max-width: 900px;
}

.gs-grid-heading {
    font-size: 1.02rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 4px 0 10px 0;
}

.gs-section-caption {
    font-size: 0.88rem;
    color: var(--gs-muted);
    margin-top: 10px;
}

/* KPI cards */
.gs-kpi-card {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 4px 2px 2px 2px;
    border-radius: 14px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.gs-kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 22px rgba(59, 130, 246, 0.18);
}

.gs-kpi-icon { font-size: 1.5rem; }

.gs-kpi-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gs-muted);
}

.gs-kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #F8FAFC;
}

/* Chart cards */
.gs-chart-title {
    font-size: 1rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 2px;
}

.gs-chart-desc {
    font-size: 0.85rem;
    color: var(--gs-muted);
    margin-bottom: 10px;
}

/* Dataset info card */
.gs-info-item {
    display: flex;
    align-items: baseline;
    gap: 8px;
    padding: 7px 0;
    font-size: 0.92rem;
    color: var(--gs-text);
}

.gs-info-label {
    font-weight: 700;
    color: #F8FAFC;
    min-width: 150px;
    flex-shrink: 0;
}

.gs-info-value code {
    background: rgba(148, 163, 184, 0.12);
    color: #93C5FD;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.85rem;
}

/* Insight card */
.gs-insight-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.gs-insight-list li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-size: 0.95rem;
    color: var(--gs-text);
    line-height: 1.5;
}

.gs-insight-check {
    color: var(--gs-primary);
    font-weight: 800;
    flex-shrink: 0;
}

.gs-empty-state {
    text-align: center;
    padding: 22px 10px;
    color: var(--gs-muted);
}

/* Sticky header on the dataset preview table, where the browser supports it */
[data-testid="stAppViewContainer"] [data-testid="stDataFrame"] [role="columnheader"] {
    position: sticky;
    top: 0;
    z-index: 1;
}
"""

st.markdown(f"<style>{ANALYTICS_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SECTION 1 — Hero
# ---------------------------------------------------------------------------

st.markdown("## 📊 Dataset Analytics")
st.markdown(
    '<div class="gs-hero-subtitle">Explore the training dataset powering GeoSlide AI through '
    "interactive statistics and visualizations.</div>",
    unsafe_allow_html=True,
)

if not is_real_dataset:
    st.warning(
        "⚠️ The real training dataset could not be located. Displaying "
        "generated placeholder data instead so every chart below still "
        "renders correctly."
    )

st.write("")


# ---------------------------------------------------------------------------
# SECTION 2 — Dataset Overview (KPI cards) (UNCHANGED statistics)
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

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4, gap="medium")

kpi_data = [
    (kpi_col1, "🗂️", "Total Records", total_records),
    (kpi_col2, "🧬", "Features", total_features),
    (kpi_col3, "🟠", "Landslide Events", landslide_events),
    (kpi_col4, "🟢", "Non-Landslide Events", non_landslide_events),
]

for col, icon, label, value in kpi_data:
    with col:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="gs-kpi-card">
                    <div class="gs-kpi-icon">{icon}</div>
                    <div class="gs-kpi-label">{label}</div>
                    <div class="gs-kpi-value">{value:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.write("")


# ---------------------------------------------------------------------------
# SECTION 3 — Charts (UNCHANGED chart generation, one premium card each)
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">📈 Charts</div>', unsafe_allow_html=True)

CHART_TEMPLATE = "plotly_white"
COLOR_SEQUENCE = ["#2E86AB", "#E67E22", "#27AE60", "#8E44AD", "#C0392B"]

chart_row1_col1, chart_row1_col2 = st.columns(2, gap="medium")

# 1. Target Distribution
with chart_row1_col1:
    with st.container(border=True):
        st.markdown('<div class="gs-chart-title">Target Distribution</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="gs-chart-desc">Share of landslide vs. non-landslide records in the dataset.</div>',
            unsafe_allow_html=True,
        )
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
    with st.container(border=True):
        st.markdown('<div class="gs-chart-title">Rainfall Distribution</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="gs-chart-desc">Frequency of recorded rainfall values across all rows.</div>',
            unsafe_allow_html=True,
        )
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
    with st.container(border=True):
        st.markdown('<div class="gs-chart-title">Slope Angle Distribution</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="gs-chart-desc">Distribution of terrain slope angles across all rows.</div>',
            unsafe_allow_html=True,
        )
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
    with st.container(border=True):
        st.markdown('<div class="gs-chart-title">Soil Moisture Distribution</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="gs-chart-desc">Distribution of recorded soil moisture values.</div>',
            unsafe_allow_html=True,
        )
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


# ---------------------------------------------------------------------------
# SECTION 4 — Correlation Heatmap (UNCHANGED calculation, larger standalone card)
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">🧮 Correlation Heatmap</div>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown(
        '<div class="gs-chart-desc">Pairwise correlation between numeric features (capped to the '
        "first 20 numeric columns for readability).</div>",
        unsafe_allow_html=True,
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
            '<div class="gs-section-caption">🔴 Red indicates positive correlation. '
            "🔵 Blue indicates negative correlation.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Not enough numeric columns to compute a correlation heatmap.")

st.write("")


# ---------------------------------------------------------------------------
# SECTION 5 — Dataset Preview (UNCHANGED data: dataset_df.head(100))
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">🔎 Dataset Preview</div>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown(
        '<div class="gs-chart-desc">First rows of the training dataset, exactly as loaded.</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(dataset_df.head(100), width="stretch", hide_index=True, height=420)

st.write("")


# ---------------------------------------------------------------------------
# SECTION 6 — Dataset Information (UNCHANGED calculations, compact card)
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">ℹ️ Dataset Information</div>', unsafe_allow_html=True)

missing_values_total = int(dataset_df.isna().sum().sum())
missing_values_pct = (
    round((missing_values_total / (dataset_df.shape[0] * dataset_df.shape[1])) * 100, 2)
    if dataset_df.size > 0
    else 0.0
)

dataset_name_display = DATASET_NAME if not is_real_dataset else os.path.basename(dataset_source)
source_display = dataset_source if is_real_dataset else DATASET_SOURCE

with st.container(border=True):
    info_col1, info_col2 = st.columns(2, gap="medium")
    with info_col1:
        st.markdown(
            f"""
            <div class="gs-info-item"><span class="gs-info-label">📁 Dataset Name</span>
                <span class="gs-info-value">{dataset_name_display}</span></div>
            <div class="gs-info-item"><span class="gs-info-label">🎯 Target Column</span>
                <span class="gs-info-value"><code>{resolved_target_column}</code></span></div>
            <div class="gs-info-item"><span class="gs-info-label">🧬 Features</span>
                <span class="gs-info-value">{total_features:,}</span></div>
            """,
            unsafe_allow_html=True,
        )
    with info_col2:
        st.markdown(
            f"""
            <div class="gs-info-item"><span class="gs-info-label">🗂️ Records</span>
                <span class="gs-info-value">{total_records:,}</span></div>
            <div class="gs-info-item"><span class="gs-info-label">⚠️ Missing Values</span>
                <span class="gs-info-value">{missing_values_total:,} ({missing_values_pct}%)</span></div>
            <div class="gs-info-item"><span class="gs-info-label">🌐 Source</span>
                <span class="gs-info-value">{source_display}</span></div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("📄 View feature list", expanded=False):
        feature_cols = [c for c in dataset_df.columns if c != resolved_target_column]
        st.write(", ".join(feature_cols) if feature_cols else "No feature columns available.")

st.write("")


# ---------------------------------------------------------------------------
# SECTION 7 — Insights (derived only from stats already computed above)
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">💡 Insights</div>', unsafe_allow_html=True)

_class_total = landslide_events + non_landslide_events
_minority_share = (min(landslide_events, non_landslide_events) / _class_total) if _class_total else 0.0
_balance_insight = (
    "Reasonably balanced target classes"
    if _minority_share >= 0.4
    else "Imbalanced target classes - minority class makes up "
    f"{_minority_share * 100:.1f}% of records"
)
_missing_insight = (
    "No missing values in the dataset"
    if missing_values_total == 0
    else f"{missing_values_total:,} missing values ({missing_values_pct}% of all cells)"
)

with st.container(border=True):
    st.markdown(
        f"""
        <ul class="gs-insight-list">
            <li><span class="gs-insight-check">✓</span> {_balance_insight}</li>
            <li><span class="gs-insight-check">✓</span> {_missing_insight}</li>
            <li><span class="gs-insight-check">✓</span> {total_features:,} engineered features</li>
            <li><span class="gs-insight-check">✓</span> Target column (<code>{resolved_target_column}</code>)
                present - suitable for supervised learning</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )