"""Reusable, professional sidebar navigation for the GeoSlide dashboard.

Visual-only redesign: still renders real `st.page_link` widgets (so
navigation, routing, and page targets are completely untouched) — only
the surrounding markup/CSS and icon set changed. Emoji icons in the
active-page detector and page filenames are internal identifiers, not
UI, and are left as-is since renaming pages would change navigation.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import streamlit as st

# Each item still points at the exact same page file as before — only
# the display icon (now a Material Symbol rendered natively by
# st.page_link, no emoji) and grouping label changed.
NAV_GROUPS = [
    {
        "label": "Overview",
        "items": [
            {"key": "dashboard", "title": "Dashboard", "icon": ":material/home:", "page": "Home.py"},
        ],
    },
    {
        "label": "Analyze",
        "items": [
            {"key": "prediction", "title": "Prediction", "icon": ":material/search:", "page": "pages/1_🔍_Prediction.py"},
            {"key": "shap", "title": "SHAP Analysis", "icon": ":material/psychology:", "page": "pages/2_SHAP_Analysis.py"},
        ],
    },
    {
        "label": "Explore",
        "items": [
            {"key": "map", "title": "Historical Map", "icon": ":material/public:", "page": "pages/3_Historical_Map.py"},
            {"key": "analytics", "title": "Dataset Analytics", "icon": ":material/bar_chart:", "page": "pages/4_Dataset_Analytics.py"},
        ],
    },
    {
        "label": "Info",
        "items": [
            {"key": "about", "title": "About", "icon": ":material/info:", "page": "pages/5_About.py"},
        ],
    },
]

# Self-contained CSS (does not depend on design_system.css tokens, since
# not every page loads that file) so the sidebar looks identical and
# correct regardless of which page renders it.
_SIDEBAR_CSS = """
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid rgba(15, 23, 42, 0.06);
    box-shadow: 3px 0 18px rgba(28, 35, 31, 0.05);
    padding: 1.1rem 0.85rem 1rem;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 0.2rem;
    display: flex;
    flex-direction: column;
    min-height: 100%;
}
[data-testid="stSidebar"] hr { display: none; }

/* ---- Brand header ---- */
.sidebar-brand-card {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    background: #F7F5F2;
    border: 1px solid rgba(15, 23, 42, 0.05);
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    border-radius: 14px;
    padding: 0.8rem 0.85rem;
    margin-bottom: 1.35rem;
}
.sidebar-brand-logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.3rem;
    height: 2.3rem;
    border-radius: 10px;
    flex-shrink: 0;
    background: linear-gradient(135deg, #2F6B4F 0%, #1C4433 100%);
    color: #FFFFFF;
    box-shadow: 0 4px 10px rgba(47, 107, 79, 0.28);
}
.sidebar-brand-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1C231F;
    line-height: 1.25;
    letter-spacing: -0.01em;
}
.sidebar-brand-subtitle {
    font-size: 0.74rem;
    color: #8C8779;
    line-height: 1.3;
    margin-top: 1px;
}

/* ---- Section grouping ---- */
.sidebar-group { margin-bottom: 0.35rem; }
.sidebar-group-label {
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #B5AE9F;
    padding: 0 0.65rem;
    margin: 0.95rem 0 0.35rem;
}

/* ---- Nav items (real st.page_link widgets underneath) ---- */
.sidebar-nav-list {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}
.nav-item { border-radius: 10px; }

.nav-item [data-testid="stPageLink"],
.nav-item a.stPageLink {
    border-radius: 10px !important;
    transition: background-color 150ms cubic-bezier(0.4,0,0.2,1),
                transform 150ms cubic-bezier(0.4,0,0.2,1),
                color 150ms cubic-bezier(0.4,0,0.2,1);
}
.nav-item [data-testid="stPageLink"] > div,
.nav-item a.stPageLink {
    padding: 0.5rem 0.65rem !important;
}
.nav-item [data-testid="stPageLink"] p,
.nav-item [data-testid="stPageLink"] span,
.nav-item [data-testid="stPageLink"] svg {
    color: #4B564F !important;
    font-weight: 500 !important;
    font-size: 0.88rem;
}
.nav-item [data-testid="stPageLink"]:hover,
.nav-item a.stPageLink:hover {
    background: #F1EEE8 !important;
    transform: translateX(3px);
}
.nav-item.active [data-testid="stPageLink"],
.nav-item.active a.stPageLink {
    background: #EBF3EE !important;
}
.nav-item.active [data-testid="stPageLink"] p,
.nav-item.active [data-testid="stPageLink"] span,
.nav-item.active [data-testid="stPageLink"] svg {
    color: #2F6B4F !important;
    font-weight: 600 !important;
}
.nav-item.active [data-testid="stPageLink"]:hover,
.nav-item.active a.stPageLink:hover {
    transform: none;
}

/* ---- Footer ---- */
.sidebar-footer {
    margin-top: auto;
    padding: 0.9rem 0.65rem 0.1rem;
    border-top: 1px solid rgba(15, 23, 42, 0.06);
}
.sidebar-footer [data-testid="stCaptionContainer"] p {
    font-size: 0.71rem !important;
    color: #ABA595 !important;
    line-height: 1.55 !important;
    margin: 0 !important;
}
"""


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

    st.markdown(f"<style>{_SIDEBAR_CSS}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand-card">
                <div class="sidebar-brand-logo">
                    <svg width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round"
                         stroke-linejoin="round">
                        <path d="m8 3 4 8 5-5 5 15H2L8 3z"/>
                    </svg>
                </div>
                <div>
                    <div class="sidebar-brand-title">GeoSlide AI</div>
                    <div class="sidebar-brand-subtitle">Machine Learning Dashboard</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for group in NAV_GROUPS:
            st.markdown('<div class="sidebar-group">', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-group-label">{group["label"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-nav-list">', unsafe_allow_html=True)
            for item in group["items"]:
                is_active = item["key"] == active_page
                container_class = "nav-item active" if is_active else "nav-item"
                st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
                st.page_link(
                    item["page"],
                    label=item["title"],
                    icon=item["icon"],
                    use_container_width=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
        st.caption("Version 1.0")
        st.caption("Built with FastAPI + Streamlit")
        st.markdown("</div>", unsafe_allow_html=True)