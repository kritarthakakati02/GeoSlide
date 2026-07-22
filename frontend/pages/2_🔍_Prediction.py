"""
GeoSlide - Prediction Page
============================
Phase 10.3 (Part 1): Prediction Page UI.

This page collects environmental and geological parameters from the
user via a series of organized expanders, and provides buttons to load
sample data, reset the form, and (in a future phase) run a prediction.

NOTE: This phase implements ONLY the UI. No prediction logic, no API
requests, and no SHAP explanations are implemented here.
"""

import streamlit as st

from utils import api
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
# Field definitions
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
# Session State Initialization
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
# Button Callbacks
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
    Gather form inputs, encode categorical fields, and (in a future
    phase) call the backend prediction API.

    For Phase 10.3 (Part 1), this only wires up the button so the UI
    is complete. The actual prediction call is not implemented yet.
    """
    payload = _collect_form_payload()

    try:
        result = api.predict(payload)
        st.session_state["prediction_result"] = {
            "status": "success",
            "data": result,
        }
    except NotImplementedError:
        st.session_state["prediction_result"] = {
            "status": "not_implemented",
            "data": None,
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
# Page Header
# ---------------------------------------------------------------------------

st.title("🔍 Landslide Risk Prediction")
st.markdown("Enter environmental and geological parameters to assess landslide risk.")
st.divider()


# ---------------------------------------------------------------------------
# Helper for rendering a numeric field grid inside an expander
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
# 1. Weather Conditions
# ---------------------------------------------------------------------------

with st.expander("🌧️ Weather Conditions", expanded=True):
    _render_numeric_fields(WEATHER_FIELDS)


# ---------------------------------------------------------------------------
# 2. Terrain & Geography
# ---------------------------------------------------------------------------

with st.expander("⛰️ Terrain & Geography", expanded=False):
    _render_numeric_fields(TERRAIN_FIELDS)


# ---------------------------------------------------------------------------
# 3. Soil Characteristics
# ---------------------------------------------------------------------------

with st.expander("🧪 Soil Characteristics", expanded=False):
    _render_numeric_fields(SOIL_FIELDS)


# ---------------------------------------------------------------------------
# 4. Vegetation & Land Use
# ---------------------------------------------------------------------------

with st.expander("🌱 Vegetation & Land Use", expanded=False):
    _render_numeric_fields(VEGETATION_NUMERIC_FIELDS)
    st.selectbox(
        "Land Use",
        options=LAND_USE_OPTIONS,
        key="land_use",
    )


# ---------------------------------------------------------------------------
# 5. Geological Activity
# ---------------------------------------------------------------------------

with st.expander("🌋 Geological Activity", expanded=False):
    _render_numeric_fields(GEOLOGICAL_FIELDS)


# ---------------------------------------------------------------------------
# 6. Sensor Measurements
# ---------------------------------------------------------------------------

with st.expander("📡 Sensor Measurements", expanded=False):
    _render_numeric_fields(SENSOR_FIELDS)


# ---------------------------------------------------------------------------
# 7. Soil Type
# ---------------------------------------------------------------------------

with st.expander("🪨 Soil Type", expanded=False):
    st.selectbox(
        "Soil Type",
        options=SOIL_TYPE_OPTIONS,
        key="soil_type",
    )


st.divider()


# ---------------------------------------------------------------------------
# Action Buttons
# ---------------------------------------------------------------------------

btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    st.button(
        "📂 Load Sample Data",
        use_container_width=True,
        on_click=_load_sample_data,
    )

with btn_col2:
    st.button(
        "🔄 Reset Form",
        use_container_width=True,
        on_click=_reset_form,
    )

with btn_col3:
    st.button(
        "🚨 Predict Landslide Risk",
        type="primary",
        use_container_width=True,
        on_click=_predict_landslide_risk,
    )


st.divider()


# ---------------------------------------------------------------------------
# Prediction Result Placeholder
# ---------------------------------------------------------------------------

st.subheader("Prediction Result")

result_container = st.container()

with result_container:
    result = st.session_state.get("prediction_result")

    if result is None:
        st.info("No prediction yet. Fill in the parameters above and click **Predict Landslide Risk**.")
    elif result["status"] == "not_implemented":
        st.warning(
            "Prediction logic is not implemented yet. "
            "This will be available in a future phase."
        )
        placeholder_col1, placeholder_col2, placeholder_col3 = st.columns(3)
        with placeholder_col1:
            st.metric("Risk Level", "—")
        with placeholder_col2:
            st.metric("Probability", "—")
        with placeholder_col3:
            st.metric("Prediction Status", "Pending")
    elif result["status"] == "success":
        # Reserved for a future phase once api.predict() is implemented.
        data = result["data"] or {}
        placeholder_col1, placeholder_col2, placeholder_col3 = st.columns(3)
        with placeholder_col1:
            st.metric("Risk Level", data.get("risk_level", "—"))
        with placeholder_col2:
            st.metric("Probability", data.get("probability", "—"))
        with placeholder_col3:
            st.metric("Prediction Status", data.get("status", "—"))
