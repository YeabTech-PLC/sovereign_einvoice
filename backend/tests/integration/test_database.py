from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_postgresql_readiness() -> None:
    """Verify an authenticated PostgreSQL query through the API."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "ok",
    }
