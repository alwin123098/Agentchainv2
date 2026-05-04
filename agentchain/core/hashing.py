from __future__ import annotations

import hashlib
import json
from typing import Any

from agentchain.models.schemas import ExecutionProof, ExecutionStep


def canonical_json(payload: Any) -> str:
    """Serialize data in a stable form so equal proofs always hash identically."""
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def step_to_hashable(step: ExecutionStep) -> dict[str, Any]:
    return step.model_dump(mode="json")


def proof_payload_for_hash(input_text: str, steps: list[ExecutionStep], output: str) -> dict[str, Any]:
    return {
        "input": input_text,
        "steps": [step_to_hashable(step) for step in steps],
        "output": output,
    }


def generate_execution_hash(input_text: str, steps: list[ExecutionStep], output: str) -> str:
    payload = proof_payload_for_hash(input_text=input_text, steps=steps, output=output)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def verify_execution_hash(proof: ExecutionProof) -> bool:
    expected = generate_execution_hash(
        input_text=proof.input,
        steps=proof.steps,
        output=proof.output,
    )
    return expected == proof.hash
