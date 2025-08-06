from pathlib import Path
from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_PATH = Path(__file__).parent.parent.parent


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    endpoint: str = "/endpoint"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class LoggingConfig(BaseModel):
    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"
    log_format: str


class DataBase(BaseModel):
    url: PostgresDsn
    echo: bool
    echo_pool: bool
    pool_size: int
    max_overflow: int


class GunicornConfig(BaseModel):
    host: str
    port: int
    workers: int
    timeout: int


class Links(BaseModel):
    url: str = "https://spimex.com/markets/oil_products/trades/results/?page=page-"
    domain: str = "https://spimex.com/"
    parse_method: str = "lxml"


class Redis(BaseModel):
    url: str = "redis://cache:6379/5"
    dates_key: str = "last_dates"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_PATH / ".template.env",
            BASE_PATH / ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="FASTAPI__",
    )
    gunicorn: GunicornConfig
    db: DataBase
    logging: LoggingConfig
    api: ApiPrefix = ApiPrefix()
    links: Links = Links()
    redis: Redis = Redis()


settings = Settings()
