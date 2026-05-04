from __future__ import annotations

from agentchain.core.proof_engine import ProofEngine
from agentchain.models.schemas import ExecutionProof, LLMCallStep, ToolCallStep
from agentchain.utils.deterministic_runtime import mock_llm_call, run_tool


class WorkerAgent:
    """Executes user tasks and returns a complete execution proof."""

    def __init__(self, agent_id: str = "worker-001", proof_engine: ProofEngine | None = None) -> None:
        self.agent_id = agent_id
        self.proof_engine = proof_engine or ProofEngine()

    def execute(self, input_text: str) -> ExecutionProof:
        steps = []

        tool_args = {"text": input_text}
        tool_result = run_tool("text_stats", tool_args)
        steps.append(ToolCallStep(tool="text_stats", args=tool_args, result=tool_result))

        prompt = self._build_prompt(input_text=input_text, stats=tool_result)
        response = mock_llm_call(prompt)
        steps.append(LLMCallStep(prompt=prompt, response=response))

        return self.proof_engine.build_proof(
            agent_id=self.agent_id,
            input_text=input_text,
            output=response,
            steps=steps,
        )

    @staticmethod
    def _build_prompt(*, input_text: str, stats: dict[str, int]) -> str:
        return (
            "Execute task with verification context. "
            f"Task={input_text}. "
            f"Stats=characters:{stats['characters']},words:{stats['words']},"
            f"unique_words:{stats['unique_words']}."
        )
