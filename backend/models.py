from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "user"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: User

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict

class RegisterResponse(BaseModel):
    message: str
    user: User

class AppleSignInRequest(BaseModel):
    identity_token: str
    authorization_code: str

class GoogleSignInRequest(BaseModel):
    id_token: str
    access_token: str
