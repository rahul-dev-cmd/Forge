# Architecture Decision Records (ADR Log)

## ADR-001: Async Python & FastAPI for Backend API Engine
- **Status**: Accepted
- **Context**: Need high concurrency for streaming responses, webhooks, and git synchronization.
- **Decision**: Adopt FastAPI with async SQLAlchemy 2.0 and asyncpg.

## ADR-002: Modular Multi-Language Tree-Sitter AST Parsing
- **Status**: Accepted
- **Context**: Milestone 7 required language parsing without hardcoding individual parsers.
- **Decision**: Implement `ParserManager` with AST language detectors and tree-sitter fallback.

## ADR-003: Single Unified Vector Collection (`forge_vectors`) with Payload Filters
- **Status**: Accepted
- **Context**: Milestone 8 vector storage layout choices.
- **Decision**: Use a single unified Qdrant collection `forge_vectors` filtering payload by `workspace_id`, `repository_id`, and `snapshot_id`.

## ADR-004: AgentOrchestrator Execution Layer & ToolExecutor Permission Guard
- **Status**: Accepted
- **Context**: Milestone 9 AI Copilot required safe tool calling without direct DB or repository access.
- **Decision**: Enforce `AgentOrchestrator` handling retries, timeouts, and SSE streams, routing tool calls through `ToolExecutor` permission checks.
