#!/usr/bin/env python3
"""Verify that core layer has no forbidden imports."""
import ast
import sys
from pathlib import Path

FORBIDDEN_IMPORTS = [
    # Frameworks & drivers
    "fastapi", "uvicorn", "asyncpg", "redis", "sqlalchemy",
    "jinja2", "requests", "httpx", "docker", "kubernetes",
    # Security-sensitive modules (must stay in adapters)
    "os",  # Prevents direct env var access in core
    "secrets",  # Cryptographic generation must be in adapters
    "hashlib",  # Use IPasswordHasher port instead
    "jwt", "jose",  # Use ITokenService port instead
]

def check_file(filepath: Path) -> list[str]:
    violations = []
    try:
        with open(filepath) as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name == forbidden or alias.name.startswith(forbidden + ".") 
                           for forbidden in FORBIDDEN_IMPORTS):
                        violations.append(f"{filepath}: imports {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(node.module == forbidden or node.module.startswith(forbidden + ".")
                           for forbidden in FORBIDDEN_IMPORTS):
                    violations.append(f"{filepath}: imports from {node.module}")
    except Exception as e:
        violations.append(f"{filepath}: parse error - {e}")
    return violations

def main():
    core_path = Path("core")
    if not core_path.exists():
        print("✅ No core directory yet - skipping verification")
        return 0
    
    violations = []
    for py_file in core_path.rglob("*.py"):
        violations.extend(check_file(py_file))
    
    if violations:
        print("❌ Hexagonal violation detected:")
        for v in violations:
            print(f"  {v}")
        print("\nCore layer must not import: " + ", ".join(FORBIDDEN_IMPORTS))
        print("\nReason: Business logic must use ports, not framework/crypto modules directly.")
        return 1
    
    print("✅ Hexagonal architecture verified - core has no forbidden imports")
    print("   - No framework imports")
    print("   - No direct os.environ access")
    print("   - No direct crypto/secrets imports")
    return 0

if __name__ == "__main__":
    sys.exit(main())
