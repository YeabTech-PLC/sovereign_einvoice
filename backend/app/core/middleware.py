from uuid import UUID, uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Attach a validated correlation ID to each request."""

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        supplied_id = request.headers.get("X-Correlation-ID")

        try:
            correlation_id = str(UUID(supplied_id)) if supplied_id else str(uuid4())
        except (ValueError, TypeError, AttributeError):
            correlation_id = str(uuid4())

        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id

        return response
