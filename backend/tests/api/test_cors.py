from uuid import uuid4

from httpx import AsyncClient

from app.config import Settings


def preflight(origin: str) -> dict[str, str]:
    return {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }


async def test_the_site_may_call_the_api(client: AsyncClient, settings: Settings) -> None:
    origin = settings.cors_origins[0]

    response = await client.options("/chat", headers=preflight(origin))

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


async def test_other_sites_may_not_call_the_api(client: AsyncClient) -> None:
    response = await client.options("/chat", headers=preflight("https://elsewhere.example"))

    assert "access-control-allow-origin" not in response.headers


async def test_the_site_can_read_when_to_ask_again(client: AsyncClient, settings: Settings) -> None:
    body = {"message": "mock: limit", "history": [], "locale": "en", "session_id": str(uuid4())}

    response = await client.post("/chat", json=body, headers={"Origin": settings.cors_origins[0]})

    assert response.status_code == 429
    assert "retry-after" in response.headers["access-control-expose-headers"].lower()
