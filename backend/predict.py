"""
Module 9.3 - Prediction Engine
GeoSlide Project

This module is responsible ONLY for turning a raw feature list into a
landslide prediction using the previously trained/saved KNN model,
StandardScaler, and feature name list. It contains no API routes and
no Pydantic models — it is a plain, importable prediction function.
"""

from typing import List, Dict, Union

import numpy as np

# Import the model loader functions.
# NOTE: adjust these names if model_loader.py exposes different
# function names for retrieving the model, scaler, and feature list.
from model_loader import get_knn_model, get_scaler, get_feature_names


def _compute_risk_level(probability: float) -> str:
    """
    Map a landslide probability (0.0 - 1.0) to a human-readable
    risk level bucket.

    0-25%   -> Low
    26-50%  -> Moderate
    51-75%  -> High
    76-100% -> Very High
    """
    percentage = probability * 100

    if percentage <= 25:
        return "Low"
    elif percentage <= 50:
        return "Moderate"
    elif percentage <= 75:
        return "High"
    else:
        return "Very High"


def predict_landslide(features: List[float]) -> Dict[str, Union[int, float, str]]:
    """
    Predict landslide occurrence and risk level from a list of input features.

    Args:
        features: A list of numeric feature values, in the same order as
                   the feature names the model was trained on.

    Returns:
        A dictionary with:
            {
                "prediction": int,      # predicted class label
                "probability": float,   # probability of the positive (landslide) class
                "risk_level": str       # Low / Moderate / High / Very High
            }

    Raises:
        ValueError: if input validation fails at any stage.
    """

    # --- Basic input validation -------------------------------------------------
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

    # --- Retrieve model, scaler, and feature names -------------------------------
    model = get_knn_model()
    if model is None:
        raise ValueError("Failed to retrieve the KNN model. Model is not available.")

    scaler = get_scaler()
    if scaler is None:
        raise ValueError("Failed to retrieve the StandardScaler. Scaler is not available.")

    feature_names = get_feature_names()
    if not feature_names:
        raise ValueError("Failed to retrieve feature names. Feature names are not available.")

    # --- Validate feature count against saved feature names -----------------------
    expected_count = len(feature_names)
    provided_count = len(features)

    if provided_count != expected_count:
        raise ValueError(
            f"Feature count mismatch: expected {expected_count} features "
            f"({feature_names}), but received {provided_count} features."
        )

    # --- Convert input into a NumPy array with shape (1, n_features) --------------
    try:
        input_array = np.array(features, dtype=float).reshape(1, -1)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Failed to convert input features to a NumPy array: {exc}")

    # --- Scale the input using the saved scaler ------------------------------------
    try:
        scaled_input = scaler.transform(input_array)
    except Exception as exc:
        raise ValueError(f"Failed to scale input features using the saved scaler: {exc}")

    # --- Predict the class using the KNN model --------------------------------------
    try:
        prediction = model.predict(scaled_input)
    except Exception as exc:
        raise ValueError(f"Failed to generate prediction from the KNN model: {exc}")

    # --- Predict probabilities using predict_proba() ---------------------------------
    try:
        probabilities = model.predict_proba(scaled_input)
    except Exception as exc:
        raise ValueError(f"Failed to generate class probabilities from the KNN model: {exc}")

    # --- Compute the landslide probability (positive class) --------------------------
    # Assumes the positive ("landslide") class is the last column, which is the
    # standard convention for binary classifiers in scikit-learn (classes_[-1]).
    try:
        positive_class_index = list(model.classes_).index(1) if 1 in model.classes_ else -1
        landslide_probability = float(probabilities[0][positive_class_index])
    except Exception as exc:
        raise ValueError(f"Failed to compute the landslide (positive class) probability: {exc}")

    # --- Convert probability into a risk level bucket ----------------------------------
    risk_level = _compute_risk_level(landslide_probability)

    return {
        "prediction": int(prediction[0]),
        "probability": landslide_probability,
        "risk_level": risk_level,
    }
