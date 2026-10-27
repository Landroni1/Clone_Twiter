from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.database import get_db
from src.models import User
from src.schemas import BaseResponse, UserProfileResponse
from src.services import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о собственном пользователе",
)
async def get_my_profile(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Возвращает полную информацию о текущем авторизованном пользователе,
    включая списки подписчиков (followers) и подписок (following).
    :param current_user:
    :param db:
    :return user:
    """
    user = await UserService.get_user_profile(db=db, user_id=int(current_user.id))
    return UserProfileResponse(result=True, user=user)


@router.get(
    "/{user_id}",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о другом пользователе по ID",
)
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Возвращает информацию о профиле любого пользователя по его идентификатору.
    Доступно только авторизованному пользователю (проверяется заголовок api-key).
    :param user_id:
    :param db:
    :param current_user:
    :return user:
    """
    user = await UserService.get_user_profile(db=db, user_id=user_id)
    return UserProfileResponse(result=True, user=user)


@router.post(
    "/{user_id}/follow",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Подписаться на пользователя",
)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Оформляет подписку текущего пользователя на пользователя user_id.
    :param user_id:
    :param current_user:
    :param db:
    :return True:
    """
    await UserService.follow(db=db, follower=current_user, target_user_id=user_id)
    return BaseResponse(result=True)


@router.delete(
    "/{user_id}/follow",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Отписаться от пользователя",
)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Отменяет подписку текущего пользователя на пользователя user_id.
    :param user_id:
    :param current_user:
    :param db:
    :return True:
    """
    await UserService.unfollow(db=db, follower=current_user, target_user_id=user_id)
    return BaseResponse(result=True)
