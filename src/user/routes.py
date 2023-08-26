import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.database_postgres import get_session
from src.database_redis import redis_db
from src.user.schemas import NewPasswordSchema
from src.user import repository as repository_users
from src.auth.service import auth_service
from src.models import User
from src.config import settings

router = APIRouter(prefix='/user', tags=["user"])


@router.patch("/set_password", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def set_password(body: NewPasswordSchema, current_user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_session), rdb: Redis = Depends(redis_db.get_redis_db)):
    """
    .. http:patch:: /set_password

       Set a new password for the currently authenticated user.

       :param body: The input data containing the current password, the new password, and its confirmation.
       :type body: NewPasswordSchema
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :param rdb: Redis database instance used to delete the user's session.
       :type rdb: Redis, optional
       :return: A message indicating the status of the password update process.
       :rtype: dict
       :raises HTTPException:
           - 400 Bad Request if the two provided new passwords do not match or if the current password is incorrect.

       **Notes**:

       The function verifies the correctness of the provided current password. If it's correct, the user's password is updated in the database and the user's session is deleted from Redis.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.
       - redis_db.get_redis_db: Dependency to get the Redis database instance.
    """
    if body.new_password != body.r_new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")
    elif not auth_service.verify_password(body.current_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is not correct.")
    else:
        new_password_hash = auth_service.get_password_hash(body.new_password)
        await repository_users.update_password(current_user, new_password_hash, db)
        await rdb.delete(f'user:{current_user.email}')
        return {"message": "Password updated sucsessfully."}


@router.patch('/set_avatar', dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_user_avatar(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: AsyncSession = Depends(get_session)):
    """
    .. http:patch:: /set_avatar

       Update or set the avatar of the currently authenticated user.

       :param file: The uploaded file containing the new avatar image. If not provided, a default file input will be used.
       :type file: UploadFile, optional
       :param current_user: The authenticated user making the request. If not provided, the user will be obtained from the authentication service.
       :type current_user: User, optional
       :param db: The asynchronous database session to be used for the operation. If not provided, a session will be generated using the `get_session` dependency.
       :type db: AsyncSession, optional
       :return: A message indicating the status of the avatar update process.
       :rtype: dict

       **Notes**:

       The function uploads the new avatar image to Cloudinary under a specific public ID constructed using the authenticated user's username. The image is then resized and cropped to fit a standard avatar size. The constructed image URL is updated in the database for the current user.

       **Dependencies**:

       - RateLimiter: Limits the number of requests to 2 every 5 seconds.
       - get_current_user: Dependency to get the currently authenticated user.
       - get_session: Dependency to get the current asynchronous database session.

       **External Services**:

       - Cloudinary: Used for image uploading, manipulation, and delivery.
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    await repository_users.update_avatar(current_user, src_url, db)
    return {"message": "Avatar Updated"}
