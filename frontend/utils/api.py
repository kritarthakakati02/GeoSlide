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
