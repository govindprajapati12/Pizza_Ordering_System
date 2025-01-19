from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from utils.jwt import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, create_access_token, create_refresh_token, verify_token
from models.models import Coupon, CouponUsage, User
from schemas.auth import LoginRequest, LoginResponse, RegistrationRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def register_user(user_data: RegistrationRequest, db: Session):
    try:
        # Check if the email is already registered
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    except Exception as e:
        print(str(e))
        raise e
    
    # Hash the password
    hashed_password = await hash_password(user_data.password)
    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        role="user",
    )
    
    # Add the new user to the database
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Fetch all existing coupons
    existing_coupons = db.query(Coupon).all()

    # Assign each coupon to the new user
    for coupon in existing_coupons:
        coupon_usage = CouponUsage(user_id=user.id, coupon_id=coupon.id)
        db.add(coupon_usage)
    
    db.commit()
    return user

async def authenticate_user(login_data, db: Session):
    # Find user by email
    user = db.query(User).filter(User.email == login_data.username).first()

    # If user not found or password is incorrect, raise error
    if not user or not await verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT tokens
    access_token = create_access_token({"sub": user.email, "role": user.role, "username": user.name})
    refresh_token = create_refresh_token({"sub": user.email})

    # Return login response with user details
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        username=user.name,  # Include the username
        role=user.role,  # Include the role
    )

def generate_new_access_token(refresh_token: str, db: Session) -> str:
    """
    Validate the refresh token and generate a new access token.
    """
    try:
        # Decode the refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")  # Extract the 'sub' (email) from the token payload

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Query the user from the database using the email
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Generate a new access token
        access_token_expiry = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = jwt.encode(
            {"sub": user.email, "role": user.role, "exp": datetime.utcnow() + access_token_expiry},
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        return new_access_token

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )