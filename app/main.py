from fastapi import FastAPI

from app.db import Base
from app.db import engine

from app.api.measurements import router as measurements_router

# Skapa databastabeller vid uppstart
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reef AI",
    version="0.1.0",
    description="AI Backend för GHL ProfiLux och Reef Systems"
)

# Routers
app.include_router(
    measurements_router
)

# Root endpoint
@app.get("/")
def root():
    return {
        "name": "Reef AI",
        "status": "online",
        "version": "0.1.0"
    }

# Healthcheck
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }