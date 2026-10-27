from pydantic import BaseModel, ConfigDict, Field


class CustomModel(BaseModel):
    """Базовый класс Pydantic v2 для автоматического маппинга из моделей SQLAlchemy."""

    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseModel):
    """Стандартный успешный ответ без тела данных."""

    result: bool = Field(default=True, description="Статус операции")


class ErrorResponse(BaseModel):
    """Единый формат ошибки."""

    result: bool = Field(default=False, description="Флаг успешности")
    error_type: str = Field(..., description="Класс или тип ошибки")
    error_message: str = Field(..., description="Понятное описание причины ошибки")
