import os
import uuid

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import TweetMedia

UPLOAD_DIR = os.path.join("static", "uploads")


class MediaService:
    """Сервис для обработки и сохранения медиафайлов."""

    @staticmethod
    async def save_media(db: AsyncSession, file: UploadFile) -> TweetMedia:
        """
        Сохраняет входящий файл из формы на диск и создает запись в таблице tweet_media.
        :param db:
        :param file:
        :return media_entry:
        """
        upload_dir = settings.UPLOAD_DIR
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)

        file_extension = (
            os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
        )
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"

        disk_path = os.path.join(upload_dir, unique_filename)
        web_path = f"/static/uploads/{unique_filename}"

        try:
            async with aiofiles.open(disk_path, mode="wb") as out_file:
                while content := await file.read(1024 * 1024):
                    await out_file.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Не удалось сохранить файл на диск: {str(e)}",
            )

        media_entry = TweetMedia(file_path=web_path, tweet_id=None)
        db.add(media_entry)
        await db.commit()
        await db.refresh(media_entry)

        return media_entry
