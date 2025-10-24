import random
from datetime import timedelta
from email.message import EmailMessage

from aiosmtplib import SMTP
from redis.asyncio import ConnectionPool, Redis

from coffee_shop.settings import settings


class OTPService:
    """Handles OTP generation, verification, and email delivery."""

    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    async def generate_otp(
        self,
        key: str,
        ttl: int = int(timedelta(days=2).total_seconds()),
    ) -> str:
        """Generate and store OTP in Redis (via connection pool)."""
        otp = str(random.randint(100000, 999999))

        async with Redis(connection_pool=self.pool) as redis:
            added = await redis.setnx(key, otp)
            if not added:
                raise Exception(
                    "OTP already sent. Please wait before requesting again.",
                )
            await redis.expire(key, ttl)
        return otp

    async def verify_otp(self, key: str, code: str) -> bool:
        """Verify OTP from Redis and remove after successful match."""
        async with Redis(connection_pool=self.pool) as redis:
            stored = await redis.get(key)
            if stored and stored.decode() == code:
                await redis.delete(key)
                return True
        return False

    async def send_email(self, recipient: str, otp: str):
        """Send OTP code via SMTP."""
        msg = EmailMessage()
        msg["From"] = settings.smtp_from
        msg["To"] = recipient
        msg["Subject"] = "Your Coffee Shop verification code"
        msg.set_content(f"Your verification code is: {otp}")

        async with SMTP(
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            start_tls=settings.smtp_use_tls,
        ) as smtp:
            await smtp.login(settings.smtp_user, settings.smtp_password)
            await smtp.send_message(msg)
