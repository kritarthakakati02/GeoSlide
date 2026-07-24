"""
GeoSlide - Prediction Page
============================
Phase 10.4: Prediction Page UI + live backend integration.

This page collects environmental and geological parameters from the
user via a series of organized expanders, and lets the user load
sample data, reset the form, or run a live prediction against the
GeoSlide FastAPI backend (KNN model).

SHAP explainability is intentionally not shown here (see the SHAP
Analysis page) — this page only handles the KNN prediction workflow.

UI note: this file was redesigned into a premium dashboard layout
(2-column input grid, centered actions, large result card, metric
row). All prediction logic, feature-vector building, and API calls
below are byte-for-byte unchanged from before the redesign - only
layout/CSS/presentation code was touched.
"""

import streamlit as st

from components.sidebar import render_sidebar
from utils import api
from utils.constants import RISK_LEVEL_COLORS
from utils.helpers import (
    LAND_USE_OPTIONS,
    SOIL_TYPE_OPTIONS,
    encode_land_use,
    encode_soil_type,
    get_sample_input_data,
)


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Prediction | GeoSlide",
    page_icon="🔍",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Field definitions (UNCHANGED)
# ---------------------------------------------------------------------------
# Each entry: key -> (label, min_value, max_value, default, step)

WEATHER_FIELDS = {
    "rainfall": ("Rainfall (mm)", 0.0, 1000.0, 0.0, 0.5),
    "rainfall_3d": ("Rainfall (Last 3 Days, mm)", 0.0, 2000.0, 0.0, 0.5),
    "rainfall_7d": ("Rainfall (Last 7 Days, mm)", 0.0, 3000.0, 0.0, 0.5),
    "temperature": ("Temperature (°C)", -30.0, 60.0, 20.0, 0.1),
    "humidity": ("Humidity (%)", 0.0, 100.0, 50.0, 0.1),
}

TERRAIN_FIELDS = {
    "slope_angle": ("Slope Angle (°)", 0.0, 90.0, 0.0, 0.1),
    "aspect": ("Aspect (°)", 0.0, 360.0, 0.0, 1.0),
    "elevation": ("Elevation (m)", 0.0, 9000.0, 0.0, 1.0),
    "distance_to_road": ("Distance to Road (m)", 0.0, 10000.0, 0.0, 1.0),
    "proximity_to_water": ("Proximity to Water (m)", 0.0, 10000.0, 0.0, 1.0),
}

SOIL_FIELDS = {
    "soil_saturation": ("Soil Saturation (%)", 0.0, 100.0, 0.0, 0.1),
    "soil_moisture": ("Soil Moisture (%)", 0.0, 100.0, 0.0, 0.1),
    "soil_ph": ("Soil pH", 0.0, 14.0, 7.0, 0.1),
    "clay_content": ("Clay Content (%)", 0.0, 100.0, 0.0, 0.1),
    "sand_content": ("Sand Content (%)", 0.0, 100.0, 0.0, 0.1),
    "silt_content": ("Silt Content (%)", 0.0, 100.0, 0.0, 0.1),
    "soil_erosion_rate": ("Soil Erosion Rate (t/ha/yr)", 0.0, 100.0, 0.0, 0.1),
    "soil_temperature": ("Soil Temperature (°C)", -30.0, 60.0, 15.0, 0.1),
    "pore_water_pressure": ("Pore Water Pressure (kPa)", 0.0, 500.0, 0.0, 0.1),
}

VEGETATION_NUMERIC_FIELDS = {
    "ndvi_index": ("NDVI Index", -1.0, 1.0, 0.0, 0.01),
    "vegetation_cover": ("Vegetation Cover (%)", 0.0, 100.0, 0.0, 0.1),
}

GEOLOGICAL_FIELDS = {
    "earthquake_activity": ("Earthquake Activity (magnitude)", 0.0, 10.0, 0.0, 0.1),
    "historical_landslide_count": ("Historical Landslide Count", 0, 500, 0, 1),
}

SENSOR_FIELDS = {
    "microseismic_activity": ("Microseismic Activity", 0.0, 100.0, 0.0, 0.01),
    "acoustic_emission": ("Acoustic Emission", 0.0, 500.0, 0.0, 0.1),
    "soil_strain": ("Soil Strain", 0.0, 10.0, 0.0, 0.01),
    "tdr_reflection_index": ("TDR Reflection Index", 0.0, 10.0, 0.0, 0.01),
}

# All numeric field groups combined, used for reset/sample-loading logic.
ALL_NUMERIC_FIELD_GROUPS = [
    WEATHER_FIELDS,
    TERRAIN_FIELDS,
    SOIL_FIELDS,
    VEGETATION_NUMERIC_FIELDS,
    GEOLOGICAL_FIELDS,
    SENSOR_FIELDS,
]

DROPDOWN_KEYS = ["land_use", "soil_type"]


# ---------------------------------------------------------------------------
# Session State Initialization (UNCHANGED)
# ---------------------------------------------------------------------------

def _init_session_state() -> None:
    """Initialize default session_state values for every form field."""
    for field_group in ALL_NUMERIC_FIELD_GROUPS:
        for key, (_, _, _, default, _) in field_group.items():
            st.session_state.setdefault(key, default)

    st.session_state.setdefault("land_use", LAND_USE_OPTIONS[0])
    st.session_state.setdefault("soil_type", SOIL_TYPE_OPTIONS[0])

    st.session_state.setdefault("prediction_result", None)


_init_session_state()


# ---------------------------------------------------------------------------
# Button Callbacks (UNCHANGED — feature vector / API logic)
# ---------------------------------------------------------------------------

def _load_sample_data() -> None:
    """Populate all form fields with sample/demo values."""
    sample = get_sample_input_data()
    for key, value in sample.items():
        st.session_state[key] = value
    st.session_state["prediction_result"] = None


def _reset_form() -> None:
    """Reset all form fields back to their default values."""
    for field_group in ALL_NUMERIC_FIELD_GROUPS:
        for key, (_, _, _, default, _) in field_group.items():
            st.session_state[key] = default

    st.session_state["land_use"] = LAND_USE_OPTIONS[0]
    st.session_state["soil_type"] = SOIL_TYPE_OPTIONS[0]
    st.session_state["prediction_result"] = None


def _predict_landslide_risk() -> None:
    """
    Gather form inputs, encode categorical fields, build the ordered
    feature vector the model expects, and call the backend prediction
    API.

    Any failure (validation, connection, timeout, bad response) is
    caught and stored in session_state so the UI can show a clear
    error message instead of crashing.
    """
    payload = _collect_form_payload()

    try:
        result = api.predict(payload)
        st.session_state["prediction_result"] = {
            "status": "success",
            "data": result,
        }
    except KeyError as exc:
        st.session_state["prediction_result"] = {
            "status": "error",
            "message": f"Could not build the feature vector: {exc}",
        }
    except api.BackendUnavailableError as exc:
        st.session_state["prediction_result"] = {
            "status": "error",
            "message": (
                "⚠️ Can't reach the GeoSlide backend. Make sure the FastAPI "
                f"server is running (`uvicorn app:app --reload`). Details: {exc}"
            ),
        }
    except api.BackendTimeoutError as exc:
        st.session_state["prediction_result"] = {
            "status": "error",
            "message": f"⏱️ The backend took too long to respond. {exc}",
        }
    except api.InvalidResponseError as exc:
        st.session_state["prediction_result"] = {
            "status": "error",
            "message": f"The backend returned an unexpected response: {exc}",
        }
    except api.APIError as exc:
        st.session_state["prediction_result"] = {
            "status": "error",
            "message": f"Something went wrong while contacting the backend: {exc}",
        }


def _collect_form_payload() -> dict:
    """Build the full feature payload from current session_state values."""
    payload = {}

    for field_group in ALL_NUMERIC_FIELD_GROUPS:
        for key in field_group:
            payload[key] = st.session_state[key]

    payload.update(encode_land_use(st.session_state["land_use"]))
    payload.update(encode_soil_type(st.session_state["soil_type"]))

    return payload


# ---------------------------------------------------------------------------
# Sidebar (shared, unmodified)
# ---------------------------------------------------------------------------

render_sidebar()


# ---------------------------------------------------------------------------
# Page-scoped dark theme + layout CSS
# ---------------------------------------------------------------------------
# Same scoping approach as Home.py: everything lives under
# [data-testid="stAppViewContainer"] and is only ever injected while
# this script is the active page, so it cannot leak into other pages.

PREDICTION_CSS = """
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
    max-width: 1400px;
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

/* Input cards (expanders) */
[data-testid="stAppViewContainer"] [data-testid="stExpander"] {
    background: var(--gs-card) !important;
    border: 1px solid var(--gs-border) !important;
    border-radius: var(--gs-radius) !important;
    box-shadow: 0 10px 24px rgba(2, 6, 23, 0.35) !important;
    margin-bottom: 14px;
    overflow: hidden;
}

[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary {
    padding: 4px 6px !important;
}

[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary p {
    font-size: 0.98rem;
    font-weight: 700;
    color: #F1F5F9 !important;
}

[data-testid="stAppViewContainer"] [data-testid="stExpander"]:hover {
    border-color: rgba(59, 130, 246, 0.4) !important;
}

/* Number inputs / selects */
[data-testid="stAppViewContainer"] [data-testid="stNumberInput"] input,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] > div {
    background: #0F172A !important;
    color: var(--gs-text) !important;
    border-radius: 10px !important;
    border: 1px solid var(--gs-border) !important;
}

[data-testid="stAppViewContainer"] label p {
    color: var(--gs-muted) !important;
    font-size: 0.82rem !important;
}

/* Result & metric cards */
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--gs-card) !important;
    border: 1px solid var(--gs-border) !important;
    border-radius: var(--gs-radius) !important;
    box-shadow: 0 12px 28px rgba(2, 6, 23, 0.45) !important;
}

/* Buttons */
[data-testid="stAppViewContainer"] .stButton > button {
    border-radius: 999px !important;
    font-weight: 700;
    padding: 0.6rem 1rem;
}

[data-testid="stAppViewContainer"] button[kind="secondary"] {
    background: var(--gs-card) !important;
    border: 1px solid var(--gs-border) !important;
    color: #E2E8F0 !important;
}

[data-testid="stAppViewContainer"] button[kind="primary"] {
    background: linear-gradient(90deg, var(--gs-primary) 0%, var(--gs-accent) 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-size: 1.05rem;
    padding: 0.85rem 1.2rem !important;
    box-shadow: 0 14px 30px rgba(16, 185, 129, 0.3) !important;
}

[data-testid="stAppViewContainer"] button[kind="primary"]:hover {
    filter: brightness(1.06);
    transform: translateY(-2px);
}

/* Progress bar */
[data-testid="stAppViewContainer"] [data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--gs-primary) 0%, var(--gs-accent) 100%) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stProgress"] {
    background: rgba(148, 163, 184, 0.15) !important;
    border-radius: 999px;
}

.gs-page-subtitle {
    font-size: 0.98rem;
    color: var(--gs-muted);
    margin-top: -6px;
    margin-bottom: 4px;
}

.gs-grid-heading {
    font-size: 1.02rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 4px 0 10px 0;
}

.gs-risk-badge {
    display: inline-block;
    padding: 8px 20px;
    border-radius: 999px;
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.01em;
}

.gs-result-eyebrow {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gs-muted);
    margin-bottom: 10px;
}

.gs-result-status {
    font-size: 0.95rem;
    color: var(--gs-text);
    margin-top: 10px;
}

.gs-confidence-label {
    font-size: 0.85rem;
    color: var(--gs-muted);
    margin-top: 6px;
}

.gs-metric-icon { font-size: 1.2rem; margin-bottom: 4px; }
.gs-metric-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gs-muted);
}
.gs-metric-value {
    font-size: 1.4rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-top: 2px;
}

.gs-factor-chip {
    display: inline-block;
    background: rgba(59, 130, 246, 0.12);
    border: 1px solid rgba(59, 130, 246, 0.35);
    color: #DBEAFE;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 999px;
    margin: 0 8px 8px 0;
}

.gs-empty-state {
    text-align: center;
    padding: 22px 10px;
    color: var(--gs-muted);
}
"""

st.markdown(f"<style>{PREDICTION_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SECTION 1 — Page Header
# ---------------------------------------------------------------------------

st.markdown("## 🔍 Landslide Risk Prediction")
st.markdown(
    '<div class="gs-page-subtitle">Enter environmental and geological parameters to assess landslide risk.</div>',
    unsafe_allow_html=True,
)
st.write("")


# ---------------------------------------------------------------------------
# Helper for rendering a numeric field grid inside an expander (UNCHANGED)
# ---------------------------------------------------------------------------

def _render_numeric_fields(field_group: dict, columns: int = 2) -> None:
    keys = list(field_group.keys())
    cols = st.columns(columns)

    for idx, key in enumerate(keys):
        label, min_value, max_value, default, step = field_group[key]
        col = cols[idx % columns]

        is_int = isinstance(default, int)
        with col:
            st.number_input(
                label,
                min_value=(int(min_value) if is_int else float(min_value)),
                max_value=(int(max_value) if is_int else float(max_value)),
                step=(int(step) if is_int else float(step)),
                key=key,
            )


# ---------------------------------------------------------------------------
# SECTION 2 — Prediction Input Panel (responsive 2-column card grid)
# ---------------------------------------------------------------------------
# Same expander bodies / fields / keys as before - only the container
# arrangement changed from one long vertical stack to a 2-column grid.

st.markdown('<div class="gs-grid-heading">Input Parameters</div>', unsafe_allow_html=True)

row1_left, row1_right = st.columns(2, gap="medium")
with row1_left:
    with st.expander("🌧️ Weather Conditions", expanded=True):
        _render_numeric_fields(WEATHER_FIELDS)
with row1_right:
    with st.expander("⛰️ Terrain & Geography", expanded=False):
        _render_numeric_fields(TERRAIN_FIELDS)

row2_left, row2_right = st.columns(2, gap="medium")
with row2_left:
    with st.expander("🧪 Soil Characteristics", expanded=False):
        _render_numeric_fields(SOIL_FIELDS)
with row2_right:
    with st.expander("🌱 Vegetation & Land Use", expanded=False):
        _render_numeric_fields(VEGETATION_NUMERIC_FIELDS)
        st.selectbox(
            "Land Use",
            options=LAND_USE_OPTIONS,
            key="land_use",
        )

row3_left, row3_right = st.columns(2, gap="medium")
with row3_left:
    with st.expander("🌋 Geological Activity", expanded=False):
        _render_numeric_fields(GEOLOGICAL_FIELDS)
with row3_right:
    with st.expander("📡 Sensor Measurements", expanded=False):
        _render_numeric_fields(SENSOR_FIELDS)

row4_left, row4_right = st.columns(2, gap="medium")
with row4_left:
    with st.expander("🪨 Soil Type", expanded=False):
        st.selectbox(
            "Soil Type",
            options=SOIL_TYPE_OPTIONS,
            key="soil_type",
        )
# row4_right intentionally left empty - 7 groups is an odd number, so
# Soil Type sits alone in the last row rather than being stretched or
# awkwardly paired.

st.write("")


# ---------------------------------------------------------------------------
# SECTION 3 — Action Buttons (centered, Predict visually dominant)
# ---------------------------------------------------------------------------

btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1], gap="medium")

with btn_col1:
    st.button(
        "📂 Load Sample",
        use_container_width=True,
        on_click=_load_sample_data,
    )

with btn_col2:
    st.button(
        "🟢 Predict Landslide Risk",
        type="primary",
        use_container_width=True,
        on_click=_predict_landslide_risk,
    )

with btn_col3:
    st.button(
        "🔄 Reset",
        use_container_width=True,
        on_click=_reset_form,
    )

st.write("")


# ---------------------------------------------------------------------------
# SECTION 4 & 5 — Prediction Result (large focus card + metric row)
# ---------------------------------------------------------------------------


def _format_probability(value):
    """Format probability as a percentage rounded to one decimal place."""
    if value is None:
        return "—"

    try:
        probability = float(value)
    except (TypeError, ValueError):
        return "—"

    return f"{probability * 100:.1f}%"


def _format_prediction(value):
    """Translate numeric prediction values into user-friendly labels."""
    if value is None:
        return "—"

    text_value = str(value).strip()
    if text_value in {"0", "0.0", "No Landslide"}:
        return "No Landslide"
    if text_value in {"1", "1.0", "Landslide Likely"}:
        return "Landslide Likely"

    return str(value)


def _extract_top_factors(data: dict):
    """
    Look for an optional list of contributing factors in the /predict
    response, if the backend happens to include one. This never calls
    SHAP or any other endpoint - it only reads keys that may already
    be present on the existing `data` dict returned by api.predict().
    """
    for key in ("top_contributing_factors", "contributing_factors", "top_factors"):
        value = data.get(key)
        if value:
            return value
    return None


st.markdown('<div class="gs-grid-heading">🧠 Prediction Result</div>', unsafe_allow_html=True)

result = st.session_state.get("prediction_result")

with st.container(border=True):
    if result is None:
        st.markdown(
            """
            <div class="gs-empty-state">
                <div style="font-size:1.6rem;">🛰️</div>
                <div style="margin-top:6px;">No prediction yet. Fill in the parameters above and click
                <b>Predict Landslide Risk</b>.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif result["status"] == "error":
        st.error(result.get("message", "Prediction could not be completed."))
    elif result["status"] == "success":
        data = result.get("data") or {}
        risk_level = data.get("risk_level", "Unknown")
        probability = data.get("probability", 0.0)
        prediction = data.get("prediction", 0)
        color = RISK_LEVEL_COLORS.get(risk_level, "#808080")
        verdict = _format_prediction(prediction)
        probability_text = _format_probability(probability)

        st.markdown('<div class="gs-result-eyebrow">Assessment Result</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="gs-risk-badge" style="background-color:{color};">{risk_level} Risk</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="gs-result-status">Prediction status: <b>{verdict}</b></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="gs-confidence-label">Probability</div>', unsafe_allow_html=True)
        try:
            st.progress(float(probability))
        except (TypeError, ValueError):
            st.progress(0.0)
        st.markdown(f'<div class="gs-confidence-label">Confidence: <b>{probability_text}</b></div>', unsafe_allow_html=True)

        top_factors = _extract_top_factors(data)
        if top_factors:
            st.write("")
            st.markdown('<div class="gs-confidence-label">Top Contributing Factors</div>', unsafe_allow_html=True)
            chips = ""
            for factor in list(top_factors)[:5]:
                factor_label = factor.get("name", str(factor)) if isinstance(factor, dict) else str(factor)
                chips += f'<span class="gs-factor-chip">{factor_label}</span>'
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.write("")
            st.page_link(
                "pages/2_SHAP_Analysis.py",
                label="🧠 See detailed feature contributions in SHAP Analysis →",
                icon=None,
            )

        st.write("")
        m1, m2, m3, m4 = st.columns(4, gap="medium")
        for col, icon, label, value in [
            (m1, "🚨", "Risk Level", risk_level),
            (m2, "📈", "Probability", probability_text),
            (m3, "🔮", "Prediction", verdict),
            (m4, "🤖", "Model", "KNN"),
        ]:
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div class="gs-metric-icon">{icon}</div>
                        <div class="gs-metric-label">{label}</div>
                        <div class="gs-metric-value">{value}</div>
                        """,
                        unsafe_allow_html=True,
                    )
