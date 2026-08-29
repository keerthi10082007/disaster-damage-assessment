"""FastAPI application main module"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os

# Import all routers
from app.api import geocoding, disasters, imagery, detection, damage
from app.api import population, infrastructure, zones, priority, ai, chat

app = FastAPI(
    title="Disaster Damage Assessment API",
    description="AI-Powered Multi-Disaster Damage Assessment and Emergency Response Prioritization System",
    version="0.1.0"
)

# CORS middleware
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
async def root():
    return {
        "status": "running",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Disaster Damage Assessment API - DETECT → ASSESS → PRIORITIZE → RESPOND"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Include all routers
app.include_router(geocoding.router, prefix="/api")
app.include_router(disasters.router, prefix="/api")
app.include_router(imagery.router, prefix="/api")
app.include_router(detection.router, prefix="/api")
app.include_router(damage.router, prefix="/api")
app.include_router(population.router, prefix="/api")
app.include_router(infrastructure.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(priority.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
