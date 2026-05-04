# AGENTCHAIN v2

A minimal production-grade trust layer for autonomous AI agents.

The system enforces that every worker output is:

- Provable through a structured execution proof
- Verifiable through deterministic hashing
- Replayable through an independent replay engine

## Architecture

- Execution Layer: `agents/worker_agent.py`, `utils/deterministic_runtime.py`
- Trust Layer: `core/proof_engine.py`, `core/hashing.py`, `core/replay_engine.py`, `core/verifier.py`
- Orchestration Layer: `orchestration/orchestrator.py`
- Application Layer: `api/main.py`

## Run Locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn agentchain.api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Example Request

```bash
curl -X POST http://127.0.0.1:8000/execute-task \
  -H "Content-Type: application/json" \
  -d '{"input":"Summarize the trust guarantees for this task"}'
```

## Example Response

```json
{
  "output": "AGENTCHAIN_RESULT::EXECUTE TASK WITH VERIFICATION CONTEXT. TASK=SUMMARIZE THE TRUST GUARANTEES FOR THIS TASK. STATS=CHARACTERS:44,WORDS:7,UNIQUE_WORDS:7.",
  "execution_proof": {
    "task_id": "3f3e7fd2-ef3d-4fcb-a25b-03f7ddba4781",
    "agent_id": "worker-001",
    "input": "Summarize the trust guarantees for this task",
    "output": "AGENTCHAIN_RESULT::EXECUTE TASK WITH VERIFICATION CONTEXT. TASK=SUMMARIZE THE TRUST GUARANTEES FOR THIS TASK. STATS=CHARACTERS:44,WORDS:7,UNIQUE_WORDS:7.",
    "steps": [
      {
        "type": "tool_call",
        "tool": "text_stats",
        "args": {
          "text": "Summarize the trust guarantees for this task"
        },
        "result": {
          "characters": 44,
          "words": 7,
          "unique_words": 7
        }
      },
      {
        "type": "llm_call",
        "prompt": "Execute task with verification context. Task=Summarize the trust guarantees for this task. Stats=characters:44,words:7,unique_words:7.",
        "response": "AGENTCHAIN_RESULT::EXECUTE TASK WITH VERIFICATION CONTEXT. TASK=SUMMARIZE THE TRUST GUARANTEES FOR THIS TASK. STATS=CHARACTERS:44,WORDS:7,UNIQUE_WORDS:7."
      }
    ],
    "timestamp": 1777900000.0,
    "hash": "sha256-hex-generated-at-runtime"
  },
  "verification_result": {
    "accepted": true,
    "trust_score": 100.0,
    "hash_valid": true,
    "replay_valid": true,
    "issues": []
  },
  "trust_score": 100.0
}
```
