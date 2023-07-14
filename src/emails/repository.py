from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.models import Contact, Email, User
from src.emails.schemas import EmailIn


async def get_all_emails(contact_id, current_user: User, session: AsyncSession) -> list[Email]:
    async with session.begin():
        stmt = select(Email) \
            .join(Contact) \
            .where(and_(Email.contact_id == contact_id, Contact.owner_id == current_user.id)) \
            .order_by(Email.id)
        emails = await session.execute(stmt)
    return [email for email in emails.scalars()]


async def add_email(contact_id: int,
                    email: EmailIn,
                    current_user: User,
                    session: AsyncSession) -> Contact | None:
    async with session.begin():
        contact = await session.get(Contact, contact_id)
        if contact and contact.owner_id == current_user.id:
            session.add(Email(**email.dict(), contact_id=contact.id))
            return contact


async def update_email(contact_id: int,
                       email_id: int,
                       new_email: EmailIn,
                       current_user: User,
                       session: AsyncSession) -> Email | None:
    async with session.begin():
        stmt = select(Email) \
            .join(Contact) \
            .where(
            and_(Email.contact_id == contact_id, Email.id == email_id, Contact.owner_id == current_user.id)) \
            .limit(1)
        email = await session.execute(stmt)
        email = email.scalars().one_or_none()
        if email:
            email.address = new_email.address
            await session.commit()
    return email


async def remove_email(contact_id: int,
                       email_id: int,
                       current_user: User,
                       session: AsyncSession) -> bool:

    async with session.begin():
        stmt = select(Email) \
            .join(Contact) \
            .where(
            and_(Email.contact_id == contact_id, Email.id == email_id, Contact.owner_id == current_user.id)) \
            .limit(1)
        email = await session.execute(stmt)
        email = email.scalars().one_or_none()
        if email:
            await session.delete(email)
            return True
        else:
            return False
