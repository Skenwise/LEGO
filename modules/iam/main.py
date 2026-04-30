"""IAM Module Main Application - FastAPI with Hexagonal Architecture."""
from contextlib import asynccontextmanager
from typing import Optional
import os
import logging

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Core ports
from core.ports.driving import IAuthService
from core.ports.driven import (
    IIdentityRepository, ICredentialRepository, ISessionStore,
    IPasswordHasher, ITokenService, IAuditLogger, IEventBus,
    IAuthStrategyRegistry, IRevocationStore
)

# Use Cases
from core.use_cases import RegisterUser, AuthenticateUser, RefreshToken, RevokeSession

# Adapters (Implementations)
from adapters.secondary.security import Argon2PasswordHasher, JWTTokenService
from adapters.secondary.persistence.postgres.profile_schema import PostgresIdentityRepository
from adapters.secondary.persistence.postgres.auth_schema import PostgresCredentialRepository
from adapters.secondary.persistence.audit_schema import PostgresAuditLogger
from adapters.secondary.messaging import SimpleEventBus
from adapters.secondary.config import EnvSecretManager
from adapters.secondary.cache.in_memory_revocation_store import InMemoryRevocationStore
from adapters.secondary.cache.in_memory_session_store import InMemorySessionStore
from adapters.secondary.auth_strategies import LocalStrategy, StrategyRegistry

# Shared DTOs
from shared.dtos import RegisterUserDto, AuthenticateUserDto, RefreshTokenDto, RevokeSessionDto, TokenResponseDto
from shared.errors import DomainError

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
)
logger = logging.getLogger("iam")

# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
app = FastAPI(title="VaultGuard IAM", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_request_ip(request: Request) -> Optional[str]:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: Initialize database pools and dependency injection."""
    import asyncpg
    
    logger.info("Starting IAM module...")
    
    # Create database pools (dual-schema for ISO 8.27)
    app.state.profile_pool = await asyncpg.create_pool(
        os.getenv("PROFILE_DATABASE_URL", "postgresql://profile_user:profile_pass@localhost:5435/profile_db"),
        min_size=5,
        max_size=20,
    )
    app.state.auth_pool = await asyncpg.create_pool(
        os.getenv("AUTH_DATABASE_URL", "postgresql://auth_user:auth_pass@localhost:5436/auth_db"),
        min_size=5,
        max_size=20,
    )
    
    # Initialize adapters
    hasher = Argon2PasswordHasher()
    secret_manager = EnvSecretManager()
    jwt_secret = await secret_manager.get_secret("JWT_SECRET")
    jwt_refresh_secret = await secret_manager.get_secret("JWT_REFRESH_SECRET")
    token_service = JWTTokenService(jwt_secret, jwt_refresh_secret)
    
    identity_repo = PostgresIdentityRepository(app.state.profile_pool)
    credential_repo = PostgresCredentialRepository(app.state.auth_pool)
    audit_logger = PostgresAuditLogger(app.state.profile_pool)
    event_bus = SimpleEventBus()
    revocation_store = InMemoryRevocationStore()
    session_store = InMemorySessionStore()
    
    # Strategy registry
    strategy_registry = StrategyRegistry()
    strategy_registry.register(LocalStrategy(identity_repo, credential_repo, hasher))
    
    # Create use cases
    register_user = RegisterUser(
        identity_repo, credential_repo, hasher,
        token_service, audit_logger, event_bus
    )
    authenticate_user = AuthenticateUser(
        identity_repo, credential_repo, hasher,
        token_service, audit_logger, strategy_registry
    )
    refresh_token = RefreshToken(token_service, audit_logger)
    revoke_session = RevokeSession(session_store, token_service, audit_logger)
    
    # Create service implementation
    class AuthServiceImpl(IAuthService):
        async def register(self, dto: RegisterUserDto) -> TokenResponseDto:
            return await register_user.execute(dto, None)
        
        async def authenticate(self, dto: AuthenticateUserDto) -> TokenResponseDto:
            return await authenticate_user.execute(dto, None)
        
        async def refresh(self, dto: RefreshTokenDto) -> TokenResponseDto:
            return await refresh_token.execute(dto, None)
        
        async def revoke(self, user_id: str, dto: RevokeSessionDto) -> None:
            return await revoke_session.execute(user_id, dto, None)
    
    app.state.auth_service = AuthServiceImpl()
    
    logger.info("IAM module ready")
    yield
    
    # Shutdown
    await app.state.profile_pool.close()
    await app.state.auth_pool.close()
    logger.info("IAM module shutdown")


app.router.lifespan_context = lifespan


def get_auth_service(request: Request) -> IAuthService:
    """Dependency injection for FastAPI routes."""
    return request.app.state.auth_service


# ========== HEALTH ENDPOINTS ==========

@app.get("/health", tags=["observability"])
async def health():
    """Liveness probe: Is the process running?"""
    return {"status": "alive", "version": "0.1.0"}


@app.get("/health/ready", tags=["observability"])
async def ready(request: Request):
    """Readiness probe: Can this instance serve traffic?"""
    checks = {
        "profile_db": not request.app.state.profile_pool.is_closing(),
        "auth_db": not request.app.state.auth_pool.is_closing(),
        "config": bool(os.getenv("JWT_SECRET")),
    }
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    raise HTTPException(503, detail={"status": "not_ready", "checks": checks})


# ========== AUTH ENDPOINTS ==========

@app.post("/auth/register", response_model=TokenResponseDto, status_code=201, tags=["auth"])
@limiter.limit("5/minute")
async def register(
    request: Request,
    dto: RegisterUserDto,
    auth_service: IAuthService = Depends(get_auth_service),
):
    """Register a new user account."""
    try:
        return await auth_service.register(dto)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=TokenResponseDto, tags=["auth"])
@limiter.limit("10/minute")
async def login(
    request: Request,
    dto: AuthenticateUserDto,
    auth_service: IAuthService = Depends(get_auth_service),
):
    """Authenticate user and return JWT tokens."""
    try:
        return await auth_service.authenticate(dto)
    except DomainError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/auth/refresh", response_model=TokenResponseDto, tags=["auth"])
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    dto: RefreshTokenDto,
    auth_service: IAuthService = Depends(get_auth_service),
):
    """Refresh access token using refresh token."""
    try:
        return await auth_service.refresh(dto)
    except DomainError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/auth/revoke", status_code=204, tags=["auth"])
@limiter.limit("10/minute")
async def revoke(
    request: Request,
    dto: RevokeSessionDto,
    user_id: str,
    auth_service: IAuthService = Depends(get_auth_service),
):
    """Revoke a session (logout)."""
    try:
        await auth_service.revoke(user_id, dto)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
