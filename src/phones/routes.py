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
    """
    .. http:get:: /read/contact={contact_id}

       Retrieve all phone numbers associated with a specific contact ID for the current user.

       :param contact_id: The unique identifier of the contact for which phone numbers are to be retrieved.
       :type contact_id: int
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the query. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A list of `PhoneOut` objects representing the phone numbers associated with the specified contact ID for the current user.
       :rtype: List[PhoneOut]
       :raises HTTPException: If no phone numbers are found for the specified contact ID and current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    all_phones = await phones_db.get_all_phones(contact_id, current_user, db)
    if all_phones:
        return all_phones
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phones not found.")


@router.post("/create/contact={contact_id}", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_phone(contact_id: int, phone: PhoneIn, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
    .. http:post:: /create/contact={contact_id}

       Add a new phone number to the specified contact for the current user.

       :param contact_id: The unique identifier of the contact to which the phone number will be added.
       :type contact_id: int
       :param phone: The input data required to add a new phone number.
       :type phone: PhoneIn
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful addition of the phone number.
       :rtype: dict
       :status 201: Phone number was successfully added to the contact.
       :raises HTTPException: If the specified contact is not found for the current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    respond = await phones_db.add_phone(contact_id, phone, current_user, db)
    if respond:
        return {"detail": "Phone added sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.put("/update/contact={contact_id}&phone={phone_id}",
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_phone(new_phone: PhoneIn, contact_id: int, phone_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
    .. http:put:: /update/contact={contact_id}&phone={phone_id}

       Update an existing phone number for a specified contact of the current user.

       :param new_phone: The input data containing the updated details of the phone number.
       :type new_phone: PhoneIn
       :param contact_id: The unique identifier of the contact associated with the phone number to be updated.
       :type contact_id: int
       :param phone_id: The unique identifier of the phone number to be updated.
       :type phone_id: int
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful update of the phone number.
       :rtype: dict
       :raises HTTPException: If the specified phone number is not found for the given contact ID and current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    respond = await phones_db.update_phone(contact_id, phone_id, new_phone, current_user, db)
    if respond:
        return {"detail": "Phone updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found.")


@router.delete("/delete/contact={contact_id}&phone={phone_id}",
               dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_phone(contact_id: int, phone_id: int, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
    .. http:delete:: /delete/contact={contact_id}&phone={phone_id}

       Delete a specific phone number associated with a given contact ID for the current user.

       :param contact_id: The unique identifier of the contact associated with the phone number to be deleted.
       :type contact_id: int
       :param phone_id: The unique identifier of the phone number to be deleted.
       :type phone_id: int
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful deletion of the phone number.
       :rtype: dict
       :raises HTTPException: If the specified phone number is not found for the given contact ID and current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    respond = await phones_db.remove_phone(contact_id, phone_id, current_user, db)
    if respond:
        return {"detail": "Phone deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found.")
