from fastapi import APIRouter

from src.api.medias import router as medias_router
from src.api.tweets import router as tweets_router
from src.api.users import router as users_router

api_router = APIRouter()

api_router.include_router(tweets_router)
api_router.include_router(users_router)
api_router.include_router(medias_router)

__all__ = ["api_router"]
