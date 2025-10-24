import random
from datetime import timedelta

from redis.asyncio import Redis


def generate_otp() -> str:
    """Generate 6-digit OTP code."""
    return str(random.randint(100000, 999999))


async def save_otp(redis: Redis, email: str, otp: str, ttl_minutes: int = 10):
    """Save OTP to Redis with TTL."""
    await redis.setex(f"otp:{email}", timedelta(minutes=ttl_minutes), otp)


async def get_otp(redis: Redis, email: str) -> str | None:
    """Get OTP by email from Redis."""
    return await redis.get(f"otp:{email}")


async def delete_otp(redis: Redis, email: str):
    """Delete OTP after successful verification."""
    await redis.delete(f"otp:{email}")
