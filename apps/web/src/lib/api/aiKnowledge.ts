import { api } from "./client";

export interface EmbeddingStatusResponse {
  repository_id: string;
  status: string;
  total_vectors?: number;
  total_tokens?: number;
  provider?: string;
  model_name?: string;
  dimensions?: number;
  commit_sha?: string;
  version_hash?: string;
  embedded?: boolean;
}

export interface RepositoryKnowledgeSummary {
  repository_id: string;
  knowledge_ready?: boolean;
  total_vectors?: number;
  total_tokens?: number;
  estimated_cost_usd?: number;
  provider?: string;
  model_name?: string;
  dimensions?: number;
  embedding_health?: string;
}

export interface SearchResultItem {
  chunk_id: string;
  file_path: string;
  language: string;
  start_line: number;
  end_line: number;
  content: string;
  vector_score: number;
  bm25_score: number;
  symbol_bonus: number;
  dependency_bonus: number;
  final_score: number;
  symbols: string[];
}

export interface ContextPackage {
  repository: {
    id: string;
    name: string;
    full_name: string;
    default_branch: string;
  };
  workspace: {
    id: string;
  };
  query: string;
  retrievedChunks: {
    chunk_id: string;
    file_path: string;
    language: string;
    start_line: number;
    end_line: number;
    content: string;
    score: number;
  }[];
  relatedSymbols: {
    name: string;
    fqn: string;
    symbol_type: string;
    visibility: string;
    file_path: string;
    start_line: number;
    end_line: number;
  }[];
  dependencyGraph: {
    imports: { source_file: string; target_module: string }[];
    dependencies: { source: string; target: string; type: string }[];
  };
  files: { file_path: string; language: string }[];
  metadata: {
    parent_classes: string[];
    child_methods: string[];
    call_graph: { caller: string; callee: string; file: string; line: number }[];
    readme_snippet: string;
    package_metadata: string;
  };
  confidence: number;
  citations: { file_path: string; start_line: number; end_line: number; score: number }[];
}

export interface EmbeddingJobItem {
  id: string;
  job_type: string;
  status: string;
  progress_pct: number;
  processed_chunks: number;
  total_chunks: number;
  tokens_processed: number;
  estimated_cost_usd: number;
  error_message?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface SearchHistoryItem {
  id: string;
  query: string;
  search_type: string;
  result_count: number;
  top_similarity_score: number;
  top_bm25_score: number;
  final_score: number;
  duration_ms: number;
  created_at: string;
}

export const aiKnowledgeApi = {
  async getEmbeddingStatus(repositoryId: string): Promise<EmbeddingStatusResponse> {
    const res = await api.get<{ data: EmbeddingStatusResponse }>(`/repositories/${repositoryId}/embeddings/status`);
    return res.data;
  },

  async triggerEmbed(repositoryId: string): Promise<void> {
    await api.post(`/repositories/${repositoryId}/embed`);
  },

  async triggerReembed(repositoryId: string): Promise<void> {
    await api.post(`/repositories/${repositoryId}/reembed`);
  },

  async getKnowledgeSummary(repositoryId: string): Promise<RepositoryKnowledgeSummary> {
    const res = await api.get<{ data: RepositoryKnowledgeSummary }>(`/repositories/${repositoryId}/knowledge`);
    return res.data;
  },

  async search(
    repositoryId: string,
    query: string,
    searchType = "hybrid",
    topK = 10
  ): Promise<SearchResultItem[]> {
    const res = await api.post<{ data: SearchResultItem[] }>(`/repositories/${repositoryId}/search`, {
      query,
      search_type: searchType,
      top_k: topK,
    });
    return res.data || [];
  },

  async retrieveContext(repositoryId: string, query: string, topK = 5): Promise<ContextPackage> {
    const res = await api.post<{ data: ContextPackage }>(`/repositories/${repositoryId}/retrieve-context`, {
      query,
      top_k: topK,
    });
    return res.data;
  },

  async listEmbeddingJobs(repositoryId: string): Promise<EmbeddingJobItem[]> {
    const res = await api.get<{ data: EmbeddingJobItem[] }>(`/repositories/${repositoryId}/embedding-jobs`);
    return res.data || [];
  },

  async listSearchHistory(repositoryId: string): Promise<SearchHistoryItem[]> {
    const res = await api.get<{ data: SearchHistoryItem[] }>(`/repositories/${repositoryId}/search-history`);
    return res.data || [];
  },
};
