import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi_users.authentication import JWTStrategy
from fastapi_users.models import UP


class TokenTypeJWTStrategy(JWTStrategy):
    """
    Extended JWTStrategy that adds token type claim to JWT payload.
    This ensures access tokens and refresh tokens are differentiated.
    """

    def __init__(self, secret: str, lifetime_seconds: int, token_type: str):
        super().__init__(secret=secret, lifetime_seconds=lifetime_seconds)
        self.token_type = token_type

    async def write_token(self, user: UP) -> str:
        """Write a token with token type claim included."""
        data = {
            "sub": str(user.id),
            "type": self.token_type,  # Add token type
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            + timedelta(seconds=self.lifetime_seconds),
        }
        return jwt.encode(data, self.secret, algorithm=self.algorithm)

    async def read_token(self, token: str, user_manager):
        """Decode token and return user object if valid."""
        try:
            data = jwt.decode(token, self.secret, algorithms=[self.algorithm])

            # Check token type
            if data.get("type") != self.token_type:
                return None

            user_id = data.get("sub")
            if not user_id:
                return None

            # Get user from database
            user = await user_manager.get(uuid.UUID(user_id))
            return user

        except jwt.ExpiredSignatureError:
            print("⚠️ Token expired")
            return None
        except jwt.InvalidTokenError:
            print("⚠️ Invalid token")
            return None
