"""JWTTokenService - Implements ITokenService port."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Optional, Dict, Set
from uuid import UUID
from jose import jwt, JWTError

from core.ports.driven.itoken_service import ITokenService
from core.domain.value_objects.token_claim import TokenClaim


class JWTTokenService(ITokenService):
    """JWT token service with HS256 signing and revocation support."""
    
    def __init__(
        self,
        secret_key: str,
        refresh_secret_key: str,
        access_ttl_minutes: int = 15,
        refresh_ttl_days: int = 7,
        algorithm: str = "HS256",
    ):
        self._secret_key = secret_key
        self._refresh_secret_key = refresh_secret_key
        self._access_ttl_minutes = access_ttl_minutes
        self._refresh_ttl_days = refresh_ttl_days
        self._algorithm = algorithm
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._revoked_tokens: Set[str] = set()
        self._user_tokens: Dict[str, Set[str]] = {}  # Track tokens per user
    
    async def create_access_token(self, claim: TokenClaim) -> str:
        user_id_str = str(claim.user_id) if isinstance(claim.user_id, UUID) else claim.user_id
        
        payload = {
            "sub": user_id_str,
            "exp": int(claim.expires_at.timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "type": "access",
            "scopes": list(claim.scopes),
        }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        )
    
    async def create_refresh_token(self, claim: TokenClaim) -> tuple[str, str]:
        user_id_str = str(claim.user_id) if isinstance(claim.user_id, UUID) else claim.user_id
        refresh_id = f"ref_{user_id_str}_{int(claim.expires_at.timestamp())}"
        
        # Track this token for the user
        if user_id_str not in self._user_tokens:
            self._user_tokens[user_id_str] = set()
        self._user_tokens[user_id_str].add(refresh_id)
        
        payload = {
            "sub": user_id_str,
            "exp": int(claim.expires_at.timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "type": "refresh",
            "refresh_id": refresh_id,
        }
        
        loop = asyncio.get_event_loop()
        token = await loop.run_in_executor(
            self._executor,
            lambda: jwt.encode(payload, self._refresh_secret_key, algorithm=self._algorithm)
        )
        
        return token, refresh_id
    
    async def verify_token(self, token: str, token_type: str) -> Optional[TokenClaim]:
        secret = self._secret_key if token_type == "access" else self._refresh_secret_key
        
        try:
            loop = asyncio.get_event_loop()
            payload = await loop.run_in_executor(
                self._executor,
                lambda: jwt.decode(token, secret, algorithms=[self._algorithm])
            )
        except JWTError:
            return None
        
        if payload.get("type") != token_type:
            return None
        
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            return None
        
        if token_type == "refresh":
            refresh_id = payload.get("refresh_id")
            if refresh_id and await self.is_revoked(refresh_id):
                return None
        
        return TokenClaim(
            user_id=payload["sub"],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            token_type=token_type,
            scopes=tuple(payload.get("scopes", [])),
        )
    
    async def revoke_refresh_token(self, refresh_token_id: str) -> None:
        self._revoked_tokens.add(refresh_token_id)
    
    async def is_revoked(self, refresh_token_id: str) -> bool:
        return refresh_token_id in self._revoked_tokens
    
    async def revoke_all_user_tokens(self, user_id: str) -> None:
        """Revoke all tokens for a user (security incident)."""
        user_id_str = str(user_id) if isinstance(user_id, UUID) else user_id
        
        if user_id_str in self._user_tokens:
            for token_id in self._user_tokens[user_id_str]:
                self._revoked_tokens.add(token_id)
            self._user_tokens[user_id_str].clear()
