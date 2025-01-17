from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from utils.jwt import is_admin,is_user
from core.auth import oauth2_scheme
from os import path
import os
from db.config import get_db
from sqlalchemy.orm import Session
# Admin Check Dependency
def admin_required(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    return is_admin(token,db)


def get_upload_path():
    # Define your image upload path here
    # This can be adjusted based on your project structure
    upload_dir = os.path.join(os.getcwd(), "static", "images")
    return upload_dir


def user_required(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return is_user(token,db)