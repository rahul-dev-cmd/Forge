import { apiClient, ApiEnvelope } from "./client";

export type ProjectStatus = "active" | "archived" | "completed" | "draft";
export type ProjectPriority = "low" | "medium" | "high" | "critical";

export interface ProjectDto {
  id: string;
  workspace_id: string;
  owner_id: string;
  name: string;
  slug: string;
  description?: string | null;
  status: ProjectStatus;
  priority: ProjectPriority;
  tags?: string[];
  due_date?: string | null;
  visibility?: string;
  is_favorite?: boolean;
  version: number;
  created_at?: string;
}

export interface ListProjectsParams {
  workspaceId: string;
  query?: string;
  status?: string;
  priority?: string;
  sortBy?: string;
  order?: "asc" | "desc";
  page?: number;
  limit?: number;
}

export async function listProjects(params: ListProjectsParams): Promise<{
  items: ProjectDto[];
  total: number;
}> {
  const search = new URLSearchParams();
  search.set("workspace_id", params.workspaceId);
  if (params.query) search.set("query", params.query);
  if (params.status && params.status !== "all") search.set("status", params.status);
  if (params.priority && params.priority !== "all") search.set("priority", params.priority);
  if (params.sortBy) search.set("sort_by", params.sortBy);
  if (params.order) search.set("order", params.order);
  if (params.page) search.set("page", String(params.page));
  if (params.limit) search.set("limit", String(params.limit));

  const res = await apiClient.get<ApiEnvelope<ProjectDto[]>>(`/projects?${search.toString()}`);
  return {
    items: res.data ?? [],
    total: res.meta?.total ?? res.data?.length ?? 0,
  };
}

export async function getProject(workspaceId: string, idOrSlug: string): Promise<ProjectDto> {
  const res = await apiClient.get<ApiEnvelope<ProjectDto>>(
    `/projects/${workspaceId}/${idOrSlug}`
  );
  return res.data;
}
