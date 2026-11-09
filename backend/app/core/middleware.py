import logging
from time import perf_counter
from uuid import UUID, uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.request")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Assign correlation IDs and log sanitized request metadata."""

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
        started_at = perf_counter()

        response = await call_next(request)

        duration_ms = round((perf_counter() - started_at) * 1000, 2)

        route = request.scope.get("route")
        route_template = getattr(route, "path", "unmatched")

        log_extra = {
            "event": "request_completed",
            "correlation_id": correlation_id,
            "method": request.method,
            "route": route_template,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }

        if response.status_code >= 500:
            logger.error("request_completed", extra=log_extra)
        elif response.status_code >= 400:
            logger.warning("request_completed", extra=log_extra)
        else:
            logger.info("request_completed", extra=log_extra)

        response.headers["X-Correlation-ID"] = correlation_id

        return response
