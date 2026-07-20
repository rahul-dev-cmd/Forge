import { api } from "./client";

export interface SystemStatsResponse {
  total_users: number;
  total_workspaces: number;
  total_repositories: number;
  total_tokens_consumed: number;
  total_llm_cost_usd: number;
}

export interface SystemDiagnosticsResponse {
  timestamp: number;
  database: { connected: boolean; connection_pool: string };
  redis_cache: { status: string; hit_ratio_pct: number };
  qdrant_vector_db: { status: string; collection: string };
  workers: { queue_name: string; active_workers: number; queue_depth: number };
  llm_providers: {
    active_provider: string;
    failover_configured: boolean;
    available_providers: string[];
  };
}

export interface WorkspaceActivityItem {
  id: string;
  action: string;
  target_type: string;
  target_id?: string | null;
  created_at: string;
}

export const adminApi = {
  async getSystemStats(): Promise<SystemStatsResponse> {
    const res = await api.get<{ data: SystemStatsResponse }>("/admin/stats");
    return res.data;
  },

  async getDiagnostics(): Promise<SystemDiagnosticsResponse> {
    const res = await api.get<{ data: SystemDiagnosticsResponse }>("/admin/diagnostics");
    return res.data;
  },

  async listWorkspaceActivity(workspaceId: string): Promise<WorkspaceActivityItem[]> {
    const res = await api.get<{ data: WorkspaceActivityItem[] }>(`/workspaces/${workspaceId}/activity`);
    return res.data || [];
  },
};
