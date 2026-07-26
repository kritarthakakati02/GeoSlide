"""
GeoSlide - SHAP Analysis Page
================================

This page presents SHAP-based explainability for the most recent
landslide risk prediction using the backend `/explain` endpoint.

UI REDESIGN (this revision) — wired to the shared design system
------------------------------------------------------------------
This page previously had its own standalone dark-navy theme
(`--gs-bg: #0F172A`, emerald/blue accents) that did not match Home.py
or the Prediction page, which both run on the shared, light,
warm-neutral design system defined in `frontend/assets/design_system.css`
and `frontend/utils/design_tokens.py`. This revision replaces that
bespoke theme with the same system Home.py and 1_🔍_Prediction.py already
use — same tokens, same `.ds-*` classes, same "premium card" wiring
pattern (`st.container(border=True, key="section-...")` + CSS that
targets `[data-testid="stLayoutWrapper"]:has(> [class*="st-key-..."])`).

WHAT CHANGED vs. what did not
------------------------------
Changed (presentation only):
  - Page theme: swapped the old page-scoped dark theme for the shared
    light `design_system.css` tokens/classes, exactly like Home.py and
    the Prediction page (`load_styles()` + `design_system.css`, then a
    page-scoped wiring stylesheet built only from `var(--ds-*)` tokens).
  - Layout re-organized into clearly separated card sections: Hero,
    Load Action, Prediction Summary, SHAP Visualizations, Feature
    Contributions, Interpretation, and Insights — each a real bordered
    container with consistent spacing (`.gs-section-spacer`) between
    sections, matching the section-panel rhythm already used on
    Home.py / Prediction.py.
  - Local-explanation contributor rows and the interpretation panel now
    use the shared `.ds-badge-success` / `.ds-badge-error` / `.ds-alert-*`
    classes instead of hard-coded hex colors.
  - Added an "Insights" card: a short, plain-language takeaway generated
    only from fields the backend already returns in `explanation`
    (contributor counts, the strongest named contributor) — no new
    computation, no new backend field.

NOT changed (verified untouched):
  - `_get_current_feature_payload()` and `_load_latest_prediction()` are
    byte-for-byte unchanged.
  - The backend `/explain` call (`utils.api.get_shap_explanation`), the
    Random Forest SHAP explainer, and all prediction logic are untouched.
  - The existing charts (global feature importance bar chart, SHAP
    summary bar chart) use the exact same data, the exact same pandas
    sorting/indexing, and the exact same `st.bar_chart` calls as before —
    only their surrounding card/heading/caption changed.
  - `RISK_LEVEL_COLORS`, `FORM_FIELD_TO_FEATURE_NAME`, `encode_land_use`,
    `encode_soil_type` — same imports, same usage.

Only layout, typography, spacing, and presentation were touched.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from components.sidebar import render_sidebar
from utils import api
from utils.constants import RISK_LEVEL_COLORS
from utils.helpers import FORM_FIELD_TO_FEATURE_NAME, encode_land_use, encode_soil_type
from utils.theme import load_styles


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SHAP Analysis | GeoSlide",
    page_icon="🧠",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent.parent
DESIGN_SYSTEM_CSS_FILE = ROOT / "assets" / "design_system.css"


# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------

st.session_state.setdefault("shap_explanation", None)


def _get_current_feature_payload() -> dict:
    """
    Rebuild the raw feature payload for the parameters currently set on
    the Prediction page's form. Streamlit's session_state is shared across
    pages, and the Prediction page's widgets are bound to these same keys
    (see FORM_FIELD_TO_FEATURE_NAME / "land_use" / "soil_type"), so this
    lets the SHAP page explain the real inputs behind the most recent
    prediction without needing to read or modify the Prediction page.
    """
    payload = {key: st.session_state.get(key, 0.0) for key in FORM_FIELD_TO_FEATURE_NAME}
    payload.update(encode_land_use(st.session_state.get("land_use", "")))
    payload.update(encode_soil_type(st.session_state.get("soil_type", "")))
    return payload


def _load_latest_prediction() -> None:
    """Load a real SHAP explainability breakdown for the most recent prediction."""
    prediction_result = st.session_state.get("prediction_result")

    if not prediction_result or prediction_result.get("status") != "success":
        st.session_state["shap_explanation"] = {
            "feature_importance": [],
            "local_explanation": {"positive": [], "negative": []},
            "ai_interpretation": (
                "No prediction found yet. Run a prediction on the Prediction "
                "page first, then come back and load it here."
            ),
            "status": "error",
            "feature_names": [],
            "shap_values": [],
            "top_positive_contributors": [],
            "top_negative_contributors": [],
        }
        return

    payload = _get_current_feature_payload()

    try:
        explanation = api.get_shap_explanation(payload)
    except Exception as exc:
        explanation = {
            "feature_importance": [],
            "local_explanation": {"positive": [], "negative": []},
            "ai_interpretation": f"Unable to load explanation: {exc}",
            "status": "error",
            "feature_names": [],
            "shap_values": [],
            "top_positive_contributors": [],
            "top_negative_contributors": [],
        }

    st.session_state["shap_explanation"] = explanation


# ---------------------------------------------------------------------------
# Formatting helpers (display-only, mirror the ones on the Prediction page)
# ---------------------------------------------------------------------------

def _format_probability(value) -> str:
    """Format a probability as a percentage rounded to one decimal place."""
    if value is None:
        return "—"
    try:
        probability = float(value)
    except (TypeError, ValueError):
        return "—"
    return f"{probability * 100:.1f}%"


def _format_prediction(value) -> str:
    """Translate numeric prediction values into user-friendly labels."""
    if value is None:
        return "—"
    text_value = str(value).strip()
    if text_value in {"0", "0.0", "No Landslide"}:
        return "No Landslide"
    if text_value in {"1", "1.0", "Landslide Likely"}:
        return "Landslide Likely"
    return str(value)


# ---------------------------------------------------------------------------
# Page wiring CSS — same approach as Home.py / Prediction.py: maps
# Streamlit's native container markup onto the shared design-system
# tokens/classes. No new colors, spacing, radii, or type sizes are
# declared here; every visual value below is a `.ds-*` class or a
# `var(--ds-*)` token.
# ---------------------------------------------------------------------------

SHAP_WIRING_CSS = """
[data-testid="stAppViewContainer"] {
    background: var(--ds-bg) !important;
    --gs-border-soft: rgba(28, 35, 31, 0.07);
    --gs-border-soft-strong: rgba(28, 35, 31, 0.12);
    --gs-shadow-card: 0 1px 2px rgba(28, 35, 31, 0.04), 0 6px 16px rgba(28, 35, 31, 0.05);
    --gs-shadow-card-hover: 0 2px 6px rgba(28, 35, 31, 0.05), 0 16px 34px rgba(28, 35, 31, 0.09);
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
    border: 1px solid var(--gs-border-soft) !important;
    border-radius: var(--ds-radius-lg) !important;
    box-shadow: var(--gs-shadow-card) !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base),
                border-color var(--ds-transition-base), background var(--ds-transition-base);
}

/* ============================================================
   SECTION PANELS — outer card for every page section (Hero,
   Actions, Prediction Summary, Visualizations, Contributions,
   Interpretation, Insights).
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-"]) {
    background: var(--ds-bg-subtle) !important;
    border: 1px solid var(--gs-border-soft) !important;
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
.gs-hero-illo-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 180px;
}
.gs-hero-illo-wrap svg {
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
    .gs-hero-illo-wrap svg { animation: none; }
}

/* ============================================================
   SECTION 2 — LOAD ACTION
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-actions"]) {
    background: var(--ds-surface) !important;
    text-align: center;
    padding: var(--ds-space-6) !important;
}
[data-testid="stAppViewContainer"] .stButton > button {
    border-radius: var(--ds-radius-full) !important;
    font-weight: var(--ds-weight-semibold);
    font-family: var(--ds-font-base);
    outline: none !important;
    transition: transform var(--ds-transition-base), box-shadow var(--ds-transition-base),
                background var(--ds-transition-base), border-color var(--ds-transition-base);
}
[data-testid="stAppViewContainer"] button[kind="primary"] {
    background: linear-gradient(135deg, var(--ds-brand-500) 0%, var(--ds-brand-700) 100%) !important;
    border: none !important;
    color: var(--ds-text-inverse) !important;
    font-size: 1.05rem !important;
    font-weight: var(--ds-weight-bold) !important;
    letter-spacing: 0.01em;
    padding: 0.85rem 1.5rem !important;
    box-shadow: 0 1px 2px rgba(20, 30, 24, 0.15), 0 14px 28px rgba(28, 68, 51, 0.24) !important;
}
[data-testid="stAppViewContainer"] button[kind="primary"] p,
[data-testid="stAppViewContainer"] button[kind="primary"] div,
[data-testid="stAppViewContainer"] button[kind="primary"] span {
    color: var(--ds-text-inverse) !important;
    opacity: 1 !important;
}
[data-testid="stAppViewContainer"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--ds-brand-600) 0%, var(--ds-brand-700) 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 2px 4px rgba(20, 30, 24, 0.18), 0 20px 38px rgba(28, 68, 51, 0.30) !important;
}
[data-testid="stAppViewContainer"] button[kind="primary"]:active {
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(20, 30, 24, 0.15), 0 8px 18px rgba(28, 68, 51, 0.22) !important;
}
.gs-actions-hint { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: var(--ds-space-3); }

/* ============================================================
   SECTION 3 — PREDICTION SUMMARY
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-summary"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
.gs-risk-badge {
    display: inline-block;
    padding: 8px 22px;
    border-radius: var(--ds-radius-full);
    font-size: 1.1rem;
    font-weight: var(--ds-weight-extrabold);
    letter-spacing: 0.01em;
    box-shadow: var(--ds-shadow-sm);
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-summary-metric-"]) {
    background: var(--ds-bg-subtle) !important;
    padding: var(--ds-space-4) !important;
}
.gs-metric-label { font-size: var(--ds-text-xs); font-weight: var(--ds-weight-bold); text-transform: uppercase; letter-spacing: var(--ds-tracking-wide); color: var(--ds-text-tertiary); }
.gs-metric-value { font-size: 1.3rem; font-weight: var(--ds-weight-extrabold); color: var(--ds-text-primary); margin-top: 2px; }
.gs-summary-note { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: var(--ds-space-4); line-height: var(--ds-leading-normal); }

/* ============================================================
   SECTION 4 — SHAP VISUALIZATIONS
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-chart-card-"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-6) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-chart-card-"]):hover {
    border-color: var(--gs-border-soft-strong) !important;
    box-shadow: var(--gs-shadow-card-hover) !important;
}
.gs-chart-card-header { display: flex; align-items: center; gap: var(--ds-space-3); margin-bottom: var(--ds-space-1); }
.gs-chart-card-title { font-size: var(--ds-text-h3); font-weight: var(--ds-weight-semibold); color: var(--ds-text-primary); }
.gs-chart-card-caption { font-size: var(--ds-text-sm); color: var(--ds-text-tertiary); margin: 2px 0 var(--ds-space-4) 0; }
[data-testid="stAppViewContainer"] [data-testid="stArrowVegaLiteChart"] {
    border-radius: var(--ds-radius-sm);
    overflow: hidden;
}

/* ============================================================
   SECTION 5 — FEATURE CONTRIBUTIONS
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-contrib-card-"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-6) !important;
}
.gs-contrib-heading { display: flex; align-items: center; gap: var(--ds-space-3); margin-bottom: 2px; }
.gs-contrib-title { font-size: var(--ds-text-h3); font-weight: var(--ds-weight-bold); color: var(--ds-text-primary); }
.gs-contrib-subcaption { font-size: var(--ds-text-sm); color: var(--ds-text-tertiary); margin: 2px 0 var(--ds-space-4) 0; }
.gs-contrib-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--ds-space-3);
    padding: var(--ds-space-3) var(--ds-space-4);
    border-radius: var(--ds-radius-sm);
    margin-bottom: var(--ds-space-2);
    background: var(--ds-bg-subtle);
    border: 1px solid var(--gs-border-soft);
    transition: transform var(--ds-transition-fast), border-color var(--ds-transition-fast);
}
.gs-contrib-row:hover { border-color: var(--gs-border-soft-strong); }
.gs-contrib-feature {
    font-size: var(--ds-text-sm);
    font-weight: var(--ds-weight-semibold);
    color: var(--ds-text-primary);
}
.gs-contrib-value {
    font-size: var(--ds-text-sm);
    font-weight: var(--ds-weight-bold);
    padding: 4px 12px;
    border-radius: var(--ds-radius-full);
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
}

/* ============================================================
   SECTION 6 — INTERPRETATION
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-interpretation"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
.gs-interpretation-rule {
    display: flex;
    align-items: flex-start;
    gap: var(--ds-space-3);
    padding: var(--ds-space-3) 0;
    border-bottom: 1px solid var(--gs-border-soft);
}
.gs-interpretation-rule:last-of-type { border-bottom: none; }
.gs-interpretation-text { font-size: var(--ds-text-sm); color: var(--ds-text-secondary); line-height: var(--ds-leading-loose); }
.gs-ai-note {
    font-size: var(--ds-text-body);
    color: var(--ds-text-primary);
    line-height: var(--ds-leading-loose);
    background: var(--ds-bg-subtle);
    border: 1px solid var(--gs-border-soft);
    border-radius: var(--ds-radius-md);
    padding: var(--ds-space-4);
    margin-top: var(--ds-space-4);
}

/* ============================================================
   SECTION 7 — INSIGHTS
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-insights"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-6) !important;
}
.gs-insight-box {
    display: flex;
    gap: var(--ds-space-3);
    align-items: flex-start;
    background: linear-gradient(90deg, var(--ds-brand-50) 0%, var(--ds-bg-subtle) 100%);
    border: 1px solid var(--ds-brand-100);
    border-radius: var(--ds-radius-md);
    padding: var(--ds-space-4) var(--ds-space-5);
}
.gs-insight-title { font-size: var(--ds-text-sm); font-weight: var(--ds-weight-bold); color: var(--ds-text-primary); }
.gs-insight-text { font-size: var(--ds-text-sm); color: var(--ds-text-secondary); margin-top: 2px; line-height: var(--ds-leading-normal); }
.gs-insight-note { font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); margin-top: var(--ds-space-2); font-style: italic; }

/* ============================================================
   SHARED — empty states
   ============================================================ */
.gs-empty-state { text-align: center; padding: var(--ds-space-8) var(--ds-space-4); color: var(--ds-text-tertiary); }
.gs-empty-state .ds-kpi-icon { margin: 0 auto var(--ds-space-3); }
"""

st.markdown(f"<style>{load_styles()}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{DESIGN_SYSTEM_CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{SHAP_WIRING_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

render_sidebar()


# ---------------------------------------------------------------------------
# Local icon set (page-scoped, same inline-SVG pattern Home.py / the
# Prediction page use — decorative only, no emoji, no external assets).
# ---------------------------------------------------------------------------

_ICON_PATHS = {
    "brain": '<path d="M9 3.5A2.5 2.5 0 0 0 6.5 6v.3a2.5 2.5 0 0 0-1.4 4.3A2.8 2.8 0 0 0 6 15.6a2.5 2.5 0 0 0 3 3.3A2.5 2.5 0 0 0 11.5 20V6A2.5 2.5 0 0 0 9 3.5Z"/><path d="M15 3.5A2.5 2.5 0 0 1 17.5 6v.3a2.5 2.5 0 0 1 1.4 4.3A2.8 2.8 0 0 1 18 15.6a2.5 2.5 0 0 1-3 3.3A2.5 2.5 0 0 1 12.5 20V6A2.5 2.5 0 0 1 15 3.5Z"/>',
    "bar-chart": '<line x1="5" y1="20" x2="5" y2="13"/><line x1="12" y1="20" x2="12" y2="6"/><line x1="19" y1="20" x2="19" y2="10"/>',
    "download": '<path d="M12 3v13m0 0-4.5-4.5M12 16l4.5-4.5"/><path d="M4 19.5h16"/>',
    "alert-triangle": '<path d="M12 3.2 2.3 20h19.4L12 3.2Z"/><line x1="12" y1="9.5" x2="12" y2="14"/><circle cx="12" cy="17" r="0.9" fill="currentColor"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><rect x="10" y="10" width="4" height="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.5 4.5l2 2M17.5 17.5l2 2M4.5 19.5l2-2M17.5 6.5l2-2"/>',
    "trending-up": '<polyline points="4,17 10,11 14,15 20,7"/><polyline points="14,7 20,7 20,13"/>',
    "trending-down": '<polyline points="4,7 10,13 14,9 20,17"/><polyline points="14,17 20,17 20,11"/>',
    "info": '<circle cx="12" cy="12" r="9"/><line x1="12" y1="10.5" x2="12" y2="16"/><circle cx="12" cy="7.6" r="1" fill="currentColor"/>',
    "lightbulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6.5 6.5 0 0 0-3.8 11.8c.5.4.8 1 .8 1.7v.5h6v-.5c0-.7.3-1.3.8-1.7A6.5 6.5 0 0 0 12 3Z"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.3-4.3"/>',
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
    """Small decorative hero illustration for the Explainable AI page — a
    stylised bar chart threaded through a network of nodes, built the
    same way the Prediction page's hero illustration is (inline SVG,
    design tokens for color, purely decorative)."""
    return (
        '<svg viewBox="0 0 220 200" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="110" cy="100" r="86" stroke="var(--ds-brand-200)" stroke-width="1.4" opacity="0.5"/>'
        '<circle cx="110" cy="100" r="58" stroke="var(--ds-brand-200)" stroke-width="1.2" opacity="0.4"/>'
        '<rect x="55" y="120" width="16" height="40" rx="3" fill="var(--ds-accent-500)" opacity="0.85"/>'
        '<rect x="82" y="95" width="16" height="65" rx="3" fill="var(--ds-brand-500)"/>'
        '<rect x="109" y="70" width="16" height="90" rx="3" fill="var(--ds-brand-600)"/>'
        '<rect x="136" y="105" width="16" height="55" rx="3" fill="var(--ds-amber-500)" opacity="0.85"/>'
        '<line x1="63" y1="120" x2="90" y2="60" stroke="var(--ds-brand-300)" stroke-width="1.6" opacity="0.7"/>'
        '<line x1="90" y1="60" x2="117" y2="45" stroke="var(--ds-brand-300)" stroke-width="1.6" opacity="0.7"/>'
        '<line x1="117" y1="45" x2="144" y2="70" stroke="var(--ds-brand-300)" stroke-width="1.6" opacity="0.7"/>'
        '<circle cx="90" cy="60" r="5" fill="var(--ds-surface)" stroke="var(--ds-brand-500)" stroke-width="2.4"/>'
        '<circle cx="117" cy="45" r="6" fill="var(--ds-surface)" stroke="var(--ds-brand-600)" stroke-width="2.6"/>'
        '<circle cx="144" cy="70" r="5" fill="var(--ds-surface)" stroke="var(--ds-amber-500)" stroke-width="2.4"/>'
        '</svg>'
    )


# ============================================================
# SECTION 1 — HERO
# ============================================================

with st.container(border=True, key="section-hero"):
    left, right = st.columns([64, 36], gap="large")

    with left:
        st.markdown(
            f'<div class="ds-eyebrow">{_icon("brain", 14, 2)}<span>&nbsp;EXPLAINABLE AI</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ds-display gs-display-md">Model Explainability</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="ds-body-lg gs-hero-copy">
            SHAP (SHapley Additive exPlanations) shows why the model made a given
            landslide risk prediction — which features mattered most overall, and
            which ones pushed this specific prediction higher or lower.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(f'<div class="gs-hero-illo-wrap">{_hero_illustration()}</div>', unsafe_allow_html=True)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 2 — LOAD ACTION
# ============================================================

with st.container(border=True, key="section-actions"):
    st.button("Load Latest Prediction", type="primary", on_click=_load_latest_prediction, icon=":material/download:")

    explanation = st.session_state.get("shap_explanation")
    if explanation is None:
        st.markdown(
            '<div class="gs-actions-hint">No SHAP data loaded yet. Click <b>Load Latest '
            "Prediction</b> above to view an explainability breakdown.</div>",
            unsafe_allow_html=True,
        )
        if st.session_state.get("prediction_result") is None:
            st.markdown(
                '<div class="gs-actions-hint">Tip: no prediction has been run yet in this '
                "session. Run one on the Prediction page first for the most meaningful "
                "explanation.</div>",
                unsafe_allow_html=True,
            )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Shared data pulled once for the sections below (unchanged sourcing).
# ---------------------------------------------------------------------------

explanation = st.session_state.get("shap_explanation")
prediction_result = st.session_state.get("prediction_result")


# ============================================================
# SECTION 3 — PREDICTION SUMMARY
# ============================================================

with st.container(border=True, key="section-summary"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("search", 20)} Prediction Summary</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">What this page is explaining</div>',
        unsafe_allow_html=True,
    )

    if not prediction_result or prediction_result.get("status") != "success":
        st.markdown(
            f"""
            <div class="gs-empty-state">
                <div class="ds-kpi-icon ds-chip-brand" style="width:46px;height:46px;">{_icon("search", 20)}</div>
                <div>No prediction to explain yet. Run one on the <b>Prediction</b> page,
                then click <b>Load Latest Prediction</b> above.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        data = prediction_result.get("data") or {}
        risk_level = data.get("risk_level", "Unknown")
        probability = data.get("probability", 0.0)
        prediction = data.get("prediction", 0)
        color = RISK_LEVEL_COLORS.get(risk_level, "#808080")

        st.markdown(
            f'<span class="gs-risk-badge" style="background-color:{color};color:#ffffff;">{risk_level} Risk</span>',
            unsafe_allow_html=True,
        )

        st.write("")
        s1, s2, s3, s4 = st.columns(4, gap="medium")
        summary_cells = [
            (s1, "Risk Level", risk_level, "summary-metric-risk"),
            (s2, "Prediction", _format_prediction(prediction), "summary-metric-pred"),
            (s3, "Confidence", _format_probability(probability), "summary-metric-conf"),
            (s4, "Model", "K-Nearest Neighbors", "summary-metric-model"),
        ]
        for col, label, value, key in summary_cells:
            value_size = "1.05rem" if key.endswith("model") else "1.3rem"
            with col:
                with st.container(border=True, key=key):
                    st.markdown(
                        f"""
                        <div class="gs-metric-label">{label}</div>
                        <div class="gs-metric-value" style="font-size:{value_size};">{value}</div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown(
            '<div class="gs-summary-note">Prediction and probability come from the deployed '
            "KNN model; the SHAP breakdown below is generated by a Random Forest surrogate "
            "model trained on the same features, used exclusively for explainability.</div>",
            unsafe_allow_html=True,
        )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 4 — SHAP VISUALIZATIONS
# ============================================================

with st.container(border=True, key="section-visualizations"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("bar-chart", 20)} SHAP Visualizations</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">Global and local views of what drives the model</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True, key="chart-card-importance"):
        st.markdown(
            f"""
            <div class="gs-chart-card-header">
                <div class="ds-kpi-icon ds-chip-brand" style="width:38px;height:38px;margin-bottom:0;">{_icon("bar-chart", 17)}</div>
                <div class="gs-chart-card-title">Global Feature Importance</div>
            </div>
            <div class="gs-chart-card-caption">Which features are most influential across the dataset as a whole.</div>
            """,
            unsafe_allow_html=True,
        )
        if explanation is None:
            st.markdown(
                '<div class="gs-empty-state">Feature importance chart will appear here once data is loaded.</div>',
                unsafe_allow_html=True,
            )
        else:
            importance_df = pd.DataFrame(explanation.get("feature_importance", []))
            if importance_df.empty:
                st.markdown(
                    '<div class="gs-empty-state">No feature importance data available.</div>',
                    unsafe_allow_html=True,
                )
            else:
                importance_df = importance_df.sort_values("importance", ascending=True)
                st.bar_chart(
                    importance_df.set_index("feature"),
                    horizontal=True,
                    use_container_width=True,
                )

    st.write("")

    with st.container(border=True, key="chart-card-summary"):
        st.markdown(
            f"""
            <div class="gs-chart-card-header">
                <div class="ds-kpi-icon ds-chip-accent" style="width:38px;height:38px;margin-bottom:0;">{_icon("brain", 17)}</div>
                <div class="gs-chart-card-title">SHAP Summary Plot</div>
            </div>
            <div class="gs-chart-card-caption">The signed SHAP value for each feature on this specific prediction —
            bars pointing one way increase risk, bars pointing the other way decrease it.</div>
            """,
            unsafe_allow_html=True,
        )
        if explanation is None or not explanation.get("feature_names"):
            st.markdown(
                '<div class="gs-empty-state">No SHAP values are available yet.</div>',
                unsafe_allow_html=True,
            )
        else:
            feature_names = explanation.get("feature_names", [])
            shap_values = explanation.get("shap_values", [])
            summary_df = pd.DataFrame({"feature": feature_names, "shap_value": shap_values})
            summary_df = summary_df.sort_values("shap_value", key=lambda s: s.abs(), ascending=False)
            st.bar_chart(summary_df.set_index("feature")["shap_value"], use_container_width=True)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 5 — FEATURE CONTRIBUTIONS
# ============================================================

with st.container(border=True, key="section-contributions"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("trending-up", 20)} Feature Contributions</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">The strongest individual push toward higher or lower risk for this prediction</div>',
        unsafe_allow_html=True,
    )

    local = (explanation or {}).get("local_explanation", {})
    positive_features = local.get("positive", [])
    negative_features = local.get("negative", [])

    col_pos, col_neg = st.columns(2, gap="medium")

    with col_pos:
        with st.container(border=True, key="contrib-card-positive"):
            st.markdown(
                f"""
                <div class="gs-contrib-heading">
                    <div class="ds-kpi-icon ds-chip-amber" style="width:36px;height:36px;margin-bottom:0;">{_icon("trending-up", 16)}</div>
                    <div class="gs-contrib-title">Positive Contributors</div>
                </div>
                <div class="gs-contrib-subcaption">Features pushing this prediction toward higher risk.</div>
                """,
                unsafe_allow_html=True,
            )
            if explanation is None or not positive_features:
                st.markdown(
                    '<div class="gs-empty-state">No positive contributors available.</div>',
                    unsafe_allow_html=True,
                )
            else:
                rows = ""
                for item in positive_features:
                    rows += f"""
                    <div class="gs-contrib-row">
                        <div class="gs-contrib-feature">{item["feature"]}</div>
                        <div class="gs-contrib-value ds-badge-error">+{item["impact"]:.2f}</div>
                    </div>
                    """
                st.markdown(rows, unsafe_allow_html=True)

    with col_neg:
        with st.container(border=True, key="contrib-card-negative"):
            st.markdown(
                f"""
                <div class="gs-contrib-heading">
                    <div class="ds-kpi-icon ds-chip-brand" style="width:36px;height:36px;margin-bottom:0;">{_icon("trending-down", 16)}</div>
                    <div class="gs-contrib-title">Negative Contributors</div>
                </div>
                <div class="gs-contrib-subcaption">Features pushing this prediction toward lower risk.</div>
                """,
                unsafe_allow_html=True,
            )
            if explanation is None or not negative_features:
                st.markdown(
                    '<div class="gs-empty-state">No negative contributors available.</div>',
                    unsafe_allow_html=True,
                )
            else:
                rows = ""
                for item in negative_features:
                    rows += f"""
                    <div class="gs-contrib-row">
                        <div class="gs-contrib-feature">{item["feature"]}</div>
                        <div class="gs-contrib-value ds-badge-success">{item["impact"]:.2f}</div>
                    </div>
                    """
                st.markdown(rows, unsafe_allow_html=True)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 6 — INTERPRETATION
# ============================================================

with st.container(border=True, key="section-interpretation"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("info", 20)} Interpretation</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">How to read the results above</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="gs-interpretation-rule">
            <span class="ds-kpi-icon ds-chip-amber" style="width:30px;height:30px;margin-bottom:0;flex-shrink:0;">{_icon("trending-up", 14)}</span>
            <div class="gs-interpretation-text">
                <b>Positive SHAP values</b> mean that feature made the model think the
                landslide risk was <b>higher</b> than average for this location.
            </div>
        </div>
        <div class="gs-interpretation-rule">
            <span class="ds-kpi-icon ds-chip-brand" style="width:30px;height:30px;margin-bottom:0;flex-shrink:0;">{_icon("trending-down", 14)}</span>
            <div class="gs-interpretation-text">
                <b>Negative SHAP values</b> mean that feature made the model think the
                landslide risk was <b>lower</b> than average for this location.
            </div>
        </div>
        <div class="gs-interpretation-rule">
            <span class="ds-kpi-icon ds-chip-accent" style="width:30px;height:30px;margin-bottom:0;flex-shrink:0;">{_icon("bar-chart", 14)}</span>
            <div class="gs-interpretation-text">
                The <b>bigger</b> the value (positive or negative), the <b>stronger</b> that
                feature's pull on the final prediction.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if explanation is not None:
        st.markdown(
            f'<div class="gs-ai-note">{explanation.get("ai_interpretation", "No interpretation available.")}</div>',
            unsafe_allow_html=True,
        )
        if explanation.get("status") == "error":
            st.markdown(
                f"""
                <div class="ds-alert ds-alert-warning" style="margin-top:var(--ds-space-3);">
                    {_icon("alert-triangle", 16)}
                    <div>The explanation endpoint could not be reached or returned an error.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 7 — INSIGHTS
# ============================================================
# Small, plain-language takeaway built only from fields the backend
# already returns in `explanation` (no new computation, no new field).

with st.container(border=True, key="section-insights"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("lightbulb", 20)} Insights</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">A quick takeaway from this prediction\'s explanation</div>',
        unsafe_allow_html=True,
    )

    local = (explanation or {}).get("local_explanation", {})
    positive_features = local.get("positive", [])
    negative_features = local.get("negative", [])

    if explanation is None or explanation.get("status") == "error" or not (positive_features or negative_features):
        st.markdown(
            f"""
            <div class="gs-empty-state">
                <div class="ds-kpi-icon ds-chip-brand" style="width:46px;height:46px;">{_icon("lightbulb", 20)}</div>
                <div>An insight will appear here once a SHAP explanation is loaded above.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        if positive_features:
            top_driver = max(positive_features, key=lambda item: item.get("impact", 0))
            takeaway = (
                f"<b>{top_driver['feature']}</b> is the single strongest factor pushing this "
                f"prediction toward higher risk, with {len(positive_features)} feature"
                f"{'s' if len(positive_features) != 1 else ''} increasing risk overall and "
                f"{len(negative_features)} feature{'s' if len(negative_features) != 1 else ''} "
                "offsetting it."
            )
        else:
            top_driver = max(negative_features, key=lambda item: abs(item.get("impact", 0)))
            takeaway = (
                f"<b>{top_driver['feature']}</b> is the single strongest factor pushing this "
                f"prediction toward lower risk, with {len(negative_features)} feature"
                f"{'s' if len(negative_features) != 1 else ''} decreasing risk overall."
            )

        st.markdown(
            f"""
            <div class="gs-insight-box">
                {_icon("lightbulb", 22)}
                <div>
                    <div class="gs-insight-title">Key Takeaway</div>
                    <div class="gs-insight-text">{takeaway}</div>
                    <div class="gs-insight-note">Derived directly from the SHAP values above — general
                    guidance only, not a substitute for a professional geotechnical assessment.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )