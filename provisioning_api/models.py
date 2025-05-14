from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class TaskStatus(str):
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    equipment_id: str
    status: str = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    details: dict | None = None
