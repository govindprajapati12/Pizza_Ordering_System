
from pydantic import BaseModel

class ToppingBase(BaseModel):
    name: str
    price: float

class ToppingCreate(ToppingBase):
    pass

class ToppingResponse(ToppingBase):
    id: int

    class Config:
        orm_mode = True
