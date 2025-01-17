from pydantic import BaseModel
from typing import Optional

# Request schema for creating or updating a pizza
class PizzaCreateUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]

# Response schema for retrieving a pizza
class PizzaResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image: Optional[str]
    price: float

    class Config:
        orm_mode = True
