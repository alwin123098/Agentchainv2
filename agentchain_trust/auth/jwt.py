"""JWT token management."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from agentchain_trust.config import get_settings

settings = get_settings()


class TokenManager:
    """Manage JWT tokens."""

    @staticmethod
    def create_token(
        data: Dict[str, Any],
        expires_in_hours: Optional[int] = None,
    ) -> str:
        """Create a JWT token."""
        if expires_in_hours is None:
            expires_in_hours = settings.jwt_expiration_hours

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=expires_in_hours)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            return payload
        except JWTError:
            return None