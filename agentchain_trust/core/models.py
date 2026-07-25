"""Core data models for trust verification."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class StepType(str, Enum):
    """Types of execution steps."""
    TOOL_CALL = "tool_call"
    LLM_CALL = "llm_call"
    MEMORY_ACCESS = "memory_access"
    DECISION = "decision"


class ExecutionStep(BaseModel):
    """Single step in agent execution."""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: StepType
    name: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    timestamp: float
    duration_ms: float
    success: bool = True
    error_message: Optional[str] = None


class ExecutionProof(BaseModel):
    """Proof of agent execution with all steps."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    organization_id: str
    user_id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    steps: List[ExecutionStep] = []
    timestamp: float
    execution_duration_ms: float
    hash: str
    merkle_root: Optional[str] = None
    model_used: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "agent_id": "agent-001",
                "organization_id": "org-uuid",
                "user_id": "user-uuid",
                "input_data": {"query": "Summarize AI trends"},
                "output_data": {"summary": "AI trends in 2024..."},
                "steps": [],
                "timestamp": 1234567890.0,
                "execution_duration_ms": 1234.5,
                "hash": "sha256-hex",
                "model_used": "gpt-4"
            }
        }


class VerificationIssue(BaseModel):
    """Issue found during verification."""
    severity: str = Field(..., description="critical, warning, info")
    code: str
    message: str
    step_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    """Result of verification process."""
    verification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    status: str = Field(..., description="accepted, rejected, pending")
    trust_score: float = Field(ge=0, le=100)
    hash_valid: bool
    replay_valid: Optional[bool] = None
    determinism_score: Optional[float] = None
    transparency_score: Optional[float] = None
    issues: List[VerificationIssue] = []
    verified_at: datetime
    verified_by: str = "system"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TrustMetrics(BaseModel):
    """Trust metrics for an agent over time."""
    agent_id: str
    organization_id: str
    total_verifications: int = 0
    successful_verifications: int = 0
    failed_verifications: int = 0
    average_trust_score: float = 0.0
    last_verification_at: Optional[datetime] = None
    trust_trend_7d: Optional[float] = None
    trust_trend_30d: Optional[float] = None
    calculated_at: datetime