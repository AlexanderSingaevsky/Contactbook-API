from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

import src.emails.repository as emails_db
from src.database_postgres import get_session
from src.emails.schemas import EmailIn, EmailOut
from src.auth.service import auth_service
from src.models import User

router = APIRouter(prefix='/emails', tags=["emails"])


@router.get("/all/{contact_id}", response_model=list[EmailOut], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_emails(contact_id: int,
                      current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_session)):
    """
        ## Retrieve all emails for a specific contact belonging to the current user.

        ### Args:
            contact_id (int): The ID of the contact whose emails to retrieve.
            current_user (User): The authenticated user accessing the emails.
            db (AsyncSession): The database session.

        ### Returns:
            List[EmailOut]: A list of emails belonging to the specified contact.

        ### Raises:
            HTTPException: If no emails are found for the specified contact or
                if the contact does not belong to the current user.
                Returns HTTP status code 404 (Not Found).
        """
    all_emails = await emails_db.get_all_emails(contact_id, current_user, db)
    if all_emails:
        return all_emails
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emails not found.")


@router.post("/create/{contact_id}", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_email(contact_id: int,
                       email: EmailIn,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
        ## Create a new email for a specific contact belonging to the current user.

        ### Args:
            contact_id (int): The ID of the contact to add the email to.
            email (EmailIn): The email information to create.
            current_user (User): The authenticated user creating the email.
            db (AsyncSession): The database session.

        ### Returns:
            Dict[str, str]: A dictionary with a detail message indicating the successful addition of the email.

        ### Raises:
            HTTPException: If the specified contact does not exist or
                does not belong to the current user. Returns HTTP status code 404 (Not Found).
        """
    respond = await emails_db.add_email(contact_id, email, current_user, db)
    if respond:
        return {"detail": "Email added sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.put("/update/{contact_id}/{email_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_email(new_email: EmailIn,
                       contact_id: int,
                       email_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
       ## Update an existing email for a specific contact belonging to the current user.

       ### Args:
           new_email (EmailIn): The updated email information.
           contact_id (int): The ID of the contact to update the email for.
           email_id (int): The ID of the email to update.
           current_user (User): The authenticated user updating the email.
           db (AsyncSession): The database session.

       ### Returns:
           Dict[str, str]: A dictionary with a detail message indicating the successful update of the email.

       ### Raises:
           HTTPException: If the specified contact or email does not exist or
               if the email does not belong to the specified contact or current user.
               Returns HTTP status code 404 (Not Found).
       """
    respond = await emails_db.update_email(contact_id, email_id, new_email, current_user, db)
    if respond:
        return {"detail": "Email updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")


@router.delete("/delete/{contact_id}/{email_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_email(contact_id: int,
                       email_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
        ## Delete an email from a specific contact belonging to the current user.

        ### Args:
            contact_id (int): The ID of the contact to delete the email from.
            email_id (int): The ID of the email to delete.
            current_user (User): The authenticated user deleting the email.
            db (AsyncSession): The database session.

        ### Returns:
            Dict[str, str]: A dictionary with a detail message indicating the successful deletion of the email.

        ### Raises:
            HTTPException: If the specified contact or email does not exist or
                if the email does not belong to the specified contact or current user.
                Returns HTTP status code 404 (Not Found).
        """
    respond = await emails_db.remove_email(contact_id, email_id, current_user, db)
    if respond:
        return {"detail": "Email deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")
