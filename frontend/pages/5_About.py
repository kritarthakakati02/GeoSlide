"""
GeoSlide - About Page
========================
Phase 10.7: About Page.

A static, presentation-ready overview of the GeoSlide project: what it
does, how it works, the technology stack, key highlights, system
architecture, datasets used, the developer behind it, and
acknowledgements.

This page is purely informational — no data loading, no charts, no
API calls.
"""

import streamlit as st

from components.sidebar import render_sidebar


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="About | GeoSlide",
    page_icon="ℹ️",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

render_sidebar()

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------

st.title("ℹ️ About GeoSlide")
st.markdown("An Explainable AI system for Landslide Risk Assessment.")
st.divider()


# ---------------------------------------------------------------------------
# Section 1 — Project Overview
# ---------------------------------------------------------------------------

st.subheader("🎯 Project Overview")

with st.container(border=True):
    st.markdown(
        "**GeoSlide** predicts landslide risk using machine learning, "
        "and explains every prediction using **SHAP** — so users don't "
        "just get a risk score, they understand *why*."
    )

st.divider()


# ---------------------------------------------------------------------------
# Section 2 — How GeoSlide Works (Workflow Diagram)
# ---------------------------------------------------------------------------

st.subheader("⚙️ How GeoSlide Works")

WORKFLOW_STEPS = [
    ("🗂️", "Dataset"),
    ("🧹", "Preprocessing"),
    ("🛠️", "Feature Engineering"),
    ("📍", "KNN Prediction"),
    ("🧠", "SHAP Explainability"),
    ("📊", "Interactive Dashboard"),
]

workflow_cols = st.columns(len(WORKFLOW_STEPS) * 2 - 1)

for idx, (icon, label) in enumerate(WORKFLOW_STEPS):
    col_idx = idx * 2
    with workflow_cols[col_idx]:
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center; font-size:1.8rem;'>{icon}</div>"
                f"<div style='text-align:center; font-weight:600; font-size:0.85rem;'>{label}</div>",
                unsafe_allow_html=True,
            )
    if col_idx + 1 < len(workflow_cols):
        with workflow_cols[col_idx + 1]:
            st.markdown(
                "<div style='text-align:center; font-size:1.8rem; margin-top:0.6rem;'>➡️</div>",
                unsafe_allow_html=True,
            )

st.divider()


# ---------------------------------------------------------------------------
# Section 3 — Technology Stack
# ---------------------------------------------------------------------------

st.subheader("🧰 Technology Stack")

TECH_STACK = [
    ("🐍", "Python", "Core language"),
    ("⚡", "FastAPI", "Backend API"),
    ("🎈", "Streamlit", "Frontend dashboard"),
    ("🤖", "Scikit-learn", "ML modeling"),
    ("🧠", "SHAP", "Explainability"),
    ("📈", "Plotly", "Interactive charts"),
    ("🗺️", "Folium", "Interactive maps"),
    ("🐼", "Pandas", "Data processing"),
    ("💾", "Joblib", "Model persistence"),
]

tech_cols = st.columns(3)
for idx, (icon, name, desc) in enumerate(TECH_STACK):
    with tech_cols[idx % 3]:
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center; font-size:1.6rem;'>{icon}</div>"
                f"<div style='text-align:center; font-weight:600;'>{name}</div>"
                f"<div style='text-align:center; font-size:0.8rem; color:gray;'>{desc}</div>",
                unsafe_allow_html=True,
            )

st.divider()


# ---------------------------------------------------------------------------
# Section 4 — Project Highlights
# ---------------------------------------------------------------------------

st.subheader("✨ Project Highlights")

HIGHLIGHTS = [
    ("🧬", "34 Features"),
    ("📍", "KNN Model"),
    ("🧠", "Explainable AI"),
    ("📊", "Interactive Dashboard"),
    ("🌍", "Historical Map"),
    ("📈", "Analytics"),
]

highlight_cols = st.columns(3)
for idx, (icon, label) in enumerate(HIGHLIGHTS):
    with highlight_cols[idx % 3]:
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center; font-size:1.8rem;'>{icon}</div>"
                f"<div style='text-align:center; font-weight:600;'>{label}</div>",
                unsafe_allow_html=True,
            )

st.divider()


# ---------------------------------------------------------------------------
# Section 5 — Project Architecture
# ---------------------------------------------------------------------------

st.subheader("🏗️ Project Architecture")

ARCHITECTURE_LAYERS = [
    ("🎈", "Frontend", "Streamlit multi-page dashboard for prediction, SHAP analysis, maps, and analytics."),
    ("⚡", "Backend", "FastAPI service handling prediction requests and model inference."),
    ("🤖", "Models", "Trained KNN model and preprocessing pipeline, persisted with Joblib."),
    ("🗂️", "Datasets", "Sensor and historical landslide data used for training and analytics."),
]

arch_cols = st.columns(4)
for idx, (icon, layer, desc) in enumerate(ARCHITECTURE_LAYERS):
    with arch_cols[idx]:
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center; font-size:1.8rem;'>{icon}</div>"
                f"<div style='text-align:center; font-weight:700;'>{layer}</div>"
                f"<div style='text-align:center; font-size:0.8rem; color:gray;'>{desc}</div>",
                unsafe_allow_html=True,
            )

st.divider()


# ---------------------------------------------------------------------------
# Section 6 — Datasets
# ---------------------------------------------------------------------------

st.subheader("🗃️ Datasets")

DATASETS = [
    ("📡", "Wireless Sensor Network Dataset", "Ground-based sensor readings (soil, seismic, and acoustic measurements) used to train the risk prediction model."),
    ("🛰️", "NASA Global Landslide Catalog", "Historical, geolocated landslide events used for the Historical Map and trend analysis."),
]

dataset_cols = st.columns(2)
for idx, (icon, name, desc) in enumerate(DATASETS):
    with dataset_cols[idx]:
        with st.container(border=True):
            st.markdown(f"### {icon} {name}")
            st.markdown(desc)

st.divider()


# ---------------------------------------------------------------------------
# Section 7 — Developer
# ---------------------------------------------------------------------------

st.subheader("👨‍💻 Developer")

with st.container(border=True):
    dev_col1, dev_col2, dev_col3 = st.columns(3)
    with dev_col1:
        st.markdown("**🧑 Name**")
        st.markdown("_Add developer name here_")
    with dev_col2:
        st.markdown("**🎓 College**")
        st.markdown("_Add college / university name here_")
    with dev_col3:
        st.markdown("**💼 Internship**")
        st.markdown("_Add internship program name here_")

st.divider()


# ---------------------------------------------------------------------------
# Section 8 — Acknowledgements
# ---------------------------------------------------------------------------

st.subheader("🙏 Acknowledgements")

ACKNOWLEDGEMENTS = [
    ("📚", "Open Source Libraries", "Built on the shoulders of the Python open-source ecosystem."),
    ("🏫", "SMIT", "For providing training and mentorship support."),
    ("🌐", "IAESTE Internship", "For the internship opportunity that made this project possible."),
    ("🤝", "Machine Learning Community", "For research, tools, and shared knowledge that shaped this work."),
]

ack_cols = st.columns(4)
for idx, (icon, name, desc) in enumerate(ACKNOWLEDGEMENTS):
    with ack_cols[idx]:
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center; font-size:1.6rem;'>{icon}</div>"
                f"<div style='text-align:center; font-weight:600;'>{name}</div>"
                f"<div style='text-align:center; font-size:0.8rem; color:gray;'>{desc}</div>",
                unsafe_allow_html=True,
            )
