from datetime import datetime
import time
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from models.models import Cart, CartItem, CartTopping, Order, OrderItem, Coupon, CouponUsage,OrderTopping
from schemas.cart import CartItemCreate, CartToppingCreate
from schemas.order import OrderCreate
from sqlalchemy import func



async def create_cart(user_id: int, db: Session):
    try:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error creating cart: {str(e)}")

# Add an item to the cart
async def add_item_to_cart(user_id: int, cart_item: CartItemCreate, db: Session):
    try:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = await create_cart(user_id, db)
        
        cart_item_obj = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.pizza_id == cart_item.pizza_id
        ).first()

        if cart_item_obj:
            cart_item_obj.quantity += cart_item.quantity
        else:
            cart_item_obj = CartItem(
                cart_id=cart.id,
                pizza_id=cart_item.pizza_id,
                quantity=cart_item.quantity
            )
            db.add(cart_item_obj)
            db.commit()
            db.refresh(cart_item_obj)

        for topping in cart_item.toppings:
            existing_topping = db.query(CartTopping).filter(
                CartTopping.cart_item_id == cart_item_obj.id,
                CartTopping.topping_id == topping.topping_id
            ).first()
            if existing_topping:
                existing_topping.quantity += topping.quantity
            else:
                cart_topping = CartTopping(
                    cart_item_id=cart_item_obj.id,
                    topping_id=topping.topping_id,
                    quantity=topping.quantity
                )
                db.add(cart_topping)

        db.commit()
        db.refresh(cart)
        await update_cart_total_price(cart.id, db)

        return cart_item_obj
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error adding item to cart: {str(e)}")


# Add topping to cart item
async def add_topping_to_cart(cart_item_id: int, topping_id: int, quantity: int, db: Session):
    try:
        cart_topping = CartTopping(cart_item_id=cart_item_id, topping_id=topping_id, quantity=quantity)
        db.add(cart_topping)
        db.commit()
        db.refresh(cart_topping)
        return cart_topping
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error adding topping to cart: {str(e)}")
    
async def get_cart(user_id: int, db: Session):
    try:
        # Fetch the user's cart
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            raise Exception("No active cart found for this user.")

        # Fetch the cart items and their details
        cart_items = []
        for cart_item in cart.cart_items:
            # Get the price and name of each cart item
            pizza = cart_item.pizza
            item_price = pizza.price
            pizza_name = pizza.name

            # Fetch toppings for this item
            toppings = []
            for cart_topping in cart_item.cart_toppings:
                topping = cart_topping.topping
                topping_price = topping.price * cart_topping.quantity
                topping_name = topping.name

                # Include topping details
                toppings.append({
                    "topping_id": cart_topping.topping_id,
                    "topping_name": topping_name,
                    "quantity": cart_topping.quantity,
                    "price": topping_price
                })

            # Add item details to the response
            cart_items.append({
                "cart_item_id": cart_item.id,
                "pizza_id": cart_item.pizza_id,
                "pizza_name": pizza_name,
                "quantity": cart_item.quantity,
                "item_price": item_price,
                "toppings": toppings
            })
        # Return cart details along with the total and discounted prices
        return {
            "cart_id": cart.id,
            "user_id": cart.user_id,
            "created_at": cart.created_at,
            "items": cart_items,
            "total_price": cart.total_price,
            "discounted_price": cart.discounted_price
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error retrieving cart: {str(e)}")


# Apply a coupon to the cart
async def apply_coupon_to_cart(cart_id: int, coupon_code: str, db: Session):
    try:
        coupon = db.query(Coupon).filter(Coupon.code == coupon_code).first()
        if not coupon:
            raise Exception("Coupon not found or expired.")

        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            raise Exception("Cart not found.")

        user = cart.user
        coupon_usage = db.query(CouponUsage).filter(
            CouponUsage.user_id == user.id,
            CouponUsage.coupon_id == coupon.id
        ).first()

        if coupon_usage and coupon_usage.usage_limit == 0:
            raise Exception("Coupon already used by this user.")

        total_price_decimal = Decimal(str(cart.total_price))
        discount_amount = Decimal(str(coupon.discount))
        cart.discounted_price = total_price_decimal - discount_amount

        if not coupon_usage:
            coupon_usage = CouponUsage(
                user_id=user.id,
                coupon_id=coupon.id,
                usage_limit=0,
                used_at=datetime.utcnow()
            )
            db.add(coupon_usage)
        else:
            coupon_usage.usage_limit = 0
            coupon_usage.used_at = datetime.utcnow()

        db.commit()
        db.refresh(cart)
        return cart
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error applying coupon to cart: {str(e)}")


# Remove a coupon from the cart
async def remove_coupon_from_cart(cart_id: int, db: Session):
    try:
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            raise Exception("Cart not found.")

        user = cart.user
        coupon_usage = db.query(CouponUsage).filter(
            CouponUsage.user_id == user.id,
            CouponUsage.usage_limit == 0
        ).first()

        if not coupon_usage:
            raise Exception("No coupon applied to this cart.")

        discount_amount = cart.discounted_price + float(coupon_usage.coupon.discount)
        cart.discounted_price = discount_amount
        coupon_usage.usage_limit = 1
        coupon_usage.used_at = None

        db.commit()
        return {
            "cart_id": cart.id,
            "recalculated_total": cart.total_price,
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error removing coupon from cart: {str(e)}")



# Update the quantity of an item in the cart
async def update_cart_item(cart_item_id: int, updated_cart_Quantity: int, db: Session):
    try:
        cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if not cart_item:
            raise Exception("Cart item not found.")

        # Update the quantity of the cart item
        cart_item.quantity = updated_cart_Quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error updating cart item: {str(e)}")


# Remove item from cart
async def remove_item_from_cart(cart_item_id: int, user_id: int, db: Session):
    try:
        # Fetch the cart item with toppings and pizza details
        cart_item = (
            db.query(CartItem)
            .options(
                joinedload(CartItem.cart_toppings).joinedload(CartTopping.topping),
                joinedload(CartItem.pizza)
            )
            .filter(CartItem.id == cart_item_id)
            .first()
        )

        if not cart_item:
            raise Exception("Cart item not found.")

        # Fetch the associated cart
        cart = db.query(Cart).filter(Cart.id == cart_item.cart_id, Cart.user_id == user_id).first()
        if not cart:
            raise Exception("Cart not found.")

        # Remove the cart item and related toppings
        db.delete(cart_item)
        db.commit()

        # Check if there are remaining items in the cart
        remaining_items = (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart.id)
            .all()
        )

        if not remaining_items:
            # If no items remain, delete the cart
            db.delete(cart)
            db.commit()
            return {"message": "Cart item removed and cart deleted as it was the last item."}

        # Update cart total price and discounted price
        updated_cart = await update_cart_total_price(cart.id, db)
        return {"message": "Cart item removed successfully.", "updated_cart": updated_cart}

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error removing item from cart: {str(e)}")

# Checkout cart and create an order
async def checkout_cart(cart_id: int, db: Session):
    try:
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            raise Exception("Cart not found.")
        if not cart.cart_items:
            raise Exception("Cannot checkout an empty cart.")

        final_price = cart.discounted_price if cart.discounted_price else cart.total_price
        order = Order(user_id=cart.user_id, total_price=final_price)
        db.add(order)
        db.commit()
        db.refresh(order)

        for cart_item in cart.cart_items:
            order_item = OrderItem(
                order_id=order.id,
                pizza_id=cart_item.pizza_id,
                quantity=cart_item.quantity
            )
            db.add(order_item)
            db.commit()  # Commit here to save order_item and populate its id
            db.refresh(order_item)  # Refresh to get the populated id

            for cart_topping in cart_item.cart_toppings:
                order_topping = OrderTopping(
                    order_item_id=order_item.id,  # Now it will have a valid id
                    topping_id=cart_topping.topping_id,
                    quantity=cart_topping.quantity
                )
                db.add(order_topping)

        db.commit()

        # Clean up the cart items and toppings
        db.query(CartTopping).filter(CartItem.cart_id == cart_id).delete(synchronize_session='fetch')
        db.query(CartItem).filter(CartItem.cart_id == cart_id).delete(synchronize_session='fetch')

        db.commit()
        return order
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error during checkout: {str(e)}")


ORDER_STATUSES = ["Received", "Preparing", "Baking", "Ready for Pickup", "Completed"]

def update_order_status(order_id: int, db: Session):
    try:
        for status in ORDER_STATUSES:
            # Pause for 10 seconds between status updates
            time.sleep(5)  # Explicitly call time.sleep
            
            # Update the order status in the database
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                print(f"Order {order_id} not found.")
                return
            
            order.status = status
            db.commit()
            
            # Stop updating if the order is completed
            if status == "Completed":
                break
    except Exception as e:
        print(f"Error updating order status: {str(e)}")


# # Update cart total price
# async def update_cart_total_price(cart_id: int, db: Session):
#     try:
#         cart = db.query(Cart).filter(Cart.id == cart_id).first()
#         if not cart:
#             raise Exception("Cart not found.")
#         cart_total_price = cart.total_price
#         discounted_price = cart.discounted_price
#         discounted_amount = cart.total_price - cart.discounted_price
#         total_price = 0
#         for cart_item in cart.cart_items:
#             pizza = cart_item.pizza
#             total_price += pizza.price * cart_item.quantity
#             for cart_topping in cart_item.cart_toppings:
#                 topping = cart_topping.topping
#                 total_price += topping.price * cart_topping.quantity

#         cart.total_price = total_price
#         cart.discounted_price = float(total_price) - discounted_amount
#         db.commit()
#         db.refresh(cart)
#         return total_price
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise Exception(f"Error updating cart total price: {str(e)}")


# Update cart total price
async def update_cart_total_price(cart_id: int, db: Session):
    try:
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            raise Exception("Cart not found.")

        discounted_amount = cart.total_price - cart.discounted_price
        total_price = 0

        # Calculate total price of all items in the cart
        for cart_item in cart.cart_items:
            pizza_price = cart_item.pizza.price if cart_item.pizza else 0
            print(pizza_price)
            toppings_price = sum(
                (topping.topping.price if topping.topping else 0) * topping.quantity
                for topping in cart_item.cart_toppings
            )
            total_price += (pizza_price * cart_item.quantity) + toppings_price

        # Update cart total and discounted prices
        cart.total_price = total_price
        cart.discounted_price = max(0, float(total_price) - discounted_amount)  # Ensure non-negative discounted price
        db.commit()
        db.refresh(cart)
        return cart
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error updating cart total price: {str(e)}")
