"""Async client for Trust Layer API."""

import asyncio
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin

try:
    import aiohttp
except ImportError:
    aiohttp = None

from .models import (
    ExecutionProof,
    VerificationResult,
    BatchVerificationResult,
    AgentMetrics,
    SystemStats,
)
from .exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    TrustLayerException,
)


class AsyncTrustLayerClient:
    """Async client for AgentChain Trust Layer API."""

    DEFAULT_BASE_URL = "http://localhost:8000"
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Initialize the async client.

        Args:
            api_key: API key for authentication
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        if aiohttp is None:
            raise ImportError(
                "aiohttp is required for async client. Install with: pip install aiohttp"
            )

        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout
        self.session = None

    async def _ensure_session(self):
        """Ensure session is initialized."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request."""
        await self._ensure_session()
        url = urljoin(self.base_url, endpoint)

        try:
            async with self.session.request(
                method,
                url,
                json=data,
            ) as response:
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status >= 500:
                    raise NetworkError(f"Server error: {response.status}")
                elif response.status >= 400:
                    raise TrustLayerException(
                        f"Request failed: {response.status}"
                    )

                return await response.json()
        except aiohttp.ClientError as e:
            raise NetworkError(f"Request failed: {str(e)}")

    async def verify_execution(
        self,
        proof: ExecutionProof,
        enable_replay: bool = True,
    ) -> VerificationResult:
        """Verify an execution proof (async)."""
        payload = proof.to_dict()
        response = await self._make_request(
            "POST",
            "/v1/verify-execution",
            data=payload,
        )
        return VerificationResult(response)

    async def batch_verify(
        self,
        proofs: List[ExecutionProof],
        enable_replay: bool = True,
    ) -> BatchVerificationResult:
        """Batch verify multiple proofs (async)."""
        payload = {
            "proofs": [proof.to_dict() for proof in proofs],
            "enable_replay": enable_replay,
        }
        response = await self._make_request(
            "POST",
            "/v1/batch-verify",
            data=payload,
        )
        return BatchVerificationResult(response)

    async def get_verification(self, task_id: str) -> VerificationResult:
        """Get verification result (async)."""
        response = await self._make_request(
            "GET",
            f"/v1/verification/{task_id}",
        )
        return VerificationResult(response)

    async def get_agent_metrics(self, agent_id: str) -> AgentMetrics:
        """Get agent metrics (async)."""
        response = await self._make_request(
            "GET",
            f"/v1/agent/{agent_id}/metrics",
        )
        return AgentMetrics(response)

    async def get_stats(self) -> SystemStats:
        """Get system statistics (async)."""
        response = await self._make_request("GET", "/v1/stats")
        return SystemStats(response)

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
