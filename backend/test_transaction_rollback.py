
import asyncio
import selectors

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.session import AsyncSessionLocal, engine
from app.models.message import Message


CONVERSATION_ID = "13c11d7f-35bc-473f-a28b-b3d6a657b7f0"
TEST_MARKER = "KNOWLY_TRANSACTION_ROLLBACK_TEST"


async def main():
    async with AsyncSessionLocal() as db:
        try:
            # First message is valid.
            user_message = Message(
                conversation_id=CONVERSATION_ID,
                role="user",
                content=TEST_MARKER,
            )

            # Deliberately invalid role violates the database constraint.
            invalid_message = Message(
                conversation_id=CONVERSATION_ID,
                role="invalid_role",
                content=TEST_MARKER,
            )

            db.add_all([user_message, invalid_message])

            await db.flush()

            raise AssertionError(
                "Expected database constraint failure did not occur."
            )

        except IntegrityError:
            print("Database constraint failure: EXPECTED")

            await db.rollback()

        # Verify that neither message was persisted.
        result = await db.execute(
            select(Message).where(
                Message.content == TEST_MARKER
            )
        )

        remaining_messages = result.scalars().all()

        print("Persisted test messages:", len(remaining_messages))

        assert len(remaining_messages) == 0, (
            "Rollback failed: test messages remain in the database."
        )

        print("TRANSACTION ROLLBACK TEST: PASSED")


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
