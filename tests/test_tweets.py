import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_delete_tweet(client: AsyncClient, test_users):
    u1, u2 = test_users
    resp = await client.post(
        "/api/tweets",
        headers={"api-key": u1.api_key},
        json={"tweet_data": "Тестовый твит", "tweet_media_ids": []},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["result"] is True
    tweet_id = data["tweet_id"]

    resp_forbidden = await client.delete(
        f"/api/tweets/{tweet_id}", headers={"api-key": u2.api_key}
    )
    assert resp_forbidden.status_code == 403

    resp_delete = await client.delete(
        f"/api/tweets/{tweet_id}", headers={"api-key": u1.api_key}
    )
    assert resp_delete.status_code == 200
    assert resp_delete.json()["result"] is True


@pytest.mark.asyncio
async def test_likes_and_feed(client: AsyncClient, test_users):
    u1, u2 = test_users
    resp = await client.post(
        "/api/tweets",
        headers={"api-key": u1.api_key},
        json={"tweet_data": "Твит для лайка"},
    )
    tweet_id = resp.json()["tweet_id"]

    resp_like = await client.post(
        f"/api/tweets/{tweet_id}/likes", headers={"api-key": u2.api_key}
    )
    assert resp_like.status_code == 200
    assert resp_like.json()["result"] is True

    await client.post(f"/api/users/{u1.id}/follow", headers={"api-key": u2.api_key})

    resp_feed = await client.get("/api/tweets", headers={"api-key": u2.api_key})
    assert resp_feed.status_code == 200
    feed_data = resp_feed.json()
    assert feed_data["result"] is True
    assert len(feed_data["tweets"]) >= 1
    assert feed_data["tweets"][0]["likes"][0]["user_id"] == u2.id
