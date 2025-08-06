from datetime import date

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, status

from app.api.api_v1.schemas import (
    DynamicRequest,
    LastDatesRequest,
    TradingResultResponse,
    TradingResultsRequest,
)
from app.core.services.service import Service

router = APIRouter(
    prefix="/trading",
    tags=["trading"],
)


@router.get(
    path="get_last_trading_dates/",
    response_model=list[date],
    status_code=status.HTTP_200_OK,
)
@inject
async def get_last_trading_dates(
    service: FromDishka[Service], request: LastDatesRequest = Depends()
):
    return await service.get_last_trading_dates(limit=request.limit)


@router.get(
    path="get_dynamics/",
    response_model=list[TradingResultResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def get_dynamics(
    service: FromDishka[Service],
    request: DynamicRequest = Depends(),
):
    results = await service.get_dynamics(request=request)
    return results


@router.get(
    path="get_trading_results/",
    response_model=list[TradingResultResponse],
    status_code=status.HTTP_200_OK,
)
@inject
async def get_trading_results(
    service: FromDishka[Service],
    request: TradingResultsRequest = Depends(),
):
    return await service.get_trading_results(request=request)
