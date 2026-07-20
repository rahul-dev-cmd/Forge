# API_SPEC.md

**Project:** Forge  
**Document:** API Specification  
**Version:** 1.0.0  
**Status:** Implementation Contract  
**Last Updated:** July 2026  
**Owner:** Backend Team  
**Audience:** Frontend Developers, Backend Developers, AI Engineers, API Consumers

---

# Document History

| Version | Date      | Author     | Changes                                 |
| ------- | --------- | ---------- | --------------------------------------- |
| 1.0.0   | July 2026 | Forge Team | Initial MVP API implementation contract |

---

# Table of Contents

1. API Philosophy
2. Source Documents
3. Target Technology
4. MVP Boundary
5. Authentication
6. Common Conventions
7. Error Model
8. Pagination and Filtering
9. MVP Endpoint Catalogue
10. Endpoint Details
11. UI Coverage Matrix
12. Database Coverage Matrix
13. Future APIs
14. Implementation Rules
15. Open Questions

---

# 1. API Philosophy

Forge exposes a focused REST API for the MVP.

The API exists to support the approved product scope:

- Authentication state
- Project creation and access
- GitHub repository import
- Repository browsing and file editing
- Repository-aware AI chat
- AI-generated code suggestions
- Git diff review
- Commit and push
- Notifications

The API must not implement future product areas until they are promoted into the MVP contract.

---

# 2. Source Documents

This API contract is derived from:

- PRODUCT.md
- UI_UX.md
- TECHNICAL_ARCHITECTURE.md
- AI_SYSTEM.md
- DATABASE_SCHEMA.md

If implementation details conflict, API_SPEC.md is the backend contract, but it must remain consistent with the documents above.

---

# 3. Target Technology

| Area               | Technology                             |
| ------------------ | -------------------------------------- |
| Backend Framework  | FastAPI                                |
| API Style          | REST                                   |
| API Schema         | OpenAPI 3.1                            |
| Database           | PostgreSQL                             |
| ORM                | SQLAlchemy                             |
| Migrations         | Alembic                                |
| Authentication     | OAuth-backed JWT bearer authentication |
| AI Streaming       | Server-Sent Events (SSE)               |
| MVP Vector Storage | PostgreSQL with pgvector               |

---

# 4. MVP Boundary

## Included in MVP

- GitHub and Google OAuth sign-in flow with JWT-authenticated API requests
- Current user profile and user preferences
- Current workspace resolution
- Project list, creation, details, and metadata updates
- Dashboard summary
- Repository import from GitHub
- Repository import and indexing status
- Repository branch list
- Repository file tree browsing
- Repository file reading and saving
- Repository search
- AI conversations and SSE message streaming
- AI-generated code suggestions and patches
- Git diff review
- Commit approved changes
- Push committed branches
- Notifications

## Explicitly Future

The following are not MVP APIs and must not be implemented as production endpoints yet:

- Pull Request Review
- Architecture Visualization
- Project Health Dashboard
- Team Collaboration
- Tasks
- Discussions
- Timeline

---

# 5. Authentication

OAuth is handled by the authentication layer described in PRODUCT.md and TECHNICAL_ARCHITECTURE.md.

Backend API requests use JWT bearer authentication after sign-in.

```
Authorization: Bearer <jwt>
```

Every MVP endpoint requires authentication unless explicitly stated otherwise.

## Authorization Rules

- Users may access only workspaces where they are members.
- Users may access only projects in accessible workspaces.
- Users may access only repositories attached to accessible projects.
- Code changes, commits, pushes, and destructive file operations require explicit user action.
- Automatic commits, automatic pushes, automatic merges, and repository deletion are not permitted in the MVP.

---

# 6. Common Conventions

## Base Path

```
/api/v1
```

## Content Type

Requests and responses use JSON unless an endpoint explicitly streams SSE.

```
Content-Type: application/json
```

## IDs

All internal entity identifiers use UUID strings.

## Timestamps

All timestamps are ISO 8601 strings in UTC.

## Naming

JSON fields use `snake_case` to align with backend models and database naming.

---

# 7. Error Model

All errors return the same shape.

```json
{
  "error": {
    "code": "repository_not_found",
    "message": "Repository was not found.",
    "details": {}
  }
}
```

## Standard Status Codes

| Status | Meaning                           |
| ------ | --------------------------------- |
| 400    | Invalid request                   |
| 401    | Missing or invalid authentication |
| 403    | User lacks access                 |
| 404    | Resource not found                |
| 409    | Conflicting state                 |
| 422    | Validation error                  |
| 429    | Rate limit exceeded               |
| 500    | Internal server error             |

---

# 8. Pagination and Filtering

Collection endpoints use cursor pagination unless the endpoint explicitly returns a small fixed-size summary.

## Query Parameters

| Parameter | Type    | Required | Description                                         |
| --------- | ------- | -------- | --------------------------------------------------- |
| limit     | integer | No       | Maximum records to return. Default 25, maximum 100. |
| cursor    | string  | No       | Opaque pagination cursor.                           |
| q         | string  | No       | Search query where supported.                       |

## Response Shape

```json
{
  "items": [],
  "next_cursor": null
}
```

---

# 9. MVP Endpoint Catalogue

| ID           | Method | Path                                                           | Purpose                                        | Database Tables                                                                                                                                           | UI Screens / Components                                      |
| ------------ | ------ | -------------------------------------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| AUTH-01      | GET    | `/api/v1/me`                                                   | Return current user profile                    | Users, Sessions, Workspace Members, User Preferences                                                                                                      | Top Navigation, User Avatar, Settings                        |
| AUTH-02      | PATCH  | `/api/v1/me/preferences`                                       | Update current user preferences                | Users, User Preferences                                                                                                                                   | Theme Toggle, Settings, UI Preferences                       |
| AUTH-03      | POST   | `/api/v1/auth/logout`                                          | End current API session                        | Sessions, Audit Logs                                                                                                                                      | User Avatar Menu                                             |
| WORKSPACE-01 | GET    | `/api/v1/workspaces/current`                                   | Return active workspace context                | Workspaces, Workspace Members, Users                                                                                                                      | Project Switcher, Sidebar                                    |
| DASHBOARD-01 | GET    | `/api/v1/dashboard/summary`                                    | Return MVP dashboard summary                   | Users, Projects, Repositories, Repository Imports, Repository Sync Jobs, AI Conversations, Notifications, Repository Activity                             | Dashboard, Recent Projects, Activity Feed, AI Suggestions    |
| PROJECT-01   | GET    | `/api/v1/projects`                                             | List accessible projects                       | Projects, Workspaces, Workspace Members, Repositories, Repository Statistics                                                                              | Dashboard, Project Switcher                                  |
| PROJECT-02   | POST   | `/api/v1/projects`                                             | Create a project                               | Projects, Project Settings, Workspaces, Workspace Members, Audit Logs                                                                                     | Dashboard Quick Actions, Project Switcher                    |
| PROJECT-03   | GET    | `/api/v1/projects/{project_id}`                                | Return project details                         | Projects, Project Settings, Repositories, Repository Statistics                                                                                           | Project Workspace, Project Overview                          |
| PROJECT-04   | PATCH  | `/api/v1/projects/{project_id}`                                | Update project metadata                        | Projects, Project Settings, Audit Logs                                                                                                                    | Project Overview, Settings                                   |
| PROJECT-05   | GET    | `/api/v1/projects/{project_id}/activity`                       | Return project activity feed                   | Repository Activity, User Activity, AI Conversations, Repository Imports, Git Commits                                                                     | Dashboard Activity Feed, Project Workspace                   |
| REPO-01      | GET    | `/api/v1/projects/{project_id}/repositories`                   | List project repositories                      | Repositories, Repository Metadata, Repository Statistics, Repository Sync Jobs                                                                            | Dashboard, Project Workspace                                 |
| REPO-02      | POST   | `/api/v1/projects/{project_id}/repositories/import`            | Import GitHub repository                       | Repositories, Repository Imports, Repository Sync Jobs, Repository Metadata, Repository Settings, Audit Logs                                              | Dashboard Quick Actions, Empty Repository, Repository Import |
| REPO-03      | GET    | `/api/v1/repositories/{repository_id}`                         | Return repository details                      | Repositories, Repository Metadata, Repository Languages, Repository Frameworks, Repository Statistics, Repository Settings                                | Project Workspace, Repository Overview, Status Bar           |
| REPO-04      | GET    | `/api/v1/repositories/{repository_id}/import-jobs/{import_id}` | Return import status                           | Repository Imports, Repository Sync Jobs, Indexing Jobs, Embedding Jobs, Notifications                                                                    | Repository Loading, Status Bar, Toast Notifications          |
| REPO-05      | GET    | `/api/v1/repositories/{repository_id}/branches`                | List repository branches                       | Repository Branches, Repositories                                                                                                                         | Repository Explorer, Status Bar                              |
| REPO-06      | GET    | `/api/v1/repositories/{repository_id}/tree`                    | Browse repository file tree                    | Repositories, Repository Branches, Repository Documents                                                                                                   | Repository Explorer                                          |
| REPO-07      | GET    | `/api/v1/repositories/{repository_id}/files`                   | Read file content                              | Repositories, Repository Branches, Repository Documents, Repository Chunks                                                                                | Code Editor, Repository Explorer                             |
| REPO-08      | PUT    | `/api/v1/repositories/{repository_id}/files`                   | Save file content in working copy              | Repositories, Repository Branches, Repository Documents, Repository Activity, Audit Logs                                                                  | Code Editor, Status Bar                                      |
| REPO-09      | GET    | `/api/v1/repositories/{repository_id}/search`                  | Search repository files and indexed content    | Repository Documents, Repository Chunks, Embeddings, Retrieval Logs                                                                                       | Repository Search, Global Search, AI Panel                   |
| AI-01        | GET    | `/api/v1/repositories/{repository_id}/ai/conversations`        | List repository conversations                  | AI Conversations, Conversation Messages, Conversation Summaries                                                                                           | AI Panel, AI History                                         |
| AI-02        | POST   | `/api/v1/repositories/{repository_id}/ai/conversations`        | Create AI conversation                         | AI Conversations, Conversation Messages                                                                                                                   | AI Panel                                                     |
| AI-03        | GET    | `/api/v1/ai/conversations/{conversation_id}`                   | Return conversation with messages              | AI Conversations, Conversation Messages, Conversation Summaries                                                                                           | AI Panel Conversation                                        |
| AI-04        | POST   | `/api/v1/ai/conversations/{conversation_id}/messages`          | Send prompt and stream AI response             | AI Conversations, Conversation Messages, Prompt Logs, Retrieval Logs, Tool Execution Logs, AI Usage Analytics, Model Usage, Context Cache, Response Cache | AI Panel Prompt Box, Streaming AI Response                   |
| AI-05        | POST   | `/api/v1/repositories/{repository_id}/ai/code-suggestions`     | Generate code suggestion or patch              | Code Suggestions, Code Patches, AI Conversations, Conversation Messages, Tool Execution Logs, Prompt Logs                                                 | AI Panel, Code Editor, Git Diff View                         |
| AI-06        | PATCH  | `/api/v1/ai/code-suggestions/{suggestion_id}`                  | Accept, reject, or revise generated suggestion | Code Suggestions, Code Patches, Repository Activity, Audit Logs                                                                                           | Git Diff View, AI Panel                                      |
| GIT-01       | GET    | `/api/v1/repositories/{repository_id}/changes`                 | Return current working changes and diffs       | Repositories, Repository Branches, Code Patches, Repository Activity                                                                                      | Git Diff View, Status Bar                                    |
| GIT-02       | POST   | `/api/v1/repositories/{repository_id}/commits`                 | Commit approved changes                        | Git Commits, Repository Branches, Repository Activity, Audit Logs, Notifications                                                                          | Git Diff View, Commit Dialog, Toast Notifications            |
| GIT-03       | POST   | `/api/v1/repositories/{repository_id}/push`                    | Push committed branch to GitHub                | Git Commits, Repository Branches, Repository Sync Jobs, Repository Activity, Audit Logs, Notifications                                                    | Git Diff View, Status Bar, Toast Notifications               |
| NOTIFY-01    | GET    | `/api/v1/notifications`                                        | List current user notifications                | Notifications, Users                                                                                                                                      | Top Navigation, Notifications                                |
| NOTIFY-02    | PATCH  | `/api/v1/notifications/{notification_id}`                      | Mark notification read/unread                  | Notifications, Users                                                                                                                                      | Notifications, Toast Notifications                           |

---

# 10. Endpoint Details

## AUTH-01 - Get Current User

```
GET /api/v1/me
```

Returns the authenticated user, active session metadata, workspace memberships, and preferences.

**Tables:** Users, Sessions, Workspace Members, User Preferences  
**UI:** Top Navigation, User Avatar, Settings

## AUTH-02 - Update Preferences

```
PATCH /api/v1/me/preferences
```

Request:

```json
{
  "theme": "dark",
  "preferred_ai_model": "gpt-4.1",
  "editor_settings": {}
}
```

**Tables:** Users, User Preferences  
**UI:** Theme Toggle, Settings, Editor Preferences

## AUTH-03 - Logout

```
POST /api/v1/auth/logout
```

Invalidates the current API session token or refresh session.

**Tables:** Sessions, Audit Logs  
**UI:** User Avatar Menu

## WORKSPACE-01 - Current Workspace

```
GET /api/v1/workspaces/current
```

Returns the active workspace, current member role, and basic workspace metadata.

**Tables:** Workspaces, Workspace Members, Users  
**UI:** Sidebar, Project Switcher

## DASHBOARD-01 - Dashboard Summary

```
GET /api/v1/dashboard/summary
```

Returns only MVP dashboard data:

- Current project summary
- Quick action availability
- Recent projects
- Recent repository imports
- Recent AI conversations
- Recent commits
- Notifications
- Repository indexing events

This endpoint must not return project health metrics, task counts, team activity, discussion activity, or timeline intelligence in the MVP.

**Tables:** Users, Projects, Repositories, Repository Imports, Repository Sync Jobs, AI Conversations, Notifications, Repository Activity  
**UI:** Dashboard, Recent Projects, Activity Feed, AI Suggestions

## PROJECT-01 - List Projects

```
GET /api/v1/projects
```

Lists projects visible to the authenticated user.

**Tables:** Projects, Workspaces, Workspace Members, Repositories, Repository Statistics  
**UI:** Dashboard, Project Switcher

## PROJECT-02 - Create Project

```
POST /api/v1/projects
```

Request:

```json
{
  "name": "Forge",
  "description": "AI-native project operating system",
  "workspace_id": "uuid"
}
```

**Tables:** Projects, Project Settings, Workspaces, Workspace Members, Audit Logs  
**UI:** Dashboard Quick Actions, Project Switcher

## PROJECT-03 - Get Project

```
GET /api/v1/projects/{project_id}
```

Returns project metadata, repository summaries, settings, and indexing state.

**Tables:** Projects, Project Settings, Repositories, Repository Statistics  
**UI:** Project Workspace, Project Overview

## PROJECT-04 - Update Project

```
PATCH /api/v1/projects/{project_id}
```

Allows metadata updates only.

Allowed fields:

- name
- description
- visibility
- default_branch

**Tables:** Projects, Project Settings, Audit Logs  
**UI:** Project Overview, Settings

## PROJECT-05 - Project Activity

```
GET /api/v1/projects/{project_id}/activity
```

Returns recent MVP activity:

- Repository imports
- Repository indexing events
- AI conversations
- Commits
- Pushes
- Notifications

Team activity, task activity, discussions, and timeline intelligence are future.

**Tables:** Repository Activity, User Activity, AI Conversations, Repository Imports, Git Commits  
**UI:** Dashboard Activity Feed, Project Workspace

## REPO-01 - List Project Repositories

```
GET /api/v1/projects/{project_id}/repositories
```

Lists repositories attached to a project.

**Tables:** Repositories, Repository Metadata, Repository Statistics, Repository Sync Jobs  
**UI:** Dashboard, Project Workspace

## REPO-02 - Import Repository

```
POST /api/v1/projects/{project_id}/repositories/import
```

Request:

```json
{
  "provider": "github",
  "owner": "openai",
  "name": "forge",
  "default_branch": "main"
}
```

Starts repository import, clone, metadata extraction, indexing, chunking, and embedding jobs.

**Tables:** Repositories, Repository Imports, Repository Sync Jobs, Repository Metadata, Repository Settings, Audit Logs  
**UI:** Dashboard Quick Actions, Empty Repository, Repository Import

## REPO-03 - Get Repository

```
GET /api/v1/repositories/{repository_id}
```

Returns repository metadata, indexing state, language/framework summaries, and settings.

**Tables:** Repositories, Repository Metadata, Repository Languages, Repository Frameworks, Repository Statistics, Repository Settings  
**UI:** Project Workspace, Repository Overview, Status Bar

## REPO-04 - Import Status

```
GET /api/v1/repositories/{repository_id}/import-jobs/{import_id}
```

Returns repository import, indexing, and embedding progress.

**Tables:** Repository Imports, Repository Sync Jobs, Indexing Jobs, Embedding Jobs, Notifications  
**UI:** Repository Loading, Status Bar, Toast Notifications

## REPO-05 - Branches

```
GET /api/v1/repositories/{repository_id}/branches
```

Returns synchronized branches and default branch metadata.

**Tables:** Repository Branches, Repositories  
**UI:** Repository Explorer, Status Bar

## REPO-06 - File Tree

```
GET /api/v1/repositories/{repository_id}/tree?branch=main&path=src
```

Returns folders and files for the requested path.

**Tables:** Repositories, Repository Branches, Repository Documents  
**UI:** Repository Explorer

## REPO-07 - Read File

```
GET /api/v1/repositories/{repository_id}/files?branch=main&path=src/app.ts
```

Reads file content from the repository working copy and returns indexed document metadata when available.

**Tables:** Repositories, Repository Branches, Repository Documents, Repository Chunks  
**UI:** Code Editor, Repository Explorer

## REPO-08 - Save File

```
PUT /api/v1/repositories/{repository_id}/files
```

Request:

```json
{
  "branch": "main",
  "path": "src/app.ts",
  "content": "file contents"
}
```

Saves content to the temporary working copy. It does not commit or push automatically.

**Tables:** Repositories, Repository Branches, Repository Documents, Repository Activity, Audit Logs  
**UI:** Code Editor, Status Bar

## REPO-09 - Repository Search

```
GET /api/v1/repositories/{repository_id}/search?q=auth&limit=25
```

Searches indexed repository documents and chunks. Semantic ranking may use embeddings.

**Tables:** Repository Documents, Repository Chunks, Embeddings, Retrieval Logs  
**UI:** Repository Search, Global Search, AI Panel

## AI-01 - List Conversations

```
GET /api/v1/repositories/{repository_id}/ai/conversations
```

Lists conversations scoped to a repository.

**Tables:** AI Conversations, Conversation Messages, Conversation Summaries  
**UI:** AI Panel, AI History

## AI-02 - Create Conversation

```
POST /api/v1/repositories/{repository_id}/ai/conversations
```

Request:

```json
{
  "title": "Authentication flow",
  "model": "gpt-4.1",
  "context_strategy": "repository"
}
```

**Tables:** AI Conversations, Conversation Messages  
**UI:** AI Panel

## AI-03 - Get Conversation

```
GET /api/v1/ai/conversations/{conversation_id}
```

Returns conversation metadata and messages.

**Tables:** AI Conversations, Conversation Messages, Conversation Summaries  
**UI:** AI Panel Conversation

## AI-04 - Send Message

```
POST /api/v1/ai/conversations/{conversation_id}/messages
```

Streams response using SSE.

Request:

```json
{
  "content": "Explain the authentication flow.",
  "referenced_files": ["src/auth.ts"]
}
```

SSE events:

| Event               | Description                |
| ------------------- | -------------------------- |
| `message.delta`     | Partial assistant response |
| `tool.started`      | Tool execution started     |
| `tool.completed`    | Tool execution completed   |
| `message.completed` | Final assistant response   |
| `error`             | Stream failure             |

**Tables:** AI Conversations, Conversation Messages, Prompt Logs, Retrieval Logs, Tool Execution Logs, AI Usage Analytics, Model Usage, Context Cache, Response Cache  
**UI:** AI Panel Prompt Box, Streaming AI Response

## AI-05 - Generate Code Suggestion

```
POST /api/v1/repositories/{repository_id}/ai/code-suggestions
```

Request:

```json
{
  "conversation_id": "uuid",
  "instruction": "Add form validation to this file.",
  "target_files": ["src/components/Form.tsx"]
}
```

Creates a code suggestion and patch for user review. It does not apply, commit, or push changes automatically.

**Tables:** Code Suggestions, Code Patches, AI Conversations, Conversation Messages, Tool Execution Logs, Prompt Logs  
**UI:** AI Panel, Code Editor, Git Diff View

## AI-06 - Update Code Suggestion

```
PATCH /api/v1/ai/code-suggestions/{suggestion_id}
```

Request:

```json
{
  "status": "accepted"
}
```

Allowed statuses:

- accepted
- rejected
- revised

Accepted suggestions update the working copy only after explicit user action.

**Tables:** Code Suggestions, Code Patches, Repository Activity, Audit Logs  
**UI:** Git Diff View, AI Panel

## GIT-01 - Current Changes

```
GET /api/v1/repositories/{repository_id}/changes?branch=main
```

Returns working-copy changes and unified diffs.

**Tables:** Repositories, Repository Branches, Code Patches, Repository Activity  
**UI:** Git Diff View, Status Bar

## GIT-02 - Commit Changes

```
POST /api/v1/repositories/{repository_id}/commits
```

Request:

```json
{
  "branch": "main",
  "message": "feat: update authentication flow",
  "file_paths": ["src/auth.ts"]
}
```

Creates a Git commit after explicit user approval.

**Tables:** Git Commits, Repository Branches, Repository Activity, Audit Logs, Notifications  
**UI:** Git Diff View, Commit Dialog, Toast Notifications

## GIT-03 - Push Branch

```
POST /api/v1/repositories/{repository_id}/push
```

Request:

```json
{
  "branch": "main",
  "remote": "origin"
}
```

Pushes a committed branch to GitHub after explicit user approval.

**Tables:** Git Commits, Repository Branches, Repository Sync Jobs, Repository Activity, Audit Logs, Notifications  
**UI:** Git Diff View, Status Bar, Toast Notifications

## NOTIFY-01 - List Notifications

```
GET /api/v1/notifications
```

Returns current user notifications.

**Tables:** Notifications, Users  
**UI:** Top Navigation, Notifications

## NOTIFY-02 - Update Notification

```
PATCH /api/v1/notifications/{notification_id}
```

Request:

```json
{
  "is_read": true
}
```

**Tables:** Notifications, Users  
**UI:** Notifications, Toast Notifications

---

# 11. UI Coverage Matrix

| UI Surface               | MVP API Support                                          | Notes                                                                                                              |
| ------------------------ | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Landing Page             | None required                                            | Static marketing surface for MVP.                                                                                  |
| Authentication           | AUTH-01, AUTH-03                                         | OAuth initiation may be handled by auth provider integration.                                                      |
| Dashboard                | DASHBOARD-01, PROJECT-01, PROJECT-02, REPO-02, NOTIFY-01 | Project health, tasks, and team activity are future.                                                               |
| Project Workspace        | WORKSPACE-01, PROJECT-03, PROJECT-05, REPO-01, REPO-03   | Central MVP workspace.                                                                                             |
| Repository Explorer      | REPO-05, REPO-06, REPO-07, REPO-09                       | Rename, delete, create folder, and drag-and-drop are future unless implemented through REPO-08 for file save only. |
| Code Editor              | REPO-07, REPO-08, AI-05, AI-06                           | Auto-save may call REPO-08.                                                                                        |
| AI Panel                 | AI-01, AI-02, AI-03, AI-04, AI-05                        | Uses SSE for streaming responses.                                                                                  |
| Git Diff View            | AI-06, GIT-01, GIT-02, GIT-03                            | Pull request creation and review are future.                                                                       |
| Notifications            | NOTIFY-01, NOTIFY-02                                     | Supports repository, AI, commit, push, and error notifications.                                                    |
| Settings                 | AUTH-02, PROJECT-04                                      | Advanced workspace/team settings are future.                                                                       |
| Architecture View        | Future                                                   | No MVP API.                                                                                                        |
| Team Collaboration       | Future                                                   | No MVP API.                                                                                                        |
| Tasks                    | Future                                                   | No MVP API.                                                                                                        |
| Discussions              | Future                                                   | No MVP API.                                                                                                        |
| Timeline                 | Future                                                   | No MVP API.                                                                                                        |
| Project Health Dashboard | Future                                                   | No MVP API.                                                                                                        |
| Pull Request Review      | Future                                                   | No MVP API.                                                                                                        |

---

# 12. Database Coverage Matrix

| Domain                  | MVP Tables Used                                                                                                                                                                   |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Auth and User State     | Users, Sessions, User Preferences                                                                                                                                                 |
| Workspace Access        | Workspaces, Workspace Members                                                                                                                                                     |
| Projects                | Projects, Project Settings                                                                                                                                                        |
| Repository Import       | Repositories, Repository Imports, Repository Sync Jobs, Repository Metadata, Repository Settings                                                                                  |
| Repository Intelligence | Repository Documents, Repository Chunks, Chunk Metadata, Embeddings, Indexing Jobs, Embedding Jobs, Repository Snapshots                                                          |
| AI Chat                 | AI Conversations, Conversation Messages, Conversation Summaries, Prompt Logs, Retrieval Logs, Tool Execution Logs, AI Usage Analytics, Model Usage, Context Cache, Response Cache |
| Code Suggestions        | Code Suggestions, Code Patches                                                                                                                                                    |
| Git Workflow            | Repository Branches, Git Commits, Repository Activity, Audit Logs                                                                                                                 |
| Notifications           | Notifications                                                                                                                                                                     |

---

# 13. Future APIs

Future APIs are intentionally excluded from MVP implementation.

| Future Area                | Future API Shape                                                         | Database Status                                                                      | UI Status |
| -------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ | --------- |
| Pull Request Review        | `/api/v1/repositories/{repository_id}/pull-requests/*`                   | Pull request and review tables are post-MVP                                          | Future    |
| Architecture Visualization | `/api/v1/repositories/{repository_id}/architecture/*`                    | Knowledge graph tables are future                                                    | Future    |
| Project Health Dashboard   | `/api/v1/projects/{project_id}/health`                                   | No MVP health table                                                                  | Future    |
| Team Collaboration         | `/api/v1/workspaces/{workspace_id}/members/*`, `/api/v1/collaboration/*` | Team collaboration table is future; workspace membership remains core access control | Future    |
| Tasks                      | `/api/v1/tasks/*`                                                        | Tasks table is future                                                                | Future    |
| Discussions                | `/api/v1/discussions/*`                                                  | No discussion table exists yet                                                       | Future    |
| Timeline                   | `/api/v1/repositories/{repository_id}/timeline/*`                        | Timeline intelligence table is future                                                | Future    |

Future endpoints must not be scaffolded as production APIs until the corresponding product, UI, AI, and database documentation is promoted to MVP.

---

# 14. Implementation Rules

1. Implement MVP endpoints before future endpoints.
2. Every implemented route must appear in the MVP Endpoint Catalogue.
3. Every route handler must enforce workspace/project/repository access.
4. Every route handler that mutates data must write an audit or activity record when the database schema defines one.
5. AI responses must use repository retrieval where possible and must log usage, prompts, retrieval, and tool execution.
6. AI code suggestions must not write commits or push branches automatically.
7. Git commits and pushes require explicit user action.
8. API responses must use the common error model.
9. Endpoint additions require updating this document first.
10. Future APIs require product approval before implementation.

---

# 15. Open Questions

These questions must be resolved before the corresponding future APIs are promoted:

- Whether pull request creation belongs in MVP or the same future scope as Pull Request Review.
- Whether architecture visualization requires a dedicated knowledge graph schema or can start from repository chunks and metadata.
- Whether project health requires a new table or can be computed from repository statistics, indexing state, and AI coverage.
- Whether team collaboration means only workspace membership or real-time shared workflows.
- Whether discussions should be standalone or attached to conversations, projects, or repositories.
