"""
GeoSlide - About Page
========================

A static, presentation-ready overview of the GeoSlide project: what it
does, its core features, the technology stack, the machine learning
pipeline, the roadmap ahead, and the developer behind it.

This page is purely informational — no data loading, no charts, no
API calls.

UI REDESIGN (this revision) — wired to the shared design system
------------------------------------------------------------------
This page previously used plain, unstyled Streamlit primitives
(`st.subheader`, bare `st.columns` grids) that didn't match Home.py or
the redesigned Prediction, SHAP Analysis, and Historical Map pages,
which all run on the shared, light, warm-neutral design system defined
in `frontend/assets/design_system.css` and
`frontend/utils/design_tokens.py`. This revision wires the About page
into that same system — same tokens, same `.ds-*` classes, same
"premium card" pattern (`st.container(border=True, key="section-...")`
+ CSS that targets
`[data-testid="stLayoutWrapper"]:has(> [class*="st-key-..."])`) already
used on Home.py and the redesigned inner pages.

Layout (top to bottom): Hero, Project Overview, Core Features,
Technology Stack, Machine Learning Pipeline, Future Enhancements,
Developer. Every section lives in its own bordered card, per the
redesign brief.

Content notes:
  - The Acknowledgements section has been removed entirely, along with
    every reference to college/university, internship, IAESTE,
    department, supervisor, or project submission — none of that
    content exists anywhere in this file.
  - The Developer section shows only "Developer" and "Kritartha
    Kakati" — no designation, biography, social links, or contact
    details.
  - Core Features, Technology Stack, and the ML Pipeline steps carry
    forward the same factual content the previous About page had
    (feature list, tech stack, workflow stages), just presented as
    premium cards with short descriptive copy instead of bare labels.
  - Future Enhancements is new, forward-looking roadmap content,
    clearly framed as planned rather than existing functionality.

This is a content page only — no backend, navigation, or shared
component logic lives here or was touched by this redesign.
"""

from pathlib import Path

import streamlit as st

from components.sidebar import render_sidebar
from utils.theme import load_styles


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="About | GeoSlide",
    page_icon="ℹ️",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent.parent
DESIGN_SYSTEM_CSS_FILE = ROOT / "assets" / "design_system.css"
HERO_ILLUSTRATION_FILE = ROOT / "assets" / "images" / "geoslide_ecosystem.png"


# ---------------------------------------------------------------------------
# Page wiring CSS — same approach as Home.py / the Prediction / SHAP /
# Historical Map pages: maps Streamlit's native container markup onto
# the shared design-system tokens/classes. No new colors, spacing,
# radii, or type sizes are declared here; every visual value below is
# a `.ds-*` class or a `var(--ds-*)` token.
# ---------------------------------------------------------------------------

ABOUT_WIRING_CSS = """
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
   BASELINE — every real bordered container starts from the same
   premium card look, then gets overridden per-section below.
   ============================================================ */
[data-testid="stAppViewContainer"] [data-testid="stLayoutWrapper"] {
    background: var(--ds-surface) !important;
    border: 1px solid var(--ds-border) !important;
    border-style: solid !important;
    border-radius: var(--ds-radius-lg) !important;
    box-shadow: var(--ds-shadow-sm) !important;
    outline: none !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base),
                border-color var(--ds-transition-base), background var(--ds-transition-base);
}
/* Clean-border safety net — neutralizes any legacy/duplicate default
   Streamlit border markup that would otherwise stack under the
   custom border above and read as a rough, doubled outline. Purely
   cosmetic: no size, spacing, or layout is touched. */
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stAppViewContainer"] [data-testid="stLayoutWrapper"] > div {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
[data-testid="stAppViewContainer"] button {
    outline: none !important;
    border-style: solid !important;
}
[data-testid="stAppViewContainer"] button:focus,
[data-testid="stAppViewContainer"] button:focus-visible {
    outline: none !important;
}

/* ============================================================
   SECTION PANELS — outer card for every page section (Hero,
   Overview, Features, Tech Stack, Pipeline, Roadmap, Developer).
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-"]) {
    background: var(--ds-bg-subtle) !important;
    border: 1px solid var(--ds-border) !important;
    box-shadow: var(--ds-shadow-xs) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}

/* ============================================================
   SECTION 1 — HERO
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-hero"]) {
    background: var(--ds-surface) !important;
    box-shadow: var(--ds-shadow-md) !important;
    padding: var(--ds-space-8) !important;
}
.gs-hero-copy {
    max-width: 94%;
    font-size: 1.02rem !important;
    line-height: var(--ds-leading-loose) !important;
    color: var(--ds-text-secondary) !important;
    font-weight: var(--ds-weight-regular);
    margin-top: var(--ds-space-3);
}
.gs-display-md {
    font-size: 2.2rem !important;
    line-height: 1.15 !important;
    margin: var(--ds-space-3) 0 0 !important;
}
[class*="st-key-hero-illo-wrap"] {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 180px;
}
[class*="st-key-hero-illo-wrap"] img {
    width: 100%;
    max-width: 230px;
    height: auto;
    animation: gs-hero-float 7s ease-in-out infinite;
    filter: drop-shadow(0 18px 30px rgba(28, 35, 31, 0.12));
}
@keyframes gs-hero-float {
    0%, 100% { transform: translateY(0px); }
    50%      { transform: translateY(-10px); }
}
@media (prefers-reduced-motion: reduce) {
    [class*="st-key-hero-illo-wrap"] img { animation: none; }
}

/* ============================================================
   SECTION 2 — PROJECT OVERVIEW
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-overview"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
.gs-overview-copy {
    font-size: var(--ds-text-body);
    color: var(--ds-text-secondary);
    line-height: var(--ds-leading-loose);
    max-width: 92%;
}
.gs-overview-stats { display: flex; flex-wrap: wrap; gap: var(--ds-space-3); margin-top: var(--ds-space-4); }
.gs-overview-stat {
    display: inline-flex;
    align-items: center;
    gap: var(--ds-space-2);
    background: var(--ds-bg-subtle);
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-full);
    padding: 7px 16px;
    font-size: var(--ds-text-sm);
    font-weight: var(--ds-weight-semibold);
    color: var(--ds-text-secondary);
}

/* ============================================================
   SECTION 3 — CORE FEATURES
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-features"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-feature-card-"]) {
    background: var(--ds-bg-subtle) !important;
    padding: var(--ds-space-5) !important;
    height: 160px;
    display: flex !important;
    flex-direction: column;
    justify-content: flex-start;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-feature-card-"]):hover {
    transform: var(--ds-lift-hover);
    border-color: var(--ds-brand-200) !important;
    box-shadow: var(--ds-shadow-hover) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-feature-card-"]):hover .ds-kpi-icon { transform: scale(1.08); }
[class*="st-key-feature-card-"] .ds-kpi-icon { transition: transform var(--ds-transition-base); }

/* ============================================================
   SECTION 4 — TECHNOLOGY STACK
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-techstack"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
.gs-tech-row { display: flex; flex-wrap: wrap; gap: var(--ds-space-3); margin-top: var(--ds-space-1); }
.gs-tech-chip {
    display: inline-flex;
    align-items: center;
    gap: var(--ds-space-3);
    background: var(--ds-surface);
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-md);
    padding: var(--ds-space-2) var(--ds-space-4) var(--ds-space-2) var(--ds-space-2);
    box-shadow: var(--ds-shadow-sm);
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base), border-color var(--ds-transition-base);
}
.gs-tech-chip:hover {
    transform: var(--ds-lift-hover);
    box-shadow: var(--ds-shadow-hover);
    border-color: var(--ds-brand-200);
}
.gs-tech-chip-icon {
    width: 32px;
    height: 32px;
    border-radius: var(--ds-radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.gs-tech-chip-name {
    font-size: var(--ds-text-sm);
    font-weight: var(--ds-weight-semibold);
    color: var(--ds-text-primary);
}

/* ============================================================
   SECTION 5 — MACHINE LEARNING PIPELINE
   (steps are raw .ds-card divs, same pattern as Home.py's Workflow)
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-pipeline"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
.gs-pipeline-row { display: flex; align-items: stretch; justify-content: space-between; gap: var(--ds-space-3); margin-top: var(--ds-space-2); }
.gs-pipeline-row + .gs-pipeline-row { margin-top: var(--ds-space-5); }
.gs-pipeline-step {
    position: relative; flex: 1;
    padding: var(--ds-space-6) var(--ds-space-4) var(--ds-space-5) !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base), border-color var(--ds-transition-base);
}
.gs-pipeline-step:hover { transform: translateY(-3px); border-color: var(--ds-brand-200); box-shadow: var(--ds-shadow-md); }
.gs-pipeline-step .ds-chip-brand { transition: transform var(--ds-transition-base); }
.gs-pipeline-step:hover .ds-chip-brand { transform: scale(1.08); }
.gs-pipeline-badge {
    position: absolute; top: calc(-1 * var(--ds-space-3)); left: var(--ds-space-4);
    width: 26px; height: 26px; border-radius: var(--ds-radius-full);
    background: var(--ds-brand-500); color: var(--ds-text-inverse);
    font-size: var(--ds-text-xs); font-weight: var(--ds-weight-bold);
    display: flex; align-items: center; justify-content: center; box-shadow: var(--ds-shadow-sm);
}
.gs-pipeline-arrow { flex: 0 0 auto; color: var(--ds-brand-400); opacity: 0.6; margin-top: var(--ds-space-10); transition: opacity var(--ds-transition-base); }
.gs-pipeline-row:hover .gs-pipeline-arrow { opacity: 0.85; }

/* ============================================================
   SECTION 6 — FUTURE ENHANCEMENTS (roadmap cards)
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-roadmap"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-roadmap-card-"]) {
    background: var(--ds-bg-subtle) !important;
    padding: var(--ds-space-5) !important;
    height: 168px;
    display: flex !important;
    flex-direction: column;
    justify-content: flex-start;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-roadmap-card-"]):hover {
    transform: var(--ds-lift-hover);
    border-color: var(--ds-accent-200, var(--ds-border)) !important;
    box-shadow: var(--ds-shadow-hover) !important;
}
.gs-roadmap-head { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--ds-space-2); }

/* ============================================================
   SECTION 7 — DEVELOPER
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-developer"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-8) !important;
    text-align: center;
}
.gs-developer-avatar {
    width: 64px; height: 64px;
    border-radius: var(--ds-radius-full);
    background: var(--ds-brand-50);
    color: var(--ds-brand-600);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto var(--ds-space-4);
}
.gs-developer-label {
    font-size: var(--ds-text-xs);
    font-weight: var(--ds-weight-bold);
    text-transform: uppercase;
    letter-spacing: var(--ds-tracking-wide);
    color: var(--ds-text-tertiary);
    margin-bottom: var(--ds-space-2);
}
.gs-developer-name {
    font-size: 1.6rem;
    font-weight: var(--ds-weight-extrabold);
    color: var(--ds-text-primary);
    letter-spacing: var(--ds-tracking-tight);
}
"""

st.markdown(f"<style>{load_styles()}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{DESIGN_SYSTEM_CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{ABOUT_WIRING_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

render_sidebar()


# ---------------------------------------------------------------------------
# Local icon set (page-scoped, same inline-SVG pattern Home.py and the
# redesigned inner pages use — decorative only, no emoji, no external
# assets).
# ---------------------------------------------------------------------------

_ICON_PATHS = {
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18Z"/>',
    "brain": '<path d="M9 3.5A2.5 2.5 0 0 0 6.5 6v.3a2.5 2.5 0 0 0-1.4 4.3A2.8 2.8 0 0 0 6 15.6a2.5 2.5 0 0 0 3 3.3A2.5 2.5 0 0 0 11.5 20V6A2.5 2.5 0 0 0 9 3.5Z"/><path d="M15 3.5A2.5 2.5 0 0 1 17.5 6v.3a2.5 2.5 0 0 1 1.4 4.3A2.8 2.8 0 0 1 18 15.6a2.5 2.5 0 0 1-3 3.3A2.5 2.5 0 0 1 12.5 20V6A2.5 2.5 0 0 1 15 3.5Z"/>',
    "layers": '<path d="m12 3 8 4.2-8 4.2-8-4.2Z"/><path d="m4 12 8 4.2 8-4.2"/><path d="m4 16.4 8 4.2 8-4.2"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 3v2.2M12 18.8V21M4.9 6.3l1.6 1.5M17.5 16.2l1.6 1.5M3 12h2.2M18.8 12H21M4.9 17.7l1.6-1.5M17.5 7.8l1.6-1.5"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.3-4.3"/>',
    "monitor": '<rect x="2.5" y="4" width="19" height="13" rx="1.5"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>',
    "bar-chart": '<line x1="5" y1="20" x2="5" y2="13"/><line x1="12" y1="20" x2="12" y2="6"/><line x1="19" y1="20" x2="19" y2="10"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><rect x="10" y="10" width="4" height="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.5 4.5l2 2M17.5 17.5l2 2M4.5 19.5l2-2M17.5 6.5l2-2"/>',
    "code": '<polyline points="15 6 21 12 15 18"/><polyline points="9 18 3 12 9 6"/>',
    "zap": '<path d="M12.5 2 4 13h6l-1 9L20 11h-6l-1-9Z"/>',
    "git-branch": '<line x1="7" y1="3" x2="7" y2="14"/><circle cx="17" cy="6" r="2.6"/><circle cx="7" cy="17.4" r="2.6"/><path d="M17 8.6a8 8 0 0 1-8 8"/>',
    "table": '<rect x="3" y="3" width="18" height="18" rx="1.5"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
    "database": '<ellipse cx="12" cy="5.5" rx="8" ry="2.7"/><path d="M4 5.5v13c0 1.5 3.6 2.7 8 2.7s8-1.2 8-2.7v-13"/><path d="M4 12c0 1.5 3.6 2.7 8 2.7s8-1.2 8-2.7"/>',
    "hash": '<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>',
    "arrow-right": '<line x1="4" y1="12" x2="18" y2="12"/><polyline points="12 6 18 12 12 18"/>',
    "smartphone": '<rect x="7" y="2.5" width="10" height="19" rx="2"/><line x1="11" y1="18.5" x2="13" y2="18.5"/>',
    "user": '<circle cx="12" cy="8" r="3.4"/><path d="M5 20c0-3.9 3.1-7 7-7s7 3.1 7 7"/>',
    "sparkles": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
}


def _icon(name: str, size: int = 20, stroke_width: float = 1.8) -> str:
    """Inline Lucide-style SVG icon (no emoji)."""
    body = _ICON_PATHS.get(name, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" '
        f'stroke-linejoin="round" style="display:block;">{body}</svg>'
    )


def _hero_illustration() -> str:
    """Small decorative hero illustration — a stylised AI chip wired into
    a small neural network, built the same way the Prediction/SHAP/
    Historical Map hero illustrations are (inline SVG, design tokens
    for color, purely decorative)."""
    return (
        '<svg viewBox="0 0 220 200" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="110" cy="100" r="82" stroke="var(--ds-brand-200)" stroke-width="1.4" opacity="0.5"/>'
        '<rect x="82" y="72" width="56" height="56" rx="10" fill="var(--ds-surface)" '
        'stroke="var(--ds-brand-500)" stroke-width="2.2"/>'
        '<rect x="96" y="86" width="28" height="28" rx="4" fill="var(--ds-brand-100)"/>'
        '<line x1="110" y1="60" x2="110" y2="72" stroke="var(--ds-brand-400)" stroke-width="2"/>'
        '<line x1="110" y1="128" x2="110" y2="140" stroke="var(--ds-brand-400)" stroke-width="2"/>'
        '<line x1="70" y1="100" x2="82" y2="100" stroke="var(--ds-brand-400)" stroke-width="2"/>'
        '<line x1="138" y1="100" x2="150" y2="100" stroke="var(--ds-brand-400)" stroke-width="2"/>'
        '<circle cx="110" cy="52" r="6" fill="var(--ds-amber-500)"/>'
        '<circle cx="110" cy="148" r="6" fill="var(--ds-accent-500)"/>'
        '<circle cx="60" cy="100" r="6" fill="var(--ds-accent-500)"/>'
        '<circle cx="160" cy="100" r="6" fill="var(--ds-amber-500)"/>'
        '<path d="M60 100 40 70" stroke="var(--ds-brand-300)" stroke-width="1.4" opacity="0.7"/>'
        '<path d="M160 100 180 70" stroke="var(--ds-brand-300)" stroke-width="1.4" opacity="0.7"/>'
        '<path d="M60 100 40 130" stroke="var(--ds-brand-300)" stroke-width="1.4" opacity="0.7"/>'
        '<path d="M160 100 180 130" stroke="var(--ds-brand-300)" stroke-width="1.4" opacity="0.7"/>'
        '<circle cx="40" cy="70" r="4" fill="var(--ds-brand-300)"/>'
        '<circle cx="180" cy="70" r="4" fill="var(--ds-brand-300)"/>'
        '<circle cx="40" cy="130" r="4" fill="var(--ds-brand-300)"/>'
        '<circle cx="180" cy="130" r="4" fill="var(--ds-brand-300)"/>'
        '</svg>'
    )


def _feature_card(icon: str, chip_class: str, title: str, desc: str, key: str) -> None:
    with st.container(border=True, key=key):
        st.markdown(
            f"""
            <div class="ds-kpi-icon {chip_class}" style="width:42px;height:42px;">{_icon(icon, 19)}</div>
            <div class="ds-card-title" style="margin-top:var(--ds-space-3);font-size:1.02rem;">{title}</div>
            <div class="ds-card-desc" style="margin-top:2px;">{desc}</div>
            """,
            unsafe_allow_html=True,
        )


def _pipeline_row_html(steps) -> str:
    parts = ['<div class="gs-pipeline-row">']
    for i, (icon, label, desc, step_no) in enumerate(steps):
        parts.append(
            f'<div class="gs-pipeline-step ds-card">'
            f'<div class="gs-pipeline-badge">{step_no}</div>'
            f'<div class="ds-chip-brand" style="width:42px;height:42px;border-radius:var(--ds-radius-xs);'
            f'display:flex;align-items:center;justify-content:center;'
            f'margin:0 auto var(--ds-space-3);">{_icon(icon, 19)}</div>'
            f'<div class="ds-h3" style="text-align:center;">{label}</div>'
            f'<div class="ds-text-sm" style="text-align:center;margin-top:2px;">{desc}</div>'
            f'</div>'
        )
        if i < len(steps) - 1:
            parts.append(f'<div class="gs-pipeline-arrow">{_icon("arrow-right", 18)}</div>')
    parts.append("</div>")
    return "".join(parts)


def _badge_row(items) -> None:
    chip_classes = ["ds-chip-brand", "ds-chip-accent", "ds-chip-amber"]
    spans = "".join(
        f'<span class="gs-tech-chip">'
        f'<span class="gs-tech-chip-icon {chip_classes[i % len(chip_classes)]}">{_icon(icon, 15)}</span>'
        f'<span class="gs-tech-chip-name">{name}</span>'
        f'</span>'
        for i, (icon, name) in enumerate(items)
    )
    st.markdown(f'<div class="gs-tech-row">{spans}</div>', unsafe_allow_html=True)


def _roadmap_card(icon: str, chip_class: str, title: str, desc: str, key: str) -> None:
    with st.container(border=True, key=key):
        st.markdown(
            f"""
            <div class="gs-roadmap-head">
                <div class="ds-kpi-icon {chip_class}" style="width:42px;height:42px;">{_icon(icon, 19)}</div>
                <span class="ds-badge ds-badge-info">Planned</span>
            </div>
            <div class="ds-card-title" style="margin-top:var(--ds-space-3);font-size:1.02rem;">{title}</div>
            <div class="ds-card-desc" style="margin-top:2px;">{desc}</div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SECTION 1 — HERO
# ============================================================

with st.container(border=True, key="section-hero"):
    left, right = st.columns([64, 36], gap="large")

    with left:
        st.markdown(
            f'<div class="ds-eyebrow">{_icon("sparkles", 14, 2)}<span>&nbsp;ABOUT GEOSLIDE AI</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ds-display gs-display-md">About GeoSlide AI</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="ds-body-lg gs-hero-copy">
            GeoSlide AI is a Machine Learning-based landslide risk assessment
            platform that combines geospatial intelligence, environmental
            analytics, explainable AI, and interactive visualizations to
            support smarter landslide risk analysis.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        with st.container(key="hero-illo-wrap"):
            st.image(str(HERO_ILLUSTRATION_FILE), use_container_width=True)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 2 — PROJECT OVERVIEW
# ============================================================

with st.container(border=True, key="section-overview"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("globe", 20)} Project Overview</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="gs-overview-copy">
        <b>GeoSlide</b> predicts landslide risk using machine learning, and explains
        every prediction using <b>SHAP</b> — so users don't just get a risk score,
        they understand <i>why</i>. It's trained on ground-based sensor readings and
        cross-referenced against NASA's Global Landslide Catalog of real historical
        events, giving predictions grounded in both live measurements and
        documented history.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="gs-overview-stats">
            <span class="gs-overview-stat">{_icon("database", 14)}&nbsp;2 Data Sources</span>
            <span class="gs-overview-stat">{_icon("hash", 14)}&nbsp;34 Engineered Features</span>
            <span class="gs-overview-stat">{_icon("cpu", 14)}&nbsp;KNN Model</span>
            <span class="gs-overview-stat">{_icon("brain", 14)}&nbsp;SHAP Explainability</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 3 — CORE FEATURES
# ============================================================

with st.container(border=True, key="section-features"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("zap", 20)} Core Features</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">What GeoSlide brings together in one dashboard</div>',
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3, gap="medium")
    with f1:
        _feature_card(
            "layers", "ds-chip-brand", "34 Engineered Features",
            "Environmental and geological inputs engineered from sensor and terrain data.",
            "feature-card-0",
        )
    with f2:
        _feature_card(
            "cpu", "ds-chip-accent", "KNN Prediction Model",
            "A k-Nearest Neighbors classifier trained to estimate landslide risk.",
            "feature-card-1",
        )
    with f3:
        _feature_card(
            "brain", "ds-chip-amber", "Explainable AI",
            "Every prediction is broken down with SHAP so results are transparent, not a black box.",
            "feature-card-2",
        )

    st.write("")
    f4, f5, f6 = st.columns(3, gap="medium")
    with f4:
        _feature_card(
            "monitor", "ds-chip-brand", "Interactive Dashboard",
            "A Streamlit multi-page app for prediction, explainability, mapping, and analytics.",
            "feature-card-3",
        )
    with f5:
        _feature_card(
            "globe", "ds-chip-accent", "Historical Map",
            "Explore NASA's Global Landslide Catalog on an interactive world map.",
            "feature-card-4",
        )
    with f6:
        _feature_card(
            "bar-chart", "ds-chip-amber", "Dataset Analytics",
            "Inspect feature distributions, correlations, and dataset statistics.",
            "feature-card-5",
        )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 4 — TECHNOLOGY STACK
# ============================================================

with st.container(border=True, key="section-techstack"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("code", 20)} Technology Stack</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">The tools GeoSlide is built with</div>',
        unsafe_allow_html=True,
    )
    _badge_row(
        [
            ("code", "Python"),
            ("zap", "FastAPI"),
            ("monitor", "Streamlit"),
            ("cpu", "Scikit-learn"),
            ("brain", "SHAP"),
            ("bar-chart", "Plotly"),
            ("globe", "Folium"),
            ("table", "Pandas"),
            ("database", "Joblib"),
        ]
    )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 5 — MACHINE LEARNING PIPELINE
# ============================================================

with st.container(border=True, key="section-pipeline"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("git-branch", 20)} Machine Learning Pipeline</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">From raw data to an explained prediction</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        _pipeline_row_html(
            [
                ("layers", "Dataset", "Sensor and historical landslide records collected for training.", 1),
                ("settings", "Preprocessing", "Clean, encode, and prepare the raw data for modeling.", 2),
                ("hash", "Feature Engineering", "Derive 34 engineered features from raw environmental inputs.", 3),
            ]
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        _pipeline_row_html(
            [
                ("search", "KNN Prediction", "Run the k-Nearest Neighbors model to estimate risk.", 4),
                ("brain", "SHAP Explainability", "Break down each prediction into per-feature contributions.", 5),
                ("monitor", "Interactive Dashboard", "Visualize predictions, maps, and analytics in one place.", 6),
            ]
        ),
        unsafe_allow_html=True,
    )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 6 — FUTURE ENHANCEMENTS
# ============================================================

with st.container(border=True, key="section-roadmap"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("sparkles", 20)} Future Enhancements</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">What\'s on the roadmap — planned, not yet built</div>',
        unsafe_allow_html=True,
    )

    r1, r2 = st.columns(2, gap="medium")
    with r1:
        _roadmap_card(
            "globe", "ds-chip-brand", "Real-Time Satellite Data Integration",
            "Incorporate live satellite feeds for continuous, up-to-the-minute risk monitoring.",
            "roadmap-card-0",
        )
    with r2:
        _roadmap_card(
            "smartphone", "ds-chip-accent", "Mobile Companion App",
            "Bring predictions, alerts, and the historical map to a native mobile experience.",
            "roadmap-card-1",
        )

    st.write("")
    r3, r4 = st.columns(2, gap="medium")
    with r3:
        _roadmap_card(
            "zap", "ds-chip-amber", "Automated Risk Alerts",
            "Push notifications when risk crosses a critical threshold for a monitored area.",
            "roadmap-card-2",
        )
    with r4:
        _roadmap_card(
            "cpu", "ds-chip-brand", "Multi-Region Model Tuning",
            "Fine-tune models for region-specific soil, terrain, and climate patterns.",
            "roadmap-card-3",
        )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 7 — DEVELOPER
# ============================================================

with st.container(border=True, key="section-developer"):
    st.markdown(
        f'<div class="gs-developer-avatar">{_icon("user", 28)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="gs-developer-label">Developer</div>', unsafe_allow_html=True)
    st.markdown('<div class="gs-developer-name">Kritartha Kakati</div>', unsafe_allow_html=True)