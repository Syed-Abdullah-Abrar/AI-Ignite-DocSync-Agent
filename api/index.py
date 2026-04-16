"""
Vercel Serverless Entry Point

Wraps the FastAPI app for Vercel's Python runtime.
Vercel expects a `handler` or a FastAPI/ASGI app in api/index.py.
"""
import sys
import os

# Add project root to Python path so `from src.*` imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set environment to signal we're on Vercel (no SQLite persistence)
os.environ.setdefault("VERCEL", "1")

from src.api.main import app

# Vercel expects the app object named `app` or a handler function
# FastAPI is ASGI-compatible, Vercel's Python runtime handles it
