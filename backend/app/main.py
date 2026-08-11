"""
ForgeHub AI — FastAPI Application Entry Point
"""
from __future__ import annotations

from fastapi import FastAPI, APIRouter
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
# On Vercel, frontend and backend are on the same domain so CORS isn't an issue
# for same-origin calls. Extra origins listed for local dev and preview deploys.
_origins = [
    settings.frontend_origin,
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # all Vercel preview + prod URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────────────────────
# Mount routers at both root and /api prefix for compatibility across all environments
api_router = APIRouter(prefix="/api")
api_router.include_router(datasets.router)
api_router.include_router(generation.router)
api_router.include_router(validation.router)
api_router.include_router(publish.router)

app.include_router(api_router)
app.include_router(datasets.router)
app.include_router(generation.router)
app.include_router(validation.router)
app.include_router(publish.router)


@app.get("/health", tags=["health"])
@app.get("/api/health", tags=["health"])
def health():
    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "llm_provider": settings.llm_provider,
        "version": "1.0.0",
    }

