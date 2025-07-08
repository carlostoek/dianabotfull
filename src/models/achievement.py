
from pydantic import BaseModel

class Achievement(BaseModel):
    """Represents an achievement or badge that users can unlock."""
    id: int
    name: str
    description: str
    icon: str  # e.g., an emoji or a URL to an image
