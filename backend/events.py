"""
Event Management System
Handles events, vouchers, and participant management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
import random
import string
from fastapi import HTTPException, status
from models import Event, EventCreate, EventUpdate, EventStatus, EventList
from models import Voucher, VoucherCreate, VoucherUpdate, VoucherStatus, VoucherList, VoucherRedeem, VoucherRedeemResponse

# In-memory storage for MVP (will be database later)
events_db: Dict[str, Event] = {}
vouchers_db: Dict[str, Voucher] = {}
event_participants: Dict[str, List[str]] = {}  # event_id -> list of user emails

def generate_voucher_code() -> str:
    """Generate a unique voucher code"""
    while True:
        # Generate 8-character alphanumeric code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # Check if code already exists
        if not any(v.code == code for v in vouchers_db.values()):
            return code

async def create_event(event_data: EventCreate, admin_email: str) -> Event:
    """Create a new event"""
    event_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    event = Event(
        id=event_id,
        admin_email=admin_email,
        created_at=now,
        updated_at=now,
        **event_data.model_dump()
    )
    
    events_db[event_id] = event
    event_participants[event_id] = [admin_email]  # Admin is automatically a participant
    
    return event

async def get_event(event_id: str) -> Optional[Event]:
    """Get event by ID"""
    return events_db.get(event_id)

async def get_events_by_admin(admin_email: str) -> List[Event]:
    """Get all events created by admin"""
    return [event for event in events_db.values() if event.admin_email == admin_email]

async def get_all_events() -> List[Event]:
    """Get all events"""
    return list(events_db.values())

async def update_event(event_id: str, event_data: EventUpdate, admin_email: str) -> Event:
    """Update an event"""
    if event_id not in events_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    event = events_db[event_id]
    
    # Check if user is admin of this event
    if event.admin_email != admin_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only event admin can update this event"
        )
    
    # Update fields
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    event.updated_at = datetime.utcnow()
    events_db[event_id] = event
    
    return event

async def delete_event(event_id: str, admin_email: str) -> bool:
    """Delete an event"""
    if event_id not in events_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    event = events_db[event_id]
    
    # Check if user is admin of this event
    if event.admin_email != admin_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only event admin can delete this event"
        )
    
    # Delete event and related data
    del events_db[event_id]
    if event_id in event_participants:
        del event_participants[event_id]
    
    # Delete related vouchers
    vouchers_to_delete = [v_id for v_id, voucher in vouchers_db.items() if voucher.event_id == event_id]
    for v_id in vouchers_to_delete:
        del vouchers_db[v_id]
    
    return True

async def create_voucher(voucher_data: VoucherCreate, admin_email: str) -> Voucher:
    """Create a new voucher for an event"""
    # Check if event exists
    if voucher_data.event_id not in events_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    event = events_db[voucher_data.event_id]
    
    # Check if user is admin of this event
    if event.admin_email != admin_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only event admin can create vouchers for this event"
        )
    
    voucher_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    voucher = Voucher(
        id=voucher_id,
        code=generate_voucher_code(),
        admin_email=admin_email,
        created_at=now,
        **voucher_data.model_dump()
    )
    
    vouchers_db[voucher_id] = voucher
    return voucher

async def get_voucher_by_code(code: str) -> Optional[Voucher]:
    """Get voucher by code"""
    for voucher in vouchers_db.values():
        if voucher.code == code:
            return voucher
    return None

async def get_vouchers_by_event(event_id: str, admin_email: str) -> List[Voucher]:
    """Get all vouchers for an event"""
    # Check if user is admin of this event
    event = events_db.get(event_id)
    if not event or event.admin_email != admin_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return [v for v in vouchers_db.values() if v.event_id == event_id]

async def redeem_voucher(voucher_code: str, user_email: str) -> VoucherRedeemResponse:
    """Redeem a voucher for event participation"""
    voucher = await get_voucher_by_code(voucher_code)
    
    if not voucher:
        return VoucherRedeemResponse(
            success=False,
            message="Invalid voucher code"
        )
    
    # Check if voucher is active
    if voucher.status != VoucherStatus.ACTIVE:
        return VoucherRedeemResponse(
            success=False,
            message="Voucher is not active"
        )
    
    # Check if voucher has expired
    if voucher.expires_at and voucher.expires_at < datetime.utcnow():
        voucher.status = VoucherStatus.EXPIRED
        return VoucherRedeemResponse(
            success=False,
            message="Voucher has expired"
        )
    
    # Check if voucher usage limit reached
    if voucher.used_count >= voucher.max_uses:
        voucher.status = VoucherStatus.USED
        return VoucherRedeemResponse(
            success=False,
            message="Voucher usage limit reached"
        )
    
    # Get event
    event = events_db.get(voucher.event_id)
    if not event:
        return VoucherRedeemResponse(
            success=False,
            message="Event not found"
        )
    
    # Check if user is already a participant
    participants = event_participants.get(voucher.event_id, [])
    if user_email in participants:
        return VoucherRedeemResponse(
            success=False,
            message="User is already a participant in this event"
        )
    
    # Check event participant limit
    if event.max_participants and len(participants) >= event.max_participants:
        return VoucherRedeemResponse(
            success=False,
            message="Event participant limit reached"
        )
    
    # Add user to participants
    participants.append(user_email)
    event_participants[voucher.event_id] = participants
    
    # Update event participant count
    event.participant_count = len(participants)
    events_db[voucher.event_id] = event
    
    # Update voucher usage
    voucher.used_count += 1
    if voucher.used_count >= voucher.max_uses:
        voucher.status = VoucherStatus.USED
    
    return VoucherRedeemResponse(
        success=True,
        message="Voucher redeemed successfully",
        event=event,
        voucher=voucher
    )

async def get_user_events(user_email: str) -> List[Event]:
    """Get all events where user is a participant"""
    user_events = []
    for event_id, participants in event_participants.items():
        if user_email in participants:
            event = events_db.get(event_id)
            if event:
                user_events.append(event)
    return user_events
