from unittest.mock import patch

import pytest

from app.db.session import get_db


class FakeAsyncSession:
    def __init__(self):
        self.rollback_called = False
        self.closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.closed = True

    async def rollback(self):
        self.rollback_called = True


@pytest.mark.asyncio
async def test_get_db_rolls_back_when_request_fails():
    fake_session = FakeAsyncSession()

    with patch(
        "app.db.session.AsyncSessionLocal",
        return_value=fake_session,
    ):
        db_generator = get_db()

        session = await anext(db_generator)

        assert session is fake_session

        with pytest.raises(RuntimeError, match="Database commit failed"):
            await db_generator.athrow(
                RuntimeError("Database commit failed")
            )

    assert fake_session.rollback_called is True
    assert fake_session.closed is True


@pytest.mark.asyncio
async def test_get_db_does_not_rollback_on_normal_completion():
    fake_session = FakeAsyncSession()

    with patch(
        "app.db.session.AsyncSessionLocal",
        return_value=fake_session,
    ):
        db_generator = get_db()

        session = await anext(db_generator)

        assert session is fake_session

        with pytest.raises(StopAsyncIteration):
            await anext(db_generator)

    assert fake_session.rollback_called is False
    assert fake_session.closed is True
