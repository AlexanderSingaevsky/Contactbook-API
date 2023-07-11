from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

import src.contacts.repository as contacts_db
from src.database import get_session
from src.contacts.schemas import ContactOut, ContactIn


router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/all", response_model=list[ContactOut])
async def read_contacts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    all_contacts = await contacts_db.get_contacts(skip, limit, db)
    if all_contacts:
        return all_contacts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.get("/{contact_id}", response_model=list[ContactOut])
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_session)):
    all_contacts = await contacts_db.get_contact(contact_id, db)
    if all_contacts:
        return all_contacts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.get("/search/{prompt}", response_model=list[ContactOut])
async def search_contact(prompt: str, db: AsyncSession = Depends(get_session)):
    all_contacts = await contacts_db.search_in_contacts(prompt, db)
    if all_contacts:
        return all_contacts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactIn, db: AsyncSession = Depends(get_session)):
    await contacts_db.add_contact(contact, db)
    return {"detail": "Contact created sucsessfully."}


@router.put("/update/{contact_id}")
async def update_contact(contact: ContactIn, contact_id: int, db: AsyncSession = Depends(get_session)):
    respond = await contacts_db.update_contact(contact, contact_id, db)
    if respond:
        return {"detail": "Contact updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.delete("/delete/{contact_id}")
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_session)):
    respond = await contacts_db.remove_contact(contact_id, db)
    if respond:
        return {"detail": "Contact deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
