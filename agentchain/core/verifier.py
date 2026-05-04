from __future__ import annotations

from agentchain.core.hashing import verify_execution_hash
from agentchain.core.replay_engine import ReplayEngine
from agentchain.models.schemas import ExecutionProof, VerificationResult


class ProofVerifier:
    """Trust-layer gatekeeper. Invalid proofs are rejected here."""

    def __init__(self, replay_engine: ReplayEngine | None = None) -> None:
        self.replay_engine = replay_engine or ReplayEngine()

    def verify(self, proof: ExecutionProof) -> VerificationResult:
        issues: list[str] = []
        hash_valid = verify_execution_hash(proof)
        if not hash_valid:
            issues.append("execution hash mismatch")

        replay_valid, replay_issues = self.replay_engine.replay(proof)
        issues.extend(replay_issues)

        accepted = hash_valid and replay_valid
        trust_score = self._score(hash_valid=hash_valid, replay_valid=replay_valid)

        return VerificationResult(
            accepted=accepted,
            trust_score=trust_score,
            hash_valid=hash_valid,
            replay_valid=replay_valid,
            issues=issues,
        )

    @staticmethod
    def _score(*, hash_valid: bool, replay_valid: bool) -> float:
        score = 0.0
        if hash_valid:
            score += 40.0
        if replay_valid:
            score += 60.0
        return score
