from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User


async def update_password(user: User, pwd_hash: str, session: AsyncSession) -> None:
    async with session.begin():
        user.password = pwd_hash
        await session.commit()


async def update_avatar(user: User, url: str, session: AsyncSession) -> None:
    async with session.begin():
        user.avatar = url
        await session.commit()
