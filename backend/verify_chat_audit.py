
import asyncio
import selectors

from sqlalchemy import select

from app.db.session import AsyncSessionLocal, engine
from app.models.audit_log import AuditLog

CONVERSATION_ID = "13c11d7f-35bc-473f-a28b-b3d6a657b7f0"


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AuditLog)
            .where(
                AuditLog.event_type == "chat.answer.generated",
                AuditLog.resource_id == CONVERSATION_ID,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(5)
        )

        events = result.scalars().all()

        print("Matching audit events:", len(events))

        for event in events:
            print("\nEvent:", event.event_type)
            print("Outcome:", event.outcome)
            print("Resource type:", event.resource_type)
            print("Resource ID:", event.resource_id)
            print("Metadata:", event.metadata_)

        if events:
            print("\nAUDIT LOG VERIFICATION: PASSED")
        else:
            print("\nAUDIT LOG VERIFICATION: NO MATCHING EVENTS")


try:
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )
finally:
    asyncio.run(
        engine.dispose(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        ),
    )
