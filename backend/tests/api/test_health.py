from httpx import AsyncClient


async def test_health_reports_ok_and_the_commit_being_served(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "git_sha": "abc1234"}
