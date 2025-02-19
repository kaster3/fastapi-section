import logging

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.db_helper import DataBaseHelper
from app.core.database.models.base import Base
from tests.core.settings import TestSettings

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture()
async def init_models(db_helper: DataBaseHelper):
    async with db_helper.engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with db_helper.engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await db_helper.dispose()


@pytest_asyncio.fixture()
async def settings() -> TestSettings:
    return TestSettings()


@pytest_asyncio.fixture()
async def db_helper(settings: TestSettings) -> DataBaseHelper:
    return DataBaseHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
    )


@pytest_asyncio.fixture()
async def db_session(db_helper: DataBaseHelper) -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session
