"""Verification service for processing proofs."""

from typing import Optional, Dict, Any, List, Callable
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from agentchain_trust.core.models import ExecutionProof, VerificationResult
from agentchain_trust.core.verifier import Verifier
from agentchain_trust.database.models import (
    ExecutionProofRecord,
    VerificationRecordDB,
    TrustMetricsRecord,
    AuditLogRecord,
)


class VerificationService:
    """Service for verification operations."""

    def __init__(self):
        self.verifier = Verifier()

    def verify_execution(
        self,
        proof: ExecutionProof,
        db: Session,
        enable_replay: bool = True,
        tool_implementations: Optional[Dict[str, Callable]] = None,
    ) -> VerificationResult:
        """Verify execution proof."""
        # Run verification
        result = self.verifier.verify_execution(
            proof,
            tool_implementations=tool_implementations,
            enable_replay=enable_replay,
        )

        # Store proof record
        proof_record = ExecutionProofRecord(
            id=str(uuid.uuid4()),
            task_id=proof.task_id,
            agent_id=proof.agent_id,
            organization_id=proof.organization_id,
            user_id=proof.user_id,
            input_data=proof.input_data,
            output_data=proof.output_data,
            hash=proof.hash,
            merkle_root=proof.merkle_root,
            model_used=proof.model_used,
            execution_duration_ms=proof.execution_duration_ms,
            steps_count=len(proof.steps),
            metadata=proof.metadata,
            stored_proof=proof.model_dump(),
        )
        db.add(proof_record)

        # Store verification record
        verification_record = VerificationRecordDB(
            id=str(uuid.uuid4()),
            verification_id=result.verification_id,
            task_id=proof.task_id,
            status=result.status,
            trust_score=result.trust_score,
            hash_valid=result.hash_valid,
            replay_valid=result.replay_valid,
            determinism_score=result.determinism_score,
            transparency_score=result.transparency_score,
            issues=[issue.model_dump() for issue in result.issues],
        )
        db.add(verification_record)

        # Update trust metrics
        self._update_metrics(proof, result, db)

        db.commit()

        return result

    def _update_metrics(
        self,
        proof: ExecutionProof,
        result: VerificationResult,
        db: Session,
    ) -> None:
        """Update trust metrics for agent."""
        metrics = db.query(TrustMetricsRecord).filter_by(
            agent_id=proof.agent_id,
            organization_id=proof.organization_id,
        ).first()

        if not metrics:
            metrics = TrustMetricsRecord(
                id=str(uuid.uuid4()),
                agent_id=proof.agent_id,
                organization_id=proof.organization_id,
            )
            db.add(metrics)

        metrics.total_verifications += 1
        if result.status == "accepted":
            metrics.successful_verifications += 1
        else:
            metrics.failed_verifications += 1

        # Update average trust score
        old_avg = metrics.average_trust_score
        total = metrics.total_verifications
        metrics.average_trust_score = (
            (old_avg * (total - 1) + result.trust_score) / total
        )
        metrics.updated_at = datetime.utcnow()

    def get_verification_result(
        self,
        task_id: str,
        db: Session,
    ) -> Optional[VerificationResult]:
        """Get verification result for a task."""
        record = db.query(VerificationRecordDB).filter_by(task_id=task_id).first()
        if not record:
            return None

        # Reconstruct VerificationResult from record
        # (simplified - in production would be more detailed)
        return VerificationResult(
            verification_id=record.verification_id,
            task_id=record.task_id,
            status=record.status,
            trust_score=record.trust_score,
            hash_valid=record.hash_valid,
            replay_valid=record.replay_valid,
            determinism_score=record.determinism_score,
            transparency_score=record.transparency_score,
            issues=[],
            verified_at=record.created_at,
        )

    def get_agent_metrics(
        self,
        agent_id: str,
        organization_id: str,
        db: Session,
    ) -> Optional[Dict[str, Any]]:
        """Get trust metrics for agent."""
        metrics = db.query(TrustMetricsRecord).filter_by(
            agent_id=agent_id,
            organization_id=organization_id,
        ).first()

        if not metrics:
            return None

        return {
            "agent_id": metrics.agent_id,
            "total_verifications": metrics.total_verifications,
            "successful_verifications": metrics.successful_verifications,
            "failed_verifications": metrics.failed_verifications,
            "average_trust_score": metrics.average_trust_score,
            "trust_trend_7d": metrics.trust_trend_7d,
            "trust_trend_30d": metrics.trust_trend_30d,
            "calculated_at": metrics.calculated_at,
        }