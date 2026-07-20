# Security Architecture and Policy — Forge

> **Project:** Forge  
> **Document:** Security Architecture & Policy  
> **Version:** 1.0.0  
> **Last Updated:** July 2026  
> **Status:** Active  
> **Target Audience:** Security Engineers, Developers, DevOps, Operations

---

## Executive Summary & Security Overview

Forge is an AI-native Project Operating System combining project management, repository synchronization, developer workflows, and AI intelligence. Because Forge interfaces directly with private software repositories, OAuth credentials, and user data, security is engineered directly into every layer of the platform architecture.

### Defense-in-Depth Model

Forge follows a **Defense-in-Depth** security philosophy across all components:

```text
+-----------------------------------------------------------------------+
|  1. Network & Edge: HTTPS/TLS 1.3, Security Headers, CORS, Firewalls |
+-----------------------------------------------------------------------+
|  2. Web Frontend: Next.js SSR, Clerk Session Auth, Zod Validation     |
+-----------------------------------------------------------------------+
|  3. API Gateway: FastAPI Middleware, Request Tracing, Rate Limiting   |
+-----------------------------------------------------------------------+
|  4. Auth & Authorization: RS256 JWKS JWTs, Hierarchical RBAC          |
+-----------------------------------------------------------------------+
|  5. Application Services: Input Validation, Sanitization, Webhooks    |
+-----------------------------------------------------------------------+
|  6. Encryption & Storage: Fernet AES-128-CBC, HMAC-SHA256, Soft Delete |
+-----------------------------------------------------------------------+
|  7. Database Layer: SQLAlchemy Parameterized ORM, UUIDs, PostgreSQL   |
+-----------------------------------------------------------------------+
|  8. Background Workers: ARQ Isolation, Idempotent Queues, Cleanups     |
+-----------------------------------------------------------------------+
```

### Core Security Guarantees

1. **Zero Raw Token Persistence**: Forge **never** stores GitHub Personal Access Tokens (PATs) or unencrypted credentials. All tokens are short-lived or encrypted at rest using authenticated Fernet encryption.
2. **Stateless Authentication**: API communication relies on signed JWTs verified against dynamic JWKS public keys.
3. **Strict Scope & Least Privilege**: Access to organizations, workspaces, and projects is governed by explicit RBAC hierarchies enforced in FastAPI dependency chains.
4. **Complete Auditability**: High-risk actions and authentication events are logged as structured JSON logs and saved to dedicated database audit trails.

---

## Authentication Architecture

Forge delegates primary identity provider management to **Clerk**, providing enterprise-grade multi-factor authentication (MFA), passwordless logins, and session management.

```text
+------+             +-------+             +-------------+             +--------------+
| User | ---------> | Clerk | ---------> | Next.js Web | ---------> |  FastAPI API |
+------+             +-------+             +-------------+             +--------------+
                       |                          |                           |
                Issues RS256 JWT           Passes Bearer              Verifies JWKS
                       |                          |                           |
                       +--------------------------+---------------------------+
```

### Clerk JWT Integration

- **Frontend**: The Next.js application (`apps/web`) leverages `@clerk/nextjs` middleware (`apps/web/src/middleware.ts`) to validate session tokens on incoming requests.
- **Backend Verification**: The FastAPI application (`apps/api`) verifies JWT tokens asynchronously in `app.dependencies.auth.get_current_user`.
- **Keys Endpoint**: Public keys are fetched from Clerk's JWKS endpoint (`settings.CLERK_JWKS_URL`) and cached in memory (`jwks_cache`).

### JWT Verification Flow

1. **Header Parsing**: The API extracts the Bearer token from the `Authorization` header (`HTTPBearer`).
2. **Key Identifier (`kid`) Matching**: Reads unverified JWT headers to extract the `kid` claim.
3. **Signature Validation**: Resolves the matching RSA public key from the cached JWKS key set (`jwt.algorithms.RSAAlgorithm.from_jwk`) and decodes the token using **RS256**.
4. **Claims Inspection**: Verifies token expiration (`exp`) and extracts the subject claim (`sub`), representing the unique Clerk User ID.
5. **User Syncing**: Resolves or auto-provisions the user record in PostgreSQL via `user_service.get_or_create_user`.

### Local Development Authentication Fallback

For local developer environments without active Clerk credentials:
- If `settings.CLERK_SECRET_KEY` uses a placeholder or a token matching `mock-token-<username>` is presented, the backend gracefully routes requests to a local mock authentication handler (`auth.py`), provisioning a mock developer profile without bypassing authentication guards on production.

---

## Authorization & Role-Based Access Control (RBAC)

Authorization in Forge is structured around a strict hierarchy enforced across **Workspaces** and **Organizations**.

### Role Hierarchy & Ranks

Defined in `apps/api/app/utils/rbac_hierarchy.py`, numeric ranks govern access level evaluation:

#### Workspace Roles (`WorkspaceRole`)

| Role | Rank | Description |
| :--- | :--- | :--- |
| **OWNER** | `5` | Full administrative control, billing, workspace deletion |
| **ADMIN** | `4` | Member management, project creation, workspace settings |
| **MANAGER** | `3` | Project management, repository linking, team assignments |
| **DEVELOPER** | `2` | Write access to projects, tasks, repository syncing |
| **VIEWER** | `1` | Read-only access to workspace resources |

#### Organization Roles (`OrganizationRole`)

| Role | Rank | Description |
| :--- | :--- | :--- |
| **OWNER** | `4` | Full organization governance |
| **ADMIN** | `3` | Organization member management and workspace management |
| **MEMBER** | `2` | Standard member access across workspaces |
| **GUEST** | `1` | Restricted guest access |

### Authorization Enforcers

RBAC checks are implemented as reusable FastAPI dependency classes (`apps/api/app/dependencies/rbac.py`):

- **`WorkspaceRoleChecker`**: Validates whether the authenticated user possesses an allowed role within the target workspace.
- **`OrgRoleChecker`**: Enforces organization-level permissions.
- **`ProjectWorkspaceRoleChecker`**: Verifies workspace membership for project-level actions by resolving the project's parent workspace.

```python
# Example endpoint enforcement in apps/api/app/api/v1/projects.py
@router.get("")
async def list_projects(
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _ = Depends(WorkspaceRoleChecker([WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MANAGER, WorkspaceRole.DEVELOPER, WorkspaceRole.VIEWER]))
):
    ...
```

### Hierarchy Rules & Mutation Constraints

- **Assignment Rule**: An actor can only assign roles strictly *below* their own rank (`assert_can_assign_workspace_role`).
- **Management Rule**: An actor can only modify or remove members whose current role rank is strictly *below* theirs (`assert_can_manage_workspace_member`).

---

## Cryptography & Credential Encryption

Forge handles sensitive credentials, including GitHub OAuth user tokens, refresh tokens, and installation access tokens. All stored secrets are encrypted at rest using authenticated symmetric encryption.

```text
+-----------------------+     SHA-256     +---------------------------+
| CREDENTIALS_ENCRYPTION| -------------> | Base64 URL-Safe Key (32b) |
|         KEY           |                 +-------------+-------------+
+-----------------------+                               |
                                                        v
                                          +---------------------------+
                                          | Fernet (AES-128-CBC +     |
                                          |        HMAC-SHA256)       |
                                          +--------------+------------+
                                                         |
+-----------------------+     Encrypt     +--------------v------------+
|  Plaintext Access Token| -------------> |  Base64 Ciphertext Token  |
+-----------------------+                 +---------------------------+
```

### Symmetric Authenticated Encryption (Fernet)

Implemented in `apps/api/app/utils/encryption.py`:

- **Algorithm**: Fernet (AES-128 in CBC mode with PKCS7 padding, signed using HMAC-SHA256 for integrity authentication).
- **Key Derivation**: Derive a 256-bit key by hashing `settings.CREDENTIALS_ENCRYPTION_KEY` using **SHA-256** (`_derive_fernet_key`), followed by URL-safe base64 encoding.
- **Protected Fields**:
  - `encrypted_user_token` (GitHub User Access Token)
  - `encrypted_access_token` (GitHub Installation Access Token)
  - `encrypted_refresh_token` (OAuth Refresh Token)

---

## GitHub Integration Security Model

Forge connects with GitHub using the **GitHub App Model** rather than user-level Personal Access Tokens (PATs), establishing a secure, limited boundary.

### GitHub App vs. PAT Model

- **Granular Scopes**: The GitHub App requests only required permissions (e.g., repository metadata, pull requests, issues, webhooks).
- **Organization Isolation**: Access is explicitly granted per installation by repository owners.
- **Token Ephemerality**: Installation tokens automatically expire after **1 hour**.

### GitHub App JWT Generation

To authenticate as the GitHub App (e.g., to request installation access tokens), Forge generates short-lived RS256 JWTs (`apps/api/app/integrations/github/app_auth.py`):
- **Algorithm**: RS256 signed using the App's Private Key PEM (`settings.GITHUB_APP_PRIVATE_KEY`).
- **Validity**: Maximum 9 minutes (`expires_in = 540`), safely within GitHub's 10-minute maximum limit.
- **Claims**: `iss` set to `settings.GITHUB_APP_ID`, `iat` set to `now - 60`.

### Webhook Signature Verification

All incoming GitHub webhooks (`apps/api/app/api/v1/webhooks.py`) are strictly verified in `apps/api/app/integrations/github/webhooks.py` before processing:

```python
def verify_webhook_signature(payload_body: bytes, signature_header: str | None) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    secret = settings.GITHUB_APP_WEBHOOK_SECRET.encode("utf-8")
    expected = hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
    received = signature_header.removeprefix("sha256=")
    # Constant-time comparison prevents timing attacks
    return hmac.compare_digest(expected, received)
```

- **Timing Attack Prevention**: Employs `hmac.compare_digest` for constant-time string comparison.
- **Replay Protection**: Webhook events are assigned UUIDs and logged in `webhook_events`. Processing tasks enforce idempotency.

---

## HTTP & API Security Hardening

### CORS Configuration

Configured via FastAPI's `CORSMiddleware` in `apps/api/app/main.py`:
- `allow_origins`: Strictly bound to `settings.CORS_ORIGINS` (defaulting to explicit local ports in dev: `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:8000`).
- Wildcards (`*`) are prohibited when `allow_credentials=True`.

### HTTP Security Headers

Production HTTP response headers configured on the Next.js edge and reverse proxy:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### Content Security Policy (CSP - Planned)

```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-...'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.clerk.com https://api.github.com; frame-ancestors 'none';
```

### Request Tracing & Correlation

Every request traversing the API pipeline is tagged with a unique request identifier (`apps/api/app/middleware/request_id.py`):
- Checks for incoming `X-Request-ID` or generates a fresh `uuid.uuid4()`.
- Binds the request ID to the current async context using Python `contextvars.ContextVar` (`request_id_var`).
- Injects `X-Request-ID` into every HTTP response header for end-to-end tracing.

### Input & Resource Validation

- **Backend (Pydantic v2)**: Schemas enforce strict type coercion, string trimming, ISO date validation, and UUID formats.
- **Frontend (Zod & React Hook Form)**: Client-side validation prevents malformed payloads prior to dispatch.
- **Pagination & Query Bounds**: Mandatory page size limits (`limit` capped at 100) prevent memory exhaustion attacks.

---

## Database Security & Data Protection

### SQL Injection Protection

Forge relies exclusively on **SQLAlchemy 2.0 Async ORM / Core query builder**, which emits parameterized SQL statements for all queries. Direct string concatenation in SQL queries is strictly prohibited. The health check (`health.py`) uses a static, parameterless query (`text("SHOW server_version")`).

### Primary Keys & Soft Deletes

- **UUID Primary Keys**: Models utilize `uuid.uuid4()` primary keys (`UUIDMixin`), eliminating sequential ID enumeration vulnerabilities.
- **Soft Deletes**: Deletions update the `deleted_at` timestamp rather than purging database records immediately, supporting data recovery and post-incident auditing.

### Database Connection Security

- Database connection strings are supplied via environment variables (`DATABASE_URL`).
- Production connections must enforce SSL mode (`sslmode=require`).
- Database connections use async connection pooling (`asyncpg`).

---

## Logging, Auditing & Monitoring

### Structured JSON Logging

Application logs are processed by a custom `JSONFormatter` (`apps/api/app/utils/logger.py`), ensuring clean ingestion by log management systems (e.g., Datadog, ELK, CloudWatch):

```json
{
  "timestamp": "2026-07-20T09:02:20.123456+00:00",
  "level": "INFO",
  "name": "forge",
  "message": "HTTP GET /api/v1/projects completed in 0.0125s with status 200",
  "request_id": "c4f8a1b2-d903-4e11-8a92-b519bd4ca0c4"
}
```

### Database Audit Trail

Critical operational events are saved to the `audit_logs` database table (`apps/api/app/models/audit_log.py`):

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key |
| `actor_id` | `UUID` | User who initiated the action (Foreign Key to `users.id`) |
| `action` | `VARCHAR(100)` | Operation name (e.g., `workspace_creation`, `role_update`) |
| `target_type` | `VARCHAR(100)` | Affected entity type (`project`, `workspace`, `user`) |
| `target_id` | `UUID` | ID of the target entity |
| `details` | `JSONB` | Context metadata payload |
| `ip_address` | `VARCHAR(50)` | Client IP address |
| `created_at` | `TIMESTAMPTZ` | Timestamp in UTC |

---

## Background Worker & Storage Security

### ARQ Background Workers

Background execution is handled by **ARQ workers** connected to Redis (`apps/api/app/workers`):

- **Queue Isolation**: Separate queues isolate workloads by risk and compute footprint:
  - `sync_queue`: Handles repository synchronization and webhooks.
  - `index_queue`: Dedicated queue for code indexing and embeddings.
  - `ai_queue`: Dedicated queue for LLM requests and agent workflows.
- **Job Timeouts & Stale Pruning**: Jobs have strict timeout limits (600 seconds). The `cleanup` cron job automatically flags stale jobs as failed after 90 minutes.
- **Idempotency**: Tasks check state flags (`SyncStatus.SYNCING`) before starting work to avoid duplicate processing.

### Repository Storage Security

- **Metadata-First Architecture**: Forge synchronizes repository metadata via GitHub APIs without requiring local repository clones for standard project management.
- **Path Traversal Prevention**: File path parameters undergo strict sanitization to prevent directory traversal (`../`) vulnerabilities.
- **Storage Permissions**: Process execution permissions are restricted to the unprivileged application service account.

---

## Current Rate Limiting & Planned Improvements

### Current Implementation

Implemented via FastAPI middleware (`apps/api/app/middleware/rate_limit.py`):
- **Algorithm**: In-memory 60-second sliding window based on client IP.
- **Limit**: Capped at `settings.RATE_LIMIT_PER_MINUTE` (default: 100 requests per minute).
- **HTTP Response**: Exceeding requests receive an `HTTP 429 Too Many Requests` status code.

### Limitations & Planned Upgrades

1. **Distributed Synchronization**: The current in-memory store is instance-local. Production deployment will migrate rate limiting to Redis (`settings.REDIS_URL`) to enforce global limits across load-balanced instances.
2. **User-Based Rate Limiting**: Limit evaluation will be updated to key off authenticated Clerk User IDs in addition to IP addresses, mitigating false positives for users sharing NAT IP gateways.

---

## Dependency & Supply Chain Security

- **Lockfile Integrity**: Dependency versions are locked using `pnpm-lock.yaml` (Node.js) and `pyproject.toml` (Python).
- **Automated Dependency Auditing**: CI workflows execute `pnpm audit` and `pip-audit` to detect known vulnerabilities in third-party packages.
- **Container Hardening**: Docker images leverage minimal base images (`python:3.13-slim`) and run container workloads under non-root users.

---

## Incident Response & Secret Rotation

In the event of a suspected credential compromise or security incident, follow these rotation procedures:

### 1. Invalidate & Rotate GitHub App Secrets
- Navigate to **GitHub Developer Settings -> GitHub Apps -> Forge**.
- Generate a new **Client Secret** and **Private Key (.pem)**.
- Update `GITHUB_APP_CLIENT_SECRET` and `GITHUB_APP_PRIVATE_KEY` in environment config.
- Revoke all old active keys.

### 2. Rotate Credentials Encryption Key
- Execute a migration script to re-encrypt `encrypted_user_token` and `encrypted_access_token` columns using a new derived key.
- Update `CREDENTIALS_ENCRYPTION_KEY` in environment variables and restart backend services.

### 3. Invalidate Active User Sessions
- Revoke session tokens directly in the **Clerk Dashboard**.
- Rotate `CLERK_SECRET_KEY` if backend compromise is suspected.

---

## Security Roadmap

```text
Near-Term (Q3 2026)             Mid-Term (Q4 2026)             Long-Term (2027)
+------------------------+      +------------------------+      +------------------------+
| - Redis Rate Limiting  | ---> | - SAST & DAST in CI    | ---> | - AI Prompt Injection  |
| - Content Security Pol.|      | - Secret Scanning      |      |   Defense Framework    |
| - PostgreSQL RLS       |      | - Dep. Vulnerability   |      | - AI Permission Layer  |
|                        |      |   Alerts (Dependabot)  |      | - Sandboxed Tool Exec. |
+------------------------+      +------------------------+      +------------------------+
```

### Near-Term Improvements
- **Distributed Redis Rate Limiting**: Migrate in-memory sliding window to a Redis-backed token bucket.
- **Content Security Policy (CSP)**: Enforce strict CSP headers across Next.js routes.
- **Row-Level Security (RLS)**: Enforce database tenant isolation directly within PostgreSQL policies.

### Mid-Term Improvements
- **Automated SAST/DAST**: Integrate static and dynamic security scanning tools into GitHub Actions CI pipelines.
- **Secret Scanning**: Implement automated secret scanning to prevent hardcoded keys from being committed.

### Long-Term AI Security Improvements
- **Prompt Injection Defense**: Guard LLM context builders against malicious user inputs embedded in repository code or issues.
- **AI Permission Layer**: Enforce user-level RBAC constraints on AI tool execution and repository mutations.
- **Sandboxed Execution**: Execute generated code and shell commands within isolated, ephemeral microVM containers.

---

## Reporting a Vulnerability

If you discover a security vulnerability in Forge, please report it responsibly:

- **Email**: `security@forge.dev` (or submit via GitHub Private Vulnerability Reporting)
- **Encryption**: You may encrypt reports using our Security PGP Key.
- **Response SLA**: We acknowledge receipt of vulnerability reports within **24 hours** and aim to provide a remediation timeline within **72 hours**.
- **Public Disclosure**: Please do not disclose vulnerabilities publicly until a fix has been released and verified.
