"""OpenEnv server entry point.

This module exposes the FastAPI ``app`` instance expected by the OpenEnv
runtime (``server.app:app``) and a ``main()`` callable used by the
``[project.scripts]`` ``server`` entry point.

The actual environment, routes, and lifespan handlers live in
``src/server.py``. This module simply re-exports them so the project
satisfies the OpenEnv multi-mode deployment layout
(``server/app.py`` with a top-level ``app`` ASGI application).
"""

from __future__ import annotations

import os

# Re-export the FastAPI application from the existing src/server.py module.
# OpenEnv discovers the ASGI app via ``server.app:app``.
from src.server import app, start_server

__all__ = ["app", "main", "start_server"]


def main() -> None:
    """Console-script entry point for ``server`` defined in pyproject.toml.

    Reads ``HOST`` and ``PORT`` environment variables (with sensible defaults
    matching the Hugging Face Spaces convention) and starts the FastAPI
    application via uvicorn.
    """
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "7860"))
    start_server(host=host, port=port)


if __name__ == "__main__":
    main()
