"""InMemorySessionStore - MVP session storage."""
from typing import Dict, Optional
from datetime import datetime

from core.domain.entities import Session
from core.ports.driven import ISessionStore


class InMemorySessionStore(ISessionStore):
    """In-memory session store (MVP only)."""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
    
    async def create(self, session: Session) -> Session:
        self._sessions[session.id] = session
        return session
    
    async def get(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session and session.is_expired():
            await self.revoke(session_id)
            return None
        return session
    
    async def get_by_refresh_token(self, refresh_token_id: str) -> Optional[Session]:
        for session in self._sessions.values():
            if session.refresh_token_id == refresh_token_id and not session.is_expired():
                return session
        return None
    
    async def revoke(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._sessions[session_id].revoke()
    
    async def revoke_all_for_user(self, user_id: str) -> None:
        for session in self._sessions.values():
            if session.user_id == user_id:
                session.revoke()
