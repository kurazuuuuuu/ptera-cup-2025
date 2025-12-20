from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db import get_async_session
from src.models import ScheduleEvent, ScheduleEventCreate, ScheduleEventRead, ScheduleEventUpdate, User
from src.auth import current_active_user

router = APIRouter()

@router.get("/", response_model=List[ScheduleEventRead])
async def get_events(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await db.execute(select(ScheduleEvent).where(ScheduleEvent.user_id == user.id))
    return result.scalars().all()

@router.post("/", response_model=ScheduleEventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: ScheduleEventCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    db_event = ScheduleEvent(**event.model_dump(), user_id=user.id)
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

@router.put("/{event_id}", response_model=ScheduleEventRead)
async def update_event(
    event_id: uuid.UUID,
    event_update: ScheduleEventUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await db.execute(select(ScheduleEvent).where(ScheduleEvent.id == event_id, ScheduleEvent.user_id == user.id))
    db_event = result.scalars().first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event_data = event_update.dict(exclude_unset=True)
    for key, value in event_data.items():
        setattr(db_event, key, value)
        
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await db.execute(select(ScheduleEvent).where(ScheduleEvent.id == event_id, ScheduleEvent.user_id == user.id))
    db_event = result.scalars().first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    await db.delete(db_event)
    await db.commit()
