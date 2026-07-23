"""
GeoSlide - Frontend API Client
================================
Client wrapper for communicating with the GeoSlide FastAPI backend.
"""

from typing import Any, Dict

import requests

BACKEND_URL = "http://127.0.0.1:8000/predict"


def _build_feature_vector(payload: Dict[str, Any]) -> list[float]:
    """Convert the form payload into the exact feature order expected by the backend."""
    land_use = payload.get("land_use", "")
    soil_type = payload.get("soil_type", "")

    land_use_encoded = {
        "Land_Use_Urban": 1 if land_use == "Urban" else 0,
        "Land_Use_Forest": 1 if land_use == "Forest" else 0,
        "Land_Use_Agriculture": 1 if land_use == "Agriculture" else 0,
    }
    soil_type_encoded = {
        "Soil_Type_Gravel": 1 if soil_type == "Gravel" else 0,
        "Soil_Type_Sand": 1 if soil_type == "Sand" else 0,
        "Soil_Type_Silt": 1 if soil_type == "Silt" else 0,
        "Soil_Type_Clay": 1 if soil_type == "Clay" else 0,
    }

    return [
        payload.get("rainfall", 0.0),
        payload.get("slope_angle", 0.0),
        payload.get("soil_saturation", 0.0),
        payload.get("vegetation_cover", 0.0),
        payload.get("rainfall_3d", 0.0),
        payload.get("rainfall_7d", 0.0),
        payload.get("aspect", 0.0),
        payload.get("elevation", 0.0),
        payload.get("ndvi_index", 0.0),
        land_use_encoded["Land_Use_Urban"],
        land_use_encoded["Land_Use_Forest"],
        land_use_encoded["Land_Use_Agriculture"],
        payload.get("earthquake_activity", 0.0),
        payload.get("proximity_to_water", 0.0),
        payload.get("distance_to_road", 0.0),
        payload.get("temperature", 0.0),
        payload.get("humidity", 0.0),
        payload.get("soil_ph", 0.0),
        payload.get("clay_content", 0.0),
        payload.get("sand_content", 0.0),
        payload.get("silt_content", 0.0),
        payload.get("soil_erosion_rate", 0.0),
        payload.get("historical_landslide_count", 0),
        soil_type_encoded["Soil_Type_Gravel"],
        soil_type_encoded["Soil_Type_Sand"],
        soil_type_encoded["Soil_Type_Silt"],
        soil_type_encoded["Soil_Type_Clay"],
        payload.get("pore_water_pressure", 0.0),
        payload.get("soil_moisture", 0.0),
        payload.get("microseismic_activity", 0.0),
        payload.get("acoustic_emission", 0.0),
        payload.get("soil_strain", 0.0),
        payload.get("soil_temperature", 0.0),
        payload.get("tdr_reflection_index", 0.0),
    ]


def predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send a landslide risk prediction request to the backend."""
    features = _build_feature_vector(payload)

    try:
        response = requests.post(BACKEND_URL, json={"features": features}, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Backend returned an unexpected response format.")

        return {
            "status": "success",
            "data": {
                "prediction": int(data.get("prediction", 0)),
                "probability": float(data.get("probability", 0.0)),
                "risk_level": str(data.get("risk_level", "Unknown")),
            },
        }
    except requests.exceptions.Timeout:
        return {"status": "error", "data": {"error": "The prediction request timed out."}}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "data": {"error": "The backend is unavailable. Please try again later."}}
    except requests.exceptions.HTTPError as exc:
        return {"status": "error", "data": {"error": f"Prediction request failed: {exc}"}}
    except ValueError as exc:
        return {"status": "error", "data": {"error": str(exc)}}
    except Exception as exc:
        return {"status": "error", "data": {"error": f"Unexpected error: {exc}"}}


def check_health() -> Dict[str, Any]:
    """Placeholder for a future backend health-check call."""
    raise NotImplementedError(
        "check_health() is not implemented yet. "
        "Backend integration will be added in a later phase."
    )


def get_shap_explanation(prediction_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Retrieve a SHAP explainability breakdown for a landslide risk
    prediction.

    NOTE: The backend does not yet expose a SHAP explainability
    endpoint, so this function does NOT make any network/API calls.
    It always returns placeholder/mock data so the SHAP Analysis page
    can be built and demoed independently of the backend. Once a real
    `/shap/explain` (or similar) backend endpoint exists, this function
    should be updated to call it (e.g. via `requests.post(...)`) and
    fall back to placeholder data only on error.

    Args:
        prediction_data: Optional dictionary describing the prediction
            to explain (e.g. the most recent result from the
            Prediction page's session state). Currently unused beyond
            being accepted for forward-compatibility with the future
            real implementation.

    Returns:
        A dictionary shaped like the eventual backend response:
            {
                "feature_importance": [
                    {"feature": str, "importance": float}, ...
                ],
                "local_explanation": {
                    "positive": [{"feature": str, "impact": float}, ...],
                    "negative": [{"feature": str, "impact": float}, ...],
                },
                "ai_interpretation": str,
                "status": "placeholder",
            }
    """
    return {
        "feature_importance": [
            {"feature": "Soil Saturation", "importance": 0.27},
            {"feature": "Rainfall (Last 7 Days)", "importance": 0.22},
            {"feature": "Slope Angle", "importance": 0.18},
            {"feature": "Pore Water Pressure", "importance": 0.14},
            {"feature": "NDVI Index", "importance": 0.09},
            {"feature": "Distance to Road", "importance": 0.06},
            {"feature": "Soil Type (Clay)", "importance": 0.04},
        ],
        "local_explanation": {
            "positive": [
                {"feature": "Soil Saturation", "impact": 0.18},
                {"feature": "Rainfall (Last 7 Days)", "impact": 0.15},
                {"feature": "Slope Angle", "impact": 0.11},
            ],
            "negative": [
                {"feature": "Vegetation Cover", "impact": -0.09},
                {"feature": "Distance to Road", "impact": -0.06},
                {"feature": "Soil pH", "impact": -0.03},
            ],
        },
        "ai_interpretation": (
            "The model's prediction was driven primarily by elevated soil "
            "saturation and heavy rainfall over the past 7 days, both of "
            "which are strongly associated with increased landslide risk. "
            "Steep slope angle further amplified the risk score. On the "
            "other hand, healthy vegetation cover and a greater distance "
            "from the nearest road slightly reduced the predicted risk. "
            "This is placeholder text and will be replaced with a "
            "real, model-generated interpretation once the backend SHAP "
            "endpoint is available."
        ),
        "status": "placeholder",
    }
