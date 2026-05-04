from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field


class StepType(str, Enum):
    LLM_CALL = "llm_call"
    TOOL_CALL = "tool_call"


class LLMCallStep(BaseModel):
    type: Literal["llm_call"] = "llm_call"
    prompt: str
    response: str


class ToolCallStep(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    tool: str
    args: Any
    result: Any


ExecutionStep = Annotated[
    Union[LLMCallStep, ToolCallStep],
    Field(discriminator="type"),
]


class ExecutionProof(BaseModel):
    task_id: str
    agent_id: str
    input: str
    output: str
    steps: list[ExecutionStep]
    timestamp: float
    hash: str


class TaskRequest(BaseModel):
    input: str = Field(..., min_length=1)


class VerificationResult(BaseModel):
    accepted: bool
    trust_score: float = Field(..., ge=0, le=100)
    hash_valid: bool
    replay_valid: bool
    issues: list[str] = Field(default_factory=list)


class TaskResponse(BaseModel):
    output: str
    execution_proof: ExecutionProof
    verification_result: VerificationResult
    trust_score: float = Field(..., ge=0, le=100)
