"""Configuration Loader - 12-Factor App with environment-specific enforcement."""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DatabaseConfig:
    """Database configuration for a specific schema."""
    url: str
    min_pool_size: int = 5
    max_pool_size: int = 20
    
    @classmethod
    def from_env(cls, prefix: str) -> "DatabaseConfig":
        url = os.getenv(f"{prefix}_DATABASE_URL")
        if not url:
            raise ValueError(f"Missing {prefix}_DATABASE_URL")
        return cls(
            url=url,
            min_pool_size=int(os.getenv(f"{prefix}_POOL_MIN", "5")),
            max_pool_size=int(os.getenv(f"{prefix}_POOL_MAX", "20")),
        )


@dataclass
class JWTSettings:
    secret_key: str
    refresh_secret_key: str
    key_id: str
    access_ttl_minutes: int = 15
    refresh_ttl_days: int = 7
    algorithm: str = "HS256"
    
    @classmethod
    def from_env(cls, env: str = "dev") -> "JWTSettings":
        key_id = os.getenv("JWT_KEY_ID", "kid_v1")
        
        if env == "production":
            secret_key = cls._read_secret_file("/run/secrets/jwt_secret")
            refresh_secret_key = cls._read_secret_file("/run/secrets/jwt_refresh_secret")
        else:
            secret_key = os.getenv("JWT_SECRET")
            refresh_secret_key = os.getenv("JWT_REFRESH_SECRET")
        
        if not secret_key or not refresh_secret_key:
            raise ValueError("JWT secrets missing")
        
        return cls(
            secret_key=secret_key,
            refresh_secret_key=refresh_secret_key,
            key_id=key_id,
            access_ttl_minutes=int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15")),
            refresh_ttl_days=int(os.getenv("JWT_REFRESH_TTL_DAYS", "7")),
        )
    
    @staticmethod
    def _read_secret_file(path: str) -> str:
        secret_path = Path(path)
        if not secret_path.exists():
            raise ValueError(f"Secret file not found: {path}")
        return secret_path.read_text().strip()


@dataclass
class LoggingConfig:
    level: str
    format: str
    
    @classmethod
    def from_env(cls) -> "LoggingConfig":
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "json"),
        )


def parse_cors_origins(origins_str: str, env: str) -> List[str]:
    """Parse CORS origins with production safety - NO wildcards in production!"""
    origins = [o.strip() for o in origins_str.split(",")]
    
    # Production: NO wildcards allowed
    if env == "production" and "*" in origins:
        raise ValueError(
            "CORS_ORIGINS cannot be '*' in production. "
            "Specify exact origins: http://app.example.com,https://app.example.com"
        )
    
    # Development: provide safe defaults
    if env == "dev" and origins == ["*"]:
        return ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
    
    return origins


@dataclass
class Settings:
    env: str
    version: str
    profile_db: DatabaseConfig
    auth_db: DatabaseConfig
    jwt: JWTSettings
    logging: LoggingConfig
    cors_origins: List[str]
    mfa_enabled: bool
    
    @classmethod
    def load(cls) -> "Settings":
        env = os.getenv("ENVIRONMENT", "dev")
        version = os.getenv("APP_VERSION", "0.1.0")
        
        cors_origins_str = os.getenv("CORS_ORIGINS", "*")
        cors_origins = parse_cors_origins(cors_origins_str, env)
        
        return cls(
            env=env,
            version=version,
            profile_db=DatabaseConfig.from_env("PROFILE"),
            auth_db=DatabaseConfig.from_env("AUTH"),
            jwt=JWTSettings.from_env(env),
            logging=LoggingConfig.from_env(),
            cors_origins=cors_origins,
            mfa_enabled=os.getenv("MFA_ENABLED", "false").lower() == "true",
        )
    
    def validate(self) -> None:
        if self.env == "production":
            if "localhost" in self.profile_db.url or "localhost" in self.auth_db.url:
                raise ValueError("Production: cannot use localhost database URLs")
        
        print(f"✅ Configuration loaded: env={self.env}, version={self.version}")
        print(f"   CORS origins: {self.cors_origins}")


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings.load()
        _settings.validate()
    return _settings
