"""
Module 9.5 - Prediction API

FastAPI application entrypoint for the GeoSlide service.

This module wires together the application lifespan (model loading),
the root health-check endpoint, and the prediction endpoint.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from explain import explain_landslide
from model_loader import load_models
from predict import predict_landslide
from schemas import ExplainResponse, PredictionRequest, PredictionResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events.

    Loads the landslide prediction model into memory when the
    application starts, and makes it available for the lifetime
    of the app.
    """
    load_models()
    yield


app = FastAPI(title="GeoSlide API", lifespan=lifespan)


@app.get("/")
async def root():
    """
    Root health-check endpoint.

    Returns a simple status message confirming the API is running.
    """
    return {"status": "GeoSlide API is running"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Generate a landslide risk prediction from input features.

    Accepts a PredictionRequest containing the ordered feature values
    expected by the model, runs inference via predict_landslide, and
    returns a PredictionResponse with the prediction, probability,
    and risk level.

    Raises:
        HTTPException(400): If the provided features are invalid.
        HTTPException(500): If an unexpected error occurs during prediction.
    """
    try:
        result = predict_landslide(request.features)
        return PredictionResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@app.post("/explain", response_model=ExplainResponse)
async def explain(request: PredictionRequest) -> ExplainResponse:
    """
    Generate a real SHAP-based explanation for a set of input features.

    Accepts the same ordered feature vector shape as /predict, runs
    shap.TreeExplainer against the Random Forest explainability model
    (models/rf_explainer.joblib) via explain_landslide, and returns an
    ExplainResponse with SHAP values, global feature importance, and
    the top positive/negative local contributors.

    Note: this endpoint does not use or affect the KNN prediction
    model - it exists purely to explain predictions after the fact.

    Raises:
        HTTPException(400): If the provided features are invalid.
        HTTPException(500): If an unexpected error occurs during explanation.
    """
    try:
        result = explain_landslide(request.features)
        return ExplainResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc
