# Site Reliability Engineering (SRE) Guide

## 1. Service Level Indicators (SLIs) & Objectives (SLOs)

- **Availability SLO**: 99.9% successful HTTP responses (`2xx` & `3xx`) over a 30-day rolling window.
- **Latency SLO**: 95% of non-AI requests resolved in under 200 ms.
- **RAG Retrieval SLO**: 95% of hybrid vector searches completed in under 500 ms.

---

## 2. Capacity Planning & Scaling Rules

- **Autoscaling Target**: Horizontal Pod Autoscaler (HPA) scales API replicas when CPU utilization exceeds 80% or memory exceeds 1.5 Gi.
- **Vector DB Scaling**: Qdrant replica shards scale horizontally on node addition.
