from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import json
from datetime import datetime, timedelta
from typing import List, Optional
import aiofiles
import uuid

from auth import authenticate_user, create_access_token, verify_token, create_user, authenticate_apple_user, authenticate_google_user, ACCESS_TOKEN_EXPIRE_MINUTES
from models import UserLogin, UserCreate, LoginResponse, RegisterResponse, User, AppleSignInRequest, GoogleSignInRequest, EventCreate, EventUpdate, EventList, Event, VoucherCreate, VoucherUpdate, VoucherList, VoucherRedeem, VoucherRedeemResponse, Voucher
from events import create_event, get_event, get_events_by_admin, get_all_events, update_event, delete_event, create_voucher, get_vouchers_by_event, redeem_voucher, get_user_events

app = FastAPI(
    title="SuperMoment API",
    description="API for collecting and sharing photos and videos from different angles",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # U produkciji će biti ograničeno
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# In-memory storage for MVP (will be database later)
events = {}
vouchers = {}
users = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SuperMoment API is active!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/auth/login", response_model=LoginResponse)
async def login(user_credentials: UserLogin):
    """Login endpoint"""
    user = authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "is_active": user["is_active"]
        }
    }

@app.post("/auth/register", response_model=RegisterResponse)
async def register(user_data: UserCreate):
    """Register new user endpoint"""
    try:
        user = create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role
        )
        
        return {
            "message": "User created successfully",
            "user": User(
                email=user["email"],
                full_name=user["full_name"],
                role=user["role"],
                is_active=user["is_active"]
            )
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.get("/auth/me")
async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information"""
    user = verify_token(credentials.credentials)
    return {
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "is_active": user["is_active"]
    }

@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout endpoint (client should discard token)"""
    return {"message": "Successfully logged out"}

@app.post("/auth/apple", response_model=LoginResponse)
async def apple_sign_in(apple_data: AppleSignInRequest):
    """Apple Sign In endpoint"""
    try:
        user = authenticate_apple_user(apple_data.identity_token, apple_data.authorization_code)
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "is_active": user["is_active"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Apple Sign In failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/auth/google", response_model=LoginResponse)
async def google_sign_in(google_data: GoogleSignInRequest):
    """Google Sign In endpoint"""
    try:
        user = authenticate_google_user(google_data.id_token, google_data.access_token)
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "is_active": user["is_active"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google Sign In failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user"""
    return verify_token(credentials.credentials)



@app.get("/events/{event_id}")
async def get_event(event_id: str):
    """Gets event information"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return events[event_id]

@app.post("/events/{event_id}/upload")
async def upload_media(
    event_id: str,
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    timestamp: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Uploads media file for an event"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Create upload directory if it doesn't exist
    upload_dir = f"uploads/{event_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Create moment entry
    moment = {
        "id": str(uuid.uuid4()),
        "file_id": file_id,
        "filename": filename,
        "user_id": current_user["email"],
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp,
        "uploaded_at": datetime.now().isoformat(),
        "file_size": len(content),
        "file_type": file.content_type
    }
    
    events[event_id]["moments"].append(moment)
    
    return {
        "message": "File successfully uploaded",
        "moment_id": moment["id"],
        "file_id": file_id
    }

@app.get("/events/{event_id}/moments")
async def get_moments(event_id: str, user_id: Optional[str] = None):
    """Gets all moments for an event"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    moments = events[event_id]["moments"]
    
    # If user_id is specified, filter only their moments
    if user_id:
        moments = [m for m in moments if m["user_id"] == user_id]
    
    return {"moments": moments, "count": len(moments)}

@app.post("/vouchers/create")
async def create_voucher(
    event_id: str = Form(...),
    max_participants: int = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Creates a new voucher for an event"""
    voucher_id = str(uuid.uuid4())
    
    voucher = {
        "id": voucher_id,
        "event_id": event_id,
        "admin_user_id": current_user["email"],
        "max_participants": max_participants,
        "participants": [],
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    
    vouchers[voucher_id] = voucher
    
    return {"voucher_id": voucher_id, "voucher": voucher}

@app.post("/vouchers/{voucher_id}/join")
async def join_voucher_endpoint(voucher_id: str, user_id: str = Form(...)):
    """Joins a user to a voucher"""
    if voucher_id not in vouchers:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    voucher = vouchers[voucher_id]
    
    if len(voucher["participants"]) >= voucher["max_participants"]:
        raise HTTPException(status_code=400, detail="Voucher is full")
    
    if user_id in voucher["participants"]:
        raise HTTPException(status_code=400, detail="User is already joined to this voucher")
    
    voucher["participants"].append(user_id)
    
    return {"message": "Successfully joined voucher"}

# Event Management Endpoints
@app.post("/events", response_model=Event)
async def create_new_event(
    event_data: EventCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new event"""
    event = await create_event(event_data, current_user["email"])
    return event.model_dump()

@app.get("/events", response_model=EventList)
async def list_events(
    current_user: dict = Depends(get_current_user),
    admin_only: bool = False
):
    """List events - admin's events or all events user participates in"""
    if admin_only:
        events = await get_events_by_admin(current_user["email"])
    else:
        events = await get_user_events(current_user["email"])
    
    return EventList(events=events, total=len(events))

@app.get("/events/all", response_model=EventList)
async def list_all_events(
    current_user: dict = Depends(get_current_user)
):
    """List all events (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all events"
        )
    
    events = await get_all_events()
    return EventList(events=events, total=len(events))

@app.get("/events/{event_id}", response_model=Event)
async def get_event_by_id(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get event by ID"""
    event = await get_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user is participant or admin
    participants = await get_user_events(current_user["email"])
    if event not in participants and event.admin_email != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return event

@app.put("/events/{event_id}", response_model=Event)
async def update_event_by_id(
    event_id: str,
    event_data: EventUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an event"""
    return await update_event(event_id, event_data, current_user["email"])

@app.delete("/events/{event_id}")
async def delete_event_by_id(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an event"""
    success = await delete_event(event_id, current_user["email"])
    return {"message": "Event deleted successfully"}

# Voucher Management Endpoints
@app.post("/vouchers", response_model=Voucher)
async def create_new_voucher(
    voucher_data: VoucherCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new voucher for an event"""
    return await create_voucher(voucher_data, current_user["email"])

@app.get("/vouchers/event/{event_id}", response_model=VoucherList)
async def list_vouchers_for_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """List all vouchers for an event"""
    vouchers = await get_vouchers_by_event(event_id, current_user["email"])
    return VoucherList(vouchers=vouchers, total=len(vouchers))

@app.post("/vouchers/redeem", response_model=VoucherRedeemResponse)
async def redeem_voucher_code(
    voucher_data: VoucherRedeem,
    current_user: dict = Depends(get_current_user)
):
    """Redeem a voucher code"""
    return await redeem_voucher(voucher_data.voucher_code, current_user["email"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
