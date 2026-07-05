import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, html: str) -> bool:
    """Generic Resend send helper. Returns True on a 2xx response, False on any
    failure (missing API key, non-2xx response, or exception) — never raises.
    """
    if not settings.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set — email not sent to %s", to)
        return False
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": "GC Move OS <onboarding@resend.dev>",
                    "to": [to],
                    "subject": subject,
                    "html": html,
                },
            )
            if resp.status_code >= 400:
                logger.error(
                    "Resend API error sending email to %s: %s %s",
                    to, resp.status_code, resp.text,
                )
                return False
            logger.info("Email sent to %s", to)
            return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, e)
        return False
