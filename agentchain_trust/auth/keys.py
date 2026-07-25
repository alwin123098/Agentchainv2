"""API key management and validation."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
import uuid


class APIKeyManager:
    """Manage API keys."""

    KEY_PREFIX = "agentchain_"
    KEY_LENGTH = 32

    @staticmethod
    def generate_key() -> str:
        """Generate a new API key."""
        random_part = secrets.token_urlsafe(APIKeyManager.KEY_LENGTH)
        return f"{APIKeyManager.KEY_PREFIX}{random_part}"

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def extract_key_from_header(auth_header: str) -> Optional[str]:
        """Extract API key from Authorization header."""
        try:
            if auth_header.startswith("Bearer "):
                return auth_header[7:]
        except Exception:
            pass
        return None

    @staticmethod
    def create_key_record(
        organization_id: str,
        name: str,
        tier: str = "free",
        expires_in_days: Optional[int] = None,
    ) -> Tuple[str, str]:
        """Create a new API key record.

        Returns tuple of (key, key_id).
        """
        key = APIKeyManager.generate_key()
        key_id = str(uuid.uuid4())
        key_hash = APIKeyManager.hash_key(key)

        # Return raw key (only shown once) and hash for storage
        return key, key_id