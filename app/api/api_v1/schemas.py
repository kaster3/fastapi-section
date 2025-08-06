from datetime import date, datetime

from pydantic import BaseModel, Field, field_serializer


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

    @field_serializer("date", "created_on", "updated_on")
    def serialize_dates(self, v: date | datetime) -> str:
        return v.isoformat()

    class Config:
        from_attributes = True


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
