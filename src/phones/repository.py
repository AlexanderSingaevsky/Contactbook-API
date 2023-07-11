from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from src.models import Contact, Phone, Email
from src.phones.schemas import PhoneIn


async def get_all_phones(contact_id: int, session: AsyncSession) -> list[Phone]:
    async with session.begin():
        contact = await session.execute(select(Phone).filter(Phone.contact_id == contact_id))
    return [contact for contact in contact.unique().scalars()]


async def add_phone(contact_id: int,
                    phone: PhoneIn,
                    session: AsyncSession) -> Contact | None:
    async with session.begin():
        contact = await session.get(Contact, contact_id)
        if contact:
            contact.phones.append(Phone(number=phone.number))
            await session.flush()
    return contact


async def update_phone(contact_id: int,
                       phone_id: int,
                       new_phone: PhoneIn,
                       session: AsyncSession) -> Phone | None:
    async with session.begin():
        phone = await session.get(Phone, phone_id)
        if phone and phone.contact_id == contact_id:
            phone.number = new_phone.number
            await session.flush()
    return phone


async def remove_phone(contact_id: int, phone_id: int, session: AsyncSession):
    async with session.begin():
        phone = await session.get(Phone, phone_id)
        if phone and phone.contact_id == contact_id:
            await session.delete(phone)
            return True
