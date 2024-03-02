"""SQLAlchemy models for Task."""
import datetime
from typing import Optional
from pydantic import validator
from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from api.database.models.commons import (
    UUIDField,
    CreatedAtField,
    CreatedByField
)

class TaskModel(SQLModel):
    """Base model for Task."""

class TaskInputs(TaskModel):
    """TaskInputs model."""
    inputs: Optional[dict] = Field(
        default=None,
        sa_type=JSONB,
        nullable=True
    )

    params: Optional[dict] = Field(
        default=None,
        sa_type=JSONB,
        nullable=True
    )

class TaskOutputs(TaskModel):
    """TaskOutputs model."""
    outputs: Optional[dict] = Field(
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
    progress: Optional[float] = Field(None, nullable=True)

class TaskRead(
    TaskBase,
    UUIDField,
    CreatedAtField,
    CreatedByField):
    """TaskRead model."""

class TaskCreate(
    TaskInputs,
    CreatedByField):
    """TaskCreate model."""
    name: str = Field(index=True, nullable=False)

class TaskUpdate(TaskModel):
    """TaskUpdate model."""
    status: Optional[str] = Field(None, nullable=True)
    status_desc: Optional[str] = Field(None, nullable=True)
    progress: Optional[float] = Field(None, nullable=True)
    start_time: Optional[datetime.datetime] = Field(None, nullable=True)
    end_time: Optional[datetime.datetime] = Field(None, nullable=True)

class Task(
    TaskBase,
    TaskInputs,
    TaskOutputs,
    UUIDField,
    CreatedAtField,
    CreatedByField,
    table=True):
    """Task model."""

    @validator("progress")
    def progress_must_be_between_0_and_1(cls, v: int): # pylint: disable=no-self-argument, no-self-use
        """Validate progress must be between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("progress must be between 0 and 1.")
        return v

    @validator("status")
    def status_must_be_valid(cls, v: str): # pylint: disable=no-self-argument, no-self-use
        """Validate status must be one of PENDING, RUNNING, COMPLETED, FAILED."""
        if v.upper() not in ["PENDING", "RUNNING", "COMPLETED", "FAILED"]:
            raise ValueError("status must be one of PENDING, RUNNING, COMPLETED, FAILED.")
        return v.upper()

    class Config:
        """Config for Task model."""
        arbitrary_types_allowed = True # Allow JSON types
