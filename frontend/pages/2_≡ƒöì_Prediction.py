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
"""

import streamlit as st

from components.sidebar import render_sidebar
from utils import api
from utils.constants import RISK_LEVEL_COLORS
from utils.helpers import (
    LAND_USE_OPTIONS,
    SOIL_TYPE_OPTIONS,
    build_feature_vector,
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
<<<<<<<< HEAD:frontend/pages/1_🔍_Prediction.py
    """Gather form inputs, build the backend payload, and store the prediction result."""
========
    """
    Gather form inputs, encode categorical fields, build the ordered
    feature vector the model expects, and call the backend prediction
    API.

    Any failure (validation, connection, timeout, bad response) is
    caught and stored in session_state so the UI can show a clear
    error message instead of crashing.
    """
>>>>>>>> 9274063391122d774fc7099c2286f5496e15e6ba:frontend/pages/2_≡ƒöì_Prediction.py
    payload = _collect_form_payload()
    result = api.predict(payload)

<<<<<<<< HEAD:frontend/pages/1_🔍_Prediction.py
    if result.get("status") == "success":
========
    try:
        features = build_feature_vector(payload)
        result = api.predict(features)
>>>>>>>> 9274063391122d774fc7099c2286f5496e15e6ba:frontend/pages/2_≡ƒöì_Prediction.py
        st.session_state["prediction_result"] = {
            "status": "success",
            "data": result.get("data", {}),
        }
<<<<<<<< HEAD:frontend/pages/1_🔍_Prediction.py
    else:
        st.session_state["prediction_result"] = {
            "status": "error",
            "data": result.get("data", {}),
========
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
>>>>>>>> 9274063391122d774fc7099c2286f5496e15e6ba:frontend/pages/2_≡ƒöì_Prediction.py
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
# Sidebar
# ---------------------------------------------------------------------------

render_sidebar()

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
# Prediction Result
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


def _get_risk_badge(value):
    """Return a color and label for the risk badge."""
    if value is None:
        return None, "—"

    normalized = str(value).strip().lower()
    if "very" in normalized and "high" in normalized:
        return "#dc3545", "Very High"
    if "high" in normalized:
        return "#fd7e14", "High"
    if "moderate" in normalized:
        return "#ffc107", "Moderate"
    if "low" in normalized:
        return "#28a745", "Low"

    return "#6c757d", str(value)


st.subheader("Prediction Result")

result_container = st.container()

with result_container:
    result = st.session_state.get("prediction_result")

    if result is None:
        st.info("No prediction yet. Fill in the parameters above and click **Predict Landslide Risk**.")
<<<<<<<< HEAD:frontend/pages/1_🔍_Prediction.py
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
            st.metric("Prediction", "Pending")
    elif result["status"] == "success":
        data = result["data"] or {}
        risk_level = data.get("risk_level", "—")
        probability = data.get("probability")
        prediction = data.get("prediction", "—")
        badge_color, badge_text = _get_risk_badge(risk_level)

        placeholder_col1, placeholder_col2, placeholder_col3 = st.columns(3)
        with placeholder_col1:
            st.metric("Risk Level", risk_level if risk_level != "—" else "—")
            if badge_color and risk_level != "—":
                st.markdown(
                    f'<span style="display:inline-block;padding:4px 10px;border-radius:999px;background-color:{badge_color};color:white;font-weight:600;">{badge_text}</span>',
                    unsafe_allow_html=True,
                )
        with placeholder_col2:
            st.metric("Probability", _format_probability(probability))
            if probability is not None:
                try:
                    st.progress(float(probability))
                except (TypeError, ValueError):
                    st.progress(0.0)
        with placeholder_col3:
            st.metric("Prediction", _format_prediction(prediction))
    else:
        data = result["data"] or {}
        st.error(data.get("error", "Prediction could not be completed."))
        placeholder_col1, placeholder_col2, placeholder_col3 = st.columns(3)
        with placeholder_col1:
            st.metric("Risk Level", "—")
        with placeholder_col2:
            st.metric("Probability", "—")
        with placeholder_col3:
            st.metric("Prediction", "—")
========

    elif result["status"] == "error":
        st.error(result["message"])

    elif result["status"] == "success":
        data = result["data"]
        risk_level = data.get("risk_level", "Unknown")
        probability = data.get("probability", 0.0)
        prediction = data.get("prediction", 0)
        probability_pct = probability * 100
        color = RISK_LEVEL_COLORS.get(risk_level, "#808080")
        verdict = "Landslide Likely" if prediction == 1 else "No Landslide Predicted"

        st.markdown(
            f"""
            <div style="
                border-left: 6px solid {color};
                background-color: rgba(128, 128, 128, 0.08);
                border-radius: 10px;
                padding: 1.25rem 1.5rem;
                margin-bottom: 1rem;
            ">
                <div style="font-size: 0.9rem; opacity: 0.75; letter-spacing: 0.03em; text-transform: uppercase;">
                    Assessment Result
                </div>
                <div style="font-size: 1.6rem; font-weight: 700; color: {color}; margin-top: 0.25rem;">
                    {risk_level} Risk
                </div>
                <div style="font-size: 1rem; opacity: 0.85; margin-top: 0.25rem;">
                    {verdict}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Risk Level", risk_level)
        with metric_col2:
            st.metric("Landslide Probability", f"{probability_pct:.1f}%")
        with metric_col3:
            st.metric("Predicted Class", "Landslide" if prediction == 1 else "No Landslide")

        st.progress(min(max(probability, 0.0), 1.0))
>>>>>>>> 9274063391122d774fc7099c2286f5496e15e6ba:frontend/pages/2_≡ƒöì_Prediction.py
