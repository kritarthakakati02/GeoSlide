"""
GeoSlide API entrypoint.

Only responsibility added here (Module 9.2 integration):
    - Load models on startup via a FastAPI lifespan context manager.
    - Fail fast (stop the application) if model loading fails.

No prediction logic or additional endpoints are implemented here.
"""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from model_loader import load_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load all GeoSlide models before accepting requests.
    try:
        load_models()
    except FileNotFoundError as e:
        print(f"Failed to load GeoSlide models: {e}")
        sys.exit(1)

    yield

    # Shutdown: nothing to clean up for Module 9.2.


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "GeoSlide API is running."}
