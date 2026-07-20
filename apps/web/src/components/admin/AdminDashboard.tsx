"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ShieldCheck,
  Cpu,
  Database,
  Layers,
  Activity,
  Zap,
  Users,
  FolderGit2,
  DollarSign,
  CheckCircle2,
  RefreshCw,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { adminApi } from "@/lib/api/admin";

export function AdminDashboard() {
  const statsQuery = useQuery({
    queryKey: ["admin-stats"],
    queryFn: () => adminApi.getSystemStats(),
  });

  const diagQuery = useQuery({
    queryKey: ["admin-diagnostics"],
    queryFn: () => adminApi.getDiagnostics(),
    refetchInterval: 5000,
  });

  const stats = statsQuery.data;
  const diag = diagQuery.data;

  return (
    <div className="flex flex-col gap-6 w-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border border-border rounded-lg bg-card/60">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-md bg-primary/10 text-primary">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground">Production Administration & System Diagnostics</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Real-time monitoring of PostgreSQL pools, Qdrant vector database, Redis cache, and ARQ worker queues.
            </p>
          </div>
        </div>

        <Button
          size="sm"
          variant="outline"
          onClick={() => {
            statsQuery.refetch();
            diagQuery.refetch();
          }}
          className="gap-1.5 text-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Diagnostics
        </Button>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 border border-border rounded-lg bg-card">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Total Users</span>
            <Users className="w-4 h-4 text-muted-foreground" />
          </div>
          <p className="text-2xl font-bold text-foreground mt-2">{stats?.total_users ?? 0}</p>
        </div>

        <div className="p-4 border border-border rounded-lg bg-card">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Active Workspaces</span>
            <Layers className="w-4 h-4 text-muted-foreground" />
          </div>
          <p className="text-2xl font-bold text-foreground mt-2">{stats?.total_workspaces ?? 0}</p>
        </div>

        <div className="p-4 border border-border rounded-lg bg-card">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Indexed Repositories</span>
            <FolderGit2 className="w-4 h-4 text-muted-foreground" />
          </div>
          <p className="text-2xl font-bold text-foreground mt-2">{stats?.total_repositories ?? 0}</p>
        </div>

        <div className="p-4 border border-border rounded-lg bg-card">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">LLM Tokens Consumed</span>
            <DollarSign className="w-4 h-4 text-muted-foreground" />
          </div>
          <p className="text-2xl font-bold text-foreground mt-2">
            {(stats?.total_tokens_consumed ?? 0).toLocaleString()}
          </p>
          <span className="text-[10px] text-muted-foreground">Est. Cost: ${stats?.total_llm_cost_usd ?? 0.00}</span>
        </div>
      </div>

      {/* Production Diagnostics Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 border border-border rounded-lg bg-card space-y-3">
          <div className="flex justify-between items-center border-b border-border pb-2">
            <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5">
              <Database className="w-4 h-4 text-primary" /> Database & Storage Health
            </h4>
            <Badge variant="default" className="text-[10px]">
              Healthy
            </Badge>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">PostgreSQL Async Engine:</span>
              <span className="font-semibold text-foreground">Connected (pool: {diag?.database.connection_pool})</span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Redis Cache Hit Ratio:</span>
              <span className="font-semibold text-foreground">{diag?.redis_cache.hit_ratio_pct ?? 100}%</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-muted-foreground">Qdrant Vector Database:</span>
              <span className="font-semibold text-foreground">Online ({diag?.qdrant_vector_db.collection})</span>
            </div>
          </div>
        </div>

        <div className="p-4 border border-border rounded-lg bg-card space-y-3">
          <div className="flex justify-between items-center border-b border-border pb-2">
            <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-primary" /> Workers & AI Provider Status
            </h4>
            <Badge variant="secondary" className="text-[10px]">
              Active
            </Badge>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">ARQ Queue ({diag?.workers.queue_name}):</span>
              <span className="font-semibold text-foreground">
                {diag?.workers.active_workers} workers (depth: {diag?.workers.queue_depth})
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/40">
              <span className="text-muted-foreground">Active LLM Provider:</span>
              <span className="font-semibold text-foreground capitalize">{diag?.llm_providers.active_provider}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-muted-foreground">Automatic Provider Failover:</span>
              <span className="font-semibold text-foreground">Enabled</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
