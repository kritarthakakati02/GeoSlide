"""
GeoSlide - SHAP Analysis Page
================================

This page presents SHAP-based explainability for the most recent
landslide risk prediction using the backend `/explain` endpoint.

UI note: this file was redesigned into a premium "Explainable AI"
dashboard (page-scoped dark theme, prediction summary card, chart
cards, two-column local-explanation badges, collapsible plain-language
interpretation). This mirrors the same redesign approach already used
on the Prediction page (1_🔍_Prediction.py) for visual consistency.

Nothing about *what* is computed changed:
    - `_get_current_feature_payload()` and `_load_latest_prediction()`
      are byte-for-byte unchanged from before the redesign.
    - The backend `/explain` call (utils.api.get_shap_explanation),
      the Random Forest SHAP explainer, and all prediction logic are
      untouched.
    - The existing charts (global feature importance bar chart, SHAP
      summary bar chart) use the exact same data and st.bar_chart
      calls as before - only their surrounding container/typography
      changed.

Only layout, typography, spacing, and presentation were touched.
"""

import pandas as pd
import streamlit as st

from components.sidebar import render_sidebar
from utils import api
from utils.constants import RISK_LEVEL_COLORS
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
# Formatting helpers (display-only, mirror the ones on the Prediction page)
# ---------------------------------------------------------------------------

def _format_probability(value) -> str:
    """Format a probability as a percentage rounded to one decimal place."""
    if value is None:
        return "—"
    try:
        probability = float(value)
    except (TypeError, ValueError):
        return "—"
    return f"{probability * 100:.1f}%"


def _format_prediction(value) -> str:
    """Translate numeric prediction values into user-friendly labels."""
    if value is None:
        return "—"
    text_value = str(value).strip()
    if text_value in {"0", "0.0", "No Landslide"}:
        return "No Landslide"
    if text_value in {"1", "1.0", "Landslide Likely"}:
        return "Landslide Likely"
    return str(value)


# ---------------------------------------------------------------------------
# Page-scoped dark theme + layout CSS
# ---------------------------------------------------------------------------
# Same scoping approach as the Prediction page: everything lives under
# [data-testid="stAppViewContainer"] and is only ever injected while this
# script is the active page, so it cannot leak into other pages. Uses the
# same design tokens (--gs-*) as 1_🔍_Prediction.py for a consistent look
# across the app.

SHAP_CSS = """
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

/* Cards (bordered containers used for the summary / chart / local-explanation blocks) */
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

[data-testid="stAppViewContainer"] button[kind="primary"] {
    background: linear-gradient(90deg, var(--gs-primary) 0%, var(--gs-accent) 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-size: 1.02rem;
    padding: 0.8rem 1.2rem !important;
    box-shadow: 0 14px 30px rgba(16, 185, 129, 0.3) !important;
}

[data-testid="stAppViewContainer"] button[kind="primary"]:hover {
    filter: brightness(1.06);
    transform: translateY(-2px);
}

/* Expander (used for the collapsible Interpretation card) */
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

.gs-page-subtitle {
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

.gs-risk-badge {
    display: inline-block;
    padding: 8px 20px;
    border-radius: 999px;
    font-size: 1.15rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.01em;
}

.gs-summary-eyebrow {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gs-muted);
    margin-bottom: 10px;
}

.gs-summary-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 18px;
    margin-top: 14px;
}

@media (max-width: 900px) {
    .gs-summary-grid { grid-template-columns: repeat(2, 1fr); }
}

.gs-summary-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.gs-summary-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gs-muted);
}

.gs-summary-value {
    font-size: 1.3rem;
    font-weight: 800;
    color: #F8FAFC;
}

.gs-empty-state {
    text-align: center;
    padding: 22px 10px;
    color: var(--gs-muted);
}

/* Local explanation contributor rows */
.gs-contrib-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.05rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 4px;
}

.gs-contrib-subcaption {
    font-size: 0.82rem;
    color: var(--gs-muted);
    margin-bottom: 14px;
}

.gs-contrib-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px;
    border-radius: 12px;
    margin-bottom: 10px;
    background: rgba(148, 163, 184, 0.06);
    border: 1px solid var(--gs-border);
}

.gs-contrib-feature {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1rem;
    font-weight: 700;
    color: var(--gs-text);
}

.gs-contrib-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}

.gs-contrib-value {
    font-size: 1.1rem;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 999px;
}

.gs-contrib-value.positive {
    color: #FCA5A5;
    background: rgba(239, 68, 68, 0.14);
}

.gs-contrib-value.negative {
    color: #6EE7B7;
    background: rgba(16, 185, 129, 0.14);
}

.gs-interpretation-rule {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
}

.gs-interpretation-rule .gs-contrib-dot {
    margin-top: 6px;
}

.gs-interpretation-text {
    font-size: 0.95rem;
    color: var(--gs-text);
    line-height: 1.55;
}

.gs-ai-note {
    font-size: 0.95rem;
    color: var(--gs-text);
    line-height: 1.6;
    margin-top: 10px;
}
"""

st.markdown(f"<style>{SHAP_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

render_sidebar()


# ---------------------------------------------------------------------------
# SECTION 1 — Page Header
# ---------------------------------------------------------------------------

st.markdown("## 🧠 Explainable AI")
st.markdown(
    '<div class="gs-page-subtitle">SHAP (SHapley Additive exPlanations) shows why the model '
    "made a given landslide risk prediction - which features mattered most overall, and which "
    "ones pushed this specific prediction higher or lower.</div>",
    unsafe_allow_html=True,
)
st.write("")

st.button("📥 Load Latest Prediction", type="primary", on_click=_load_latest_prediction)
st.write("")

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

st.write("")


# ---------------------------------------------------------------------------
# SECTION 2 — Latest Prediction Summary
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">Latest Prediction Summary</div>', unsafe_allow_html=True)

prediction_result = st.session_state.get("prediction_result")

with st.container(border=True):
    if not prediction_result or prediction_result.get("status") != "success":
        st.markdown(
            """
            <div class="gs-empty-state">
                <div style="font-size:1.6rem;">🛰️</div>
                <div style="margin-top:6px;">No prediction to explain yet. Run one on the
                <b>Prediction</b> page, then click <b>Load Latest Prediction</b> above.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        data = prediction_result.get("data") or {}
        risk_level = data.get("risk_level", "Unknown")
        probability = data.get("probability", 0.0)
        prediction = data.get("prediction", 0)
        color = RISK_LEVEL_COLORS.get(risk_level, "#808080")

        st.markdown('<div class="gs-summary-eyebrow">What this page is explaining</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="gs-risk-badge" style="background-color:{color};">{risk_level} Risk</span>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="gs-summary-grid">
                <div class="gs-summary-item">
                    <div class="gs-summary-label">Risk Level</div>
                    <div class="gs-summary-value" style="color:{color};">{risk_level}</div>
                </div>
                <div class="gs-summary-item">
                    <div class="gs-summary-label">Prediction</div>
                    <div class="gs-summary-value">{_format_prediction(prediction)}</div>
                </div>
                <div class="gs-summary-item">
                    <div class="gs-summary-label">Probability</div>
                    <div class="gs-summary-value">{_format_probability(probability)}</div>
                </div>
                <div class="gs-summary-item">
                    <div class="gs-summary-label">Confidence</div>
                    <div class="gs-summary-value">{_format_probability(probability)}</div>
                </div>
                <div class="gs-summary-item">
                    <div class="gs-summary-label">Model</div>
                    <div class="gs-summary-value" style="font-size:1.05rem;">K-Nearest Neighbors</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="gs-section-caption">Prediction and probability come from the deployed '
            "KNN model; the SHAP breakdown below is generated by a Random Forest surrogate model "
            "trained on the same features, used exclusively for explainability.</div>",
            unsafe_allow_html=True,
        )

st.write("")


# ---------------------------------------------------------------------------
# SECTION 3 — Global Feature Importance
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">📊 Global Feature Importance</div>', unsafe_allow_html=True)

with st.container(border=True):
    if explanation is None:
        st.markdown(
            '<div class="gs-empty-state">Feature importance chart will appear here once data is loaded.</div>',
            unsafe_allow_html=True,
        )
    else:
        importance_df = pd.DataFrame(explanation.get("feature_importance", []))
        if importance_df.empty:
            st.markdown(
                '<div class="gs-empty-state">No feature importance data available.</div>',
                unsafe_allow_html=True,
            )
        else:
            importance_df = importance_df.sort_values("importance", ascending=True)
            st.bar_chart(
                importance_df.set_index("feature"),
                horizontal=True,
                use_container_width=True,
            )
    st.markdown(
        '<div class="gs-section-caption">This chart shows which features are most influential '
        "across the dataset.</div>",
        unsafe_allow_html=True,
    )

st.write("")


# ---------------------------------------------------------------------------
# SECTION 4 — SHAP Summary Plot
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">🐝 SHAP Summary Plot</div>', unsafe_allow_html=True)

with st.container(border=True):
    if explanation is None or not explanation.get("feature_names"):
        st.markdown(
            '<div class="gs-empty-state">No SHAP values are available yet.</div>',
            unsafe_allow_html=True,
        )
    else:
        feature_names = explanation.get("feature_names", [])
        shap_values = explanation.get("shap_values", [])
        summary_df = pd.DataFrame({"feature": feature_names, "shap_value": shap_values})
        summary_df = summary_df.sort_values("shap_value", key=lambda s: s.abs(), ascending=False)
        st.bar_chart(summary_df.set_index("feature")["shap_value"], use_container_width=True)
    st.markdown(
        '<div class="gs-section-caption">Each bar is the signed SHAP value for one feature on this '
        "specific prediction - bars pointing one way increase risk, bars pointing the other way "
        "decrease it.</div>",
        unsafe_allow_html=True,
    )

st.write("")


# ---------------------------------------------------------------------------
# SECTION 5 — Local Explanation
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">🔎 Local Explanation</div>', unsafe_allow_html=True)

local = (explanation or {}).get("local_explanation", {})
positive_features = local.get("positive", [])
negative_features = local.get("negative", [])

col_pos, col_neg = st.columns(2, gap="medium")

with col_pos:
    with st.container(border=True):
        st.markdown(
            '<div class="gs-contrib-heading">🟢 Positive Contributors</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="gs-contrib-subcaption">Features pushing this prediction toward higher risk.</div>',
            unsafe_allow_html=True,
        )
        if explanation is None or not positive_features:
            st.markdown(
                '<div class="gs-empty-state">No positive contributors available.</div>',
                unsafe_allow_html=True,
            )
        else:
            rows = ""
            for item in positive_features:
                rows += f"""
                <div class="gs-contrib-row">
                    <div class="gs-contrib-feature">
                        <span class="gs-contrib-dot" style="background:#EF4444;"></span>
                        {item["feature"]}
                    </div>
                    <div class="gs-contrib-value positive">+{item["impact"]:.2f}</div>
                </div>
                """
            st.markdown(rows, unsafe_allow_html=True)

with col_neg:
    with st.container(border=True):
        st.markdown(
            '<div class="gs-contrib-heading">🔴 Negative Contributors</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="gs-contrib-subcaption">Features pushing this prediction toward lower risk.</div>',
            unsafe_allow_html=True,
        )
        if explanation is None or not negative_features:
            st.markdown(
                '<div class="gs-empty-state">No negative contributors available.</div>',
                unsafe_allow_html=True,
            )
        else:
            rows = ""
            for item in negative_features:
                rows += f"""
                <div class="gs-contrib-row">
                    <div class="gs-contrib-feature">
                        <span class="gs-contrib-dot" style="background:#10B981;"></span>
                        {item["feature"]}
                    </div>
                    <div class="gs-contrib-value negative">{item["impact"]:.2f}</div>
                </div>
                """
            st.markdown(rows, unsafe_allow_html=True)

st.write("")


# ---------------------------------------------------------------------------
# SECTION 6 — Interpretation (collapsible)
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">💬 Interpretation</div>', unsafe_allow_html=True)

with st.expander("ℹ️ How to read these results", expanded=True):
    st.markdown(
        """
        <div class="gs-interpretation-rule">
            <span class="gs-contrib-dot" style="background:#EF4444;"></span>
            <div class="gs-interpretation-text">
                <b>Positive SHAP values</b> mean that feature made the model think the
                landslide risk was <b>higher</b> than average for this location.
            </div>
        </div>
        <div class="gs-interpretation-rule">
            <span class="gs-contrib-dot" style="background:#10B981;"></span>
            <div class="gs-interpretation-text">
                <b>Negative SHAP values</b> mean that feature made the model think the
                landslide risk was <b>lower</b> than average for this location.
            </div>
        </div>
        <div class="gs-interpretation-rule">
            <span class="gs-contrib-dot" style="background:#3B82F6;"></span>
            <div class="gs-interpretation-text">
                The <b>bigger</b> the value (positive or negative), the <b>stronger</b> that
                feature's pull on the final prediction.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if explanation is not None:
        st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="gs-ai-note">{explanation.get("ai_interpretation", "No interpretation available.")}</div>',
            unsafe_allow_html=True,
        )
        if explanation.get("status") == "error":
            st.caption("⚠️ The explanation endpoint could not be reached or returned an error.")