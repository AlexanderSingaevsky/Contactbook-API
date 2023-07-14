from pydantic import BaseModel, Field
from datetime import date


# Input pydantic schemas
class EmailIn(BaseModel):
    address: str = Field(max_length=50, default="Email address")


# Output pydantic schemas
class EmailOut(EmailIn):
    id: int
    # contact_id: int

    class Config:
        orm_mode = True
