"""
GeoSlide - Explainability Engine
================================

This module computes SHAP-based explanations for a single input feature vector
using the saved Random Forest explainer model. It is intentionally separate
from the KNN prediction logic and does not alter the prediction endpoint.
"""

from typing import Dict, List, Union

import numpy as np
import shap

from model_loader import get_feature_names, get_rf_model, get_scaler


def _normalize_shap_values(raw_values) -> np.ndarray:
    """Normalize SHAP values returned by shap into a 2D array for one sample."""
    if isinstance(raw_values, list):
        if len(raw_values) == 2 and all(isinstance(item, np.ndarray) for item in raw_values):
            return np.asarray(raw_values[1]).reshape(-1, len(raw_values[1][0]))
        if len(raw_values) > 0 and isinstance(raw_values[0], np.ndarray):
            return np.asarray(raw_values[0]).reshape(-1, len(raw_values[0][0]))
        raise ValueError("Unsupported SHAP value structure returned by the explainer.")

    values = np.asarray(raw_values)
    if values.ndim == 3:
        return values[:, :, 1]
    if values.ndim == 2:
        return values

    raise ValueError(f"Unsupported SHAP value shape: {values.shape}")


def explain_landslide(features: List[float]) -> Dict[str, Union[list, str]]:
    """
    Compute SHAP contributions for a single feature vector using the saved RF explainer.

    Returns a structured explanation payload containing the feature names, SHAP values,
    the strongest positive contributors, and the strongest negative contributors.
    """
    if features is None:
        raise ValueError("Input features cannot be None.")

    if not isinstance(features, (list, tuple)):
        raise ValueError("Input features must be provided as a list of floats.")

    if len(features) == 0:
        raise ValueError("Input features list cannot be empty.")

    for value in features:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(
                f"All feature values must be numeric (int or float). "
                f"Got value of type {type(value).__name__}: {value!r}"
            )

    model = get_rf_model()
    if model is None:
        raise ValueError("Failed to retrieve the Random Forest explainer. Model is not available.")

    scaler = get_scaler()
    if scaler is None:
        raise ValueError("Failed to retrieve the StandardScaler. Scaler is not available.")

    feature_names = get_feature_names()
    if not feature_names:
        raise ValueError("Failed to retrieve feature names. Feature names are not available.")

    expected_count = len(feature_names)
    provided_count = len(features)
    if provided_count != expected_count:
        raise ValueError(
            f"Feature count mismatch: expected {expected_count} features "
            f"({feature_names}), but received {provided_count}."
        )

    try:
        input_array = np.array(features, dtype=float).reshape(1, -1)
        scaled_input = scaler.transform(input_array)
    except Exception as exc:
        raise ValueError(f"Failed to prepare feature matrix for explanation: {exc}") from exc

    try:
        explainer = shap.TreeExplainer(model)
        raw_values = explainer.shap_values(scaled_input)
    except Exception as exc:
        raise ValueError(f"Failed to compute SHAP values: {exc}") from exc

    try:
        shap_values = _normalize_shap_values(raw_values)[0]
    except Exception as exc:
        raise ValueError(f"Failed to normalize SHAP values: {exc}") from exc

    if len(shap_values) != len(feature_names):
        raise ValueError(
            f"SHAP output length mismatch: expected {len(feature_names)} features, "
            f"but received {len(shap_values)}."
        )

    feature_importance = [
        {"feature": name, "importance": float(abs(value))}
        for name, value in zip(feature_names, shap_values)
    ]
    feature_importance.sort(key=lambda item: item["importance"], reverse=True)

    positive_contributors = [
        {"feature": feature_names[idx], "impact": float(shap_values[idx])}
        for idx in range(len(feature_names))
        if shap_values[idx] > 0
    ]
    positive_contributors.sort(key=lambda item: item["impact"], reverse=True)
    positive_contributors = positive_contributors[:5]

    negative_contributors = [
        {"feature": feature_names[idx], "impact": float(shap_values[idx])}
        for idx in range(len(feature_names))
        if shap_values[idx] < 0
    ]
    negative_contributors.sort(key=lambda item: item["impact"])
    negative_contributors = negative_contributors[:5]

    positive_summary = ", ".join(
        f"{item['feature']} ({item['impact']:+.2f})" for item in positive_contributors[:3]
    ) if positive_contributors else "no strong positive drivers"
    negative_summary = ", ".join(
        f"{item['feature']} ({item['impact']:+.2f})" for item in negative_contributors[:3]
    ) if negative_contributors else "no strong negative drivers"

    return {
        "feature_names": feature_names,
        "shap_values": [float(value) for value in shap_values],
        "feature_importance": feature_importance,
        "top_positive_contributors": positive_contributors,
        "top_negative_contributors": negative_contributors,
        "local_explanation": {
            "positive": positive_contributors,
            "negative": negative_contributors,
        },
        "ai_interpretation": (
            "The strongest positive contributors to this prediction were "
            f"{positive_summary}, while the strongest negative contributors were "
            f"{negative_summary}."
        ),
        "status": "success",
    }
