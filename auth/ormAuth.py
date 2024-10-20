from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Response, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import timedelta, datetime
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from config import db, settings
from pymongo import ReturnDocument
from bson import ObjectId
from utils.utils import get_current_user2, send_reset_email, create_reset_token
from uuid import uuid4
import json
from models.authModel import Auth
SECRET_KEY = settings.SECRET_KEY  # Use SECRET_KEY from settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

class User(BaseModel):
    id: Optional[str] = None
    email: str
    password: str
    created_at: Optional[datetime] = None  # Add created_at field
    updated_at: Optional[datetime] = None

class UserInDB(User):
    id: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/signup")
async def signup(user: User):
    try:
        email = user.email
        password = user.password
        if not email or not password:
            raise HTTPException(status_code=400, detail="email and password are required")
        existing_user = Auth.objects.filter(email=email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="email already registered")

        hashed_password = pwd_context.hash(password)
        user = Auth(
            email=email,
            password=hashed_password
        )
        user.save()

        return {"message": "User created successfully"}
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/signin")
async def signin(user: User, response: Response):
    try:
        email = user.email
        password = user.password
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")

        user = Auth.objects.filter(email=email).first()
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        is_valid_password = pwd_context.verify(password, user["password"])
        if not is_valid_password:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        access_token = create_access_token(data={"sub": user["email"], "user_id": str(user["id"])})
        response.set_cookie(key="access_token", value=access_token, httponly=True)

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me", response_model=User)
async def read_me(current_user: UserInDB = Depends(get_current_user2)):
    try:
        current_user['id'] = str(current_user['id'])
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/forget-password")
async def forget_password(request: PasswordResetRequest, background_tasks: BackgroundTasks):
    try:
        user =  Auth.objects.filter(email=request.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User with this email does not exist")
        
        reset_token = create_reset_token({"sub": str(user["id"])})
        background_tasks.add_task(send_reset_email, request.email, reset_token)

        return {"message": "Password reset email sent"}
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

@router.post("/reset-password")
async def reset_password(data: PasswordReset):
    try:
        payload = jwt.decode(data.token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        user = Auth.objects.filter(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        hashed_password = pwd_context.hash(data.new_password)
        result = Auth.objects(id=user_id).update_one(set__password=hashed_password)
        if result == 0:
            raise HTTPException(status_code=404, detail="User not found")
    
        return {"message": "Password reset successful"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Token decoding error") from e


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, current_user: dict = Depends(get_current_user2)):
    try:
        response.delete_cookie(key="access_token")

        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during logout") from e

