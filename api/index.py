"""
Vercel Python serverless entry point for ForgeHub AI backend.
Vercel's @vercel/python runtime imports this file and calls the ASGI app.
"""
import sys
import os

# Make the backend package importable from this entry point
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app  # noqa: F401 — Vercel imports `app` directly
