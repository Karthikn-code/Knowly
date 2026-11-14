
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.conversations import router as conversations_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.messages import router as messages_router

from app.core.config import settings
from app.core.rate_limiter import limiter
from app.services.document_tasks import document_recovery_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application background services."""

    recovery_task = asyncio.create_task(
        document_recovery_loop(),
        name="knowly-document-recovery",
    )

    app.state.document_recovery_task = recovery_task

    try:
        yield
    finally:
        recovery_task.cancel()

        try:
            await recovery_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Knowly API",
    description="Backend API for Knowly - Your AI Document Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure rate limiting.
app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

# Configure OAuth state and nonce session storage.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.OAUTH_STATE_SECRET.get_secret_value(),
    session_cookie="knowly_oauth_state",
    max_age=600,
    same_site="lax",
    https_only=settings.APP_ENV == "production",
)

# Configure frontend access.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
    expose_headers=["Content-Disposition"],
)

# Register API routes.
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(conversations_router, prefix=settings.API_V1_PREFIX)
app.include_router(messages_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Knowly API",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Knowly Backend",
    }
