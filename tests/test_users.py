import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_profile_and_follow(client: AsyncClient, test_users):
    u1, u2 = test_users

    resp_me = await client.get("/api/users/me", headers={"api-key": u1.api_key})
    assert resp_me.status_code == 200
    assert resp_me.json()["user"]["name"] == "User 1"

    resp_follow = await client.post(
        f"/api/users/{u2.id}/follow", headers={"api-key": u1.api_key}
    )
    assert resp_follow.status_code == 200
    assert resp_follow.json()["result"] is True

    resp_me_updated = await client.get("/api/users/me", headers={"api-key": u1.api_key})
    assert len(resp_me_updated.json()["user"]["following"]) == 1
    assert resp_me_updated.json()["user"]["following"][0]["id"] == u2.id

    resp_unfollow = await client.delete(
        f"/api/users/{u2.id}/follow", headers={"api-key": u1.api_key}
    )
    assert resp_unfollow.status_code == 200
    assert resp_unfollow.json()["result"] is True
