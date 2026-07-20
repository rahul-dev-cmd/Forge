"""Feature Flag Evaluation Service."""

from __future__ import annotations

import uuid
from typing import Any


class FeatureFlagService:
    """Evaluates global system feature flags and workspace overrides."""

    def __init__(self):
        self._flags = {
            "experimental_ai": True,
            "vector_search_v2": True,
            "streaming_events": True,
            "mcp_tools": True,
        }

    async def is_enabled(self, flag_key: str, workspace_id: uuid.UUID | str | None = None) -> bool:
        return self._flags.get(flag_key, True)


feature_flag_service = FeatureFlagService()
