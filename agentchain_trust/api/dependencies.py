"""API dependencies (authentication, database, etc)."""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from agentchain_trust.database.db import get_db
from agentchain_trust.auth.keys import APIKeyManager
from agentchain_trust.database.models import APIKey

security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthCredentials = Security(security),
    db: Session = Depends(get_db),
) -> str:
    """Verify API key and return organization ID."""
    key = credentials.credentials
    key_hash = APIKeyManager.hash_key(key)

    api_key = db.query(APIKey).filter_by(
        key_hash=key_hash,
        is_active=True,
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # Check if expired
    from datetime import datetime
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired",
        )

    return api_key.organization_id


async def get_current_user_id(
    organization_id: str = Depends(verify_api_key),
) -> str:
    """Get current organization ID from verified API key."""
    return organization_id