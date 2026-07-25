"""Main client for Trust Layer API."""

import requests
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin

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
from .retry import RetryStrategy


class TrustLayerClient:
    """Client for AgentChain Trust Layer API."""

    DEFAULT_BASE_URL = "http://localhost:8000"
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ):
        """Initialize the client.

        Args:
            api_key: API key for authentication
            base_url: Base URL of the API (default: http://localhost:8000)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout
        self.retry_strategy = RetryStrategy(max_retries=max_retries)

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "agentchain-trust-sdk/1.0.0",
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling."""
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.retry_strategy.execute(
                self.session.request,
                method,
                url,
                json=data,
                timeout=self.timeout,
                **kwargs,
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 500:
                raise NetworkError(f"Server error: {response.status_code}")
            elif response.status_code >= 400:
                raise TrustLayerException(
                    f"Request failed: {response.status_code} - {response.text}"
                )

            return response.json()
        except requests.RequestException as e:
            raise NetworkError(f"Request failed: {str(e)}")

    def verify_execution(
        self,
        proof: ExecutionProof,
        enable_replay: bool = True,
    ) -> VerificationResult:
        """Verify an execution proof.

        Args:
            proof: ExecutionProof object
            enable_replay: Enable determinism verification

        Returns:
            VerificationResult object
        """
        payload = proof.to_dict()

        response = self._make_request(
            "POST",
            "/v1/verify-execution",
            data=payload,
        )

        return VerificationResult(response)

    def batch_verify(
        self,
        proofs: List[ExecutionProof],
        enable_replay: bool = True,
    ) -> BatchVerificationResult:
        """Batch verify multiple proofs.

        Args:
            proofs: List of ExecutionProof objects
            enable_replay: Enable determinism verification

        Returns:
            BatchVerificationResult object
        """
        payload = {
            "proofs": [proof.to_dict() for proof in proofs],
            "enable_replay": enable_replay,
        }

        response = self._make_request(
            "POST",
            "/v1/batch-verify",
            data=payload,
        )

        return BatchVerificationResult(response)

    def get_verification(
        self,
        task_id: str,
    ) -> VerificationResult:
        """Get verification result by task ID.

        Args:
            task_id: Task ID from verification

        Returns:
            VerificationResult object
        """
        response = self._make_request(
            "GET",
            f"/v1/verification/{task_id}",
        )

        return VerificationResult(response)

    def get_agent_metrics(
        self,
        agent_id: str,
    ) -> AgentMetrics:
        """Get metrics for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            AgentMetrics object
        """
        response = self._make_request(
            "GET",
            f"/v1/agent/{agent_id}/metrics",
        )

        return AgentMetrics(response)

    def get_stats(self) -> SystemStats:
        """Get system statistics.

        Returns:
            SystemStats object
        """
        response = self._make_request(
            "GET",
            "/v1/stats",
        )

        return SystemStats(response)

    def health_check(self) -> bool:
        """Check API health.

        Returns:
            True if API is healthy
        """
        try:
            response = self.session.get(
                urljoin(self.base_url, "/health"),
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
