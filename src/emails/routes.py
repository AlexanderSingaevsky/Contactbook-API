from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

import src.emails.repository as emails_db
from src.database_postgres import get_session
from src.emails.schemas import EmailIn, EmailOut
from src.auth.service import auth_service
from src.models import User

router = APIRouter(prefix='/emails', tags=["emails"])


@router.get("/read/contact={contact_id}", response_model=list[EmailOut], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_emails(contact_id: int, current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_session)):
    all_emails = await emails_db.get_all_emails(contact_id, current_user, db)
    if all_emails:
        return all_emails
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emails not found.")


@router.post("/create/contact={contact_id}", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_email(contact_id: int, email: EmailIn, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    respond = await emails_db.add_email(contact_id, email, current_user, db)
    if respond:
        return {"detail": "Email added sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.put("/update/contact={contact_id}&email={email_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_email(new_email: EmailIn, contact_id: int, email_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    respond = await emails_db.update_email(contact_id, email_id, new_email, current_user, db)
    if respond:
        return {"detail": "Email updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")


@router.delete("/delete/contact={contact_id}&email={email_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_email(contact_id: int, email_id: int, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    respond = await emails_db.remove_email(contact_id, email_id, current_user, db)
    if respond:
        return {"detail": "Email deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
