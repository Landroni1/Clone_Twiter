from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.database import get_db
from src.models import User
from src.schemas import (
    BaseResponse,
    TweetCreate,
    TweetCreateResponse,
    TweetFeedResponse,
    TweetOut,
)
from src.services import TweetService

router = APIRouter(prefix="/api/tweets", tags=["Tweets"])


@router.post(
    "",
    response_model=TweetCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Опубликовать новый твит",
)
async def create_tweet(
    tweet_in: TweetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Создает новый твит текущего пользователя.
    Если переданы tweet_media_ids, они связываются с данным твитом.
    :param tweet_in:
    :param current_user:
    :param db:
    :return True:
    """
    tweet = await TweetService.create_tweet(
        db=db,
        user=current_user,
        tweet_data=tweet_in.tweet_data,
        media_ids=tweet_in.tweet_media_ids,
    )
    return TweetCreateResponse(result=True, tweet_id=int(tweet.id))


@router.delete(
    "/{tweet_id}",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить твит",
)
async def delete_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаляет твит по ID.
    Внутри сервиса строго проверяется, что автор твита совпадает с current_user.
    :param tweet_id:
    :param current_user:
    :param db:
    :return True:
    """
    await TweetService.delete_tweet(db=db, tweet_id=tweet_id, user=current_user)
    return BaseResponse(result=True)


@router.post(
    "/{tweet_id}/likes",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Поставить отметку «Нравится»",
)
async def add_like(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ставит отметку «Нравится» на твит от имени текущего пользователя.
    :param tweet_id:
    :param current_user:
    :param db:
    :return True:
    """
    await TweetService.add_like(db=db, tweet_id=tweet_id, user=current_user)
    return BaseResponse(result=True)


@router.delete(
    "/{tweet_id}/likes",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Удалить отметку «Нравится»",
)
async def delete_like(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Убирает отметку «Нравится» на твит от имени текущего пользователя.
    :param tweet_id:
    :param current_user:
    :param db:
    :return True:
    """
    await TweetService.remove_like(db=db, tweet_id=tweet_id, user=current_user)
    return BaseResponse(result=True)


@router.get(
    "",
    response_model=TweetFeedResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить новостную ленту",
)
async def get_feed(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Формирует новостную ленту:
    - Твиты пользователей, на которых подписан текущий юзер + свои собственные твиты.
    - Сортировка по популярности (количеству отметок «Нравится») в порядке убывания.
    :param current_user:
    :param db:
    :return tweets:
    """
    tweets = await TweetService.get_feed(db=db, user=current_user)
    return TweetFeedResponse(
        result=True, tweets=[TweetOut.model_validate(tweet) for tweet in tweets]
    )
