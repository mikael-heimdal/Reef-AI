from fastapi import FastAPI

from app.db import Base
from app.db import engine

from app.api.measurements import (
    router as measurements_router
)

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="Reef AI",
    version="0.1.0"
)

app.include_router(
    measurements_router
)


@app.get("/")
def root():

    return {
        "name": "Reef AI",
        "status": "online"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }