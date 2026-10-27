from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user
from src.database import get_db
from src.models import User
from src.schemas import MediaUploadResponse
from src.services import MediaService

router = APIRouter(prefix="/api/medias", tags=["Media"])


@router.post(
    "",
    response_model=MediaUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка медиафайла для твита",
)
async def upload_media(
    file: UploadFile = File(..., description="Загружаемый файл (изображение)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Принимает файл из формы (multipart/form-data),
    сохраняет его на диск/в хранилище,
    создает запись в таблице tweet_media с tweet_id=None
    и возвращает media_id.

    :param file:
    :param current_user:
    :param db:
    :return media_id:
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "result": False,
                "error_type": "InvalidFileFormatError",
                "error_message": "Only image files are allowed",
            },
        )
    media = await MediaService.save_media(db=db, file=file)
    return MediaUploadResponse(result=True, media_id=int(media.id))
