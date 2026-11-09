from uuid import UUID

from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_root_endpoint() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


async def test_liveness_endpoint() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


async def test_correlation_id_is_returned() -> None:
    supplied_id = "2e8ad132-6dd5-4a19-885b-c4dd1a62ae19"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/health/live",
            headers={"X-Correlation-ID": supplied_id},
        )

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == supplied_id


async def test_invalid_correlation_id_is_replaced() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/health/live",
            headers={"X-Correlation-ID": "not-a-valid-uuid"},
        )

    assert response.status_code == 200
    UUID(response.headers["X-Correlation-ID"])
