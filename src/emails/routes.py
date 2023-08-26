from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

import src.emails.repository as emails_db
from src.database_postgres import get_session
from src.emails.schemas import EmailIn, EmailOut
from src.auth.service import auth_service
from src.models import User

router = APIRouter(prefix='/emails', tags=["emails"])


@router.get("/read/contact={contact_id}", response_model=list[EmailOut])
async def read_emails(contact_id: int, current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_session)):
    """
    .. http:get:: /read/contact={contact_id}

       Retrieve all emails associated with a specific contact ID for the current user.

       :param contact_id: The unique identifier of the contact for which emails are to be retrieved.
       :type contact_id: int
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the query. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A list of `EmailOut` objects representing the emails associated with the specified contact ID for the current user.
       :rtype: List[EmailOut]
       :raises HTTPException: If no emails are found for the specified contact ID and current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    all_emails = await emails_db.get_all_emails(contact_id, current_user, db)
    if all_emails:
        return all_emails
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emails not found.")


@router.post("/create/contact={contact_id}", status_code=status.HTTP_201_CREATED)
async def create_email(contact_id: int, email: EmailIn, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
    .. http:post:: /create/contact={contact_id}

       Add a new email to the specified contact for the current user.

       :param contact_id: The unique identifier of the contact to which the email will be added.
       :type contact_id: int
       :param email: The input data required to add a new email.
       :type email: EmailIn
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful addition of the email.
       :rtype: dict
       :status 201: Email was successfully added to the contact.
       :raises HTTPException: If the specified contact is not found for the current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    respond = await emails_db.add_email(contact_id, email, current_user, db)
    if respond:
        return {"detail": "Email added sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.put("/update/contact={contact_id}&email={email_id}")
async def update_email(new_email: EmailIn, contact_id: int, email_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
    .. http:put:: /update/contact={contact_id}&email={email_id}

       Update an existing email for a specified contact of the current user.

       :param new_email: The input data containing the updated details of the email.
       :type new_email: EmailIn
       :param contact_id: The unique identifier of the contact associated with the email to be updated.
       :type contact_id: int
       :param email_id: The unique identifier of the email to be updated.
       :type email_id: int
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful update of the email.
       :rtype: dict
       :raises HTTPException: If the specified email is not found for the given contact ID and current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    respond = await emails_db.update_email(contact_id, email_id, new_email, current_user, db)
    if respond:
        return {"detail": "Email updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")


@router.delete("/delete/contact={contact_id}&email={email_id}")
async def delete_email(contact_id: int, email_id: int, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
    .. http:delete:: /delete/contact={contact_id}&email={email_id}

       Delete a specific email associated with a given contact ID for the current user.

       :param contact_id: The unique identifier of the contact associated with the email to be deleted.
       :type contact_id: int
       :param email_id: The unique identifier of the email to be deleted.
       :type email_id: int
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the successful deletion of the email.
       :rtype: dict
       :raises HTTPException: If the specified email is not found for the given contact ID and current user, an HTTPException with a 404 status code is raised.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
    """
    respond = await emails_db.remove_email(contact_id, email_id, current_user, db)
    if respond:
        return {"detail": "Email deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
