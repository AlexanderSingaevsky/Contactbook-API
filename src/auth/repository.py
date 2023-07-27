from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models import User
from src.auth.schemas import UserModel


async def get_user_by_email(email: str, session: AsyncSession) -> User:
    async with session.begin():
        stmt = select(User).where(User.email == email).limit(1)
        result = await session.execute(stmt)
        return result.scalars().unique().one_or_none()


async def create_user(body: UserModel, session: AsyncSession) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    async with session.begin():
        session.add(new_user)
    return new_user


async def update_token(user: User, token: str | None, session: AsyncSession) -> None:
    async with session.begin():
        user.refresh_token = token
        await session.commit()
