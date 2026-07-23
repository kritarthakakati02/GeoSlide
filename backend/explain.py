"""
Module 9.6 - Explainability Engine
GeoSlide Project

This module is responsible ONLY for turning a raw feature list into a
real SHAP-based explanation, using the previously trained/saved Random
Forest explainer model, the shared StandardScaler, and the shared
feature name list. It contains no API routes and no Pydantic models —
it is a plain, importable explanation function, mirroring predict.py.

IMPORTANT: The Random Forest model loaded here is used exclusively to
generate SHAP explanations (via shap.TreeExplainer). It does NOT
replace the KNN model, which remains the deployed prediction model
(see predict.py). Per notebooks/07_shap_explainability.ipynb, both KNN
and the Random Forest explainer were trained on the same standardized
feature set, so SHAP attributions from the Random Forest are a
faithful, transferable proxy for understanding which sensor signals
drive risk.

Performance note (per explicit project requirement): global feature
importance is expensive to compute (it requires running SHAP over a
sample of the training set), so it is computed lazily on the FIRST
/explain request only, then cached in memory for the lifetime of the
process. It is never recomputed at startup and never recomputed per
request. Local SHAP values for the specific prediction being explained
are always computed fresh, since they are cheap (a single instance)
and must reflect the exact input given.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import shap

from model_loader import get_feature_names, get_rf_model, get_scaler

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
TRAINING_DATASET_PATH = (BASE_DIR / ".." / "datasets" / "wsn_landslide_data.csv").resolve()

# Number of top positive/negative contributors to surface per explanation.
_TOP_N_CONTRIBUTORS = 5

# Sample size used to compute global feature importance once. Large
# enough to be representative of the ~10k-row training set, small
# enough to stay fast for a live demo.
_GLOBAL_IMPORTANCE_SAMPLE_SIZE = 200

# ----------------------------------------------------------------------
# Module-level caches. Built once, reused for the lifetime of the
# process - never rebuilt per-request.
# ----------------------------------------------------------------------
_explainer = None
_global_importance_cache: Optional[List[Dict[str, float]]] = None


def _get_explainer():
    """Lazily build (and cache) the shap.TreeExplainer for the RF model."""
    global _explainer
    if _explainer is None:
        _explainer = shap.TreeExplainer(get_rf_model())
    return _explainer


def _select_positive_class_values(shap_values_ndarray: np.ndarray, rf_model) -> np.ndarray:
    """
    Normalize raw shap.Explanation.values to the positive ("landslide")
    class, handling both the 3-D (samples, features, classes) output
    produced for a binary RandomForestClassifier and the 2-D fallback.
    """
    if shap_values_ndarray.ndim == 3:
        classes = list(rf_model.classes_)
        positive_class_index = classes.index(1) if 1 in classes else -1
        return shap_values_ndarray[:, :, positive_class_index]
    return shap_values_ndarray


def _compute_global_feature_importance() -> List[Dict[str, float]]:
    """
    Compute mean |SHAP value| per feature across a representative
    sample of the real training dataset (datasets/wsn_landslide_data.csv).
    This is the expensive step this module is designed to run only
    once - callers must go through get_global_feature_importance().
    """
    rf_model = get_rf_model()
    scaler = get_scaler()
    feature_names = get_feature_names()

    if not TRAINING_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Training dataset not found at '{TRAINING_DATASET_PATH}'. "
            "Cannot compute global SHAP feature importance."
        )

    training_df = pd.read_csv(TRAINING_DATASET_PATH)

    missing_cols = [name for name in feature_names if name not in training_df.columns]
    if missing_cols:
        raise ValueError(
            f"Training dataset is missing expected feature column(s): {missing_cols}"
        )

    sample_size = min(_GLOBAL_IMPORTANCE_SAMPLE_SIZE, len(training_df))
    sample_df = training_df[feature_names].sample(n=sample_size, random_state=42)

    scaled_sample = scaler.transform(sample_df.to_numpy(dtype=float))
    scaled_sample_df = pd.DataFrame(scaled_sample, columns=feature_names)

    explainer = _get_explainer()
    shap_result = explainer(scaled_sample_df)
    positive_values = _select_positive_class_values(shap_result.values, rf_model)

    mean_abs_shap = np.abs(positive_values).mean(axis=0)

    importance = [
        {"feature": name, "importance": float(score)}
        for name, score in zip(feature_names, mean_abs_shap)
    ]
    importance.sort(key=lambda item: item["importance"], reverse=True)
    return importance


def get_global_feature_importance() -> List[Dict[str, float]]:
    """
    Return the cached global SHAP feature importance, computing it
    once on first call and reusing it for the lifetime of the process.
    """
    global _global_importance_cache
    if _global_importance_cache is None:
        _global_importance_cache = _compute_global_feature_importance()
    return _global_importance_cache


def _build_ai_interpretation(top_positive: List[Dict], top_negative: List[Dict]) -> str:
    """
    Compose a short natural-language summary of the top real SHAP
    contributors for this prediction. Purely a text rendering of
    already-computed SHAP values - no synthetic/placeholder content.
    """
    if not top_positive and not top_negative:
        return "No individual feature pushed this prediction strongly in either direction."

    sentences = []

    if top_positive:
        described = ", ".join(
            f"{item['feature']} (+{item['impact']:.3f})" for item in top_positive[:3]
        )
        sentences.append(f"Factors increasing landslide risk: {described}.")

    if top_negative:
        described = ", ".join(
            f"{item['feature']} ({item['impact']:.3f})" for item in top_negative[:3]
        )
        sentences.append(f"Factors decreasing landslide risk: {described}.")

    return " ".join(sentences)


def explain_landslide(features: List[float]) -> Dict[str, Union[list, dict, str]]:
    """
    Compute a real SHAP-based explanation for a single landslide risk
    prediction, using the trained Random Forest explainability model.

    Args:
        features: A list of numeric feature values, in the same order
                   as the feature names the models were trained on
                   (identical shape/order to the /predict endpoint).

    Returns:
        A dictionary with:
            {
                "status": str,
                "feature_names": List[str],
                "shap_values": List[float],            # per-feature SHAP value for this instance
                "feature_importance": List[Dict],       # cached global mean(|SHAP|) ranking
                "local_explanation": {
                    "positive": List[Dict],
                    "negative": List[Dict],
                },
                "top_positive_contributors": List[Dict],
                "top_negative_contributors": List[Dict],
                "ai_interpretation": str,
            }

    Raises:
        ValueError: if input validation fails at any stage.
    """

    # --- Basic input validation (mirrors predict.py) -----------------------------
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

    # --- Retrieve model, scaler, and feature names --------------------------------
    rf_model = get_rf_model()
    if rf_model is None:
        raise ValueError("Failed to retrieve the Random Forest explainability model.")

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

    # --- Scale the input using the same saved scaler used for KNN -----------------
    # The Random Forest explainer was trained on StandardScaler-transformed
    # features (see notebooks/07_shap_explainability.ipynb), so the same
    # transform is required here for SHAP values to be meaningful.
    try:
        input_df = pd.DataFrame([features], columns=feature_names)
        scaled_array = scaler.transform(input_df)
        scaled_df = pd.DataFrame(scaled_array, columns=feature_names)
    except Exception as exc:
        raise ValueError(f"Failed to scale input features using the saved scaler: {exc}")

    # --- Compute real LOCAL SHAP values for this instance (always fresh) -----------
    try:
        explainer = _get_explainer()
        shap_result = explainer(scaled_df)
        positive_values = _select_positive_class_values(shap_result.values, rf_model)
        instance_shap_values = [float(v) for v in positive_values[0]]
    except Exception as exc:
        raise ValueError(f"Failed to compute SHAP values from the Random Forest model: {exc}")

    # --- Global feature importance (cached after the first request only) -----------
    try:
        feature_importance = get_global_feature_importance()
    except Exception as exc:
        raise ValueError(f"Failed to compute global feature importance: {exc}")

    # --- Local (per-instance) contributors, split by sign --------------------------
    contributions = list(zip(feature_names, instance_shap_values))
    positive_contributions = sorted(
        (c for c in contributions if c[1] > 0), key=lambda c: c[1], reverse=True
    )
    negative_contributions = sorted(
        (c for c in contributions if c[1] < 0), key=lambda c: c[1]
    )

    top_positive_contributors = [
        {"feature": name, "impact": value} for name, value in positive_contributions[:_TOP_N_CONTRIBUTORS]
    ]
    top_negative_contributors = [
        {"feature": name, "impact": value} for name, value in negative_contributions[:_TOP_N_CONTRIBUTORS]
    ]

    ai_interpretation = _build_ai_interpretation(top_positive_contributors, top_negative_contributors)

    return {
        "status": "success",
        "feature_names": feature_names,
        "shap_values": instance_shap_values,
        "feature_importance": feature_importance,
        "local_explanation": {
            "positive": top_positive_contributors,
            "negative": top_negative_contributors,
        },
        "top_positive_contributors": top_positive_contributors,
        "top_negative_contributors": top_negative_contributors,
        "ai_interpretation": ai_interpretation,
    }
