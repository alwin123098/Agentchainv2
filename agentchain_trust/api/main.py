"""Main FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from agentchain_trust.config import get_settings
from agentchain_trust.database.db import get_db, init_db
from agentchain_trust.api.dependencies import verify_api_key, get_current_user_id
from agentchain_trust.api.schemas import (
    ExecutionProofRequest,
    VerificationResultResponse,
    BatchVerifyRequest,
    BatchVerifyResponse,
    AgentMetricsResponse,
)
from agentchain_trust.core.models import ExecutionProof, ExecutionStep, StepType
from agentchain_trust.services.verification_service import VerificationService
from agentchain_trust.database.models import AuditLogRecord

settings = get_settings()

app = FastAPI(
    title="AgentChain Trust Layer API v2",
    description="Production-grade trust verification system for AI agents",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
verification_service = VerificationService()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/v1/verify-execution", response_model=VerificationResultResponse)
async def verify_execution(
    request: ExecutionProofRequest,
    organization_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    req: Request = None,
):
    """Verify an execution proof.
    
    **Request Body:**
    - `agent_id`: Unique identifier for the agent
    - `input_data`: Input parameters for the execution
    - `output_data`: Output/result of the execution
    - `steps`: List of execution steps with details
    - `model_used`: LLM model name (optional)
    - `metadata`: Additional metadata (optional)
    
    **Response:**
    - `verification_id`: Unique verification ID
    - `task_id`: Unique task ID
    - `status`: accepted/rejected/pending
    - `trust_score`: 0-100 score
    - Detailed verification information
    """
    try:
        # Create ExecutionProof from request
        steps = [
            ExecutionStep(
                type=StepType(step.type),
                name=step.name,
                input_data=step.input_data,
                output_data=step.output_data,
                timestamp=datetime.utcnow().timestamp(),
                duration_ms=step.duration_ms,
                success=step.success,
                error_message=step.error_message,
            )
            for step in request.steps
        ]

        proof = ExecutionProof(
            agent_id=request.agent_id,
            organization_id=organization_id,
            user_id="api-user",
            input_data=request.input_data,
            output_data=request.output_data,
            timestamp=datetime.utcnow().timestamp(),
            execution_duration_ms=sum(s.duration_ms for s in steps),
            hash="",
            steps=steps,
            model_used=request.model_used,
            metadata=request.metadata,
        )

        # Finalize proof (compute hashes)
        from agentchain_trust.core.proof_engine import ProofEngine
        proof_engine = ProofEngine()
        proof = proof_engine.finalize_proof(proof)

        # Verify
        result = verification_service.verify_execution(
            proof,
            db,
            enable_replay=settings.replay_enabled,
        )

        # Log to audit trail
        _log_audit(
            db,
            organization_id,
            "verify_execution",
            "execution_proof",
            proof.task_id,
            "success",
            req,
        )

        return VerificationResultResponse(
            verification_id=result.verification_id,
            task_id=result.task_id,
            status=result.status,
            trust_score=result.trust_score,
            hash_valid=result.hash_valid,
            replay_valid=result.replay_valid,
            determinism_score=result.determinism_score,
            transparency_score=result.transparency_score,
            issues=[
                {
                    "severity": issue.severity,
                    "code": issue.code,
                    "message": issue.message,
                    "step_id": issue.step_id,
                }
                for issue in result.issues
            ],
            verified_at=result.verified_at,
        )

    except Exception as e:
        _log_audit(
            db,
            organization_id,
            "verify_execution",
            "execution_proof",
            None,
            "failed",
            req,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.get("/v1/verification/{task_id}", response_model=VerificationResultResponse)
async def get_verification(
    task_id: str,
    organization_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Retrieve verification result for a specific task."""
    result = verification_service.get_verification_result(task_id, db)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification result not found",
        )

    return VerificationResultResponse(
        verification_id=result.verification_id,
        task_id=result.task_id,
        status=result.status,
        trust_score=result.trust_score,
        hash_valid=result.hash_valid,
        replay_valid=result.replay_valid,
        determinism_score=result.determinism_score,
        transparency_score=result.transparency_score,
        issues=[],
        verified_at=result.verified_at,
    )


@app.post("/v1/batch-verify", response_model=BatchVerifyResponse)
async def batch_verify(
    request: BatchVerifyRequest,
    organization_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Batch verify multiple execution proofs in one request.
    
    **Request Body:**
    - `proofs`: List of ExecutionProofRequest objects
    - `enable_replay`: Enable determinism verification (default: true)
    
    **Response:**
    - `batch_id`: Unique batch verification ID
    - `total_proofs`: Total proofs submitted
    - `successful`: Number successfully verified
    - `failed`: Number failed
    - `results`: List of verification results
    """
    batch_id = str(uuid.uuid4())
    results = []
    successful = 0
    failed = 0

    for proof_request in request.proofs:
        try:
            steps = [
                ExecutionStep(
                    type=StepType(step.type),
                    name=step.name,
                    input_data=step.input_data,
                    output_data=step.output_data,
                    timestamp=datetime.utcnow().timestamp(),
                    duration_ms=step.duration_ms,
                    success=step.success,
                    error_message=step.error_message,
                )
                for step in proof_request.steps
            ]

            proof = ExecutionProof(
                agent_id=proof_request.agent_id,
                organization_id=organization_id,
                user_id="api-user",
                input_data=proof_request.input_data,
                output_data=proof_request.output_data,
                timestamp=datetime.utcnow().timestamp(),
                execution_duration_ms=sum(s.duration_ms for s in steps),
                hash="",
                steps=steps,
                model_used=proof_request.model_used,
                metadata=proof_request.metadata,
            )

            from agentchain_trust.core.proof_engine import ProofEngine
            proof_engine = ProofEngine()
            proof = proof_engine.finalize_proof(proof)

            result = verification_service.verify_execution(
                proof,
                db,
                enable_replay=request.enable_replay,
            )

            results.append(
                VerificationResultResponse(
                    verification_id=result.verification_id,
                    task_id=result.task_id,
                    status=result.status,
                    trust_score=result.trust_score,
                    hash_valid=result.hash_valid,
                    replay_valid=result.replay_valid,
                    determinism_score=result.determinism_score,
                    transparency_score=result.transparency_score,
                    issues=[],
                    verified_at=result.verified_at,
                )
            )
            successful += 1
        except Exception as e:
            failed += 1

    return BatchVerifyResponse(
        batch_id=batch_id,
        total_proofs=len(request.proofs),
        successful=successful,
        failed=failed,
        results=results,
    )


@app.get("/v1/agent/{agent_id}/metrics", response_model=AgentMetricsResponse)
async def get_agent_metrics(
    agent_id: str,
    organization_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get trust metrics for a specific agent.
    
    **Response includes:**
    - Total verifications performed
    - Success/failure counts
    - Average trust score
    - 7-day and 30-day trust trends
    """
    metrics = verification_service.get_agent_metrics(agent_id, organization_id, db)

    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent metrics not found",
        )

    return AgentMetricsResponse(**metrics)


@app.get("/v1/stats")
async def get_system_stats(
    organization_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get system-wide statistics for organization."""
    from agentchain_trust.database.models import (
        ExecutionProofRecord,
        VerificationRecordDB,
    )
    
    total_proofs = db.query(ExecutionProofRecord).filter_by(
        organization_id=organization_id
    ).count()
    
    verifications = db.query(VerificationRecordDB).join(
        ExecutionProofRecord,
        ExecutionProofRecord.task_id == VerificationRecordDB.task_id
    ).filter(ExecutionProofRecord.organization_id == organization_id).all()
    
    accepted_count = sum(1 for v in verifications if v.status == "accepted")
    rejected_count = sum(1 for v in verifications if v.status == "rejected")
    avg_trust_score = sum(v.trust_score for v in verifications) / len(verifications) if verifications else 0
    
    return {
        "organization_id": organization_id,
        "total_proofs": total_proofs,
        "total_verifications": len(verifications),
        "accepted_verifications": accepted_count,
        "rejected_verifications": rejected_count,
        "average_trust_score": avg_trust_score,
        "timestamp": datetime.utcnow().isoformat(),
    }


def _log_audit(
    db: Session,
    organization_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    status: str,
    request: Request,
):
    """Log audit trail."""
    if not settings.audit_log_enabled:
        return

    try:
        audit_log = AuditLogRecord(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Failed to log audit: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
    )