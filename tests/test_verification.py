"""Tests for the verification engine."""

import pytest
from datetime import datetime
from agentchain_trust.core.models import (
    ExecutionProof,
    ExecutionStep,
    StepType,
    VerificationResult,
)
from agentchain_trust.core.hashing import ExecutionHasher
from agentchain_trust.core.proof_engine import ProofEngine
from agentchain_trust.core.verifier import Verifier


def test_execution_hasher():
    """Test hash generation."""
    hasher = ExecutionHasher()
    
    step = {
        "type": "tool_call",
        "name": "calculator",
        "input_data": {"a": 1, "b": 2},
        "output_data": {"result": 3},
        "timestamp": 1234567890.0,
        "success": True,
    }
    
    hash1 = hasher.hash_step(step)
    hash2 = hasher.hash_step(step)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex digest


def test_merkle_root():
    """Test merkle tree generation."""
    hasher = ExecutionHasher()
    
    hashes = [
        "a" * 64,
        "b" * 64,
        "c" * 64,
    ]
    
    root = hasher.generate_merkle_root(hashes)
    assert len(root) == 64
    
    # Verify merkle root
    assert hasher.verify_merkle_root(hashes, root)


def test_proof_engine():
    """Test proof generation."""
    engine = ProofEngine()
    
    proof = engine.create_proof(
        agent_id="test-agent",
        organization_id="test-org",
        user_id="test-user",
        input_data={"query": "test"},
        output_data={"result": "test result"},
    )
    
    assert proof.agent_id == "test-agent"
    assert proof.organization_id == "test-org"
    assert proof.task_id is not None
    assert len(proof.steps) == 0


def test_proof_finalization():
    """Test proof finalization with hashing."""
    engine = ProofEngine()
    
    proof = engine.create_proof(
        agent_id="test-agent",
        organization_id="test-org",
        user_id="test-user",
        input_data={"query": "test"},
        output_data={"result": "test result"},
    )
    
    # Add a step
    engine.add_step(
        proof,
        StepType.TOOL_CALL,
        "calculator",
        {"a": 1, "b": 2},
        {"result": 3},
        10.5,
    )
    
    # Finalize
    proof = engine.finalize_proof(proof)
    
    assert proof.hash != ""
    assert proof.merkle_root != ""
    assert len(proof.steps) == 1


def test_proof_integrity_verification():
    """Test proof integrity check."""
    engine = ProofEngine()
    
    proof = engine.create_proof(
        agent_id="test-agent",
        organization_id="test-org",
        user_id="test-user",
        input_data={"query": "test"},
        output_data={"result": "test result"},
    )
    
    proof = engine.finalize_proof(proof)
    
    # Verify integrity
    assert engine.verify_proof_integrity(proof)
    
    # Tamper with proof
    proof.output_data["result"] = "tampered"
    
    # Should fail verification
    assert not engine.verify_proof_integrity(proof)


def test_verifier():
    """Test the main verifier."""
    verifier = Verifier()
    engine = ProofEngine()
    
    proof = engine.create_proof(
        agent_id="test-agent",
        organization_id="test-org",
        user_id="test-user",
        input_data={"query": "test"},
        output_data={"result": "test result"},
    )
    
    engine.add_step(
        proof,
        StepType.TOOL_CALL,
        "calculator",
        {"a": 1, "b": 2},
        {"result": 3},
        10.5,
    )
    
    proof = engine.finalize_proof(proof)
    
    result = verifier.verify_execution(proof, enable_replay=False)
    
    assert result.verification_id is not None
    assert result.task_id == proof.task_id
    assert result.hash_valid
    assert result.status in ["accepted", "rejected", "pending"]
    assert 0 <= result.trust_score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])