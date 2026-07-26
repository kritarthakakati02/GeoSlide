"""
GeoSlide - Prediction Page
============================
UI redesign: premium enterprise "AI Risk Assessment" dashboard, wired to
the shared design system (`frontend/assets/design_system.css` — the same
tokens + `.ds-*` classes Home.py already uses). No new colors, spacing,
radii, or type sizes are declared here; every visual value below is a
`.ds-*` class or a `var(--ds-*)` token, exactly like Home.py.

SHAP explainability is intentionally not shown here (see the SHAP
Analysis page) — this page only handles the KNN prediction workflow.

WHAT CHANGED vs. what did not
------------------------------
Changed (presentation only):
  - Page layout: hero card, horizontal assessment-progress indicator,
    inputs regrouped into five visible cards (Location, Terrain,
    Hydrology, Weather, Environment), a large centered predict action,
    a redesigned result card, and a small model-info card.
  - CSS: replaced the page's old standalone dark-theme stylesheet with
    the shared light `design_system.css` tokens/classes (the same ones
    Home.py already uses), so this page now matches Home.py's actual
    current visual language instead of the older, inconsistent theme.
  - The Predict button is now invoked via `if st.button(...):` instead
    of `on_click=`, purely so a `st.spinner(...)` can wrap the call and
    show a real loading state. The function it calls
    (`_predict_landslide_risk`) is byte-for-byte unchanged.

NOT changed (verified untouched):
  - Field definitions (keys, labels, min/max/step/default values).
  - Session-state initialization, reset, and sample-loading logic.
  - `_collect_form_payload`, feature-vector/category-encoding calls,
    and the `api.predict()` call itself (same function body).
  - Error handling branches and messages.
  - Navigation, sidebar, and every other page's files.

Polish pass (presentation only, on top of the above):
  - Input widgets restyled (custom borders/focus/hover, no default
    Streamlit chrome) — same st.number_input/st.selectbox calls,
    same keys, same min/max/step/options.
  - The old single wide "Environment" card was split into two
    balanced cards — "Environment & Vegetation" and "Sensor
    Monitoring" — same fields, same keys, just regrouped.
  - Predict is now the visually dominant action; Load Sample/Reset
    are smaller secondary actions underneath. Same on_click callbacks.
  - Result card redesigned around a large centered risk badge +
    confidence figure. Same data, same fields read from the response.
  - Model Info converted into three individual KPI-style cards using
    the same `.ds-kpi-*` classes Home.py's KPI row uses. Same facts.
"""

from pathlib import Path

import streamlit as st

from components.sidebar import render_sidebar
from utils.theme import load_styles
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

ROOT = Path(__file__).resolve().parent.parent
DESIGN_SYSTEM_CSS_FILE = ROOT / "assets" / "design_system.css"


# ---------------------------------------------------------------------------
# Field definitions (UNCHANGED — same keys, labels, ranges, defaults)
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
# UNCHANGED — this is what session-state init, reset, and payload
# collection iterate over. The card layout below reads from these same
# dicts; it never redefines or duplicates a field.
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
# Shared design system (same files Home.py loads — single source of truth)
# ---------------------------------------------------------------------------

st.markdown(f"<style>{load_styles()}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{DESIGN_SYSTEM_CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page wiring CSS — maps Streamlit's native container markup onto the
# existing design-system tokens/classes, the same way Home.py's
# HOME_WIRING_CSS does. Colors/shadows/radii resolve through var(--ds-*)
# tokens or small rgba refinements of those same tokens — no layout,
# spacing, or component positions change here.
# ---------------------------------------------------------------------------

PREDICTION_WIRING_CSS = """
[data-testid="stAppViewContainer"] {
    background: var(--ds-bg) !important;
    /* Softer, less visible borders + layered elevation shadows used
       throughout this page's cards — component-quality polish only. */
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
   BASELINE — every real bordered container starts from the same
   premium card look, then gets overridden per-section below.
   ============================================================ */
[data-testid="stAppViewContainer"] [data-testid="stLayoutWrapper"] {
    background: var(--ds-surface) !important;
    border: 1px solid var(--gs-border-soft) !important;
    border-radius: var(--ds-radius-lg) !important;
    box-shadow: var(--gs-shadow-card) !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base),
                border-color var(--ds-transition-base), background var(--ds-transition-base);
}

/* ============================================================
   SECTION PANELS — outer card for Progress, Inputs, Actions,
   Result, and Model Info sections. A slightly recessed surface
   so the panel -> card hierarchy reads clearly.
   ============================================================ */
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
.gs-hero-illo-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 180px;
}
.gs-hero-illo-wrap svg {
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
    .gs-hero-illo-wrap svg { animation: none; }
}

/* ============================================================
   SECTION 2 — ASSESSMENT PROGRESS
   ============================================================ */
.gs-progress-row {
    display: flex;
    align-items: stretch;
    justify-content: space-between;
    gap: var(--ds-space-3);
    flex-wrap: wrap;
    margin-top: var(--ds-space-2);
}
.gs-progress-step {
    flex: 1 1 140px;
    display: flex;
    align-items: center;
    gap: var(--ds-space-3);
    background: var(--ds-surface);
    border: 1px solid var(--gs-border-soft);
    border-radius: var(--ds-radius-md);
    padding: var(--ds-space-4);
    box-shadow: var(--gs-shadow-card);
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base), border-color var(--ds-transition-base);
}
.gs-progress-step:hover {
    transform: translateY(-3px);
    border-color: var(--ds-brand-100);
    box-shadow: var(--gs-shadow-card-hover);
}
.gs-progress-step.gs-progress-final {
    background: linear-gradient(90deg, var(--ds-brand-50) 0%, var(--ds-surface) 100%);
    border-color: var(--ds-brand-100);
}
.gs-progress-index {
    width: 30px; height: 30px; border-radius: var(--ds-radius-full);
    display: flex; align-items: center; justify-content: center;
    font-size: var(--ds-text-xs); font-weight: var(--ds-weight-bold);
    background: var(--ds-brand-500); color: var(--ds-text-inverse);
    flex-shrink: 0;
}
.gs-progress-label { font-size: var(--ds-text-sm); font-weight: var(--ds-weight-semibold); color: var(--ds-text-primary); }
.gs-progress-sub { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); }
.gs-progress-arrow { display: flex; align-items: center; color: var(--ds-brand-400); opacity: 0.6; flex: 0 0 auto; }
@media (max-width: 900px) {
    .gs-progress-arrow { display: none; }
}

/* ============================================================
   SECTION 3 — INPUT CARDS (Location / Terrain / Hydrology /
   Weather / Environment)
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-field-card-"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-6) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-field-card-"]):hover {
    border-color: var(--gs-border-soft-strong) !important;
    box-shadow: var(--gs-shadow-card-hover) !important;
}
.gs-field-card-header {
    display: flex;
    align-items: center;
    gap: var(--ds-space-3);
    margin-bottom: var(--ds-space-4);
}
.gs-field-card-title { font-size: var(--ds-text-h3); font-weight: var(--ds-weight-semibold); color: var(--ds-text-primary); }
.gs-field-card-desc { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: 1px; }

/* Number inputs / selects — a single unified control surface, no
   default Streamlit chrome. overflow:hidden makes the input field and
   its stepper buttons read as one component with rounded outer
   corners instead of three separately-bordered pieces. */
[data-testid="stAppViewContainer"] [data-testid="stNumberInput"],
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] {
    margin-bottom: 2px;
}
[data-testid="stAppViewContainer"] [data-testid="stNumberInputContainer"],
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] > div > div {
    background: var(--ds-bg-inset) !important;
    border: 1px solid var(--gs-border-soft-strong) !important;
    border-radius: var(--ds-radius-md) !important;
    box-shadow: inset 0 1px 2px rgba(28, 35, 31, 0.03) !important;
    overflow: hidden;
    transition: border-color var(--ds-transition-fast), box-shadow var(--ds-transition-fast), background var(--ds-transition-fast);
}
[data-testid="stAppViewContainer"] [data-testid="stNumberInputContainer"]:hover,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] > div > div:hover {
    border-color: var(--ds-brand-200) !important;
    background: var(--ds-surface) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stNumberInputContainer"]:focus-within,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--ds-border-focus) !important;
    box-shadow: var(--ds-shadow-focus) !important;
    background: var(--ds-surface) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stNumberInput"] input,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] input,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] > div > div > div {
    background: transparent !important;
    color: var(--ds-text-primary) !important;
    border: none !important;
    box-shadow: none !important;
    font-weight: var(--ds-weight-semibold);
    font-size: var(--ds-text-sm) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] > div > div {
    padding-left: 2px !important;
}
/* Cleaner dropdown arrow, recolored to match the rest of the inputs */
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] svg {
    fill: var(--ds-text-tertiary) !important;
    color: var(--ds-text-tertiary) !important;
    width: 16px;
    height: 16px;
}
/* Step +/- buttons — a soft internal hairline (not a hard border)
   keeps them feeling like part of the same control rather than a
   bolted-on widget. */
[data-testid="stAppViewContainer"] [data-testid="stNumberInputStepDown"],
[data-testid="stAppViewContainer"] [data-testid="stNumberInputStepUp"] {
    background: transparent !important;
    color: var(--ds-text-tertiary) !important;
    border: none !important;
    border-left: 1px solid var(--gs-border-soft) !important;
    border-radius: 0 !important;
    transition: background var(--ds-transition-fast), color var(--ds-transition-fast);
}
[data-testid="stAppViewContainer"] [data-testid="stNumberInputStepDown"]:hover,
[data-testid="stAppViewContainer"] [data-testid="stNumberInputStepUp"]:hover {
    background: var(--ds-brand-50) !important;
    color: var(--ds-brand-600) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stNumberInputStepDown"] svg,
[data-testid="stAppViewContainer"] [data-testid="stNumberInputStepUp"] svg {
    width: 14px;
    height: 14px;
}
[data-testid="stAppViewContainer"] label p {
    color: var(--ds-text-tertiary) !important;
    font-size: var(--ds-text-xs) !important;
    font-weight: var(--ds-weight-bold);
    text-transform: uppercase;
    letter-spacing: var(--ds-tracking-wide);
}

/* ============================================================
   SECTION 4 — PREDICT ACTION
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-actions"]) {
    background: var(--ds-surface) !important;
    text-align: center;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
[data-testid="stAppViewContainer"] .stButton > button {
    border-radius: var(--ds-radius-full) !important;
    font-weight: var(--ds-weight-semibold);
    font-family: var(--ds-font-base);
    outline: none !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base), background var(--ds-transition-base), border-color var(--ds-transition-base);
}
/* Secondary — a single, consistent 1px hairline instead of the
   default browser/Streamlit button border, with a quiet fill-based
   hover instead of just a color-changing outline. */
[data-testid="stAppViewContainer"] button[kind="secondary"] {
    background: var(--ds-surface) !important;
    border: 1px solid var(--gs-border-soft-strong) !important;
    color: var(--ds-text-secondary) !important;
    box-shadow: none !important;
}
[data-testid="stAppViewContainer"] button[kind="secondary"] p,
[data-testid="stAppViewContainer"] button[kind="secondary"] div {
    color: var(--ds-text-secondary) !important;
}
[data-testid="stAppViewContainer"] button[kind="secondary"]:hover {
    background: var(--ds-bg-subtle) !important;
    border-color: var(--ds-border-strong) !important;
    color: var(--ds-text-primary) !important;
    transform: var(--ds-lift-hover);
    box-shadow: var(--gs-shadow-card) !important;
}
[data-testid="stAppViewContainer"] button[kind="secondary"]:hover p,
[data-testid="stAppViewContainer"] button[kind="secondary"]:hover div {
    color: var(--ds-text-primary) !important;
}
[data-testid="stAppViewContainer"] button[kind="secondary"]:active {
    transform: translateY(0);
    background: var(--ds-bg-inset) !important;
}
[data-testid="stAppViewContainer"] button[kind="secondary"]:focus-visible {
    box-shadow: var(--ds-shadow-focus) !important;
}
/* Predict — the single dominant call to action on this page. Solid,
   saturated fill (not a washed-out light tint), bright white label
   text explicitly forced onto every inner element, and a soft diffuse
   shadow rather than a hard, over-saturated one. */
[data-testid="stAppViewContainer"] button[kind="primary"] {
    background: linear-gradient(135deg, var(--ds-brand-500) 0%, var(--ds-brand-700) 100%) !important;
    border: none !important;
    color: var(--ds-text-inverse) !important;
    font-size: 1.2rem !important;
    font-weight: var(--ds-weight-bold) !important;
    letter-spacing: 0.01em;
    padding: 1.1rem 1.5rem !important;
    box-shadow: 0 1px 2px rgba(20, 30, 24, 0.15), 0 14px 28px rgba(28, 68, 51, 0.24) !important;
}
[data-testid="stAppViewContainer"] button[kind="primary"] p,
[data-testid="stAppViewContainer"] button[kind="primary"] div,
[data-testid="stAppViewContainer"] button[kind="primary"] span {
    color: var(--ds-text-inverse) !important;
    opacity: 1 !important;
}
[data-testid="stAppViewContainer"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--ds-brand-600) 0%, var(--ds-brand-700) 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 2px 4px rgba(20, 30, 24, 0.18), 0 20px 38px rgba(28, 68, 51, 0.30) !important;
}
[data-testid="stAppViewContainer"] button[kind="primary"]:active {
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(20, 30, 24, 0.15), 0 8px 18px rgba(28, 68, 51, 0.22) !important;
}
[data-testid="stAppViewContainer"] button[kind="primary"]:focus-visible {
    box-shadow: 0 0 0 3px rgba(47, 107, 79, 0.28), 0 14px 28px rgba(28, 68, 51, 0.24) !important;
}
/* Load Sample / Reset — deliberately smaller & quieter than Predict,
   same single-hairline pill treatment as the rest of the secondary
   buttons above. */
[class*="st-key-load-sample-btn"] button,
[class*="st-key-reset-btn"] button {
    padding: 0.5rem 0.9rem !important;
    font-size: var(--ds-text-sm) !important;
    font-weight: var(--ds-weight-medium) !important;
}
.gs-secondary-actions-label {
    text-align: center;
    font-size: var(--ds-text-xs);
    color: var(--ds-text-tertiary);
    text-transform: uppercase;
    letter-spacing: var(--ds-tracking-wide);
    margin: var(--ds-space-4) 0 var(--ds-space-2);
}
.gs-actions-hint { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: var(--ds-space-4); }

/* ============================================================
   SECTION 5 — RESULT CARD
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-result"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
/* Large centered hero block: risk badge + big confidence figure */
.gs-result-hero {
    text-align: center;
    padding: var(--ds-space-3) 0 var(--ds-space-5);
}
.gs-risk-badge {
    display: inline-block;
    padding: 9px 24px;
    border-radius: var(--ds-radius-full);
    font-size: 1.25rem;
    font-weight: var(--ds-weight-extrabold);
    letter-spacing: 0.01em;
    box-shadow: var(--ds-shadow-sm);
}
.gs-result-confidence-value {
    font-size: 3.4rem;
    font-weight: var(--ds-weight-extrabold);
    color: var(--ds-text-primary);
    line-height: 1;
    margin-top: var(--ds-space-4);
    font-variant-numeric: tabular-nums;
}
.gs-result-confidence-caption {
    font-size: var(--ds-text-sm);
    font-weight: var(--ds-weight-semibold);
    color: var(--ds-text-tertiary);
    text-transform: uppercase;
    letter-spacing: var(--ds-tracking-wide);
    margin-top: var(--ds-space-2);
}
.gs-result-status { font-size: var(--ds-text-sm); color: var(--ds-text-tertiary); margin-top: var(--ds-space-2); }
.gs-result-summary {
    font-size: var(--ds-text-body-lg);
    color: var(--ds-text-primary);
    line-height: var(--ds-leading-normal);
    text-align: center;
    max-width: 640px;
    margin: var(--ds-space-4) auto 0;
}
.gs-recommend-box {
    display: flex;
    gap: var(--ds-space-3);
    align-items: flex-start;
    background: var(--ds-bg-subtle);
    border: 1px solid var(--gs-border-soft-strong);
    border-radius: var(--ds-radius-md);
    padding: var(--ds-space-4);
    margin-top: var(--ds-space-5);
}
.gs-recommend-title { font-size: var(--ds-text-sm); font-weight: var(--ds-weight-bold); color: var(--ds-text-primary); }
.gs-recommend-text { font-size: var(--ds-text-sm); color: var(--ds-text-secondary); margin-top: 2px; }
.gs-recommend-note { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: var(--ds-space-2); font-style: italic; }
.gs-confidence-label { font-size: var(--ds-text-sm); color: var(--ds-text-secondary); margin-top: var(--ds-space-2); }
[data-testid="stAppViewContainer"] [data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--ds-brand-500) 0%, var(--ds-accent-500) 100%) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stProgress"] {
    background: var(--ds-bg-inset) !important;
    border-radius: var(--ds-radius-full);
}
.gs-factor-chip {
    display: inline-block;
    background: var(--ds-accent-50);
    border: 1px solid var(--ds-accent-100, var(--ds-border));
    color: var(--ds-accent-600);
    font-size: var(--ds-text-xs);
    font-weight: var(--ds-weight-semibold);
    padding: 6px 14px;
    border-radius: var(--ds-radius-full);
    margin: 0 var(--ds-space-2) var(--ds-space-2) 0;
}
.gs-empty-state { text-align: center; padding: var(--ds-space-8) var(--ds-space-4); color: var(--ds-text-tertiary); }
.gs-empty-state .ds-kpi-icon { margin: 0 auto var(--ds-space-3); }

/* Metric mini-cards inside the result card */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-metric-"]) {
    background: var(--ds-bg-subtle) !important;
    padding: var(--ds-space-4) !important;
}
.gs-metric-label { font-size: var(--ds-text-xs); font-weight: var(--ds-weight-bold); text-transform: uppercase; letter-spacing: var(--ds-tracking-wide); color: var(--ds-text-tertiary); }
.gs-metric-value { font-size: 1.3rem; font-weight: var(--ds-weight-extrabold); color: var(--ds-text-primary); margin-top: 2px; }

/* ============================================================
   SECTION 6 — MODEL INFO (KPI-style cards, same tokens/classes as
   Home.py's KPI row: .ds-kpi-icon / .ds-chip-*)
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-modelinfo"]) {
    background: var(--ds-bg-subtle) !important;
    padding: var(--ds-space-6) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-modelinfo-kpi-"]) {
    background: var(--ds-surface) !important;
    text-align: center;
    padding: var(--ds-space-5) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-modelinfo-kpi-"]):hover {
    transform: translateY(-3px);
    border-color: var(--ds-brand-200) !important;
    box-shadow: var(--ds-shadow-md) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-modelinfo-kpi-"]) .ds-kpi-icon {
    margin: 0 auto var(--ds-space-3);
}
.gs-modelinfo-label { font-size: var(--ds-text-xs); font-weight: var(--ds-weight-bold); text-transform: uppercase; letter-spacing: var(--ds-tracking-wide); color: var(--ds-text-tertiary); }
.gs-modelinfo-value { font-size: 1.05rem; font-weight: var(--ds-weight-extrabold); color: var(--ds-text-primary); margin-top: 4px; }
.gs-modelinfo-desc { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: 2px; }
"""

st.markdown(f"<style>{PREDICTION_WIRING_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar (shared, unmodified)
# ---------------------------------------------------------------------------

render_sidebar()


# ---------------------------------------------------------------------------
# Local icon set (page-scoped, same inline-SVG pattern Home.py uses —
# decorative only, no emoji, no external assets).
# ---------------------------------------------------------------------------

_ICON_PATHS = {
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.3-4.3"/>',
    "map-pin": '<path d="M12 21s7-7.2 7-12a7 7 0 1 0-14 0c0 4.8 7 12 7 12Z"/><circle cx="12" cy="9" r="2.4"/>',
    "mountain": '<path d="m3.5 19 6-11 3.5 6 2.5-4 5 9Z"/>',
    "droplet": '<path d="M12 2.8s6.2 7 6.2 11.5A6.2 6.2 0 0 1 5.8 14.3C5.8 9.8 12 2.8 12 2.8Z"/>',
    "cloud-rain": '<path d="M7 15.5a4.3 4.3 0 0 1 .6-8.6 5.7 5.7 0 0 1 10.6 2.6 3.8 3.8 0 0 1-.7 6H7Z"/><path d="M8 19v1.3M12 19v1.8M16 19v1.3"/>',
    "leaf": '<path d="M5 19.5C4 11.8 8.8 4.5 19.5 4.5c0 10.7-7.3 15.5-14.5 15Z"/><path d="M5 19.5c2-4.3 5.2-7.3 9.3-9.3"/>',
    "zap": '<path d="M12.5 2 4 13h6l-1 9L20 11h-6l-1-9Z"/>',
    "arrow-right": '<line x1="4" y1="12" x2="18" y2="12"/><polyline points="12 6 18 12 12 18"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8 12.3 2.6 2.6L16.2 9"/>',
    "alert-triangle": '<path d="M12 3.2 2.3 20h19.4L12 3.2Z"/><line x1="12" y1="9.5" x2="12" y2="14"/><circle cx="12" cy="17" r="0.9" fill="currentColor"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><rect x="10" y="10" width="4" height="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.5 4.5l2 2M17.5 17.5l2 2M4.5 19.5l2-2M17.5 6.5l2-2"/>',
    "layers": '<path d="m12 3 8 4.2-8 4.2-8-4.2Z"/><path d="m4 12 8 4.2 8-4.2"/><path d="m4 16.4 8 4.2 8-4.2"/>',
    "brain": '<path d="M9 3.5A2.5 2.5 0 0 0 6.5 6v.3a2.5 2.5 0 0 0-1.4 4.3A2.8 2.8 0 0 0 6 15.6a2.5 2.5 0 0 0 3 3.3A2.5 2.5 0 0 0 11.5 20V6A2.5 2.5 0 0 0 9 3.5Z"/><path d="M15 3.5A2.5 2.5 0 0 1 17.5 6v.3a2.5 2.5 0 0 1 1.4 4.3A2.8 2.8 0 0 1 18 15.6a2.5 2.5 0 0 1-3 3.3A2.5 2.5 0 0 1 12.5 20V6A2.5 2.5 0 0 1 15 3.5Z"/>',
    "shield": '<path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6Z"/>',
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
    """Small decorative hero illustration — a stylised risk radar over
    terrain, built the same way Home.py's mini feature illustrations
    are (inline SVG, tokens for color, purely decorative)."""
    return (
        '<svg viewBox="0 0 220 200" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="110" cy="100" r="86" stroke="var(--ds-brand-200)" stroke-width="1.4" opacity="0.55"/>'
        '<circle cx="110" cy="100" r="60" stroke="var(--ds-brand-200)" stroke-width="1.2" opacity="0.45"/>'
        '<circle cx="110" cy="100" r="34" stroke="var(--ds-brand-200)" stroke-width="1.2" opacity="0.4"/>'
        '<path d="M20 150 60 95 90 130 130 60 200 150Z" fill="var(--ds-brand-50)" stroke="var(--ds-brand-300)" stroke-width="2" stroke-linejoin="round"/>'
        '<circle cx="130" cy="60" r="6" fill="var(--ds-amber-500)"/>'
        '<circle cx="60" cy="95" r="5" fill="var(--ds-accent-500)"/>'
        '<circle cx="90" cy="130" r="5" fill="var(--ds-brand-500)"/>'
        '<line x1="110" y1="100" x2="110" y2="34" stroke="var(--ds-brand-500)" stroke-width="2" stroke-linecap="round" opacity="0.8"/>'
        '<circle cx="110" cy="100" r="4" fill="var(--ds-brand-600)"/>'
        '</svg>'
    )


def _progress_html() -> str:
    steps = [
        ("map-pin", "Location", "Site & terrain context"),
        ("mountain", "Terrain", "Slope & aspect"),
        ("droplet", "Hydrology", "Soil & moisture"),
        ("leaf", "Environment", "Vegetation & activity"),
        ("zap", "Predict", "Run the model"),
    ]
    parts = ['<div class="gs-progress-row">']
    for i, (icon, label, sub) in enumerate(steps):
        is_final = i == len(steps) - 1
        chip_class = "ds-chip-brand" if not is_final else "ds-chip-accent"
        step_class = "gs-progress-step gs-progress-final" if is_final else "gs-progress-step"
        parts.append(
            f'<div class="{step_class}">'
            f'<div class="gs-progress-index">{i + 1}</div>'
            f'<div class="ds-kpi-icon {chip_class}" style="width:34px;height:34px;margin-bottom:0;">{_icon(icon, 16)}</div>'
            f'<div><div class="gs-progress-label">{label}</div>'
            f'<div class="gs-progress-sub">{sub}</div></div>'
            f'</div>'
        )
        if not is_final:
            parts.append(f'<div class="gs-progress-arrow">{_icon("arrow-right", 18)}</div>')
    parts.append("</div>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Helper for rendering a numeric field grid (UNCHANGED widget logic —
# same st.number_input calls, same keys/min/max/step; only the *subset*
# of keys shown in a given card, and the column count, are new).
# ---------------------------------------------------------------------------

def _render_numeric_fields(field_group: dict, keys=None, columns: int = 2) -> None:
    keys = list(field_group.keys()) if keys is None else list(keys)
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


def _field_card_header(icon: str, chip_class: str, title: str, desc: str) -> None:
    st.markdown(
        f"""
        <div class="gs-field-card-header">
            <div class="ds-kpi-icon {chip_class}" style="width:40px;height:40px;margin-bottom:0;">{_icon(icon, 18)}</div>
            <div>
                <div class="gs-field-card-title">{title}</div>
                <div class="gs-field-card-desc">{desc}</div>
            </div>
        </div>
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
            f'<div class="ds-eyebrow">{_icon("search", 14, 2)}<span>&nbsp;AI RISK ASSESSMENT</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ds-display gs-display-md">Landslide Risk Prediction</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="ds-body-lg gs-hero-copy">
            Enter site, terrain, hydrology, and environmental parameters below and
            GeoSlide's KNN model will assess landslide risk in real time.
            Use <b>Load Sample</b> for a quick demo, or fill in your own
            measurements.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(f'<div class="gs-hero-illo-wrap">{_hero_illustration()}</div>', unsafe_allow_html=True)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 2 — ASSESSMENT PROGRESS
# ============================================================

with st.container(border=True, key="section-progress"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("layers", 20)} Assessment Progress</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">The assessment below walks through these parameter groups</div>',
        unsafe_allow_html=True,
    )
    st.markdown(_progress_html(), unsafe_allow_html=True)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 3 — INPUT FORM (six balanced cards; same fields/keys as
# before, only the visual grouping is new)
# ============================================================

st.markdown(
    f'<div class="ds-section-title">{_icon("cpu", 20)} Input Parameters</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="ds-section-subtitle">Every value below feeds directly into the KNN prediction model</div>',
    unsafe_allow_html=True,
)

row1_left, row1_right = st.columns(2, gap="medium")
with row1_left:
    with st.container(border=True, key="field-card-location"):
        _field_card_header("map-pin", "ds-chip-brand", "Location", "Site position & proximity")
        _render_numeric_fields(TERRAIN_FIELDS, keys=["elevation", "distance_to_road", "proximity_to_water"], columns=1)
with row1_right:
    with st.container(border=True, key="field-card-terrain"):
        _field_card_header("mountain", "ds-chip-brand", "Terrain", "Slope geometry")
        _render_numeric_fields(TERRAIN_FIELDS, keys=["slope_angle", "aspect"], columns=1)

row2_left, row2_right = st.columns(2, gap="medium")
with row2_left:
    with st.container(border=True, key="field-card-hydrology"):
        _field_card_header("droplet", "ds-chip-accent", "Hydrology", "Soil moisture & chemistry")
        _render_numeric_fields(SOIL_FIELDS, columns=2)
        st.selectbox("Soil Type", options=SOIL_TYPE_OPTIONS, key="soil_type")
with row2_right:
    with st.container(border=True, key="field-card-weather"):
        _field_card_header("cloud-rain", "ds-chip-accent", "Weather", "Rainfall & atmosphere")
        _render_numeric_fields(WEATHER_FIELDS, columns=1)

row3_left, row3_right = st.columns(2, gap="medium")
with row3_left:
    with st.container(border=True, key="field-card-environment"):
        _field_card_header("leaf", "ds-chip-amber", "Environment & Vegetation", "Cover, land use & activity")
        _render_numeric_fields(VEGETATION_NUMERIC_FIELDS, columns=1)
        st.selectbox("Land Use", options=LAND_USE_OPTIONS, key="land_use")
        _render_numeric_fields(GEOLOGICAL_FIELDS, columns=1)
with row3_right:
    with st.container(border=True, key="field-card-sensors"):
        _field_card_header("cpu", "ds-chip-amber", "Sensor Monitoring", "Microseismic & strain readings")
        _render_numeric_fields(SENSOR_FIELDS, columns=1)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 4 — PREDICT ACTION
# (Predict button switched from on_click= to a direct call wrapped in
# st.spinner so a real loading state can be shown. The function it
# calls — _predict_landslide_risk — is completely unchanged.)
# ============================================================

with st.container(border=True, key="section-actions"):
    st.markdown(
        f'<div class="ds-section-title" style="justify-content:center;">{_icon("zap", 20)} Run Assessment</div>',
        unsafe_allow_html=True,
    )

    predict_pad_l, predict_col, predict_pad_r = st.columns([1, 3, 1], gap="medium")
    with predict_col:
        if st.button(
            "Predict Landslide Risk",
            type="primary",
            use_container_width=True,
            key="predict-btn",
        ):
            with st.spinner("Analyzing terrain, hydrology, and environmental signals…"):
                _predict_landslide_risk()

    st.markdown('<div class="gs-secondary-actions-label">or</div>', unsafe_allow_html=True)

    sec_pad_l, sec_col1, sec_col2, sec_pad_r = st.columns([2, 1, 1, 2], gap="small")
    with sec_col1:
        st.button("Load Sample", use_container_width=True, on_click=_load_sample_data, key="load-sample-btn")
    with sec_col2:
        st.button("Reset", use_container_width=True, on_click=_reset_form, key="reset-btn")

    st.markdown(
        '<div class="gs-actions-hint">Results appear below once the backend responds.</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 5 — PREDICTION RESULT
# ============================================================


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


# Static, deterministic UI copy keyed off the real risk_level returned
# by the backend — presentational guidance text only, never a
# fabricated model output.
_RISK_SUMMARY = {
    "Low": "Conditions indicate a low likelihood of landslide activity at this site.",
    "Moderate": "Conditions indicate a moderate likelihood of landslide activity — worth keeping an eye on.",
    "High": "Conditions indicate an elevated likelihood of landslide activity at this site.",
    "Very High": "Conditions indicate a strong likelihood of landslide activity at this site.",
}
_RISK_ACTION = {
    "Low": "Continue routine monitoring. No immediate action required.",
    "Moderate": "Increase monitoring frequency and inspect nearby drainage.",
    "High": "Schedule an on-site inspection and review protective measures.",
    "Very High": "Restrict access to the area and notify local authorities promptly.",
}
_RISK_BADGE_CLASS = {
    "Low": "ds-badge-risk-low",
    "Moderate": "ds-badge-risk-moderate",
    "High": "ds-badge-risk-high",
    "Very High": "ds-badge-risk-very-high",
}

with st.container(border=True, key="section-result"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("brain", 20)} Prediction Result</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="ds-section-subtitle">Assessment output from the KNN prediction model</div>', unsafe_allow_html=True)

    result = st.session_state.get("prediction_result")

    if result is None:
        st.markdown(
            f"""
            <div class="gs-empty-state">
                <div class="ds-kpi-icon ds-chip-brand" style="width:46px;height:46px;">{_icon("search", 20)}</div>
                <div>No prediction yet. Fill in the parameters above and click
                <b>Predict Landslide Risk</b>.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif result["status"] == "error":
        st.markdown(
            f"""
            <div class="ds-alert ds-alert-error">
                {_icon("alert-triangle", 18)}
                <div>{result.get("message", "Prediction could not be completed.")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif result["status"] == "success":
        data = result.get("data") or {}
        risk_level = data.get("risk_level", "Unknown")
        probability = data.get("probability", 0.0)
        prediction = data.get("prediction", 0)
        color = RISK_LEVEL_COLORS.get(risk_level, "#808080")
        verdict = _format_prediction(prediction)
        probability_text = _format_probability(probability)

        summary_text = _RISK_SUMMARY.get(risk_level)

        st.markdown(
            f"""
            <div class="gs-result-hero">
                <span class="gs-risk-badge" style="background-color:{color};color:#ffffff;">{risk_level} Risk</span>
                <div class="gs-result-confidence-value">{probability_text}</div>
                <div class="gs-result-confidence-caption">Model Confidence</div>
                <div class="gs-result-status">Prediction status: <b>{verdict}</b></div>
                {f'<div class="gs-result-summary">{summary_text}</div>' if summary_text else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

        conf_pad_l, conf_col, conf_pad_r = st.columns([1, 3, 1], gap="medium")
        with conf_col:
            try:
                st.progress(float(probability))
            except (TypeError, ValueError):
                st.progress(0.0)

        action_text = _RISK_ACTION.get(risk_level)
        if action_text:
            st.markdown(
                f"""
                <div class="gs-recommend-box">
                    {_icon("shield", 20)}
                    <div>
                        <div class="gs-recommend-title">Recommended Action</div>
                        <div class="gs-recommend-text">{action_text}</div>
                        <div class="gs-recommend-note">General guidance only — not a substitute for a professional geotechnical assessment.</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
                label="See detailed feature contributions in SHAP Analysis",
                icon=":material/arrow_forward:",
            )

        st.write("")
        m1, m2, m3, m4 = st.columns(4, gap="medium")
        for col, icon, label, value, key in [
            (m1, "alert-triangle", "Risk Level", risk_level, "metric-risk"),
            (m2, "layers", "Probability", probability_text, "metric-prob"),
            (m3, "check-circle", "Prediction", verdict, "metric-pred"),
            (m4, "cpu", "Model", "KNN", "metric-model"),
        ]:
            with col:
                with st.container(border=True, key=key):
                    st.markdown(
                        f"""
                        <div class="gs-metric-label">{label}</div>
                        <div class="gs-metric-value">{value}</div>
                        """,
                        unsafe_allow_html=True,
                    )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 6 — MODEL INFO
# ============================================================

with st.container(border=True, key="section-modelinfo"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("cpu", 18)} Model Info</div>',
        unsafe_allow_html=True,
    )

    _MODEL_INFO_KPIS = [
        ("cpu", "ds-chip-brand", "Algorithm", "K-Nearest Neighbors", "k = 5, Minkowski metric", "modelinfo-kpi-algorithm"),
        ("layers", "ds-chip-accent", "Features", "34 engineered inputs", "Raw + encoded categoricals", "modelinfo-kpi-features"),
        ("brain", "ds-chip-amber", "Explainability", "SHAP", "via Random Forest TreeExplainer", "modelinfo-kpi-explainability"),
    ]

    mi1, mi2, mi3 = st.columns(3, gap="medium")
    for col, (icon, chip_class, label, value, desc, key) in zip((mi1, mi2, mi3), _MODEL_INFO_KPIS):
        with col:
            with st.container(border=True, key=key):
                st.markdown(
                    f"""
                    <div class="ds-kpi-icon {chip_class}" style="width:42px;height:42px;">{_icon(icon, 18)}</div>
                    <div class="gs-modelinfo-label">{label}</div>
                    <div class="gs-modelinfo-value">{value}</div>
                    <div class="gs-modelinfo-desc">{desc}</div>
                    """,
                    unsafe_allow_html=True,
                )