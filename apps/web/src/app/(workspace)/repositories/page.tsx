"use client";

import * as React from "react";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Github, Plus, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { LoadingErrorWrapper } from "@/components/shared/LoadingErrorWrapper";
import { Skeleton } from "@/components/ui/Skeleton";
import { RepositoryCard } from "@/components/repositories/RepositoryCard";
import { RepositoryFilters } from "@/components/repositories/RepositoryFilters";
import { ImportWizard } from "@/components/repositories/ImportWizard";
import { listRepositories, syncRepository } from "@/lib/api/repositories";
import { completeGitHubCallback } from "@/lib/api/github";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { listWorkspaces } from "@/lib/api/workspaces";

function RepositoriesPageInner() {
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const activeWorkspaceId = useWorkspaceStore((s) => s.activeWorkspaceId);
  const setActiveWorkspaceId = useWorkspaceStore((s) => s.setActiveWorkspaceId);

  const [query, setQuery] = React.useState("");
  const [debouncedQuery, setDebouncedQuery] = React.useState("");
  const [syncStatus, setSyncStatus] = React.useState("all");
  const [sortBy, setSortBy] = React.useState("updated_at");
  const [order, setOrder] = React.useState<"asc" | "desc">("desc");
  const [page, setPage] = React.useState(1);
  const [importOpen, setImportOpen] = React.useState(false);
  const [syncingId, setSyncingId] = React.useState<string | null>(null);
  const [banner, setBanner] = React.useState<string | null>(null);

  React.useEffect(() => {
    const t = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(t);
  }, [query]);

  const workspacesQuery = useQuery({
    queryKey: ["workspaces"],
    queryFn: listWorkspaces,
  });

  React.useEffect(() => {
    if (!activeWorkspaceId && workspacesQuery.data?.[0]) {
      setActiveWorkspaceId(workspacesQuery.data[0].id);
    }
  }, [activeWorkspaceId, workspacesQuery.data, setActiveWorkspaceId]);

  const workspaceId = activeWorkspaceId ?? workspacesQuery.data?.[0]?.id ?? "";

  React.useEffect(() => {
    if (searchParams.get("import") === "1") {
      setImportOpen(true);
    }
    const github = searchParams.get("github");
    if (github !== "callback") return;
    const code = searchParams.get("code") ?? undefined;
    const installationId = searchParams.get("installation_id") ?? undefined;
    if (!code && !installationId) return;

    let cancelled = false;
    (async () => {
      try {
        await completeGitHubCallback({
          code,
          installationId,
          workspaceId: workspaceId || undefined,
        });
        if (!cancelled) {
          setBanner(
            installationId
              ? "GitHub App installed successfully."
              : "GitHub account connected successfully."
          );
          setImportOpen(true);
          queryClient.invalidateQueries({ queryKey: ["github-installations"] });
        }
      } catch (err) {
        if (!cancelled) {
          setBanner(err instanceof Error ? err.message : "GitHub connection failed");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [searchParams, workspaceId, queryClient]);

  const reposQuery = useQuery({
    queryKey: [
      "repositories",
      workspaceId,
      debouncedQuery,
      syncStatus,
      sortBy,
      order,
      page,
    ],
    queryFn: () =>
      listRepositories({
        workspaceId,
        query: debouncedQuery || undefined,
        syncStatus: syncStatus === "all" ? undefined : syncStatus,
        sortBy,
        order,
        page,
        limit: 12,
      }),
    enabled: !!workspaceId,
    refetchInterval: (q) => {
      const items = q.state.data?.items ?? [];
      const busy = items.some((r) => r.sync_status === "syncing" || r.sync_status === "queued");
      return busy ? 3000 : false;
    },
  });

  const syncMutation = useMutation({
    mutationFn: (id: string) => syncRepository(id),
    onMutate: (id) => setSyncingId(id),
    onSettled: () => {
      setSyncingId(null);
      queryClient.invalidateQueries({ queryKey: ["repositories"] });
    },
  });

  const total = reposQuery.data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / 12));

  let state: "loading" | "loaded" | "error" | "empty" = "loaded";
  if (!workspaceId || reposQuery.isLoading) state = "loading";
  else if (reposQuery.isError) state = "error";
  else if ((reposQuery.data?.items.length ?? 0) === 0) state = "empty";

  return (
    <div className="flex flex-col gap-6 max-w-5xl select-none pb-10">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-border pb-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Github className="w-5 h-5" />
            Repositories
          </h1>
          <p className="text-xs text-muted-foreground">
            Browse connected GitHub repositories, sync metadata, and prepare for AI indexing.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="h-9 gap-1.5"
            onClick={() => reposQuery.refetch()}
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </Button>
          <Button size="sm" className="h-9 gap-1.5" onClick={() => setImportOpen(true)}>
            <Plus className="w-3.5 h-3.5" />
            Import
          </Button>
        </div>
      </div>

      {banner ? (
        <div className="rounded-md border border-primary/20 bg-primary/5 px-3 py-2 text-xs text-foreground">
          {banner}
        </div>
      ) : null}

      <RepositoryFilters
        query={query}
        syncStatus={syncStatus}
        sortBy={sortBy}
        order={order}
        onQueryChange={(v) => {
          setQuery(v);
          setPage(1);
        }}
        onSyncStatusChange={(v) => {
          setSyncStatus(v);
          setPage(1);
        }}
        onSortByChange={setSortBy}
        onOrderChange={setOrder}
      />

      <LoadingErrorWrapper
        state={state === "empty" ? "loaded" : state}
        onRetry={() => reposQuery.refetch()}
        loadingSkeleton={
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-36 w-full rounded-lg" />
            ))}
          </div>
        }
      >
        {state === "empty" ? (
          <EmptyState
            title="Connect your first repository"
            description="Install the Forge GitHub App, then import repositories. Forge syncs metadata only — no cloning."
            icon={Github}
            actionText="Import from GitHub"
            onActionClick={() => setImportOpen(true)}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {(reposQuery.data?.items ?? []).map((repo) => (
              <RepositoryCard
                key={repo.id}
                repository={repo}
                syncing={syncingId === repo.id}
                onSync={(repoId) => syncMutation.mutate(repoId)}
              />
            ))}
          </div>
        )}
      </LoadingErrorWrapper>

      {totalPages > 1 && state === "loaded" ? (
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            Page {page} of {totalPages} · {total} repositories
          </span>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next
            </Button>
          </div>
        </div>
      ) : null}

      {workspaceId ? (
        <ImportWizard open={importOpen} onOpenChange={setImportOpen} workspaceId={workspaceId} />
      ) : null}
    </div>
  );
}

export default function RepositoriesPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-5xl space-y-3 p-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-36 w-full" />
        </div>
      }
    >
      <RepositoriesPageInner />
    </Suspense>
  );
}
