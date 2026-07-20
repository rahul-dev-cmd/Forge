// Shared TypeScript Type Definitions for Forge

export interface User {
  id: string;
  email: string;
  clerkId: string;
  avatarUrl?: string;
  githubId?: string;
  googleId?: string;
  theme?: "light" | "dark";
  createdAt: Date;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  ownerId: string;
  createdAt: Date;
}

export interface Membership {
  id: string;
  userId: string;
  organizationId: string;
  role: "owner" | "admin" | "member" | "guest";
  createdAt: Date;
}

export type WorkspaceRole = "owner" | "admin" | "manager" | "developer" | "viewer";

export interface Workspace {
  id: string;
  name: string;
  slug?: string;
  ownerId: string;
  organizationId?: string;
  role?: WorkspaceRole;
  description?: string;
}

export type ProjectStatus = "active" | "archived" | "completed" | "draft";
export type ProjectPriority = "low" | "medium" | "high" | "critical";

export interface Project {
  id: string;
  workspaceId: string;
  ownerId?: string;
  name: string;
  slug?: string;
  description?: string;
  status?: ProjectStatus;
  priority?: ProjectPriority;
  tags?: string[];
  version?: number;
  visibility?: string;
  isFavorite?: boolean;
  dueDate?: string | null;
  createdAt?: string;
}

export interface OrganizationInvitation {
  id: string;
  organizationId: string;
  email: string;
  role: Membership["role"];
  status: "pending" | "accepted" | "rejected" | "expired";
  expiresAt: string;
}

export interface Repository {
  id: string;
  projectId: string;
  name: string;
  gitUrl: string;
  isIndexed: boolean;
  provider?: "github" | "gitlab" | "bitbucket" | "azure_devops" | "local";
  visibility?: "public" | "private" | "internal";
  connectionStatus?: string;
}

export interface ActivityEvent {
  id: string;
  type: "audit" | "repository" | string;
  action: string;
  actorId?: string | null;
  createdAt: string;
  details?: Record<string, unknown> | null;
}
