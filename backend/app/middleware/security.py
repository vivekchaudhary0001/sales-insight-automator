from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

# Blocked user-agent patterns (bots, scanners)
BLOCKED_AGENTS = {"sqlmap", "nikto", "nmap", "masscan", "zgrab", "python-requests/2.2"}


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Applies security hardening headers and blocks suspicious requests.
    Defends against:
      - Clickjacking (X-Frame-Options)
      - MIME sniffing (X-Content-Type-Options)
      - XSS (X-XSS-Protection, CSP)
      - Information leakage (Server header removal)
      - Known scanner/bot user-agents
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Block suspicious user-agents
        user_agent = request.headers.get("user-agent", "").lower()
        for blocked in BLOCKED_AGENTS:
            if blocked in user_agent:
                logger.warning(f"Blocked suspicious UA: {user_agent} from {request.client.host}")
                return Response(content="Forbidden", status_code=403)

        # Block suspiciously large Content-Length headers before reading body
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 15 * 1024 * 1024:
            return Response(content="Payload too large", status_code=413)

        response: Response = await call_next(request)

        # Security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; object-src 'none';"
        )
        # Remove server fingerprinting
        response.headers.pop("server", None)
        response.headers.pop("x-powered-by", None)

        return response
