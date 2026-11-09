import logging

from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.exceptions import register_exception_handlers
from app.core.middleware import CorrelationIdMiddleware


class ExamplePayload(BaseModel):
    quantity: int


def create_test_app() -> FastAPI:
    test_app = FastAPI()

    register_exception_handlers(test_app)
    test_app.add_middleware(CorrelationIdMiddleware)

    @test_app.get("/missing/{resource_id}")
    async def missing_resource(resource_id: str):
        raise HTTPException(
            status_code=404,
            detail=f"Internal resource detail: {resource_id}",
        )

    @test_app.post("/validate")
    async def validate_payload(payload: ExamplePayload):
        return payload

    @test_app.get("/crash")
    async def trigger_internal_error():
        raise RuntimeError("sensitive-database-password")

    @test_app.get("/records/{record_id}")
    async def get_record(record_id: str):
        return {"status": "ok"}

    return test_app


async def test_http_exception_does_not_expose_internal_detail() -> None:
    test_app = create_test_app()

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        response = await client.get("/missing/private-resource-id")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert "private-resource-id" not in response.text


async def test_validation_does_not_echo_rejected_input() -> None:
    test_app = create_test_app()

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/validate",
            json={"quantity": "sensitive-input-value"},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "sensitive-input-value" not in response.text
    assert response.json()["error"]["issues"]


async def test_internal_error_is_sanitized(
    caplog,
) -> None:
    test_app = create_test_app()
    caplog.set_level(logging.ERROR)

    async with AsyncClient(
        transport=ASGITransport(
            app=test_app,
            raise_app_exceptions=False,
        ),
        base_url="http://test",
    ) as client:
        response = await client.get("/crash")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "sensitive-database-password" not in response.text
    assert "sensitive-database-password" not in caplog.text

    error_record = next(
        record
        for record in caplog.records
        if getattr(record, "event", None) == "unhandled_exception"
    )

    assert error_record.exception_type == "RuntimeError"
    assert error_record.exc_info is None


async def test_request_log_uses_route_template(
    caplog,
) -> None:
    test_app = create_test_app()
    caplog.set_level(logging.INFO, logger="app.request")

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        response = await client.get("/records/private-taxpayer-id")

    assert response.status_code == 200
    assert "private-taxpayer-id" not in caplog.text

    request_record = next(
        record for record in caplog.records if getattr(record, "event", None) == "request_completed"
    )

    assert request_record.route == "/records/{record_id}"
    assert request_record.status_code == 200
    assert request_record.duration_ms >= 0
