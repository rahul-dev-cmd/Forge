"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Code,
  FileCode,
  Layers,
  Cpu,
  RefreshCw,
  Search,
  CheckCircle2,
  AlertCircle,
  Clock,
  Play,
  Terminal,
  FileText,
  HelpCircle,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  codeIntelligenceApi,
  IndexStatusResponse,
  RepositoryMetrics,
  LanguageStat,
  IndexedFile,
  CodeSymbol,
  IndexJob,
} from "@/lib/api/codeIntelligence";

interface RepositoryIntelligenceProps {
  repositoryId: string;
}

export function RepositoryIntelligence({ repositoryId }: RepositoryIntelligenceProps) {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = React.useState<"metrics" | "files" | "symbols" | "jobs">("metrics");
  const [fileSearch, setFileSearch] = React.useState("");
  const [symbolSearch, setSymbolSearch] = React.useState("");
  const [symbolFilter, setSymbolFilter] = React.useState<string>("all");

  const statusQuery = useQuery({
    queryKey: ["code-index-status", repositoryId],
    queryFn: () => codeIntelligenceApi.getIndexStatus(repositoryId),
    refetchInterval: (q) => {
      const status = q.state.data?.status;
      return status === "running" || status === "queued" ? 2000 : false;
    },
  });

  const metricsQuery = useQuery({
    queryKey: ["code-metrics", repositoryId],
    queryFn: () => codeIntelligenceApi.getMetrics(repositoryId),
  });

  const languagesQuery = useQuery({
    queryKey: ["code-languages", repositoryId],
    queryFn: () => codeIntelligenceApi.getLanguages(repositoryId),
  });

  const filesQuery = useQuery({
    queryKey: ["code-files", repositoryId],
    queryFn: () => codeIntelligenceApi.listFiles(repositoryId),
  });

  const symbolsQuery = useQuery({
    queryKey: ["code-symbols", repositoryId, symbolSearch, symbolFilter],
    queryFn: () =>
      codeIntelligenceApi.listSymbols(
        repositoryId,
        symbolSearch || undefined,
        symbolFilter !== "all" ? symbolFilter : undefined
      ),
  });

  const jobsQuery = useQuery({
    queryKey: ["code-index-jobs", repositoryId],
    queryFn: () => codeIntelligenceApi.listIndexJobs(repositoryId),
    refetchInterval: 3000,
  });

  const cloneMutation = useMutation({
    mutationFn: () => codeIntelligenceApi.triggerClone(repositoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["code-index-status", repositoryId] });
      queryClient.invalidateQueries({ queryKey: ["code-index-jobs", repositoryId] });
    },
  });

  const indexMutation = useMutation({
    mutationFn: () => codeIntelligenceApi.triggerIndex(repositoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["code-index-status", repositoryId] });
      queryClient.invalidateQueries({ queryKey: ["code-index-jobs", repositoryId] });
    },
  });

  const reindexMutation = useMutation({
    mutationFn: () => codeIntelligenceApi.triggerReindex(repositoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["code-index-status", repositoryId] });
      queryClient.invalidateQueries({ queryKey: ["code-index-jobs", repositoryId] });
    },
  });

  const statusData = statusQuery.data;
  const metrics = metricsQuery.data;
  const languages = languagesQuery.data || [];
  const files = filesQuery.data || [];
  const symbols = symbolsQuery.data || [];
  const jobs = jobsQuery.data || [];

  const filteredFiles = React.useMemo(() => {
    if (!fileSearch) return files;
    return files.filter((f) => f.file_path.toLowerCase().includes(fileSearch.toLowerCase()));
  }, [files, fileSearch]);

  const isIndexing = statusData?.status === "running" || statusData?.status === "queued";

  return (
    <div className="flex flex-col gap-6 w-full">
      {/* Indexing Status Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 border border-border rounded-lg bg-card/50">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-md bg-primary/10 text-primary">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-foreground">Code Intelligence Engine</h3>
              <Badge
                variant={
                  statusData?.status === "completed"
                    ? "default"
                    : statusData?.status === "running"
                    ? "secondary"
                    : "outline"
                }
                className="text-[10px] capitalize"
              >
                {statusData?.status || "none"}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {statusData?.status === "completed"
                ? `Indexed ${statusData.total_files || 0} files, ${statusData.total_symbols || 0} symbols, ${statusData.total_chunks || 0} chunks (AST v${statusData.ast_version || "1.0"})`
                : isIndexing
                ? "AST symbol parsing and dependency graph extraction in progress..."
                : "Repository not yet indexed locally for code intelligence."}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button
            size="sm"
            variant="outline"
            disabled={cloneMutation.isPending || isIndexing}
            onClick={() => cloneMutation.mutate()}
            className="gap-1.5 text-xs"
          >
            <Play className="w-3.5 h-3.5" />
            Clone
          </Button>
          <Button
            size="sm"
            disabled={indexMutation.isPending || isIndexing}
            onClick={() => indexMutation.mutate()}
            className="gap-1.5 text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isIndexing ? "animate-spin" : ""}`} />
            {isIndexing ? "Indexing..." : "Index Repository"}
          </Button>
          {statusData?.status === "completed" && (
            <Button
              size="sm"
              variant="ghost"
              disabled={reindexMutation.isPending || isIndexing}
              onClick={() => reindexMutation.mutate()}
              className="gap-1.5 text-xs text-muted-foreground"
            >
              Re-index
            </Button>
          )}
        </div>
      </div>

      {/* Language Breakdown Bar */}
      {languages.length > 0 && (
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-medium text-foreground">Language Distribution</span>
            <span className="text-muted-foreground">{languages.length} languages detected</span>
          </div>
          <div className="h-2 w-full flex rounded-full overflow-hidden bg-secondary">
            {languages.map((l, i) => (
              <div
                key={l.language}
                style={{ width: `${l.percentage}%` }}
                className={`h-full ${
                  i === 0 ? "bg-primary" : i === 1 ? "bg-chart-2" : i === 2 ? "bg-chart-3" : "bg-muted-foreground"
                }`}
                title={`${l.language}: ${l.percentage}% (${l.file_count} files)`}
              />
            ))}
          </div>
          <div className="flex flex-wrap gap-4 text-[11px] text-muted-foreground">
            {languages.slice(0, 5).map((l) => (
              <span key={l.language} className="inline-flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-primary" />
                <span className="font-medium text-foreground capitalize">{l.language}</span>
                <span>{l.percentage}%</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-border">
        <button
          onClick={() => setActiveTab("metrics")}
          className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeTab === "metrics"
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Overview & Metrics
        </button>
        <button
          onClick={() => setActiveTab("files")}
          className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeTab === "files"
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Files ({files.length})
        </button>
        <button
          onClick={() => setActiveTab("symbols")}
          className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeTab === "symbols"
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Symbols & AST
        </button>
        <button
          onClick={() => setActiveTab("jobs")}
          className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
            activeTab === "jobs"
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Index Jobs ({jobs.length})
        </button>
      </div>

      {/* Tab 1: Overview & Metrics */}
      {activeTab === "metrics" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 border border-border rounded-lg bg-card">
            <p className="text-xs text-muted-foreground">Maintainability Index</p>
            <p className="text-2xl font-bold text-foreground mt-1">
              {metrics?.maintainability_index ?? "—"} / 100
            </p>
            <span className="text-[10px] text-success">Good maintainability</span>
          </div>

          <div className="p-4 border border-border rounded-lg bg-card">
            <p className="text-xs text-muted-foreground">Average Complexity</p>
            <p className="text-2xl font-bold text-foreground mt-1">
              {metrics?.average_complexity ?? "—"}
            </p>
            <span className="text-[10px] text-muted-foreground">Cyclomatic score per file</span>
          </div>

          <div className="p-4 border border-border rounded-lg bg-card">
            <p className="text-xs text-muted-foreground">Extracted Symbols</p>
            <p className="text-2xl font-bold text-foreground mt-1">
              {metrics?.total_symbols ?? 0}
            </p>
            <span className="text-[10px] text-muted-foreground">
              {metrics?.total_classes || 0} Classes, {metrics?.total_functions || 0} Functions
            </span>
          </div>

          <div className="p-4 border border-border rounded-lg bg-card">
            <p className="text-xs text-muted-foreground">Pre-Embedding Chunks</p>
            <p className="text-2xl font-bold text-foreground mt-1">
              {metrics?.total_chunks ?? 0}
            </p>
            <span className="text-[10px] text-muted-foreground">Ready for Milestone 8 AI</span>
          </div>

          <div className="p-4 border border-border rounded-lg bg-card col-span-full sm:col-span-2">
            <h4 className="text-xs font-semibold text-foreground mb-3">Code Annotations & Docs</h4>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="p-2 border border-border rounded bg-muted/40">
                <span className="text-xs text-muted-foreground">TODOs</span>
                <p className="text-lg font-semibold text-foreground">{metrics?.todo_count ?? 0}</p>
              </div>
              <div className="p-2 border border-border rounded bg-muted/40">
                <span className="text-xs text-muted-foreground">FIXMEs</span>
                <p className="text-lg font-semibold text-destructive">{metrics?.fixme_count ?? 0}</p>
              </div>
              <div className="p-2 border border-border rounded bg-muted/40">
                <span className="text-xs text-muted-foreground">Doc Coverage</span>
                <p className="text-lg font-semibold text-foreground">
                  {metrics?.documentation_coverage_pct ?? 0}%
                </p>
              </div>
            </div>
          </div>

          <div className="p-4 border border-border rounded-lg bg-card col-span-full sm:col-span-2">
            <h4 className="text-xs font-semibold text-foreground mb-2">Repository Footprint</h4>
            <div className="space-y-1.5 text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>Largest File:</span>
                <span className="font-mono text-foreground">{metrics?.largest_file_path || "N/A"}</span>
              </div>
              <div className="flex justify-between">
                <span>Deepest Directory Depth:</span>
                <span className="font-mono text-foreground">{metrics?.deepest_directory_depth ?? 0} levels</span>
              </div>
              <div className="flex justify-between">
                <span>Total Lines of Code:</span>
                <span className="font-mono text-foreground">{metrics?.total_lines ?? 0} LOC</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Indexed Files */}
      {activeTab === "files" && (
        <div className="space-y-3">
          <div className="relative max-w-sm">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search file path..."
              value={fileSearch}
              onChange={(e) => setFileSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-md border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <div className="border border-border rounded-lg overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-muted/50 text-muted-foreground font-medium border-b border-border">
                <tr>
                  <th className="p-2.5">File Path</th>
                  <th className="p-2.5">Language</th>
                  <th className="p-2.5">Lines</th>
                  <th className="p-2.5">Symbols</th>
                  <th className="p-2.5">Complexity</th>
                  <th className="p-2.5 text-right">Size</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredFiles.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-muted-foreground">
                      No indexed files found. Click &quot;Index Repository&quot; to start.
                    </td>
                  </tr>
                ) : (
                  filteredFiles.map((file) => (
                    <tr key={file.id} className="hover:bg-muted/30">
                      <td className="p-2.5 font-mono text-foreground">{file.file_path}</td>
                      <td className="p-2.5 capitalize">{file.language}</td>
                      <td className="p-2.5">{file.line_count}</td>
                      <td className="p-2.5">{file.symbol_count}</td>
                      <td className="p-2.5">
                        <Badge
                          variant={file.cyclomatic_complexity > 10 ? "destructive" : "outline"}
                          className="text-[10px]"
                        >
                          Complexity {file.cyclomatic_complexity}
                        </Badge>
                      </td>
                      <td className="p-2.5 text-right font-mono text-muted-foreground">
                        {(file.size_bytes / 1024).toFixed(1)} KB
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Symbols & AST */}
      {activeTab === "symbols" && (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <div className="relative max-w-sm flex-1">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search symbols by name..."
                value={symbolSearch}
                onChange={(e) => setSymbolSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs rounded-md border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <select
              value={symbolFilter}
              onChange={(e) => setSymbolFilter(e.target.value)}
              className="px-2.5 py-1.5 text-xs rounded-md border border-border bg-background text-foreground"
            >
              <option value="all">All Types</option>
              <option value="class">Class</option>
              <option value="function">Function</option>
              <option value="method">Method</option>
              <option value="interface">Interface</option>
              <option value="enum">Enum</option>
            </select>
          </div>

          <div className="grid grid-cols-1 gap-2">
            {symbols.length === 0 ? (
              <div className="p-8 text-center text-xs text-muted-foreground border border-border rounded-lg">
                No matching code symbols found.
              </div>
            ) : (
              symbols.map((s) => (
                <div key={s.id} className="p-3 border border-border rounded-lg bg-card flex justify-between gap-4">
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-[10px] uppercase">
                        {s.symbol_type}
                      </Badge>
                      <span className="font-mono font-semibold text-xs text-foreground truncate">{s.name}</span>
                      <span className="text-[10px] text-muted-foreground">({s.visibility})</span>
                    </div>
                    <p className="font-mono text-[11px] text-muted-foreground truncate">{s.fqn}</p>
                    {s.docstring && (
                      <p className="text-[11px] italic text-muted-foreground line-clamp-1">{s.docstring}</p>
                    )}
                  </div>
                  <div className="text-right text-[11px] text-muted-foreground shrink-0">
                    <span>Lines {s.start_line} - {s.end_line}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab 4: Index Jobs & Worker Status */}
      {activeTab === "jobs" && (
        <div className="space-y-3">
          <div className="border border-border rounded-lg overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-muted/50 text-muted-foreground font-medium border-b border-border">
                <tr>
                  <th className="p-2.5">Job Type</th>
                  <th className="p-2.5">Status</th>
                  <th className="p-2.5">Progress</th>
                  <th className="p-2.5">Files Processed</th>
                  <th className="p-2.5">Started At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">
                      No background index jobs recorded.
                    </td>
                  </tr>
                ) : (
                  jobs.map((j) => (
                    <tr key={j.id} className="hover:bg-muted/30">
                      <td className="p-2.5 font-mono capitalize">{j.job_type.replace(/_/g, " ")}</td>
                      <td className="p-2.5">
                        <Badge
                          variant={
                            j.status === "completed"
                              ? "default"
                              : j.status === "failed"
                              ? "destructive"
                              : "secondary"
                          }
                          className="text-[10px] capitalize"
                        >
                          {j.status}
                        </Badge>
                      </td>
                      <td className="p-2.5">{j.progress_pct.toFixed(0)}%</td>
                      <td className="p-2.5">{j.processed_files} / {j.total_files}</td>
                      <td className="p-2.5 text-muted-foreground">
                        {j.started_at ? new Date(j.started_at).toLocaleTimeString() : "—"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
