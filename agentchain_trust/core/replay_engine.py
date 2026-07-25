"""Replay engine for validating deterministic execution."""

from typing import Any, Dict, List, Optional, Callable
from .models import ExecutionProof, ExecutionStep, StepType, VerificationIssue
import json


class ReplayEngine:
    """Replay and validate agent executions for determinism."""

    def __init__(self):
        self.tool_registry: Dict[str, Callable] = {}
        self.replay_history = {}

    def register_tool(self, tool_name: str, tool_func: Callable) -> None:
        """Register a deterministic tool for replay."""
        self.tool_registry[tool_name] = tool_func

    def replay_execution(
        self,
        proof: ExecutionProof,
        tool_implementations: Optional[Dict[str, Callable]] = None,
    ) -> tuple[bool, List[VerificationIssue]]:
        """Replay execution and verify determinism."""
        issues: List[VerificationIssue] = []
        all_deterministic = True

        if not proof.steps:
            return True, issues

        for step in proof.steps:
            if step.type == StepType.TOOL_CALL:
                # Verify tool call can be replayed
                if step.name in tool_implementations or step.name in self.tool_registry:
                    tool_func = tool_implementations.get(step.name) or self.tool_registry.get(step.name)
                    try:
                        replayed_output = tool_func(**step.input_data)
                        # Check if output matches original
                        if not self._outputs_match(replayed_output, step.output_data):
                            all_deterministic = False
                            issues.append(
                                VerificationIssue(
                                    severity="warning",
                                    code="NON_DETERMINISTIC_TOOL",
                                    message=f"Tool '{step.name}' produced different output on replay",
                                    step_id=step.step_id,
                                )
                            )
                    except Exception as e:
                        issues.append(
                            VerificationIssue(
                                severity="critical",
                                code="TOOL_EXECUTION_FAILED",
                                message=f"Tool '{step.name}' failed during replay: {str(e)}",
                                step_id=step.step_id,
                            )
                        )
                        all_deterministic = False
                else:
                    issues.append(
                        VerificationIssue(
                            severity="warning",
                            code="TOOL_NOT_FOUND",
                            message=f"Tool '{step.name}' not registered for replay",
                            step_id=step.step_id,
                        )
                    )

            elif step.type == StepType.LLM_CALL:
                # LLM calls are non-deterministic by nature, flag for awareness
                issues.append(
                    VerificationIssue(
                        severity="info",
                        code="NON_DETERMINISTIC_LLM",
                        message="LLM calls are inherently non-deterministic",
                        step_id=step.step_id,
                    )
                )

        return all_deterministic, issues

    def _outputs_match(self, output1: Any, output2: Any, tolerance: float = 0.001) -> bool:
        """Check if two outputs match (with tolerance for floats)."""
        if type(output1) != type(output2):
            return False

        if isinstance(output1, dict):
            if set(output1.keys()) != set(output2.keys()):
                return False
            return all(self._outputs_match(output1[k], output2[k]) for k in output1.keys())

        elif isinstance(output1, (list, tuple)):
            if len(output1) != len(output2):
                return False
            return all(self._outputs_match(a, b) for a, b in zip(output1, output2))

        elif isinstance(output1, float) and isinstance(output2, float):
            return abs(output1 - output2) < tolerance

        else:
            return output1 == output2