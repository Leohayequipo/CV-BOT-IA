from fastapi import FastAPI
from httpx import AsyncClient

from app.api.errors import UNEXPECTED_ERROR_MESSAGE


async def test_unknown_route_answers_with_the_error_shape(client: AsyncClient) -> None:
    response = await client.get("/no-such-route")

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": "Not Found"}}


async def test_wrong_method_keeps_the_allow_header(client: AsyncClient) -> None:
    response = await client.post("/health")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"
    assert response.headers["allow"] == "GET"


async def test_unexpected_error_hides_its_details(app: FastAPI, client: AsyncClient) -> None:
    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("internal detail that must not leak")

    response = await client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "message": UNEXPECTED_ERROR_MESSAGE}
    }
