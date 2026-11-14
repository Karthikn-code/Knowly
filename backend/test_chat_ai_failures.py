
import asyncio
import selectors
from types import SimpleNamespace
from uuid import UUID

from fastapi import HTTPException, Request
from sqlalchemy import func, select

from app.api.v1.endpoints import chat
from app.db.session import AsyncSessionLocal, engine
from app.models.audit_log import AuditLog
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.message import MessageCreate
from app.services.embedding_service import GeminiEmbeddingError
from app.services.gemini_service import GeminiGenerationError


CONVERSATION_ID = UUID(
    "13c11d7f-35bc-473f-a28b-b3d6a657b7f0"
)


async def main():
    original_answer_question = chat.answer_question

    async with AsyncSessionLocal() as db:

        # Retrieve stable user ID without retaining an ORM User object.
        user_result = await db.execute(
            select(Conversation.user_id).where(
                Conversation.id == CONVERSATION_ID
            )
        )

        user_id = user_result.scalar_one_or_none()

        if user_id is None:
            raise RuntimeError("Test conversation not found.")

        # SimpleNamespace prevents ORM expiration after rollback.
        current_user = SimpleNamespace(id=user_id)

        request = Request({
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("localhost", 8000),
        })

        async def count_messages():
            result = await db.execute(
                select(func.count())
                .select_from(Message)
                .where(
                    Message.conversation_id == CONVERSATION_ID
                )
            )
            return result.scalar_one()

        async def count_success_audits():
            result = await db.execute(
                select(func.count())
                .select_from(AuditLog)
                .where(
                    AuditLog.event_type == "chat.answer.generated",
                    AuditLog.resource_id == str(CONVERSATION_ID),
                )
            )
            return result.scalar_one()

        scenarios = [
            GeminiEmbeddingError("Simulated embedding failure"),
            GeminiGenerationError("Simulated generation failure"),
        ]

        try:
            for error in scenarios:

                before_messages = await count_messages()
                before_audits = await count_success_audits()

                async def simulated_failure(**kwargs):
                    raise error

                chat.answer_question = simulated_failure

                try:
                    await chat.chat_with_documents(
                        conversation_id=CONVERSATION_ID,
                        payload=MessageCreate(
                            content="Test AI failure handling."
                        ),
                        request=request,
                        current_user=current_user,
                        _=None,
                        db=db,
                    )

                    raise AssertionError(
                        "Expected HTTPException was not raised."
                    )

                except HTTPException as exc:
                    assert exc.status_code == 503

                    print(
                        type(error).__name__,
                        "-> HTTP",
                        exc.status_code,
                    )

                after_messages = await count_messages()
                after_audits = await count_success_audits()

                assert after_messages == before_messages
                assert after_audits == before_audits

                print("Messages unchanged: PASSED")
                print("Success audit unchanged: PASSED")

            print("\nAI FAILURE HANDLING TEST: PASSED")

        finally:
            chat.answer_question = original_answer_question


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
