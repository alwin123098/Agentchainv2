from __future__ import annotations

from agentchain.agents.verifier_agent import VerifierAgent
from agentchain.agents.worker_agent import WorkerAgent
from agentchain.models.schemas import TaskResponse


class Orchestrator:
    """Routes user tasks through worker execution and verifier acceptance."""

    def __init__(
        self,
        worker: WorkerAgent | None = None,
        verifier: VerifierAgent | None = None,
    ) -> None:
        self.worker = worker or WorkerAgent()
        self.verifier = verifier or VerifierAgent()

    def execute_task(self, input_text: str) -> TaskResponse:
        proof = self.worker.execute(input_text)
        verification = self.verifier.verify(proof)

        return TaskResponse(
            output=proof.output if verification.accepted else "",
            execution_proof=proof,
            verification_result=verification,
            trust_score=verification.trust_score,
        )
