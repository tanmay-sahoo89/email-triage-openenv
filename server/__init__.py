"""OpenEnv server package - exposes the FastAPI application entry point."""

from server.app import app, main

__all__ = ["app", "main"]
