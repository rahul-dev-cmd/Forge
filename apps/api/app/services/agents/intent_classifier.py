"""Intent Classifier — Categorizes user queries to optimize multi-agent routing."""

from __future__ import annotations

from app.models.enums import IntentCategory, AgentType


class IntentClassifier:
    """Classifies user queries into discrete intent categories."""

    def classify_intent(self, prompt: str) -> tuple[IntentCategory, AgentType]:
        text = prompt.lower()

        if any(w in text for w in ("debug", "error", "trace", "exception", "bug", "crash", "fix error")):
            return IntentCategory.DEBUG, AgentType.DEBUG_ASSISTANT
        elif any(w in text for w in ("review", "smell", "maintainability", "refactor", "best practice", "quality")):
            return IntentCategory.REVIEW, AgentType.CODE_REVIEWER
        elif any(w in text for w in ("explain", "how does", "what is", "understand", "walkthrough")):
            return IntentCategory.EXPLAIN, AgentType.CODE_EXPLAINER
        elif any(w in text for w in ("plan", "task", "milestone", "step", "implement", "roadmap")):
            return IntentCategory.PLAN, AgentType.PLANNER
        elif any(w in text for w in ("doc", "readme", "api doc", "generate doc", "module doc")):
            return IntentCategory.DOCUMENTATION, AgentType.DOCUMENTATION_ASSISTANT
        elif any(w in text for w in ("architecture", "summary", "overview", "structure", "design")):
            return IntentCategory.ARCHITECTURE, AgentType.REPOSITORY_ANALYST

        return IntentCategory.EXPLAIN, AgentType.COORDINATOR


intent_classifier = IntentClassifier()
