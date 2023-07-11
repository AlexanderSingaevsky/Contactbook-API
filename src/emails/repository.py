from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from src.models import Contact, Phone, Email
from src.emails.schemas import EmailIn


async def get_all_emails(contact_id: int, session: AsyncSession) -> list[Email]:
    async with session.begin():
        contact = await session.execute(select(Email).filter(Email.contact_id == contact_id))
    return [contact for contact in contact.unique().scalars()]


async def add_email(contact_id: int,
                    email: EmailIn,
                    session: AsyncSession) -> Contact | None:
    async with session.begin():
        contact = await session.get(Contact, contact_id)
        if contact:
            contact.emails.append(Email(address=email.address))
            await session.flush()
    return contact


async def update_email(contact_id: int,
                       email_id: int,
                       new_email: EmailIn,
                       session: AsyncSession) -> Email | None:
    async with session.begin():
        email = await session.get(Email, email_id)
        if email and email.contact_id == contact_id:
            email.address = new_email.address
            await session.flush()
    return email


async def remove_email(contact_id: int, email_id: int, session: AsyncSession):
    async with session.begin():
        email = await session.get(Email, email_id)
        if email and email.contact_id == contact_id:
            await session.delete(email)
            return True
