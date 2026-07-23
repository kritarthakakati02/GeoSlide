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


class FeatureImportanceItem(BaseModel):
    """A single feature's global importance score (mean |SHAP value| across a cached sample of the training data)."""

    feature: str = Field(..., description="Feature name.")
    importance: float = Field(..., description="Global importance score for this feature.")


class ContributorItem(BaseModel):
    """A single feature's local SHAP contribution to one specific prediction."""

    feature: str = Field(..., description="Feature name.")
    impact: float = Field(..., description="Signed SHAP value: positive increases risk, negative decreases it.")


class LocalExplanation(BaseModel):
    """Top features pushing a single prediction higher (positive) or lower (negative)."""

    positive: list[ContributorItem] = Field(default_factory=list)
    negative: list[ContributorItem] = Field(default_factory=list)


class ExplainResponse(BaseModel):
    """
    Schema representing the output payload returned by the SHAP
    explainability endpoint for a single input feature vector.
    """

    status: str = Field(..., description="'success' if the explanation was computed successfully.")
    feature_names: list[str] = Field(..., description="Feature names, in model order.")
    shap_values: list[float] = Field(
        ..., description="Signed SHAP value per feature for this specific instance (positive class)."
    )
    feature_importance: list[FeatureImportanceItem] = Field(
        ..., description="Cached global SHAP feature importance ranking, computed once from a training data sample."
    )
    local_explanation: LocalExplanation = Field(
        ..., description="Top positive/negative contributors for this specific prediction."
    )
    top_positive_contributors: list[ContributorItem] = Field(default_factory=list)
    top_negative_contributors: list[ContributorItem] = Field(default_factory=list)
    ai_interpretation: str = Field(
        ..., description="Natural-language summary of the top drivers behind this prediction."
    )
