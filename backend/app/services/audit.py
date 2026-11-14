
from typing import Any
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


def get_client_ip(request: Request) -> str | None:
    """Get the direct client IP address."""

    if request.client is None:
        return None

    return request.client.host


def get_user_agent(request: Request) -> str | None:
    """Get the client user-agent safely."""

    user_agent = request.headers.get("user-agent")

    if not user_agent:
        return None

    return user_agent[:512]


async def record_audit_event(
    db: AsyncSession,
    *,
    event_type: str,
    outcome: str,
    request: Request | None = None,
    user_id: UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Add an authentication or security event to the audit log."""

    if not event_type or len(event_type) > 100:
        raise ValueError("Invalid audit event type.")

    if not outcome or len(outcome) > 30:
        raise ValueError("Invalid audit event outcome.")

    audit_entry = AuditLog(
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
        metadata_=metadata or {},
    )

    db.add(audit_entry)
