# Known Gaps & Production Roadmap

## WBS 3.0 - Infrastructure Gaps

| Gap | Risk | MVP Mitigation | Production Fix | Priority |
|-----|------|----------------|----------------|----------|
| **Audit logs share profile DB pool** | Same user can modify audit logs | Append-only pattern in app code | Separate DB user with INSERT-only permissions | Medium |
| **No cross-schema transaction** | Identity saved but credential fails -> orphan record | Compensating action (delete on failure) | Saga pattern or tx outbox | High |
| **Session store in-memory** | Lost on restart | Documentation | Redis cluster | Medium |
| **Revocation store in-memory** | Lost on restart | Documentation | Redis + PostgreSQL | Medium |
| **Event bus in-memory** | Events lost on crash | Documentation | Redis Streams | Low |
| **Secret manager env-only** | Secrets in env vars | Documentation | HashiCorp Vault | Medium |

## Cross-Schema Transaction Gap - Detailed

**Problem:**

Identity saved but credential fails -> orphaned user

**Solution for MVP (Compensating Action):**

try:
    identity = await identity_repo.save(identity)
    credential = await credential_repo.save(credential)
except Exception:
    await identity_repo.delete(identity.id)
    raise

**Production Solution:** Saga pattern or transactional outbox.

## CORS Security

- **Dev default:** http://localhost:3000,http://localhost:8000
- **Production:** Must set explicit origins, no wildcard allowed
- **Enforced:** config/settings.py raises error

## Resolution Status

| Gap | Resolution | Status |
|-----|------------|--------|
| CORS wildcard | Fixed in config/settings.py | ✅ |
| Audit DB isolation | Accept for MVP; documented | ✅ |
| Cross-schema transaction | Design documented | ⏳ WBS 4.0 |
