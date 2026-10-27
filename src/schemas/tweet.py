from typing import List, Optional

from pydantic import BaseModel, Field

from .common import CustomModel
from .user import UserShort


class TweetCreate(BaseModel):
    """
    Входящие данные от фронтенда при создании твита.
    """

    tweet_data: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Текст твита не может быть пустым",
    )
    tweet_media_ids: Optional[List[int]] = Field(
        default=None,
        description="Необязательный список ID медиафайлов, прикрепляемых к твиту",
    )


class TweetCreateResponse(BaseModel):
    """
    Ответ сервера при успешном создании твита.
    """

    result: bool = Field(default=True)
    tweet_id: int = Field(..., description="ID созданного твита")


class TweetLikeUser(CustomModel):
    """
    Информация о пользователе, который поставил лайк твиту.
    """

    user_id: int = Field(..., description="ID лайкнувшего пользователя")
    name: str = Field(..., description="Имя лайкнувшего пользователя")


class TweetOut(CustomModel):
    """
    Структура единичного твита в ленте.
    """

    id: int
    content: str
    attachments: List[str] = Field(
        default_factory=list, description="Список относительных ссылок"
    )
    author: UserShort = Field(..., description="Автор публикации")
    likes: List[TweetLikeUser] = Field(
        default_factory=list,
        description="Список пользователей поставивших отметку 'Нравиться'",
    )


class TweetFeedResponse(BaseModel):
    """
    Итоговый ответ сервера для GET /api/tweets.
    """

    result: bool = Field(default=True)
    tweets: List[TweetOut] = Field(
        default_factory=list, description="Отсортированная по популярности лента твитов"
    )
