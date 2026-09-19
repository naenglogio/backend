from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from app.domains.users import service
from app.domains.users.schema import PasswordResetComplete


async def test_complete_password_reset_rejects_current_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_password = "current-password1"
    user = SimpleNamespace(password_hash=service.hash_password(current_password))
    session = AsyncMock()

    monkeypatch.setattr(
        service,
        "_get_verified_password_reset",
        AsyncMock(return_value=SimpleNamespace()),
    )
    monkeypatch.setattr(
        service,
        "_get_active_user_by_email",
        AsyncMock(return_value=user),
    )

    data = PasswordResetComplete(email="USER@example.com", new_password=current_password)

    with pytest.raises(service.SameAsOldPasswordError):
        await service.complete_password_reset(session, data)

    session.execute.assert_not_awaited()
    session.commit.assert_not_awaited()
