from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import get_user_by_email
from src.models import User


async def verify_email(user: User, session: AsyncSession) -> None:
    async with session.begin():
        user.is_confirmed = True
        await session.commit()
