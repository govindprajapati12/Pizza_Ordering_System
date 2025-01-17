import threading
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.cart import CartResponse, CartItemResponse,CartItemCreate
from services.cart import (
    get_cart,
    add_item_to_cart,
    update_cart_item,
    remove_item_from_cart,
    apply_coupon_to_cart,
    checkout_cart,
    remove_coupon_from_cart
)
from services.email import send_order_confirmation_service
from db.config import get_db
from utils.dependencies import user_required
from services.cart import update_order_status
from threading import Thread
router = APIRouter(prefix="/cart")

@router.get("/", dependencies=[Depends(user_required)])
async def get_user_cart(db: Session = Depends(get_db), current_user: dict = Depends(user_required)):
    try:
        cart = await get_cart(current_user.id, db)
        return {"message": "Cart retrieved successfully", "data": cart}
    except Exception as e:
        return {"message": str(e)}

@router.post("/items", dependencies=[Depends(user_required)])
async def add_item_to_user_cart(cart_item: CartItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(user_required)):
    # Call the service function to add items to the cart
    added_item = await add_item_to_cart(current_user.id, cart_item, db)
    print(added_item)
    return {"message": "Item added to cart successfully", "data": added_item}


# Update Cart Item Quantity
@router.put("/items/{cart_item_id}", dependencies=[Depends(user_required)])
async def update_cart_item_quantity(cart_item_id: int,updated_cart_Quantity: int, db: Session = Depends(get_db), current_user: dict = Depends(user_required)):
    cart = await get_cart(current_user.id, db)  # Fetch user's cart
    updated_item = await update_cart_item(cart_item_id,updated_cart_Quantity=updated_cart_Quantity, db=db)  # Update the item quantity
    return {"message": "Cart item updated successfully", "data": updated_item}


@router.delete("/items/{cart_item_id}", dependencies=[Depends(user_required)])
async def remove_item_from_user_cart(
    cart_item_id: int, db: Session = Depends(get_db), current_user: dict = Depends(user_required)
):
    try:
        result = await remove_item_from_cart(cart_item_id=cart_item_id, user_id=current_user.id, db=db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Apply Coupon to Cart
@router.post("/coupons", dependencies=[Depends(user_required)])
async def apply_coupon(cart_coupon: str, db: Session = Depends(get_db),current_user: dict = Depends(user_required)):
    cart = await get_cart(current_user.id, db)
    applied_coupon = await apply_coupon_to_cart(cart["cart_id"], cart_coupon, db)
    return {"message": "Coupon applied successfully", "data": applied_coupon}

# Remove Coupon from Cart
@router.post("/coupons/remove", dependencies=[Depends(user_required)])
async def remove_coupon(db: Session = Depends(get_db),current_user: dict = Depends(user_required)):
    cart = await get_cart(current_user.id, db)
    print('this is cart/////////////',cart["cart_id"])
    removed_coupon = await remove_coupon_from_cart(cart["cart_id"], db)     
    return {"message": "Coupon removed successfully", "data": removed_coupon}   

# Checkout Cart (Placing Order)
@router.post("/checkout", dependencies=[Depends(user_required)])
async def checkout(db: Session = Depends(get_db), current_user: dict = Depends(user_required)):
    cart = await get_cart(current_user.id, db)  # Fetch user's cart
    order = await checkout_cart(cart["cart_id"], db)  # Checkout the cart and place the order

    
    await send_order_confirmation_service(order.id, db)
    # Start a background thread to update the order status
    threading.Thread(target=update_order_status, args=(order.id, db)).start()
     
    return {"message": "Order placed successfully", "data": order}