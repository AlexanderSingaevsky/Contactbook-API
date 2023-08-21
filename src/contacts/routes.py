from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

import src.contacts.repository as contacts_db
from src.database_postgres import get_session
from src.contacts.schemas import ContactOut, ContactIn
from src.models import User
from src.auth.service import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/read", response_model=list[ContactOut], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contacts(current_user: User = Depends(auth_service.get_current_user),
                        db: AsyncSession = Depends(get_session)):
    all_contacts = await contacts_db.get_contacts(current_user, db)
    if all_contacts:
        return all_contacts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.get("/contact={contact_id}", response_model=ContactOut, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contact(contact_id: int, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    contact = await contacts_db.get_contact(contact_id, current_user, db)
    if contact:
        return contact
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.get("/search/string={search_string}", response_model=list[ContactOut],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_contact(search_string: str, current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    all_contacts = await contacts_db.search_in_contacts(search_string, current_user, db)
    if all_contacts:
        return all_contacts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.post("/create", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(contact: ContactIn, current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    await contacts_db.add_contact(contact, current_user, db)
    return {"detail": "Contact created sucsessfully."}


@router.put("/update/contact={contact_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_contact(contact: ContactIn, contact_id: int,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    respond = await contacts_db.update_contact(contact, contact_id, current_user, db)
    if respond:
        return {"detail": "Contact updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.delete("/delete/contact={contact_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_contact(contact_id: int, current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    respond = await contacts_db.remove_contact(contact_id, current_user, db)
    if respond:
        return {"detail": "Contact deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
