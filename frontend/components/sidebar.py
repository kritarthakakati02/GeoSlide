"""Reusable, professional sidebar navigation for the GeoSlide dashboard.

Visual-only redesign: still renders real `st.page_link` widgets (so
navigation, routing, and page targets are completely untouched) — only
the surrounding markup/CSS and icon set changed. Emoji icons in the
active-page detector and page filenames are internal identifiers, not
UI, and are left as-is since renaming pages would change navigation.

This revision moves branding to a single top-of-sidebar logo block
(the GeoSlide mark), removes the old mid-sidebar brand card and the
OVERVIEW / ANALYZE / EXPLORE / INFO section headers in favor of one
flat nav list, and adds a compact status footer. Every `st.page_link`
still targets the exact same page file / key as before.
"""

from __future__ import annotations

import base64
import inspect
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
LOGO_FILE = ROOT / "assets" / "logo.png"

# Flat nav list — same items, same page targets, same keys, same order
# as the old grouped structure. Only the icon glyphs changed (closest
# Material Symbols equivalents to Lucide House / Crosshair / Brain /
# Globe / BarChart3 / Info, since st.page_link only accepts Material
# Symbol identifiers, not arbitrary icon sets).
NAV_ITEMS = [
    {"key": "dashboard", "title": "Home", "icon": ":material/home:", "page": "Home.py"},
    {"key": "prediction", "title": "Prediction", "icon": ":material/gps_fixed:", "page": "pages/1_🔍_Prediction.py"},
    {"key": "shap", "title": "SHAP Analysis", "icon": ":material/psychology:", "page": "pages/2_SHAP_Analysis.py"},
    {"key": "map", "title": "Historical Map", "icon": ":material/public:", "page": "pages/3_Historical_Map.py"},
    {"key": "analytics", "title": "Dataset Analytics", "icon": ":material/bar_chart:", "page": "pages/4_Dataset_Analytics.py"},
    {"key": "about", "title": "About", "icon": ":material/info:", "page": "pages/5_About.py"},
]

# Self-contained CSS (does not depend on design_system.css tokens, since
# not every page loads that file) so the sidebar looks identical and
# correct regardless of which page renders it.
_SIDEBAR_CSS = """
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #EAF3EE 0%, #DCEBE2 100%) !important;
    border-right: 1px solid rgba(15, 23, 42, 0.12);
    box-shadow: 3px 0 18px rgba(28, 35, 31, 0.05);
    padding: 0.9rem 0.75rem 0.85rem;
}
[data-testid="stSidebar"] > div {
    background: transparent !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 0.1rem;
    display: flex;
    flex-direction: column;
    min-height: 100%;
    background: transparent !important;
}
[data-testid="stSidebar"] hr { display: none; }

/* Safety net: hide Streamlit's built-in auto-generated multipage nav
   (the actual source of the duplicate menu / duplicate Home item).
   The real fix is frontend/.streamlit/config.toml
   ([client] showSidebarNavigation = false); this rule just guards
   against environments where that config isn't picked up. Purely
   cosmetic — it has no effect on routing, since navigation still
   happens through the st.page_link widgets below. */
[data-testid="stSidebarNav"] { display: none !important; }

/* ---- Top brand block ---- */
.sidebar-brand-top {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 1rem 0.5rem 1.3rem;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}
.sidebar-brand-logo-img {
    width: 82px;
    height: 82px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 6px 16px rgba(28, 68, 51, 0.28), 0 1px 3px rgba(15, 23, 42, 0.10);
    background: #FFFFFF;
}
.sidebar-brand-name {
    font-size: 1rem;
    font-weight: 800;
    color: #1C231F;
    letter-spacing: -0.01em;
    margin-top: 0.85rem;
    line-height: 1.2;
}
.sidebar-brand-tagline {
    font-size: 0.7rem;
    font-weight: 500;
    color: #8C8779;
    letter-spacing: 0.02em;
    margin-top: 0.3rem;
    line-height: 1.3;
}

/* ---- Nav items (real st.page_link widgets underneath) ---- */
.sidebar-nav-list {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    margin-top: 0.15rem;
}
.nav-item {
    border-radius: 10px;
    position: relative;
}

.nav-item [data-testid="stPageLink"],
.nav-item a.stPageLink {
    border-radius: 10px !important;
    background: transparent !important;
    transition: background-color 160ms ease, color 160ms ease;
}
.nav-item [data-testid="stPageLink"] > div,
.nav-item a.stPageLink {
    padding: 0.48rem 0.6rem !important;
    background: transparent !important;
}
.nav-item [data-testid="stPageLink"] p,
.nav-item [data-testid="stPageLink"] span {
    color: #4B564F !important;
    font-weight: 700 !important;
    font-size: 0.95rem;
    transition: color 160ms ease;
}
.nav-item [data-testid="stPageLink"] [data-testid="stIconMaterial"] {
    color: #000000 !important;
    font-size: 19px !important;
    transition: color 160ms ease;
}
.nav-item:hover {
    background: rgba(47, 107, 79, 0.16) !important;
}
.nav-item:hover [data-testid="stPageLink"] p,
.nav-item:hover [data-testid="stPageLink"] span {
    color: #2F6B4F !important;
}
.nav-item:hover [data-testid="stPageLink"] [data-testid="stIconMaterial"] {
    color: #000000 !important;
}

.nav-item.active {
    background: linear-gradient(135deg, #2F6B4F 0%, #25553F 100%) !important;
    box-shadow: inset 4px 0 0 rgba(255, 255, 255, 0.9),
                0 8px 22px rgba(28, 68, 51, 0.38), 0 2px 6px rgba(28, 68, 51, 0.24);
}
/* Strip any background Streamlit itself paints on inner wrappers for the
   "current page" indicator, and any lingering hover tint from above, so
   the emerald gradient on .nav-item (the div this file renders and fully
   controls) is always what's visible — never covered by an inner layer. */
.nav-item.active [data-testid="stPageLink"],
.nav-item.active [data-testid="stPageLink"] > div,
.nav-item.active a.stPageLink {
    background: transparent !important;
}
.nav-item.active [data-testid="stPageLink"] p,
.nav-item.active [data-testid="stPageLink"] span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}
.nav-item.active [data-testid="stPageLink"] [data-testid="stIconMaterial"] {
    color: #000000 !important;
}
.nav-item.active:hover {
    background: linear-gradient(135deg, #2F6B4F 0%, #25553F 100%) !important;
}
.nav-item.active:hover [data-testid="stPageLink"] p,
.nav-item.active:hover [data-testid="stPageLink"] span {
    color: #FFFFFF !important;
}
.nav-item.active:hover [data-testid="stPageLink"] [data-testid="stIconMaterial"] {
    color: #000000 !important;
}

/* ---- Footer ---- */
.sidebar-footer {
    margin-top: auto;
    padding: 0.75rem 0.6rem 0.1rem;
    border-top: 1px solid rgba(15, 23, 42, 0.06);
}
.sidebar-status-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.72rem;
    font-weight: 600;
    color: #4B564F;
}
.sidebar-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #2F6B4F;
    box-shadow: 0 0 0 3px rgba(47, 107, 79, 0.15);
    flex-shrink: 0;
}
.sidebar-status-version {
    font-size: 0.68rem;
    color: #ABA595;
    opacity: 0.55;
    margin-top: 0.25rem;
}
"""


@st.cache_data(show_spinner=False)
def _load_logo_base64() -> str:
    """Base64-encode the GeoSlide logo once so it can be embedded inline
    (allows precise circular-crop + shadow styling that `st.image` alone
    cannot give inside a custom-centered layout)."""
    if not LOGO_FILE.exists():
        return ""
    return base64.b64encode(LOGO_FILE.read_bytes()).decode("utf-8")


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
        logo_b64 = _load_logo_base64()
        logo_img_html = (
            f'<img class="sidebar-brand-logo-img" src="data:image/png;base64,{logo_b64}" alt="GeoSlide logo" />'
            if logo_b64
            else ""
        )
        st.markdown(
            f"""
            <div class="sidebar-brand-top">
                {logo_img_html}
                <div class="sidebar-brand-name">GeoSlide AI</div>
                <div class="sidebar-brand-tagline">Machine Learning • Landslide Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-nav-list">', unsafe_allow_html=True)
        for item in NAV_ITEMS:
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
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="sidebar-footer">
                <div class="sidebar-status-row">
                    <span class="sidebar-status-dot"></span>
                    <span>System Online</span>
                </div>
                <div class="sidebar-status-version">Version 1.0</div>
            </div>
            """,
            unsafe_allow_html=True,
        )