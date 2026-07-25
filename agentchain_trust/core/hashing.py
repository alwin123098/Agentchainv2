"""Cryptographic hashing for execution proofs."""

import hashlib
import json
from typing import Any, Dict, List
from datetime import datetime


class ExecutionHasher:
    """Generate and verify cryptographic hashes for execution proofs."""

    ALGORITHM = "sha256"

    @staticmethod
    def serialize_for_hash(data: Any) -> str:
        """Serialize data to JSON in deterministic order."""
        return json.dumps(data, sort_keys=True, default=str, separators=(',', ':'))

    @staticmethod
    def hash_step(step: Dict[str, Any]) -> str:
        """Generate hash for a single execution step."""
        step_data = {
            "type": step.get("type"),
            "name": step.get("name"),
            "input": step.get("input_data"),
            "output": step.get("output_data"),
            "timestamp": step.get("timestamp"),
            "success": step.get("success"),
        }
        serialized = ExecutionHasher.serialize_for_hash(step_data)
        return hashlib.sha256(serialized.encode()).hexdigest()

    @staticmethod
    def generate_merkle_root(step_hashes: List[str]) -> str:
        """Generate merkle tree root from step hashes."""
        if not step_hashes:
            return hashlib.sha256(b"").hexdigest()

        # Build merkle tree bottom-up
        current_level = step_hashes.copy()
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                hash_val = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(hash_val)
            current_level = next_level

        return current_level[0]

    @staticmethod
    def hash_execution_proof(proof: Dict[str, Any]) -> str:
        """Generate hash for entire execution proof."""
        proof_data = {
            "task_id": proof.get("task_id"),
            "agent_id": proof.get("agent_id"),
            "input": proof.get("input_data"),
            "output": proof.get("output_data"),
            "timestamp": proof.get("timestamp"),
            "merkle_root": proof.get("merkle_root"),
        }
        serialized = ExecutionHasher.serialize_for_hash(proof_data)
        return hashlib.sha256(serialized.encode()).hexdigest()

    @staticmethod
    def verify_hash(proof: Dict[str, Any], expected_hash: str) -> bool:
        """Verify a proof hash."""
        computed_hash = ExecutionHasher.hash_execution_proof(proof)
        return computed_hash == expected_hash

    @staticmethod
    def verify_merkle_root(step_hashes: List[str], expected_root: str) -> bool:
        """Verify merkle tree root."""
        computed_root = ExecutionHasher.generate_merkle_root(step_hashes)
        return computed_root == expected_root