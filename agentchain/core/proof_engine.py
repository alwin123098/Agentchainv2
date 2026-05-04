from __future__ import annotations

import time
from uuid import uuid4

from agentchain.core.hashing import generate_execution_hash
from agentchain.models.schemas import ExecutionProof, ExecutionStep


class ProofEngine:
    """Creates tamper-evident execution proofs."""

    def build_proof(
        self,
        *,
        agent_id: str,
        input_text: str,
        output: str,
        steps: list[ExecutionStep],
    ) -> ExecutionProof:
        proof_hash = generate_execution_hash(
            input_text=input_text,
            steps=steps,
            output=output,
        )
        return ExecutionProof(
            task_id=str(uuid4()),
            agent_id=agent_id,
            input=input_text,
            output=output,
            steps=steps,
            timestamp=time.time(),
            hash=proof_hash,
        )
