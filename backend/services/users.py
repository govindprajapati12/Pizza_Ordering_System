# app/services/admin.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.models import User, Order
from sqlalchemy.exc import SQLAlchemyError
from services.auth import register_user



async def create_admin_service(admin_data, db: Session):
    try:
        # Register a new user using the existing register_user function
        new_admin = await register_user(admin_data, db)
        
        # Set the user's role to 'admin'
        new_admin.role = "admin"
        
        # Commit the changes to the database
        db.commit()
        db.refresh(new_admin)
        
        return new_admin  # Return the updated admin object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating admin: {str(e)}")
    
# Get all users from the database
async def get_all_users(db: Session):
    try:
        # Fetch all users and return them as dictionaries
        users = db.query(User).all()
        return [{"id": user.id, "username": user.name, "email": user.email,"role":user.role} for user in users]
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching users: {str(e)}")

# Get details of a specific user by user_id
async def get_user_details(user_id: int, db: Session):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Return the user details as a dictionary
        return {"id": user.id, "username": user.name, "email": user.email,"role":user.role}
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching user details: {str(e)}")

# Get all orders of a specific user
async def get_user_orders(user_id: int, db: Session):
    try:
        orders = db.query(Order).filter(Order.user_id == user_id).all()
        # Return a list of orders as dictionaries
        return [{"id": order.id, "total_price": order.total_price, "status": order.status, "created_at": order.created_at} for order in orders]
    except SQLAlchemyError as e:
        raise Exception(f"Error fetching user orders: {str(e)}")
