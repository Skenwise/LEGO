"""PostgresIdentityRepository - Implements IIdentityRepository for profile_schema."""
import json
from typing import Optional

from core.domain.entities import Identity
from core.domain.value_objects import Email
from core.ports.driven import IIdentityRepository


class PostgresIdentityRepository(IIdentityRepository):
    """PostgreSQL implementation for Identity aggregate (profile_schema)."""
    
    def __init__(self, pool):
        """Initialize with asyncpg connection pool for profile_schema."""
        self._pool = pool
    
    async def get_by_id(self, identity_id: str) -> Optional[Identity]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, email, display_name, is_active, email_verified, created_at, updated_at "
                "FROM profile_schema.identities WHERE id = $1",
                identity_id
            )
        if not row:
            return None
        return Identity(
            id=row["id"],
            email=Email.create(row["email"]),
            display_name=row["display_name"],
            is_active=row["is_active"],
            email_verified=row["email_verified"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    async def get_by_email(self, email: Email) -> Optional[Identity]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, email, display_name, is_active, email_verified, created_at, updated_at "
                "FROM profile_schema.identities WHERE email = $1",
                email.value
            )
        if not row:
            return None
        return Identity(
            id=row["id"],
            email=Email.create(row["email"]),
            display_name=row["display_name"],
            is_active=row["is_active"],
            email_verified=row["email_verified"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    async def email_exists(self, email: Email) -> bool:
        async with self._pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM profile_schema.identities WHERE email = $1",
                email.value
            )
        return count > 0
    
    async def save(self, identity: Identity) -> Identity:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Check if exists
                existing = await self.get_by_id(identity.id)
                if existing:
                    # Update
                    await conn.execute(
                        """
                        UPDATE profile_schema.identities 
                        SET display_name = $1, is_active = $2, email_verified = $3, updated_at = $4
                        WHERE id = $5
                        """,
                        identity.display_name,
                        identity.is_active,
                        identity.email_verified,
                        identity.updated_at,
                        identity.id,
                    )
                else:
                    # Insert
                    await conn.execute(
                        """
                        INSERT INTO profile_schema.identities 
                        (id, email, display_name, is_active, email_verified, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        identity.id,
                        identity.email.value,
                        identity.display_name,
                        identity.is_active,
                        identity.email_verified,
                        identity.created_at,
                        identity.updated_at,
                    )
        return identity

    async def delete(self, identity_id: str) -> None:
        """Delete identity by ID (compensating action)."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM profile_schema.identities WHERE id = $1",
                identity_id
            )
