from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime

class Task(BaseModel):
    id: int
    description: str
    completed: bool
    completed_at: Optional[datetime] = None
    
    @field_serializer("completed_at")
    def serialise_completed_at(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%d %b %Y, %H:%M")