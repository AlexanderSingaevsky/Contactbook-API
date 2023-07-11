from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

import src.emails.repository as emails_db
from src.database import get_session
from src.emails.schemas import EmailIn, EmailOut


router = APIRouter(prefix='/emails', tags=["emails"])


@router.get("/all/{contact_id}", response_model=list[EmailOut])
async def read_emails(contact_id: int, db: AsyncSession = Depends(get_session)):
    all_emails = await emails_db.get_all_emails(contact_id, db)
    if all_emails:
        return all_emails
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.post("/create/{contact_id}", status_code=status.HTTP_201_CREATED)
async def create_email(contact_id: int, phone: EmailIn, db: AsyncSession = Depends(get_session)):
    await emails_db.add_email(contact_id, phone, db)
    return {"detail": "Email added sucsessfully."}


@router.put("/update/{contact_id}/{email_id}")
async def update_email(new_email: EmailIn, contact_id: int, email_id: int,  db: AsyncSession = Depends(get_session)):
    respond = await emails_db.update_email(contact_id, email_id, new_email, db)
    if respond:
        return {"detail": "Email updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.delete("/delete/{contact_id}/{email_id}")
async def delete_email(contact_id: int, email_id: int,  db: AsyncSession = Depends(get_session)):
    respond = await emails_db.remove_email(contact_id, email_id, db)
    if respond:
        return {"detail": "Email deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
