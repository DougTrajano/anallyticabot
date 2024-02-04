"""SQLAlchemy models for Task."""
import datetime
from typing import Optional
from pydantic import validator
from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from api.database.models.commons import (
    UUIDField,
    CreatedAtField,
    CreatedByField,
    UpdatedAtField,
    UpdatedByField
)

class TaskModel(SQLModel):
    """Base model for Task."""

class TaskInput(TaskModel):
    """TaskInput model."""
    input: Optional[dict] = Field(
        default=None,
        sa_type=JSONB,
        nullable=True
    )

class TaskOutput(TaskModel):
    """TaskOutput model."""
    output: Optional[dict] = Field(
        default=None,
        sa_type=JSONB,
        nullable=True
    )

class TaskBase(TaskModel):
    """Base model for Task."""
    name: str = Field(index=True, nullable=False)
    version: str
    status: str = Field("PENDING", nullable=False)
    status_desc: Optional[str] = Field(None, nullable=True)
    start_time: Optional[datetime.datetime] = Field(None, nullable=True)
    end_time: Optional[datetime.datetime] = Field(None, nullable=True)
    progress: int = Field(0)

class Task(
    TaskBase,
    UUIDField,
    CreatedAtField,
    CreatedByField,
    UpdatedAtField,
    UpdatedByField,
    table=True):
    """Task model."""

    @validator("progress")
    def progress_must_be_between_0_and_100(cls, v: int): # pylint: disable=no-self-argument, no-self-use
        """Validate progress must be between 0 and 100."""
        if v < 0 or v > 100:
            raise ValueError("progress must be between 0 and 100")
        return v

    @validator("status")
    def status_must_be_valid(cls, v: str): # pylint: disable=no-self-argument, no-self-use
        """Validate status must be one of PENDING, RUNNING, COMPLETED, FAILED."""
        if v.upper() not in ["PENDING", "RUNNING", "COMPLETED", "FAILED"]:
            raise ValueError("status must be one of PENDING, RUNNING, COMPLETED, FAILED.")
        return v.upper()

    class Config:
        """Config for Task model."""
        arbitrary_types_allowed = True # Allow JSON type

class TaskRead(
    TaskBase,
    UUIDField,
    CreatedAtField,
    CreatedByField,
    UpdatedAtField,
    UpdatedByField):
    """TaskRead model."""

class TaskCreate(
    TaskInput,
    CreatedByField):
    """TaskCreate model."""
    name: str = Field(index=True, nullable=False)

class TaskUpdate(
    TaskInput,
    UUIDField,
    UpdatedByField):
    """TaskUpdate model."""
