from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
import uuid

# ==========================================
# Auth Models
# Matching Swift: LoginRequest
# ==========================================
# ==========================================
# Auth Models
# Matching Swift: LoginRequest
# ==========================================
class LoginRequest(SQLModel):
    email: str
    password: str

# Matching Swift: RegisterRequest
class RegisterRequest(SQLModel):
    username: str
    email: str
    password: str

# Matching Swift: AuthResponse
class AuthResponse(SQLModel):
    token: str
    user: "UserRead"

# ==========================================
# Database Models (SQLModel tables)
# ==========================================

# SQLAlchemyBaseUserTableUUID replacement
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=320)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScheduleEventBase(SQLModel):
    title: str
    category: str
    start_date: datetime
    end_date: datetime
    is_ai_generated: bool = False
    ek_event_id: Optional[str] = None
    color_hex: Optional[str] = None

class ScheduleEvent(ScheduleEventBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfileBase(SQLModel):
    encoded_preferences: str

class UserProfile(UserProfileBase, table=True):
    user_id: uuid.UUID = Field(primary_key=True, foreign_key="user.id")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TimelinePostBase(SQLModel):
    content: str
    category: Optional[str] = None
    icon_url: Optional[str] = None
    event_date: Optional[str] = None
    color_hex: Optional[str] = None

class TimelinePost(TimelinePostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    event_id: uuid.UUID = Field(foreign_key="scheduleevent.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ==========================================
# Pydantic / Response Models (DTOs)
# Matching Swift structs
# ==========================================

# Matching Swift: User
class UserRead(SQLModel):
    id: uuid.UUID
    username: str
    email: str
    created_at: datetime

# Matching Swift: ScheduleEvent
class ScheduleEventRead(ScheduleEventBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ScheduleEventCreate(ScheduleEventBase):
    pass

class ScheduleEventUpdate(SQLModel):
    title: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_ai_generated: Optional[bool] = None
    ek_event_id: Optional[str] = None

# Matching Swift: UserProfile
class UserProfileRead(UserProfileBase):
    user_id: uuid.UUID
    last_updated: datetime

# Matching Swift: TimelinePost
class TimelinePostRead(TimelinePostBase):
    id: uuid.UUID
    user_id: uuid.UUID
    event_id: uuid.UUID
    created_at: datetime

class TimelinePostCreate(TimelinePostBase):
    event_id: uuid.UUID

class TimelineReaction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    post_id: uuid.UUID = Field(foreign_key="timelinepost.id")
    reaction_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TimelineFeedResponse(SQLModel):
    post: TimelinePostRead
    user: UserRead
    likes: int
    my_reaction: Optional[str] = None

# Re-update forward refs for nested models
AuthResponse.model_rebuild()
