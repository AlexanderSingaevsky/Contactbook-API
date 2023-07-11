from pydantic import BaseModel, Field
from datetime import date


class PhoneIn(BaseModel):
    number: str = Field(max_length=50, default="Phone number")


class PhoneOut(PhoneIn):
    id: int = Field()
    # contact_id: int = Field()

    class Config:
        orm_mode = True
