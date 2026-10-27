import os
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.config import settings
from src.models import TweetMedia

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "files"


@pytest.mark.asyncio
async def test_upload_media_success(client: AsyncClient, test_users, db_session):
    u1, _ = test_users
    image_path = FIXTURES_DIR / "test_image_1.jpg"

    with open(image_path, "rb") as f:
        files = {"file": ("test_image_1.jpg", f, "image/jpeg")}
        resp = await client.post(
            "/api/medias", headers={"api-key": u1.api_key}, files=files
        )

    assert resp.status_code == 201
    data = resp.json()
    assert data["result"] is True
    assert "media_id" in data
    media_id = data["media_id"]

    stmt = select(TweetMedia).where(TweetMedia.id == media_id)
    result = await db_session.execute(stmt)
    media_record = result.scalar_one_or_none()
    assert media_record is not None

    filename = os.path.basename(media_record.file_path)
    real_saved_file_path = os.path.join(settings.UPLOAD_DIR, filename)

    assert os.path.exists(real_saved_file_path)
    assert os.path.getsize(real_saved_file_path) > 0


@pytest.mark.asyncio
async def test_upload_invalid_text_file(client: AsyncClient, test_users):
    u1, _ = test_users
    txt_path = FIXTURES_DIR / "test_documents.txt"

    with open(txt_path, "rb") as f:
        files = {"file": ("test_documents.txt", f, "text/plain")}
        response = await client.post(
            "/api/medias", headers={"api-key": u1.api_key}, files=files
        )

    assert response.status_code == 400
    data = response.json()
    assert data["result"] is False
    assert data["error_type"] == "InvalidFileFormatError"


@pytest.mark.asyncio
async def test_upload_media_and_attach_to_tweet(client: AsyncClient, test_users):
    u1, _ = test_users
    image_path = FIXTURES_DIR / "test_image_1.jpg"

    with open(image_path, "rb") as f:
        files = {"file": ("test_image_1.jpg", f, "image/jpeg")}
        media_resp = await client.post(
            "/api/medias", headers={"api-key": u1.api_key}, files=files
        )
    media_id = media_resp.json()["media_id"]

    tweet_resp = await client.post(
        "/api/tweets",
        headers={"api-key": u1.api_key},
        json={
            "tweet_data": "Тестовый твит с настоящей картинкой",
            "tweet_media_ids": [media_id],
        },
    )
    assert tweet_resp.status_code == 201

    feed_resp = await client.get("/api/tweets", headers={"api-key": u1.api_key})
    feed_data = feed_resp.json()
    assert feed_data["result"] is True
    tweet = feed_data["tweets"][0]
    assert len(tweet["attachments"]) == 1
    assert tweet["attachments"][0].startswith("/static/uploads/")
