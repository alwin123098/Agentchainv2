# AgentChain Trust Layer Python SDK

Official Python SDK for AgentChain Trust Layer API.

## Installation

```bash
pip install agentchain-trust-sdk
```

### With async support

```bash
pip install agentchain-trust-sdk[async]
```

## Quick Start

```python
from agentchain_trust_sdk import TrustLayerClient, ExecutionProof, StepType

# Initialize client
client = TrustLayerClient(api_key="agentchain_your_key")

# Create execution proof
proof = ExecutionProof(
    agent_id="agent-001",
    input_data={"query": "What is AI?"},
    output_data={"answer": "AI is..."}
)

# Add steps
proof.add_step(
    step_type=StepType.TOOL_CALL,
    name="search",
    input_data={"q": "AI"},
    output_data={"results": [...]},
    duration_ms=150.0
)

# Verify
result = client.verify_execution(proof)
print(f"Trust Score: {result.trust_score}")
print(f"Status: {result.status}")
```

## Features

✅ Sync & Async support
✅ Automatic retries with backoff
✅ Type hints
✅ Comprehensive error handling
✅ Easy batch operations

## Documentation

- [API Reference](https://docs.agentchain.ai/sdk/python)
- [Examples](examples/)
- [Async Usage](docs/async.md)

## License

MIT
