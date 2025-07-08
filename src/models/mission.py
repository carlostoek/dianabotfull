
from pydantic import BaseModel, Field

class Mission(BaseModel):
    """Represents a mission that users can complete."""
    id: int
    name: str
    description: str
    reward_points: int = Field(gt=0)
