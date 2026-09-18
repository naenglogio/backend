"""비밀번호를 받는 모든 엔드포인트가 공유하는 입력 정책."""

from typing import Annotated

from pydantic import AfterValidator, Field


def validate_password_complexity(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("비밀번호는 UTF-8 기준 72바이트 이하여야 합니다.")
    if not any(character.isdigit() for character in password):
        raise ValueError("비밀번호에는 숫자가 하나 이상 포함되어야 합니다.")
    if not any(not character.isalnum() for character in password):
        raise ValueError("비밀번호에는 특수문자가 하나 이상 포함되어야 합니다.")
    return password


Password = Annotated[
    str,
    Field(min_length=8, max_length=72),
    AfterValidator(validate_password_complexity),
]
