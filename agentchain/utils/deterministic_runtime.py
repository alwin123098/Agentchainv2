from __future__ import annotations

import re
from typing import Any


def mock_llm_call(prompt: str) -> str:
    """Deterministic LLM stand-in used by workers and replay verification."""
    normalized = " ".join(prompt.strip().split())
    return f"AGENTCHAIN_RESULT::{normalized.upper()}"


def run_tool(tool: str, args: Any) -> Any:
    if tool == "text_stats":
        text = str(args.get("text", "")) if isinstance(args, dict) else str(args)
        words = re.findall(r"\b\w+\b", text)
        return {
            "characters": len(text),
            "words": len(words),
            "unique_words": len({word.lower() for word in words}),
        }

    raise ValueError(f"Unsupported tool: {tool}")
