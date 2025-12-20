from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

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

class UserBase(SQLModel):
    username: str
    email: str

class User(UserBase, table=True):
    id: str = Field(primary_key=True)
    password_hash: str
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
    user_id: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfileBase(SQLModel):
    encoded_preferences: str

class UserProfile(UserProfileBase, table=True):
    user_id: str = Field(primary_key=True, foreign_key="user.id")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TimelinePostBase(SQLModel):
    content: str

class TimelinePost(TimelinePostBase, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    event_id: str = Field(foreign_key="scheduleevent.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ==========================================
# Pydantic / Response Models (DTOs)
# Matching Swift structs
# ==========================================

# Matching Swift: User
class UserRead(UserBase):
    id: str
    created_at: datetime

# Matching Swift: ScheduleEvent
class ScheduleEventRead(ScheduleEventBase):
    id: str
    user_id: str
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
    user_id: str
    last_updated: datetime

# Matching Swift: TimelinePost
class TimelinePostRead(TimelinePostBase):
    id: str
    user_id: str
    event_id: str
    created_at: datetime

class TimelinePostCreate(TimelinePostBase):
    event_id: str

# Re-update forward refs for nested models
AuthResponse.update_forward_refs()
