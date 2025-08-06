from datetime import date

from pydantic import BaseModel, Field


class TradingResultResponse(BaseModel):
    id: int
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: int
    total: int
    count: int
    date: date
    created_on: date
    updated_on: date


class LastDatesRequest(BaseModel):
    limit: int = Field(default=10, description="Количество последних торговых дней", gt=0)


class DynamicRequest(BaseModel):
    oil_id: str | None = Field(None, description="Код нефтепродукта")
    delivery_type_id: str | None = Field(None, description="Тип поставки")
    delivery_basis_id: str | None = Field(None, description="Базис поставки")
    start_date: date = Field(..., description="Начальная дата периода")
    end_date: date = Field(..., description="Конечная дата периода")


class TradingResultsRequest(BaseModel):
    oil_id: str | None = Field(None, description="Код нефтепродукта")
    delivery_type_id: str | None = Field(None, description="Тип поставки")
    delivery_basis_id: str | None = Field(None, description="Базис поставки")
