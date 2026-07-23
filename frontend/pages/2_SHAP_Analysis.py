"""
GeoSlide - SHAP Analysis Page
================================

This page presents SHAP-based explainability for the most recent
landslide risk prediction using the backend `/explain` endpoint.
"""

import pandas as pd
import streamlit as st

from components.sidebar import render_sidebar
from utils import api
from utils.helpers import FORM_FIELD_TO_FEATURE_NAME, encode_land_use, encode_soil_type


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SHAP Analysis | GeoSlide",
    page_icon="🧠",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------

st.session_state.setdefault("shap_explanation", None)


def _get_current_feature_payload() -> dict:
    """
    Rebuild the raw feature payload for the parameters currently set on
    the Prediction page's form. Streamlit's session_state is shared across
    pages, and the Prediction page's widgets are bound to these same keys
    (see FORM_FIELD_TO_FEATURE_NAME / "land_use" / "soil_type"), so this
    lets the SHAP page explain the real inputs behind the most recent
    prediction without needing to read or modify the Prediction page.
    """
    payload = {key: st.session_state.get(key, 0.0) for key in FORM_FIELD_TO_FEATURE_NAME}
    payload.update(encode_land_use(st.session_state.get("land_use", "")))
    payload.update(encode_soil_type(st.session_state.get("soil_type", "")))
    return payload


def _load_latest_prediction() -> None:
    """Load a real SHAP explainability breakdown for the most recent prediction."""
    prediction_result = st.session_state.get("prediction_result")

    if not prediction_result or prediction_result.get("status") != "success":
        st.session_state["shap_explanation"] = {
            "feature_importance": [],
            "local_explanation": {"positive": [], "negative": []},
            "ai_interpretation": (
                "No prediction found yet. Run a prediction on the Prediction "
                "page first, then come back and load it here."
            ),
            "status": "error",
            "feature_names": [],
            "shap_values": [],
            "top_positive_contributors": [],
            "top_negative_contributors": [],
        }
        return

    payload = _get_current_feature_payload()

    try:
        explanation = api.get_shap_explanation(payload)
    except Exception as exc:
        explanation = {
            "feature_importance": [],
            "local_explanation": {"positive": [], "negative": []},
            "ai_interpretation": f"Unable to load explanation: {exc}",
            "status": "error",
            "feature_names": [],
            "shap_values": [],
            "top_positive_contributors": [],
            "top_negative_contributors": [],
        }

    st.session_state["shap_explanation"] = explanation


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

render_sidebar()

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------

st.title("🧠 SHAP Explainability")
st.markdown(
    "SHAP (SHapley Additive exPlanations) highlights the features that "
    "most influenced the model's landslide risk prediction, showing both "
    "the overall importance of each feature and how it pushed a specific "
    "prediction higher or lower."
)

st.button("📥 Load Latest Prediction", type="primary", on_click=_load_latest_prediction)

st.divider()

explanation = st.session_state.get("shap_explanation")

if explanation is None:
    st.info(
        "No SHAP data loaded yet. Click **Load Latest Prediction** above "
        "to view an explainability breakdown."
    )
    if st.session_state.get("prediction_result") is None:
        st.caption(
            "Tip: No prediction has been run yet in this session. Run one "
            "on the Prediction page first for the most meaningful "
            "explanation."
        )


# ---------------------------------------------------------------------------
# 1. Feature Importance
# ---------------------------------------------------------------------------

st.subheader("📊 Feature Importance")
st.caption("Global ranking of which features most influence the model overall.")

with st.container(border=True):
    if explanation is None:
        st.write("_Feature importance chart will appear here once data is loaded._")
    else:
        importance_df = pd.DataFrame(explanation.get("feature_importance", []))
        if importance_df.empty:
            st.write("_No feature importance data available._")
        else:
            importance_df = importance_df.sort_values("importance", ascending=True)
            st.bar_chart(
                importance_df.set_index("feature"),
                horizontal=True,
                use_container_width=True,
            )

st.divider()


# ---------------------------------------------------------------------------
# 2. SHAP Summary Plot
# ---------------------------------------------------------------------------

st.subheader("🐝 SHAP Summary Plot")
st.caption("Distribution of SHAP values across features (beeswarm-style summary).")

with st.container(border=True):
    if explanation is None or not explanation.get("feature_names"):
        st.write("_No SHAP values are available yet._")
    else:
        feature_names = explanation.get("feature_names", [])
        shap_values = explanation.get("shap_values", [])
        summary_df = pd.DataFrame({"feature": feature_names, "shap_value": shap_values})
        summary_df = summary_df.sort_values("shap_value", key=lambda s: s.abs(), ascending=False)
        st.bar_chart(summary_df.set_index("feature")["shap_value"], use_container_width=True)

st.divider()


# ---------------------------------------------------------------------------
# 3. Local Explanation
# ---------------------------------------------------------------------------

st.subheader("🔎 Local Explanation")
st.caption("Top features pushing this specific prediction higher or lower.")

col_pos, col_neg = st.columns(2)

local = (explanation or {}).get("local_explanation", {})
positive_features = local.get("positive", [])
negative_features = local.get("negative", [])

with col_pos:
    st.markdown("**⬆️ Top Positive Contributors** _(increase risk)_")
    if explanation is None or not positive_features:
        st.write("_No positive contributors available._")
    else:
        for item in positive_features:
            st.metric(item["feature"], f'+{item["impact"]:.2f}')

with col_neg:
    st.markdown("**⬇️ Top Negative Contributors** _(decrease risk)_")
    if explanation is None or not negative_features:
        st.write("_No negative contributors available._")
    else:
        for item in negative_features:
            st.metric(item["feature"], f'{item["impact"]:.2f}')

st.divider()


# ---------------------------------------------------------------------------
# 4. AI Interpretation
# ---------------------------------------------------------------------------

st.subheader("💬 AI Interpretation")
st.caption("Natural-language summary of what drove this prediction.")

with st.container(border=True):
    if explanation is None:
        st.write("_AI-generated interpretation will appear here once data is loaded._")
    else:
        st.markdown(explanation.get("ai_interpretation", "_No interpretation available._"))
        if explanation.get("status") == "error":
            st.caption("⚠️ The explanation endpoint could not be reached or returned an error.")
