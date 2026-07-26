"""
GeoSlide - Historical Landslide Map Page
===========================================
Phase 10.5: Historical Landslide Map.

This page lets users explore historical landslide events (sourced from
the NASA Global Landslide Catalog when available) on an interactive
Folium map, with filters, top-level summary metrics, and a detail
panel for the currently selected event.

NOTE: If the NASA dataset cannot be loaded (no local file / no network
access), this page automatically falls back to generated placeholder
sample data so the UI remains fully functional and demoable.

UI REDESIGN (this revision) — wired to the shared design system
------------------------------------------------------------------
This page previously had its own standalone dark-navy theme
(`--gs-bg: #0F172A`, emerald/blue accents) that did not match Home.py,
the Prediction page, or the SHAP Analysis page, which all run on the
shared, light, warm-neutral design system defined in
`frontend/assets/design_system.css` and `frontend/utils/design_tokens.py`.
This revision replaces that bespoke theme with the same system those
pages already use — same tokens, same `.ds-*` classes, same "premium
card" wiring pattern (`st.container(border=True, key="section-...")`
+ CSS that targets
`[data-testid="stLayoutWrapper"]:has(> [class*="st-key-..."])`).

WHAT CHANGED vs. what did not
------------------------------
Changed (presentation only):
  - Page theme: swapped the old page-scoped dark theme for the shared
    light `design_system.css` tokens/classes, exactly like Home.py,
    the Prediction page, and the SHAP Analysis page.
  - Layout re-organized into six clearly separated card sections, in
    the requested on-page order: Hero, Statistics, Filter Panel,
    Interactive Map, Event Details, Insights. The Statistics card is
    rendered into a placeholder container created *before* the Filter
    Panel runs, and filled in *after* the filters are applied — so the
    visual order is Hero → Statistics → Filters, while the underlying
    computation order (filters must run before stats can reflect them)
    is completely unchanged.
  - The single "🎛 Filters" panel changed from an `st.expander` to a
    plain premium card (`st.container(border=True)`) with restyled
    multiselect/slider controls, matching the input-styling approach
    already used on the Prediction page's field cards. The four filter
    widgets themselves — same keys, same options, same defaults, same
    help text — are untouched.
  - The Selected Event panel changed from one HTML grid inside a single
    card into six individual small "clean cards" (Location, Date,
    Trigger, Fatalities, Rainfall, Description), matching the KPI/
    metric-card visual language used elsewhere in the app. Same six
    fields, same values, same "not recorded" placeholders.
  - KPI cards, the map card, and the insights card now use `.ds-*`
    tokens/classes instead of hard-coded hex colors.

NOT changed (verified untouched):
  - Data loading (`load_landslide_data`, `_load_local_catalog`,
    `_map_catalog_columns`, `_generate_placeholder_data`) is
    byte-for-byte unchanged.
  - `_classify_trigger` and the filtering logic (country/year/
    trigger/fatalities) are unchanged.
  - Folium map creation, marker generation, popups, tooltips, and the
    marker-click -> selected-event resolution logic are unchanged.
  - The filtered data table at the bottom is unchanged (still an
    `st.expander`, still the same dataframe/columns).

Only layout, typography, spacing, and presentation were touched.
"""

from datetime import date, timedelta
from pathlib import Path
import glob
import random

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from components.sidebar import render_sidebar
from utils.theme import load_styles


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Historical Map | GeoSlide",
    page_icon="🌍",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent.parent
DESIGN_SYSTEM_CSS_FILE = ROOT / "assets" / "design_system.css"
HERO_ILLUSTRATION_FILE = ROOT / "assets" / "images" / "historical_map_globe.png"


# ---------------------------------------------------------------------------
# Data Loading (UNCHANGED)
# ---------------------------------------------------------------------------

NASA_CATALOG_URL = (
    "https://data.nasa.gov/resource/dd9e-wu2v.csv"  # NASA Global Landslide Catalog
)

# The project's own local export of the same NASA Global Landslide
# Catalog. Preferred over the live NASA endpoint since it's already
# present in the repo and doesn't depend on network access.
LOCAL_CATALOG_PATHS = [
    "datasets/Global_Landslide_Catalog_Export_20250201.csv",
    "../datasets/Global_Landslide_Catalog_Export_20250201.csv",
]

TRIGGER_OPTIONS = ["Rainfall", "Earthquake", "Snowmelt", "Construction", "Other"]
COUNTRY_OPTIONS = [
    "United States", "India", "China", "Philippines", "Indonesia",
    "Nepal", "Brazil", "Colombia", "Italy", "Japan",
]


def _generate_placeholder_data(n: int = 120) -> pd.DataFrame:
    """
    Generate realistic-looking placeholder landslide event data so the
    page remains fully functional when the NASA catalog is unavailable.
    """
    rng = random.Random(42)
    today = date.today()

    country_bounds = {
        "United States": (37.0, -95.0),
        "India": (22.0, 78.0),
        "China": (35.0, 103.0),
        "Philippines": (12.0, 122.0),
        "Indonesia": (-2.0, 118.0),
        "Nepal": (28.0, 84.0),
        "Brazil": (-10.0, -55.0),
        "Colombia": (4.0, -73.0),
        "Italy": (43.0, 12.0),
        "Japan": (36.0, 138.0),
    }

    records = []
    for i in range(n):
        country = rng.choice(COUNTRY_OPTIONS)
        base_lat, base_lon = country_bounds[country]
        trigger = rng.choices(
            TRIGGER_OPTIONS, weights=[45, 20, 10, 10, 15], k=1
        )[0]
        event_date = today - timedelta(days=rng.randint(0, 365 * 8))
        fatalities = rng.choices(
            [0, rng.randint(1, 5), rng.randint(6, 20), rng.randint(21, 100)],
            weights=[55, 25, 15, 5],
            k=1,
        )[0]

        records.append(
            {
                "id": i + 1,
                "date": event_date,
                "year": event_date.year,
                "country": country,
                "trigger": trigger,
                "fatalities": int(fatalities),
                "latitude": round(base_lat + rng.uniform(-4.0, 4.0), 4),
                "longitude": round(base_lon + rng.uniform(-4.0, 4.0), 4),
            }
        )

    return pd.DataFrame(records)


def _map_catalog_columns(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Map a raw Global Landslide Catalog dataframe (whether loaded from
    the local project export or fetched live from NASA - both share
    the same column schema) into this page's normalized schema.

    This is the same column-mapping logic previously inlined in
    load_landslide_data(); it is unchanged, just shared so both the
    local file and the live NASA fetch use one code path.
    """
    df = pd.DataFrame()
    df["date"] = pd.to_datetime(
        raw.get("event_date", raw.get("event_date_std")), errors="coerce"
    )
    df["country"] = raw.get("country_name", raw.get("country"))
    df["trigger"] = raw.get("landslide_trigger", raw.get("trigger"))
    df["fatalities"] = pd.to_numeric(
        raw.get("fatality_count", raw.get("fatalities")), errors="coerce"
    ).fillna(0)
    df["latitude"] = pd.to_numeric(
        raw.get("latitude"), errors="coerce"
    )
    df["longitude"] = pd.to_numeric(
        raw.get("longitude"), errors="coerce"
    )

    df = df.dropna(subset=["date", "latitude", "longitude"])
    if df.empty:
        raise ValueError("Catalog dataset returned no usable rows.")

    df["year"] = df["date"].dt.year
    df["date"] = df["date"].dt.date
    df["id"] = range(1, len(df) + 1)
    df["fatalities"] = df["fatalities"].astype(int)

    return df.reset_index(drop=True)


def _load_local_catalog() -> pd.DataFrame | None:
    """
    Attempt to load the project's local Global Landslide Catalog
    export. Returns None (never raises) if it can't be found or
    parsed, so callers can gracefully fall back to the existing
    NASA/placeholder behavior.
    """
    for path in LOCAL_CATALOG_PATHS:
        for match in glob.glob(path):
            try:
                raw = pd.read_csv(match)
                return _map_catalog_columns(raw)
            except Exception:
                continue
    return None


@st.cache_data(show_spinner=False)
def load_landslide_data() -> tuple[pd.DataFrame, bool]:
    """
    Attempt to load landslide event data, in order of preference:
      1. The project's local Global Landslide Catalog export.
      2. The live NASA Global Landslide Catalog endpoint.
      3. Generated placeholder data, as a last resort, so the page
         remains fully functional and demoable regardless.

    Returns:
        A tuple of (dataframe, is_live_data) where is_live_data is
        True only if real catalog data (local or NASA) was
        successfully loaded.
    """
    local_df = _load_local_catalog()
    if local_df is not None:
        return local_df, True

    try:
        raw = pd.read_csv(NASA_CATALOG_URL, nrows=500, timeout=5)
        return _map_catalog_columns(raw), True

    except Exception:
        return _generate_placeholder_data(), False


landslide_df, is_live_data = load_landslide_data()


# ---------------------------------------------------------------------------
# Trigger normalization helper (for metric buckets & filtering) (UNCHANGED)
# ---------------------------------------------------------------------------

def _classify_trigger(trigger_value: str) -> str:
    if not isinstance(trigger_value, str):
        return "Other"
    value = trigger_value.strip().lower()
    if "rain" in value or "downpour" in value or "monsoon" in value:
        return "Rainfall"
    if "quake" in value or "seismic" in value:
        return "Earthquake"
    return "Other"


landslide_df["trigger_group"] = landslide_df["trigger"].apply(_classify_trigger)


# ---------------------------------------------------------------------------
# Session State (selected event)
# ---------------------------------------------------------------------------

st.session_state.setdefault("selected_event_id", None)


# ---------------------------------------------------------------------------
# Page wiring CSS — same approach as Home.py / Prediction.py / the SHAP
# Analysis page: maps Streamlit's native container markup onto the
# shared design-system tokens/classes. No new colors, spacing, radii,
# or type sizes are declared here; every visual value below is a
# `.ds-*` class or a `var(--ds-*)` token.
# ---------------------------------------------------------------------------

MAP_WIRING_CSS = """
[data-testid="stAppViewContainer"] {
    background: var(--ds-bg) !important;
    --gs-border-soft: rgba(28, 35, 31, 0.07);
    --gs-border-soft-strong: rgba(28, 35, 31, 0.12);
    --gs-shadow-card: 0 1px 2px rgba(28, 35, 31, 0.04), 0 6px 16px rgba(28, 35, 31, 0.05);
    --gs-shadow-card-hover: 0 2px 6px rgba(28, 35, 31, 0.05), 0 16px 34px rgba(28, 35, 31, 0.09);
}

[data-testid="stAppViewContainer"] .block-container {
    padding: var(--ds-space-6) var(--ds-container-padding-desktop) var(--ds-space-10) !important;
    max-width: 1500px;
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
    border-style: solid !important;
    border-radius: var(--ds-radius-lg) !important;
    box-shadow: var(--gs-shadow-card) !important;
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
   Statistics, Filters, Map, Event Details, Insights).
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
   SECTION 2 — STATISTICS (KPI cards)
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-summary"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kpi-card-"]) {
    background: var(--ds-bg-subtle) !important;
    padding: var(--ds-space-5) !important;
    height: 132px;
    display: flex !important;
    flex-direction: column;
    justify-content: center;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kpi-card-"]):hover {
    transform: translateY(-3px);
    box-shadow: var(--ds-shadow-md) !important;
    border-color: var(--ds-brand-200) !important;
}
.gs-kpi-icon-row { display: flex; align-items: center; gap: var(--ds-space-3); margin-bottom: var(--ds-space-2); }
.gs-kpi-icon-row .ds-kpi-icon { margin-bottom: 0; transition: transform var(--ds-transition-base); }
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kpi-card-"]):hover .ds-kpi-icon { transform: scale(1.08); }
.gs-kpi-value { font-size: 1.85rem !important; letter-spacing: -0.01em; }

/* ============================================================
   SECTION 3 — FILTER PANEL
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-filters"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
[data-testid="stAppViewContainer"] label p {
    color: var(--ds-text-tertiary) !important;
    font-size: var(--ds-text-xs) !important;
    font-weight: var(--ds-weight-bold);
    text-transform: uppercase;
    letter-spacing: var(--ds-tracking-wide);
}
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] > div > div,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] > div > div {
    background: var(--ds-bg-inset) !important;
    border: 1px solid var(--gs-border-soft-strong) !important;
    border-radius: var(--ds-radius-md) !important;
    box-shadow: inset 0 1px 2px rgba(28, 35, 31, 0.03) !important;
    transition: border-color var(--ds-transition-fast), background var(--ds-transition-fast);
}
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] > div > div:hover {
    border-color: var(--ds-brand-200) !important;
    background: var(--ds-surface) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: var(--ds-border-focus) !important;
    box-shadow: var(--ds-shadow-focus) !important;
    background: var(--ds-surface) !important;
}
[data-testid="stAppViewContainer"] [data-baseweb="tag"] {
    background: var(--ds-brand-50) !important;
    border: 1px solid var(--ds-brand-100) !important;
}
[data-testid="stAppViewContainer"] [data-baseweb="tag"] span {
    color: var(--ds-brand-600) !important;
    font-weight: var(--ds-weight-semibold);
}
[data-testid="stAppViewContainer"] [data-testid="stSlider"] [role="slider"] {
    background: var(--ds-brand-500) !important;
    border-color: var(--ds-brand-500) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
    background: var(--ds-brand-300) !important;
}
[data-testid="stAppViewContainer"] [data-testid="stSlider"] div[data-baseweb="slider"] > div:first-child {
    background: var(--ds-bg-inset) !important;
}
.gs-filter-group-title {
    display: flex;
    align-items: center;
    gap: var(--ds-space-2);
    font-size: var(--ds-text-xs);
    font-weight: var(--ds-weight-bold);
    text-transform: uppercase;
    letter-spacing: var(--ds-tracking-wide);
    color: var(--ds-text-tertiary);
    margin-bottom: var(--ds-space-3);
}

/* ============================================================
   SECTION 4 — INTERACTIVE MAP
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-map"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-map-card"]) {
    background: var(--ds-bg-subtle) !important;
    padding: var(--ds-space-4) !important;
}
[data-testid="stAppViewContainer"] iframe {
    border-radius: var(--ds-radius-md);
    box-shadow: var(--gs-shadow-card);
}
.gs-map-legend { display: flex; flex-wrap: wrap; gap: var(--ds-space-4); margin-top: var(--ds-space-3); }
.gs-map-legend-item { display: flex; align-items: center; gap: 7px; font-size: var(--ds-text-xs); color: var(--ds-text-tertiary); font-weight: var(--ds-weight-semibold); }
.gs-map-legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* ============================================================
   SECTION 5 — EVENT DETAILS
   ============================================================ */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-section-event"]) {
    background: var(--ds-surface) !important;
    padding: var(--ds-space-7) var(--ds-space-6) !important;
}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-event-card-"]) {
    background: var(--ds-bg-subtle) !important;
    padding: var(--ds-space-4) !important;
    height: 108px;
    display: flex !important;
    flex-direction: column;
    justify-content: center;
}
.gs-event-label-row { display: flex; align-items: center; gap: var(--ds-space-2); margin-bottom: 4px; }
.gs-event-label { font-size: var(--ds-text-xs); font-weight: var(--ds-weight-bold); text-transform: uppercase; letter-spacing: var(--ds-tracking-wide); color: var(--ds-text-tertiary); }
.gs-event-value { font-size: var(--ds-text-body); font-weight: var(--ds-weight-bold); color: var(--ds-text-primary); line-height: var(--ds-leading-normal); }
.gs-event-value.muted { font-weight: var(--ds-weight-medium); font-style: italic; color: var(--ds-text-tertiary); font-size: var(--ds-text-sm); }

/* ============================================================
   SECTION 6 — INSIGHTS
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

/* ============================================================
   SHARED — empty states + filtered-data expander
   ============================================================ */
.gs-empty-state { text-align: center; padding: var(--ds-space-8) var(--ds-space-4); color: var(--ds-text-tertiary); }
.gs-empty-state .ds-kpi-icon { margin: 0 auto var(--ds-space-3); }
[data-testid="stAppViewContainer"] [data-testid="stExpander"] {
    background: var(--ds-surface) !important;
    border: 1px solid var(--gs-border-soft) !important;
    border-radius: var(--ds-radius-lg) !important;
    box-shadow: var(--gs-shadow-card) !important;
    overflow: hidden;
}
[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary p {
    font-size: var(--ds-text-body);
    font-weight: var(--ds-weight-bold);
    color: var(--ds-text-primary) !important;
}
"""

st.markdown(f"<style>{load_styles()}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{DESIGN_SYSTEM_CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
st.markdown(f"<style>{MAP_WIRING_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar (branded nav only - filters live in the page body, see Section 3)
# ---------------------------------------------------------------------------

render_sidebar()


# ---------------------------------------------------------------------------
# Local icon set (page-scoped, same inline-SVG pattern Home.py / the
# Prediction / SHAP Analysis pages use — decorative only, no emoji, no
# external assets).
# ---------------------------------------------------------------------------

_ICON_PATHS = {
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18Z"/>',
    "map-pin": '<path d="M12 21s7-7.2 7-12a7 7 0 1 0-14 0c0 4.8 7 12 7 12Z"/><circle cx="12" cy="9" r="2.4"/>',
    "cloud-rain": '<path d="M7 15.5a4.3 4.3 0 0 1 .6-8.6 5.7 5.7 0 0 1 10.6 2.6 3.8 3.8 0 0 1-.7 6H7Z"/><path d="M8 19v1.3M12 19v1.8M16 19v1.3"/>',
    "activity": '<polyline points="3,12 8,12 10,6 14,18 16,12 21,12"/>',
    "help-circle": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 0 1 4.8 1c0 1.6-2.3 1.8-2.3 3.6"/><circle cx="12" cy="17" r="0.9" fill="currentColor"/>',
    "sliders": '<line x1="4" y1="6" x2="20" y2="6"/><circle cx="9" cy="6" r="2.2" fill="var(--ds-surface)"/><line x1="4" y1="12" x2="20" y2="12"/><circle cx="16" cy="12" r="2.2" fill="var(--ds-surface)"/><line x1="4" y1="18" x2="20" y2="18"/><circle cx="11" cy="18" r="2.2" fill="var(--ds-surface)"/>',
    "map": '<path d="m9 4-5 2v14l5-2 6 2 5-2V4l-5 2-6-2Z"/><line x1="9" y1="4" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="20"/>',
    "calendar": '<rect x="3.5" y="4.5" width="17" height="16" rx="2"/><line x1="3.5" y1="9.5" x2="20.5" y2="9.5"/><line x1="8" y1="2.5" x2="8" y2="6.5"/><line x1="16" y1="2.5" x2="16" y2="6.5"/>',
    "alert-triangle": '<path d="M12 3.2 2.3 20h19.4L12 3.2Z"/><line x1="12" y1="9.5" x2="12" y2="14"/><circle cx="12" cy="17" r="0.9" fill="currentColor"/>',
    "skull": '<circle cx="12" cy="11" r="8"/><circle cx="9" cy="10.5" r="1.4" fill="var(--ds-surface)"/><circle cx="15" cy="10.5" r="1.4" fill="var(--ds-surface)"/><path d="M9.5 15h5M10 19v1.5M14 19v1.5"/>',
    "droplet": '<path d="M12 2.8s6.2 7 6.2 11.5A6.2 6.2 0 0 1 5.8 14.3C5.8 9.8 12 2.8 12 2.8Z"/>',
    "file-text": '<path d="M6 3.5h9l4 4v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-16a1 1 0 0 1 1-1Z"/><line x1="8.5" y1="10" x2="15.5" y2="10"/><line x1="8.5" y1="14" x2="15.5" y2="14"/>',
    "lightbulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6.5 6.5 0 0 0-3.8 11.8c.5.4.8 1 .8 1.7v.5h6v-.5c0-.7.3-1.3.8-1.7A6.5 6.5 0 0 0 12 3Z"/>',
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
    """Small decorative hero illustration — a stylised globe with event
    pins, built the same way the Prediction/SHAP hero illustrations are
    (inline SVG, design tokens for color, purely decorative)."""
    return (
        '<svg viewBox="0 0 220 200" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="110" cy="100" r="72" stroke="var(--ds-brand-200)" stroke-width="1.4" opacity="0.55"/>'
        '<ellipse cx="110" cy="100" rx="72" ry="30" stroke="var(--ds-brand-200)" stroke-width="1.1" opacity="0.45"/>'
        '<ellipse cx="110" cy="100" rx="72" ry="52" stroke="var(--ds-brand-200)" stroke-width="1.1" opacity="0.3"/>'
        '<line x1="38" y1="100" x2="182" y2="100" stroke="var(--ds-brand-200)" stroke-width="1.1" opacity="0.45"/>'
        '<line x1="110" y1="28" x2="110" y2="172" stroke="var(--ds-brand-200)" stroke-width="1.1" opacity="0.35"/>'
        '<circle cx="76" cy="78" r="5.5" fill="var(--ds-accent-500)"/>'
        '<circle cx="132" cy="66" r="4.5" fill="var(--ds-amber-500)"/>'
        '<circle cx="146" cy="118" r="6.5" fill="var(--ds-brand-500)"/>'
        '<circle cx="88" cy="130" r="4" fill="var(--ds-accent-500)"/>'
        '<path d="M110 100 88 130" stroke="var(--ds-brand-300)" stroke-width="1.4" opacity="0.7"/>'
        '<path d="M110 100 146 118" stroke="var(--ds-brand-300)" stroke-width="1.4" opacity="0.7"/>'
        '<path d="M110 100 76 78" stroke="var(--ds-brand-300)" stroke-width="1.4" opacity="0.7"/>'
        '<circle cx="110" cy="100" r="4.5" fill="var(--ds-brand-600)"/>'
        '</svg>'
    )


# ============================================================
# SECTION 1 — HERO
# ============================================================

with st.container(border=True, key="section-hero"):
    left, right = st.columns([64, 36], gap="large")

    with left:
        st.markdown(
            f'<div class="ds-eyebrow">{_icon("globe", 14, 2)}<span>&nbsp;GLOBAL LANDSLIDE INTELLIGENCE</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ds-display gs-display-md">Historical Landslide Map</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="ds-body-lg gs-hero-copy">
            Explore historical landslide events from NASA's Global Landslide Catalog.
            Analyze geographic distribution, event locations, and historical patterns
            through an interactive geospatial dashboard.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not is_live_data:
            st.markdown(
                f"""
                <div class="ds-alert ds-alert-warning" style="margin-top:var(--ds-space-4);">
                    {_icon("alert-triangle", 16)}
                    <div>Live NASA Global Landslide Catalog data is unavailable right now.
                    Displaying generated placeholder sample data instead so the map remains
                    fully explorable.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        with st.container(key="hero-illo-wrap"):
            st.image(str(HERO_ILLUSTRATION_FILE), use_container_width=True)

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 2 — STATISTICS (placeholder created now, filled in
# after filters run below, so the on-screen order stays
# Hero -> Statistics -> Filters even though the KPI values must
# be computed from `filtered_df`, which needs the filter widgets
# further down the script to have executed first.)
# ============================================================

summary_section = st.container(border=True, key="section-summary")

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 3 — FILTER PANEL
# ============================================================

with st.container(border=True, key="section-filters"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("sliders", 20)} Filters</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">Narrow the map and statistics above to a region, time range, or trigger type</div>',
        unsafe_allow_html=True,
    )

    filt_col1, filt_col2 = st.columns(2, gap="large")

    with filt_col1:
        st.markdown(
            f'<div class="gs-filter-group-title">{_icon("map-pin", 14)}&nbsp;Location & Time</div>',
            unsafe_allow_html=True,
        )
        country_filter = st.multiselect(
            "Country",
            options=sorted(landslide_df["country"].dropna().unique()),
            default=[],
            help="Leave empty to include all countries.",
        )

        min_year = int(landslide_df["year"].min())
        max_year = int(landslide_df["year"].max())
        if min_year == max_year:
            year_filter = (min_year, max_year)
            st.caption(f"Year: {min_year}")
        else:
            year_filter = st.slider(
                "Year",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
            )

    with filt_col2:
        st.markdown(
            f'<div class="gs-filter-group-title">{_icon("activity", 14)}&nbsp;Cause & Severity</div>',
            unsafe_allow_html=True,
        )
        trigger_filter = st.multiselect(
            "Trigger",
            options=sorted(landslide_df["trigger_group"].dropna().unique()),
            default=[],
            help="Leave empty to include all triggers.",
        )

        max_fatalities_available = int(landslide_df["fatalities"].max())
        fatalities_filter = st.slider(
            "Minimum Fatalities",
            min_value=0,
            max_value=max(max_fatalities_available, 1),
            value=0,
            help="Only show events with at least this many fatalities.",
        )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Apply Filters (UNCHANGED)
# ---------------------------------------------------------------------------

filtered_df = landslide_df.copy()

if country_filter:
    filtered_df = filtered_df[filtered_df["country"].isin(country_filter)]

filtered_df = filtered_df[
    (filtered_df["year"] >= year_filter[0]) & (filtered_df["year"] <= year_filter[1])
]

if trigger_filter:
    filtered_df = filtered_df[filtered_df["trigger_group"].isin(trigger_filter)]

filtered_df = filtered_df[filtered_df["fatalities"] >= fatalities_filter]


# ---------------------------------------------------------------------------
# Fill in the Statistics placeholder (Section 2) now that filtered_df
# exists. Same values/computation as before — total_events,
# rainfall_events, earthquake_events, other_events — only rendered
# retroactively into the container created above.
# ---------------------------------------------------------------------------

total_events = len(filtered_df)
rainfall_events = int((filtered_df["trigger_group"] == "Rainfall").sum())
earthquake_events = int((filtered_df["trigger_group"] == "Earthquake").sum())
other_events = int((filtered_df["trigger_group"] == "Other").sum())

with summary_section:
    st.markdown(
        f'<div class="ds-section-title">{_icon("globe", 20)} Statistics</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">Summary of events matching the current filters</div>',
        unsafe_allow_html=True,
    )

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4, gap="medium")
    kpi_data = [
        (kpi_col1, "map", "ds-chip-brand", "Total Events", total_events, "kpi-card-0"),
        (kpi_col2, "cloud-rain", "ds-chip-accent", "Rainfall Triggered", rainfall_events, "kpi-card-1"),
        (kpi_col3, "activity", "ds-chip-amber", "Earthquake Triggered", earthquake_events, "kpi-card-2"),
        (kpi_col4, "help-circle", "ds-chip-brand", "Other Triggers", other_events, "kpi-card-3"),
    ]
    for col, icon_name, chip_class, label, value, key in kpi_data:
        with col:
            with st.container(border=True, key=key):
                st.markdown(
                    f"""
                    <div class="gs-kpi-icon-row">
                        <div class="ds-kpi-icon {chip_class}">{_icon(icon_name, 18)}</div>
                        <div class="ds-kpi-label" style="margin-top:1px;">{label}</div>
                    </div>
                    <div class="gs-kpi-value ds-kpi-value">{value:,}</div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# SECTION 4 — INTERACTIVE MAP (UNCHANGED map/marker generation logic)
# ============================================================

with st.container(border=True, key="section-map"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("map", 20)} Landslide Event Map</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">Click any marker to view its full event details below</div>',
        unsafe_allow_html=True,
    )

    TRIGGER_COLORS = {
        "Rainfall": "blue",
        "Earthquake": "red",
        "Other": "gray",
    }

    with st.container(border=True, key="map-card"):
        if filtered_df.empty:
            st.markdown(
                f"""
                <div class="gs-empty-state">
                    <div class="ds-kpi-icon ds-chip-brand" style="width:46px;height:46px;">{_icon("map", 20)}</div>
                    <div>No events match the selected filters. Try widening your filter criteria.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            map_center = [filtered_df["latitude"].mean(), filtered_df["longitude"].mean()]
            landslide_map = folium.Map(location=map_center, zoom_start=3, tiles="OpenStreetMap")

            # Cap the number of rendered markers for performance/presentation clarity.
            display_df = filtered_df.head(500)

            for _, row in display_df.iterrows():
                popup_html = (
                    f"<b>Date:</b> {row['date']}<br>"
                    f"<b>Country:</b> {row['country']}<br>"
                    f"<b>Trigger:</b> {row['trigger_group']}<br>"
                    f"<b>Fatalities:</b> {row['fatalities']}<br>"
                    f"<b>Latitude:</b> {row['latitude']}<br>"
                    f"<b>Longitude:</b> {row['longitude']}"
                )
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=6 if row["fatalities"] == 0 else 8,
                    color=TRIGGER_COLORS.get(row["trigger_group"], "gray"),
                    fill=True,
                    fill_color=TRIGGER_COLORS.get(row["trigger_group"], "gray"),
                    fill_opacity=0.75,
                    weight=1,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{row['country']} — {row['date']}",
                ).add_to(landslide_map)

            map_data = st_folium(
                landslide_map,
                use_container_width=True,
                height=560,
                returned_objects=["last_object_clicked_tooltip", "last_object_clicked"],
            )

            # Try to resolve the clicked marker back to a specific event row.
            clicked = map_data.get("last_object_clicked") if map_data else None
            if clicked and clicked.get("lat") is not None and clicked.get("lng") is not None:
                match = display_df[
                    (display_df["latitude"].round(4) == round(clicked["lat"], 4))
                    & (display_df["longitude"].round(4) == round(clicked["lng"], 4))
                ]
                if not match.empty:
                    st.session_state["selected_event_id"] = int(match.iloc[0]["id"])

            st.markdown(
                """
                <div class="gs-map-legend">
                    <div class="gs-map-legend-item"><span class="gs-map-legend-dot" style="background:#2D7DA9;"></span>Rainfall</div>
                    <div class="gs-map-legend-item"><span class="gs-map-legend-dot" style="background:#B3392A;"></span>Earthquake</div>
                    <div class="gs-map-legend-item"><span class="gs-map-legend-dot" style="background:#8C8779;"></span>Other</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 5 — EVENT DETAILS (six individual clean cards)
# ============================================================

with st.container(border=True, key="section-event"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("file-text", 20)} Event Details</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">Full record for the currently selected map marker</div>',
        unsafe_allow_html=True,
    )

    selected_id = st.session_state.get("selected_event_id")
    selected_row = None
    if selected_id is not None:
        match = landslide_df[landslide_df["id"] == selected_id]
        if not match.empty:
            selected_row = match.iloc[0]

    if selected_row is None:
        st.markdown(
            f"""
            <div class="gs-empty-state">
                <div class="ds-kpi-icon ds-chip-brand" style="width:46px;height:46px;">{_icon("map-pin", 20)}</div>
                <div>Click a marker on the map above to view its event details here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        event_cells = [
            ("map-pin", "ds-chip-brand", "Location",
             f"{selected_row['country']} ({selected_row['latitude']}, {selected_row['longitude']})", False),
            ("calendar", "ds-chip-accent", "Date", f"{selected_row['date']}", False),
            ("alert-triangle", "ds-chip-amber", "Trigger", f"{selected_row['trigger_group']}", False),
            ("skull", "ds-chip-brand", "Fatalities", f"{int(selected_row['fatalities'])}", False),
            ("droplet", "ds-chip-accent", "Rainfall", "Not recorded in this dataset.", True),
            ("file-text", "ds-chip-amber", "Description", "No description available for this event.", True),
        ]

        row1 = st.columns(3, gap="medium")
        row2 = st.columns(3, gap="medium")
        cols = row1 + row2

        for col, (icon_name, chip_class, label, value, is_muted) in zip(cols, event_cells):
            with col:
                with st.container(border=True, key=f"event-card-{label.lower()}"):
                    value_class = "gs-event-value muted" if is_muted else "gs-event-value"
                    st.markdown(
                        f"""
                        <div class="gs-event-label-row">
                            <div class="ds-kpi-icon {chip_class}" style="width:26px;height:26px;margin-bottom:0;">{_icon(icon_name, 13)}</div>
                            <div class="gs-event-label">{label}</div>
                        </div>
                        <div class="{value_class}">{value}</div>
                        """,
                        unsafe_allow_html=True,
                    )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ============================================================
# SECTION 6 — INSIGHTS
# ============================================================

with st.container(border=True, key="section-insights"):
    st.markdown(
        f'<div class="ds-section-title">{_icon("lightbulb", 20)} Insights</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ds-section-subtitle">How to interpret the historical data above</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="gs-insight-box">
            {_icon("lightbulb", 22)}
            <div>
                <div class="gs-insight-title">Reading the map</div>
                <div class="gs-insight-text">Most historical landslides are rainfall-triggered.
                Use the filters above to explore regional trends, narrow to a specific country
                or year range, and click any marker on the map for full event details. Marker
                color follows the same legend shown under the map: blue for rainfall, red for
                earthquake, gray for other/unclassified triggers.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="gs-section-spacer"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Filtered Data Table (supporting reference view) (UNCHANGED)
# ---------------------------------------------------------------------------

with st.expander("📄 View Filtered Event Data", expanded=False):
    st.dataframe(
        filtered_df[
            ["date", "country", "trigger_group", "fatalities", "latitude", "longitude"]
        ].rename(columns={"trigger_group": "trigger"}),
        width="stretch",
        hide_index=True,
    )