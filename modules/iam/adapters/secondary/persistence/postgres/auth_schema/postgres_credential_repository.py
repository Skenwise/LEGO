"""PostgresCredentialRepository - Implements ICredentialRepository for auth_schema."""
from typing import Optional

from core.domain.entities import Credential
from core.domain.value_objects import PasswordHash
from core.ports.driven import ICredentialRepository


class PostgresCredentialRepository(ICredentialRepository):
    """PostgreSQL implementation for Credential aggregate (auth_schema - ISO 8.27 isolated)."""
    
    def __init__(self, pool):
        """Initialize with asyncpg connection pool for auth_schema (different DB user!)."""
        self._pool = pool
    
    async def get_by_identity_id(self, identity_id: str) -> Optional[Credential]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, identity_id, password_hash, mfa_secret, mfa_enabled, 
                       backup_codes_hash, failed_attempts, locked_until, 
                       last_login_at, created_at, updated_at
                FROM auth_schema.credentials WHERE identity_id = $1
                """,
                identity_id
            )
        if not row:
            return None
        return Credential(
            id=row["id"],
            identity_id=row["identity_id"],
            password_hash=PasswordHash.from_string(row["password_hash"]),
            mfa_secret=row["mfa_secret"],
            mfa_enabled=row["mfa_enabled"],
            backup_codes_hash=row["backup_codes_hash"],
            failed_attempts=row["failed_attempts"],
            locked_until=row["locked_until"],
            last_login_at=row["last_login_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    
    async def save(self, credential: Credential) -> Credential:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                existing = await self.get_by_identity_id(credential.identity_id)
                if existing:
                    await conn.execute(
                        """
                        UPDATE auth_schema.credentials 
                        SET password_hash = $1, mfa_secret = $2, mfa_enabled = $3,
                            backup_codes_hash = $4, failed_attempts = $5, locked_until = $6,
                            last_login_at = $7, updated_at = $8
                        WHERE identity_id = $9
                        """,
                        str(credential.password_hash),
                        credential.mfa_secret,
                        credential.mfa_enabled,
                        credential.backup_codes_hash,
                        credential.failed_attempts,
                        credential.locked_until,
                        credential.last_login_at,
                        credential.updated_at,
                        credential.identity_id,
                    )
                else:
                    await conn.execute(
                        """
                        INSERT INTO auth_schema.credentials 
                        (id, identity_id, password_hash, mfa_secret, mfa_enabled,
                         backup_codes_hash, failed_attempts, locked_until,
                         last_login_at, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        """,
                        credential.id,
                        credential.identity_id,
                        str(credential.password_hash),
                        credential.mfa_secret,
                        credential.mfa_enabled,
                        credential.backup_codes_hash,
                        credential.failed_attempts,
                        credential.locked_until,
                        credential.last_login_at,
                        credential.created_at,
                        credential.updated_at,
                    )
        return credential
    
    async def update_failed_attempts(self, identity_id: str, attempts: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE auth_schema.credentials SET failed_attempts = $1 WHERE identity_id = $2",
                attempts, identity_id
            )
    
    async def lock_account(self, identity_id: str, locked_until) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE auth_schema.credentials SET locked_until = $1 WHERE identity_id = $2",
                locked_until, identity_id
            )
