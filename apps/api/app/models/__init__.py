from app.db.base_class import Base
from app.models.user import User, UserSettings
from app.models.organization import Organization, OrganizationMembership
from app.models.workspace import Workspace, WorkspaceMember
from app.models.project import Project, ProjectSettings
from app.models.repository import Repository, RepositorySettings
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.activity import RepositoryActivity
from app.models.invitation import OrganizationInvitation
from app.models.github import GitHubInstallation, GitHubAccountLink
from app.models.git_metadata import (
    Branch,
    Commit,
    PullRequest,
    Issue,
    Contributor,
    RepositoryLanguage,
    RepositoryTopic,
)
from app.models.sync import RepositorySync
from app.models.webhook import WebhookEvent
from app.models.checkpoints import RepositorySyncCheckpoint, GitHubRateLimit
from app.models.code_intelligence import (
    RepositorySnapshot,
    RepositoryIndex,
    IndexedFile,
    CodeSymbol,
    CodeReference,
    CodeChunk,
    ImportGraph,
    CallGraph,
    DependencyGraph,
    RepositoryMetric,
    IndexJob,
    IndexCheckpoint,
    LanguageStatistic,
)
from app.models.ai_knowledge import (
    EmbeddingJob,
    EmbeddingVersion,
    EmbeddingRecord,
    RetrievalSession,
    SearchHistory,
    KnowledgeContext,
    RepositoryKnowledge,
)
from app.models.copilot import (
    Conversation,
    ConversationMessage,
    AgentExecution,
    ToolInvocation,
    PromptTemplate,
    LLMUsage,
    ConversationSummary,
)
from app.models.collaboration import (
    WorkspaceActivity,
    RepositoryComment,
    NotificationRecord,
    WorkspaceQuota,
    FeatureFlagRecord,
)




