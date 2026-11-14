
import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.rate_limiter import limiter
from app.core.dependencies import get_current_user
from app.core.security import CSRFProtection, create_csrf_token
from app.db.session import get_db
from app.models.session import Session as UserSession
from app.models.user import User
from app.services.audit import record_audit_event
from app.services.google_oauth import oauth


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/google/login")
@limiter.limit("10/minute")
async def google_login(request: Request):
    """Redirect the user to Google's sign-in page."""

    redirect_uri = request.url_for("google_callback")

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
    )


@router.get("/google/callback", name="google_callback")
@limiter.limit("10/minute")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verify Google's identity response and create a Knowly session."""

    try:
        token = await oauth.google.authorize_access_token(request)

    except OAuthError:
        request.session.clear()

        logger.exception("Google OAuth verification failed.")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authentication could not be verified.",
        )

    except Exception:
        request.session.clear()

        logger.exception("Google OAuth token exchange or verification failed.")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to verify your Google authentication.",
        )

    userinfo = token.get("userinfo")

    if not userinfo:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not return verified identity information.",
        )

    # Validate Google's verified identity claims.
    google_sub = userinfo.get("sub")
    email = userinfo.get("email")
    email_verified = userinfo.get("email_verified")
    issuer = userinfo.get("iss")
    audience = userinfo.get("aud")

    audience_valid = (
        audience == settings.GOOGLE_CLIENT_ID
        if isinstance(audience, str)
        else isinstance(audience, (list, tuple))
        and settings.GOOGLE_CLIENT_ID in audience
    )

    if (
        not isinstance(google_sub, str)
        or not google_sub
        or not isinstance(email, str)
        or not email
        or email_verified is not True
        or issuer not in (
            "https://accounts.google.com",
            "accounts.google.com",
        )
        or not audience_valid
    ):
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account verification failed.",
        )

    request.session.clear()

    try:
        # Identify returning users using Google's stable subject.
        result = await db.execute(
            select(User).where(User.google_sub == google_sub)
        )

        user = result.scalar_one_or_none()
        newly_registered = False

        # Create a new account safely using a savepoint.
        if user is None:
            new_user = User(
                google_sub=google_sub,
                email=email,
                full_name=userinfo.get("name"),
                profile_picture=userinfo.get("picture"),
                is_active=True,
            )

            try:
                async with db.begin_nested():
                    db.add(new_user)
                    await db.flush()

                user = new_user
                newly_registered = True

            except IntegrityError:
                # Another request may have registered this Google identity.
                result = await db.execute(
                    select(User).where(User.google_sub == google_sub)
                )

                user = result.scalar_one_or_none()

                if user is None:
                    raise

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This Knowly account is inactive.",
            )

        # Refresh the profile using verified Google claims.
        user.email = email
        user.full_name = userinfo.get("name")
        user.profile_picture = userinfo.get("picture")

        # Generate a cryptographically random session token.
        raw_session_token = secrets.token_urlsafe(32)

        token_hash = hashlib.sha256(
            raw_session_token.encode("utf-8")
        ).hexdigest()

        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.SESSION_TTL_SECONDS
        )

        db.add(
            UserSession(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
        )

        # Record account registration and login in the same transaction.
        if newly_registered:
            await record_audit_event(
                db,
                event_type="user_registered",
                outcome="success",
                request=request,
                user_id=user.id,
                resource_type="user",
                resource_id=str(user.id),
            )

        await record_audit_event(
            db,
            event_type="google_login_success",
            outcome="success",
            request=request,
            user_id=user.id,
            resource_type="session",
            metadata={
                "authentication_provider": "google",
            },
        )

        # Commit user/profile/session/audit changes together.
        await db.commit()

    except HTTPException:
        await db.rollback()
        raise

    except Exception:
        logger.exception(
            "Google callback failed during user/session processing."
        )

        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete your Knowly authentication.",
        )

    # Generate a session-bound CSRF token.
    csrf_token = create_csrf_token(raw_session_token)

    response = RedirectResponse(
        url=f"{settings.FRONTEND_URL.rstrip('/')}/dashboard",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Referrer-Policy"] = "no-referrer"

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=raw_session_token,
        max_age=settings.SESSION_TTL_SECONDS,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        path="/",
    )

    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=settings.SESSION_TTL_SECONDS,
        httponly=False,
        secure=True,
        samesite="lax",
        path="/",
    )

    return response


@router.get("/me")
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Return the currently authenticated Knowly user."""

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "profile_picture": current_user.profile_picture,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    _: CSRFProtection,
    db: AsyncSession = Depends(get_db),
):
    """Revoke the current session and clear authentication cookies."""

    raw_token = request.cookies.get(settings.SESSION_COOKIE_NAME)

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    result = await db.execute(
        select(UserSession).where(
            UserSession.token_hash == token_hash,
            UserSession.user_id == current_user.id,
            UserSession.revoked_at.is_(None),
        )
    )

    user_session = result.scalar_one_or_none()

    if user_session is not None:
        user_session.revoked_at = datetime.now(timezone.utc)

        await record_audit_event(
            db,
            event_type="logout_success",
            outcome="success",
            request=request,
            user_id=current_user.id,
            resource_type="session",
        )

        try:
            await db.commit()

        except Exception:
            await db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to complete logout.",
            )

    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
    )

    response.delete_cookie(
        key=settings.CSRF_COOKIE_NAME,
        path="/",
        secure=True,
        samesite="lax",
    )

    response.headers["Cache-Control"] = "no-store"

    return {
        "message": "Successfully logged out.",
    }
