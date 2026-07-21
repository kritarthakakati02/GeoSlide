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
