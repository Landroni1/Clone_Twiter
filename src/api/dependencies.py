from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User


async def get_current_user(
    api_key: str = Header(
        ..., alias="api-key", description="Токен авторизации пользователя"
    ),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Зависимость (Dependency) для авторизации пользователя.

    Считывает заголовок 'api-key'.
    Ищет пользователя в PostgreSQL.
    Если пользователь не найден, возвращает 401 с телом ошибки по формату.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "result": False,
                "error_type": "AuthenticationError",
                "error_message": "Header 'api-key' is missing",
            },
        )

    query = select(User).where(User.api_key == api_key)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "result": False,
                "error_type": "AuthenticationError",
                "error_message": f"User with api-key '{api_key}' not found",
            },
        )
    return user
