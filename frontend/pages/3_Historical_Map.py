"""
GeoSlide - Historical Landslide Map Page
===========================================
Phase 10.5: Historical Landslide Map.

This page lets users explore historical landslide events (sourced from
the NASA Global Landslide Catalog when available) on an interactive
Folium map, with sidebar filters, top-level summary metrics, and a
detail panel for the currently selected event.

NOTE: If the NASA dataset cannot be loaded (no local file / no network
access), this page automatically falls back to generated placeholder
sample data so the UI remains fully functional and demoable.
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
# Data Loading
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
# Trigger normalization helper (for metric buckets & filtering)
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
# Sidebar
# ---------------------------------------------------------------------------

render_sidebar()

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------

st.title("🌍 Historical Landslide Map")
st.markdown("Explore historical landslide events using the NASA Global Landslide Catalog.")

if not is_live_data:
    st.warning(
        "⚠️ Live NASA Global Landslide Catalog data is unavailable right now. "
        "Displaying generated placeholder sample data instead so the map "
        "remains fully explorable."
    )

st.divider()


# ---------------------------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------------------------

st.sidebar.header("🔎 Filters")

country_filter = st.sidebar.multiselect(
    "Country",
    options=sorted(landslide_df["country"].dropna().unique()),
    default=[],
    help="Leave empty to include all countries.",
)

min_year = int(landslide_df["year"].min())
max_year = int(landslide_df["year"].max())
if min_year == max_year:
    year_filter = (min_year, max_year)
    st.sidebar.caption(f"Year: {min_year}")
else:
    year_filter = st.sidebar.slider(
        "Year",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

trigger_filter = st.sidebar.multiselect(
    "Trigger",
    options=sorted(landslide_df["trigger_group"].dropna().unique()),
    default=[],
    help="Leave empty to include all triggers.",
)

max_fatalities_available = int(landslide_df["fatalities"].max())
fatalities_filter = st.sidebar.slider(
    "Minimum Fatalities",
    min_value=0,
    max_value=max(max_fatalities_available, 1),
    value=0,
    help="Only show events with at least this many fatalities.",
)


# ---------------------------------------------------------------------------
# Apply Filters
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
# Top Metrics
# ---------------------------------------------------------------------------

total_events = len(filtered_df)
rainfall_events = int((filtered_df["trigger_group"] == "Rainfall").sum())
earthquake_events = int((filtered_df["trigger_group"] == "Earthquake").sum())
other_events = int((filtered_df["trigger_group"] == "Other").sum())

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Total Events", f"{total_events:,}")
metric_col2.metric("🌧️ Rainfall Triggered", f"{rainfall_events:,}")
metric_col3.metric("🌋 Earthquake Triggered", f"{earthquake_events:,}")
metric_col4.metric("❓ Other Triggers", f"{other_events:,}")

st.divider()


# ---------------------------------------------------------------------------
# Map
# ---------------------------------------------------------------------------

st.subheader("🗺️ Landslide Event Map")

TRIGGER_COLORS = {
    "Rainfall": "blue",
    "Earthquake": "red",
    "Other": "gray",
}

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
        height=520,
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

st.divider()


# ---------------------------------------------------------------------------
# Below the Map: Selected Event Details
# ---------------------------------------------------------------------------

st.subheader("📋 Selected Event Details")

selected_id = st.session_state.get("selected_event_id")
selected_row = None
if selected_id is not None:
    match = landslide_df[landslide_df["id"] == selected_id]
    if not match.empty:
        selected_row = match.iloc[0]

with st.container(border=True):
    if selected_row is None:
        st.write("_Click a marker on the map above to view its event details here._")
    else:
        detail_col1, detail_col2, detail_col3 = st.columns(3)
        with detail_col1:
            st.markdown(f"**📅 Date:** {selected_row['date']}")
            st.markdown(f"**🌍 Country:** {selected_row['country']}")
        with detail_col2:
            st.markdown(f"**⚡ Trigger:** {selected_row['trigger_group']}")
            st.markdown(f"**☠️ Fatalities:** {int(selected_row['fatalities'])}")
        with detail_col3:
            st.markdown(f"**🧭 Latitude:** {selected_row['latitude']}")
            st.markdown(f"**🧭 Longitude:** {selected_row['longitude']}")


# ---------------------------------------------------------------------------
# Filtered Data Table (supporting reference view)
# ---------------------------------------------------------------------------

with st.expander("📄 View Filtered Event Data", expanded=False):
    st.dataframe(
        filtered_df[
            ["date", "country", "trigger_group", "fatalities", "latitude", "longitude"]
        ].rename(columns={"trigger_group": "trigger"}),
        width="stretch",
        hide_index=True,
    )
