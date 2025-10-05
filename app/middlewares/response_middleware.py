
import json
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException


class ResponsePatternMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip middleware for OpenAPI/Swagger/Redoc endpoints
        if request.url.path.startswith(
            ("/api/docs", "/api/redoc", "/api/openapi.json")
        ):
            return await call_next(request)

        try:
            response = await call_next(request)

            # For streaming responses, we need to read the body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Reset the body iterator
            response.body_iterator = iter([response_body])

            # Try JSON decode, fallback to text
            try:
                data = json.loads(response_body) if response_body else None
            except Exception:
                data = response_body.decode() if response_body else None

            # Decide success based on status_code
            is_success = 200 <= response.status_code < 400

            return JSONResponse(
                status_code=response.status_code,
                content={
                    "success": is_success,
                    "message": "Request successful." if is_success else "Request failed.",
                    "response": data if is_success else None,
                    "errors": None if is_success else data,
                }
            )


        except RequestValidationError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "message": "Validation error.",
                    "response": None,
                    "errors": exc.errors(),
                },
            )

        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "message": exc.detail,
                    "response": None,
                    "errors": {"type": "HTTPException", "detail": exc.detail},
                },
            )

        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected server error occurred.",
                    "response": None,
                    "errors": {"type": type(exc).__name__, "detail": str(exc)},
                },
            )
