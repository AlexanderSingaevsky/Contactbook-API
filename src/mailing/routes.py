import secrets
from fastapi import BackgroundTasks, APIRouter, Depends, HTTPException, status, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.mailing.schemas import EmailSchema, ResetPasswordSchema
from src.mailing import repository as repository_mailing
from src.mailing.service import mail_service
from src.mailing.repository import verify_email
from src.auth.service import auth_service
from src.auth.repository import get_user_by_email
from src.database_postgres import get_session
from src.database_redis import redis_db

router = APIRouter(prefix='/mailing', tags=["mailing"])


@router.get('/confirm_email/token={token}')
async def confirm_email(token: str, db: AsyncSession = Depends(get_session)):
    """
    .. http:get:: /confirm_email/token={token}

       Confirm the email of a user using a verification token.

       :param token: The verification token associated with the email confirmation.
       :type token: str
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the status of the email confirmation.
       :rtype: dict
       :raises HTTPException:
           - 400 Bad Request if the verification process encounters an error.

       **Notes**:

       The function extracts the email from the provided token and verifies if the email exists in the database. If the email is already confirmed, a message indicating the same is returned. Otherwise, the email is marked as confirmed.
    """
    email = await auth_service.get_email_from_token(token)
    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    elif user.is_confirmed:
        return {"message": "Your email is already confirmed"}
    else:
        await verify_email(user, db)
        return {"message": "Email confirmed"}


@router.post('/send_confirm_email')
async def send_confirm_email(body: EmailSchema, background_tasks: BackgroundTasks, request: Request,
                             db: AsyncSession = Depends(get_session)):
    """
    .. http:post:: /send_confirm_email

       Send a confirmation email to the user for email verification.

       :param body: The input data containing the email address to which the confirmation email will be sent.
       :type body: EmailSchema
       :param background_tasks: A utility for background tasks execution, used here to send the confirmation email asynchronously.
       :type background_tasks: BackgroundTasks
       :param request: The current HTTP request object to extract base URL for email generation.
       :type request: Request
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the status of the confirmation email sending process.
       :rtype: dict

       **Notes**:

       The function checks if the provided email exists in the database and is already confirmed. If not, it sends a confirmation email to the user's email address asynchronously.
    """
    user = await get_user_by_email(body.email, db)
    if user.is_confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(mail_service.send_verification_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.post('/send_reset_password_email')
async def send_reset_password_email(body: EmailSchema, background_tasks: BackgroundTasks, request: Request,
                                    db: AsyncSession = Depends(get_session),
                                    rdb: Redis = Depends(redis_db.get_redis_db)):
    """
    .. http:post:: /send_reset_password_email

       Send a password reset email to the user.

       :param body: The input data containing the email address to which the password reset email will be sent.
       :type body: EmailSchema
       :param background_tasks: A utility for background tasks execution, used here to send the password reset email asynchronously.
       :type background_tasks: BackgroundTasks
       :param request: The current HTTP request object to extract base URL for email generation.
       :type request: Request
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :param rdb: Redis database instance used to store the reset token temporarily.
       :type rdb: Redis, optional
       :return: A message indicating the status of the password reset email sending process.
       :rtype: dict

       **Notes**:

       The function checks if the provided email exists in the database. If it does, a password reset token is generated and stored in the Redis database with a 15-minute expiration. A password reset email containing the token is then sent to the user's email address asynchronously.
    """
    user = await get_user_by_email(body.email, db)
    if user:
        reset_token = secrets.token_urlsafe(32)
        await rdb.set(f"{reset_token}", user.email)
        await rdb.expire(f"{reset_token}", 900)
        background_tasks.add_task(mail_service.send_password_reset_mail, user.email, user.username, request.base_url,
                                  reset_token)
    return {"message": "Check your email for password reset."}


@router.patch('/reset_password/token={reset_token}')
async def reset_password(body: ResetPasswordSchema, reset_token: str, db: AsyncSession = Depends(get_session),
                         rdb: Redis = Depends(redis_db.get_redis_db)):
    """
    .. http:patch:: /reset_password/token={reset_token}

       Reset the user's password using a verification token.

       :param body: The input data containing the new password and its confirmation.
       :type body: ResetPasswordSchema
       :param reset_token: The verification token associated with the password reset process.
       :type reset_token: str
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :param rdb: Redis database instance used to fetch the reset token and associated email.
       :type rdb: Redis, optional
       :return: A message indicating the status of the password reset process.
       :rtype: dict
       :raises HTTPException:
           - 400 Bad Request if the reset token is invalid or the two provided passwords do not match.

       **Notes**:

       The function fetches the associated email from the Redis database using the provided reset token. It then checks the validity of the new password and its confirmation. If all checks pass, the user's password is updated in the database, and the reset token is deleted from Redis.
    """
    user = await rdb.get(f"{reset_token}")
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error.")
    elif body.new_password != body.r_new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")
    else:
        user = user.decode('utf-8')
        current_user = await get_user_by_email(user, db)
        new_password_hash = auth_service.get_password_hash(body.new_password)
        await repository_mailing.update_password(current_user, new_password_hash, db)
        await rdb.delete(f"{reset_token}")
        return {"message": "Password updated sucsessfully."}
