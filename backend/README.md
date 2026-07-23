# GeoSlide Backend

FastAPI service that loads the trained GeoSlide model artifacts and
exposes a `/predict` endpoint used by the Streamlit frontend.

## Structure

- `app.py` — FastAPI application: lifespan model loading, health-check
  route, and the `/predict` endpoint.
- `model_loader.py` — Loads the KNN model, RF/SHAP explainer, scaler,
  feature names, and metadata from `../models/`.
- `predict.py` — Turns a raw feature list into a prediction, probability,
  and risk level using the loaded KNN model + scaler.
- `schemas.py` — Pydantic request/response schemas (`PredictionRequest`,
  `PredictionResponse`).
- `requirements.txt` — Python dependencies for the backend.
- `__init__.py` — Marks this directory as a Python package.

## Running

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then visit `http://127.0.0.1:8000/` to see the health-check message, or
`http://127.0.0.1:8000/docs` for interactive API docs.

### `POST /predict`

Request body:

```json
{ "features": [45.0, 32.0, 68.0, "... 34 values total, in the exact order of models/feature_names.pkl"] }
```

Response body:

```json
{ "prediction": 1, "probability": 0.87, "risk_level": "Very High" }
```

The Streamlit frontend (`frontend/utils/api.py`) points at this service
via the `GEOSLIDE_API_URL` environment variable, defaulting to
`http://127.0.0.1:8000`.
