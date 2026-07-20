import { apiClient, ApiEnvelope } from "./client";

export type WorkspaceRole = "owner" | "admin" | "manager" | "developer" | "viewer";

export interface WorkspaceDto {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  owner_id: string;
  organization_id?: string | null;
  role?: WorkspaceRole;
  created_at?: string;
}

export async function listWorkspaces(): Promise<WorkspaceDto[]> {
  const res = await apiClient.get<ApiEnvelope<WorkspaceDto[]>>("/workspaces");
  return res.data ?? [];
}

export async function createWorkspace(input: {
  owner_id: string;
  name: string;
  slug: string;
  description?: string;
  organization_id?: string;
}): Promise<WorkspaceDto> {
  const res = await apiClient.post<ApiEnvelope<WorkspaceDto>>("/workspaces", input);
  return res.data;
}
