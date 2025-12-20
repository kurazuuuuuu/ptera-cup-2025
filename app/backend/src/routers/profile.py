from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db import get_async_session
from src.models import UserProfile, UserProfileRead, UserProfileBase, User
from src.auth import current_active_user
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=UserProfileRead)
async def get_profile(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalars().first()
    
    if not profile:
        # Return empty/default profile if not found, or create one if preferred
        # For now, let's Raise 404 or return a default? 
        # API Schema says GET /profile, typically expects one.
        # Let's return 404 so client knows to create/PUT one, or just return an empty struct if needed.
        # Given "UserPreferenceEncoder" logic in Swift, might be better to return 404.
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile

@router.put("/", response_model=UserProfileRead)
async def update_profile(
    profile_data: UserProfileBase,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    db_profile = result.scalars().first()
    
    if db_profile:
        db_profile.encoded_preferences = profile_data.encoded_preferences
        db_profile.last_updated = datetime.utcnow()
    else:
        db_profile = UserProfile(
            user_id=user.id,
            encoded_preferences=profile_data.encoded_preferences
        )
        db.add(db_profile)
    
    await db.commit()
    await db.refresh(db_profile)
    return db_profile
