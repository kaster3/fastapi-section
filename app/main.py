import logging
from asyncio import create_task
from contextlib import asynccontextmanager

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api import router as api_router
from app.core import Settings
from app.core.gunicorn import Application, get_app_options
from app.core.repositories.cache_repository import ICacheRepository
from app.core.services.service import Service
from app.ioc.init_container import init_async_container


@asynccontextmanager
async def lifespan(app: FastAPI):
    container: AsyncContainer = app.state.dishka_container
    async with container() as requested_container:
        service = await requested_container.get(Service)
        cache = await requested_container.get(ICacheRepository)
        await service.load_docs_in_db()
        create_task(cache.schedule_daily_flush())

    logging.info("Application starts successfully!")
    yield
    logging.info("Shutting down application...")
    await app.state.dishka_container.close()
    logging.info("Application ends successfully!")


def create_fastapi_app() -> FastAPI:
    """Создаем FastAPI приложение и настраиваем его на роутеры"""
    app = FastAPI(
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )
    app.include_router(
        router=api_router,
    )
    return app


def create_app(settings: Settings) -> FastAPI:
    """Настраиваем логи, контейнер с зависимостями и инициализируем наше приложение"""
    logging.basicConfig(
        level=settings.logging.log_level,
        format=settings.logging.log_format,
    )
    app = create_fastapi_app()
    container = init_async_container(settings=settings)
    setup_dishka(container, app)
    return app


# Запускаем приложение с uvicorn воркерами и gunicorn менеджера
if __name__ == "__main__":
    settings = Settings()
    Application(
        application=create_app(settings=settings),
        options=get_app_options(
            host=settings.gunicorn.host,
            port=settings.gunicorn.port,
            timeout=settings.gunicorn.timeout,
            workers=settings.gunicorn.workers,
            log_level=settings.logging.log_level,
        ),
    ).run()
