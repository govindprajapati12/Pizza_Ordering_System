from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.models import Order, OrderItem, OrderTopping, Cart, CartItem, CouponUsage, Pizza, Topping
from schemas.order import OrderCreate

# Create an order based on the cart
async def create_order(cart_id: int, db: Session):
    try:
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            raise Exception("Cart not found.")
        
        order = Order(user_id=cart.user_id, total_price=cart.total_price)
        db.add(order)
        db.commit()
        db.refresh(order)

        for cart_item in cart.cart_items:
            order_item = OrderItem(order_id=order.id, pizza_id=cart_item.pizza_id, quantity=cart_item.quantity)
            db.add(order_item)
            db.commit()

            for cart_topping in cart_item.cart_toppings:
                order_topping = OrderTopping(order_item_id=order_item.id, topping_id=cart_topping.topping_id, quantity=cart_topping.quantity)
                db.add(order_topping)
                db.commit()

        # Clear the coupon usage
        coupon_usage = db.query(CouponUsage).filter(CouponUsage.user_id == cart.user_id).first()
        if coupon_usage:
            db.delete(coupon_usage)
            db.commit()

        return order

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error creating order: {str(e)}")
    
async def get_all_orders_for_user(user_id: int, db: Session):
    try:
        orders = db.query(Order).filter(Order.user_id == user_id).all()
        if not orders:
            return {"message": "No orders found for this user."}

        order_data = []
        for order in orders:
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            order_toppings = db.query(OrderTopping).filter(OrderTopping.order_item_id.in_([item.id for item in order_items])).all()

            order_items_data = []
            for item in order_items:
                pizza = db.query(Pizza).filter(Pizza.id == item.pizza_id).first()
                item_price = (pizza.price * item.quantity) if pizza else 0
                
                item_toppings = []
                total_topping_price = 0
                for topping in order_toppings:
                    if topping.order_item_id == item.id:
                        topping_details = db.query(Topping).filter(Topping.id == topping.topping_id).first()
                        topping_price = (topping_details.price * topping.quantity) if topping_details else 0
                        total_topping_price += topping_price
                        item_toppings.append({
                            "order_item_id": topping.order_item_id,
                            "topping_id": topping.topping_id,
                            "topping_name": topping_details.name if topping_details else None,
                            "quantity": topping.quantity,
                            "price": topping_price,
                        })

                order_items_data.append({
                    "id": item.id,
                    "pizza_id": item.pizza_id,
                    "pizza_name": pizza.name if pizza else None,
                    "quantity": item.quantity,
                    "item_price": item_price,
                    "toppings": item_toppings,
                    "total_topping_price": total_topping_price,
                })

            order_data.append({
                "order_id": order.id,
                "total_price": order.total_price,
                "created_at": order.created_at,
                "status": order.status,
                "items": order_items_data,
            })

        return {"message": "Orders retrieved successfully", "data": order_data}
    
    except SQLAlchemyError as e:
        db.rollback()
        return {"message": f"Error retrieving user orders: {str(e)}", "data": []}
    
async def get_order_by_id(order_id: int, db: Session):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise Exception("Order not found.")

        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        order_toppings = db.query(OrderTopping).filter(OrderTopping.order_item_id.in_([item.id for item in order_items])).all()

        order_items_data = []
        for item in order_items:
            pizza = db.query(Pizza).filter(Pizza.id == item.pizza_id).first()
            item_price = (pizza.price * item.quantity) if pizza else 0

            item_toppings = []
            total_topping_price = 0
            for topping in order_toppings:
                if topping.order_item_id == item.id:
                    topping_details = db.query(Topping).filter(Topping.id == topping.topping_id).first()
                    topping_price = (topping_details.price * topping.quantity) if topping_details else 0
                    total_topping_price += topping_price
                    item_toppings.append({
                        "order_item_id": topping.order_item_id,
                        "topping_id": topping.topping_id,
                        "topping_name": topping_details.name if topping_details else None,
                        "quantity": topping.quantity,
                        "price": topping_price,
                    })

            order_items_data.append({
                "id": item.id,
                "pizza_id": item.pizza_id,
                "pizza_name": pizza.name if pizza else None,
                "quantity": item.quantity,
                "item_price": item_price,
                "toppings": item_toppings,
                "total_topping_price": total_topping_price,
            })

        return {
            "order_id": order.id,
            "total_price": order.total_price,
            "created_at": order.created_at,
            "status": order.status,
            "items": order_items_data,
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error retrieving order by ID: {str(e)}")



async def get_all_orders(db: Session):
    try:
        orders = db.query(Order).all()

        if not orders:
            return {"message": "No orders found.", "data": []}

        order_data = []
        for order in orders:
            # Fetching order items for the current order
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            order_toppings = db.query(OrderTopping).filter(OrderTopping.order_item_id.in_([item.id for item in order_items])).all()

            order_data.append({
                "order": {
                    "id": order.id,
                    "user_id": order.user_id,
                    "total_price": order.total_price,
                    "created_at": order.created_at,
                    "status": order.status,
                },
                "order_items": [
                    {
                        "id": item.id,
                        "pizza_id": item.pizza_id,
                        "quantity": item.quantity
                    } for item in order_items
                ],
                "order_toppings": [
                    {
                        "order_item_id": topping.order_item_id,
                        "topping_id": topping.topping_id,
                        "quantity": topping.quantity
                    } for topping in order_toppings
                ]
            })
        
        return {"message": "Orders retrieved successfully", "data": order_data}

    except SQLAlchemyError as e:
        db.rollback()
        return {"message": f"Error retrieving orders: {str(e)}", "data": []}
    


    # Delete Order for Admin
async def delete_order_for_admin(order_id: int, db: Session):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise Exception("Order not found.")
        
        db.delete(order)
        db.commit()
        return {"message": "Order deleted successfully.", "data": {}}
    
    except SQLAlchemyError as e:
        db.rollback()
        return {"message": f"Error deleting order: {str(e)}", "data": {}}
    


# Update Order Status (Admin only)
async def update_order_status_for_admin(order_id: int, new_status: str, db: Session):
    try:
        # Define the valid statuses
        valid_statuses = ['Received', 'Preparing', 'Baking', 'Ready for Pickup', 'Completed']
        
        # Check if the provided new status is valid
        if new_status not in valid_statuses:
            raise Exception("Invalid order status.")
        
        # Fetch the order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise Exception("Order not found.")
        
        # Update the order status
        order.status = new_status
        db.commit()
        db.refresh(order)
        
        return {"message": "Order status updated successfully", "data": {"order_id": order.id, "status": order.status}}
    
    except SQLAlchemyError as e:
        db.rollback()
        return {"message": f"Error updating order status: {str(e)}", "data": {}}