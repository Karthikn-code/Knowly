
import hashlib
import hmac
import secrets
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import Depends, HTTPException, Request, status

from app.core.config import settings


def validate_request_origin(request: Request) -> None:
    """Allow requests only from the configured frontend origin."""

    origin = request.headers.get("origin")

    if not origin or origin == "null":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is required or invalid.",
        )

    expected = urlsplit(settings.FRONTEND_URL)
    supplied = urlsplit(origin)

    if (
        not expected.scheme
        or not expected.hostname
        or not supplied.scheme
        or not supplied.hostname
        or supplied.username is not None
        or supplied.password is not None
        or supplied.path
        or supplied.query
        or supplied.fragment
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )

    try:
        expected_port = expected.port
        supplied_port = supplied.port
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )

    if (
        supplied.scheme.lower() != expected.scheme.lower()
        or supplied.hostname.lower() != expected.hostname.lower()
        or supplied_port != expected_port
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )


def _create_signature(session_token: str, nonce: str) -> str:
    """Create an HMAC-SHA256 signature bound to a session."""

    message = f"{session_token}.{nonce}".encode("utf-8")

    secret = settings.CSRF_SECRET_KEY.get_secret_value().encode("utf-8")

    return hmac.new(
        secret,
        message,
        hashlib.sha256,
    ).hexdigest()


def create_csrf_token(session_token: str) -> str:
    """Generate a cryptographically signed, session-bound CSRF token."""

    nonce = secrets.token_urlsafe(32)
    signature = _create_signature(session_token, nonce)

    return f"{nonce}.{signature}"


async def verify_csrf_token(request: Request) -> None:
    """Validate Origin, cookie/header equality and session-bound signature."""

    validate_request_origin(request)

    session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    cookie_token = request.cookies.get(settings.CSRF_COOKIE_NAME)
    header_token = request.headers.get("X-CSRF-Token")

    if not session_token or not cookie_token or not header_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed.",
        )

    if not secrets.compare_digest(cookie_token, header_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed.",
        )

    try:
        nonce, supplied_signature = cookie_token.rsplit(".", 1)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed.",
        )

    if not nonce or len(supplied_signature) != 64:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed.",
        )

    expected_signature = _create_signature(
        session_token,
        nonce,
    )

    if not secrets.compare_digest(
        supplied_signature,
        expected_signature,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed.",
        )


CSRFProtection = Annotated[
    None,
    Depends(verify_csrf_token),
]
