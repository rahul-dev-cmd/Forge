"""Prometheus & OpenTelemetry Metrics Exporter Module."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Response

router = APIRouter(tags=["Metrics"])


class TelemetryMetrics:
    """
    In-memory Prometheus Metric Collector.
    Tracks API latency, vector search durations, LLM token counts, and cache hits.
    """

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.llm_tokens_prompt = 0
        self.llm_tokens_completion = 0
        self.vector_searches = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def record_request(self, status_code: int):
        self.request_count += 1
        if status_code >= 400:
            self.error_count += 1

    def record_tokens(self, prompt_tokens: int, completion_tokens: int):
        self.llm_tokens_prompt += prompt_tokens
        self.llm_tokens_completion += completion_tokens

    def record_cache(self, hit: bool):
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    def generate_prometheus_text(self) -> str:
        lines = [
            "# HELP forge_http_requests_total Total HTTP requests received",
            "# TYPE forge_http_requests_total counter",
            f"forge_http_requests_total {self.request_count}",
            "# HELP forge_http_errors_total Total HTTP error responses",
            "# TYPE forge_http_errors_total counter",
            f"forge_http_errors_total {self.error_count}",
            "# HELP forge_llm_prompt_tokens_total Total LLM prompt tokens consumed",
            "# TYPE forge_llm_prompt_tokens_total counter",
            f"forge_llm_prompt_tokens_total {self.llm_tokens_prompt}",
            "# HELP forge_llm_completion_tokens_total Total LLM completion tokens generated",
            "# TYPE forge_llm_completion_tokens_total counter",
            f"forge_llm_completion_tokens_total {self.llm_tokens_completion}",
            "# HELP forge_cache_hits_total Total cache hits",
            "# TYPE forge_cache_hits_total counter",
            f"forge_cache_hits_total {self.cache_hits}",
            "# HELP forge_cache_misses_total Total cache misses",
            "# TYPE forge_cache_misses_total counter",
            f"forge_cache_misses_total {self.cache_misses}",
        ]
        return "\n".join(lines) + "\n"


telemetry_metrics = TelemetryMetrics()


@router.get("/metrics")
async def metrics_endpoint():
    """Prometheus Scrape Endpoint."""
    content = telemetry_metrics.generate_prometheus_text()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")
