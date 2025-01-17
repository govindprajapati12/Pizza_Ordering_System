from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CartItemResponse(BaseModel):
    pizza_id: int
    quantity: int
    toppings: Optional[List[int]] = []

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]
    total_price: float
    created_at: datetime

class CartToppingCreate(BaseModel):
    topping_id: int  # The ID of the topping to be added to the cart item
    quantity: int    # The quantity of the topping

class CartItemCreate(BaseModel):
    pizza_id: int             # The ID of the pizza to be added to the cart
    quantity: int             # The quantity of the pizza
    toppings: List[CartToppingCreate]  # A list of toppings to be added to the pizza

    class Config:
        orm_mode = True
