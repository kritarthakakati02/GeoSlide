"""
GeoSlide AI - Home Dashboard

Redesigned as a premium AI/SaaS style landing dashboard. This file is
intentionally self-contained: every visual element specific to the new
design (dark theme tokens, hero, KPI cards, workflow timeline, feature
grid, tech badges) lives here rather than in the shared
components/utils modules, so no other page's look, behavior, or
navigation logic is affected.

Nothing backend-, prediction-, SHAP-, map-, or analytics-related is
touched. Navigation still goes through the existing `st.page_link`
mechanism used across the rest of the app.
"""

import streamlit as st

from utils.theme import load_styles
from components.sidebar import render_sidebar

# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="GeoSlide AI",
    page_icon="🌍",
    layout="wide",
)

# Shared base styles (used by every page) - left untouched.
st.markdown(f"<style>{load_styles()}</style>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Home-page-only dark theme overrides
# ------------------------------------------------------------
# Scoped to [data-testid="stAppViewContainer"] (the main content area,
# not the sidebar) and only ever injected while Home.py is the active
# script, so it never bleeds into other pages.
HOME_CSS = """
:root {
    --gs-bg: #0F172A;
    --gs-surface: #131E33;
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
    background: radial-gradient(circle at 15% 0%, #132239 0%, var(--gs-bg) 45%) !important;
}

[data-testid="stAppViewContainer"] .block-container {
    padding: 1.6rem 2.6rem 1.6rem !important;
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
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li,
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
    color: var(--gs-muted) !important;
}

[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--gs-card) !important;
    border: 1px solid var(--gs-border) !important;
    border-radius: var(--gs-radius) !important;
    box-shadow: 0 12px 28px rgba(2, 6, 23, 0.45) !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-4px);
    border-color: rgba(16, 185, 129, 0.45) !important;
    box-shadow: 0 20px 40px rgba(2, 6, 23, 0.55), 0 0 0 1px rgba(16, 185, 129, 0.12) !important;
}

[data-testid="stAppViewContainer"] .stPageLink {
    border-radius: 999px !important;
    background: transparent;
}

[data-testid="stAppViewContainer"] .stPageLink p {
    color: #F8FAFC !important;
    font-weight: 600;
    text-align: center;
}

/* Primary CTA (first hero button) */
.gs-cta-primary [data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(90deg, var(--gs-primary) 0%, var(--gs-accent) 100%) !important;
    border: none !important;
}
.gs-cta-primary [data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 16px 32px rgba(16, 185, 129, 0.35) !important;
    border: none !important;
}
.gs-cta-primary .stPageLink p { color: #ffffff !important; }

.gs-eyebrow {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--gs-primary);
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 999px;
    padding: 5px 14px;
    margin-bottom: 14px;
}

.gs-hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.15;
    margin: 4px 0 6px 0;
}

.gs-hero-subtitle {
    font-size: 1.05rem;
    font-weight: 500;
    color: var(--gs-accent);
    margin-bottom: 12px;
}

.gs-hero-desc {
    font-size: 0.98rem;
    color: var(--gs-muted);
    line-height: 1.55;
    max-width: 520px;
    margin-bottom: 6px;
}

.gs-kpi-icon {
    font-size: 1.3rem;
    margin-bottom: 6px;
}
.gs-kpi-label {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gs-muted);
}
.gs-kpi-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-top: 2px;
}

.gs-section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 6px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.gs-feature-title {
    font-size: 1.02rem;
    font-weight: 700;
    color: #F8FAFC;
    margin: 6px 0 4px 0;
}
.gs-feature-desc {
    font-size: 0.85rem;
    color: var(--gs-muted);
    line-height: 1.45;
    min-height: 40px;
}

.gs-workflow-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 4px;
    margin-bottom: 4px;
}
.gs-workflow-step {
    flex: 1;
    background: var(--gs-card);
    border: 1px solid var(--gs-border);
    border-radius: var(--gs-radius);
    padding: 14px 10px;
    text-align: center;
    transition: transform 0.18s ease, border-color 0.18s ease;
}
.gs-workflow-step:hover {
    transform: translateY(-3px);
    border-color: rgba(59, 130, 246, 0.5);
}
.gs-workflow-icon { font-size: 1.3rem; }
.gs-workflow-label {
    font-size: 0.82rem;
    font-weight: 700;
    color: #E2E8F0;
    margin-top: 4px;
}
.gs-workflow-arrow {
    flex: 0 0 auto;
    color: var(--gs-primary);
    font-size: 1.3rem;
    font-weight: 700;
    opacity: 0.7;
}

.gs-badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 4px;
}
.gs-badge {
    background: var(--gs-card);
    border: 1px solid var(--gs-border);
    color: #E2E8F0;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 7px 16px;
    border-radius: 999px;
}

.gs-illustration-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 260px;
}
"""

st.markdown(f"<style>{HOME_CSS}</style>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Sidebar (shared, unmodified)
# ------------------------------------------------------------
render_sidebar()


# ============================================================
# Small local helpers (Home-page only, not shared components)
# ============================================================

def _hero_illustration() -> str:
    """Abstract gradient/network SVG - no external images."""
    return """
    <svg viewBox="0 0 420 340" xmlns="http://www.w3.org/2000/svg" width="100%" height="320">
        <defs>
            <linearGradient id="gsGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#10B981" stop-opacity="0.35"/>
                <stop offset="100%" stop-color="#3B82F6" stop-opacity="0.05"/>
            </linearGradient>
            <linearGradient id="gsRidge" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#10B981"/>
                <stop offset="100%" stop-color="#3B82F6"/>
            </linearGradient>
        </defs>
        <circle cx="210" cy="170" r="165" fill="url(#gsGlow)"/>
        <polygon points="20,260 110,140 160,200 230,90 320,220 400,190 400,300 20,300"
                 fill="none" stroke="url(#gsRidge)" stroke-width="2" opacity="0.55"/>
        <polygon points="20,280 130,190 190,230 260,150 340,250 400,230 400,300 20,300"
                 fill="none" stroke="#3B82F6" stroke-width="1.4" opacity="0.35"/>
        <g stroke="#10B981" stroke-width="1" opacity="0.55">
            <line x1="90" y1="120" x2="180" y2="70"/>
            <line x1="180" y1="70" x2="280" y2="110"/>
            <line x1="280" y1="110" x2="340" y2="60"/>
            <line x1="180" y1="70" x2="220" y2="150"/>
            <line x1="90" y1="120" x2="140" y2="190"/>
            <line x1="220" y1="150" x2="300" y2="170"/>
        </g>
        <g fill="#10B981">
            <circle cx="90" cy="120" r="5"/>
            <circle cx="180" cy="70" r="6"/>
            <circle cx="280" cy="110" r="5"/>
            <circle cx="340" cy="60" r="4"/>
        </g>
        <g fill="#3B82F6">
            <circle cx="220" cy="150" r="6"/>
            <circle cx="140" cy="190" r="4"/>
            <circle cx="300" cy="170" r="5"/>
        </g>
    </svg>
    """


def _kpi_card(icon: str, label: str, value: str) -> None:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="gs-kpi-icon">{icon}</div>
            <div class="gs-kpi-label">{label}</div>
            <div class="gs-kpi-value">{value}</div>
            """,
            unsafe_allow_html=True,
        )


def _workflow_html(steps) -> str:
    parts = ['<div class="gs-workflow-row">']
    for i, (icon, label) in enumerate(steps):
        parts.append(
            f'<div class="gs-workflow-step">'
            f'<div class="gs-workflow-icon">{icon}</div>'
            f'<div class="gs-workflow-label">{label}</div>'
            f'</div>'
        )
        if i < len(steps) - 1:
            parts.append('<div class="gs-workflow-arrow">&#8594;</div>')
    parts.append("</div>")
    return "".join(parts)


def _feature_card(icon: str, title: str, desc: str, page: str) -> None:
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:1.5rem;">{icon}</div>
            <div class="gs-feature-title">{title}</div>
            <div class="gs-feature-desc">{desc}</div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label="Open →", icon=None, use_container_width=True)


def _badge_row(items) -> None:
    spans = "".join(f'<span class="gs-badge">{i}</span>' for i in items)
    st.markdown(f'<div class="gs-badge-row">{spans}</div>', unsafe_allow_html=True)


# ============================================================
# SECTION 1 — HERO
# ============================================================

left, right = st.columns([1.3, 1], gap="large")

with left:
    st.markdown('<div class="gs-eyebrow">MACHINE LEARNING · EXPLAINABLE AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="gs-hero-title">🌍 GeoSlide AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gs-hero-subtitle">Machine Learning-Based Landslide Risk Assessment System</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="gs-hero-desc">
        Predicts landslide risk from environmental and geological data, with
        SHAP-driven explainability and NASA historical event visualization.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    cta1, cta2, cta3 = st.columns(3, gap="small")
    with cta1:
        st.markdown('<div class="gs-cta-primary">', unsafe_allow_html=True)
        with st.container(border=True):
            st.page_link(
                "pages/1_🔍_Prediction.py",
                label="🔍 Start Prediction",
                icon=None,
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    with cta2:
        with st.container(border=True):
            st.page_link(
                "pages/4_Dataset_Analytics.py",
                label="📊 Explore Dataset",
                icon=None,
                use_container_width=True,
            )
    with cta3:
        with st.container(border=True):
            st.page_link(
                "pages/3_Historical_Map.py",
                label="🗺️ Historical Map",
                icon=None,
                use_container_width=True,
            )

with right:
    st.markdown(
        f'<div class="gs-illustration-wrap">{_hero_illustration()}</div>',
        unsafe_allow_html=True,
    )

st.write("")

# ============================================================
# SECTION 2 — KPI ROW
# ============================================================

k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1:
    _kpi_card("🎯", "Accuracy", "97.82%")
with k2:
    _kpi_card("🗃️", "Dataset Size", "9,864")
with k3:
    _kpi_card("📈", "Features", "34")
with k4:
    _kpi_card("🤖", "Algorithm", "KNN")

st.write("")

# ============================================================
# SECTION 3 — WORKFLOW
# ============================================================

st.markdown('<div class="gs-section-title">⚙️ Workflow</div>', unsafe_allow_html=True)
st.markdown(
    _workflow_html(
        [
            ("🗂️", "Dataset"),
            ("⚙️", "Preprocessing"),
            ("🔮", "Prediction"),
            ("🧠", "Explainability"),
            ("📊", "Visualization"),
        ]
    ),
    unsafe_allow_html=True,
)

st.write("")

# ============================================================
# SECTION 4 — CORE FEATURES (2x2)
# ============================================================

st.markdown('<div class="gs-section-title">🚀 Core Features</div>', unsafe_allow_html=True)

f1, f2 = st.columns(2, gap="medium")
with f1:
    _feature_card(
        "🔍", "Prediction",
        "Estimate landslide susceptibility from live environmental "
        "and geological parameters.",
        "pages/1_🔍_Prediction.py",
    )
with f2:
    _feature_card(
        "🧠", "SHAP Explainability",
        "See exactly which features drove each risk prediction, "
        "feature by feature.",
        "pages/2_SHAP_Analysis.py",
    )

f3, f4 = st.columns(2, gap="medium")
with f3:
    _feature_card(
        "🌍", "Historical Map",
        "Explore NASA's Global Landslide Catalog on an interactive "
        "world map.",
        "pages/3_Historical_Map.py",
    )
with f4:
    _feature_card(
        "📊", "Dataset Analytics",
        "Inspect feature distributions, correlations and dataset "
        "statistics.",
        "pages/4_Dataset_Analytics.py",
    )

st.write("")

# ============================================================
# SECTION 5 — TECHNOLOGY STACK
# ============================================================

st.markdown('<div class="gs-section-title">🧩 Technology Stack</div>', unsafe_allow_html=True)
_badge_row(
    ["Python", "FastAPI", "Streamlit", "Scikit-learn", "SHAP", "Plotly", "Pandas", "NumPy"]
)
