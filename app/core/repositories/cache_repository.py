import asyncio
import json
import logging
from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from redis import asyncio as aioredis

log = logging.getLogger(__name__)


class ICacheRepository(Protocol):
    @abstractmethod
    async def flush_all(self) -> None:
        """Очищаем кэш redis"""
        raise NotImplementedError

    @abstractmethod
    async def schedule_daily_flush(self, hour: int = 14, minute: int = 11) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_cached_data(self, key: str) -> list[str] | None:
        """Получаем все кэшированные данные (или None если кэш пуст)"""
        raise NotImplementedError

    @abstractmethod
    async def set_cached_data(self, data: str, key: str) -> None:
        """Кэшируем полный список данных"""
        raise NotImplementedError


class RedisCacheRepository(ICacheRepository):
    def __init__(self, redis: aioredis.Redis) -> None:
        self.redis = redis

    async def flush_all(self) -> None:
        await self.redis.flushdb()
        logging.info("Cache flushed at %s", datetime.now())

    async def schedule_daily_flush(self, hour: int = 14, minute: int = 11) -> None:
        while True:
            now = datetime.now()
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if now >= target:
                target = target.replace(day=target.day + 1)

            wait_seconds = (target - now).total_seconds()
            logging.info(f"Next cache flush scheduled in {wait_seconds:.0f} seconds")

            await asyncio.sleep(wait_seconds)
            await self.flush_all()

    async def get_cached_data(self, key: str) -> list[str] | None:
        cached_data = await self.redis.get(key)
        if not cached_data:
            log.info("No cached data for key: %s", key)
            return None

        dates = json.loads(cached_data)
        log.info("Retrieved cached data for key: %s", key)
        return dates

    async def set_cached_data(self, data: str, key: str, ttl: int = 60) -> None:
        await self.redis.setex(name=key, time=ttl, value=data)
        log.info("Data cached with key: %s, TTL: %d", key, ttl)
