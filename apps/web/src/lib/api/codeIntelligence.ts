import { api } from "./client";

export interface IndexStatusResponse {
  id?: string;
  repository_id: string;
  commit_sha?: string;
  branch?: string;
  status: "none" | "pending" | "queued" | "running" | "completed" | "failed" | "cancelled";
  ast_version?: string;
  total_files?: number;
  total_symbols?: number;
  total_chunks?: number;
  total_lines?: number;
  indexed_at?: string | null;
  error_message?: string | null;
}

export interface IndexedFile {
  id: string;
  file_path: string;
  file_hash: string;
  language: string;
  size_bytes: number;
  line_count: number;
  symbol_count: number;
  chunk_count: number;
  cyclomatic_complexity: number;
  status: string;
}

export interface CodeSymbol {
  id: string;
  name: string;
  fqn: string;
  symbol_type: string;
  visibility: string;
  modifiers?: string[];
  signature?: string;
  docstring?: string;
  start_line: number;
  end_line: number;
  parameter_count: number;
}

export interface RepositoryMetrics {
  repository_id: string;
  metrics_ready?: boolean;
  total_files?: number;
  total_lines?: number;
  total_symbols?: number;
  total_chunks?: number;
  average_complexity?: number;
  maintainability_index?: number;
  largest_file_path?: string;
  largest_file_bytes?: number;
  deepest_directory_depth?: number;
  total_classes?: number;
  total_functions?: number;
  total_methods?: number;
  todo_count?: number;
  fixme_count?: number;
  documentation_coverage_pct?: number;
  language_distribution?: Record<string, number>;
}

export interface LanguageStat {
  language: string;
  file_count: number;
  line_count: number;
  bytes: number;
  percentage: number;
}

export interface IndexJob {
  id: string;
  job_type: string;
  status: string;
  progress_pct: number;
  processed_files: number;
  total_files: number;
  error_message?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
}

export const codeIntelligenceApi = {
  async getIndexStatus(repositoryId: string): Promise<IndexStatusResponse> {
    const res = await api.get<{ data: IndexStatusResponse }>(`/repositories/${repositoryId}/index`);
    return res.data;
  },

  async triggerClone(repositoryId: string): Promise<void> {
    await api.post(`/repositories/${repositoryId}/clone`);
  },

  async triggerIndex(repositoryId: string): Promise<void> {
    await api.post(`/repositories/${repositoryId}/index`);
  },

  async triggerReindex(repositoryId: string): Promise<void> {
    await api.post(`/repositories/${repositoryId}/reindex`);
  },

  async listFiles(repositoryId: string, language?: string): Promise<IndexedFile[]> {
    const params = language ? { language } : {};
    const res = await api.get<{ data: IndexedFile[] }>(`/repositories/${repositoryId}/files`, { params });
    return res.data || [];
  },

  async getDirectoryTree(repositoryId: string): Promise<Record<string, unknown>> {
    const res = await api.get<{ data: Record<string, unknown> }>(`/repositories/${repositoryId}/tree`);
    return res.data || {};
  },

  async listSymbols(repositoryId: string, query?: string, symbolType?: string): Promise<CodeSymbol[]> {
    const params: Record<string, string> = {};
    if (query) params.query = query;
    if (symbolType) params.symbol_type = symbolType;
    const res = await api.get<{ data: CodeSymbol[] }>(`/repositories/${repositoryId}/symbols`, { params });
    return res.data || [];
  },

  async getMetrics(repositoryId: string): Promise<RepositoryMetrics> {
    const res = await api.get<{ data: RepositoryMetrics }>(`/repositories/${repositoryId}/metrics`);
    return res.data;
  },

  async getLanguages(repositoryId: string): Promise<LanguageStat[]> {
    const res = await api.get<{ data: LanguageStat[] }>(`/repositories/${repositoryId}/languages`);
    return res.data || [];
  },

  async listIndexJobs(repositoryId: string): Promise<IndexJob[]> {
    const res = await api.get<{ data: IndexJob[] }>(`/repositories/${repositoryId}/index-jobs`);
    return res.data || [];
  },
};
