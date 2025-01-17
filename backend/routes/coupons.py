from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.coupons import CouponCreate, CouponResponse
from services.coupons import (
    create_new_coupon,
    get_all_coupons,
    get_coupon_by_id,
    update_existing_coupon,
    delete_coupon,
    get_user_active_coupons
)
from db.config import get_db
from utils.dependencies import admin_required,user_required

router = APIRouter(prefix="/coupons")



# Create Coupon (Admin Only)
@router.post("/", dependencies=[Depends(admin_required)])
async def create_new_coupons(coupon: CouponCreate, db: Session = Depends(get_db)):
    new_coupon = await create_new_coupon(coupon, db)
    return {"message": "Coupon created successfully", "data": new_coupon}

# Get Coupons Available for User
@router.get("/", dependencies=[Depends(user_required)])
async def get_user_coupons(db: Session = Depends(get_db), current_user: dict = Depends(user_required)):
    coupons = await get_user_active_coupons(user_id=current_user.id, db=db)
    return {"message": "Coupons retrieved successfully", "data": coupons}


# Get All Coupons (Admin Only)
@router.get("/all", dependencies=[Depends(admin_required)])
async def get_all_coupon_data(db: Session = Depends(get_db)):
    coupons = await get_all_coupons(db)
    return {"message": "All coupons retrieved successfully", "data": coupons}

# Get Coupon by ID
@router.get("/{coupon_id}")
async def get_coupon_details(coupon_id: int, db: Session = Depends(get_db)):
    coupon = await get_coupon_by_id(coupon_id, db)
    return {"message": "Coupon retrieved successfully", "data": coupon}

# Update Coupon (Admin Only)
@router.put("/{coupon_id}", dependencies=[Depends(admin_required)])
async def update_coupon(coupon_id: int, coupon: CouponCreate, db: Session = Depends(get_db)):
    updated_coupon = await update_existing_coupon(coupon_id, coupon, db)
    return {"Message": "Coupon Updated Successfully", "data": updated_coupon}

# Delete Coupon (Admin Only)
@router.delete("/{coupon_id}", response_model=dict, dependencies=[Depends(admin_required)])
async def remove_coupon(coupon_id: int, db: Session = Depends(get_db)):
    deleted_coupon = await delete_coupon(coupon_id, db)
    return {"Message": "Coupon Deleted Successfully", "data": deleted_coupon}
