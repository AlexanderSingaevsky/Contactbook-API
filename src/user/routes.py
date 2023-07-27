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


@router.post("/set_new_password", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def set_new_password(body: NewPasswordSchema,
                           current_user: User = Depends(auth_service.get_current_user),
                           db: AsyncSession = Depends(get_session),
                           rdb: Redis = Depends(redis_db.get_redis_db)):
    if body.new_password != body.r_new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")
    elif not auth_service.verify_password(body.current_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is not correct.")
    else:
        new_password_hash = auth_service.get_password_hash(body.new_password)
        await repository_users.update_password(current_user, new_password_hash, db)
        await rdb.delete(f'user:{current_user.email}')
        return {"message": "Password updated sucsessfully."}


@router.patch('/avatar', dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_avatar_user(file: UploadFile = File(),
                             current_user: User = Depends(auth_service.get_current_user),
                             db: AsyncSession = Depends(get_session)):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    await repository_users.update_avatar(current_user, src_url, db)
    return {"message": "Avatar Updated"}
