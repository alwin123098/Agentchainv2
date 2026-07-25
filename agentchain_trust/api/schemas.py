"""Pydantic request/response schemas for API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ExecutionStepSchema(BaseModel):
    """Schema for execution step."""
    type: str
    name: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    duration_ms: float
    success: bool = True
    error_message: Optional[str] = None


class ExecutionProofRequest(BaseModel):
    """Request to submit execution proof."""
    agent_id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    steps: List[ExecutionStepSchema] = []
    model_used: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VerificationIssueSchema(BaseModel):
    """Verification issue schema."""
    severity: str
    code: str
    message: str
    step_id: Optional[str] = None


class VerificationResultResponse(BaseModel):
    """Verification result response."""
    verification_id: str
    task_id: str
    status: str
    trust_score: float
    hash_valid: bool
    replay_valid: Optional[bool] = None
    determinism_score: Optional[float] = None
    transparency_score: Optional[float] = None
    issues: List[VerificationIssueSchema] = []
    verified_at: datetime


class BatchVerifyRequest(BaseModel):
    """Request to batch verify multiple proofs."""
    proofs: List[ExecutionProofRequest]
    enable_replay: bool = True


class BatchVerifyResponse(BaseModel):
    """Response for batch verification."""
    batch_id: str
    total_proofs: int
    successful: int
    failed: int
    results: List[VerificationResultResponse]


class AgentMetricsResponse(BaseModel):
    """Agent metrics response."""
    agent_id: str
    total_verifications: int
    successful_verifications: int
    failed_verifications: int
    average_trust_score: float
    trust_trend_7d: Optional[float] = None
    trust_trend_30d: Optional[float] = None
    calculated_at: datetime


class APIKeyResponse(BaseModel):
    """API key response."""
    key_id: str
    name: str
    tier: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool