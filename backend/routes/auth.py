from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.auth import RegistrationRequest, LoginRequest, LoginResponse
from services.auth import register_user, authenticate_user,generate_new_access_token
from db.config import get_db
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user_data: RegistrationRequest, db: Session = Depends(get_db)):
    new_user =  await register_user(user_data, db)  
    return {"message": "User registered successfully","data":new_user}

@router.post("/login", response_model=LoginResponse)
async def login(login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    loged_user = await authenticate_user(login_data, db)
    return loged_user  

@router.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh the access token using a valid refresh token.
    """
    try:
        # Call service function to process the refresh token
        new_access_token = generate_new_access_token(refresh_token, db)
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        raise e