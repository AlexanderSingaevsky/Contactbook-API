from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

import src.phones.repository as phones_db
from src.database_postgres import get_session
from src.phones.schemas import PhoneIn, PhoneOut
from src.auth.service import auth_service
from src.models import User

router = APIRouter(prefix='/phones', tags=["phones"])


@router.get("/read/contact={contact_id}", response_model=list[PhoneOut],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_phones(contact_id: int, current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_session)):
    all_phones = await phones_db.get_all_phones(contact_id, current_user, db)
    if all_phones:
        return all_phones
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phones not found.")


@router.post("/create/contact={contact_id}", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_phone(contact_id: int, phone: PhoneIn, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    respond = await phones_db.add_phone(contact_id, phone, current_user, db)
    if respond:
        return {"detail": "Phone added sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.put("/update/contact={contact_id}&phone={phone_id}",
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_phone(new_phone: PhoneIn, contact_id: int, phone_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    respond = await phones_db.update_phone(contact_id, phone_id, new_phone, current_user, db)
    if respond:
        return {"detail": "Phone updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found.")


@router.delete("/delete/contact={contact_id}&phone={phone_id}",
               dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_phone(contact_id: int, phone_id: int, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    respond = await phones_db.remove_phone(contact_id, phone_id, current_user, db)
    if respond:
        return {"detail": "Phone deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found.")
