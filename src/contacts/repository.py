from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from src.models import Contact, Phone, Email
from src.contacts.schemas import ContactIn


async def get_contacts(skip, limit, session: AsyncSession) -> list[Contact]:
    async with session.begin():
        contacts = await session.execute(select(Contact).limit(limit).offset(skip))
    return [contact for contact in contacts.unique().scalars()]


async def get_contact(contact_id: int, session: AsyncSession) -> list[Contact]:
    async with session.begin():
        contact = await session.execute(select(Contact).filter(Contact.id == contact_id))
        return [contact for contact in contact.unique().scalars()]


async def search_in_contacts(prompt: str, session: AsyncSession) -> list[Contact]:
    async with session.begin():
        prompt_lower = prompt.lower()
        results = await session.execute(
            select(Contact).where(
                or_(
                    func.lower(Contact.first_name).contains(prompt_lower),
                    func.lower(Contact.last_name).contains(prompt_lower),
                    Contact.emails.any(func.lower(Email.address).contains(prompt_lower)),
                    Contact.phones.any(func.lower(Phone.number).contains(prompt_lower))
                )
            )
        )
    return [result for result in results.unique().scalars()]


async def add_contact(contact: ContactIn, session: AsyncSession):
    async with session.begin():
        contact_to_add = Contact(**contact.dict())
        session.add(contact_to_add)


async def update_contact(contact_update: ContactIn, contact_id: int, session: AsyncSession):
    async with session.begin():
        contact = await session.get(Contact, contact_id)
        if contact:
            contact_data = contact_update.dict(exclude_unset=True)
            for key, value in contact_data.items():
                setattr(contact, key, value)
            await session.flush()
    return contact


async def remove_contact(contact_id: int, session: AsyncSession):
    async with session.begin():
        contact = await session.get(Contact, contact_id)
        if contact:
            await session.delete(contact)
            return True
