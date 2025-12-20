from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
import uuid

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
# We manually define the fields to avoid Pydantic/SQLModel compatibility issues with SQLAlchemy's Mapped types
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

class ScheduleEvent(ScheduleEventBase, table=True):
    id: str = Field(primary_key=True)
    # user_id needs to match the UUID type of User.id, but SQLModel/SQLAlchemy foreign keys 
    # handle type bridging. However, explicit type is better.
    # stored as string in this example to match existing logic or uuid.
    # Since SQLAlchemyBaseUserTableUUID uses UUID, we should be careful.
    # For simplicity in this refactor, we'll assume foreign keys are handled as strings or UUIDs.
    # But wait, User.id is uuid.UUID.
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfileBase(SQLModel):
    encoded_preferences: str

class UserProfile(UserProfileBase, table=True):
    user_id: uuid.UUID = Field(primary_key=True, foreign_key="user.id")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TimelinePostBase(SQLModel):
    content: str

class TimelinePost(TimelinePostBase, table=True):
    id: str = Field(primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    event_id: str = Field(foreign_key="scheduleevent.id")
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
    id: str
    user_id: uuid.UUID
    created_at: datetime

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
    id: str
    user_id: uuid.UUID
    event_id: str
    created_at: datetime

class TimelinePostCreate(TimelinePostBase):
    event_id: str

# Re-update forward refs for nested models
AuthResponse.model_rebuild()
