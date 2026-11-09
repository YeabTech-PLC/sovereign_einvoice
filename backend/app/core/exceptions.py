import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

SAFE_HTTP_ERRORS: dict[int, tuple[str, str]] = {
    400: ("bad_request", "The request could not be processed."),
    401: ("authentication_required", "Authentication is required."),
    403: ("access_denied", "Access to this resource is denied."),
    404: ("not_found", "The requested resource was not found."),
    405: ("method_not_allowed", "The request method is not allowed."),
    409: ("conflict", "The request conflicts with the current resource state."),
    413: ("payload_too_large", "The request payload is too large."),
    415: ("unsupported_media_type", "The request content type is not supported."),
    422: ("validation_error", "The request data is invalid."),
    429: ("rate_limit_exceeded", "Too many requests. Please try again later."),
    500: ("internal_error", "An unexpected error occurred."),
    502: ("upstream_error", "A dependent service could not complete the request."),
    503: ("service_unavailable", "The service is temporarily unavailable."),
    504: ("upstream_timeout", "A dependent service did not respond in time."),
}


def _correlation_id(request: Request) -> str:
    return getattr(request.state, "correlation_id", "unavailable")


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    request: Request,
    additional: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    error: dict[str, Any] = {
        "code": code,
        "message": message,
        "correlation_id": _correlation_id(request),
    }

    if additional:
        error.update(additional)

    return JSONResponse(
        status_code=status_code,
        content={"error": error},
        headers=headers,
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    code, message = SAFE_HTTP_ERRORS.get(
        exc.status_code,
        ("http_error", "The request could not be completed."),
    )

    # Deliberately do not expose exc.detail. It may contain internal
    # information or sensitive values supplied by application code.
    return _error_response(
        status_code=exc.status_code,
        code=code,
        message=message,
        request=request,
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    # Only expose field locations and validation error codes.
    # Never return rejected input, Pydantic messages or error context.
    issues = []

    for error in exc.errors()[:50]:
        location = error.get("loc", ())
        field = ".".join(str(part) for part in location)
        issue_code = str(error.get("type", "invalid"))

        issues.append(
            {
                "field": field,
                "code": issue_code,
            }
        )

    return _error_response(
        status_code=422,
        code="validation_error",
        message="The submitted data failed validation.",
        request=request,
        additional={"issues": issues},
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    route = request.scope.get("route")
    route_template = getattr(route, "path", "unmatched")

    # Do not log exception messages, request bodies, headers or tracebacks.
    logger.error(
        "unhandled_exception",
        extra={
            "event": "unhandled_exception",
            "correlation_id": _correlation_id(request),
            "method": request.method,
            "route": route_template,
            "exception_type": type(exc).__name__,
        },
    )

    return _error_response(
        status_code=500,
        code="internal_error",
        message="An unexpected error occurred. Contact support with the correlation ID.",
        request=request,
    )


def register_exception_handlers(application: FastAPI) -> None:
    """Register application-wide generic exception handlers."""
    application.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    application.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )
