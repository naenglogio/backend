"""Resend HTTP API를 통한 메일 발송 유틸리티.

RESEND_API_KEY가 설정되지 않은 환경(로컬 기본값)에서는 실제 발송 대신 로그로 남긴다.
운영 환경은 .env에 RESEND_API_KEY를 채워 실제 메일 발송을 활성화한다.
"""

import logging

import httpx

from app.core.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

_RESEND_API_URL = "https://api.resend.com/emails"


class EmailDeliveryError(AppError):
    code = "EMAIL_DELIVERY_FAILED"
    message = "이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요."
    status_code = 502


async def send_email(to_email: str, subject: str, body: str) -> None:
    api_key = settings.RESEND_API_KEY
    if not api_key:
        logger.info(
            "RESEND_API_KEY 미설정 — 메일 발송 대신 로그로 남김: to=%s subject=%s body=%s",
            to_email,
            subject,
            body,
        )
        return

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                _RESEND_API_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "from": settings.RESEND_FROM_EMAIL,
                    "to": [to_email],
                    "subject": subject,
                    "text": body,
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Resend 메일 발송 실패: to=%s error=%s", to_email, exc)
            raise EmailDeliveryError() from exc
