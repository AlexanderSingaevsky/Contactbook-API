from pydantic import BaseModel, Field
from datetime import date

from src.phones.schemas import PhoneOut
from src.emails.schemas import EmailOut


# Input pydantic schemas


class ContactIn(BaseModel):
    first_name: str = Field(min_length=2, max_length=50, default="First name")
    last_name: str | None = Field(min_length=2, max_length=50, default="Last name")
    birthday: date | None = None
    description: str | None = Field(max_length=300, default="Description")


# Output pydantic schemas

class ContactOut(ContactIn):
    id: int
    emails: list[EmailOut] | None = None
    phones: list[PhoneOut] | None = None

    class Config:
        from_attributes = True
