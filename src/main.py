import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api import api_router
from src.config import settings
from src.database import AsyncSessionLocal, Base, engine
from src.schemas import ErrorResponse
from src.utils.seeder import seed_initial_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.APP_TITLE,
    description="Бэкенд корпоративного сервиса",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            result=False, error_type="ValidationError", error_message=str(exc.errors())
        ).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "error_type" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            result=False,
            error_type=exc.__class__.__name__,
            error_message=str(exc.detail),
        ).model_dump(),
    )


app.include_router(api_router)

if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app.mount(
    settings.STATIC_URL_PREFIX,
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads",
)
