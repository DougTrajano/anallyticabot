from sqlmodel import Field, SQLModel
from pydantic import validator
from api.database.models.commons import (
    UUIDField,
    CreatedAtField,
    CreatedByField,
    UpdatedAtField,
    UpdatedByField
)

class TaskBase(SQLModel):
    name: str
    version: str
    status: str
    status_desc: str = Field(None, nullable=True)
    progress: int = Field(0)
    
    @validator("progress")
    def progress_must_be_between_0_and_100(cls, v):
        if v < 0 or v > 100:
            raise ValueError("progress must be between 0 and 100")
        return v
    
    @validator("status")
    def status_must_be_valid(cls, v):
        if v.lower() not in ["pending", "running", "completed", "failed"]:
            raise ValueError("status must be one of pending, running, completed, failed")
        return v.lower()
    
class Task(
    TaskBase,
    UUIDField,
    CreatedAtField,
    CreatedByField,
    UpdatedAtField,
    UpdatedByField,
    table=True):
    ...

class TaskRead(
    TaskBase,
    UUIDField,
    CreatedAtField,
    CreatedByField,
    UpdatedAtField,
    UpdatedByField):
    ...

class TaskCreate(
    TaskBase,
    CreatedByField):
    ...

class TaskUpdate(
    TaskBase,
    UUIDField,
    UpdatedByField):
    ...