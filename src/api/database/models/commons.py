import datetime
import uuid as uuid_pkg
from sqlalchemy import text
from sqlmodel import Field, SQLModel
from typing import Optional


class UUIDField(SQLModel):
   id: uuid_pkg.UUID = Field(
       default_factory=uuid_pkg.uuid4,
       primary_key=True,
       index=True,
       nullable=False,
       sa_column_kwargs={
           "server_default": text("gen_random_uuid()"),
           "unique": True
       }
   )

class CreatedByField(SQLModel):
    created_by: Optional[str] = Field(None, description="User who created the record.")

class CreatedAtField(SQLModel):
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)")
        }
    )

class UpdatedByField(SQLModel):
    updated_by: Optional[str] = Field(None, description="User who updated the record.")

class UpdatedAtField(SQLModel):
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp(0)"),
            "onupdate": text("current_timestamp(0)")
        }
    )
    