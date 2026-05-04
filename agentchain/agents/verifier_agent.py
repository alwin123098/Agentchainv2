from __future__ import annotations

from agentchain.core.verifier import ProofVerifier
from agentchain.models.schemas import ExecutionProof, VerificationResult


class VerifierAgent:
    """Independent verifier agent for worker execution proofs."""

    def __init__(self, agent_id: str = "verifier-001", verifier: ProofVerifier | None = None) -> None:
        self.agent_id = agent_id
        self.verifier = verifier or ProofVerifier()

    def verify(self, proof: ExecutionProof) -> VerificationResult:
        return self.verifier.verify(proof)
