"""Reusable, professional sidebar navigation for the GeoSlide dashboard."""

from __future__ import annotations

import inspect
from pathlib import Path

import streamlit as st

NAV_ITEMS = [
    {"key": "dashboard", "title": "Dashboard", "icon": "🏠", "page": "Home.py"},
    {"key": "prediction", "title": "Prediction", "icon": "🔍", "page": "pages/1_🔍_Prediction.py"},
    {"key": "shap", "title": "SHAP Analysis", "icon": "🧠", "page": "pages/2_SHAP_Analysis.py"},
    {"key": "map", "title": "Historical Map", "icon": "🌍", "page": "pages/3_Historical_Map.py"},
    {"key": "analytics", "title": "Dataset Analytics", "icon": "📊", "page": "pages/4_Dataset_Analytics.py"},
    {"key": "about", "title": "About", "icon": "ℹ", "page": "pages/5_About.py"},
]


def _detect_active_page() -> str:
    """Infer the current page from the caller module name."""
    frame = inspect.currentframe()
    try:
        caller = frame.f_back if frame else None
        while caller:
            filename = Path(caller.f_code.co_filename).name
            if filename == "Home.py":
                return "dashboard"
            if filename.startswith("1_"):
                return "prediction"
            if filename.startswith("2_"):
                return "shap"
            if filename.startswith("3_"):
                return "map"
            if filename.startswith("4_"):
                return "analytics"
            if filename.startswith("5_"):
                return "about"
            caller = caller.f_back
    finally:
        del frame

    return "dashboard"


def render_sidebar() -> None:
    """Render the shared branded sidebar navigation for all pages."""
    active_page = _detect_active_page()

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand-card">
                <div class="sidebar-brand-logo">🛰️</div>
                <div>
                    <div class="sidebar-brand-title">GeoSlide AI</div>
                    <div class="sidebar-brand-subtitle">Machine Learning Dashboard</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-nav-list">', unsafe_allow_html=True)
        for item in NAV_ITEMS:
            is_active = item["key"] == active_page
            container_class = "nav-item active" if is_active else "nav-item"
            st.markdown(f"<div class=\"{container_class}\">", unsafe_allow_html=True)
            st.page_link(
                item["page"],
                label=f"{item['icon']} {item['title']}",
                icon=None,
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
        st.caption("Version 1.0")
        st.caption("Built with FastAPI + Streamlit")
        st.markdown("</div>", unsafe_allow_html=True)

