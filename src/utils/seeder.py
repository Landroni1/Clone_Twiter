from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Follower, Tweet, User


async def seed_initial_data(db: AsyncSession) -> None:
    """
    Заполняет базу данных демонстрационными пользователями и твитами,
    если база пуста.
    """
    stmt = select(User).where(User.api_key == "test")
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return
    user_1 = User(name="Andrei Zaharov", api_key="test")
    user_2 = User(name="Vasya Smith", api_key="vasya_key")
    user_3 = User(name="Misha Kurt", api_key="misha_key")

    db.add_all([user_1, user_2, user_3])
    await db.flush()

    follow_1 = Follower(follower_id=user_1.id, followed_id=user_2.id)
    follow_2 = Follower(follower_id=user_1.id, followed_id=user_3.id)
    follow_3 = Follower(follower_id=user_2.id, followed_id=user_1.id)

    tweet_1 = Tweet(
        content="Всем привет! Добро пожаловать в корпоративный микроблог!",
        author_id=user_2.id,
    )
    tweet_2 = Tweet(content="Python и FastAPI лучшие", author_id=user_3.id)

    db.add_all([follow_1, follow_2, follow_3, tweet_1, tweet_2])
    await db.commit()
