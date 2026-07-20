import { apiClient, ApiEnvelope } from "./client";

export interface ActivityDto {
  id: string;
  type: "audit" | "repository" | string;
  action: string;
  actor_id?: string | null;
  created_at: string;
  details?: Record<string, unknown> | null;
}

export async function listWorkspaceActivities(
  workspaceId: string,
  limit = 20
): Promise<ActivityDto[]> {
  const res = await apiClient.get<ApiEnvelope<ActivityDto[]>>(
    `/activities/workspace/${workspaceId}?limit=${limit}`
  );
  return res.data ?? [];
}
