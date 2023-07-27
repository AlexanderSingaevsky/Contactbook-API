from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

import src.phones.repository as phones_db
from src.database_postgres import get_session
from src.phones.schemas import PhoneIn, PhoneOut
from src.auth.service import auth_service
from src.models import User

router = APIRouter(prefix='/phones', tags=["phones"])


@router.get("/all/{contact_id}", response_model=list[PhoneOut], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_phones(contact_id: int,
                      current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_session)):
    """
       ## Retrieve all phones for a specific contact belonging to the current user.

       ### Args:
           contact_id (int): The ID of the contact whose phones to retrieve.
           current_user (User): The authenticated user accessing the phones.
           db (AsyncSession): The database session.

       ### Returns:
           List[PhoneOut]: A list of phones belonging to the specified contact.

       ### Raises:
           HTTPException: If no phones are found for the specified contact or
               if the contact does not belong to the current user.
               Returns HTTP status code 404 (Not Found).
       """
    all_phones = await phones_db.get_all_phones(contact_id, current_user, db)
    if all_phones:
        return all_phones
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phones not found.")


@router.post("/create/{contact_id}", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_phone(contact_id: int,
                       phone: PhoneIn,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
        ## Create a new phone for a specific contact belonging to the current user.

        ### Args:
            contact_id (int): The ID of the contact to add the phone to.
            phone (PhoneIn): The phone information to create.
            current_user (User): The authenticated user creating the phone.
            db (AsyncSession): The database session.

        ### Returns:
            Dict[str, str]: A dictionary with a detail message indicating the successful addition of the phone.

        ### Raises:
            HTTPException: If the specified contact does not exist or
                does not belong to the current user. Returns HTTP status code 404 (Not Found).
    """
    respond = await phones_db.add_phone(contact_id, phone, current_user, db)
    if respond:
        return {"detail": "Phone added sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.put("/update/{contact_id}/{phone_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_phone(new_phone: PhoneIn,
                       contact_id: int,
                       phone_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
        ## Update an existing phone for a specific contact belonging to the current user.

        ### Args:
            new_phone (PhoneIn): The updated phone information.
            contact_id (int): The ID of the contact to update the phone for.
            phone_id (int): The ID of the phone to update.
            current_user (User): The authenticated user updating the phone.
            db (AsyncSession): The database session.

        ### Returns:
            Dict[str, str]: A dictionary with a detail message indicating the successful update of the phone.

        ### Raises:
            HTTPException: If the specified contact or phone does not exist or
                if the phone does not belong to the specified contact or current user.
                Returns HTTP status code 404 (Not Found).
    """
    respond = await phones_db.update_phone(contact_id, phone_id, new_phone, current_user, db)
    if respond:
        return {"detail": "Phone updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found.")


@router.delete("/delete/{contact_id}/{phone_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_phone(contact_id: int,
                       phone_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
        ## Delete a phone from a specific contact belonging to the current user.

        ### Args:
            contact_id (int): The ID of the contact to delete the phone from.
            phone_id (int): The ID of the phone to delete.
            current_user (User): The authenticated user deleting the phone.
            db (AsyncSession): The database session.

        ### Returns:
            Dict[str, str]: A dictionary with a detail message indicating the successful deletion of the phone.

        ### Raises:
            HTTPException: If the specified contact or phone does not exist or
                if the phone does not belong to the specified contact or current user.
                Returns HTTP status code 404 (Not Found).
        """
    respond = await phones_db.remove_phone(contact_id, phone_id, current_user, db)
    if respond:
        return {"detail": "Phone deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found.")
