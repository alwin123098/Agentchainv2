"""Tests for Python SDK."""

import pytest
from agentchain_trust_sdk import (
    ExecutionProof,
    ExecutionStep,
    StepType,
    VerificationResult,
    AgentMetrics,
)


def test_execution_step_creation():
    """Test ExecutionStep creation."""
    step = ExecutionStep(
        type=StepType.TOOL_CALL,
        name="calculator",
        input_data={"a": 1, "b": 2},
        output_data={"result": 3},
        duration_ms=5.2,
    )

    assert step.type == StepType.TOOL_CALL
    assert step.name == "calculator"
    assert step.success is True
    assert step.step_id is not None


def test_execution_proof_creation():
    """Test ExecutionProof creation."""
    proof = ExecutionProof(
        agent_id="agent-001",
        input_data={"query": "test"},
        output_data={"result": "test result"},
    )

    assert proof.agent_id == "agent-001"
    assert proof.task_id is not None
    assert len(proof.steps) == 0


def test_execution_proof_add_step():
    """Test adding steps to proof."""
    proof = ExecutionProof(
        agent_id="agent-001",
        input_data={},
        output_data={},
    )

    step = proof.add_step(
        step_type=StepType.TOOL_CALL,
        name="test_tool",
        input_data={"x": 1},
        output_data={"y": 2},
        duration_ms=10.0,
    )

    assert len(proof.steps) == 1
    assert step.name == "test_tool"


def test_verification_result():
    """Test VerificationResult."""
    data = {
        "verification_id": "ver-001",
        "task_id": "task-001",
        "status": "accepted",
        "trust_score": 85.5,
        "hash_valid": True,
        "replay_valid": True,
        "determinism_score": 90.0,
        "transparency_score": 85.0,
        "issues": [],
        "verified_at": "2026-07-25T15:00:00Z",
    }

    result = VerificationResult(data)
    assert result.status == "accepted"
    assert result.is_accepted is True
    assert result.trust_score == 85.5


def test_agent_metrics():
    """Test AgentMetrics."""
    data = {
        "agent_id": "agent-001",
        "total_verifications": 100,
        "successful_verifications": 95,
        "failed_verifications": 5,
        "average_trust_score": 87.5,
        "trust_trend_7d": 2.5,
        "trust_trend_30d": 1.2,
        "calculated_at": "2026-07-25T15:00:00Z",
    }

    metrics = AgentMetrics(data)
    assert metrics.agent_id == "agent-001"
    assert metrics.success_rate == 95.0
    assert metrics.average_trust_score == 87.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])