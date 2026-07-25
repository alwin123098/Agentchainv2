"""Example usage of Python SDK."""

from agentchain_trust_sdk import (
    TrustLayerClient,
    ExecutionProof,
    StepType,
)

# Initialize client
client = TrustLayerClient(api_key="agentchain_your_key_here")

# Create execution proof
proof = ExecutionProof(
    agent_id="agent-001",
    input_data={"question": "What is machine learning?"},
    output_data={"answer": "Machine learning is..."},
    model_used="gpt-4",
    metadata={"environment": "production"},
)

# Add execution steps
proof.add_step(
    step_type=StepType.TOOL_CALL,
    name="search",
    input_data={"query": "machine learning"},
    output_data={"results": ["ML is...", "ML includes..."]},
    duration_ms=150.5,
)

proof.add_step(
    step_type=StepType.LLM_CALL,
    name="gpt-4",
    input_data={"prompt": "Summarize the search results"},
    output_data={"summary": "Machine learning is..."},
    duration_ms=1250.0,
)

# Verify execution
print("\n🔍 Verifying execution...")
result = client.verify_execution(proof)

print(f"\n✅ Verification Complete!")
print(f"   Status: {result.status}")
print(f"   Trust Score: {result.trust_score}")
print(f"   Task ID: {result.task_id}")

if result.is_accepted:
    print(f"   ✅ Execution ACCEPTED")
else:
    print(f"   ❌ Execution REJECTED")

# Get agent metrics
print("\n📊 Fetching agent metrics...")
metrics = client.get_agent_metrics("agent-001")

print(f"   Total Verifications: {metrics.total_verifications}")
print(f"   Success Rate: {metrics.success_rate:.1f}%")
print(f"   Average Trust Score: {metrics.average_trust_score}")

# Batch verification example
print("\n🔄 Batch Verification...")
proof2 = ExecutionProof(
    agent_id="agent-002",
    input_data={"task": "analysis"},
    output_data={"result": "complete"},
)

batch_result = client.batch_verify([proof, proof2])
print(f"   Total: {batch_result.total_proofs}")
print(f"   Successful: {batch_result.successful}")
print(f"   Failed: {batch_result.failed}")
print(f"   Success Rate: {batch_result.success_rate:.1f}%")

# Get system stats
print("\n📈 System Statistics...")
stats = client.get_stats()
print(f"   Total Proofs: {stats.total_proofs}")
print(f"   Total Verifications: {stats.total_verifications}")
print(f"   Average Trust Score: {stats.average_trust_score}")

print("\n✅ All examples completed!")
