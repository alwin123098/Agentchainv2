"""Example usage of the Trust Layer API."""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_KEY = "agentchain_your_key_here"  # Replace with actual key


def example_basic_verification():
    """Example: Basic execution verification."""
    print("\n=== Basic Execution Verification ===")
    
    payload = {
        "agent_id": "agent-001",
        "input_data": {
            "question": "What is 2+2?"
        },
        "output_data": {
            "answer": "4",
            "confidence": 0.99
        },
        "steps": [
            {
                "type": "tool_call",
                "name": "calculator",
                "input_data": {"expression": "2+2"},
                "output_data": {"result": 4},
                "duration_ms": 5.2,
                "success": True
            }
        ],
        "model_used": "gpt-4",
        "metadata": {
            "environment": "production",
            "version": "1.0"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/verify-execution",
        json=payload,
        headers=headers
    )
    
    result = response.json()
    print(f"Status: {result['status']}")
    print(f"Trust Score: {result['trust_score']}")
    print(f"Task ID: {result['task_id']}")
    print(json.dumps(result, indent=2))
    
    return result["task_id"]


def example_batch_verification():
    """Example: Batch verify multiple proofs."""
    print("\n=== Batch Verification ===")
    
    payload = {
        "proofs": [
            {
                "agent_id": "agent-001",
                "input_data": {"query": "First task"},
                "output_data": {"result": "Result 1"},
                "steps": [],
            },
            {
                "agent_id": "agent-002",
                "input_data": {"query": "Second task"},
                "output_data": {"result": "Result 2"},
                "steps": [],
            },
        ],
        "enable_replay": False
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/batch-verify",
        json=payload,
        headers=headers
    )
    
    result = response.json()
    print(f"Batch ID: {result['batch_id']}")
    print(f"Total: {result['total_proofs']}, Successful: {result['successful']}, Failed: {result['failed']}")
    print(json.dumps(result, indent=2))


def example_get_verification(task_id):
    """Example: Retrieve verification result."""
    print(f"\n=== Get Verification Result ===")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }
    
    response = requests.get(
        f"{BASE_URL}/v1/verification/{task_id}",
        headers=headers
    )
    
    result = response.json()
    print(json.dumps(result, indent=2))


def example_agent_metrics():
    """Example: Get agent trust metrics."""
    print("\n=== Agent Trust Metrics ===")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }
    
    response = requests.get(
        f"{BASE_URL}/v1/agent/agent-001/metrics",
        headers=headers
    )
    
    result = response.json()
    print(json.dumps(result, indent=2))


def example_system_stats():
    """Example: Get system statistics."""
    print("\n=== System Statistics ===")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }
    
    response = requests.get(
        f"{BASE_URL}/v1/stats",
        headers=headers
    )
    
    result = response.json()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    print("🚀 AgentChain Trust Layer API - Usage Examples")
    print("="*50)
    
    # Run examples
    task_id = example_basic_verification()
    example_batch_verification()
    example_get_verification(task_id)
    example_agent_metrics()
    example_system_stats()
    
    print("\n✅ Examples completed!")