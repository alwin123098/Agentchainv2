"""Data models for SDK."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import uuid
import time


class StepType(str, Enum):
    """Execution step types."""
    TOOL_CALL = "tool_call"
    LLM_CALL = "llm_call"
    MEMORY_ACCESS = "memory_access"
    DECISION = "decision"


class ExecutionStep:
    """Represents a single execution step."""

    def __init__(
        self,
        type: StepType,
        name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        duration_ms: float,
        success: bool = True,
        error_message: Optional[str] = None,
    ):
        self.step_id = str(uuid.uuid4())
        self.type = type
        self.name = name
        self.input_data = input_data
        self.output_data = output_data
        self.duration_ms = duration_ms
        self.success = success
        self.error_message = error_message
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "name": self.name,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_message": self.error_message,
        }


class ExecutionProof:
    """Represents an execution proof."""

    def __init__(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        model_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.task_id = str(uuid.uuid4())
        self.agent_id = agent_id
        self.input_data = input_data
        self.output_data = output_data
        self.model_used = model_used
        self.metadata = metadata or {}
        self.steps: List[ExecutionStep] = []
        self.timestamp = time.time()

    def add_step(
        self,
        step_type: StepType,
        name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        duration_ms: float,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> ExecutionStep:
        """Add a step to the proof."""
        step = ExecutionStep(
            type=step_type,
            name=name,
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
        )
        self.steps.append(step)
        return step

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API."""
        return {
            "agent_id": self.agent_id,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "steps": [step.to_dict() for step in self.steps],
            "model_used": self.model_used,
            "metadata": self.metadata,
        }


class VerificationIssue:
    """Represents a verification issue."""

    def __init__(
        self,
        severity: str,
        code: str,
        message: str,
        step_id: Optional[str] = None,
    ):
        self.severity = severity
        self.code = code
        self.message = message
        self.step_id = step_id

    def __repr__(self) -> str:
        return f"Issue({self.severity}: {self.code} - {self.message})"


class VerificationResult:
    """Represents a verification result."""

    def __init__(self, data: Dict[str, Any]):
        self.verification_id = data.get("verification_id")
        self.task_id = data.get("task_id")
        self.status = data.get("status")
        self.trust_score = data.get("trust_score")
        self.hash_valid = data.get("hash_valid")
        self.replay_valid = data.get("replay_valid")
        self.determinism_score = data.get("determinism_score")
        self.transparency_score = data.get("transparency_score")
        self.verified_at = data.get("verified_at")
        self.issues = [
            VerificationIssue(**issue) for issue in data.get("issues", [])
        ]

    @property
    def is_accepted(self) -> bool:
        """Check if verification was accepted."""
        return self.status == "accepted"

    @property
    def is_rejected(self) -> bool:
        """Check if verification was rejected."""
        return self.status == "rejected"

    def __repr__(self) -> str:
        return f"VerificationResult(status={self.status}, score={self.trust_score})"


class BatchVerificationResult:
    """Represents batch verification results."""

    def __init__(self, data: Dict[str, Any]):
        self.batch_id = data.get("batch_id")
        self.total_proofs = data.get("total_proofs")
        self.successful = data.get("successful")
        self.failed = data.get("failed")
        self.results = [
            VerificationResult(result) for result in data.get("results", [])
        ]

    @property
    def success_rate(self) -> float:
        """Get success rate percentage."""
        if self.total_proofs == 0:
            return 0.0
        return (self.successful / self.total_proofs) * 100

    def __repr__(self) -> str:
        return f"BatchVerificationResult({self.successful}/{self.total_proofs} successful)"


class AgentMetrics:
    """Represents agent metrics."""

    def __init__(self, data: Dict[str, Any]):
        self.agent_id = data.get("agent_id")
        self.total_verifications = data.get("total_verifications")
        self.successful_verifications = data.get("successful_verifications")
        self.failed_verifications = data.get("failed_verifications")
        self.average_trust_score = data.get("average_trust_score")
        self.trust_trend_7d = data.get("trust_trend_7d")
        self.trust_trend_30d = data.get("trust_trend_30d")
        self.calculated_at = data.get("calculated_at")

    @property
    def success_rate(self) -> float:
        """Get success rate percentage."""
        if self.total_verifications == 0:
            return 0.0
        return (self.successful_verifications / self.total_verifications) * 100

    def __repr__(self) -> str:
        return f"AgentMetrics(avg_trust={self.average_trust_score}, success_rate={self.success_rate:.1f}%)"


class SystemStats:
    """Represents system statistics."""

    def __init__(self, data: Dict[str, Any]):
        self.organization_id = data.get("organization_id")
        self.total_proofs = data.get("total_proofs")
        self.total_verifications = data.get("total_verifications")
        self.accepted_verifications = data.get("accepted_verifications")
        self.rejected_verifications = data.get("rejected_verifications")
        self.average_trust_score = data.get("average_trust_score")
        self.timestamp = data.get("timestamp")

    def __repr__(self) -> str:
        return f"SystemStats(total_proofs={self.total_proofs}, avg_trust={self.average_trust_score})"
