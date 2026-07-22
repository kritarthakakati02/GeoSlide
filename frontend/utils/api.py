"""
GeoSlide - Frontend API Client
================================
HTTP layer for communicating with the GeoSlide FastAPI backend.

Phase 10.4 - Backend Integration: wires the Streamlit frontend up to
the real `/predict` and `/` (health-check) endpoints exposed by the
FastAPI backend, with explicit handling for connection failures,
timeouts, and invalid responses so the UI can fail gracefully instead
of crashing.
"""

from typing import Any, Dict

import requests

from utils.constants import HEALTH_ENDPOINT, PREDICT_ENDPOINT, REQUEST_TIMEOUT


class APIError(Exception):
    """Base class for all GeoSlide API client errors."""


class BackendUnavailableError(APIError):
    """Raised when the FastAPI backend cannot be reached at all."""


class BackendTimeoutError(APIError):
    """Raised when the backend does not respond within REQUEST_TIMEOUT."""


class InvalidResponseError(APIError):
    """Raised when the backend responds, but with bad data or a bad status."""


def predict(features: list) -> Dict[str, Any]:
    """
    Send a landslide risk prediction request to the backend.

    Args:
        features: Ordered list of numeric feature values matching
            utils.constants.FEATURE_ORDER exactly.

    Returns:
        {
            "prediction": int,
            "probability": float,
            "risk_level": str,
        }

    Raises:
        BackendUnavailableError: If the backend can't be reached
            (connection refused, DNS failure, etc.).
        BackendTimeoutError: If the backend doesn't respond in time.
        InvalidResponseError: If the backend returns a non-2xx status
            or a response body that can't be parsed / doesn't match
            the expected shape.
    """
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
    """
    Check whether the GeoSlide backend is up and responding.

    Returns:
        The JSON body of the root health-check endpoint.

    Raises:
        BackendUnavailableError: If the backend can't be reached.
        BackendTimeoutError: If the backend doesn't respond in time.
        InvalidResponseError: If the backend responds with a non-2xx
            status or invalid JSON.
    """
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
