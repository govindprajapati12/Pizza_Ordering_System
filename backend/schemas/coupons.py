from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class CouponCreate(BaseModel):
    code: str = Field(..., example="DISCOUNT2025")
    discount: float = Field(..., example=10.0)
    expiration_date: date = Field(..., example="2025-12-31")
    usage_limit: int = Field(..., example=100)

class CouponResponse(BaseModel):
    id: int
    code: str
    discount: float
    expiration_date: date
    usage_limit: int

    class Config:
        orm_mode = True
