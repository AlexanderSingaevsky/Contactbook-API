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
