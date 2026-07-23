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
from schemas import ExplanationRequest, ExplanationResponse, PredictionRequest, PredictionResponse


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


@app.post("/explain", response_model=ExplanationResponse)
async def explain(request: ExplanationRequest) -> ExplanationResponse:
    """
    Compute SHAP-based explainability values for a single input feature vector.

    This endpoint uses the existing Random Forest explainer model and returns
    the feature names, the raw SHAP values, the top positive contributors,
    the top negative contributors, and an AI-style interpretation.
    """
    try:
        result = explain_landslide(request.features)
        return ExplanationResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc
