# Forge Architecture

> Forge is an AI-native Project Operating System that combines project management, GitHub integration, and AI-powered software engineering into a single platform.

---

# High-Level Architecture

```text
                    +----------------------+
                    |      Browser         |
                    |   Next.js Frontend   |
                    +----------+-----------+
                               |
                               |
                     HTTPS / REST API
                               |
                               ▼
                    +----------------------+
                    |     FastAPI API      |
                    +----------+-----------+
                               |
      +------------------------+-------------------------+
      |                        |                         |
      ▼                        ▼                         ▼
 Authentication         Business Logic            GitHub Integration
    (Clerk)               Services                GitHub App API
      |                        |                         |
      +------------+-----------+-------------------------+
                   |
                   ▼
           Repository Layer
                   |
                   ▼
             PostgreSQL Database
                   |
         +---------+---------+
         |                   |
         ▼                   ▼
      Redis             Background Workers
                           (ARQ)

```

---

# Technology Stack

## Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Zustand

---

## Backend

- FastAPI
- SQLAlchemy Async
- Alembic
- PostgreSQL
- Redis
- ARQ Workers
- Pydantic v2

---

## Authentication

- Clerk
- JWT Verification
- Protected Routes
- RBAC

---

## Integrations

- GitHub App
- GitHub Webhooks

---

# Monorepo Structure

```
forge/

apps/
    web/
    api/

packages/
    ui/
    types/
    utils/

docs/

```

---

# Request Flow

```
User

↓

Next.js

↓

React Query

↓

FastAPI

↓

Service Layer

↓

Repository Layer

↓

Database

↓

Response

↓

React Query Cache

↓

UI
```

---

# Backend Architecture

```
API

↓

Dependencies

↓

Services

↓

Repositories

↓

Database
```

Each layer has a single responsibility.

## API

- Request validation
- Authentication
- Response formatting

---

## Services

Contains business logic.

Examples:

- Workspace Service
- Project Service
- GitHub Service
- Invitation Service

---

## Repository Layer

Responsible only for database access.

No business logic.

---

## Database

Stores all persistent application data.

---

# Authentication Flow

```
User

↓

Clerk

↓

JWT

↓

FastAPI Middleware

↓

Current User

↓

RBAC

↓

API Endpoint
```

---

# RBAC Flow

```
Request

↓

Current User

↓

Workspace Membership

↓

Role Check

↓

Permission Granted / Denied
```

Roles

- Owner
- Admin
- Manager
- Developer
- Viewer

---

# GitHub Integration

```
GitHub App

↓

Installation

↓

Encrypted Installation Token

↓

GitHub API

↓

Metadata

↓

Database

↓

Frontend
```

Forge never stores Personal Access Tokens.

---

# Webhook Flow

```
GitHub

↓

Webhook

↓

Signature Verification

↓

Webhook Log

↓

Queue Job

↓

Worker

↓

Database Update
```

---

# Background Worker Flow

```
Worker

↓

GitHub API

↓

Sync Metadata

↓

Store Data

↓

Update Sync Status
```

Jobs

- Initial Import
- Repository Sync
- Retry Failed Jobs
- Cleanup
- Webhook Processing

---

# Database Overview

Core Entities

```
User

↓

Workspace

↓

Organization

↓

Repository

↓

Project

↓

Activities

↓

Notifications

↓

GitHub Installation

↓

Repository Sync
```

---

# Frontend State

Server State

- React Query

Client State

- Zustand

Theme

- next-themes

Authentication

- Clerk

---

# Security

- Clerk Authentication
- JWT Verification
- Encrypted GitHub Tokens
- Signed Webhooks
- RBAC
- Input Validation
- SQL Injection Protection
- CSRF Protection
- Rate Limiting (planned)

---

# Current Milestones

✅ Monorepo

✅ Dashboard

✅ Authentication

✅ Backend

✅ Workspaces

✅ GitHub Integration

---

# Upcoming Architecture

## Code Intelligence

```
Repository

↓

Clone

↓

Parser

↓

AST

↓

Chunking

↓

Knowledge Graph
```

---

## AI Pipeline

```
Code

↓

Parser

↓

Embeddings

↓

Vector Database

↓

Retriever

↓

Context Builder

↓

LLM

↓

AI Agents
```

---

## Multi-Agent System

```
User

↓

Orchestrator

↓

Planning Agent

↓

Code Review Agent

↓

Documentation Agent

↓

Issue Agent

↓

Repository Agent

↓

Response
```

---

# Design Principles

- API First
- Modular Architecture
- Service-Oriented
- Async by Default
- Event Ready
- AI Native
- Secure by Default
- Type Safe
- Scalable
- Testable

---

# Future Roadmap

Milestone 7

- Repository Cloning
- Tree-sitter Parsing
- AST Generation
- Symbol Indexing

Milestone 8

- Embeddings
- Vector Database
- Knowledge Graph
- Semantic Search

Milestone 9

- AI Copilot
- Multi-Agent System
- RAG
- Context Builder

Milestone 10

- Real-Time Collaboration
- Monitoring
- Enterprise Features
- Production Deployment
