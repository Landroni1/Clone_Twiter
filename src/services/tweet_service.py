from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import Subquery, delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Follower, Tweet, TweetLike, TweetMedia, User


class TweetService:
    """
    Сервис для работы с публикациями, лайками и новостной лентой.
    """

    @staticmethod
    async def create_tweet(
        db: AsyncSession,
        user: User,
        tweet_data: str,
        media_ids: Optional[List[int]] = None,
    ) -> Tweet:
        """
        Создает твит и связывает с ним загруженные ранее картинки.
        :param db:
        :param user:
        :param tweet_data:
        :param media_ids:
        :return Tweet:
        """
        new_tweet = Tweet(content=tweet_data, author_id=user.id)
        db.add(new_tweet)
        await db.flush()

        if media_ids:
            stmt = select(TweetMedia).where(TweetMedia.id.in_(media_ids))
            result = await db.execute(stmt)
            media_items = result.scalars().all()

            for media in media_items:
                media.tweet_id = new_tweet.id
        await db.commit()
        await db.refresh(new_tweet)
        return new_tweet

    @staticmethod
    async def delete_tweet(db: AsyncSession, tweet_id: int, user: User) -> None:
        """
        Удаляет твит с проверкой авторства.
        :param db:
        :param tweet_id:
        :param user:
        :return None:
        """
        tweet = await db.get(Tweet, tweet_id)
        if not tweet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Твит с id={tweet_id} не найден",
            )
        if tweet.author_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете удалить чужой твит",
            )

        await db.delete(tweet)
        await db.commit()

    @staticmethod
    async def add_like(db: AsyncSession, tweet_id: int, user: User) -> None:
        """
        Ставит отметку «Нравится» на твит.
        :param db:
        :param tweet_id:
        :param user:
        :return None:
        """
        tweet = await db.get(Tweet, tweet_id)
        if not tweet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Твит с id={tweet_id} не найден",
            )

        stmt = select(TweetLike).where(
            TweetLike.tweet_id == tweet_id, TweetLike.user_id == user.id
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            return

        like = TweetLike(tweet_id=tweet_id, user_id=user.id)
        db.add(like)
        await db.commit()

    @staticmethod
    async def remove_like(db: AsyncSession, tweet_id: int, user: User) -> None:
        """
        Убираем отметку «Нравится» на твит.
        :param db:
        :param tweet_id:
        :param user:
        :return None:
        """
        stmt = delete(TweetLike).where(
            TweetLike.tweet_id == tweet_id, TweetLike.user_id == user.id
        )
        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def get_feed(db: AsyncSession, user: User) -> List[Tweet]:
        """
        Формирует персонализированную новостную ленту пользователя:
        - Включает твиты пользователей, на которых он подписан
        (и свои собственные твиты).
        - Сортирует строго по популярности (количеству лайков)
        в порядке убывания.
        :param db:
        :param user:
        :return List[Tweet]:
        """
        following_subquery: Subquery = (
            select(Follower.followed_id)
            .where(Follower.follower_id == user.id)
            .subquery()
        )
        stmt = (
            select(Tweet)
            .outerjoin(TweetLike, Tweet.id == TweetLike.tweet_id)
            .where(
                (Tweet.author_id.in_(following_subquery)) | (Tweet.author_id == user.id)
            )
            .options(
                selectinload(Tweet.author),
                selectinload(Tweet.likes),
                selectinload(Tweet.media),
            )
            .group_by(Tweet.id)
            .order_by(desc(func.count(TweetLike.user_id)), desc(Tweet.created_at))
        )
        result = await db.execute(stmt)
        return list(result.scalars().unique().all())
