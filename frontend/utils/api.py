"""
GeoSlide - Frontend API Client
=============================

HTTP layer for communicating with the GeoSlide FastAPI backend.
The prediction page uses the `/predict` endpoint, while the SHAP page
uses the new `/explain` endpoint.
"""

from typing import Any, Dict, List

import requests

from utils.constants import API_BASE_URL, HEALTH_ENDPOINT, PREDICT_ENDPOINT, REQUEST_TIMEOUT
from utils.helpers import build_feature_vector, encode_land_use, encode_soil_type

EXPLAIN_ENDPOINT = f"{API_BASE_URL}/explain"


class APIError(Exception):
    """Base class for all GeoSlide API client errors."""


class BackendUnavailableError(APIError):
    """Raised when the FastAPI backend cannot be reached at all."""


class BackendTimeoutError(APIError):
    """Raised when the backend does not respond within REQUEST_TIMEOUT."""


class InvalidResponseError(APIError):
    """Raised when the backend responds, but with bad data or a bad status."""


def _build_payload_from_form(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert the raw form payload into the exact feature-key shape expected by build_feature_vector."""
    feature_payload = {}
    for key in (
        "rainfall",
        "slope_angle",
        "soil_saturation",
        "vegetation_cover",
        "rainfall_3d",
        "rainfall_7d",
        "aspect",
        "elevation",
        "ndvi_index",
        "earthquake_activity",
        "proximity_to_water",
        "distance_to_road",
        "temperature",
        "humidity",
        "soil_ph",
        "clay_content",
        "sand_content",
        "silt_content",
        "soil_erosion_rate",
        "historical_landslide_count",
        "pore_water_pressure",
        "soil_moisture",
        "microseismic_activity",
        "acoustic_emission",
        "soil_strain",
        "soil_temperature",
        "tdr_reflection_index",
    ):
        feature_payload[key] = payload.get(key, 0.0)

    feature_payload.update(encode_land_use(payload.get("land_use", "")))
    feature_payload.update(encode_soil_type(payload.get("soil_type", "")))
    return feature_payload


def predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send a landslide risk prediction request to the backend."""
    features = build_feature_vector(_build_payload_from_form(payload))

    try:
        response = requests.post(
            PREDICT_ENDPOINT,
            json={"features": features},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.ConnectionError as exc:
        raise BackendUnavailableError(
            f"Could not connect to the GeoSlide backend at {PREDICT_ENDPOINT}. "
            "Make sure the FastAPI server is running."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise BackendTimeoutError(
            f"The backend did not respond within {REQUEST_TIMEOUT} seconds."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise APIError(f"Unexpected error while contacting the backend: {exc}") from exc

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise InvalidResponseError(
            f"Backend returned an error (HTTP {response.status_code}): {detail}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise InvalidResponseError("Backend returned a response that was not valid JSON.") from exc

    missing = {"prediction", "probability", "risk_level"} - data.keys()
    if missing:
        raise InvalidResponseError(
            f"Backend response is missing expected field(s): {', '.join(sorted(missing))}"
        )

    return data


def check_health() -> Dict[str, Any]:
    """Check whether the GeoSlide backend is up and responding."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.ConnectionError as exc:
        raise BackendUnavailableError(
            f"Could not connect to the GeoSlide backend at {HEALTH_ENDPOINT}."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise BackendTimeoutError(
            f"The backend did not respond within {REQUEST_TIMEOUT} seconds."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise APIError(f"Unexpected error while contacting the backend: {exc}") from exc

    if response.status_code != 200:
        raise InvalidResponseError(f"Backend health check failed (HTTP {response.status_code}).")

    try:
        return response.json()
    except ValueError as exc:
        raise InvalidResponseError("Backend health check returned invalid JSON.") from exc


def get_shap_explanation(payload: Dict[str, Any] | List[float] | None = None) -> Dict[str, Any]:
    """Send the current feature vector to the backend explainability endpoint."""
    if isinstance(payload, list):
        features = payload
    elif isinstance(payload, dict):
        features = build_feature_vector(_build_payload_from_form(payload))
    else:
        features = []

    try:
        response = requests.post(
            EXPLAIN_ENDPOINT,
            json={"features": features},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.ConnectionError as exc:
        raise BackendUnavailableError(
            f"Could not connect to the GeoSlide backend at {EXPLAIN_ENDPOINT}."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise BackendTimeoutError(
            f"The backend did not respond within {REQUEST_TIMEOUT} seconds."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise APIError(f"Unexpected error while contacting the backend: {exc}") from exc

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise InvalidResponseError(
            f"Backend returned an error (HTTP {response.status_code}): {detail}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise InvalidResponseError("Backend returned a response that was not valid JSON.") from exc

    return {
        "feature_importance": data.get("feature_importance", []),
        "local_explanation": data.get("local_explanation", {"positive": [], "negative": []}),
        "ai_interpretation": data.get("ai_interpretation", ""),
        "status": data.get("status", "success"),
        "feature_names": data.get("feature_names", []),
        "shap_values": data.get("shap_values", []),
        "top_positive_contributors": data.get("top_positive_contributors", []),
        "top_negative_contributors": data.get("top_negative_contributors", []),
    }

