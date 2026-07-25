"""Run the Trust Layer API."""

import uvicorn
from agentchain_trust.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "agentchain_trust.api.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if settings.api_env == "production" else 1,
        reload=settings.debug,
    )