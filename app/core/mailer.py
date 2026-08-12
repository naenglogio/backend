"""SMTP 발송 유틸리티.

SMTP_HOST가 설정되지 않은 환경(로컬 기본값)에서는 실제 발송 대신 로그로 남긴다.
운영 환경은 .env에 SMTP_* 값을 채워 실제 메일 발송을 활성화한다.
큐/Worker 없이 요청 처리 중 동기 SMTP 호출을 스레드로 넘겨서만 처리한다(MVP 범위).
"""

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_sync(smtp_host: str, to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message.set_content(body)

    with smtplib.SMTP(smtp_host, settings.SMTP_PORT) as smtp:
        if settings.SMTP_USE_TLS:
            smtp.starttls()
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(message)


async def send_email(to_email: str, subject: str, body: str) -> None:
    smtp_host = settings.SMTP_HOST
    if not smtp_host:
        logger.info(
            "SMTP_HOST 미설정 — 메일 발송 대신 로그로 남김: to=%s subject=%s body=%s",
            to_email,
            subject,
            body,
        )
        return
    await asyncio.to_thread(_send_sync, smtp_host, to_email, subject, body)
