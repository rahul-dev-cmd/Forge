# Forge Operations & Monitoring Guide

## 1. System Architecture Overview

Forge operates as a multi-tier AI software engineering platform:
- **API Engine**: FastAPI async python service running 4 workers per replica.
- **Background Queue**: ARQ Redis task queue executing repository syncing, AST parsing, and vector embedding pipelines.
- **Databases**: PostgreSQL 16 (Relational state & index metadata), Redis 7 (Caching & job queues), Qdrant 1.7 (Vector database).

---

## 2. Health Monitoring Probes

Forge exposes granular health checking endpoints:
- `GET /health/live`: Container liveness probe.
- `GET /health/startup`: Startup probe validating PostgreSQL initialization.
- `GET /health/ready`: Deep readiness probe inspecting PostgreSQL, Redis, Qdrant, and worker queues.
- `GET /metrics`: Prometheus metrics scrape endpoint.

---

## 3. Key Performance Indicators & Benchmark Targets

| Metric | Target SLA | Scrape / Alert Threshold |
| :--- | :--- | :--- |
| **API P95 Latency** | $< 200\text{ ms}$ | $> 500\text{ ms}$ for 5 mins |
| **Semantic Search Latency** | $< 500\text{ ms}$ | $> 1000\text{ ms}$ for 5 mins |
| **AI First-Token Latency** | $< 2.0\text{ s}$ | $> 5.0\text{ s}$ for 5 mins |
| **Target Availability** | $99.9\%$ | $< 99.5\%$ over 30 days |
