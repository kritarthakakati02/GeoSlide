"""
GeoSlide - Frontend API Client
================================
Placeholder API layer for communicating with the GeoSlide FastAPI backend.

Phase 10.3 (Part 1) only builds the Prediction Page UI. Actual HTTP
communication with the backend is intentionally NOT implemented yet.
Functions in this module are stubs that define the expected interface
for future phases and raise NotImplementedError until wired up.
"""

from typing import Any, Dict


def predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a landslide risk prediction request to the backend.

    This is a placeholder for future phases. It does NOT make any
    network/API calls yet.

    Args:
        payload: Dictionary of feature values collected from the
            Prediction Page form (including one-hot encoded
            Land Use / Soil Type fields).

    Returns:
        Expected (future) shape:
            {
                "risk_level": str,
                "probability": float,
                "status": str,
            }

    Raises:
        NotImplementedError: Always, until backend integration is
            implemented in a later phase.
    """
    raise NotImplementedError(
        "predict() is not implemented yet. "
        "Backend integration will be added in a later phase."
    )


def check_health() -> Dict[str, Any]:
    """
    Placeholder for a future backend health-check call.

    Raises:
        NotImplementedError: Always, until backend integration is
            implemented in a later phase.
    """
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
