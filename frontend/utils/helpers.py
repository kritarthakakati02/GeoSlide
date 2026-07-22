"""
GeoSlide - Frontend Helper Utilities
=====================================
Utility/helper functions used by the Streamlit frontend pages.

Phase 10.3 (Part 1) only implements the helpers required to translate
user-friendly dropdown selections (Land Use, Soil Type) into the
one-hot encoded feature format expected by the backend ML model.

No prediction logic, API calls, or SHAP explanations live here.
"""

from typing import Dict


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
