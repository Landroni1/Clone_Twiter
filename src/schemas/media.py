from pydantic import BaseModel, Field


class MediaUploadResponse(BaseModel):
    """
    Ответ сервера при успешной загрузке файла через форму.
    """

    result: bool = Field(default=True)
    media_id: int = Field(..., description="ID сохраненного файла в базе данных")
