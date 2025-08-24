from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
from datetime import datetime
from typing import List, Optional
import aiofiles
import uuid

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

@app.post("/events/create")
async def create_event(
    name: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    date: str = Form(...),
    admin_user_id: str = Form(...)
):
    """Creates a new event"""
    event_id = str(uuid.uuid4())
    
    event = {
        "id": event_id,
        "name": name,
        "description": description,
        "location": location,
        "date": date,
        "admin_user_id": admin_user_id,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "participants": [],
        "moments": []
    }
    
    events[event_id] = event
    
    return {"event_id": event_id, "event": event}

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
    user_id: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    timestamp: str = Form(...)
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
        "user_id": user_id,
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
    admin_user_id: str = Form(...),
    max_participants: int = Form(...)
):
    """Creates a new voucher for an event"""
    voucher_id = str(uuid.uuid4())
    
    voucher = {
        "id": voucher_id,
        "event_id": event_id,
        "admin_user_id": admin_user_id,
        "max_participants": max_participants,
        "participants": [],
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    
    vouchers[voucher_id] = voucher
    
    return {"voucher_id": voucher_id, "voucher": voucher}

@app.post("/vouchers/{voucher_id}/join")
async def join_voucher(voucher_id: str, user_id: str = Form(...)):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
