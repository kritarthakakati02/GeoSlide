"""
Module 9.2 - Model Loader
==========================
Responsible ONLY for locating, loading, and exposing GeoSlide's trained
model artifacts. Contains no prediction logic and no API endpoints.

Artifacts loaded from ../models/ (relative to this file):
    - knn_model.joblib
    - rf_explainer.joblib
    - scaler.joblib
    - feature_names.pkl
    - metadata.json
"""

import json
import pickle
from pathlib import Path

import joblib

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = (BASE_DIR / ".." / "models").resolve()

KNN_MODEL_PATH = MODELS_DIR / "knn_model.joblib"
RF_EXPLAINER_PATH = MODELS_DIR / "rf_explainer.joblib"
SCALER_PATH = MODELS_DIR / "scaler.joblib"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.pkl"
METADATA_PATH = MODELS_DIR / "metadata.json"

# ----------------------------------------------------------------------
# Module-level storage for loaded artifacts
# ----------------------------------------------------------------------
_knn_model = None
_rf_model = None
_scaler = None
_feature_names = None
_metadata = None
_models_loaded = False


def _require_file(path: Path) -> Path:
    """Ensure a required artifact file exists, otherwise raise a clear error."""
    if not path.exists():
        raise FileNotFoundError(
            f"Required GeoSlide model file not found: '{path}'. "
            f"Expected it inside the models directory: '{MODELS_DIR}'."
        )
    return path


def load_models() -> None:
    """
    Load all GeoSlide model artifacts into module-level variables.

    Raises:
        FileNotFoundError: if any required artifact file is missing.
    """
    global _knn_model, _rf_model, _scaler, _feature_names, _metadata, _models_loaded

    _knn_model = joblib.load(_require_file(KNN_MODEL_PATH))
    _rf_model = joblib.load(_require_file(RF_EXPLAINER_PATH))
    _scaler = joblib.load(_require_file(SCALER_PATH))

    with open(_require_file(FEATURE_NAMES_PATH), "rb") as f:
        _feature_names = pickle.load(f)

    with open(_require_file(METADATA_PATH), "r") as f:
        _metadata = json.load(f)

    _models_loaded = True
    print("All GeoSlide models loaded successfully.")


def _ensure_loaded() -> None:
    if not _models_loaded:
        raise RuntimeError(
            "Models have not been loaded yet. Call load_models() first."
        )


def get_knn_model():
    """Return the loaded KNN model."""
    _ensure_loaded()
    return _knn_model


def get_rf_model():
    """Return the loaded Random Forest explainer model."""
    _ensure_loaded()
    return _rf_model


def get_scaler():
    """Return the loaded feature scaler."""
    _ensure_loaded()
    return _scaler


def get_feature_names():
    """Return the loaded feature names."""
    _ensure_loaded()
    return _feature_names


def get_metadata():
    """Return the loaded metadata dictionary."""
    _ensure_loaded()
    return _metadata
