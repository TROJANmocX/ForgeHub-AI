"""
ForgeHub AI — FastAPI Application Entry Point
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import datasets, generation, publish, validation
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="ForgeHub AI",
    description="Metadata-Aware AI Data Engineering Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(datasets.router)
app.include_router(generation.router)
app.include_router(validation.router)
app.include_router(publish.router)


@app.get("/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "llm_provider": settings.llm_provider,
        "version": "1.0.0",
    }
