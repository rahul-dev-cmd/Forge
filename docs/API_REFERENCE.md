# Forge REST API Reference

> **Project:** Forge  
> **API Version:** v1 (`/api/v1`)  
> **FastAPI Engine:** 1.0.0  
> **Last Updated:** July 2026  
> **Status:** Production / Stable

---

## 1. Overview & Architecture

Forge exposes a stateless, RESTful JSON API providing workspace governance, project operating system workflows, repository metadata synchronization, background workers, and GitHub integration.

### Base URL

```text
Development:  http://localhost:8000/api/v1
Production:   https://api.forge.dev/api/v1
```

### Versioning Policy & Endpoint Stability

Forge follows semantic versioning for the API URL path (`/api/v1`).

- **Stable Endpoints (`/api/v1/...`)**: Fully supported for production use. Backwards-incompatible changes will trigger a major version bump (`/api/v2`).
- **Experimental Endpoints**: Marked in description headers; may undergo schema refinements in minor releases.
- **Deprecated Endpoints**: Marked with a `[Deprecated]` flag in the route summary and response headers (`Deprecation: true`). Deprecated endpoints remain active for at least one major release cycle.

---

## 2. Authentication

Forge API uses stateless **Bearer Token Authentication** powered by **Clerk JWTs**.

```text
Authorization: Bearer <clerk_jwt_token>
```

### Authentication Mechanics

1. **Token Provisioning**: The client authenticates with Clerk on the frontend and receives a signed RS256 JWT session token.
2. **Request Header**: The client sends the JWT in the standard `Authorization` header on all API requests.
3. **Backend Validation**: FastAPI inspects the Bearer token using `app.dependencies.auth.get_current_user`:
   - Fetches and caches public keys from Clerk's JWKS endpoint (`https://api.clerk.com/v1/jwks`).
   - Decodes and verifies the token signature using **RS256**.
   - Validates expiration (`exp`) and subject claim (`sub`), mapping the Clerk user ID to the internal database `User` record.
4. **Token Expiration**: Clerk tokens are short-lived. Clients must automatically refresh session tokens using the Clerk client SDK before dispatching requests.
5. **Local Dev Mock Fallback**: When `CLERK_SECRET_KEY` uses placeholder credentials or a `mock-token-<username>` Bearer token is provided in dev mode, the backend resolves a local mock user profile (`auth.py`).

### Required Headers

| Header | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `Authorization` | `string` | **Required**. Bearer token containing valid Clerk JWT | `Bearer eyJhbGciOiJSUzI1NiIs...` |
| `Content-Type` | `string` | **Required** for `POST`, `PATCH`, `PUT` requests | `application/json` |
| `X-Request-ID` | `string` | *Optional*. Custom request correlation identifier | `c4f8a1b2-d903-4e11-8a92-b519bd4ca0c4` |

---

## 3. Global Response & Error Formats

### Standard Response Envelope (`ResponseEnvelope`)

All successful API responses wrap returned data inside a uniform JSON envelope (`app.utils.response.wrap_response`):

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully.",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "cursor": "eyJpZCI6ICJjNGY4YTFiMi..."
  }
}
```

- `success` (`boolean`): Always `true` for 2xx responses.
- `data` (`object` \| `array` \| `null`): Response body contents or entity payload.
- `message` (`string`): Human-readable confirmation message.
- `meta` (`object` \| `null`): Pagination metadata (populated when listing entities).

### Standard Error Response Format

Errors return standard HTTP error status codes paired with a JSON error payload:

```json
{
  "detail": "Detailed explanation of error failure condition."
}
```

Validation failures (`422 Unprocessable Entity`) return Pydantic structured errors:

```json
{
  "detail": [
    {
      "loc": ["body", "workspace_id"],
      "msg": "Input should be a valid UUID",
      "type": "uuid_parsing"
    }
  ]
}
```

### HTTP Status Code Index

| Status Code | Code Name | Description |
| :--- | :--- | :--- |
| **`200 OK`** | Success | Request succeeded and returned requested data. |
| **`201 Created`** | Resource Created | New entity successfully initialized. |
| **`202 Accepted`** | Asynchronous Queue | Action accepted and queued for worker processing. |
| **`400 Bad Request`** | Client Error | Malformed request parameters or invalid payload logic. |
| **`401 Unauthorized`** | Auth Required | Missing, invalid, or expired authentication token. |
| **`403 Forbidden`** | Permission Denied | Authenticated user has insufficient RBAC permissions. |
| **`404 Not Found`** | Not Found | Target entity does not exist or has been deleted. |
| **`409 Conflict`** | Resource Conflict | Duplicate unique key (e.g. duplicate slug or connected repo). |
| **`422 Validation Error`** | Unprocessable Entity | Payload failed Pydantic type validation or schema constraints. |
| **`429 Too Many Requests`**| Rate Limited | Request threshold exceeded. Retry after cooldown. |
| **`500 Internal Error`** | Server Error | Internal backend exception or unhandled condition. |

---

## 4. Pagination, Filtering, Sorting & Search Conventions

### Pagination

Forge APIs support both **Offset Pagination** and **Cursor Pagination**:

#### Offset Pagination (Default)
- `page` (`integer`, default: `1`, `ge=1`): Current page number.
- `limit` (`integer`, default: `20`, `ge=1`, `le=100`): Items per page.

#### Cursor Pagination (Performance / Large Lists)
- `cursor` (`string`, optional): Opaque base64 string indicating position after which items should be returned.

### Search & Filtering

- `query` (`string`, optional): Search term matched against names, slugs, or descriptions.
- Status filters: e.g. `status=active` or `sync_status=completed`.

### Sorting

- `sort_by` (`string`, default: `"updated_at"` or `"created_at"`): Field name to sort by.
- `order` (`string`, values: `"asc"` \| `"desc"`, default: `"desc"`): Sort direction.

---

## 5. Core Data Models & Schemas

### User Model

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "rahuldev@forge.com",
  "username": "rahuldev",
  "full_name": "Rahul Dev",
  "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&fit=crop",
  "clerk_id": "user_2P9...xY8",
  "created_at": "2026-07-20T08:00:00Z"
}
```

### Workspace Model

```json
{
  "id": "c4f8a1b2-d903-4e11-8a92-b519bd4ca0c4",
  "name": "Core Platform Workspace",
  "slug": "core-platform",
  "description": "Primary monorepo engineering workspace",
  "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "organization_id": "8c8e7e2b-9b52-4a11-b990-62df9684e326",
  "created_at": "2026-07-20T08:15:00Z"
}
```

### Project Model

```json
{
  "id": "d5e9b2c3-a014-4f22-9c88-e3a1f900b123",
  "workspace_id": "c4f8a1b2-d903-4e11-8a92-b519bd4ca0c4",
  "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Forge Backend API Engine",
  "slug": "forge-api-engine",
  "description": "FastAPI microservices and ARQ worker queue engine",
  "status": "active",
  "priority": "high",
  "tags": ["backend", "fastapi", "python"],
  "due_date": "2026-12-31T23:59:59Z",
  "visibility": "private",
  "is_favorite": true,
  "version": 1,
  "created_at": "2026-07-20T08:30:00Z"
}
```

---

## 6. API Modules & Endpoints Reference

---

### Module 1: Health Check

#### `GET /api/v1/health`
Performs a deep database (PostgreSQL connection & version) and cache (Redis ping) health check.

- **Auth Required**: No (Public)
- **Response `200 OK`**:
```json
{
  "api_status": "ok",
  "postgres_status": "connected",
  "postgres_version": "PostgreSQL 16.3 on x86_64-pc-linux-gnu",
  "redis_status": "connected"
}
```

---

### Module 2: Users

#### `GET /api/v1/users/me`
Retrieve authenticated user profile.

- **Auth Required**: Yes (Bearer JWT)
- **Response `200 OK`**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "email": "rahuldev@forge.com",
  "username": "rahuldev",
  "full_name": "Rahul Dev",
  "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&fit=crop",
  "clerk_id": "user_2P9...xY8",
  "created_at": "2026-07-20T08:00:00Z"
}
```

#### `PATCH /api/v1/users/me`
Update user profile details.

- **Auth Required**: Yes (Bearer JWT)
- **Request Body** (`UserUpdate`):
```json
{
  "full_name": "Rahul Dev Senior",
  "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120"
}
```
- **Response `200 OK`**: Updated `User` object.

#### `GET /api/v1/users/me/settings`
Retrieve user preference settings.

- **Auth Required**: Yes (Bearer JWT)
- **Response `200 OK`**:
```json
{
  "id": "11111111-2222-3333-4444-555555555555",
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "theme": "dark",
  "language": "en",
  "email_notifications": true
}
```

#### `PATCH /api/v1/users/me/settings`
Update theme, language, or notification settings.

- **Auth Required**: Yes (Bearer JWT)
- **Request Body** (`UserSettingsUpdate`):
```json
{
  "theme": "dark",
  "language": "en",
  "email_notifications": false
}
```

---

### Module 3: Organizations & Invitations

#### `POST /api/v1/organizations`
Create a new organization. Creator becomes Owner.

- **Auth Required**: Yes
- **Request Body**:
```json
{
  "name": "Acme Engineering",
  "slug": "acme-engineering"
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "data": {
    "id": "8c8e7e2b-9b52-4a11-b990-62df9684e326",
    "name": "Acme Engineering",
    "slug": "acme-engineering",
    "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  },
  "message": "Organization created successfully."
}
```

#### `GET /api/v1/organizations/{org_id}`
Retrieve organization details.

- **Auth Required**: Yes (Member, Admin, or Owner)

#### `DELETE /api/v1/organizations/{org_id}`
Soft delete organization.

- **Auth Required**: Yes (Owner only)

#### `POST /api/v1/invitations/organizations/{org_id}/invitations`
Invite member to organization by generating a secure invite token.

- **Auth Required**: Yes (Org Admin or Owner)
- **Request Body**:
```json
{
  "email": "developer@acme.com",
  "role": "member"
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "data": {
    "id": "77777777-8888-9999-0000-111122223333",
    "email": "developer@acme.com",
    "role": "member",
    "token": "inv_sec_8f9a2b3c4d5e6f",
    "expires_at": "2026-07-27T08:00:00Z"
  },
  "message": "Invitation sent successfully."
}
```

#### `POST /api/v1/invitations/accept`
Accept organization invitation token.

- **Auth Required**: Yes
- **Request Body**: `{"token": "inv_sec_8f9a2b3c4d5e6f"}`

---

### Module 4: Workspaces

#### `GET /api/v1/workspaces`
List workspaces where the authenticated user holds membership.

- **Auth Required**: Yes

#### `POST /api/v1/workspaces`
Initialize a new workspace.

- **Auth Required**: Yes
- **Request Body** (`WorkspaceCreate`):
```json
{
  "name": "Frontend Monorepo Workspace",
  "slug": "frontend-monorepo",
  "description": "Next.js UI & shared packages workspace",
  "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "organization_id": "8c8e7e2b-9b52-4a11-b990-62df9684e326"
}
```

#### `GET /api/v1/workspaces/{workspace_id}`
Retrieve workspace details by UUID.

- **Auth Required**: Yes (Workspace Member)

#### `PATCH /api/v1/workspaces/{workspace_id}`
Update workspace details.

- **Auth Required**: Yes (Workspace Admin or Owner)

#### `DELETE /api/v1/workspaces/{workspace_id}`
Soft delete workspace.

- **Auth Required**: Yes (Workspace Owner only)

#### `GET /api/v1/workspaces/{workspace_id}/members`
List workspace members and assigned roles.

#### `POST /api/v1/workspaces/{workspace_id}/members`
Add user member to workspace.

- **Query Parameters**: `user_id` (UUID), `role` (`"developer"`, `"manager"`, `"admin"`)
- **Auth Required**: Yes (Workspace Admin or Owner)

---

### Module 5: Projects

#### `GET /api/v1/projects`
List, filter, sort, search, and paginate projects inside a workspace.

- **Query Parameters**:
  - `workspace_id` (`UUID`, **Required**)
  - `query` (`string`, optional)
  - `status` (`string`, optional)
  - `priority` (`string`, optional)
  - `favorite` (`boolean`, optional)
  - `sort_by` (`string`, default: `"created_at"`)
  - `order` (`string`, default: `"desc"`)
  - `page` (`integer`, default: `1`)
  - `limit` (`integer`, default: `20`, max: `100`)
  - `cursor` (`string`, optional)
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": [
    {
      "id": "d5e9b2c3-a014-4f22-9c88-e3a1f900b123",
      "workspace_id": "c4f8a1b2-d903-4e11-8a92-b519bd4ca0c4",
      "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Forge Backend API Engine",
      "slug": "forge-api-engine",
      "description": "FastAPI engine",
      "status": "active",
      "priority": "high",
      "tags": ["backend", "fastapi"],
      "due_date": null,
      "visibility": "private",
      "is_favorite": true,
      "version": 1,
      "created_at": "2026-07-20T08:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "cursor": null
  }
}
```

#### `POST /api/v1/projects`
Initialize a new project within a workspace.

- **Auth Required**: Yes (Workspace Manager, Admin, or Owner)
- **Request Body** (`ProjectCreate`):
```json
{
  "name": "Forge AI Assistant Module",
  "slug": "forge-ai-assistant",
  "description": "RAG pipeline and LLM tool execution engine",
  "workspace_id": "c4f8a1b2-d903-4e11-8a92-b519bd4ca0c4",
  "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

#### `GET /api/v1/projects/{workspace_id}/{id_or_slug}`
Retrieve project details by UUID or Slug.

#### `PATCH /api/v1/projects/{project_id}`
Update project details with version checking.

#### `POST /api/v1/projects/{project_id}/archive`
Archive project.

#### `POST /api/v1/projects/{project_id}/restore`
Restore archived project to active.

#### `POST /api/v1/projects/bulk-archive`
Bulk archive multiple projects.

- **Request Body**: `{"project_ids": ["d5e9b2c3-a014-4f22-9c88-e3a1f900b123"]}`

---

### Module 6: Repositories & GitHub Integration

#### Repository Import Sequence Diagram

```mermaid
sequenceDiagram
Client->>API: POST /repositories/import
API->>GitHub: Fetch metadata & verify installation
GitHub-->>API: Repository metadata payload
API->>Database: Save repository record & status=pending
API->>Worker: Queue sync job (sync_queue)
Worker-->>Database: Run sync & update sync_status=completed
API-->>Client: 201 Created (Import started)
```

#### `GET /api/v1/repositories`
Browse imported repositories with search, filter, sort, and pagination.

- **Query Parameters**: `workspace_id` (UUID) or `project_id` (UUID), `query`, `sync_status`, `page`, `limit`

#### `POST /api/v1/repositories/import`
Import repository from GitHub App installation and queue initial sync job.

- **Auth Required**: Yes
- **Request Body** (`RepositoryImportRequest`):
```json
{
  "installation_id": "54321098",
  "github_repo_id": 987654321,
  "name": "Forge",
  "full_name": "forge-org/forge",
  "owner_login": "forge-org",
  "html_url": "https://github.com/forge-org/forge",
  "clone_url": "https://github.com/forge-org/forge.git",
  "default_branch": "main",
  "is_private": true,
  "workspace_id": "c4f8a1b2-d903-4e11-8a92-b519bd4ca0c4",
  "project_id": "d5e9b2c3-a014-4f22-9c88-e3a1f900b123"
}
```

#### `POST /api/v1/repositories/{repository_id}/sync`
> **Idempotent**: Multiple sync trigger calls while a job is running or queued return the existing active sync job rather than creating duplicate worker tasks.

Trigger sync job for repository metadata (branches, commits, pull requests, issues, contributors).

- **Auth Required**: Yes
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "sync_job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "status": "queued",
    "arq_job_id": "sync:a1b2c3d4-e5f6-7890-1234-567890abcdef"
  },
  "message": "Repository sync queued."
}
```

#### `GET /api/v1/repositories/{repository_id}/status`
Get connection and sync status, including sync history.

#### `GET /api/v1/repositories/{repository_id}/branches`
List synced Git branches.

#### `GET /api/v1/repositories/{repository_id}/commits`
List synced Git commits.

#### `GET /api/v1/repositories/{repository_id}/pull-requests`
List synced GitHub Pull Requests.

#### `GET /api/v1/repositories/{repository_id}/issues`
List synced GitHub Issues.

#### `GET /api/v1/repositories/{repository_id}/contributors`
List repository contributors.

#### `POST /api/v1/repositories/{repository_id}/disconnect`
Disconnect repository and remove integration.

#### `PATCH /api/v1/repositories/{repository_id}/settings`
Update repository settings (AI enablement, auto-sync, indexing toggle).

- **Request Body** (`RepositorySettingsUpdate`):
```json
{
  "ai_enabled": true,
  "indexing_enabled": true,
  "auto_sync": true,
  "sync_interval": 3600
}
```

---

### Module 7: GitHub App OAuth & Management

#### `POST /api/v1/github/connect`
Generate GitHub OAuth connect URL for account linking. Returns authorization URL.

#### `POST /api/v1/github/install`
Generate GitHub App installation URL or register installation ID.

#### `GET /api/v1/github/callback`
OAuth redirect callback endpoint. Forwards code/state parameters to frontend.

#### `POST /api/v1/github/complete`
Complete OAuth account linking or App installation registration.

#### `GET /api/v1/github/installations`
List registered GitHub App installations for current user.

#### `GET /api/v1/github/repositories`
List available repositories from user's GitHub App installations.

---

### Module 8: Webhooks

#### `POST /api/v1/webhooks/github`
GitHub App Webhook receiver endpoint (`apps/api/app/api/v1/webhooks.py`).

- **Auth Required**: No (Verified via HMAC-SHA256 signature header)
- **Headers**:
  - `X-Hub-Signature-256`: `sha256=<hmac_sha256_hex_digest>`
  - `X-GitHub-Delivery`: `3f8a9b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c`
  - `X-GitHub-Event`: `push` | `pull_request` | `issues` | `installation`

- **Signature Verification**: Verifies raw request body against `settings.GITHUB_APP_WEBHOOK_SECRET` using `hmac.compare_digest`.
- **Supported Events**: `installation`, `installation_repositories`, `repository`, `push`, `pull_request`, `issues`, `create`, `delete`, `release`, `ping`.
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "accepted": true,
    "event_id": "99998888-7777-6666-5555-444433332222",
    "event_type": "push"
  },
  "message": "Webhook accepted."
}
```

---

### Module 9: Notifications

#### `GET /api/v1/notifications`
List notifications for authenticated user.

- **Query Parameters**: `unread_only` (`boolean`, default: `false`), `skip` (`int`), `limit` (`int`)

#### `POST /api/v1/notifications/read-all`
Mark all unread user notifications as read.

#### `PATCH /api/v1/notifications/{notification_id}`
Toggle single notification read state.

- **Query Parameters**: `is_read` (`boolean`, default: `true`)

---

### Module 10: Activities

#### `GET /api/v1/activities/workspace/{workspace_id}`
Retrieve combined workspace activity feed (audit logs + repository sync activities).

- **Auth Required**: Yes (Workspace Viewer or higher)
- **Query Parameters**: `limit` (`int`, default: 20)

---

## 7. Rate Limiting Policy

### Current Rate Limiting (In-Memory)

- **Algorithm**: Sliding window counter (`RateLimitMiddleware`).
- **Identifier**: Client IP address (`request.client.host`).
- **Threshold**: **100 requests per minute**.
- **Header Response on Limit Exceeded**: Returns status code `429 Too Many Requests`.

### Future Rate Limiting (Redis-backed Token Bucket)

- **Storage**: Redis (`settings.REDIS_URL`).
- **Identifier**: Authenticated Clerk User ID (falling back to client IP for unauthenticated routes).
- **Threshold**: 100 requests/minute (burst buffer: 20).

---

## 8. Multi-Language Code Examples

### Example: Import Repository & Trigger Sync

#### 1. cURL

```bash
curl -X POST "http://localhost:8000/api/v1/repositories/import" \
     -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIs..." \
     -H "Content-Type: application/json" \
     -d '{
           "installation_id": "54321098",
           "github_repo_id": 987654321,
           "name": "Forge",
           "full_name": "forge-org/forge",
           "owner_login": "forge-org",
           "html_url": "https://github.com/forge-org/forge",
           "clone_url": "https://github.com/forge-org/forge.git",
           "default_branch": "main",
           "is_private": true,
           "workspace_id": "c4f8a1b2-d903-4e11-8a92-b519bd4ca0c4"
         }'
```

#### 2. JavaScript (Fetch API)

```javascript
async function importRepository(authToken, workspaceId) {
  const response = await fetch("http://localhost:8000/api/v1/repositories/import", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${authToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      installation_id: "54321098",
      github_repo_id: 987654321,
      name: "Forge",
      full_name: "forge-org/forge",
      owner_login: "forge-org",
      html_url: "https://github.com/forge-org/forge",
      clone_url: "https://github.com/forge-org/forge.git",
      default_branch: "main",
      is_private: true,
      workspace_id: workspaceId
    })
  });

  const result = await response.json();
  console.log("Import result:", result);
  return result;
}
```

#### 3. Python (Requests Library)

```python
import requests

def import_repository(auth_token: str, workspace_id: str):
    url = "http://localhost:8000/api/v1/repositories/import"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "installation_id": "54321098",
        "github_repo_id": 987654321,
        "name": "Forge",
        "full_name": "forge-org/forge",
        "owner_login": "forge-org",
        "html_url": "https://github.com/forge-org/forge",
        "clone_url": "https://github.com/forge-org/forge.git",
        "default_branch": "main",
        "is_private": True,
        "workspace_id": workspace_id
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
```
