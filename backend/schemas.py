"""
Module 9.4 - API Schemas

This module defines the Pydantic schemas used for validating incoming
prediction requests and structuring outgoing prediction responses for
the GeoSlide API.

No business logic or model inference is implemented here. This module
is strictly responsible for data shape, typing, and documentation.
"""

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """
    Schema representing the input payload for a landslide prediction request.

    Contains the numeric feature values that will be passed to the
    prediction model.
    """

    features: list[float] = Field(
        ...,
        min_length=1,
        description=(
            "List of numeric feature values used for prediction. "
            "Values must be provided in the same order used during "
            "model training."
        ),
    )


class PredictionResponse(BaseModel):
    """
    Schema representing the output payload returned after a landslide
    prediction has been made.

    Contains the predicted class, the associated probability, and a
    human-readable risk level.
    """

    prediction: int = Field(
        ...,
        description="Predicted class label output by the model.",
    )
    probability: float = Field(
        ...,
        description="Probability score associated with the predicted class.",
    )
    risk_level: str = Field(
        ...,
        description="Human-readable risk level derived from the prediction.",
    )


class ExplanationRequest(BaseModel):
    """Schema representing the input payload for a SHAP explanation request."""

    features: list[float] = Field(
        ...,
        min_length=1,
        description=(
            "List of numeric feature values used for explainability. "
            "Values must be provided in the same order used during model training."
        ),
    )


class ExplanationResponse(BaseModel):
    """Schema representing the output payload returned for a SHAP explanation."""

    feature_names: list[str] = Field(..., description="Ordered feature names for the input vector.")
    shap_values: list[float] = Field(..., description="SHAP values for each feature.")
    feature_importance: list[dict[str, float | str]] = Field(
        ..., description="Absolute feature importance ranking derived from SHAP values."
    )
    top_positive_contributors: list[dict[str, float | str]] = Field(
        ..., description="Top features that increase the predicted risk."
    )
    top_negative_contributors: list[dict[str, float | str]] = Field(
        ..., description="Top features that decrease the predicted risk."
    )
    local_explanation: dict[str, list[dict[str, float | str]]] = Field(
        ..., description="Structured positive and negative local explanation values."
    )
    ai_interpretation: str = Field(..., description="Human-readable interpretation of the explanation.")
    status: str = Field(..., description="Status of the explanation generation process.")
