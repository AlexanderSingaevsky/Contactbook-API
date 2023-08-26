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
    """
    .. http:get:: /read

       Retrieve the list of contacts for the current user.

       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the query. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A list of `ContactOut` objects representing the contacts associated with the current user.
       :rtype: List[ContactOut]
       :raises HTTPException: If no contacts are found for the current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
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
    """
    .. http:get:: /contact={contact_id}

       Retrieve a specific contact by its ID for the current user.

       :param contact_id: The unique identifier of the contact to retrieve.
       :type contact_id: int
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the query. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A `ContactOut` object representing the contact associated with the given ID for the current user.
       :rtype: ContactOut
       :raises HTTPException: If the contact is not found for the given ID and current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    all_contacts = await contacts_db.search_in_contacts(search_string, current_user, db)
    if all_contacts:
        return all_contacts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.post("/create", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(contact: ContactIn, current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    """
    .. http:post:: /create

       Create a new contact for the current user.

       :param contact: The input data required to create a new contact.
       :type contact: ContactIn
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful creation of the contact.
       :rtype: dict
       :status 201: Contact was successfully created.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    await contacts_db.add_contact(contact, current_user, db)
    return {"detail": "Contact created sucsessfully."}


@router.put("/update/contact={contact_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_contact(contact: ContactIn, contact_id: int,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    """
    .. http:put:: /update/contact={contact_id}

       Update an existing contact for the current user based on the provided contact ID.

       :param contact: The input data required to update the contact details.
       :type contact: ContactIn
       :param contact_id: The unique identifier of the contact to be updated.
       :type contact_id: int
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful update of the contact.
       :rtype: dict
       :raises HTTPException: If the contact is not found for the given ID and current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    respond = await contacts_db.update_contact(contact, contact_id, current_user, db)
    if respond:
        return {"detail": "Contact updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.delete("/delete/contact={contact_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_contact(contact_id: int, current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    """
    .. http:delete:: /delete/contact={contact_id}

       Delete a specific contact for the current user based on the provided contact ID.

       :param contact_id: The unique identifier of the contact to be deleted.
       :type contact_id: int
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful deletion of the contact.
       :rtype: dict
       :raises HTTPException: If the contact is not found for the given ID and current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    respond = await contacts_db.remove_contact(contact_id, current_user, db)
    if respond:
        return {"detail": "Contact deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
