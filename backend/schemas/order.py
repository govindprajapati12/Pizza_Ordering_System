from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .cart import CartToppingCreate
from datetime import date

class OrderItemResponse(BaseModel):
    pizza_id: int
    quantity: int
    toppings: Optional[List[int]] = []

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]


class OrderItemCreate(BaseModel):
    pizza_id: int     # The ID of the pizza
    quantity: int     # The quantity of the pizza
    toppings: List[CartToppingCreate]  # A list of toppings associated with the pizza

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    user_id: int                      # The user ID for the order
    cart_id: int                      # The ID of the user's cart
    coupon_code: Optional[str] = None  # An optional coupon code
    order_items: List[OrderItemCreate] # The list of order items
    total_price: float                # The total price of the order
    created_at: Optional[date] = None  # Optional order creation date

    class Config:
        orm_mode = True