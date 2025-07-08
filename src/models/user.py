
from enum import Enum
from pydantic import BaseModel, Field

class UserRole(str, Enum):
    """Enumeration for user roles."""
    FREE = "free"
    VIP = "vip"

class User(BaseModel):
    """
    Represents a user in the system.
    Pydantic model for data validation and serialization.
    """
    id: int
    username: str
    role: UserRole = UserRole.FREE
    points: int = Field(default=0, ge=0)
