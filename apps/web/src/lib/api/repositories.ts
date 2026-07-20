import { apiClient, ApiEnvelope } from "./client";

export type SyncStatus =
  | "idle"
  | "queued"
  | "syncing"
  | "synced"
  | "failed"
  | "disconnected";

export interface RepositoryDto {
  id: string;
  project_id: string;
  workspace_id: string;
  provider: string;
  external_id: string;
  provider_repository_id?: string | null;
  installation_id?: string | null;
  name: string;
  owner?: string | null;
  full_name?: string | null;
  description?: string | null;
  default_branch: string;
  clone_url: string;
  html_url?: string | null;
  visibility: string;
  connection_status: string;
  sync_status: SyncStatus | string;
  sync_error?: string | null;
  last_synced_at?: string | null;
  stars_count?: number;
  forks_count?: number;
  watchers_count?: number;
  open_issues_count?: number;
  license?: string | null;
  primary_language?: string | null;
  readme_exists?: boolean;
  indexing_ready?: boolean;
  is_archived?: boolean;
  is_fork?: boolean;
  languages?: { language: string; bytes: number; percentage: number }[];
  topics?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface SyncJobDto {
  id: string;
  job_type: string;
  status: string;
  progress: number;
  started_at?: string | null;
  finished_at?: string | null;
  error_message?: string | null;
  branches_synced?: number;
  commits_synced?: number;
  pull_requests_synced?: number;
  issues_synced?: number;
  contributors_synced?: number;
}

export interface RepositoryStatusDto {
  repository_id: string;
  connection_status: string;
  sync_status: string;
  sync_error?: string | null;
  last_synced_at?: string | null;
  indexing_ready: boolean;
  last_webhook_delivery_id?: string | null;
  sync_history: SyncJobDto[];
}

export interface BranchDto {
  id: string;
  name: string;
  is_default: boolean;
  latest_commit_sha?: string | null;
  last_synced_at?: string | null;
}

export interface CommitDto {
  id: string;
  commit_sha: string;
  author_name?: string | null;
  author_login?: string | null;
  commit_message?: string | null;
  html_url?: string | null;
  additions?: number | null;
  deletions?: number | null;
  committed_at?: string | null;
}

export interface PullRequestDto {
  id: string;
  number: number;
  title: string;
  status: string;
  source_branch?: string | null;
  target_branch?: string | null;
  author_login?: string | null;
  author_avatar_url?: string | null;
  html_url?: string | null;
  draft: boolean;
  updated_at?: string | null;
}

export interface IssueDto {
  id: string;
  number: number;
  title: string;
  status: string;
  author_login?: string | null;
  html_url?: string | null;
  labels: string[];
  updated_at?: string | null;
}

export interface ContributorDto {
  id: string;
  login: string;
  avatar_url?: string | null;
  html_url?: string | null;
  contributions: number;
}

export async function listRepositories(params: {
  workspaceId?: string;
  projectId?: string;
  query?: string;
  syncStatus?: string;
  sortBy?: string;
  order?: "asc" | "desc";
  page?: number;
  limit?: number;
}): Promise<{ items: RepositoryDto[]; total: number }> {
  const search = new URLSearchParams();
  if (params.workspaceId) search.set("workspace_id", params.workspaceId);
  if (params.projectId) search.set("project_id", params.projectId);
  if (params.query) search.set("query", params.query);
  if (params.syncStatus) search.set("sync_status", params.syncStatus);
  if (params.sortBy) search.set("sort_by", params.sortBy);
  if (params.order) search.set("order", params.order);
  if (params.page) search.set("page", String(params.page));
  if (params.limit) search.set("limit", String(params.limit));

  const res = await apiClient.get<ApiEnvelope<RepositoryDto[]>>(
    `/repositories?${search.toString()}`
  );
  return {
    items: res.data ?? [],
    total: res.meta?.total ?? res.data?.length ?? 0,
  };
}

export async function getRepository(id: string): Promise<RepositoryDto> {
  const res = await apiClient.get<ApiEnvelope<RepositoryDto>>(`/repositories/${id}`);
  return res.data;
}

export async function importRepository(body: {
  workspace_id: string;
  project_id: string;
  installation_id: string;
  provider_repository_id: string;
  full_name?: string;
  name?: string;
  owner?: string;
  default_branch?: string;
  clone_url?: string;
  html_url?: string;
  private?: boolean;
}) {
  const res = await apiClient.post<
    ApiEnvelope<{ repository: RepositoryDto; sync_job: { id: string; status: string } }>
  >("/repositories/import", body);
  return res.data;
}

export async function syncRepository(id: string) {
  const res = await apiClient.post<
    ApiEnvelope<{ sync_job_id: string; status: string }>
  >(`/repositories/${id}/sync`);
  return res.data;
}

export async function getRepositoryStatus(id: string): Promise<RepositoryStatusDto> {
  const res = await apiClient.get<ApiEnvelope<RepositoryStatusDto>>(
    `/repositories/${id}/status`
  );
  return res.data;
}

export async function disconnectRepository(id: string): Promise<RepositoryDto> {
  const res = await apiClient.post<ApiEnvelope<RepositoryDto>>(
    `/repositories/${id}/disconnect`
  );
  return res.data;
}

export async function listBranches(id: string): Promise<BranchDto[]> {
  const res = await apiClient.get<ApiEnvelope<BranchDto[]>>(`/repositories/${id}/branches`);
  return res.data ?? [];
}

export async function listCommits(id: string): Promise<CommitDto[]> {
  const res = await apiClient.get<ApiEnvelope<CommitDto[]>>(`/repositories/${id}/commits`);
  return res.data ?? [];
}

export async function listPullRequests(id: string): Promise<PullRequestDto[]> {
  const res = await apiClient.get<ApiEnvelope<PullRequestDto[]>>(
    `/repositories/${id}/pull-requests`
  );
  return res.data ?? [];
}

export async function listIssues(id: string): Promise<IssueDto[]> {
  const res = await apiClient.get<ApiEnvelope<IssueDto[]>>(`/repositories/${id}/issues`);
  return res.data ?? [];
}

export async function listContributors(id: string): Promise<ContributorDto[]> {
  const res = await apiClient.get<ApiEnvelope<ContributorDto[]>>(
    `/repositories/${id}/contributors`
  );
  return res.data ?? [];
}
