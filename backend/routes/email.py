from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models .models import Order, OrderItem, OrderTopping
from db.config import get_db
from services.email import send_email, generate_order_email,send_order_confirmation_service
from utils.dependencies import user_required

router = APIRouter()

 

@router.post("/order/confirm/{order_id}",dependencies=[Depends(user_required)])
async def send_order_confirmation(order_id: int, db: Session = Depends(get_db)):
    try:
        return await send_order_confirmation_service(order_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))