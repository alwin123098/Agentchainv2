from __future__ import annotations

from fastapi import FastAPI, HTTPException

from agentchain.models.schemas import TaskRequest, TaskResponse
from agentchain.orchestration.orchestrator import Orchestrator

app = FastAPI(
    title="AGENTCHAIN v2",
    description="A trust layer for autonomous AI agents with provable, verifiable, replayable outputs.",
    version="2.0.0",
)

orchestrator = Orchestrator()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/execute-task", response_model=TaskResponse)
def execute_task(request: TaskRequest) -> TaskResponse:
    result = orchestrator.execute_task(request.input)
    if not result.verification_result.accepted:
        raise HTTPException(status_code=422, detail=result.model_dump(mode="json"))
    return result
