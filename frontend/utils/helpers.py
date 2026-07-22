"""
GeoSlide - Frontend Helper Utilities
=====================================
Utility/helper functions used by the Streamlit frontend pages.

Includes helpers to translate user-friendly dropdown selections
(Land Use, Soil Type) into the one-hot encoded feature format expected
by the backend ML model, and to assemble the final ordered feature
vector sent to the `/predict` endpoint.
"""

from typing import Dict, List

from utils.constants import FEATURE_ORDER


# ---------------------------------------------------------------------------
# Land Use one-hot encoding
# ---------------------------------------------------------------------------

LAND_USE_OPTIONS = ["Urban", "Forest", "Agriculture"]


def encode_land_use(land_use: str) -> Dict[str, int]:
    """
    Convert a Land Use dropdown selection into one-hot encoded fields.

    Args:
        land_use: One of "Urban", "Forest", "Agriculture".

    Returns:
        A dict with keys:
            Land_Use_Urban
            Land_Use_Forest
            Land_Use_Agriculture
        where the selected option maps to 1 and all others map to 0.
    """
    encoded = {
        "Land_Use_Urban": 0,
        "Land_Use_Forest": 0,
        "Land_Use_Agriculture": 0,
    }

    key = f"Land_Use_{land_use}"
    if key in encoded:
        encoded[key] = 1

    return encoded


# ---------------------------------------------------------------------------
# Soil Type one-hot encoding
# ---------------------------------------------------------------------------

SOIL_TYPE_OPTIONS = ["Gravel", "Sand", "Silt", "Clay"]


def encode_soil_type(soil_type: str) -> Dict[str, int]:
    """
    Convert a Soil Type dropdown selection into one-hot encoded fields.

    Args:
        soil_type: One of "Gravel", "Sand", "Silt", "Clay".

    Returns:
        A dict with keys:
            Soil_Type_Gravel
            Soil_Type_Sand
            Soil_Type_Silt
            Soil_Type_Clay
        where the selected option maps to 1 and all others map to 0.
    """
    encoded = {
        "Soil_Type_Gravel": 0,
        "Soil_Type_Sand": 0,
        "Soil_Type_Silt": 0,
        "Soil_Type_Clay": 0,
    }

    key = f"Soil_Type_{soil_type}"
    if key in encoded:
        encoded[key] = 1

    return encoded


# ---------------------------------------------------------------------------
# Sample data helper
# ---------------------------------------------------------------------------

def get_sample_input_data() -> Dict:
    """
    Return a dictionary of sample/demo values for all prediction page
    inputs. Used by the "Load Sample Data" button so users can quickly
    see the form populated with realistic values.

    Note: This only returns raw form values (including the raw
    Land Use / Soil Type dropdown selections), not one-hot encoded
    values. Encoding happens separately via encode_land_use /
    encode_soil_type when the form is eventually submitted.
    """
    return {
        # Weather Conditions
        "rainfall": 45.0,
        "rainfall_3d": 120.0,
        "rainfall_7d": 220.0,
        "temperature": 24.5,
        "humidity": 78.0,

        # Terrain & Geography
        "slope_angle": 32.0,
        "aspect": 180.0,
        "elevation": 850.0,
        "distance_to_road": 120.0,
        "proximity_to_water": 60.0,

        # Soil Characteristics
        "soil_saturation": 68.0,
        "soil_moisture": 34.0,
        "soil_ph": 6.4,
        "clay_content": 28.0,
        "sand_content": 42.0,
        "silt_content": 30.0,
        "soil_erosion_rate": 2.3,
        "soil_temperature": 19.0,
        "pore_water_pressure": 15.5,

        # Vegetation & Land Use
        "ndvi_index": 0.42,
        "vegetation_cover": 55.0,
        "land_use": "Forest",

        # Geological Activity
        "earthquake_activity": 2.1,
        "historical_landslide_count": 3,

        # Sensor Measurements
        "microseismic_activity": 0.35,
        "acoustic_emission": 12.4,
        "soil_strain": 0.08,
        "tdr_reflection_index": 1.6,

        # Soil Type
        "soil_type": "Clay",
    }


# ---------------------------------------------------------------------------
# Form field -> backend feature name mapping
# ---------------------------------------------------------------------------
# Maps the short session_state/form keys used on the Prediction page to the
# exact feature names the backend model was trained on (see
# models/feature_names.pkl / utils.constants.FEATURE_ORDER). One-hot fields
# (Land Use / Soil Type) are produced separately by encode_land_use() /
# encode_soil_type() and are already keyed by their final feature name.

FORM_FIELD_TO_FEATURE_NAME = {
    "rainfall": "Rainfall_mm",
    "slope_angle": "Slope_Angle",
    "soil_saturation": "Soil_Saturation",
    "vegetation_cover": "Vegetation_Cover",
    "rainfall_3d": "Rainfall_3Day",
    "rainfall_7d": "Rainfall_7Day",
    "aspect": "Aspect",
    "elevation": "Elevation_m",
    "ndvi_index": "NDVI_Index",
    "earthquake_activity": "Earthquake_Activity",
    "proximity_to_water": "Proximity_to_Water",
    "distance_to_road": "Distance_to_Road_m",
    "temperature": "Temperature_C",
    "humidity": "Humidity_percent",
    "soil_ph": "Soil_pH",
    "clay_content": "Clay_Content",
    "sand_content": "Sand_Content",
    "silt_content": "Silt_Content",
    "soil_erosion_rate": "Soil_Erosion_Rate",
    "historical_landslide_count": "Historical_Landslide_Count",
    "pore_water_pressure": "Pore_Water_Pressure_kPa",
    "soil_moisture": "Soil_Moisture_Content",
    "microseismic_activity": "Microseismic_Activity",
    "acoustic_emission": "Acoustic_Emission_dB",
    "soil_strain": "Soil_Strain",
    "soil_temperature": "Soil_Temperature_C",
    "tdr_reflection_index": "TDR_Reflection_Index",
}


def build_feature_vector(form_payload: Dict) -> List[float]:
    """
    Convert the raw form payload (short form-field keys + one-hot
    Land Use / Soil Type keys) into the exact ordered list of floats
    the backend `/predict` endpoint expects.

    Args:
        form_payload: Dict containing every short form-field key from
            FORM_FIELD_TO_FEATURE_NAME, plus the one-hot encoded keys
            produced by encode_land_use() and encode_soil_type().

    Returns:
        A list of floats in utils.constants.FEATURE_ORDER order.

    Raises:
        KeyError: If a required feature is missing from form_payload,
            naming the missing feature so the bug is easy to trace.
    """
    by_feature_name: Dict[str, float] = {}

    for form_key, feature_name in FORM_FIELD_TO_FEATURE_NAME.items():
        if form_key not in form_payload:
            raise KeyError(f"Missing expected form field: '{form_key}'")
        by_feature_name[feature_name] = form_payload[form_key]

    for feature_name in (
        "Land_Use_Urban", "Land_Use_Forest", "Land_Use_Agriculture",
        "Soil_Type_Gravel", "Soil_Type_Sand", "Soil_Type_Silt", "Soil_Type_Clay",
    ):
        if feature_name not in form_payload:
            raise KeyError(f"Missing expected one-hot feature: '{feature_name}'")
        by_feature_name[feature_name] = form_payload[feature_name]

    try:
        return [float(by_feature_name[name]) for name in FEATURE_ORDER]
    except KeyError as exc:
        raise KeyError(
            f"Feature '{exc.args[0]}' required by the model was not found in the form payload."
        )
