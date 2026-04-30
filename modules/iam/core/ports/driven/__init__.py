"""Driven Ports - Called by core to interact with external systems."""
from .iidentity_repository import IIdentityRepository
from .icredential_repository import ICredentialRepository
from .isession_store import ISessionStore
from .ipassword_hasher import IPasswordHasher
from .itoken_service import ITokenService
from .iauth_strategy import IAuthStrategy, AuthResult
from .iauth_strategy_registry import IAuthStrategyRegistry
from .iaudit_logger import IAuditLogger, AuditEvent, AuditResult
from .ievent_bus import IEventBus
from .imailer import IMailer
from .isecret_manager import ISecretManagerPort
from .irevocation_store import IRevocationStore

__all__ = [
    "IIdentityRepository",
    "ICredentialRepository",
    "ISessionStore",
    "IPasswordHasher",
    "ITokenService",
    "IAuthStrategy",
    "IAuthStrategyRegistry",
    "AuthResult",
    "IAuditLogger",
    "AuditEvent",
    "AuditResult",
    "IEventBus",
    "IMailer",
    "ISecretManagerPort",
    "IRevocationStore",
]
