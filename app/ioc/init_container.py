from dishka import AsyncContainer, make_async_container

from app.core import Settings
from app.ioc.sqlalchemy_providers import (
    RedisProvider,
    ServiceProvider,
    SQLAlchemyProvider,
)


def init_async_container(settings: Settings) -> AsyncContainer:
    container = make_async_container(
        SQLAlchemyProvider(),
        ServiceProvider(),
        RedisProvider(),
        context={
            Settings: settings,
        },
    )
    return container
