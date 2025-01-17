from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
from typing import Optional
from models.models import User
from sqlalchemy.orm import Session

SECRET_KEY = "our_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # Assuming you're using JWT
        email = payload.get("sub")  # 'sub' field in JWT is usually the email

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Query the user by email to get the user details including 'id'
        user = db.query(User).filter(User.email == email).first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Return the user object with 'id' field included
        return user
    # {"id": user.id, "sub": user.email, "role": user.role}

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
# Check if User is Admin
def is_admin(token: str,db:Session):
    user = get_current_user(token,db)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as admin")
    return user

def is_user(token: str,db: Session):
    user = get_current_user(token,db)
    if user.role == "admin" or user.role == "user":
        return user
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as user")


