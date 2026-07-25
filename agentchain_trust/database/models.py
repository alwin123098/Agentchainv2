"""SQLAlchemy database models."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class APIKey(Base):
    """API Key model."""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True)
    organization_id = Column(String, nullable=False, index=True)
    key_hash = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    tier = Column(String, default="free")  # free, pro, enterprise
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)
    requests_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, default={})

    __table_args__ = (Index("idx_api_key_org_active", "organization_id", "is_active"),)


class ExecutionProofRecord(Base):
    """Execution proof record."""
    __tablename__ = "execution_proofs"

    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False, unique=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    organization_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    input_data = Column(JSON)
    output_data = Column(JSON)
    hash = Column(String, nullable=False)
    merkle_root = Column(String, nullable=True)
    model_used = Column(String, nullable=True)
    execution_duration_ms = Column(Float)
    steps_count = Column(Integer, default=0)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    stored_proof = Column(JSON)  # Full proof JSON

    __table_args__ = (
        Index("idx_proof_agent_org", "agent_id", "organization_id"),
        Index("idx_proof_created_at", "created_at"),
    )


class VerificationRecordDB(Base):
    """Verification result record."""
    __tablename__ = "verification_records"

    id = Column(String, primary_key=True)
    verification_id = Column(String, nullable=False, unique=True)
    task_id = Column(String, ForeignKey("execution_proofs.task_id"), nullable=False, index=True)
    status = Column(String)  # accepted, rejected, pending
    trust_score = Column(Float)
    hash_valid = Column(Boolean)
    replay_valid = Column(Boolean, nullable=True)
    determinism_score = Column(Float, nullable=True)
    transparency_score = Column(Float, nullable=True)
    issues = Column(JSON, default=[])
    verified_by = Column(String, default="system")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_verification_task", "task_id"),
        Index("idx_verification_status", "status"),
    )


class AuditLogRecord(Base):
    """Audit log entry."""
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    api_key_id = Column(String, ForeignKey("api_keys.id"), nullable=True)
    organization_id = Column(String, nullable=False, index=True)
    action = Column(String)  # verify, retrieve, batch_verify, etc.
    resource_type = Column(String)  # execution_proof, verification_result
    resource_id = Column(String, nullable=True)
    status = Column(String)  # success, failed
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_audit_org_created", "organization_id", "created_at"),
        Index("idx_audit_api_key", "api_key_id"),
    )


class TrustMetricsRecord(Base):
    """Agent trust metrics."""
    __tablename__ = "trust_metrics"

    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=False, index=True)
    organization_id = Column(String, nullable=False, index=True)
    total_verifications = Column(Integer, default=0)
    successful_verifications = Column(Integer, default=0)
    failed_verifications = Column(Integer, default=0)
    average_trust_score = Column(Float, default=0.0)
    trust_trend_7d = Column(Float, nullable=True)
    trust_trend_30d = Column(Float, nullable=True)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_metrics_agent_org", "agent_id", "organization_id"),)