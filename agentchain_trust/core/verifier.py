"""Main verification engine combining all trust components."""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import uuid
from .models import (
    ExecutionProof,
    VerificationResult,
    VerificationIssue,
    TrustMetrics,
)
from .proof_engine import ProofEngine
from .replay_engine import ReplayEngine


class Verifier:
    """Main trust verification engine."""

    def __init__(self):
        self.proof_engine = ProofEngine()
        self.replay_engine = ReplayEngine()

    def verify_execution(
        self,
        proof: ExecutionProof,
        tool_implementations: Optional[Dict[str, Callable]] = None,
        enable_replay: bool = True,
    ) -> VerificationResult:
        """Verify execution proof and generate trust score."""
        issues: List[VerificationIssue] = []

        # 1. Check proof integrity
        hash_valid = self.proof_engine.verify_proof_integrity(proof)
        if not hash_valid:
            issues.append(
                VerificationIssue(
                    severity="critical",
                    code="HASH_MISMATCH",
                    message="Proof hash verification failed - execution may have been tampered with",
                )
            )

        # 2. Replay execution for determinism
        replay_valid = True
        determinism_score = 0.0
        if enable_replay and proof.steps:
            replay_valid, replay_issues = self.replay_engine.replay_execution(
                proof, tool_implementations
            )
            issues.extend(replay_issues)
            determinism_score = self._calculate_determinism_score(replay_issues)

        # 3. Calculate transparency score
        transparency_score = self._calculate_transparency_score(proof)

        # 4. Calculate overall trust score
        trust_score = self._calculate_trust_score(
            hash_valid=hash_valid,
            replay_valid=replay_valid,
            determinism_score=determinism_score,
            transparency_score=transparency_score,
            issues=issues,
        )

        # 5. Determine overall status
        status = "accepted" if trust_score >= 70 else "rejected" if trust_score < 30 else "pending"

        return VerificationResult(
            verification_id=str(uuid.uuid4()),
            task_id=proof.task_id,
            status=status,
            trust_score=trust_score,
            hash_valid=hash_valid,
            replay_valid=replay_valid,
            determinism_score=determinism_score,
            transparency_score=transparency_score,
            issues=issues,
            verified_at=datetime.utcnow(),
        )

    def _calculate_determinism_score(self, issues: List[VerificationIssue]) -> float:
        """Calculate determinism score from replay issues."""
        if not issues:
            return 100.0

        # Count non-deterministic issues
        critical_issues = [i for i in issues if i.severity == "critical"]
        warning_issues = [i for i in issues if i.severity == "warning"]

        score = 100.0
        score -= len(critical_issues) * 25
        score -= len(warning_issues) * 10

        return max(0.0, score)

    def _calculate_transparency_score(self, proof: ExecutionProof) -> float:
        """Calculate transparency score based on steps and metadata."""
        if not proof.steps:
            return 0.0

        # Score based on:
        # - Number of steps documented (max 40 points)
        # - All steps succeeded (max 30 points)
        # - Metadata richness (max 30 points)

        step_score = min(40.0, len(proof.steps) * 2)

        success_count = sum(1 for step in proof.steps if step.success)
        success_score = (success_count / len(proof.steps)) * 30 if proof.steps else 0

        metadata_score = min(30.0, len(proof.metadata) * 5)

        return step_score + success_score + metadata_score

    def _calculate_trust_score(
        self,
        hash_valid: bool,
        replay_valid: bool,
        determinism_score: float,
        transparency_score: float,
        issues: List[VerificationIssue],
    ) -> float:
        """Calculate overall trust score (0-100)."""
        score = 0.0

        # Hash validity: 40 points
        if hash_valid:
            score += 40
        else:
            score -= 40

        # Replay validity: 20 points
        if replay_valid:
            score += 20
        else:
            score -= 20

        # Determinism score: 20 points (proportional)
        score += (determinism_score / 100) * 20

        # Transparency score: 20 points (proportional)
        score += (transparency_score / 100) * 20

        # Penalize critical issues
        critical_count = sum(1 for i in issues if i.severity == "critical")
        score -= critical_count * 15

        return max(0.0, min(100.0, score))