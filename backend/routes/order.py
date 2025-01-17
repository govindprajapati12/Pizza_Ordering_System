from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.order import OrderResponse, OrderItemResponse
from services.order import (
    create_order,
    get_order_by_id,
    get_all_orders,
    get_all_orders_for_user,
    delete_order_for_admin,
    update_order_status_for_admin
)
from db.config import get_db
from utils.dependencies import admin_required, user_required

router = APIRouter(prefix="/orders")

# Create an Order (Checkout)
@router.post("/", dependencies=[Depends(user_required)])
async def place_order(order_data: OrderItemResponse, db: Session = Depends(get_db)):
    order = await create_order(order_data.cart_id, db)
    return {"message": "Order placed successfully", "data": order}


# Get All Orders (Admin Only)
@router.get("/all", dependencies=[Depends(admin_required)])
async def get_orders(db: Session = Depends(get_db)):
    try:
        # Call the service function to fetch orders
        response = await get_all_orders(db)
        
        # If no orders are found, this will be handled in the service function itself
        if response["message"] == "No orders found.":
            return {"message": response["message"], "data": []}
        
        # Otherwise, return the successful response with data
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving orders: {str(e)}")


# Get All Orders for a Specific User (User Only)
@router.get("/my-orders", dependencies=[Depends(user_required)])
async def get_user_orders(db: Session = Depends(get_db), current_user=Depends(user_required)):
    orders = await get_all_orders_for_user(current_user.id, db)
    return {"message": "User orders retrieved successfully", "data": orders}


# Get Order by ID (User & Admin)
@router.get("/{order_id}")
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = await get_order_by_id(order_id, db)
    return {"message": "Order retrieved successfully", "data": order}

# Update Order Status (Admin Only)
@router.put("/{order_id}/status", dependencies=[Depends(admin_required)])
async def update_order_status(order_id: int, new_status: str, db: Session = Depends(get_db)):
    result = await update_order_status_for_admin(order_id, new_status, db)
    if result["message"] == "Order status updated successfully":
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])


# Delete Order for Admin (Admin Only)
@router.delete("/{order_id}", dependencies=[Depends(admin_required)])
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    result = await delete_order_for_admin(order_id, db)
    if result["message"] == "Order deleted successfully.":
        return {"message": "Order deleted successfully."}
    else:
        raise HTTPException(status_code=500, detail=result["message"])