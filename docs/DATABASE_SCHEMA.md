# DATABASE_SCHEMA.md

**Project:** Forge  
**Document:** Database Schema  
**Version:** 1.0.0  
**Status:** Draft  
**Last Updated:** July 2026  
**Owner:** Backend Team  
**Audience:** Backend Developers, Database Engineers, AI Engineers

---

# Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | July 2026 | Forge Team | Initial database architecture |

---

# Table of Contents

## Part 1 – Database Foundation

1. Database Philosophy
2. Design Principles
3. PostgreSQL Overview
4. Naming Conventions
5. UUID Strategy
6. Timestamp Strategy
7. Soft Deletes
8. Audit Fields
9. Common Data Types
10. Constraints
11. Indexing Strategy
12. Migration Strategy

---

# 1. Database Philosophy

The Forge database is designed to support an AI-native software engineering platform.

Unlike a traditional CRUD application, Forge manages repositories, AI conversations, embeddings, Git metadata, user collaboration, and repository intelligence.

The database should prioritize:

- Scalability
- Consistency
- Security
- Extensibility
- Performance
- AI-readiness

The relational database stores structured business data, while semantic vectors are stored in a dedicated vector database or PostgreSQL with pgvector.

---

## Core Objectives

The database should:

- Maintain repository integrity.
- Support multiple workspaces.
- Enable efficient AI retrieval.
- Scale to large repositories.
- Minimize duplication.
- Support future AI capabilities.

---

# 2. Design Principles

Every schema decision follows these principles.

---

## Normalization First

Data should be normalized to reduce redundancy.

Denormalization should only occur when performance benefits clearly outweigh maintenance costs.

---

## Explicit Relationships

All entity relationships must be represented using foreign keys.

Avoid implicit references through string identifiers.

---

## Immutable IDs

Primary keys never change.

Human-readable names may change.

Identifiers must remain stable.

---

## Auditability

Important entities should preserve historical information.

Repository activity should remain traceable.

---

## Multi-Workspace Ready

Every resource belongs to a workspace.

Isolation between workspaces must be enforced.

---

## AI-Aware Design

Repository data should support:

- Embeddings
- Retrieval
- Conversation history
- Tool execution
- AI analytics

without requiring major schema changes.

---

# 3. PostgreSQL Overview

Forge uses PostgreSQL as the primary relational database.

Reasons:

- ACID compliance
- Excellent indexing
- Mature ecosystem
- JSON support
- Extensions
- Full-text search
- pgvector compatibility
- SQLAlchemy support

---

## PostgreSQL Extensions

Recommended:

```
uuid-ossp
```

```
pgcrypto
```

```
pgvector
```

Future:

```
pg_trgm
```

```
btree_gin
```

---

## Storage Responsibilities

PostgreSQL stores:

- Users
- Workspaces
- Projects
- Repository metadata
- AI conversations
- Git metadata
- Permissions
- Configuration

Large binary assets should be stored externally.

---

# 4. Naming Conventions

Consistency is mandatory.

---

## Tables

Plural

Examples

```
users
repositories
projects
messages
embeddings
```

---

## Columns

snake_case

Example

```
created_at
repository_id
branch_name
```

---

## Foreign Keys

Pattern

```
<entity>_id
```

Examples

```
workspace_id

repository_id

user_id
```

---

## Primary Keys

Always

```
id
```

---

## Boolean Fields

Prefix with

```
is_

has_

can_
```

Example

```
is_private

has_embeddings

can_write
```

---

## Timestamp Fields

```
created_at

updated_at

deleted_at
```

---

## Enum Naming

```
repository_status

sync_status

job_status
```

---

# 5. UUID Strategy

Every primary entity uses UUID v4.

---

## Why UUID?

Advantages

- Globally unique
- Safe for distributed systems
- Difficult to guess
- Easier future sharding
- Independent of insertion order

---

## Applies To

Users

Workspaces

Projects

Repositories

Branches

Messages

Embeddings

Jobs

Notifications

Conversations

---

## Exceptions

Small lookup tables may use integers.

Example

```
countries

languages

frameworks
```

---

# 6. Timestamp Strategy

Every mutable table should contain:

```
created_at

updated_at
```

Optional

```
deleted_at
```

---

## Rules

created_at

Never changes.

updated_at

Automatically updated.

deleted_at

NULL unless soft deleted.

---

## Time Zone

Always store timestamps in

UTC

Application converts to local time.

---

# 7. Soft Deletes

Repositories and projects should not be permanently deleted immediately.

Instead

```
deleted_at
```

is populated.

---

## Benefits

Recovery

Audit history

Accidental deletion protection

Background cleanup

---

## Permanent Deletion

Performed only by maintenance jobs after the retention period.

---

# 8. Audit Fields

Sensitive entities should include audit information.

---

## Standard Fields

```
created_by

updated_by

deleted_by
```

Each references

```
users.id
```

---

## Benefits

Track ownership.

Improve accountability.

Support enterprise auditing.

---

# 9. Common Data Types

Forge standardizes column types.

| Purpose | Type |
|----------|------|
| ID | UUID |
| Name | VARCHAR(255) |
| Description | TEXT |
| Email | VARCHAR(255) |
| URL | TEXT |
| JSON Data | JSONB |
| Boolean | BOOLEAN |
| Timestamp | TIMESTAMPTZ |
| Counter | INTEGER |
| Large Counter | BIGINT |
| Embedding | VECTOR |
| Duration | INTEGER |
| Decimal | NUMERIC |

---

## JSONB Usage

JSONB should only be used for flexible metadata.

Examples

- AI settings
- User preferences
- Provider configuration

Avoid storing structured relational data inside JSON.

---

# 10. Constraints

The database should enforce integrity wherever possible.

---

## Primary Keys

Every table requires one.

---

## Foreign Keys

Every relationship should be enforced.

---

## Unique Constraints

Examples

```
users.email

workspaces.slug

repositories.github_id
```

---

## Check Constraints

Examples

```
rating >= 0

rating <= 5
```

```
token_count >= 0
```

---

## NOT NULL

Use whenever values are mandatory.

Avoid nullable columns unless necessary.

---

# 11. Indexing Strategy

Indexes improve query performance.

Only index frequently queried fields.

---

## Always Index

Primary Keys

Foreign Keys

Repository IDs

Workspace IDs

Created At

Updated At

Status Fields

---

## Composite Indexes

Examples

```
repository_id

branch_name
```

```
workspace_id

created_at
```

---

## Full Text Search

Future

Use PostgreSQL Full Text Search where appropriate.

Examples

Documentation

Commit Messages

Repository Notes

---

## Vector Index

Embeddings should use

```
HNSW
```

or

```
IVFFlat
```

depending on scale.

---

# 12. Migration Strategy

Database changes are managed through Alembic.

---

## Rules

Every schema change requires a migration.

Never modify production tables manually.

Review generated migrations before applying.

---

## Migration Naming

Pattern

```
YYYYMMDD_description
```

Example

```
20260718_create_users_table
```

---

## Deployment Strategy

Development

Automatic migrations

↓

Staging

Migration testing

↓

Production

Manual approval

↓

Rollback Plan

Prepared before deployment

---

## Rollback Principles

Every migration should be reversible whenever practical.

Destructive migrations require backups.

---

# Database Guiding Principles

The Forge database is designed to serve as the long-term source of truth for repositories, collaboration, Git metadata, and AI intelligence.

The schema prioritizes clarity, consistency, and scalability over premature optimization.

Every table should have a single, well-defined responsibility.

Relationships should be explicit.

Integrity should be enforced by the database whenever possible.

The schema should evolve incrementally while preserving backward compatibility and supporting future AI capabilities.

---

# End of Part 1

---

# Part 2 – Core Data Model

This section defines the primary relational entities that power Forge.

These tables represent the core business logic of the platform and serve as the foundation for repository management, authentication, collaboration, and workspace organization.

Each table is designed following the principles established in **Part 1 – Database Foundation**.

---

# Core Entity Overview

```
User
 │
 ├──────────────┐
 │              │
 ▼              ▼
Workspace   User Preferences
 │
 ├──────────────┐
 │              │
 ▼              ▼
Project     Workspace Members
 │
 ▼
Repository
 │
 ├──────────────┐
 │              │
 ▼              ▼
Branches   Repository Metadata
 │
 ├──────────────┐
 │              │
 ▼              ▼
Repository Settings
Repository Statistics
Repository Languages
Repository Frameworks
Repository Imports
Repository Sync Jobs
```

---

# 1. Users

## Purpose

Represents every authenticated user of Forge.

A user may belong to multiple workspaces and own multiple projects.

---

## Columns

| Column | Type | Constraints |
|---------|------|-------------|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE NOT NULL |
| username | VARCHAR(100) | UNIQUE |
| full_name | VARCHAR(255) | NOT NULL |
| avatar_url | TEXT | NULL |
| auth_provider | VARCHAR(50) | NOT NULL |
| provider_user_id | VARCHAR(255) | NOT NULL |
| is_active | BOOLEAN | DEFAULT TRUE |
| last_login_at | TIMESTAMPTZ | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |
| deleted_at | TIMESTAMPTZ | NULL |

---

## Relationships

One User

↓

Many Workspaces

↓

Many Projects

↓

Many Repositories

---

## Indexes

```
email
username
created_at
```

---

## Example Record

```json
{
  "id": "uuid",
  "email": "john@example.com",
  "username": "john",
  "full_name": "John Doe",
  "auth_provider": "github"
}
```

---

# 2. Workspaces

## Purpose

A workspace is the highest organizational unit inside Forge.

Everything belongs to a workspace.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| owner_id | UUID FK Users |
| name | VARCHAR(255) |
| slug | VARCHAR(100) UNIQUE |
| description | TEXT |
| logo_url | TEXT |
| plan | VARCHAR(50) |
| is_personal | BOOLEAN |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |
| deleted_at | TIMESTAMPTZ |

---

## Relationships

Workspace

↓

Many Projects

↓

Many Members

↓

Many Repositories

---

## Constraints

Slug must be unique.

Owner must exist.

---

## Indexes

```
owner_id
slug
created_at
```

---

# 3. Workspace Members

## Purpose

Defines membership and permissions inside a workspace.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| workspace_id | UUID FK |
| user_id | UUID FK |
| role | ENUM |
| joined_at | TIMESTAMPTZ |
| invited_by | UUID FK Users |

---

## Roles

```
Owner

Admin

Developer

Viewer
```

---

## Constraints

Unique

```
workspace_id

user_id
```

One user cannot join the same workspace twice.

---

# 4. Projects

## Purpose

Projects group repositories around a common product or initiative.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| workspace_id | UUID FK |
| owner_id | UUID FK |
| name | VARCHAR(255) |
| slug | VARCHAR(150) |
| description | TEXT |
| visibility | ENUM |
| status | ENUM |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |
| deleted_at | TIMESTAMPTZ |

---

## Relationships

Workspace

↓

Many Projects

↓

Many Repositories

---

## Indexes

```
workspace_id

slug
```

---

# 5. Repositories

## Purpose

Represents a connected Git repository.

This is one of the most important tables in the platform.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| project_id | UUID FK |
| workspace_id | UUID FK |
| github_id | BIGINT UNIQUE |
| provider | VARCHAR(50) |
| owner | VARCHAR(255) |
| name | VARCHAR(255) |
| full_name | VARCHAR(255) |
| default_branch | VARCHAR(100) |
| clone_url | TEXT |
| html_url | TEXT |
| is_private | BOOLEAN |
| status | ENUM |
| last_synced_at | TIMESTAMPTZ |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## Relationships

Repository

↓

Branches

↓

Metadata

↓

Settings

↓

Statistics

↓

AI Data

↓

Git Data

---

## Constraints

github_id unique.

Repository must belong to one project.

Repository belongs to one workspace.

---

## Indexes

```
workspace_id

project_id

github_id

status
```

---

# 6. Repository Branches

## Purpose

Stores tracked branches for each repository.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| name | VARCHAR(255) |
| is_default | BOOLEAN |
| latest_commit_sha | VARCHAR(64) |
| last_synced_at | TIMESTAMPTZ |
| created_at | TIMESTAMPTZ |

---

## Constraints

Unique

```
repository_id

branch_name
```

---

## Indexes

```
repository_id

name
```

---

# 7. Repository Settings

## Purpose

Stores repository-specific configuration.

---

## Columns

| Column | Type |
|---------|------|
| repository_id | UUID PK FK |
| ai_enabled | BOOLEAN |
| indexing_enabled | BOOLEAN |
| auto_sync | BOOLEAN |
| default_model | VARCHAR(100) |
| embedding_model | VARCHAR(100) |
| sync_interval | INTEGER |
| settings | JSONB |
| updated_at | TIMESTAMPTZ |

---

## Notes

One-to-one relationship.

Exactly one settings row per repository.

---

# 8. Project Settings

## Purpose

Stores project-level preferences.

---

## Columns

| Column | Type |
|---------|------|
| project_id | UUID PK FK |
| default_branch | VARCHAR(100) |
| coding_style | VARCHAR(100) |
| preferred_language | VARCHAR(100) |
| ai_enabled | BOOLEAN |
| settings | JSONB |
| updated_at | TIMESTAMPTZ |

---

# 9. User Preferences

## Purpose

Stores personalized user settings.

---

## Columns

| Column | Type |
|---------|------|
| user_id | UUID PK FK |
| theme | VARCHAR(20) |
| language | VARCHAR(20) |
| timezone | VARCHAR(100) |
| preferred_ai_model | VARCHAR(100) |
| notification_settings | JSONB |
| editor_settings | JSONB |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## One-to-One

Each user owns exactly one preferences record.

---

# 10. Notifications

## Purpose

Stores in-app notifications.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| user_id | UUID FK |
| title | VARCHAR(255) |
| message | TEXT |
| type | ENUM |
| is_read | BOOLEAN |
| metadata | JSONB |
| created_at | TIMESTAMPTZ |

---

## Indexes

```
user_id

is_read

created_at
```

---

# 11. API Keys

## Purpose

Stores encrypted API keys for AI providers and integrations.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| workspace_id | UUID FK |
| provider | VARCHAR(100) |
| encrypted_key | TEXT |
| key_last_four | VARCHAR(4) |
| is_active | BOOLEAN |
| created_by | UUID FK |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## Security

API keys must always be encrypted at rest.

Never expose plaintext values.

---

# 12. Sessions

## Purpose

Tracks active authenticated sessions.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| user_id | UUID FK |
| refresh_token_hash | TEXT |
| ip_address | INET |
| user_agent | TEXT |
| expires_at | TIMESTAMPTZ |
| created_at | TIMESTAMPTZ |

---

# 13. Repository Imports

## Purpose

Tracks repository import operations.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| source | VARCHAR(100) |
| status | ENUM |
| progress | INTEGER |
| started_at | TIMESTAMPTZ |
| completed_at | TIMESTAMPTZ |
| error_message | TEXT |

---

## Status Values

```
Pending

Running

Completed

Failed
```

---

# 14. Repository Sync Jobs

## Purpose

Tracks synchronization jobs with Git providers.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| job_status | ENUM |
| started_at | TIMESTAMPTZ |
| finished_at | TIMESTAMPTZ |
| files_changed | INTEGER |
| commits_processed | INTEGER |
| error_message | TEXT |

---

# 15. Repository Metadata

## Purpose

Stores general repository information used by AI and analytics.

---

## Columns

| Column | Type |
|---------|------|
| repository_id | UUID PK FK |
| primary_language | VARCHAR(100) |
| total_files | INTEGER |
| total_lines | BIGINT |
| total_directories | INTEGER |
| license | VARCHAR(100) |
| readme_exists | BOOLEAN |
| package_manager | VARCHAR(50) |
| updated_at | TIMESTAMPTZ |

---

# 16. Repository Languages

## Purpose

Stores detected programming languages.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| language | VARCHAR(100) |
| percentage | NUMERIC(5,2) |

---

# 17. Repository Frameworks

## Purpose

Stores detected frameworks and technologies.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| framework | VARCHAR(100) |
| version | VARCHAR(50) |
| confidence | NUMERIC(5,2) |

---

# 18. Repository Statistics

## Purpose

Stores aggregated repository metrics.

---

## Columns

| Column | Type |
|---------|------|
| repository_id | UUID PK FK |
| total_commits | INTEGER |
| total_branches | INTEGER |
| total_contributors | INTEGER |
| total_embeddings | INTEGER |
| last_analysis_at | TIMESTAMPTZ |

---

# Relationship Summary

```
User
│
├── Workspace Members
│
├── Workspaces
│
└── User Preferences

Workspace
│
├── Projects
├── Members
├── API Keys
└── Repositories

Project
│
├── Settings
└── Repositories

Repository
│
├── Branches
├── Metadata
├── Settings
├── Statistics
├── Languages
├── Frameworks
├── Imports
└── Sync Jobs
```

---

# Core Data Model Principles

- Every entity belongs to a workspace.
- UUIDs are used for all primary entities.
- Foreign keys enforce referential integrity.
- Frequently queried columns are indexed.
- One-to-one configuration tables isolate mutable settings from core entities.
- Metadata and analytics are separated from operational tables to reduce write contention and improve scalability.
- JSONB is reserved for flexible configuration, not relational data.

---

# End of Part 2

---

# Part 3 – AI Data Model

This section defines the database schema supporting Forge's AI-native capabilities.

Unlike traditional developer tools, Forge continuously analyzes repositories, builds semantic representations, retrieves relevant context, orchestrates AI workflows, and stores conversation history.

The AI data model is designed to support:

- Repository Intelligence
- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Conversation History
- Tool Execution
- Usage Analytics
- Model Evaluation
- Future Multi-Agent Systems

This layer complements—not replaces—the core relational model defined in Part 2.

---

# AI Data Architecture Overview

```
Repository
      │
      ▼
Repository Documents
      │
      ▼
Repository Chunks
      │
      ▼
Embeddings
      │
      ▼
Vector Index
      │
      ▼
Semantic Retrieval
      │
      ▼
AI Conversation
      │
      ▼
Messages
      │
      ▼
Tool Calls
      │
      ▼
Prompt Logs
      │
      ▼
Usage Analytics
```

---

# 1. Repository Documents

## Purpose

Represents every indexed document inside a repository.

A document may represent:

- Source File
- Markdown
- README
- Configuration File
- API Specification
- Documentation

Each document is chunked before embedding.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| branch_id | UUID FK |
| path | TEXT |
| file_name | VARCHAR(255) |
| extension | VARCHAR(20) |
| language | VARCHAR(100) |
| checksum | VARCHAR(128) |
| size_bytes | BIGINT |
| indexed_at | TIMESTAMPTZ |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## Constraints

Unique

```
repository_id

branch_id

path
```

---

## Indexes

```
repository_id

branch_id

path
```

---

# 2. Repository Chunks

## Purpose

Stores semantic chunks extracted from repository documents.

Chunks are the primary retrieval unit for RAG.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| document_id | UUID FK |
| chunk_index | INTEGER |
| content | TEXT |
| token_count | INTEGER |
| start_line | INTEGER |
| end_line | INTEGER |
| chunk_type | VARCHAR(100) |
| metadata | JSONB |
| created_at | TIMESTAMPTZ |

---

## Chunk Types

```
Function

Class

Interface

Component

Markdown

Configuration

API

Test

Comment
```

---

## Constraints

Unique

```
document_id

chunk_index
```

---

# 3. Embeddings

## Purpose

Stores vector representations for repository chunks.

These vectors enable semantic similarity search.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| chunk_id | UUID FK |
| embedding_model | VARCHAR(100) |
| dimensions | INTEGER |
| embedding | VECTOR |
| created_at | TIMESTAMPTZ |

---

## Notes

One embedding per chunk per embedding model.

Future versions may support multiple embedding providers.

---

## Vector Index

Recommended

```
HNSW
```

Future

```
IVFFlat
```

---

# 4. Chunk Metadata

## Purpose

Stores structured metadata for advanced retrieval.

---

## Columns

| Column | Type |
|---------|------|
| chunk_id | UUID PK FK |
| symbol_name | VARCHAR(255) |
| parent_symbol | VARCHAR(255) |
| visibility | VARCHAR(50) |
| complexity_score | NUMERIC |
| dependency_count | INTEGER |
| imports | JSONB |
| exports | JSONB |
| annotations | JSONB |

---

## Usage

Improves

- Semantic Ranking
- Repository Navigation
- Future Knowledge Graph generation

---

# 5. AI Conversations

## Purpose

Represents an AI chat session.

A conversation belongs to one repository.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| workspace_id | UUID FK |
| repository_id | UUID FK |
| user_id | UUID FK |
| title | VARCHAR(255) |
| model | VARCHAR(100) |
| context_strategy | VARCHAR(100) |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## Relationships

Conversation

↓

Messages

↓

Tool Calls

---

# 6. Conversation Messages

## Purpose

Stores every exchanged message.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| conversation_id | UUID FK |
| role | ENUM |
| content | TEXT |
| token_count | INTEGER |
| prompt_tokens | INTEGER |
| completion_tokens | INTEGER |
| latency_ms | INTEGER |
| created_at | TIMESTAMPTZ |

---

## Roles

```
System

User

Assistant

Tool
```

---

## Indexes

```
conversation_id

created_at
```

---

# 7. Conversation Summaries

## Purpose

Stores compressed summaries for long-running conversations.

Summaries reduce token usage while preserving important context.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| conversation_id | UUID FK |
| summary | TEXT |
| message_count | INTEGER |
| generated_at | TIMESTAMPTZ |

---

# 8. Prompt Logs

## Purpose

Stores the final prompts sent to the LLM.

Used for debugging, evaluation, and prompt engineering.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| conversation_id | UUID FK |
| prompt_type | VARCHAR(100) |
| prompt | TEXT |
| context_tokens | INTEGER |
| total_tokens | INTEGER |
| created_at | TIMESTAMPTZ |

---

## Security

Sensitive information should be masked before storage when appropriate.

---

# 9. AI Usage Analytics

## Purpose

Tracks aggregate AI usage.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| workspace_id | UUID FK |
| repository_id | UUID FK |
| total_requests | INTEGER |
| total_tokens | BIGINT |
| estimated_cost | NUMERIC |
| average_latency_ms | INTEGER |
| updated_at | TIMESTAMPTZ |

---

# 10. Model Usage

## Purpose

Tracks usage by AI model.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| model_name | VARCHAR(100) |
| provider | VARCHAR(100) |
| requests | INTEGER |
| prompt_tokens | BIGINT |
| completion_tokens | BIGINT |
| total_cost | NUMERIC |
| average_latency | INTEGER |

---

# 11. Tool Execution Logs

## Purpose

Logs every tool invocation during AI orchestration.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| conversation_id | UUID FK |
| tool_name | VARCHAR(100) |
| input | JSONB |
| output | JSONB |
| status | ENUM |
| execution_time_ms | INTEGER |
| created_at | TIMESTAMPTZ |

---

## Status

```
Success

Failed

Cancelled
```

---

# 12. Retrieval Logs

## Purpose

Stores retrieval operations for evaluation.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| conversation_id | UUID FK |
| query | TEXT |
| retrieved_chunks | INTEGER |
| retrieval_time_ms | INTEGER |
| reranking_time_ms | INTEGER |
| created_at | TIMESTAMPTZ |

---

# 13. Embedding Jobs

## Purpose

Tracks repository embedding generation.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| branch_id | UUID FK |
| status | ENUM |
| processed_documents | INTEGER |
| processed_chunks | INTEGER |
| started_at | TIMESTAMPTZ |
| finished_at | TIMESTAMPTZ |

---

# 14. Indexing Jobs

## Purpose

Tracks indexing operations.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| trigger | VARCHAR(100) |
| status | ENUM |
| files_indexed | INTEGER |
| duration_ms | INTEGER |
| created_at | TIMESTAMPTZ |

---

## Triggers

```
Repository Import

Manual Refresh

Webhook

Scheduled Sync
```

---

# 15. Repository Snapshots

## Purpose

Represents repository state at indexing time.

Snapshots improve consistency between Git history and AI retrieval.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| commit_sha | VARCHAR(64) |
| branch_name | VARCHAR(255) |
| indexed_documents | INTEGER |
| indexed_chunks | INTEGER |
| created_at | TIMESTAMPTZ |

---

# 16. Context Cache

## Purpose

Caches assembled retrieval context.

Reduces repeated retrieval work.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| conversation_id | UUID FK |
| query_hash | VARCHAR(128) |
| context | JSONB |
| expires_at | TIMESTAMPTZ |

---

# 17. Response Cache

## Purpose

Caches AI responses for deterministic queries.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| request_hash | VARCHAR(128) UNIQUE |
| model | VARCHAR(100) |
| response | TEXT |
| expires_at | TIMESTAMPTZ |
| created_at | TIMESTAMPTZ |

---

# AI Relationship Summary

```
Repository
│
├── Repository Documents
│     │
│     ├── Repository Chunks
│     │      │
│     │      ├── Embeddings
│     │      └── Chunk Metadata
│
├── Repository Snapshots
│
├── Embedding Jobs
│
└── Indexing Jobs

Conversation
│
├── Messages
├── Prompt Logs
├── Tool Execution Logs
├── Retrieval Logs
├── Conversation Summaries
└── Context Cache

Workspace
│
└── AI Usage Analytics
```

---

# AI Data Model Principles

- Documents are immutable until repository changes.
- Chunks are the fundamental retrieval unit.
- Embeddings remain independent of LLM providers.
- Conversations preserve complete interaction history.
- Tool executions are fully auditable.
- AI analytics are stored separately from operational data.
- Caching improves latency without becoming the system of record.
- Repository snapshots ensure reproducible AI responses tied to a specific code state.
- Every AI-related operation should be traceable, measurable, and reproducible.

---

# End of Part 3

---

# Part 4 – Git & Collaboration Data Model

This section defines the database schema responsible for Git operations, code collaboration, repository history, activity tracking, and future collaborative AI capabilities.

These tables bridge repository intelligence with developer workflows, enabling Forge to reason about repository evolution, code reviews, pull requests, and engineering activity.

The schema is designed to remain provider-agnostic while supporting GitHub, GitLab, Bitbucket, Azure DevOps, and future Git providers.

---

# Git Architecture Overview

```
Repository
     │
     ▼
Branches
     │
     ▼
Commits
     │
     ├──────────────┐
     ▼              ▼
Pull Requests   Repository Activity
     │
     ▼
Reviews
     │
     ▼
Review Comments
     │
     ▼
Code Suggestions
     │
     ▼
Code Patches

Future

Commits
     │
     ▼
Knowledge Graph
     │
     ▼
Timeline Intelligence
```

---

# 1. Git Commits

## Purpose

Stores metadata for commits synchronized from the Git provider.

The actual Git history remains in the repository.

Forge stores searchable metadata for AI reasoning.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| branch_id | UUID FK |
| commit_sha | VARCHAR(64) UNIQUE |
| parent_commit_sha | VARCHAR(64) |
| author_name | VARCHAR(255) |
| author_email | VARCHAR(255) |
| commit_message | TEXT |
| additions | INTEGER |
| deletions | INTEGER |
| changed_files | INTEGER |
| committed_at | TIMESTAMPTZ |
| synced_at | TIMESTAMPTZ |

---

## Relationships

Repository

↓

Many Commits

---

## Indexes

```
repository_id

branch_id

commit_sha

committed_at
```

---

# 2. Pull Requests (Future)

Pull request storage is reserved for post-MVP workflows and has no MVP API contract.

## Purpose

Represents pull requests imported from Git providers.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| provider_pr_id | BIGINT |
| number | INTEGER |
| title | VARCHAR(500) |
| description | TEXT |
| source_branch | VARCHAR(255) |
| target_branch | VARCHAR(255) |
| status | ENUM |
| author_id | UUID FK Users |
| merged_at | TIMESTAMPTZ |
| closed_at | TIMESTAMPTZ |
| created_at | TIMESTAMPTZ |
| updated_at | TIMESTAMPTZ |

---

## Status

```
Open

Draft

Merged

Closed
```

---

## Relationships

Pull Request

↓

Reviews

↓

Comments

↓

Suggestions

---

# 3. Pull Request Reviews (Future)

Pull request review storage is reserved for post-MVP workflows and has no MVP API contract.

## Purpose

Stores review decisions for pull requests.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| pull_request_id | UUID FK |
| reviewer_id | UUID FK Users |
| decision | ENUM |
| review_body | TEXT |
| submitted_at | TIMESTAMPTZ |

---

## Decisions

```
Approved

Changes Requested

Commented
```

---

# 4. Review Comments (Future)

Review comment storage is reserved for post-MVP pull request workflows and has no MVP API contract.

## Purpose

Stores inline review comments.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| review_id | UUID FK |
| file_path | TEXT |
| line_number | INTEGER |
| comment | TEXT |
| created_by | UUID FK Users |
| created_at | TIMESTAMPTZ |

---

## Indexes

```
review_id

file_path
```

---

# 5. Code Suggestions

## Purpose

Stores AI-generated code suggestions.

Suggestions are recommendations only and never modify repositories automatically.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| conversation_id | UUID FK |
| file_path | TEXT |
| suggestion_type | ENUM |
| description | TEXT |
| confidence_score | NUMERIC(4,2) |
| status | ENUM |
| created_by_ai | BOOLEAN |
| created_at | TIMESTAMPTZ |

---

## Suggestion Types

```
Bug Fix

Refactor

Optimization

Documentation

Security

Style

Testing
```

---

## Status

```
Pending

Accepted

Rejected

Applied
```

---

# 6. Code Patches

## Purpose

Stores generated code patches before user approval.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| suggestion_id | UUID FK |
| file_path | TEXT |
| diff | TEXT |
| lines_added | INTEGER |
| lines_removed | INTEGER |
| generated_at | TIMESTAMPTZ |

---

## Notes

Stores unified diff format.

No patch is automatically applied.

---

# 7. Repository Activity

## Purpose

Stores repository-level activity events.

Used for dashboards and analytics.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| actor_id | UUID FK Users |
| activity_type | ENUM |
| metadata | JSONB |
| created_at | TIMESTAMPTZ |

---

## Activity Types

```
Import

Sync

Branch Created

Commit Indexed

Pull Request Opened

AI Analysis

AI Review

Embedding Generated

Repository Updated
```

---

# 8. Audit Logs

## Purpose

Provides a permanent audit trail of important system actions.

Critical for security and enterprise deployments.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| workspace_id | UUID FK |
| user_id | UUID FK |
| action | VARCHAR(255) |
| resource_type | VARCHAR(100) |
| resource_id | UUID |
| ip_address | INET |
| user_agent | TEXT |
| metadata | JSONB |
| created_at | TIMESTAMPTZ |

---

## Example Actions

```
Workspace Created

Repository Imported

Repository Deleted

API Key Added

Settings Updated

AI Request Executed
```

---

# 9. User Activity

## Purpose

Tracks user interactions inside Forge.

Used for personalization, analytics, and future recommendation systems.

---

## Columns

| Column | Type |
|---------|------|
| id | UUID |
| user_id | UUID FK |
| activity | VARCHAR(255) |
| repository_id | UUID FK |
| duration_seconds | INTEGER |
| metadata | JSONB |
| created_at | TIMESTAMPTZ |

---

# Future Tables

The following tables are intentionally excluded from the MVP.

They define the planned evolution of Forge.

---

# 10. Tasks (Future)

## Purpose

Supports AI-assisted engineering task management.

Examples

- Bug Fix
- Feature Request
- Refactor
- Documentation
- Technical Debt

---

## Planned Columns

- id
- repository_id
- title
- description
- priority
- status
- assigned_to
- created_at

---

# 11. Team Collaboration (Future)

## Purpose

Supports collaborative engineering workflows.

Examples

- Shared conversations
- Pair programming
- AI collaboration sessions
- Workspace discussions

---

## Planned Columns

- id
- workspace_id
- conversation_id
- participant_id
- permissions

---

# 12. Knowledge Graph Nodes (Future)

## Purpose

Represents semantic entities extracted from repositories.

Examples

```
Class

Function

Module

API

Database Table

Interface

Component
```

---

## Planned Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| node_type | VARCHAR(100) |
| symbol_name | VARCHAR(255) |
| metadata | JSONB |

---

# 13. Knowledge Graph Edges (Future)

## Purpose

Represents relationships between repository entities.

Examples

```
Imports

Calls

References

Implements

Depends On

Uses

Overrides
```

---

## Planned Columns

| Column | Type |
|---------|------|
| id | UUID |
| source_node | UUID FK |
| target_node | UUID FK |
| relationship | VARCHAR(100) |
| weight | NUMERIC |

---

# 14. Timeline Intelligence (Future)

## Purpose

Tracks repository evolution over time.

Enables AI to answer questions like:

- When was authentication introduced?
- Which files changed most frequently?
- Which modules became more complex?
- How has the architecture evolved?

---

## Planned Columns

| Column | Type |
|---------|------|
| id | UUID |
| repository_id | UUID FK |
| commit_sha | VARCHAR(64) |
| snapshot_data | JSONB |
| generated_at | TIMESTAMPTZ |

---

# Relationship Summary

```
Repository
│
├── Branches
│      │
│      └── Commits
│
├── Pull Requests
│      │
│      ├── Reviews
│      │      │
│      │      └── Review Comments
│      │
│      └── Code Suggestions
│             │
│             └── Code Patches
│
├── Repository Activity
│
└── Audit Logs

Future

Repository
│
├── Knowledge Graph Nodes
│      │
│      └── Knowledge Graph Edges
│
├── Timeline Intelligence
│
├── Tasks
│
└── Collaboration
```

---

# Git & Collaboration Design Principles

## Git as the Source of Truth

Forge mirrors Git metadata but never replaces the Git repository itself.

---

## Human-Centered Collaboration

AI provides recommendations, while users retain full control over reviews, merges, and code modifications.

---

## Immutable History

Git commit metadata should never be modified after synchronization.

---

## Auditable Operations

Important actions—including AI-assisted suggestions, repository imports, permission changes, and administrative events—must be recorded in audit logs.

---

## Provider Agnostic

The schema abstracts Git provider details, enabling support for GitHub, GitLab, Bitbucket, Azure DevOps, and future integrations without major schema changes.

---

## Future-Ready

Knowledge Graphs, Timeline Intelligence, collaborative AI workflows, and engineering task management are planned as modular extensions rather than fundamental redesigns.

---

# End of Part 4

---

# Part 5 – Database Architecture

This section defines the overall architecture, relationships, performance strategies, security model, and operational guidelines for the Forge database.

Unlike previous sections that focused on individual tables, this section describes how the entire database functions as a unified system supporting AI-native software engineering workflows.

---

# Database Architecture Overview

```
                        Users
                          │
            ┌─────────────┴─────────────┐
            │                           │
     User Preferences           Workspace Members
            │                           │
            ▼                           ▼
                      Workspaces
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
        Projects      API Keys     Notifications
            │
            ▼
      Repositories
            │
 ┌──────────┼────────────────────────────────────┐
 ▼          ▼          ▼          ▼              ▼
Branches Metadata Settings Statistics Repository Activity
 │
 ▼
Commits
 │
 ▼
Pull Requests
 │
 ▼
Reviews
 │
 ▼
Review Comments

Repositories
 │
 ├─────────────── AI Layer ──────────────────┐
 ▼                                           ▼
Documents                              Conversations
 │                                           │
 ▼                                           ▼
Chunks                                   Messages
 │                                           │
 ▼                                           ▼
Embeddings                           Prompt Logs
 │                                           │
 ▼                                           ▼
Vector Search                     Tool Execution Logs
 │
 ▼
Context Retrieval
```

---

# 1. Entity Relationship Summary

## Core Relationships

```
User
 ├── Workspaces
 ├── User Preferences
 ├── Sessions
 └── Notifications

Workspace
 ├── Members
 ├── Projects
 ├── API Keys
 └── Repositories

Project
 ├── Settings
 └── Repositories

Repository
 ├── Branches
 ├── Metadata
 ├── Settings
 ├── Statistics
 ├── AI Data
 ├── Git Data
 └── Activity
```

---

## AI Relationships

```
Repository

↓

Documents

↓

Chunks

↓

Embeddings

↓

Semantic Search

↓

Conversation

↓

Messages

↓

Tool Calls
```

---

## Git Relationships

```
Repository

↓

Branches

↓

Commits

↓

Pull Requests

↓

Reviews

↓

Comments

↓

Suggestions
```

---

# 2. Foreign Key Strategy

Forge enforces referential integrity using explicit foreign keys.

Every relationship must be represented at the database level.

---

## Rules

- No orphaned records.
- No implicit relationships.
- Parent records must exist before child records.
- Foreign keys should be indexed.
- Cascading behavior should be explicit.

---

## Example

```
repositories.project_id

↓

projects.id
```

---

# 3. Cascade Rules

Different entities require different deletion strategies.

---

## CASCADE

Use when child records have no meaning without the parent.

Examples

```
Conversation

↓

Messages
```

```
Document

↓

Chunks

↓

Embeddings
```

---

## RESTRICT

Use when deletion would cause data loss.

Examples

```
Workspace

↓

Repositories
```

A workspace cannot be deleted while repositories still exist.

---

## SET NULL

Use for optional historical references.

Examples

```
deleted_by

updated_by
```

If a user account is removed, historical records remain.

---

## Soft Delete Preferred

Critical business entities should be soft deleted.

Examples

- Workspaces
- Projects
- Repositories
- Conversations

---

# 4. Transaction Strategy

Database operations should remain atomic.

Either every operation succeeds or none do.

---

## Example

Repository Import

```
Create Repository

↓

Create Metadata

↓

Create Settings

↓

Create Statistics

↓

Commit
```

If one operation fails:

Rollback everything.

---

## AI Operations

Conversation

↓

Message

↓

Prompt Log

↓

Tool Log

↓

Usage Metrics

Should execute inside coordinated transactions where appropriate.

---

# 5. Locking Strategy

Forge primarily relies on PostgreSQL's MVCC (Multi-Version Concurrency Control).

This minimizes blocking while supporting concurrent users.

---

## Pessimistic Locking

Reserved for rare cases such as:

- Repository synchronization
- Migration jobs
- Billing updates

---

## Optimistic Locking

Preferred for:

- User settings
- Conversations
- Repository metadata
- AI analytics

---

# 6. Index Strategy

Indexes are critical for performance.

---

## Primary Indexes

Every table includes:

```
Primary Key

Foreign Keys
```

---

## Secondary Indexes

Frequently queried columns.

Examples

```
repository_id

workspace_id

created_at

status

user_id
```

---

## Composite Indexes

Examples

```
workspace_id

created_at
```

```
repository_id

branch_name
```

```
conversation_id

created_at
```

---

## Vector Indexes

Embeddings should use

```
HNSW
```

Future

```
IVFFlat
```

depending on repository size.

---

# 7. Performance Optimization

Forge is designed for repositories ranging from small personal projects to enterprise-scale codebases.

---

## Strategies

- Proper indexing
- Query optimization
- Connection pooling
- Prepared statements
- Lazy loading
- Batch processing
- Pagination
- Incremental indexing

---

## Avoid

- N+1 queries
- Full table scans
- Excessive joins
- Large transactions

---

# 8. Partitioning Strategy

Partitioning is unnecessary for the MVP but should be considered as data grows.

---

## Candidate Tables

AI Messages

Prompt Logs

Retrieval Logs

Tool Logs

Audit Logs

Repository Activity

---

## Partition Keys

By

```
created_at
```

or

```
workspace_id
```

depending on workload.

---

# 9. Caching Strategy

The database should remain the source of truth.

Caching exists only to improve performance.

---

## Cache Candidates

Repository metadata

Workspace settings

User preferences

Context retrieval

AI responses

Repository statistics

---

## Cache Layers

Application Cache

↓

Redis

↓

PostgreSQL

---

## Cache Invalidation

Invalidate cache when:

- Repository sync completes
- Settings change
- New embeddings are generated
- AI context changes

---

# 10. Backup Strategy

Backups protect against accidental deletion and infrastructure failures.

---

## Schedule

Daily full backup

Hourly incremental backup

Point-in-time recovery enabled

---

## Backup Scope

Database

Migration history

Configuration

Indexes

Metadata

Audit logs

---

## Storage

Backups should be encrypted and stored in geographically separate locations.

---

# 11. Recovery Strategy

Recovery procedures should be regularly tested.

---

## Recovery Objectives

Recovery Time Objective (RTO)

Less than 30 minutes.

Recovery Point Objective (RPO)

Less than 15 minutes.

---

## Recovery Workflow

Restore Backup

↓

Replay WAL Logs

↓

Integrity Check

↓

Application Validation

↓

Resume Service

---

# 12. Data Retention

Different categories of data require different retention policies.

| Data Type | Retention |
|-----------|-----------|
| AI Conversations | Configurable |
| Prompt Logs | 90 Days |
| Tool Logs | 90 Days |
| Retrieval Logs | 90 Days |
| Audit Logs | 1 Year |
| Repository Activity | 1 Year |
| Sessions | Until Expiration |
| Notifications | 180 Days |

Retention periods should remain configurable for enterprise deployments.

---

# 13. Security

Security is enforced at multiple layers.

---

## Principles

Least Privilege

Workspace Isolation

Encrypted Secrets

Parameterized Queries

Role-Based Access Control

Audit Logging

---

## SQL Injection Protection

Always use ORM parameterized queries.

Never construct SQL using string concatenation.

---

## Workspace Isolation

Every query involving repositories, conversations, or AI data must validate the requesting user's workspace membership.

---

# 14. Encryption

Sensitive information must be encrypted both in transit and at rest.

---

## At Rest

- API Keys
- OAuth Tokens
- Provider Secrets

---

## In Transit

All database connections must use TLS.

---

## Passwords

Passwords should never be stored directly.

Authentication providers manage credentials, or hashes must use a strong password hashing algorithm such as Argon2 or bcrypt.

---

# 15. Sensitive Data Handling

Sensitive information should be minimized.

---

## Never Store

Plaintext API keys

Passwords

Private SSH keys

OAuth secrets

Access tokens in logs

---

## Masking

Examples

```
sk-****************9X

ghp_****************KQ
```

---

## Logging Rules

Logs should never expose:

- Secrets
- Embeddings
- Full prompts containing confidential information

---

# 16. Migration Best Practices

Schema evolution should remain predictable and reversible.

---

## Guidelines

- One logical change per migration
- Review generated SQL
- Test on staging before production
- Avoid destructive changes without backups
- Keep migrations idempotent where possible

---

## Deployment Pipeline

Development

↓

Staging

↓

Migration Validation

↓

Production

↓

Monitoring

---

# 17. Future Scaling

The database architecture should support long-term growth without requiring major redesigns.

---

## Horizontal Scaling

Future options include:

- Read replicas
- Connection pooling
- Distributed caching
- Background workers
- Dedicated vector databases
- Multi-region deployments

---

## AI Scaling

Future improvements may include:

- Separate vector storage
- Knowledge Graph databases
- Event-driven indexing
- Multi-agent coordination
- Distributed retrieval pipelines

---

# 18. Database Guiding Principles

Every future database change should follow these principles.

---

## Source of Truth

The relational database remains the authoritative source for all structured application data.

---

## Explicit Relationships

Relationships must be modeled with foreign keys rather than inferred in application code.

---

## Separation of Concerns

Operational data, AI metadata, analytics, and audit logs should remain logically separated to improve maintainability and scalability.

---

## Performance

Optimize for common access patterns before introducing complexity.

---

## Reliability

Prefer consistency and correctness over premature optimization.

---

## Security

Protect user data through encryption, least-privilege access, comprehensive auditing, and secure development practices.

---

## Scalability

Design schemas and migrations so the platform can grow from a hackathon prototype to an enterprise-grade engineering platform.

---

# Final Architecture Philosophy

Forge's database is more than a storage layer—it is the operational backbone of the platform.

The relational schema manages users, workspaces, repositories, collaboration, and Git metadata, while supporting AI-native workflows through structured repository intelligence, semantic indexing, conversation history, and analytics.

The architecture is intentionally modular. Core business entities, AI systems, Git operations, and future capabilities such as Knowledge Graphs and Timeline Intelligence are isolated into well-defined domains, allowing the platform to evolve without disruptive schema redesigns.

Every design decision emphasizes clarity, integrity, scalability, and long-term maintainability, ensuring the database remains a reliable foundation as Forge grows from an MVP into a production-ready AI software engineering platform.

---

# End of DATABASE_SCHEMA.md
