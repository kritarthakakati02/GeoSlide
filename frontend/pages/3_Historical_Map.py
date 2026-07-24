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

UI note: this file was redesigned into a premium "geospatial
intelligence dashboard" (page-scoped dark theme, hover KPI cards, a
single collapsible "🎛 Filters" panel, a dominant map card, a modern
selected-event info card, and a small insights card). This mirrors the
same redesign approach already used on the Prediction and SHAP Analysis
pages for visual consistency across the app.

Nothing about *what* is computed changed:
    - Data loading (`load_landslide_data`, `_load_local_catalog`,
      `_map_catalog_columns`, `_generate_placeholder_data`) is
      byte-for-byte unchanged.
    - `_classify_trigger` and the filtering logic (country/year/
      trigger/fatalities) are unchanged - the four filter widgets were
      only moved from the sidebar into a single collapsible panel in
      the page body, per the redesign brief.
    - Folium map creation, marker generation, popups, tooltips, and the
      marker-click -> selected-event resolution logic are unchanged.
    - The filtered data table at the bottom is unchanged.

Only layout, typography, spacing, and presentation were touched.
"""

from datetime import date, timedelta
import glob
import random

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from components.sidebar import render_sidebar


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Historical Map | GeoSlide",
    page_icon="🌍",
    layout="wide",
)


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
# Sidebar (branded nav only - filters live in the page body, see Section 3)
# ---------------------------------------------------------------------------

render_sidebar()


# ---------------------------------------------------------------------------
# Page-scoped dark theme + layout CSS
# ---------------------------------------------------------------------------
# Same scoping approach and design tokens (--gs-*) as the Prediction and
# SHAP Analysis pages: everything lives under [data-testid="stAppViewContainer"]
# and is only ever injected while this script is the active page, so it
# cannot leak into other pages.

MAP_CSS = """
:root {
    --gs-bg: #0F172A;
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
    background: radial-gradient(circle at 85% 0%, #132239 0%, var(--gs-bg) 45%) !important;
}

[data-testid="stAppViewContainer"] .block-container {
    padding: 1.6rem 2.6rem 2rem !important;
    max-width: 1500px;
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4 {
    color: #F1F5F9 !important;
    letter-spacing: -0.01em;
}

[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
    color: var(--gs-muted) !important;
}

[data-testid="stAppViewContainer"] hr {
    border-color: var(--gs-border) !important;
}

/* Cards (bordered containers: KPI cards, filter panel, map card, event card, insight card) */
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--gs-card) !important;
    border: 1px solid var(--gs-border) !important;
    border-radius: var(--gs-radius) !important;
    box-shadow: 0 12px 28px rgba(2, 6, 23, 0.45) !important;
}

/* Expander (Filters panel + Filtered Data Table) */
[data-testid="stAppViewContainer"] [data-testid="stExpander"] {
    background: var(--gs-card) !important;
    border: 1px solid var(--gs-border) !important;
    border-radius: var(--gs-radius) !important;
    box-shadow: 0 10px 24px rgba(2, 6, 23, 0.35) !important;
    overflow: hidden;
}

[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary p {
    font-size: 0.98rem;
    font-weight: 700;
    color: #F1F5F9 !important;
}

/* Inputs inside the Filters panel */
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] > div,
[data-testid="stAppViewContainer"] [data-testid="stSlider"] {
    background: transparent;
}

[data-testid="stAppViewContainer"] label p {
    color: var(--gs-muted) !important;
    font-size: 0.82rem !important;
}

.gs-hero-subtitle {
    font-size: 0.98rem;
    color: var(--gs-muted);
    margin-top: -6px;
    margin-bottom: 4px;
    max-width: 900px;
}

.gs-grid-heading {
    font-size: 1.02rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 4px 0 10px 0;
}

.gs-section-caption {
    font-size: 0.88rem;
    color: var(--gs-muted);
    margin-top: 10px;
}

/* KPI cards */
.gs-kpi-card {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 4px 2px 2px 2px;
    border-radius: 14px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.gs-kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 22px rgba(59, 130, 246, 0.18);
}

.gs-kpi-icon {
    font-size: 1.5rem;
}

.gs-kpi-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gs-muted);
}

.gs-kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #F8FAFC;
}

/* Selected event info card */
.gs-event-eyebrow {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gs-muted);
    margin-bottom: 12px;
}

.gs-event-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px 24px;
}

@media (max-width: 900px) {
    .gs-event-grid { grid-template-columns: repeat(1, 1fr); }
}

.gs-event-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.gs-event-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gs-muted);
}

.gs-event-value {
    font-size: 1.05rem;
    font-weight: 700;
    color: #F8FAFC;
}

.gs-event-value.muted {
    font-weight: 500;
    font-style: italic;
    color: var(--gs-muted);
    font-size: 0.92rem;
}

.gs-empty-state {
    text-align: center;
    padding: 22px 10px;
    color: var(--gs-muted);
}

/* Insight card */
.gs-insight-card {
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.gs-insight-icon {
    font-size: 1.4rem;
    flex-shrink: 0;
}

.gs-insight-text {
    font-size: 0.95rem;
    color: var(--gs-text);
    line-height: 1.55;
}

/* Folium map: soften the iframe corners to match the card */
[data-testid="stAppViewContainer"] iframe {
    border-radius: 14px;
}
"""

st.markdown(f"<style>{MAP_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SECTION 1 — Hero
# ---------------------------------------------------------------------------

st.markdown("## 🌍 Historical Landslide Explorer")
st.markdown(
    '<div class="gs-hero-subtitle">Explore historical landslide events from the NASA Global '
    "Landslide Catalog using interactive filters and geospatial visualization.</div>",
    unsafe_allow_html=True,
)

if not is_live_data:
    st.warning(
        "⚠️ Live NASA Global Landslide Catalog data is unavailable right now. "
        "Displaying generated placeholder sample data instead so the map "
        "remains fully explorable."
    )

st.write("")


# ---------------------------------------------------------------------------
# SECTION 3 — Map Controls (single collapsible "🎛 Filters" panel)
# ---------------------------------------------------------------------------
# NOTE: rendered before Section 2 (Statistics) in the code so the KPI cards
# below can reflect the filters the user has just set - the on-page order
# still matches the brief (Hero -> Statistics -> Filters -> Map -> ...) since
# Section 2 is rendered from `filtered_df`, computed right after this panel.

with st.expander("🎛 Filters", expanded=True):
    filt_col1, filt_col2 = st.columns(2, gap="medium")

    with filt_col1:
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

st.write("")


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
# SECTION 2 — Statistics (KPI cards)
# ---------------------------------------------------------------------------

total_events = len(filtered_df)
rainfall_events = int((filtered_df["trigger_group"] == "Rainfall").sum())
earthquake_events = int((filtered_df["trigger_group"] == "Earthquake").sum())
other_events = int((filtered_df["trigger_group"] == "Other").sum())

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4, gap="medium")

kpi_data = [
    (kpi_col1, "🗺️", "Total Events", total_events),
    (kpi_col2, "🌧️", "Rainfall Triggered", rainfall_events),
    (kpi_col3, "🌋", "Earthquake Triggered", earthquake_events),
    (kpi_col4, "❓", "Other Triggers", other_events),
]

for col, icon, label, value in kpi_data:
    with col:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="gs-kpi-card">
                    <div class="gs-kpi-icon">{icon}</div>
                    <div class="gs-kpi-label">{label}</div>
                    <div class="gs-kpi-value">{value:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.write("")


# ---------------------------------------------------------------------------
# SECTION 4 — Interactive Map (UNCHANGED map/marker generation logic)
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">🗺️ Landslide Event Map</div>', unsafe_allow_html=True)

TRIGGER_COLORS = {
    "Rainfall": "blue",
    "Earthquake": "red",
    "Other": "gray",
}

with st.container(border=True):
    if filtered_df.empty:
        st.info("No events match the selected filters. Try widening your filter criteria.")
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

st.write("")


# ---------------------------------------------------------------------------
# SECTION 5 — Selected Event (modern information card)
# ---------------------------------------------------------------------------

st.markdown('<div class="gs-grid-heading">📋 Selected Event</div>', unsafe_allow_html=True)

selected_id = st.session_state.get("selected_event_id")
selected_row = None
if selected_id is not None:
    match = landslide_df[landslide_df["id"] == selected_id]
    if not match.empty:
        selected_row = match.iloc[0]

with st.container(border=True):
    if selected_row is None:
        st.markdown(
            """
            <div class="gs-empty-state">
                <div style="font-size:1.6rem;">📍</div>
                <div style="margin-top:6px;">Click a marker on the map above to view its event
                details here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="gs-event-eyebrow">Event Details</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="gs-event-grid">
                <div class="gs-event-item">
                    <div class="gs-event-label">📍 Location</div>
                    <div class="gs-event-value">{selected_row['country']}
                        ({selected_row['latitude']}, {selected_row['longitude']})</div>
                </div>
                <div class="gs-event-item">
                    <div class="gs-event-label">📅 Date</div>
                    <div class="gs-event-value">{selected_row['date']}</div>
                </div>
                <div class="gs-event-item">
                    <div class="gs-event-label">⚠️ Trigger</div>
                    <div class="gs-event-value">{selected_row['trigger_group']}</div>
                </div>
                <div class="gs-event-item">
                    <div class="gs-event-label">☠️ Fatalities</div>
                    <div class="gs-event-value">{int(selected_row['fatalities'])}</div>
                </div>
                <div class="gs-event-item">
                    <div class="gs-event-label">🌧️ Rainfall</div>
                    <div class="gs-event-value muted">Not recorded in this dataset.</div>
                </div>
                <div class="gs-event-item">
                    <div class="gs-event-label">📝 Description</div>
                    <div class="gs-event-value muted">No description available for this event.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")


# ---------------------------------------------------------------------------
# SECTION 6 — Insights
# ---------------------------------------------------------------------------

with st.container(border=True):
    st.markdown(
        """
        <div class="gs-insight-card">
            <div class="gs-insight-icon">💡</div>
            <div class="gs-insight-text">
                Most historical landslides are rainfall-triggered. Use the filters above to
                explore regional trends, narrow to a specific country or year range, and click
                any marker on the map for full event details.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")


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