import { apiClient, ApiEnvelope } from "./client";

export interface GitHubInstallationDto {
  id: string;
  installation_id: string;
  account_login: string;
  account_id: string;
  account_type: string;
  account_avatar_url?: string | null;
  status: string;
  workspace_id?: string | null;
  last_validated_at?: string | null;
  created_at?: string | null;
}

export interface GitHubRemoteRepoDto {
  provider_repository_id: string;
  installation_id: string;
  name: string;
  full_name: string;
  owner?: string;
  private: boolean;
  default_branch: string;
  clone_url?: string;
  html_url?: string;
  description?: string | null;
  language?: string | null;
  already_imported: boolean;
  forge_repository_id?: string | null;
}

export async function connectGitHub(workspaceId?: string) {
  const res = await apiClient.post<
    ApiEnvelope<{
      mode: string;
      authorize_url: string;
      install_url: string;
      state: string;
      configured: boolean;
    }>
  >("/github/connect", { workspace_id: workspaceId ?? null });
  return res.data;
}

export async function installGitHubApp(workspaceId?: string, installationId?: string) {
  const res = await apiClient.post<
    ApiEnvelope<{
      install_url?: string;
      installation?: GitHubInstallationDto;
      configured?: boolean;
    }>
  >("/github/install", {
    workspace_id: workspaceId ?? null,
    installation_id: installationId ?? null,
  });
  return res.data;
}

export async function completeGitHubCallback(params: {
  code?: string;
  installationId?: string;
  workspaceId?: string;
}) {
  const search = new URLSearchParams();
  if (params.code) search.set("code", params.code);
  if (params.installationId) search.set("installation_id", params.installationId);
  if (params.workspaceId) search.set("workspace_id", params.workspaceId);
  const res = await apiClient.post<ApiEnvelope<Record<string, unknown>>>(
    `/github/complete?${search.toString()}`
  );
  return res.data;
}

export async function listGitHubInstallations(): Promise<GitHubInstallationDto[]> {
  const res = await apiClient.get<ApiEnvelope<GitHubInstallationDto[]>>("/github/installations");
  return res.data ?? [];
}

export async function listGitHubRepositories(params?: {
  installationId?: string;
  page?: number;
  perPage?: number;
}): Promise<{ items: GitHubRemoteRepoDto[]; total: number }> {
  const search = new URLSearchParams();
  if (params?.installationId) search.set("installation_id", params.installationId);
  if (params?.page) search.set("page", String(params.page));
  if (params?.perPage) search.set("per_page", String(params.perPage));
  const res = await apiClient.get<ApiEnvelope<GitHubRemoteRepoDto[]>>(
    `/github/repositories?${search.toString()}`
  );
  return {
    items: res.data ?? [],
    total: res.meta?.total ?? res.data?.length ?? 0,
  };
}
