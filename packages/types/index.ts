// Shared TypeScript Type Definitions for Forge

export interface User {
  id: string;
  email: string;
  githubId?: string;
  googleId?: string;
  theme?: 'light' | 'dark';
}

export interface Workspace {
  id: string;
  name: string;
  ownerId: string;
}

export interface Project {
  id: string;
  workspaceId: string;
  name: string;
  description?: string;
}

export interface Repository {
  id: string;
  projectId: string;
  name: string;
  gitUrl: string;
  isIndexed: boolean;
}
