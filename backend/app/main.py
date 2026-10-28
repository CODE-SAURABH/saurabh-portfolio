from fastapi import FastAPI

from app import __version__
from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers
from app.core.middleware import configure_middleware


def create_app() -> FastAPI:
    application = FastAPI(
        title="Saurabh Patil Portfolio API",
        version=__version__,
    )
    configure_middleware(application)
    register_exception_handlers(application)
    application.include_router(api_router, prefix="/api/v1")
    return application


def create_worker_default(application: FastAPI) -> object:
    try:
        from workers import asgi
    except ModuleNotFoundError:
        return None
    return asgi.entrypoint(application)


app = create_app()
Default = create_worker_default(app)
