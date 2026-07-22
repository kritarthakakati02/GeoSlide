"""
GeoSlide AI - Home Dashboard
"""

import streamlit as st

from utils.theme import load_styles
from components.metrics import metric_row
from components.section_header import section_header
from components.sidebar import render_sidebar

# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="GeoSlide AI",
    page_icon="🏔️",
    layout="wide",
)

st.markdown(
    f"<style>{load_styles()}</style>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
render_sidebar()

# ============================================================
# HERO
# ============================================================

section_header(
    title="GeoSlide AI",
    subtitle="Machine Learning-Based Landslide Risk Assessment System",
    icon="🏔️",
)

st.write(
    """
GeoSlide AI is an Explainable AI platform that predicts landslide
risk using environmental, geological and sensor data.

The application combines machine learning, SHAP explainability,
historical NASA landslide visualization and interactive analytics
into one professional dashboard.
"""
)

st.write("")

# ============================================================
# PROJECT HIGHLIGHTS
# ============================================================

section_header(
    title="Project Highlights",
    icon="📊",
)

metric_row(
    [
        {
            "title": "Model Accuracy",
            "value": "97.82%",
            "icon": "🎯",
        },
        {
            "title": "Dataset Size",
            "value": "9864",
            "icon": "📁",
        },
        {
            "title": "Best Model",
            "value": "KNN",
            "icon": "🤖",
        },
        {
            "title": "Features",
            "value": "34",
            "icon": "📈",
        },
    ]
)

st.write("")

# ============================================================
# CORE FEATURES
# ============================================================

section_header(
    title="Core Features",
    icon="🚀",
)

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.markdown("### 🔍 Landslide Prediction")

        st.write(
            """
Predict landslide susceptibility from environmental
and geological parameters.
"""
        )

    with st.container(border=True):

        st.markdown("### 🧠 Explainable AI")

        st.write(
            """
Understand why the model predicted a specific
risk level using SHAP explanations.
"""
        )

with col2:

    with st.container(border=True):

        st.markdown("### 🌍 Historical Landslide Map")

        st.write(
            """
Visualize historical landslide events from the
NASA Global Landslide Catalog.
"""
        )

    with st.container(border=True):

        st.markdown("### 📊 Dataset Analytics")

        st.write(
            """
Explore feature distributions, correlations
and dataset statistics.
"""
        )

st.write("")

# ============================================================
# ABOUT
# ============================================================

section_header(
    title="About GeoSlide",
    icon="ℹ️",
)

st.write(
    """
GeoSlide AI was developed as a Machine Learning internship project
to demonstrate an end-to-end AI pipeline for landslide risk
assessment.

The system integrates:

• Machine Learning prediction

• Explainable AI (SHAP)

• FastAPI backend

• Streamlit dashboard

• Historical NASA landslide visualization

• Dataset analytics
"""
)

st.divider()

st.caption(
    "Developed using FastAPI • Streamlit • Scikit-Learn • SHAP • Plotly • Folium"
)