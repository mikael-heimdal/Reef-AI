from fastapi import FastAPI

from app.db import Base
from app.db import engine

from app.api.measurements import router as measurements_router
from app.api.ghl import router as ghl_router
from app.api.livestock import router as livestock_router

# Skapa databastabeller
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reef AI",
    version="0.2.0",
    description="Reef AI Backend för ProfiLux, KH Director och Dashboard"
)

# Measurements API
app.include_router(measurements_router)

# GHL API
app.include_router(ghl_router)

# Livestock API
app.include_router(livestock_router)


@app.get("/")
def root():
    return {
        "name": "Reef AI",
        "version": "0.2.0",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }