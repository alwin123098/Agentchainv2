# AgentChain Trust Layer v2 🔐

**Production-grade trust verification system for autonomous AI agents**

AgentChain Trust Layer v2 is an enterprise-ready API that provides cryptographic proof, deterministic verification, and trust scoring for AI agent executions. Every developer can integrate it through a simple API key.

## 🎯 Features

### Core Trust Features
- ✅ **Execution Proofs**: Capture complete agent execution traces with all steps
- ✅ **Cryptographic Hashing**: SHA-256 based tamper detection with merkle trees
- ✅ **Determinism Verification**: Replay and validate execution consistency
- ✅ **Trust Scoring**: Multi-factor scoring (0-100) based on transparency, determinism, and integrity
- ✅ **Audit Logging**: Complete audit trail of all verifications

### Developer Experience
- 🔑 **API Key Authentication**: Simple Bearer token auth
- 📚 **REST API**: Comprehensive endpoints with OpenAPI docs
- 🐍 **Python SDK**: Full-featured client library
- 📦 **Batch Verification**: Verify multiple proofs in one request
- 📊 **Metrics & Analytics**: Trust trends and agent performance tracking
- 🔄 **Webhooks**: Real-time notifications (coming soon)

### Production Ready
- 🐳 **Docker Support**: Pre-configured containers
- 📈 **Prometheus Metrics**: Built-in monitoring
- 🗄️ **PostgreSQL**: Reliable data persistence
- ♻️ **Redis Caching**: Fast verification lookups
- 🔐 **Enterprise Security**: Role-based access, IP whitelisting

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/alwin123098/Agentchainv2.git
cd Agentchainv2
git checkout trust-layer-api-v2

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database and settings
```

### 3. Initialize Database

```bash
python -m agentchain_trust.cli init-database
```

### 4. Create API Key

```bash
python -m agentchain_trust.cli create-api-key \
  --org-id "my-org" \
  --name "Development Key" \
  --tier "pro"
```

### 5. Run Server

```bash
python run.py
# Server runs at http://localhost:8000
# API Docs at http://localhost:8000/docs
```

## 📖 API Documentation

### Verify Execution

```bash
curl -X POST http://localhost:8000/v1/verify-execution \
  -H "Authorization: Bearer agentchain_your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-001",
    "input_data": {"query": "What is 2+2?"},
    "output_data": {"answer": "4"},
    "steps": [],
    "model_used": "gpt-4"
  }'
```

### Get Verification Result

```bash
curl http://localhost:8000/v1/verification/{task_id} \
  -H "Authorization: Bearer agentchain_your_key"
```

### Batch Verify

```bash
curl -X POST http://localhost:8000/v1/batch-verify \
  -H "Authorization: Bearer agentchain_your_key" \
  -H "Content-Type: application/json" \
  -d '{"proofs": [...], "enable_replay": true}'
```

### Get Agent Metrics

```bash
curl http://localhost:8000/v1/agent/{agent_id}/metrics \
  -H "Authorization: Bearer agentchain_your_key"
```

## 📋 Endpoints

- `GET /health` - Health check
- `POST /v1/verify-execution` - Verify single execution
- `GET /v1/verification/{task_id}` - Get verification result
- `POST /v1/batch-verify` - Verify multiple proofs
- `GET /v1/agent/{agent_id}/metrics` - Get agent metrics
- `GET /v1/stats` - Get system statistics

## 🌟 Docker

```bash
docker-compose up -d
```

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📄 License

MIT License

## 💬 Support

- Documentation: https://docs.agentchain.ai
- Discord: https://discord.gg/agentchain
- Issues: https://github.com/alwin123098/Agentchainv2/issues
