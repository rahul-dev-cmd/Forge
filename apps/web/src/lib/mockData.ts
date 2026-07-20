export interface Project {
  id: string;
  name: string;
  description: string;
  progress: number;
  status: "active" | "completed" | "on_hold";
  priority: "high" | "medium" | "low";
  lastUpdated: string;
  repository: string;
  branch: string;
  teamMembers: string[];
  openIssues: number;
  pullRequests: number;
  aiTasks: number;
  linesOfCode: string;
  testCoverage: string;
  productivityScore: number;
}

export interface Activity {
  id: string;
  message: string;
  time: string;
  author: string;
  type: "ai" | "commit" | "sync" | "documentation" | "sprint";
}

export interface AIInsight {
  id: string;
  severity: "critical" | "warning" | "info";
  suggestion: string;
  description: string;
  recommendedAction: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
  type: "warning" | "info" | "success";
}

export interface FileNode {
  name: string;
  type: "file" | "directory";
  children?: FileNode[];
  size?: string;
  lastUpdated?: string;
}

export const MOCK_PROJECTS: Project[] = [
  {
    id: "forge-core",
    name: "Forge Core Workspace",
    description: "Repository-aware AI agentic assistant engine executing workspace workflows.",
    progress: 78,
    status: "active",
    priority: "high",
    lastUpdated: "5 mins ago",
    repository: "github.com/active-workspace/forge-monorepo",
    branch: "main",
    teamMembers: ["RD", "RK", "SL"],
    openIssues: 12,
    pullRequests: 3,
    aiTasks: 8,
    linesOfCode: "45.2k",
    testCoverage: "88.4%",
    productivityScore: 94,
  },
  {
    id: "api-gateway",
    name: "Internal API Platform",
    description: "FastAPI-based orchestrator proxy route management for agent integrations.",
    progress: 92,
    status: "completed",
    priority: "medium",
    lastUpdated: "2 hours ago",
    repository: "github.com/active-workspace/api-backend",
    branch: "main",
    teamMembers: ["RK", "AM"],
    openIssues: 0,
    pullRequests: 0,
    aiTasks: 0,
    linesOfCode: "18.7k",
    testCoverage: "94.1%",
    productivityScore: 98,
  },
  {
    id: "auth-module",
    name: "OAuth & Security Agent",
    description: "Multi-tenant auth handler and token synchronization with cryptographic validation.",
    progress: 45,
    status: "active",
    priority: "high",
    lastUpdated: "1 day ago",
    repository: "github.com/active-workspace/forge-auth",
    branch: "feature/jwt-rotation",
    teamMembers: ["RD", "AM"],
    openIssues: 22,
    pullRequests: 2,
    aiTasks: 14,
    linesOfCode: "12.4k",
    testCoverage: "62.0%",
    productivityScore: 72,
  },
  {
    id: "monaco-editor",
    name: "Forge Web Monaco Editor",
    description: "Customized Monaco editor bundle wrapping language services and inline completions.",
    progress: 20,
    status: "on_hold",
    priority: "low",
    lastUpdated: "4 days ago",
    repository: "github.com/active-workspace/forge-editor",
    branch: "main",
    teamMembers: ["SL"],
    openIssues: 5,
    pullRequests: 1,
    aiTasks: 3,
    linesOfCode: "28.1k",
    testCoverage: "41.5%",
    productivityScore: 80,
  },
  {
    id: "schema-registry",
    name: "Database Schema Registry",
    description: "Tracks active database schema version matrices and exports OpenAPI specifications.",
    progress: 60,
    status: "active",
    priority: "medium",
    lastUpdated: "1 week ago",
    repository: "github.com/active-workspace/schema-db",
    branch: "main",
    teamMembers: ["RD", "RK"],
    openIssues: 8,
    pullRequests: 1,
    aiTasks: 4,
    linesOfCode: "8.9k",
    testCoverage: "76.8%",
    productivityScore: 89,
  },
  {
    id: "documentation-docs",
    name: "User Guide & API Docs",
    description: "Technical specifications, user onboarding documents, and architectural reference layout.",
    progress: 100,
    status: "completed",
    priority: "low",
    lastUpdated: "2 weeks ago",
    repository: "github.com/active-workspace/docs-site",
    branch: "main",
    teamMembers: ["RD", "SL", "RK", "AM"],
    openIssues: 0,
    pullRequests: 0,
    aiTasks: 0,
    linesOfCode: "4.2k",
    testCoverage: "100%",
    productivityScore: 100,
  }
];

export const MOCK_ACTIVITIES: Activity[] = [
  {
    id: "act-1",
    message: "AI generated architecture document for database schema migration",
    time: "2 mins ago",
    author: "Forge Copilot",
    type: "ai"
  },
  {
    id: "act-2",
    message: "Rahul Dev pushed 3 commits to feature/jwt-rotation",
    time: "15 mins ago",
    author: "Rahul Dev",
    type: "commit"
  },
  {
    id: "act-3",
    message: "Repository connected: github.com/active-workspace/forge-auth",
    time: "1 hour ago",
    author: "Rahul Dev",
    type: "sync"
  },
  {
    id: "act-4",
    message: "Pull request #14 opened: Integrate OAuth providers",
    time: "4 hours ago",
    author: "Risha Khan",
    type: "commit"
  },
  {
    id: "act-5",
    message: "Sprint 2 completed: Web shell navigation dashboard scaffolding",
    time: "1 day ago",
    author: "Forge Core",
    type: "sprint"
  },
  {
    id: "act-6",
    message: "Updated database architecture documentation",
    time: "2 days ago",
    author: "Sarah Lee",
    type: "documentation"
  }
];

export const MOCK_INSIGHTS: AIInsight[] = [
  {
    id: "ins-1",
    severity: "critical",
    suggestion: "Authentication module missing token validation",
    description: "The authentication module in feature/jwt-rotation does not perform cryptographic validation on incoming refresh request tokens.",
    recommendedAction: "Add jwt.verify validation to refresh tokens endpoint."
  },
  {
    id: "ins-2",
    severity: "warning",
    suggestion: "Database schema migration has slow queries",
    description: "Missing index on workspaceId column in schema-db. Slow queries predicted under heavy tenant loads.",
    recommendedAction: "Inject index database migration script."
  },
  {
    id: "ins-3",
    severity: "info",
    suggestion: "Repository health is improving",
    description: "Overall test suite coverage on Forge Core has increased by 4.2% since yesterday.",
    recommendedAction: "Approve merge request for outstanding unit test suite."
  },
  {
    id: "ins-4",
    severity: "warning",
    suggestion: "High priority issues detected in OAuth",
    description: "User sessions fail to expire when credentials change on external identity providers.",
    recommendedAction: "Add dynamic scope validation checker."
  }
];

export const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: "not-1",
    title: "New AI Suggestion",
    message: "AI identified complex nesting in OAuth controller routing.",
    time: "5 mins ago",
    read: false,
    type: "warning"
  },
  {
    id: "not-2",
    title: "Build Success",
    message: "Pipeline #182 successfully compiled on branch main.",
    time: "1 hour ago",
    read: false,
    type: "success"
  },
  {
    id: "not-3",
    title: "Repository Synced",
    message: "Synchronized files successfully with github.com/forge/core.",
    time: "3 hours ago",
    read: true,
    type: "info"
  },
  {
    id: "not-4",
    title: "Security Scan Clear",
    message: "0 vulnerabilities found in package lock files.",
    time: "1 day ago",
    read: true,
    type: "success"
  },
  {
    id: "not-5",
    title: "Workspace Invitation",
    message: "Rahul invited you to participate in Internal API Platform.",
    time: "2 days ago",
    read: true,
    type: "info"
  }
];

export const MOCK_FILE_TREES: Record<string, FileNode[]> = {
  "forge-core": [
    {
      name: "apps",
      type: "directory",
      children: [
        {
          name: "web",
          type: "directory",
          children: [
            { name: "package.json", type: "file", size: "1.2 KB", lastUpdated: "5 mins ago" },
            { name: "next.config.ts", type: "file", size: "133 B", lastUpdated: "3 hours ago" },
            {
              name: "src",
              type: "directory",
              children: [
                { name: "app", type: "directory" },
                { name: "components", type: "directory" }
              ]
            }
          ]
        },
        {
          name: "api",
          type: "directory",
          children: [
            { name: "requirements.txt", type: "file", size: "380 B", lastUpdated: "1 day ago" },
            { name: "main.py", type: "file", size: "4.5 KB", lastUpdated: "2 hours ago" }
          ]
        }
      ]
    },
    {
      name: "packages",
      type: "directory",
      children: [
        { name: "types", type: "directory" },
        { name: "ui", type: "directory" }
      ]
    },
    { name: "pnpm-workspace.yaml", type: "file", size: "90 B", lastUpdated: "5 mins ago" },
    { name: "turbo.json", type: "file", size: "336 B", lastUpdated: "1 week ago" }
  ],
  "api-gateway": [
    { name: "app", type: "directory" },
    { name: "tests", type: "directory" },
    { name: "Dockerfile", type: "file", size: "480 B", lastUpdated: "2 hours ago" },
    { name: "README.md", type: "file", size: "1.5 KB", lastUpdated: "2 hours ago" }
  ]
};
