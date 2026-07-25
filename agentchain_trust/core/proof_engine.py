"""Proof engine for generating and managing execution proofs."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
import time
from .hashing import ExecutionHasher
from .models import ExecutionProof, ExecutionStep, StepType


class ProofEngine:
    """Generate and manage execution proofs."""

    def __init__(self):
        self.hasher = ExecutionHasher()

    def create_proof(
        self,
        agent_id: str,
        organization_id: str,
        user_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        model_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionProof:
        """Create a new execution proof."""
        task_id = str(uuid.uuid4())
        timestamp = time.time()

        proof = ExecutionProof(
            task_id=task_id,
            agent_id=agent_id,
            organization_id=organization_id,
            user_id=user_id,
            input_data=input_data,
            output_data=output_data,
            timestamp=timestamp,
            execution_duration_ms=0,
            hash="",
            model_used=model_used,
            metadata=metadata or {},
        )

        return proof

    def add_step(
        self,
        proof: ExecutionProof,
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
            timestamp=time.time(),
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
        )

        proof.steps.append(step)
        return step

    def finalize_proof(self, proof: ExecutionProof) -> ExecutionProof:
        """Finalize proof by computing hashes and merkle root."""
        # Calculate execution duration
        if proof.steps:
            first_step_time = proof.steps[0].timestamp
            last_step_time = proof.steps[-1].timestamp
            proof.execution_duration_ms = (last_step_time - first_step_time) * 1000
        else:
            proof.execution_duration_ms = 0

        # Generate merkle root from step hashes
        step_hashes = [self.hasher.hash_step(step.model_dump()) for step in proof.steps]
        proof.merkle_root = self.hasher.generate_merkle_root(step_hashes)

        # Generate proof hash
        proof_dict = proof.model_dump(exclude={"hash"})
        proof.hash = self.hasher.hash_execution_proof(proof_dict)

        return proof

    def verify_proof_integrity(self, proof: ExecutionProof) -> bool:
        """Verify proof hasn't been tampered with."""
        # Verify merkle root
        step_hashes = [self.hasher.hash_step(step.model_dump()) for step in proof.steps]
        merkle_valid = self.hasher.verify_merkle_root(step_hashes, proof.merkle_root)

        # Verify proof hash
        proof_dict = proof.model_dump(exclude={"hash"})
        hash_valid = self.hasher.verify_hash(proof_dict, proof.hash)

        return merkle_valid and hash_valid