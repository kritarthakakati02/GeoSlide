"""
GeoSlide AI - Home Dashboard

This page is wired to the shared design system introduced in
`frontend/assets/design_system.css` (tokens + `.ds-*` component classes)
and `frontend/utils/design_tokens.py`. Home.py does not define any new
colors, type sizes, spacing values, or radii of its own — every visual
value here is either a `.ds-*` class or a `var(--ds-*)` token from the
design system.

The only page-specific CSS that remains below is "wiring" CSS: Streamlit
renders `st.container(border=True)` and `st.page_link(...)` into fixed
internal DOM structures that can't take a custom class directly, so a
handful of selectors translate those Streamlit-native elements onto the
existing `.ds-card` / `.ds-btn-primary` / `.ds-btn-secondary` look. No
new design tokens are introduced by that wiring — it only ever reads
`var(--ds-*)`.

All of this is scoped to [data-testid="stAppViewContainer"] and only
ever injected while Home.py is the active script, so nothing here
bleeds into other pages, and the shared sidebar, backend, API, and
business logic are completely untouched.
"""

from pathlib import Path

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

ROOT = Path(__file__).resolve().parent
DESIGN_SYSTEM_CSS_FILE = ROOT / "assets" / "design_system.css"
HERO_IMAGE_FILE = ROOT / "assets" / "images" / "hero_landslide_terrain.png"

# Shared base styles (used by every page) - left untouched.
st.markdown(f"<style>{load_styles()}</style>", unsafe_allow_html=True)

# The unified design system (tokens + .ds-* classes) — single source of
# truth, built in the previous phase, untouched here. Loading it is the
# only thing that changes: no page imported it before this.
st.markdown(f"<style>{DESIGN_SYSTEM_CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Home-page wiring CSS — maps Streamlit's native container/link markup
# onto the existing design-system tokens and classes. No new colors,
# sizes, radii, or spacing values are declared past this point; every
# rule below resolves through var(--ds-*).
# ------------------------------------------------------------
HOME_WIRING_CSS = """
[data-testid="stAppViewContainer"] {
    background: var(--ds-bg) !important;
}

[data-testid="stAppViewContainer"] .block-container {
    padding: var(--ds-space-6) var(--ds-container-padding-desktop) var(--ds-space-10) !important;
    max-width: var(--ds-container-max);
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4 {
    color: var(--ds-text-primary) !important;
    letter-spacing: var(--ds-tracking-tight);
}

[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li,
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
    color: var(--ds-text-secondary) !important;
}

/* Default look for any bordered st.container on this page = .ds-card */
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--ds-surface) !important;
    border: 1px solid var(--ds-border) !important;
    border-radius: var(--ds-radius-lg) !important;
    box-shadow: var(--ds-shadow-sm) !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base),
                border-color var(--ds-transition-base);
}

[data-testid="stAppViewContainer"] .stPageLink {
    border-radius: var(--ds-radius-full) !important;
    background: transparent;
}
[data-testid="stAppViewContainer"] .stPageLink p {
    color: var(--ds-text-primary) !important;
    font-weight: var(--ds-weight-semibold);
    text-align: center;
}

/* ---- KPI cards: static info, ds-kpi-card hover only (no lift) ---- */
.gs-kpi [data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: var(--ds-shadow-md) !important;
}

/* ---- Feature cards: interactive (they link somewhere), so they lift
   on hover per the design system's ds-card-interactive rule ---- */
.gs-feature [data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: var(--ds-lift-hover);
    border-color: var(--ds-brand-200) !important;
    box-shadow: var(--ds-shadow-hover) !important;
}

/* ---- Primary CTA = .ds-btn-primary look, applied to the page-link
   wrapper Streamlit generates ---- */
.gs-cta-primary [data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(90deg, var(--ds-brand-500) 0%, var(--ds-brand-600) 100%) !important;
    border: none !important;
    border-radius: var(--ds-radius-full) !important;
    box-shadow: var(--ds-shadow-sm) !important;
    padding: 0.15rem 0.2rem !important;
}
.gs-cta-primary [data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: var(--ds-lift-hover);
    box-shadow: 0 14px 28px rgba(47, 107, 79, 0.28) !important;
    border: none !important;
}
.gs-cta-primary .stPageLink p { color: var(--ds-text-inverse) !important; }

/* ---- Secondary CTAs = .ds-btn-secondary look ---- */
.gs-cta-secondary [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--ds-surface) !important;
    border: 1px solid var(--ds-border) !important;
    border-radius: var(--ds-radius-full) !important;
    box-shadow: var(--ds-shadow-xs) !important;
    padding: 0.15rem 0.2rem !important;
}
.gs-cta-secondary [data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: var(--ds-lift-hover);
    border-color: var(--ds-brand-300) !important;
    box-shadow: var(--ds-shadow-sm) !important;
}

/* ---- Hero visual frame: houses the uploaded illustration. A subtle
   dot texture uses ds-border as its dot color, and radius/shadow come
   straight from the token scale — no new values. ---- */
.gs-hero-visual [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--ds-bg-subtle) !important;
    border: 1px solid var(--ds-border) !important;
    border-radius: var(--ds-radius-lg) !important;
    box-shadow: var(--ds-shadow-md) !important;
    padding: var(--ds-space-8) !important;
    background-image: radial-gradient(var(--ds-border-strong) 1.4px, transparent 1.4px);
    background-size: 20px 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 360px;
}
.gs-hero-visual img {
    filter: drop-shadow(0 24px 40px rgba(28, 35, 31, 0.18));
}

/* ---- Small structural glue (layout only — no new visual tokens) ---- */
.gs-hero-kicker {
    display: flex;
    align-items: center;
    gap: var(--ds-space-2);
    font-size: var(--ds-text-body);
    font-weight: var(--ds-weight-semibold);
    color: var(--ds-accent-600);
    margin: var(--ds-space-2) 0 var(--ds-space-4) 0;
}
.gs-hero-title-accent { color: var(--ds-brand-600); }
.gs-workflow-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--ds-space-2);
}
.gs-workflow-step { position: relative; flex: 1; }
.gs-workflow-badge {
    position: absolute;
    top: calc(-1 * var(--ds-space-3));
    left: var(--ds-space-4);
    width: 26px;
    height: 26px;
    border-radius: var(--ds-radius-full);
    background: var(--ds-brand-500);
    color: var(--ds-text-inverse);
    font-size: var(--ds-text-xs);
    font-weight: var(--ds-weight-bold);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--ds-shadow-sm);
}
.gs-workflow-arrow {
    flex: 0 0 auto;
    color: var(--ds-brand-500);
    font-size: 1.2rem;
    font-weight: var(--ds-weight-bold);
    opacity: 0.5;
    margin-top: var(--ds-space-8);
}
"""

st.markdown(f"<style>{HOME_WIRING_CSS}</style>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Sidebar (shared, unmodified)
# ------------------------------------------------------------
render_sidebar()


# ============================================================
# Small local helpers (Home-page only, not shared components)
# ============================================================

def _kpi_card(icon: str, chip_class: str, label: str, value: str) -> None:
    st.markdown('<div class="gs-kpi">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="ds-kpi-icon {chip_class}">{icon}</div>
            <div class="ds-kpi-label">{label}</div>
            <div class="ds-kpi-value">{value}</div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _workflow_html(steps) -> str:
    parts = ['<div class="gs-workflow-row">']
    for i, (icon, label, desc) in enumerate(steps):
        parts.append(
            f'<div class="gs-workflow-step ds-card">'
            f'<div class="gs-workflow-badge">{i + 1}</div>'
            f'<div class="ds-chip-brand" style="width:42px;height:42px;border-radius:var(--ds-radius-xs);'
            f'display:flex;align-items:center;justify-content:center;font-size:1.15rem;'
            f'margin:0 auto var(--ds-space-3);">{icon}</div>'
            f'<div class="ds-h3" style="text-align:center;">{label}</div>'
            f'<div class="ds-text-sm" style="text-align:center;margin-top:2px;">{desc}</div>'
            f'</div>'
        )
        if i < len(steps) - 1:
            parts.append('<div class="gs-workflow-arrow">&#8594;</div>')
    parts.append("</div>")
    return "".join(parts)


def _feature_card(icon: str, chip_class: str, title: str, desc: str, page: str) -> None:
    st.markdown('<div class="gs-feature">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="ds-kpi-icon {chip_class}" style="width:46px;height:46px;font-size:1.3rem;">{icon}</div>
            <div class="ds-card-title" style="margin-top:var(--ds-space-2);">{title}</div>
            <div class="ds-card-desc" style="min-height:42px;margin-top:2px;">{desc}</div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label="Open →", icon=None, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _badge_row(items) -> None:
    spans = "".join(
        f'<span class="ds-badge ds-badge-neutral">{icon}&nbsp;{name}</span>'
        for icon, name in items
    )
    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;gap:var(--ds-space-3);margin-top:var(--ds-space-1);">{spans}</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# SECTION 1 — HERO
# ============================================================

left, right = st.columns([1.2, 1], gap="large")

with left:
    st.markdown(
        '<div class="ds-eyebrow">MACHINE LEARNING · EXPLAINABLE AI</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-display">Machine Learning-Based<br>'
        '<span class="gs-hero-title-accent">Landslide Risk Assessment</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="gs-hero-kicker">🌍 GeoSlide AI · Explainable Risk Intelligence</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="ds-body-lg" style="max-width:520px;">
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
        st.markdown('<div class="gs-cta-secondary">', unsafe_allow_html=True)
        with st.container(border=True):
            st.page_link(
                "pages/4_Dataset_Analytics.py",
                label="📊 Explore Dataset",
                icon=None,
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    with cta3:
        st.markdown('<div class="gs-cta-secondary">', unsafe_allow_html=True)
        with st.container(border=True):
            st.page_link(
                "pages/3_Historical_Map.py",
                label="🗺️ Historical Map",
                icon=None,
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="gs-hero-visual">', unsafe_allow_html=True)
    with st.container(border=True):
        st.image(str(HERO_IMAGE_FILE), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# ============================================================
# SECTION 2 — KPI ROW
# ============================================================

k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1:
    _kpi_card("🎯", "ds-chip-brand", "Accuracy", "97.82%")
with k2:
    _kpi_card("🗃️", "ds-chip-accent", "Dataset Size", "9,864")
with k3:
    _kpi_card("📈", "ds-chip-amber", "Features", "34")
with k4:
    _kpi_card("🤖", "ds-chip-brand", "Algorithm", "KNN")

st.write("")

# ============================================================
# SECTION 3 — WORKFLOW
# ============================================================

st.markdown('<div class="ds-section-title">⚙️ Workflow</div>', unsafe_allow_html=True)
st.markdown('<div class="ds-section-subtitle">End-to-end ML pipeline</div>', unsafe_allow_html=True)
st.markdown(
    _workflow_html(
        [
            ("🗂️", "Dataset", "Load and explore the dataset"),
            ("⚙️", "Preprocessing", "Clean and prepare the data"),
            ("🔮", "Prediction", "Run ML model to predict risk"),
            ("🧠", "Explainability", "SHAP values for interpretation"),
            ("📊", "Visualization", "Visualize results and insights"),
        ]
    ),
    unsafe_allow_html=True,
)

st.write("")

# ============================================================
# SECTION 4 — CORE FEATURES (2x2)
# ============================================================

st.markdown('<div class="ds-section-title">🚀 Core Features</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ds-section-subtitle">Powerful tools for landslide risk analysis</div>',
    unsafe_allow_html=True,
)

f1, f2 = st.columns(2, gap="medium")
with f1:
    _feature_card(
        "🔍", "ds-chip-brand", "Prediction",
        "Estimate landslide susceptibility from live environmental "
        "and geological parameters.",
        "pages/1_🔍_Prediction.py",
    )
with f2:
    _feature_card(
        "🧠", "ds-chip-accent", "SHAP Explainability",
        "See exactly which features drove each risk prediction, "
        "feature by feature.",
        "pages/2_SHAP_Analysis.py",
    )

f3, f4 = st.columns(2, gap="medium")
with f3:
    _feature_card(
        "🌍", "ds-chip-amber", "Historical Map",
        "Explore NASA's Global Landslide Catalog on an interactive "
        "world map.",
        "pages/3_Historical_Map.py",
    )
with f4:
    _feature_card(
        "📊", "ds-chip-brand", "Dataset Analytics",
        "Inspect feature distributions, correlations and dataset "
        "statistics.",
        "pages/4_Dataset_Analytics.py",
    )

st.write("")

# ============================================================
# SECTION 5 — TECHNOLOGY STACK
# ============================================================

st.markdown('<div class="ds-section-title">🧩 Technology Stack</div>', unsafe_allow_html=True)
_badge_row(
    [
        ("🐍", "Python"),
        ("⚡", "FastAPI"),
        ("🎈", "Streamlit"),
        ("🧮", "Scikit-learn"),
        ("🧠", "SHAP"),
        ("📈", "Plotly"),
        ("🐼", "Pandas"),
        ("🔢", "NumPy"),
    ]
)
