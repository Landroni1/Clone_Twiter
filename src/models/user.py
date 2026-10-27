import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Follower(Base):
    """
    Декларативная модель таблицы подписок (Followers).
    Связывает подписчика (follower) и того, на кого подписались (followed).
    """

    __tablename__ = "followers"
    follower_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    followed_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(DateTime, default=datetime.datetime.now)


class User(Base):
    """
    Модель пользователя сервиса.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False, index=True)

    tweets = relationship(
        "Tweet", back_populates="author", cascade="all, delete-orphan"
    )

    liked_tweets = relationship(
        "TweetLike", back_populates="user", cascade="all, delete-orphan"
    )

    following = relationship(
        "User",
        secondary=Follower.__table__,
        primaryjoin=id == Follower.follower_id,
        secondaryjoin=id == Follower.followed_id,
        back_populates="followers",
        lazy="selectin",
    )

    followers = relationship(
        "User",
        secondary=Follower.__table__,
        primaryjoin=id == Follower.followed_id,
        secondaryjoin=id == Follower.follower_id,
        back_populates="following",
        lazy="selectin",
    )
