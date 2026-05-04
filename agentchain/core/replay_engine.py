from __future__ import annotations

from agentchain.models.schemas import ExecutionProof, LLMCallStep, ToolCallStep
from agentchain.utils.deterministic_runtime import mock_llm_call, run_tool


class ReplayEngine:
    """Replays logged execution steps and compares recorded results."""

    def replay(self, proof: ExecutionProof) -> tuple[bool, list[str]]:
        issues: list[str] = []

        for index, step in enumerate(proof.steps):
            if isinstance(step, LLMCallStep):
                expected_response = mock_llm_call(step.prompt)
                if step.response != expected_response:
                    issues.append(f"step {index}: llm response mismatch")

            elif isinstance(step, ToolCallStep):
                try:
                    expected_result = run_tool(step.tool, step.args)
                except ValueError as exc:
                    issues.append(f"step {index}: {exc}")
                    continue

                if step.result != expected_result:
                    issues.append(f"step {index}: tool result mismatch")

        if not proof.steps:
            issues.append("proof has no execution steps")

        if not self._output_matches_final_step(proof):
            issues.append("output does not match final llm response")

        return not issues, issues

    @staticmethod
    def _output_matches_final_step(proof: ExecutionProof) -> bool:
        final_llm_steps = [step for step in proof.steps if isinstance(step, LLMCallStep)]
        return bool(final_llm_steps) and proof.output == final_llm_steps[-1].response
