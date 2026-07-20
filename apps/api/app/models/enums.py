import enum

class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"
    DRAFT = "draft"

class ProjectPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RepositoryVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNAL = "internal"

class OrganizationRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class WorkspaceRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class RepositoryProvider(str, enum.Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    AZURE_DEVOPS = "azure_devops"
    LOCAL = "local"

class ActivityType(str, enum.Enum):
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_ARCHIVED = "project_archived"
    MEMBER_INVITED = "member_invited"
    MEMBER_JOINED = "member_joined"
    ROLE_CHANGED = "role_changed"
    REPOSITORY_ADDED = "repository_added"
    REPOSITORY_SYNCED = "repository_synced"
    REPOSITORY_DISCONNECTED = "repository_disconnected"
    GITHUB_CONNECTED = "github_connected"
    WORKSPACE_CREATED = "workspace_created"


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyncStatus(str, enum.Enum):
    IDLE = "idle"
    QUEUED = "queued"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"
    DISCONNECTED = "disconnected"


class SyncJobType(str, enum.Enum):
    INITIAL_IMPORT = "initial_import"
    REPOSITORY_SYNC = "repository_sync"
    WEBHOOK_PROCESSING = "webhook_processing"
    RETRY_FAILED = "retry_failed"
    PERIODIC_SYNC = "periodic_sync"
    CLEANUP = "cleanup"


class InstallationStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    EXPIRED = "expired"
    PERMISSION_REVOKED = "permission_revoked"


class WebhookProcessingStatus(str, enum.Enum):
    RECEIVED = "received"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    IGNORED = "ignored"


class PullRequestStatus(str, enum.Enum):
    OPEN = "open"
    DRAFT = "draft"
    MERGED = "merged"
    CLOSED = "closed"


class IssueStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class ConnectionStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PENDING = "pending"
    ERROR = "error"
    EXPIRED = "expired"


class IndexStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IndexJobType(str, enum.Enum):
    REPOSITORY_CLONE = "repository_clone"
    REPOSITORY_PULL = "repository_pull"
    REPOSITORY_INDEX = "repository_index"
    INCREMENTAL_INDEX = "incremental_index"
    CLEANUP_INDEX = "cleanup_index"
    REINDEX_REPOSITORY = "reindex_repository"
    CANCEL_INDEX = "cancel_index"
    RETRY_FAILED_INDEX = "retry_failed_index"


class SymbolType(str, enum.Enum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    INTERFACE = "interface"
    ENUM = "enum"
    VARIABLE = "variable"
    CONSTANT = "constant"


class ReferenceType(str, enum.Enum):
    CALL = "call"
    INSTANTIATION = "instantiation"
    INHERITANCE = "inheritance"
    IMPORT = "import"
    USAGE = "usage"


class DependencyType(str, enum.Enum):
    IMPORT = "import"
    EXPORT = "export"
    PACKAGE = "package"


class ChunkType(str, enum.Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    FILE = "file"
    BLOCK = "block"


class EmbeddingStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EmbeddingJobType(str, enum.Enum):
    REPOSITORY_EMBED = "repository_embed"
    INCREMENTAL_EMBED = "incremental_embed"
    REEMBED_REPOSITORY = "reembed_repository"
    CLEANUP_EMBEDDINGS = "cleanup_embeddings"
    REFRESH_EMBEDDINGS = "refresh_embeddings"
    CANCEL_EMBEDDING = "cancel_embedding"
    RETRY_FAILED_EMBEDDINGS = "retry_failed_embeddings"


class EmbeddingProviderType(str, enum.Enum):
    OPENAI = "openai"
    VOYAGE = "voyage"
    JINA = "jina"
    LOCAL = "local"


class SearchType(str, enum.Enum):
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    EXACT = "exact"


class AgentType(str, enum.Enum):
    COORDINATOR = "coordinator"
    REPOSITORY_ANALYST = "repository_analyst"
    CODE_EXPLAINER = "code_explainer"
    DEBUG_ASSISTANT = "debug_assistant"
    CODE_REVIEWER = "code_reviewer"
    DOCUMENTATION_ASSISTANT = "documentation_assistant"
    PLANNER = "planner"


class IntentCategory(str, enum.Enum):
    EXPLAIN = "explain"
    REVIEW = "review"
    DEBUG = "debug"
    PLAN = "plan"
    SUMMARIZE = "summarize"
    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"


class MessageSender(str, enum.Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class LLMProviderType(str, enum.Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LOCAL = "local"



