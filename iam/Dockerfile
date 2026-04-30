# ============================================
# STAGE 1: Builder - Install dependencies
# ============================================
FROM python:3.11.9-slim-bookworm AS builder

WORKDIR /build

# Copy dependency files first (Docker layer caching)
COPY pyproject.toml .
COPY requirements.txt . 2>/dev/null || true

# Install dependencies to a temporary location
RUN pip install --no-cache-dir --prefix=/install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.7.4 \
    argon2-cffi==23.1.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[argon2]==1.7.4 \
    asyncpg==0.29.0 \
    redis==5.0.1 \
    pyotp==2.9.0 \
    qrcode==7.4.2 \
    prometheus-client==0.19.0 \
    python-multipart==0.0.6 \
    slowapi==0.1.9

# Copy application code
COPY . .

# Compile Python bytecode (faster startup)
RUN python -m compileall -q /build || true

# ============================================
# STAGE 2: Runtime - Distroless (No shell!)
# ============================================
FROM gcr.io/distroless/python3-debian12:nonroot

LABEL maintainer="VaultGuard Team"
LABEL module="iam"
LABEL version="0.1.0"

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --from=builder /build /app

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user
USER nonroot

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["/usr/local/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
