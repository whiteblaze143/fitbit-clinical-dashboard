from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from backend.db.database import engine, Base
from backend.routers import api

# Create tables
Base.metadata.create_all(bind=engine)

from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

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

@app.exception_handler(StarletteHTTPException)
async def spa_fallback(request, exc):
    if exc.status_code == 404 and not request.url.path.startswith("/api"):
        index_path = frontend_build_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

if frontend_build_path.exists():
    app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"message": "API is running, but frontend build was not found."}
