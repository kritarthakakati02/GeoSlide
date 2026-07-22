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
# Dataset Loading
# ---------------------------------------------------------------------------

TARGET_COLUMN = "landslide"
DATASET_NAME = "GeoSlide Landslide Training Dataset"
DATASET_SOURCE = "GeoSlide processed training data (local project dataset)"

# Common candidate locations for the real training dataset. The first
# match found will be used.
CANDIDATE_DATASET_PATHS = [
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
# Page Header
# ---------------------------------------------------------------------------

st.title("📊 Dataset Analytics")
st.markdown("Explore the dataset used to train the GeoSlide landslide prediction model.")

if not is_real_dataset:
    st.warning(
        "⚠️ The real training dataset could not be located. Displaying "
        "generated placeholder data instead so every chart below still "
        "renders correctly."
    )

st.divider()


# ---------------------------------------------------------------------------
# Top Metrics
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

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Total Records", f"{total_records:,}")
metric_col2.metric("Total Features", f"{total_features:,}")
metric_col3.metric("🟠 Landslide Events", f"{landslide_events:,}")
metric_col4.metric("🟢 Non-Landslide Events", f"{non_landslide_events:,}")

st.divider()


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

st.subheader("📈 Charts")

CHART_TEMPLATE = "plotly_white"
COLOR_SEQUENCE = ["#2E86AB", "#E67E22", "#27AE60", "#8E44AD", "#C0392B"]

chart_row1_col1, chart_row1_col2 = st.columns(2)

# 1. Target Distribution
with chart_row1_col1:
    st.markdown("**1. Target Distribution**")
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
    st.markdown("**2. Rainfall Distribution**")
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

chart_row2_col1, chart_row2_col2 = st.columns(2)

# 3. Slope Angle Distribution
with chart_row2_col1:
    st.markdown("**3. Slope Angle Distribution**")
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
    st.markdown("**4. Soil Moisture Distribution**")
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

# 5. Correlation Heatmap
st.markdown("**5. Correlation Heatmap**")
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
else:
    st.info("Not enough numeric columns to compute a correlation heatmap.")

st.divider()


# ---------------------------------------------------------------------------
# Dataset Preview
# ---------------------------------------------------------------------------

st.subheader("🔎 Dataset Preview")
st.dataframe(dataset_df.head(100), width="stretch", hide_index=True)

st.divider()


# ---------------------------------------------------------------------------
# Dataset Information
# ---------------------------------------------------------------------------

st.subheader("ℹ️ Dataset Information")

missing_values_total = int(dataset_df.isna().sum().sum())
missing_values_pct = (
    round((missing_values_total / (dataset_df.shape[0] * dataset_df.shape[1])) * 100, 2)
    if dataset_df.size > 0
    else 0.0
)

with st.container(border=True):
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(f"**Dataset Name:** {DATASET_NAME if not is_real_dataset else os.path.basename(dataset_source)}")
        st.markdown(f"**Target Column:** `{resolved_target_column}`")
        st.markdown(f"**Features:** {total_features:,}")
    with info_col2:
        st.markdown(f"**Missing Values:** {missing_values_total:,} ({missing_values_pct}%)")
        st.markdown(f"**Source:** {dataset_source if is_real_dataset else DATASET_SOURCE}")
        st.markdown(f"**Records:** {total_records:,}")

    with st.expander("📄 View feature list", expanded=False):
        feature_cols = [c for c in dataset_df.columns if c != resolved_target_column]
        st.write(", ".join(feature_cols) if feature_cols else "No feature columns available.")
