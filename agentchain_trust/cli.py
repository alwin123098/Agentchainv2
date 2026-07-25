"""CLI for managing Trust Layer."""

import click
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from agentchain_trust.database.db import SessionLocal, init_db
from agentchain_trust.database.models import APIKey
from agentchain_trust.auth.keys import APIKeyManager


@click.group()
def cli():
    """AgentChain Trust Layer CLI."""
    pass


@cli.command()
def init_database():
    """Initialize the database."""
    click.echo("Initializing database...")
    init_db()
    click.echo("✅ Database initialized successfully!")


@cli.command()
@click.option('--org-id', required=True, help='Organization ID')
@click.option('--name', required=True, help='API Key name')
@click.option('--tier', default='free', help='API Key tier: free, pro, enterprise')
@click.option('--expires-days', default=None, type=int, help='Days until expiration')
def create_api_key(org_id, name, tier, expires_days):
    """Create a new API key."""
    try:
        db = SessionLocal()
        
        key = APIKeyManager.generate_key()
        key_hash = APIKeyManager.hash_key(key)
        
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        api_key_record = APIKey(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            key_hash=key_hash,
            name=name,
            tier=tier,
            expires_at=expires_at,
        )
        
        db.add(api_key_record)
        db.commit()
        
        click.echo(f"\n✅ API Key created successfully!")
        click.echo(f"\n🔑 API Key: {key}")
        click.echo(f"📝 Key ID: {api_key_record.id}")
        click.echo(f"🏢 Organization: {org_id}")
        click.echo(f"🎯 Tier: {tier}")
        if expires_at:
            click.echo(f"⏰ Expires: {expires_at.isoformat()}")
        click.echo("\n⚠️  Save this key securely! You won't be able to see it again.\n")
        
        db.close()
    except Exception as e:
        click.echo(f"❌ Error creating API key: {e}")


@cli.command()
@click.option('--org-id', required=True, help='Organization ID')
def list_api_keys(org_id):
    """List API keys for an organization."""
    try:
        db = SessionLocal()
        
        keys = db.query(APIKey).filter_by(organization_id=org_id).all()
        
        if not keys:
            click.echo(f"No API keys found for organization {org_id}")
            return
        
        click.echo(f"\n📋 API Keys for {org_id}:\n")
        for key in keys:
            status = "✅ Active" if key.is_active else "❌ Inactive"
            expires = f"Expires: {key.expires_at.isoformat()}" if key.expires_at else "Never expires"
            click.echo(f"  • {key.name} ({key.tier}) - {status}")
            click.echo(f"    ID: {key.id}")
            click.echo(f"    Created: {key.created_at.isoformat()}")
            click.echo(f"    {expires}")
            click.echo()
        
        db.close()
    except Exception as e:
        click.echo(f"❌ Error listing API keys: {e}")


@cli.command()
@click.option('--key-id', required=True, help='API Key ID')
def revoke_api_key(key_id):
    """Revoke an API key."""
    try:
        db = SessionLocal()
        
        key = db.query(APIKey).filter_by(id=key_id).first()
        if not key:
            click.echo(f"❌ API key not found: {key_id}")
            return
        
        key.is_active = False
        db.commit()
        
        click.echo(f"✅ API key revoked: {key.name}")
        db.close()
    except Exception as e:
        click.echo(f"❌ Error revoking API key: {e}")


if __name__ == '__main__':
    cli()