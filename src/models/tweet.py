import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from src.database import Base


class TweetLike(Base):
    """
    Таблица отметок «Нравится» (лайков).
    Связывает пользователя (user_id) и понравившийся твит (tweet_id).
    """

    __tablename__ = "tweet_likes"
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    tweet_id = Column(
        Integer, ForeignKey("tweets.id", ondelete="CASCADE"), primary_key=True
    )

    user = relationship("User", back_populates="liked_tweets", lazy="selectin")
    tweet = relationship("Tweet", back_populates="likes")

    @property
    def name(self) -> str:
        """
        Вспомогательное свойство для Pydantic.
        Фронтенд в likes ожидает: {"user_id": int, "name": str}.
        """
        return self.user.name if self.user else ""


class Tweet(Base):
    """
    Модель твита.
    """

    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=datetime.datetime.now, index=True)

    author = relationship("User", back_populates="tweets", lazy="selectin")
    likes = relationship(
        "TweetLike",
        back_populates="tweet",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    media = relationship(
        "TweetMedia",
        back_populates="tweet",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def attachments(self) -> list[str]:
        """
        Вспомогательное свойство для Pydantic.
        """
        return [item.file_path for item in self.media]
