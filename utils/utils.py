from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import db, settings
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
import smtplib
from email.mime.text import MIMEText
from typing import Optional
from models.authModel import Auth

RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = 15
SECRET_KEY = settings.SECRET_KEY  # Use SECRET_KEY from settings
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper function to verify the token and get the user data using authorization header
def get_current_user1(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        user = db.users.find_one({"_id": user_id})
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return user

# Modify the get_current_user function to extract the token from cookies
async def get_current_user2(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        # odm
        # user = await db.users.find_one({"_id": ObjectId(user_id)})
        # orm
        user = Auth.objects.filter(id=user_id).first()
        if user is None:
            raise credentials_exception
        # user['_id'] = str(user['_id']) #odm
        user['id'] = str(user['id'])     #orm
        return user
    except JWTError:
        raise credentials_exception

def send_reset_email(email: str, token: str):
    try:
        reset_link = f"http://yourdomain.com/reset-password?token={token}"
        message = MIMEText(f"Click the link to reset your password: {reset_link}")
        message["Subject"] = "Password Reset"
        message["From"] = "no-reply@yourdomain.com"
        message["To"] = email

        # Send email (ensure you configure your SMTP server details)
        with smtplib.SMTP("smtp.yourdomain.com", 587) as server:
            server.starttls()
            server.login("your-email@yourdomain.com", "your-email-password")
            server.sendmail("no-reply@yourdomain.com", email, message.as_string())
    
    except smtplib.SMTPException as smtp_exc:
        raise HTTPException(status_code=500, detail="Failed to send reset email") from smtp_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while sending the email") from e

def create_reset_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=RESET_PASSWORD_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as jwt_exc:
        raise HTTPException(status_code=500, detail="Token creation error") from jwt_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the token") from e
