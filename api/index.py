"""Vercel FastAPI entrypoint.

Vercel looks for a module like `api/index.py` that exposes a FastAPI
application instance named `app`. This file re-exports the `app`
defined in `api/api.py` so the deployment platform can find it.
"""
from api.api import app  # re-export the FastAPI app defined in api/api.py
