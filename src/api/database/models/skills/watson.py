from sqlmodel import Field, SQLModel
from typing import Optional
from api.database.models.commons import (
    UUIDField,
    CreatedAtField,
    CreatedByField,
    UpdatedAtField,
    UpdatedByField
)


class WatsonAssistantBase(SQLModel):
    name: str = Field(..., description="Watson Assistant name.")
    url: str = Field(..., description="Watson Assistant url.")
    assistant_id: str = Field(..., description="Watson Assistant id.")
    auth_type: Optional[str] = Field("iam", description="Watson Assistant auth type.")


class WatsonAssistant(
    WatsonAssistantBase,
    UUIDField,
    CreatedAtField,
    CreatedByField,
    UpdatedAtField,
    UpdatedByField,
    table=True):
    apikey: str = Field(..., description="Watson Assistant apikey.")

    
class WatsonAssistantRead(
    WatsonAssistantBase,
    UUIDField,
    CreatedAtField,
    CreatedByField,
    UpdatedAtField,
    UpdatedByField):
    ...


class WatsonAssistantCreate(
    WatsonAssistantBase,
    CreatedByField):
    apikey: str = Field(..., description="Watson Assistant apikey.")
    

class WatsonAssistantUpdate(
    WatsonAssistantBase,
    UUIDField,
    UpdatedByField):
    apikey: str = Field(None, description="Watson Assistant apikey.")
