import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# In-memory sliding window rate limiter
# For production: replace with Redis-backed solution
RATE_LIMIT = 10       # requests
WINDOW_SECONDS = 60   # per minute


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-IP sliding window rate limiter.
    Allows RATE_LIMIT requests per WINDOW_SECONDS.
    
    Production note: Use Redis (e.g., slowapi + redis) for distributed deployments.
    """

    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health/docs endpoints
        if request.url.path in {"/", "/health", "/docs", "/openapi.json", "/redoc"}:
            return await call_next(request)

        ip = self._get_ip(request)
        now = time.time()
        window_start = now - WINDOW_SECONDS

        # Prune old entries
        self._requests[ip] = [t for t in self._requests[ip] if t > window_start]

        if len(self._requests[ip]) >= RATE_LIMIT:
            retry_after = int(self._requests[ip][0] + WINDOW_SECONDS - now) + 1
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        self._requests[ip].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(RATE_LIMIT - len(self._requests[ip]))
        response.headers["X-RateLimit-Window"] = str(WINDOW_SECONDS)
        return response

    def _get_ip(self, request: Request) -> str:
        # Respect X-Forwarded-For for reverse proxy deployments
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
