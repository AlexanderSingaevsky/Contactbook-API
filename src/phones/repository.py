from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.models import Contact, Phone, User
from src.phones.schemas import PhoneIn


async def get_all_phones(contact_id, current_user: User, session: AsyncSession) -> list[Phone]:
    async with session.begin():
        stmt = select(Phone) \
            .join(Contact) \
            .where(and_(Phone.contact_id == contact_id, Contact.owner_id == current_user.id)) \
            .order_by(Phone.id)
        phones = await session.execute(stmt)
    return [phone for phone in phones.scalars()]


async def add_phone(contact_id: int,
                    phone: PhoneIn,
                    current_user: User,
                    session: AsyncSession) -> Contact | None:
    async with session.begin():
        contact = await session.get(Contact, contact_id)
        if contact and contact.owner_id == current_user.id:
            session.add(Phone(**phone.dict(), contact_id=contact.id))
            return contact


async def update_phone(contact_id: int,
                       phone_id: int,
                       new_phone: PhoneIn,
                       current_user: User,
                       session: AsyncSession) -> Phone | None:
    async with session.begin():
        stmt = select(Phone) \
            .join(Contact) \
            .where(
            and_(Phone.contact_id == contact_id, Phone.id == phone_id, Contact.owner_id == current_user.id)) \
            .limit(1)
        phone = await session.execute(stmt)
        phone = phone.scalars().one_or_none()
        if phone:
            phone.number = new_phone.number
            await session.commit()
    return phone


async def remove_phone(contact_id: int,
                       phone_id: int,
                       current_user: User,
                       session: AsyncSession) -> bool:
    async with session.begin():
        stmt = select(Phone) \
            .join(Contact) \
            .where(
            and_(Phone.contact_id == contact_id, Phone.id == phone_id, Contact.owner_id == current_user.id)) \
            .limit(1)
        phone = await session.execute(stmt)
        phone = phone.scalars().one_or_none()
        if phone:
            await session.delete(phone)
            return True
        else:
            return False
