from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

import src.contacts.repository as contacts_db
from src.database_postgres import get_session
from src.contacts.schemas import ContactOut, ContactIn
from src.models import User
from src.auth.service import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/all", response_model=list[ContactOut], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contacts(current_user: User = Depends(auth_service.get_current_user),
                        db: AsyncSession = Depends(get_session)):
    """
       ## Retrieve all contacts for the current user.

       ### Args:
           current_user (User): The authenticated user accessing the contacts.
           db (AsyncSession): The database session.

       ### Returns:
           List[ContactOut]: A list of contacts belonging to the current user.

       ### Raises:
           HTTPException: If no contacts are found for the current user.
               Returns HTTP status code 404 (Not Found).
       """
    all_contacts = await contacts_db.get_contacts(current_user, db)
    if all_contacts:
        return all_contacts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.get("/{contact_id}", response_model=ContactOut, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contact(contact_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session)):
    """
        ## Retrieve a specific contact for the current user by ID.

        ### Args:
            contact_id (int): The ID of the contact to retrieve.
            current_user (User): The authenticated user accessing the contact.
            db (AsyncSession): The database session.

        ### Returns:
            ContactOut: The contact matching the provided ID.

        ### Raises:
            HTTPException: If the contact with the provided ID does not exist or
                does not belong to the current user. Returns HTTP status code 404 (Not Found).
        """
    contact = await contacts_db.get_contact(contact_id, current_user, db)
    if contact:
        return contact
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.get("/search/{prompt}", response_model=list[ContactOut],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_contact(prompt: str,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    """
        ## Search for contacts that match the provided prompt for the current user.

        ### Args:
            prompt (str): The search prompt or keyword.
            current_user (User): The authenticated user performing the search.
            db (AsyncSession): The database session.

        ### Returns:
            List[ContactOut]: A list of contacts that match the search prompt.

        ### Raises:
            HTTPException: If no contacts match the search prompt for the current user.
                Returns HTTP status code 404 (Not Found).
        """
    all_contacts = await contacts_db.search_in_contacts(prompt, current_user, db)
    if all_contacts:
        return all_contacts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.post("/create", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(contact: ContactIn,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    """
        ## Create a new contact for the current user.

        ### Args:
            contact (ContactIn): The contact information to create.
            current_user (User): The authenticated user creating the contact.
            db (AsyncSession): The database session.

        ### Returns:
            Dict[str, str]: A dictionary with a detail message indicating the successful creation of the contact.

        ### Raises:
            HTTPException: If there is an error creating the contact.
    """
    await contacts_db.add_contact(contact, current_user, db)
    return {"detail": "Contact created sucsessfully."}


@router.put("/update/{contact_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_contact(contact: ContactIn,
                         contact_id: int,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    """
        ## Update an existing contact for the current user.

        ### Args:
            contact (ContactIn): The updated contact information.
            contact_id (int): The ID of the contact to update.
            current_user (User): The authenticated user updating the contact.
            db (AsyncSession): The database session.

        ### Returns:
            Dict[str, str]: A dictionary with a detail message indicating the successful update of the contact.

        ### Raises:
            HTTPException: If the contact with the provided ID does not exist or
                does not belong to the current user. Returns HTTP status code 404 (Not Found).
        """
    respond = await contacts_db.update_contact(contact, contact_id, current_user, db)
    if respond:
        return {"detail": "Contact updated sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")


@router.delete("/delete/{contact_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_contact(contact_id: int,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_session)):
    """
        ## Delete a contact for the current user by ID.

        ### Args:
            contact_id (int): The ID of the contact to delete.
            current_user (User): The authenticated user deleting the contact.
            db (AsyncSession): The database session.

        ### Returns:
            Dict[str, str]: A dictionary with a detail message indicating the successful deletion of the contact.

        ### Raises:
            HTTPException: If the contact with the provided ID does not exist or
                does not belong to the current user. Returns HTTP status code 404 (Not Found).
        """
    respond = await contacts_db.remove_contact(contact_id, current_user, db)
    if respond:
        return {"detail": "Contact deleted sucsessfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")
