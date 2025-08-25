from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

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

# Event Management Models
class EventStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    event_date: datetime
    max_participants: Optional[int] = None
    status: EventStatus = EventStatus.DRAFT

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    event_date: Optional[datetime] = None
    max_participants: Optional[int] = None
    status: Optional[EventStatus] = None

class Event(EventBase):
    id: str
    admin_email: str
    created_at: datetime
    updated_at: datetime
    participant_count: int = 0
    
    class Config:
        from_attributes = True

class EventList(BaseModel):
    events: List[Event]
    total: int

# Voucher Management Models
class VoucherStatus(str, Enum):
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class VoucherBase(BaseModel):
    event_id: str
    max_uses: int = 1
    expires_at: Optional[datetime] = None
    description: Optional[str] = None

class VoucherCreate(VoucherBase):
    pass

class VoucherUpdate(BaseModel):
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[VoucherStatus] = None

class Voucher(VoucherBase):
    id: str
    code: str
    admin_email: str
    created_at: datetime
    used_count: int = 0
    status: VoucherStatus = VoucherStatus.ACTIVE
    
    class Config:
        from_attributes = True

class VoucherList(BaseModel):
    vouchers: List[Voucher]
    total: int

class VoucherRedeem(BaseModel):
    voucher_code: str
    user_email: str

class VoucherRedeemResponse(BaseModel):
    success: bool
    message: str
    event: Optional[Event] = None
    voucher: Optional[Voucher] = None
