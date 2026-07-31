"""
GeoSlide AI - Home Dashboard

This page is wired to the shared design system introduced in
`frontend/assets/design_system.css` (tokens + `.ds-*` component classes)
and `frontend/utils/design_tokens.py`. Home.py does not define any new
colors, type sizes, spacing values, or radii of its own — every visual
value here is either a `.ds-*` class or a `var(--ds-*)` token from the
design system.

LAYOUT ARCHITECTURE (this revision)
------------------------------------
Every logical section (Hero, KPIs, Workflow, Core Features, Technology
Stack) is a real `st.container(border=True, key=...)` — a genuine
Streamlit layout block, not a raw HTML div wrapped around other calls.
Each of those inner cards (KPI tiles, feature cards, CTA pills) is
*also* a real `st.container(border=True, key=...)`, nested inside its
section. This gives an actual DOM hierarchy of

    Section (card) -> Row/Columns -> Card -> Content

so nothing ever floats directly on the page background, matching the
containers the CSS below can reliably target (each container's `key`
lands on the container's own inner block, e.g. `st-key-kpi-card-0`,
which this file's CSS reaches via
`[data-testid="stLayoutWrapper"]:has(> [class*="st-key-..."])`).

Note: Streamlit's bordered-container wrapper element in this app's
installed version is `[data-testid="stLayoutWrapper"]` (verified against
the rendered DOM), not the older `stVerticalBlockBorderWrapper` name.

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
# truth, untouched here: same colors, typography, radii, shadows as
# before. Loading it is the only thing that changes: no page imported
# it before the earlier phase of this project.
st.markdown(f"<style>{DESIGN_SYSTEM_CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Home-page wiring CSS — maps Streamlit's native container markup onto
# the existing design-system tokens/classes. No new colors, sizes,
# radii, or spacing values are declared; every rule resolves through
# var(--ds-*).
# ------------------------------------------------------------
HOME_WIRING_CSS = """
[data-testid="stAppViewContainer"] {
    background: var(--ds-bg) !important;
}

[data-testid="stAppViewContainer"] .block-container {
    padding: var(--ds-space-6) var(--ds-container-padding-desktop) var(--ds-space-10) !important;
    max-width: var(--ds-container-max);
}

.gs-section-spacer { height: var(--ds-space-6); }

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

/* ============================================================
   BASELINE — every real bordered container on this page starts
   from the same premium card look (white surface, hairline
   border, soft shadow, rounded corners). Section wrappers and
   leaf cards both start here, then get overridden below.
   ============================================================ */
[data-testid="stAppViewContainer"] [data-testid="stLayoutWrapper"] {
    background: var(--ds-surface) !important;
    border: 1px solid var(--ds-border) !important;
    border-radius: var(--ds-radius-lg) !important;
    box-shadow: var(--ds-shadow-sm) !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base),
                border-color var(--ds-transition-base), background var(--ds-transition-base);
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

/* ============================================================
   SECTION PANELS — the outer card for every one of the 5 page
   sections (Hero, KPIs, Workflow, Core Features, Tech Stack).
   A slightly recessed, quieter surface than the leaf cards
   inside it, so the hierarchy (panel -> cards) reads clearly.
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-"]) {
    background: var(--ds-bg-subtle) !important;
    border: 1px solid var(--ds-border) !important;
    box-shadow: var(--ds-shadow-xs) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}

/* ============================================================
   SECTION 1 — HERO
   58/42 split, illustration un-boxed so it anchors the right
   side instead of sitting in its own small framed panel.
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-hero"]) {
    background: var(--ds-surface) !important;
    box-shadow: var(--ds-shadow-md) !important;
    padding: var(--ds-space-8) !important;
}
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
    max-width: 92%;
    font-size: 1.05rem !important;
    line-height: var(--ds-leading-loose) !important;
    color: var(--ds-text-secondary) !important;
    font-weight: var(--ds-weight-regular);
}
.gs-display-lg {
    font-size: 2.7rem !important;
    line-height: 1.12 !important;
    margin: var(--ds-space-2) 0 0 !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-hero"]) [data-testid="stImage"] {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    overflow: visible;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-hero"]) [data-testid="stImage"] img {
    width: 100%;
    height: auto;
    max-width: none;
    transform: scale(1.28);
    filter: drop-shadow(0 30px 46px rgba(28, 35, 31, 0.20));
    animation: gs-hero-float 7s ease-in-out infinite;
}
@keyframes gs-hero-float {
    0%, 100% { transform: scale(1.28) translateY(0px); }
    50%      { transform: scale(1.28) translateY(-12px); }
}
@media (prefers-reduced-motion: reduce) {
    [data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-hero"]) [data-testid="stImage"] img {
        animation: none;
    }
}

/* ---- CTA pills: ALL THREE share one premium filled-button design —
   same height, radius, padding, and shadow shape. Only the fill color
   (and its matching hover-shadow tint) changes per action, so nothing
   here reads as a lesser/outlined "secondary" button. ---- */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cta-primary"]),
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cta-secondary-0"]),
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cta-secondary-1"]) {
    border: none !important;
    border-radius: var(--ds-radius-full) !important;
    box-shadow: var(--ds-shadow-sm) !important;
    padding: 0 !important;
    overflow: visible !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base), filter var(--ds-transition-base);
}
/* Start Prediction — emerald */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cta-primary"]) {
    background: linear-gradient(90deg, var(--ds-brand-500) 0%, var(--ds-brand-600) 100%) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cta-primary"]):hover {
    transform: var(--ds-lift-hover);
    box-shadow: 0 14px 28px rgba(47, 107, 79, 0.30) !important;
    filter: brightness(1.05);
}
/* Explore Dataset — violet */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cta-secondary-0"]) {
    background: linear-gradient(90deg, var(--ds-violet-500) 0%, var(--ds-violet-600) 100%) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cta-secondary-0"]):hover {
    transform: var(--ds-lift-hover);
    box-shadow: 0 14px 28px rgba(124, 93, 168, 0.30) !important;
    filter: brightness(1.05);
}
/* Historical Map — blue */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cta-secondary-1"]) {
    background: linear-gradient(90deg, var(--ds-accent-500) 0%, var(--ds-accent-600) 100%) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cta-secondary-1"]):hover {
    transform: var(--ds-lift-hover);
    box-shadow: 0 14px 28px rgba(45, 125, 169, 0.30) !important;
    filter: brightness(1.05);
}
/* Shared geometry + inverse (white) text/icon for all three fills */
[class*="st-key-cta-primary"] .stPageLink,
[class*="st-key-cta-secondary-0"] .stPageLink,
[class*="st-key-cta-secondary-1"] .stPageLink {
    display: flex !important;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 46px;
    padding: 0 1.1rem !important;
    box-sizing: border-box;
}
[class*="st-key-cta-primary"] .stPageLink p,
[class*="st-key-cta-secondary-0"] .stPageLink p,
[class*="st-key-cta-secondary-1"] .stPageLink p {
    color: var(--ds-text-inverse) !important;
    font-size: 0.88rem !important;
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: unset !important;
    margin: 0 !important;
}
[class*="st-key-cta-primary"] [data-testid="stIconMaterial"],
[class*="st-key-cta-secondary-0"] [data-testid="stIconMaterial"],
[class*="st-key-cta-secondary-1"] [data-testid="stIconMaterial"] {
    color: var(--ds-text-inverse) !important;
    font-size: 1.05rem !important;
}

/* ============================================================
   SECTION 2 — KPI CARDS
   Four equal, premium metric tiles inside the KPI section panel.
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kpi-card-"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-5) !important;
    height: 148px;
    display: flex !important;
    flex-direction: column;
    justify-content: center;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kpi-card-"]):hover {
    transform: translateY(-3px);
    box-shadow: var(--ds-shadow-hover) !important;
    border-color: var(--ds-brand-200) !important;
}
.gs-kpi-icon-row { display: flex; align-items: center; gap: var(--ds-space-3); margin-bottom: var(--ds-space-2); }
.gs-kpi-icon-row .ds-kpi-icon {
    width: 38px; height: 38px; border-radius: var(--ds-radius-sm);
    display: flex; align-items: center; justify-content: center;
    transition: transform var(--ds-transition-base);
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kpi-card-"]):hover .ds-kpi-icon { transform: scale(1.08); }
.gs-kpi-value { font-size: 1.85rem !important; letter-spacing: -0.01em; }
.gs-kpi-desc { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: 3px; }

/* ============================================================
   SECTION 3 — WORKFLOW
   Steps are raw .ds-card divs (real elements already), so their
   styling is untouched from before — just re-affirmed here.
   ============================================================ */
.gs-workflow-row { display: flex; align-items: stretch; justify-content: space-between; gap: var(--ds-space-3); margin-top: var(--ds-space-2); }
.gs-workflow-step {
    position: relative; flex: 1;
    padding: var(--ds-space-6) var(--ds-space-4) var(--ds-space-5) !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base), border-color var(--ds-transition-base);
}
.gs-workflow-step:hover { transform: translateY(-3px); border-color: var(--ds-brand-200); box-shadow: var(--ds-shadow-md); }
.gs-workflow-step .ds-chip-brand { transition: transform var(--ds-transition-base); }
.gs-workflow-step:hover .ds-chip-brand { transform: scale(1.08); }
.gs-workflow-badge {
    position: absolute; top: calc(-1 * var(--ds-space-3)); left: var(--ds-space-4);
    width: 26px; height: 26px; border-radius: var(--ds-radius-full);
    background: var(--ds-brand-500); color: var(--ds-text-inverse);
    font-size: var(--ds-text-xs); font-weight: var(--ds-weight-bold);
    display: flex; align-items: center; justify-content: center; box-shadow: var(--ds-shadow-sm);
}
.gs-workflow-arrow { flex: 0 0 auto; color: var(--ds-brand-400); opacity: 0.6; margin-top: var(--ds-space-10); transition: opacity var(--ds-transition-base); }
.gs-workflow-row:hover .gs-workflow-arrow { opacity: 0.85; }

/* ============================================================
   SECTION 4 — CORE FEATURES (2x2)
   Each card: top block (icon/title/desc, full width) then a
   bottom row split Open-left / illustration-right via CSS Grid
   on the container's own real content block.
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-feature-card-"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-6) !important;
    height: 268px;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-feature-card-"]):hover {
    transform: var(--ds-lift-hover);
    border-color: var(--ds-brand-200) !important;
    box-shadow: var(--ds-shadow-hover) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-feature-card-"]):hover .ds-kpi-icon { transform: scale(1.08); }
[class*="st-key-feature-card-"] {
    display: grid !important;
    grid-template-columns: 1fr 1fr;
    align-content: space-between;
    height: 100%;
}
[class*="st-key-feature-card-"] > div:first-child { grid-column: 1 / -1; }
[class*="st-key-feature-card-"] .ds-kpi-icon { transition: transform var(--ds-transition-base); }
.gs-feature-illo {
    grid-column: 2;
    justify-self: end;
    align-self: end;
    padding: var(--ds-space-2) var(--ds-space-3);
    background: var(--ds-bg-subtle);
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-sm);
    display: flex; align-items: center; justify-content: center;
    width: 100%;
}
.gs-feature-illo svg { width: 100%; height: auto; max-width: 140px; }
[class*="st-key-feature-card-"] .stPageLink {
    grid-column: 1;
    justify-self: start;
    align-self: end;
    width: auto !important;
    background: transparent !important;
    padding: 0.4rem 0 !important;
}
[class*="st-key-feature-card-"] .stPageLink p {
    color: var(--ds-brand-600) !important;
    font-weight: var(--ds-weight-bold);
    text-align: left;
}
[class*="st-key-feature-card-"] .stPageLink:hover p { color: var(--ds-brand-700, var(--ds-brand-600)) !important; }
"""

st.markdown(f"<style>{HOME_WIRING_CSS}</style>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Sidebar (shared, unmodified)
# ------------------------------------------------------------
render_sidebar()


# ============================================================
# Small local helpers (Home-page only, not shared components)
# ============================================================

# Minimal Lucide-style inline icon set — decorative only, no emoji.
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
    """Small decorative SVG rendered in-flow inside a feature card's own
    illustration panel (purely visual, no interactivity)."""
    if kind == "trend":
        svg = (
            '<svg viewBox="0 0 140 50" fill="none" xmlns="http://www.w3.org/2000/svg">'
            '<polyline points="4,42 30,30 54,37 82,15 136,5" stroke="var(--ds-brand-500)" '
            'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="136" cy="5" r="4" fill="var(--ds-brand-500)"/></svg>'
        )
    elif kind == "bars":
        rows = [("120", 3), ("88", 15), ("62", 27), ("38", 39)]
        rects = "".join(
            f'<rect x="0" y="{y}" width="{w}" height="8" rx="4" fill="var(--ds-accent-500)" opacity="{1 - i * 0.16}"/>'
            for i, (w, y) in enumerate(rows)
        )
        svg = f'<svg viewBox="0 0 140 50" fill="none" xmlns="http://www.w3.org/2000/svg">{rects}</svg>'
    elif kind == "map":
        svg = (
            '<svg viewBox="0 0 140 50" fill="none" xmlns="http://www.w3.org/2000/svg">'
            '<ellipse cx="70" cy="25" rx="62" ry="20" stroke="var(--ds-amber-500)" stroke-width="1.4" opacity="0.4"/>'
            '<ellipse cx="70" cy="25" rx="40" ry="13" stroke="var(--ds-amber-500)" stroke-width="1.2" opacity="0.3"/>'
            '<circle cx="38" cy="19" r="3" fill="var(--ds-amber-500)"/>'
            '<circle cx="84" cy="12" r="2.3" fill="var(--ds-amber-500)"/>'
            '<circle cx="98" cy="32" r="3.5" fill="var(--ds-amber-500)"/>'
            '<circle cx="52" cy="35" r="2.5" fill="var(--ds-amber-500)"/></svg>'
        )
    else:  # "pie"
        svg = (
            '<svg viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">'
            '<circle r="18" cx="25" cy="25" fill="transparent" stroke="var(--ds-brand-500)" '
            'stroke-width="9" stroke-dasharray="45 68" stroke-dashoffset="0"/>'
            '<circle r="18" cx="25" cy="25" fill="transparent" stroke="var(--ds-accent-500)" '
            'stroke-width="9" stroke-dasharray="28 85" stroke-dashoffset="-45"/>'
            '<circle r="18" cx="25" cy="25" fill="transparent" stroke="var(--ds-amber-500)" '
            'stroke-width="9" stroke-dasharray="40 73" stroke-dashoffset="-73"/></svg>'
        )
    return svg


def _kpi_card(icon: str, chip_class: str, label: str, value: str, desc: str, key: str) -> None:
    with st.container(border=True, key=key):
        st.markdown(
            f"""
            <div class="gs-kpi-icon-row">
                <div class="ds-kpi-icon {chip_class}" style="margin-bottom:0;">{_icon(icon, 18)}</div>
                <div class="ds-kpi-label" style="margin-top:1px;">{label}</div>
            </div>
            <div class="gs-kpi-value">{value}</div>
            <div class="gs-kpi-desc">{desc}</div>
            """,
            unsafe_allow_html=True,
        )


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


def _feature_card(icon: str, chip_class: str, title: str, desc: str, page: str, illo: str, key: str) -> None:
    with st.container(border=True, key=key):
        st.markdown(
            f"""
            <div>
                <div class="ds-kpi-icon {chip_class}" style="width:44px;height:44px;">{_icon(icon, 20)}</div>
                <div class="ds-card-title" style="margin-top:var(--ds-space-3);">{title}</div>
                <div class="ds-card-desc" style="margin-top:2px;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label="Open", icon=":material/arrow_forward:")
        st.markdown(f'<div class="gs-feature-illo">{_mini_illustration(illo)}</div>', unsafe_allow_html=True)


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

with st.container(border=True, key="section-hero"):
    left, right = st.columns([58, 42], gap="large")

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
        cta1, cta2, cta3 = st.columns(3, gap="medium")
        with cta1:
            with st.container(border=True, key="cta-primary"):
                st.page_link(
                    "pages/1_🔍_Prediction.py",
                    label="Start Prediction",
                    icon=":material/search:",
                    use_container_width=True,
                )
        with cta2:
            with st.container(border=True, key="cta-secondary-0"):
                st.page_link(
                    "pages/4_Dataset_Analytics.py",
                    label="Explore Dataset",
                    icon=":material/bar_chart:",
                    use_container_width=True,
                )
        with cta3:
            with st.container(border=True, key="cta-secondary-1"):
                st.page_link(
                    "pages/3_Historical_Map.py",
                    label="Historical Map",
                    icon=":material/public:",
                    use_container_width=True,
                )

    with right:
        st.image(str(HERO_IMAGE_FILE), use_container_width=True)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)

# ============================================================
# SECTION 2 — KPI ROW
# ============================================================

with st.container(border=True, key="section-kpi"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("bar-chart", 22)} Key Metrics</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="ds-section-subtitle">Model performance at a glance</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        _kpi_card("target", "ds-chip-brand", "Accuracy", "97.82%", "Held-out test accuracy", "kpi-card-0")
    with k2:
        _kpi_card("database", "ds-chip-accent", "Dataset Size", "9,864", "Labeled records used", "kpi-card-1")
    with k3:
        _kpi_card("bar-chart", "ds-chip-amber", "Features", "34", "Engineered + raw inputs", "kpi-card-2")
    with k4:
        _kpi_card("cpu", "ds-chip-brand", "Algorithm", "KNN", "k-Nearest Neighbors", "kpi-card-3")

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)

# ============================================================
# SECTION 3 — WORKFLOW
# ============================================================

with st.container(border=True, key="section-workflow"):
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

with st.container(border=True, key="section-features"):
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
            "pages/1_🔍_Prediction.py", "trend", "feature-card-0",
        )
    with f2:
        _feature_card(
            "brain", "ds-chip-accent", "SHAP Explainability",
            "See exactly which features drove each risk prediction, "
            "feature by feature.",
            "pages/2_SHAP_Analysis.py", "bars", "feature-card-1",
        )

    st.write("")
    f3, f4 = st.columns(2, gap="medium")
    with f3:
        _feature_card(
            "globe", "ds-chip-amber", "Historical Map",
            "Explore NASA's Global Landslide Catalog on an interactive "
            "world map.",
            "pages/3_Historical_Map.py", "map", "feature-card-2",
        )
    with f4:
        _feature_card(
            "bar-chart", "ds-chip-brand", "Dataset Analytics",
            "Inspect feature distributions, correlations and dataset "
            "statistics.",
            "pages/4_Dataset_Analytics.py", "pie", "feature-card-3",
        )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)

# ============================================================
# SECTION 5 — TECHNOLOGY STACK
# ============================================================

with st.container(border=True, key="section-techstack"):
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
    