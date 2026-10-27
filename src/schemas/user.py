from typing import List

from pydantic import BaseModel, Field

from .common import CustomModel


class UserShort(CustomModel):
    """
    Краткая карточка пользователя.
    """

    id: int = Field(..., description="Идентификатор пользователя")
    name: str = Field(..., description="Имя пользователя")


class UserProfile(CustomModel):
    """
    Структура данных профиля пользователя.
    """

    id: int
    name: str
    followers: List[UserShort] = Field(
        default_factory=list, description="Пользователи, подписанные на этого человека"
    )
    following: List[UserShort] = Field(
        default_factory=list,
        description="Пользователи, на которых подписан этот человек",
    )


class UserProfileResponse(BaseModel):
    """
    Итоговый ответ сервера для GET.
    """

    result: bool = Field(default=True)
    user: UserProfile
