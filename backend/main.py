from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from backend.db.database import engine, Base
from backend.routers import api

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fitbit Clinical Dashboard API")

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)

# Mount frontend build if it exists
frontend_build_path = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_build_path.exists():
    app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"message": "API is running, but frontend build was not found."}
