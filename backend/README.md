# GeoSlide Backend

This directory contains the backend project structure for GeoSlide, an
application focused on landslide susceptibility prediction.

## Current Status

This is the initial project scaffold (Module 9.1). It sets up the basic
FastAPI application structure only. No prediction logic, model loading,
or API endpoints beyond the root health-check route have been implemented
yet.

## Structure

- `app.py` — Minimal FastAPI application with a root endpoint.
- `model_loader.py` — Placeholder for future model loading logic.
- `predict.py` — Placeholder for future prediction logic.
- `schemas.py` — Placeholder for future request/response data schemas.
- `requirements.txt` — Python dependencies for the backend.
- `__init__.py` — Marks this directory as a Python package.

## Running

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then visit `http://127.0.0.1:8000/` to see the health-check message.
