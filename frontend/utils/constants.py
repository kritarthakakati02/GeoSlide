"""
constants.py

Purpose:
    Shared constant values for the GeoSlide frontend: the FastAPI
    backend location, request timeouts, and the exact ordered list
    of features the backend/KNN model expects.

Phase 10.4 - Backend Integration:
    The backend base URL can be overridden with the GEOSLIDE_API_URL
    environment variable (useful for Docker/deployment), and defaults
    to the local FastAPI dev server otherwise.
"""

import os

# ---------------------------------------------------------------------------
# Backend connection settings
# ---------------------------------------------------------------------------

API_BASE_URL = os.environ.get("GEOSLIDE_API_URL", "http://127.0.0.1:8000")

PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"
HEALTH_ENDPOINT = f"{API_BASE_URL}/"

# Seconds to wait before giving up on a backend request.
REQUEST_TIMEOUT = 10

# ---------------------------------------------------------------------------
# Feature order
# ---------------------------------------------------------------------------
# This MUST match models/feature_names.pkl exactly (verified against the
# saved artifact). The KNN model's StandardScaler was fit on features in
# this exact order, so the frontend must build the request payload in the
# exact same order.

FEATURE_ORDER = [
    "Rainfall_mm",
    "Slope_Angle",
    "Soil_Saturation",
    "Vegetation_Cover",
    "Rainfall_3Day",
    "Rainfall_7Day",
    "Aspect",
    "Elevation_m",
    "NDVI_Index",
    "Land_Use_Urban",
    "Land_Use_Forest",
    "Land_Use_Agriculture",
    "Earthquake_Activity",
    "Proximity_to_Water",
    "Distance_to_Road_m",
    "Temperature_C",
    "Humidity_percent",
    "Soil_pH",
    "Clay_Content",
    "Sand_Content",
    "Silt_Content",
    "Soil_Erosion_Rate",
    "Historical_Landslide_Count",
    "Soil_Type_Gravel",
    "Soil_Type_Sand",
    "Soil_Type_Silt",
    "Soil_Type_Clay",
    "Pore_Water_Pressure_kPa",
    "Soil_Moisture_Content",
    "Microseismic_Activity",
    "Acoustic_Emission_dB",
    "Soil_Strain",
    "Soil_Temperature_C",
    "TDR_Reflection_Index",
]

# ---------------------------------------------------------------------------
# Risk level color coding (used by the Prediction page result cards)
# ---------------------------------------------------------------------------

RISK_LEVEL_COLORS = {
    "Low": "#2ECC71",        # green
    "Moderate": "#F1C40F",   # yellow
    "High": "#E67E22",       # orange
    "Very High": "#E74C3C",  # red
}
