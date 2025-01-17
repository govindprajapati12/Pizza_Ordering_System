# app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from services.auth import register_user  # Assuming this function handles user registration
from utils.dependencies import admin_required  # Admin check dependency
from db.config import get_db
from schemas.auth import RegistrationRequest  # Assuming your schema for registration is here
from services.users import get_all_users, get_user_details, get_user_orders ,create_admin_service # Assuming these functions handle user operations
router = APIRouter()

# Create new admin (accessible only by admins)
@router.post("/create_admin", dependencies=[Depends(admin_required)])
async def create_admin(admin_data: RegistrationRequest, db: Session = Depends(get_db)):
    try:
        # Call the service function to create a new admin
        new_admin = await create_admin_service(admin_data, db)
        print(new_admin.role)
        
        return {"message": "Admin created successfully", "data": new_admin}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating admin: {str(e)}")

# Fetch all users (only accessible by admins)
@router.get("/users", dependencies=[Depends(admin_required)])
async def fetch_all_users(db: Session = Depends(get_db)):
    try:
        users = await get_all_users(db)
        return {"message": "All users fetched successfully", "data": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

# Fetch details of a specific user (only accessible by admins)
@router.get("/users/{user_id}", dependencies=[Depends(admin_required)])
async def fetch_user_by_id(user_id: int, db: Session = Depends(get_db)):
    try:
        user = await get_user_details(user_id, db)
        return {"message": f"User {user_id} fetched successfully", "data": user}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching user {user_id}: {str(e)}")

# Fetch orders for a specific user (only accessible by admins)
@router.get("/users/{user_id}/orders", dependencies=[Depends(admin_required)])
async def fetch_user_orders(user_id: int, db: Session = Depends(get_db)):
    try:
        orders = await get_user_orders(user_id, db)
        return {"message": f"Orders for user {user_id} fetched successfully", "data": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders for user {user_id}: {str(e)}")
