from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

import src.phones.repository as phones_db
from src.database import get_session
from src.phones.schemas import PhoneIn, PhoneOut


router = APIRouter(prefix='/phones', tags=["phones"])


@router.get("/all/{contact_id}", response_model=list[PhoneOut])
async def read_phones(contact_id: int, db: AsyncSession = Depends(get_session)):
    all_phones = await phones_db.get_all_phones(contact_id, db)
    if all_phones:
        return all_phones
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.post("/create/{contact_id}", status_code=status.HTTP_201_CREATED)
async def create_phone(contact_id: int, phone: PhoneIn, db: AsyncSession = Depends(get_session)):
    await phones_db.add_phone(contact_id, phone, db)
    return {"detail": "Phone added sucsessfully."}


@router.put("/update/{contact_id}/{phone_id}")
async def update_phone(new_phone: PhoneIn, contact_id: int, phone_id: int,  db: AsyncSession = Depends(get_session)):
    respond = await phones_db.update_phone(contact_id, phone_id, new_phone, db)
    if respond:
        return {"detail": "Phone updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.delete("/delete/{contact_id}/{phone_id}")
async def delete_phone(contact_id: int, phone_id: int,  db: AsyncSession = Depends(get_session)):
    respond = await phones_db.remove_phone(contact_id, phone_id, db)
    if respond:
        return {"detail": "Phone deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
