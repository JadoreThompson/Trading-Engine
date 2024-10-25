from contextlib import asynccontextmanager

import argon2

# Local
from config import DB_ENGINE, API_KEY_ALIAS, ph
from db_models import Users

# SA
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from exceptions import DoesNotExist


@asynccontextmanager
async def get_session():
    """
    Returns async SQLAlchemy session
    :return:
    """
    async with AsyncSession(DB_ENGINE) as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_user(api_key: str) -> Users:
    """
        Checks each account if the API Key matches
        TODO: Improve efficiency for large system
        :returns: user -> Users
    """
    async with get_session() as session:
        result = await session.execute(
            select(Users)
            .where(Users.api_key != None)
        )
        users = result.scalars().all()
        try:
            i = 1
            for user in users:
                try:
                    if ph.verify(user.api_key, api_key):
                        return user
                except argon2.exceptions.VerifyMismatchError:
                    continue
                except argon2.exceptions.InvalidHashError:
                    continue
            raise DoesNotExist('User')
        except DoesNotExist:
            raise
