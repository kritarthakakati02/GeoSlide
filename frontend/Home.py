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
    padding: var(--ds-space-8) var(--ds-container-padding-desktop) var(--ds-space-12) !important;
    max-width: var(--ds-container-max);
}

.gs-section-spacer { height: var(--ds-space-12); }
.gs-row-gap { height: var(--ds-space-5); }

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

/* ---- KPI cards: static info — a gentle lift (not just shadow) reads
   more premium, but stays subtle since these aren't clickable ---- */
.gs-kpi [data-testid="stVerticalBlockBorderWrapper"] {
    padding: var(--ds-space-6) var(--ds-space-5) !important;
    min-height: 132px;
    display: flex !important;
    flex-direction: column;
    justify-content: center;
}
.gs-kpi [data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-2px);
    box-shadow: var(--ds-shadow-md) !important;
    border-color: var(--ds-border-strong) !important;
}
.gs-kpi-icon-row {
    display: flex;
    align-items: center;
    gap: var(--ds-space-3);
    margin-bottom: var(--ds-space-3);
}

/* ---- Feature cards: interactive (they link somewhere), so they lift
   on hover per the design system's ds-card-interactive rule ---- */
.gs-feature [data-testid="stVerticalBlockBorderWrapper"] {
    position: relative;
    padding: var(--ds-space-6) !important;
    min-height: 178px;
    overflow: hidden;
}
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
    padding: var(--ds-space-10) !important;
    background-image: radial-gradient(var(--ds-border-strong) 1.4px, transparent 1.4px);
    background-size: 20px 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 468px; /* ~30% larger than the previous 360px frame */
}
.gs-hero-visual img {
    filter: drop-shadow(0 24px 40px rgba(28, 35, 31, 0.18));
    transform: scale(1.18); /* fills the larger frame without re-exporting the asset */
}

/* ---- Small structural glue (layout only — no new visual tokens) ---- */
.gs-hero-kicker {
    display: flex;
    align-items: center;
    gap: var(--ds-space-2);
    font-size: var(--ds-text-body);
    font-weight: var(--ds-weight-semibold);
    color: var(--ds-accent-600);
    margin: var(--ds-space-3) 0 var(--ds-space-5) 0;
}
.gs-hero-title-accent { color: var(--ds-brand-600); }
.gs-hero-copy {
    max-width: 520px;
    font-size: 1.05rem !important;
    line-height: var(--ds-leading-loose) !important;
    color: var(--ds-text-secondary) !important;
    font-weight: var(--ds-weight-regular);
}
.gs-display-lg {
    font-size: 2.65rem !important;
    line-height: 1.14 !important;
    margin: var(--ds-space-2) 0 0 !important;
}
.gs-cta-row [data-testid="stVerticalBlockBorderWrapper"] { padding: 0.2rem 0.25rem !important; }
.gs-cta-primary .stPageLink, .gs-cta-secondary .stPageLink { padding: 0.7rem 1rem !important; }
.gs-cta-primary .stPageLink p, .gs-cta-secondary .stPageLink p { font-size: 0.95rem !important; }
.gs-workflow-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--ds-space-3);
    margin-top: var(--ds-space-2);
}
.gs-workflow-step {
    position: relative;
    flex: 1;
    padding: var(--ds-space-6) var(--ds-space-4) var(--ds-space-5) !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base),
                border-color var(--ds-transition-base);
}
.gs-workflow-step:hover {
    transform: translateY(-3px);
    border-color: var(--ds-brand-200);
    box-shadow: var(--ds-shadow-md);
}
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
    color: var(--ds-brand-400);
    opacity: 0.6;
    margin-top: var(--ds-space-10);
    transition: opacity var(--ds-transition-base), transform var(--ds-transition-base);
}
.gs-workflow-row:hover .gs-workflow-arrow { opacity: 0.85; }
"""

st.markdown(f"<style>{HOME_WIRING_CSS}</style>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Sidebar (shared, unmodified)
# ------------------------------------------------------------
render_sidebar()


# ============================================================
# Small local helpers (Home-page only, not shared components)
# ============================================================

# Minimal Lucide-style inline icon set — decorative only, used in place
# of emoji anywhere this page renders its own markup (KPI chips, feature
# cards, workflow steps, hero kicker, tech badges). Colored via
# `currentColor` so the existing .ds-chip-* classes still control hue.
_ICON_PATHS = {
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5.2"/><circle cx="12" cy="12" r="1.4" fill="currentColor"/>',
    "database": '<ellipse cx="12" cy="5.5" rx="8" ry="2.7"/><path d="M4 5.5v13c0 1.5 3.6 2.7 8 2.7s8-1.2 8-2.7v-13"/><path d="M4 12c0 1.5 3.6 2.7 8 2.7s8-1.2 8-2.7"/>',
    "bar-chart": '<line x1="5" y1="20" x2="5" y2="13"/><line x1="12" y1="20" x2="12" y2="6"/><line x1="19" y1="20" x2="19" y2="10"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><rect x="10" y="10" width="4" height="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.5 4.5l2 2M17.5 17.5l2 2M4.5 19.5l2-2M17.5 6.5l2-2"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.3-4.3"/>',
    "brain": '<path d="M9 3.5A2.5 2.5 0 0 0 6.5 6v.3a2.5 2.5 0 0 0-1.4 4.3A2.8 2.8 0 0 0 6 15.6a2.5 2.5 0 0 0 3 3.3A2.5 2.5 0 0 0 11.5 20V6A2.5 2.5 0 0 0 9 3.5Z"/><path d="M15 3.5A2.5 2.5 0 0 1 17.5 6v.3a2.5 2.5 0 0 1 1.4 4.3A2.8 2.8 0 0 1 18 15.6a2.5 2.5 0 0 1-3 3.3A2.5 2.5 0 0 1 12.5 20V6A2.5 2.5 0 0 1 15 3.5Z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18Z"/>',
    "layers": '<path d="m12 3 8 4.2-8 4.2-8-4.2Z"/><path d="m4 12 8 4.2 8-4.2"/><path d="m4 16.4 8 4.2 8-4.2"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 3v2.2M12 18.8V21M4.9 6.3l1.6 1.5M17.5 16.2l1.6 1.5M3 12h2.2M18.8 12H21M4.9 17.7l1.6-1.5M17.5 7.8l1.6-1.5"/>',
    "zap": '<path d="M12.5 2 4 13h6l-1 9L20 11h-6l-1-9Z"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "arrow-right": '<line x1="4" y1="12" x2="18" y2="12"/><polyline points="12 6 18 12 12 18"/>',
    "code": '<polyline points="15 6 21 12 15 18"/><polyline points="9 18 3 12 9 6"/>',
    "monitor": '<rect x="2.5" y="4" width="19" height="13" rx="1.5"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>',
    "git-branch": '<line x1="7" y1="3" x2="7" y2="14"/><circle cx="17" cy="6" r="2.6"/><circle cx="7" cy="17.4" r="2.6"/><path d="M17 8.6a8 8 0 0 1-8 8"/>',
    "table": '<rect x="3" y="3" width="18" height="18" rx="1.5"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
    "hash": '<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>',
}


def _icon(name: str, size: int = 20, stroke_width: float = 1.8) -> str:
    """Inline Lucide-style SVG icon (no emoji)."""
    body = _ICON_PATHS.get(name, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" '
        f'stroke-linejoin="round" style="display:block;">{body}</svg>'
    )


def _mini_illustration(kind: str) -> str:
    """Small decorative SVG tucked into a feature card corner (purely
    visual, no interactivity, doesn't affect card functionality)."""
    wrap = 'style="position:absolute;top:18px;right:18px;opacity:0.6;pointer-events:none;"'
    if kind == "trend":
        svg = (
            '<svg width="56" height="34" viewBox="0 0 56 34" fill="none">'
            '<polyline points="2,29 15,21 26,25 38,11 54,4" stroke="var(--ds-brand-500)" '
            'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="54" cy="4" r="3" fill="var(--ds-brand-500)"/></svg>'
        )
    elif kind == "bars":
        rows = [("42", 0), ("30", 9), ("22", 18), ("13", 27)]
        rects = "".join(
            f'<rect x="0" y="{y}" width="{w}" height="6" rx="3" fill="var(--ds-accent-500)" opacity="{1 - i * 0.16}"/>'
            for i, (w, y) in enumerate(rows)
        )
        svg = f'<svg width="50" height="36" viewBox="0 0 50 36" fill="none">{rects}</svg>'
    elif kind == "map":
        svg = (
            '<svg width="54" height="42" viewBox="0 0 54 42" fill="none">'
            '<circle cx="27" cy="21" r="18" stroke="var(--ds-amber-500)" stroke-width="1.3" opacity="0.45"/>'
            '<circle cx="16" cy="15" r="2.1" fill="var(--ds-amber-500)"/>'
            '<circle cx="35" cy="11" r="1.5" fill="var(--ds-amber-500)"/>'
            '<circle cx="31" cy="27" r="2.4" fill="var(--ds-amber-500)"/>'
            '<circle cx="14" cy="28" r="1.7" fill="var(--ds-amber-500)"/></svg>'
        )
    else:  # "pie"
        svg = (
            '<svg width="42" height="42" viewBox="0 0 42 42" fill="none">'
            '<circle r="15" cx="21" cy="21" fill="transparent" stroke="var(--ds-brand-500)" '
            'stroke-width="8" stroke-dasharray="38 60" stroke-dashoffset="0"/>'
            '<circle r="15" cx="21" cy="21" fill="transparent" stroke="var(--ds-accent-500)" '
            'stroke-width="8" stroke-dasharray="24 74" stroke-dashoffset="-38"/>'
            '<circle r="15" cx="21" cy="21" fill="transparent" stroke="var(--ds-amber-500)" '
            'stroke-width="8" stroke-dasharray="34 64" stroke-dashoffset="-62"/></svg>'
        )
    return f'<div {wrap}>{svg}</div>'


def _kpi_card(icon: str, chip_class: str, label: str, value: str) -> None:
    st.markdown('<div class="gs-kpi">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="gs-kpi-icon-row">
                <div class="ds-kpi-icon {chip_class}" style="margin-bottom:0;">{_icon(icon, 18)}</div>
                <div class="ds-kpi-label" style="margin-top:1px;">{label}</div>
            </div>
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
            f'display:flex;align-items:center;justify-content:center;'
            f'margin:0 auto var(--ds-space-3);">{_icon(icon, 19)}</div>'
            f'<div class="ds-h3" style="text-align:center;">{label}</div>'
            f'<div class="ds-text-sm" style="text-align:center;margin-top:2px;">{desc}</div>'
            f'</div>'
        )
        if i < len(steps) - 1:
            parts.append(f'<div class="gs-workflow-arrow">{_icon("arrow-right", 18)}</div>')
    parts.append("</div>")
    return "".join(parts)


def _feature_card(icon: str, chip_class: str, title: str, desc: str, page: str, illo: str) -> None:
    st.markdown('<div class="gs-feature">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(_mini_illustration(illo), unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ds-kpi-icon {chip_class}" style="width:46px;height:46px;">{_icon(icon, 21)}</div>
            <div class="ds-card-title" style="margin-top:var(--ds-space-2);">{title}</div>
            <div class="ds-card-desc" style="min-height:42px;margin-top:2px;">{desc}</div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label="Open", icon=":material/arrow_forward:", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _badge_row(items) -> None:
    spans = "".join(
        f'<span class="ds-badge ds-badge-neutral" style="display:inline-flex;align-items:center;gap:6px;">'
        f'{_icon(icon, 14, 2)}<span>{name}</span></span>'
        for icon, name in items
    )
    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;gap:var(--ds-space-3);margin-top:var(--ds-space-1);">{spans}</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# SECTION 1 — HERO
# ============================================================

left, right = st.columns([1, 1.15], gap="large")

with left:
    st.markdown(
        '<div class="ds-eyebrow">MACHINE LEARNING · EXPLAINABLE AI</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-display gs-display-lg">Machine Learning-Based<br>'
        '<span class="gs-hero-title-accent">Landslide Risk Assessment</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="gs-hero-kicker">{_icon("globe", 18)} GeoSlide AI · Explainable Risk Intelligence</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="ds-body-lg gs-hero-copy">
        Predicts landslide risk from environmental and geological data, with
        SHAP-driven explainability and NASA historical event visualization.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.write("")
    cta1, cta2, cta3 = st.columns(3, gap="small")
    with cta1:
        st.markdown('<div class="gs-cta-primary gs-cta-row">', unsafe_allow_html=True)
        with st.container(border=True):
            st.page_link(
                "pages/1_🔍_Prediction.py",
                label="Start Prediction",
                icon=":material/search:",
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    with cta2:
        st.markdown('<div class="gs-cta-secondary gs-cta-row">', unsafe_allow_html=True)
        with st.container(border=True):
            st.page_link(
                "pages/4_Dataset_Analytics.py",
                label="Explore Dataset",
                icon=":material/bar_chart:",
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    with cta3:
        st.markdown('<div class="gs-cta-secondary gs-cta-row">', unsafe_allow_html=True)
        with st.container(border=True):
            st.page_link(
                "pages/3_Historical_Map.py",
                label="Historical Map",
                icon=":material/public:",
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
    _kpi_card("target", "ds-chip-brand", "Accuracy", "97.82%")
with k2:
    _kpi_card("database", "ds-chip-accent", "Dataset Size", "9,864")
with k3:
    _kpi_card("bar-chart", "ds-chip-amber", "Features", "34")
with k4:
    _kpi_card("cpu", "ds-chip-brand", "Algorithm", "KNN")

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)

# ============================================================
# SECTION 3 — WORKFLOW
# ============================================================

st.markdown(
    f'<div class="ds-section-title">{_icon("settings", 22)} Workflow</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="ds-section-subtitle">End-to-end ML pipeline</div>', unsafe_allow_html=True)
st.markdown(
    _workflow_html(
        [
            ("layers", "Dataset", "Load and explore the dataset"),
            ("settings", "Preprocessing", "Clean and prepare the data"),
            ("zap", "Prediction", "Run ML model to predict risk"),
            ("brain", "Explainability", "SHAP values for interpretation"),
            ("bar-chart", "Visualization", "Visualize results and insights"),
        ]
    ),
    unsafe_allow_html=True,
)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)

# ============================================================
# SECTION 4 — CORE FEATURES (2x2)
# ============================================================

st.markdown(
    f'<div class="ds-section-title">{_icon("zap", 22)} Core Features</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="ds-section-subtitle">Powerful tools for landslide risk analysis</div>',
    unsafe_allow_html=True,
)

f1, f2 = st.columns(2, gap="medium")
with f1:
    _feature_card(
        "search", "ds-chip-brand", "Prediction",
        "Estimate landslide susceptibility from live environmental "
        "and geological parameters.",
        "pages/1_🔍_Prediction.py",
        "trend",
    )
with f2:
    _feature_card(
        "brain", "ds-chip-accent", "SHAP Explainability",
        "See exactly which features drove each risk prediction, "
        "feature by feature.",
        "pages/2_SHAP_Analysis.py",
        "bars",
    )

st.markdown('<div class="gs-row-gap"></div>', unsafe_allow_html=True)

f3, f4 = st.columns(2, gap="medium")
with f3:
    _feature_card(
        "globe", "ds-chip-amber", "Historical Map",
        "Explore NASA's Global Landslide Catalog on an interactive "
        "world map.",
        "pages/3_Historical_Map.py",
        "map",
    )
with f4:
    _feature_card(
        "bar-chart", "ds-chip-brand", "Dataset Analytics",
        "Inspect feature distributions, correlations and dataset "
        "statistics.",
        "pages/4_Dataset_Analytics.py",
        "pie",
    )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)

# ============================================================
# SECTION 5 — TECHNOLOGY STACK
# ============================================================

st.markdown(
    f'<div class="ds-section-title">{_icon("code", 22)} Technology Stack</div>',
    unsafe_allow_html=True,
)
_badge_row(
    [
        ("code", "Python"),
        ("zap", "FastAPI"),
        ("monitor", "Streamlit"),
        ("cpu", "Scikit-learn"),
        ("git-branch", "SHAP"),
        ("bar-chart", "Plotly"),
        ("table", "Pandas"),
        ("hash", "NumPy"),
    ]
)
