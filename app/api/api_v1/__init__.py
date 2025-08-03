from fastapi import APIRouter

from app.core import settings

from .some_endpoint import router as endpoint
from .trading import router as trading

router = APIRouter(
    prefix=settings.api.v1.prefix,
)

for rout in (endpoint, trading):
    router.include_router(
        router=rout,
    )


@router.get("")
async def root():
    return {"message": "this path is http://127.0.0.1:8000/api/v1"}
