"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Sparkles,
  Database,
  Search,
  RefreshCw,
  Layers,
  Code2,
  GitBranch,
  Cpu,
  FileCode,
  CheckCircle2,
  Clock,
  Zap,
  Info,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  aiKnowledgeApi,
  EmbeddingStatusResponse,
  RepositoryKnowledgeSummary,
  SearchResultItem,
  ContextPackage,
  SearchHistoryItem,
} from "@/lib/api/aiKnowledge";

interface AIKnowledgeDashboardProps {
  repositoryId: string;
}

export function AIKnowledgeDashboard({ repositoryId }: AIKnowledgeDashboardProps) {
  const queryClient = useQueryClient();

  const [activeSubTab, setActiveSubTab] = React.useState<"search" | "context" | "history">("search");
  const [searchQuery, setSearchQuery] = React.useState("");
  const [contextQuery, setContextQuery] = React.useState("");

  const statusQuery = useQuery({
    queryKey: ["ai-embed-status", repositoryId],
    queryFn: () => aiKnowledgeApi.getEmbeddingStatus(repositoryId),
    refetchInterval: (q) => {
      const status = q.state.data?.status;
      return status === "processing" || status === "queued" ? 2000 : false;
    },
  });

  const summaryQuery = useQuery({
    queryKey: ["ai-knowledge-summary", repositoryId],
    queryFn: () => aiKnowledgeApi.getKnowledgeSummary(repositoryId),
  });

  const historyQuery = useQuery({
    queryKey: ["ai-search-history", repositoryId],
    queryFn: () => aiKnowledgeApi.listSearchHistory(repositoryId),
  });

  const searchMutation = useMutation({
    mutationFn: (q: string) => aiKnowledgeApi.search(repositoryId, q, "hybrid", 8),
  });

  const contextMutation = useMutation({
    mutationFn: (q: string) => aiKnowledgeApi.retrieveContext(repositoryId, q, 5),
  });

  const embedMutation = useMutation({
    mutationFn: () => aiKnowledgeApi.triggerEmbed(repositoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-embed-status", repositoryId] });
      queryClient.invalidateQueries({ queryKey: ["ai-knowledge-summary", repositoryId] });
    },
  });

  const reembedMutation = useMutation({
    mutationFn: () => aiKnowledgeApi.triggerReembed(repositoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-embed-status", repositoryId] });
      queryClient.invalidateQueries({ queryKey: ["ai-knowledge-summary", repositoryId] });
    },
  });

  const status = statusQuery.data;
  const summary = summaryQuery.data;
  const history = historyQuery.data || [];
  const searchResults = searchMutation.data || [];
  const contextPkg = contextMutation.data;

  const isEmbedding = status?.status === "processing" || status?.status === "queued";

  return (
    <div className="flex flex-col gap-6 w-full mt-4">
      {/* Knowledge Header Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 border border-border rounded-lg bg-card/60">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-md bg-primary/10 text-primary">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-foreground">AI Vector Knowledge Base</h3>
              <Badge
                variant={
                  status?.status === "ready"
                    ? "default"
                    : isEmbedding
                    ? "secondary"
                    : "outline"
                }
                className="text-[10px] capitalize"
              >
                {status?.status || "none"}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {status?.total_vectors
                ? `${status.total_vectors} vector embeddings indexed using ${status.provider} (${status.model_name}, ${status.dimensions}d)`
                : "Generate vector embeddings from repository AST code chunks to enable RAG context retrieval."}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button
            size="sm"
            disabled={embedMutation.isPending || isEmbedding}
            onClick={() => embedMutation.mutate()}
            className="gap-1.5 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isEmbedding ? "animate-spin" : ""}`} />
            {isEmbedding ? "Generating Vectors..." : "Generate Embeddings"}
          </Button>
          {status?.total_vectors ? (
            <Button
              size="sm"
              variant="outline"
              disabled={reembedMutation.isPending || isEmbedding}
              onClick={() => reembedMutation.mutate()}
              className="gap-1.5 text-xs"
            >
              Re-embed
            </Button>
          ) : null}
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 border border-border rounded-lg bg-card">
          <p className="text-xs text-muted-foreground">Indexed Vector Count</p>
          <p className="text-2xl font-bold text-foreground mt-1">
            {summary?.total_vectors ?? 0}
          </p>
          <span className="text-[10px] text-muted-foreground">Qdrant Collection Collection Payload</span>
        </div>

        <div className="p-4 border border-border rounded-lg bg-card">
          <p className="text-xs text-muted-foreground">Tokens Embedded</p>
          <p className="text-2xl font-bold text-foreground mt-1">
            {(summary?.total_tokens ?? 0).toLocaleString()}
          </p>
          <span className="text-[10px] text-muted-foreground">Est. Cost: ${summary?.estimated_cost_usd ?? 0.00}</span>
        </div>

        <div className="p-4 border border-border rounded-lg bg-card">
          <p className="text-xs text-muted-foreground">Vector Dimensions</p>
          <p className="text-2xl font-bold text-foreground mt-1">
            {summary?.dimensions ?? 384}d
          </p>
          <span className="text-[10px] text-muted-foreground">{summary?.model_name || "all-MiniLM-L6-v2"}</span>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex border-b border-border">
        <button
          onClick={() => setActiveSubTab("search")}
          className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeSubTab === "search"
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Semantic & Hybrid Search
        </button>
        <button
          onClick={() => setActiveSubTab("context")}
          className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeSubTab === "context"
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          RAG Context Package Inspector
        </button>
        <button
          onClick={() => setActiveSubTab("history")}
          className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeSubTab === "history"
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Search History ({history.length})
        </button>
      </div>

      {/* Sub-Tab 1: Semantic & Hybrid Search */}
      {activeSubTab === "search" && (
        <div className="space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (searchQuery.trim()) searchMutation.mutate(searchQuery.trim());
            }}
            className="flex gap-2"
          >
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                placeholder="Ask a technical query (e.g. 'How does authentication work?', 'Find user database models')..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs rounded-md border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <Button size="sm" type="submit" disabled={searchMutation.isPending || !searchQuery.trim()}>
              {searchMutation.isPending ? "Searching..." : "Hybrid Search"}
            </Button>
          </form>

          <div className="space-y-3">
            {searchResults.length === 0 ? (
              <div className="p-8 text-center text-xs text-muted-foreground border border-border rounded-lg">
                Enter a search query above to test vector retrieval and score ranking.
              </div>
            ) : (
              searchResults.map((r, i) => (
                <div key={i} className="p-4 border border-border rounded-lg bg-card space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <FileCode className="w-4 h-4 text-primary shrink-0" />
                      <span className="font-mono font-semibold text-xs text-foreground truncate">{r.file_path}</span>
                      <span className="text-[10px] text-muted-foreground">
                        lines {r.start_line}-{r.end_line}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      <Badge variant="outline" className="text-[10px]">
                        Vec: {r.vector_score.toFixed(2)}
                      </Badge>
                      <Badge variant="outline" className="text-[10px]">
                        BM25: {r.bm25_score.toFixed(2)}
                      </Badge>
                      <Badge variant="default" className="text-[10px]">
                        Score: {r.final_score.toFixed(2)}
                      </Badge>
                    </div>
                  </div>

                  {r.symbols.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {r.symbols.map((sym) => (
                        <Badge key={sym} variant="secondary" className="text-[9px] font-mono">
                          {sym}
                        </Badge>
                      ))}
                    </div>
                  )}

                  <pre className="p-3 bg-muted/40 rounded text-[11px] font-mono overflow-x-auto text-foreground border border-border/50">
                    {r.content}
                  </pre>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Sub-Tab 2: RAG Context Package Inspector */}
      {activeSubTab === "context" && (
        <div className="space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (contextQuery.trim()) contextMutation.mutate(contextQuery.trim());
            }}
            className="flex gap-2"
          >
            <div className="relative flex-1">
              <Zap className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                placeholder="Build RAG Context Package for query..."
                value={contextQuery}
                onChange={(e) => setContextQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs rounded-md border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <Button size="sm" type="submit" disabled={contextMutation.isPending || !contextQuery.trim()}>
              {contextMutation.isPending ? "Assembling..." : "Build Context Package"}
            </Button>
          </form>

          {contextPkg ? (
            <div className="space-y-4 border border-border rounded-lg p-4 bg-card">
              <div className="flex justify-between items-center border-b border-border pb-3">
                <div>
                  <h4 className="text-xs font-bold text-foreground">Standardized ContextPackage Contract</h4>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Target payload consumed by Milestone 9+ AI Agents
                  </p>
                </div>
                <Badge variant="default" className="text-[10px]">
                  Confidence: {(contextPkg.confidence * 100).toFixed(0)}%
                </Badge>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                <div className="p-2 border border-border rounded bg-muted/30">
                  <span className="text-muted-foreground text-[10px]">Retrieved Chunks</span>
                  <p className="font-semibold text-foreground">{contextPkg.retrievedChunks.length}</p>
                </div>
                <div className="p-2 border border-border rounded bg-muted/30">
                  <span className="text-muted-foreground text-[10px]">Related Symbols</span>
                  <p className="font-semibold text-foreground">{contextPkg.relatedSymbols.length}</p>
                </div>
                <div className="p-2 border border-border rounded bg-muted/30">
                  <span className="text-muted-foreground text-[10px]">Dependencies</span>
                  <p className="font-semibold text-foreground">{contextPkg.dependencyGraph.imports.length}</p>
                </div>
                <div className="p-2 border border-border rounded bg-muted/30">
                  <span className="text-muted-foreground text-[10px]">Citations</span>
                  <p className="font-semibold text-foreground">{contextPkg.citations.length}</p>
                </div>
              </div>

              <pre className="p-3 bg-muted/50 rounded text-[11px] font-mono overflow-x-auto text-foreground max-h-96 border border-border">
                {JSON.stringify(contextPkg, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-muted-foreground border border-border rounded-lg">
              Generate a RAG Context Package above to view the unified data contract.
            </div>
          )}
        </div>
      )}

      {/* Sub-Tab 3: Search History & Latencies */}
      {activeSubTab === "history" && (
        <div className="border border-border rounded-lg overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="bg-muted/50 text-muted-foreground font-medium border-b border-border">
              <tr>
                <th className="p-2.5">Query</th>
                <th className="p-2.5">Type</th>
                <th className="p-2.5">Results</th>
                <th className="p-2.5">Final Score</th>
                <th className="p-2.5 text-right">Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {history.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-muted-foreground">
                    No search query history recorded.
                  </td>
                </tr>
              ) : (
                history.map((h) => (
                  <tr key={h.id} className="hover:bg-muted/30">
                    <td className="p-2.5 font-mono text-foreground font-medium">{h.query}</td>
                    <td className="p-2.5 capitalize">{h.search_type}</td>
                    <td className="p-2.5">{h.result_count} matches</td>
                    <td className="p-2.5 font-mono">{h.final_score.toFixed(2)}</td>
                    <td className="p-2.5 text-right font-mono text-muted-foreground">
                      {h.duration_ms.toFixed(1)} ms
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
