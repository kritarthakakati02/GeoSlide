from fastapi import FastAPI

app = FastAPI(title="GeoSlide API")


@app.get("/")
def read_root():
    return {"message": "GeoSlide API is running."}
