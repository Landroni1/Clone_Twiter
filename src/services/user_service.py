from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Follower, User


class UserService:
    """
    Сервис управления пользователями и связями подписок
    """

    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: int) -> User:
        """
        Получает профиль пользователя по ID вместе с подгруженными
        подписчиками и подписками.
        :param db:
        :param user_id:
        :return user:
        """
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.followers), selectinload(User.following))
            .execution_options(populate_existing=True)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь с id={user_id} не найден",
            )
        return user

    @staticmethod
    async def follow(db: AsyncSession, follower: User, target_user_id: int) -> None:
        """
        Оформляет подписку текущего пользователя (follower)
        на пользователя target_user_id.
        :param db:
        :param follower:
        :param target_user_id:
        :return None:
        """
        if follower.id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя подписаться на самого себя",
            )

        target_user = await db.get(User, target_user_id)
        if not target_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID= {target_user_id} не найден",
            )

        stmt = select(Follower).where(
            Follower.follower_id == follower.id, Follower.followed_id == target_user_id
        )
        result = await db.execute(stmt)
        existing_follow = result.scalar_one_or_none()

        if existing_follow:
            return

        new_follow = Follower(follower_id=follower.id, followed_id=target_user_id)
        db.add(new_follow)
        await db.commit()

    @staticmethod
    async def unfollow(db: AsyncSession, follower: User, target_user_id: int) -> None:
        """
        Удаляет подписку текущего пользователя (follower)
        на пользователя target_user_id.
        :param db:
        :param follower:
        :param target_user_id:
        :return None:
        """

        stmt = delete(Follower).where(
            Follower.follower_id == follower.id, Follower.followed_id == target_user_id
        )
        await db.execute(stmt)
        await db.commit()
