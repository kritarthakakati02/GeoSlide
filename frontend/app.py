"""
app.py

Purpose:
    Main entry point for the GeoSlide Streamlit frontend application.
    Renders the Home Dashboard: hero section, key metric cards,
    core feature cards, an About section, and a footer.

Phase 10.2 - Home Dashboard:
    - Page configuration (title, icon, wide layout)
    - Hero section (title, subtitle, short description)
    - Four summary metric cards (st.metric)
    - Core Features section (four feature cards)
    - About section
    - Footer

Scope note:
    This phase implements only the Home Dashboard layout using
    Streamlit's built-in components. No custom CSS, no charts, no
    FastAPI/API connectivity, and no prediction logic are included
    here. Individual pages under `pages/` are not modified.
"""

import streamlit as st

# -----------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="GeoSlide AI",
    page_icon="🏔️",
    layout="wide",
)

# -----------------------------------------------------------------------
# Hero section
# -----------------------------------------------------------------------
st.title("🏔️ GeoSlide AI")
st.subheader("Machine Learning-Based Landslide Risk Assessment System")
st.write(
    "GeoSlide AI is a machine learning platform designed to assess and "
    "predict landslide risk using environmental and geospatial data. "
    "The system combines predictive modeling with explainable AI to help "
    "researchers, planners, and decision-makers better understand "
    "landslide susceptibility across different regions."
)

st.divider()

# -----------------------------------------------------------------------
# Key metrics
# -----------------------------------------------------------------------
st.subheader("Project Highlights")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric(label="Model Accuracy", value="97.82%")

with metric_col2:
    st.metric(label="Dataset Size", value="9864 Rows")

with metric_col3:
    st.metric(label="Best Model", value="KNN")

with metric_col4:
    st.metric(label="Features", value="34")

st.divider()

# -----------------------------------------------------------------------
# Core Features section
# -----------------------------------------------------------------------
st.subheader("Core Features")

feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)

with feature_col1:
    with st.container(border=True):
        st.markdown("### 🔍")
        st.markdown("**Landslide Prediction**")
        st.write(
            "Assess landslide risk based on environmental and "
            "geospatial input parameters."
        )

with feature_col2:
    with st.container(border=True):
        st.markdown("### 📊")
        st.markdown("**Explainable AI (SHAP)**")
        st.write(
            "Understand model predictions through SHAP-based "
            "feature importance analysis."
        )

with feature_col3:
    with st.container(border=True):
        st.markdown("### 🗺️")
        st.markdown("**Historical Landslide Map**")
        st.write(
            "Explore historical landslide occurrences on an "
            "interactive map."
        )

with feature_col4:
    with st.container(border=True):
        st.markdown("### 📈")
        st.markdown("**Dataset Analytics**")
        st.write(
            "Review exploratory statistics and insights from the "
            "underlying dataset."
        )

st.divider()

# -----------------------------------------------------------------------
# About section
# -----------------------------------------------------------------------
st.subheader("About")
st.write(
    "GeoSlide AI brings together machine learning and geospatial "
    "analysis to support landslide risk assessment. The project "
    "integrates a trained predictive model, explainability tools, "
    "historical landslide records, and dataset analytics into a "
    "single, accessible platform aimed at supporting research and "
    "informed decision-making."
)

st.divider()

# -----------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------
st.caption("Developed using: FastAPI · Streamlit · Scikit-Learn · SHAP")
