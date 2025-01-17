from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.models import Coupon,CouponUsage,User
from schemas.coupons import CouponCreate
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import and_

async def create_new_coupon(coupon_data: CouponCreate, db: Session):
    try:
        # Create the coupon
        coupon = Coupon(
            code=coupon_data.code,
            discount=coupon_data.discount,
            expiration_date=coupon_data.expiration_date,
        )
        db.add(coupon)
        db.commit()
        db.refresh(coupon)

        # Fetch all users from the database
        users = db.query(User).all()

        # Create coupon usage for all users
        for user in users:
            coupon_usage = CouponUsage(user_id=user.id, coupon_id=coupon.id)
            db.add(coupon_usage)

        db.commit()
        return coupon

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error creating coupon for all users: {str(e)}")

async def get_all_coupons(db: Session):
    coupons = db.query(Coupon).all()
    return coupons

async def get_coupon_by_id(coupon_id: int, db: Session):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon

async def update_existing_coupon(coupon_id: int, coupon_data: CouponCreate, db: Session):
    coupon = await get_coupon_by_id(coupon_id, db)
    coupon.code = coupon_data.code
    coupon.discount = coupon_data.discount
    coupon.expiration_date = coupon_data.expiration_date
    coupon.usage_limit = coupon_data.usage_limit
    db.commit()
    db.refresh(coupon)
    return coupon

async def delete_coupon(coupon_id: int, db: Session):
    coupon = await get_coupon_by_id(coupon_id, db)
    coupon_usage = coupon.coupon_usages
    print(coupon_usage)
    for usage in coupon_usage:
        db.delete(usage)
        db.commit()

    db.delete(coupon)
    db.commit()
    return {"id": coupon_id, "deleted": True}


async def get_user_active_coupons(user_id: int, db: Session):
    # Get current date to check coupon validity
    current_date = datetime.now().date()

    # Query to get active and unused coupons for the user
    active_coupons = db.query(Coupon).join(CouponUsage).filter(
        and_(
            CouponUsage.user_id == user_id,  # Ensure the user has not used this coupon
            Coupon.expiration_date >= current_date,  # Ensure the coupon is still valid
            CouponUsage.usage_limit == 1      # Ensure the coupon hasn't been used
        )
    ).all()
    # If no active coupons, return an empty list
    if not active_coupons:
        return []

    # Return the list of active coupons for the user
    return [{"coupon_id": coupon.id, "code": coupon.code, "discount": coupon.discount, "expiration_date": coupon.expiration_date} for coupon in active_coupons]