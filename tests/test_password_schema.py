import pytest
from app.domains.profile.schema import PasswordUpdate
from app.domains.users.schema import PasswordResetComplete, UserCreate
from pydantic import ValidationError


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (UserCreate, {"email": "user@example.com", "password": "password!", "nickname": "user"}),
        (
            PasswordResetComplete,
            {"email": "user@example.com", "new_password": "password!"},
        ),
        (
            PasswordUpdate,
            {"current_password": "current", "new_password": "password!"},
        ),
    ],
)
def test_password_requires_digit(model: type, payload: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        model(**payload)


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (UserCreate, {"email": "user@example.com", "password": "password1", "nickname": "user"}),
        (
            PasswordResetComplete,
            {"email": "user@example.com", "new_password": "password1"},
        ),
        (
            PasswordUpdate,
            {"current_password": "current", "new_password": "password1"},
        ),
    ],
)
def test_password_requires_special_character(model: type, payload: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        model(**payload)


def test_password_accepts_shared_policy() -> None:
    password = "password1!"
    created_user = UserCreate(email="user@example.com", password=password, nickname="user")
    completed_reset = PasswordResetComplete(email="user@example.com", new_password=password)
    password_update = PasswordUpdate(current_password="current", new_password=password)

    assert created_user.password == password
    assert completed_reset.new_password == password
    assert password_update.new_password == password


def test_password_rejects_more_than_72_utf8_bytes() -> None:
    with pytest.raises(ValidationError):
        PasswordUpdate(current_password="current", new_password="가" * 24 + "1!")
