from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MoneyModel(BaseModel):
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
