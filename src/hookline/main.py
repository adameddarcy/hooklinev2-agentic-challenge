"""Application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from hookline import __version__
from hookline.config import Settings, get_settings
from hookline.db import Base, make_engine, make_session_factory
from hookline.routers import deliveries, events, subscriptions
from hookline.services.dispatcher import Dispatcher


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application.

    The database and HTTP client are created in the lifespan handler and kept on
    ``app.state``, so tests can build an isolated app with their own settings.
    """
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = make_engine(settings.database_url)
        Base.metadata.create_all(engine)
        app.state.session_factory = make_session_factory(engine)
        async with httpx.AsyncClient(headers={"User-Agent": settings.user_agent}) as client:
            app.state.dispatcher = Dispatcher(
                client, timeout_seconds=settings.delivery_timeout_seconds
            )
            yield
        engine.dispose()

    app = FastAPI(title="Hookline", version=__version__, lifespan=lifespan)
    app.include_router(subscriptions.router)
    app.include_router(events.router)
    app.include_router(deliveries.router)

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
