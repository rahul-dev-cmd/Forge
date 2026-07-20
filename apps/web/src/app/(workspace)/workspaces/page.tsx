"use client";

import * as React from "react";
import { Building, ArrowRight, UserPlus, Plus, RefreshCw } from "lucide-react";
import Link from "next/link";
import { listWorkspaces, createWorkspace, WorkspaceDto } from "@/lib/api/workspaces";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { useUser } from "@/providers/AuthProvider";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { LoadingErrorWrapper } from "@/components/shared/LoadingErrorWrapper";
import { apiClient } from "@/lib/api/client";

export default function WorkspacesPage() {
  const { user } = useUser();
  const { activeWorkspaceId, setActiveWorkspaceId } = useWorkspaceStore();
  const [workspaces, setWorkspaces] = React.useState<WorkspaceDto[]>([]);
  const [state, setState] = React.useState<"loading" | "loaded" | "error" | "empty">("loading");
  const [creating, setCreating] = React.useState(false);

  const load = React.useCallback(async () => {
    setState("loading");
    try {
      const data = await listWorkspaces();
      setWorkspaces(data);
      const current = useWorkspaceStore.getState().activeWorkspaceId;
      if (!current && data.length > 0) {
        setActiveWorkspaceId(data[0].id);
      }
      setState(data.length === 0 ? "empty" : "loaded");
    } catch {
      setState("error");
    }
  }, [setActiveWorkspaceId]);

  React.useEffect(() => {
    load();
  }, [load]);

  const handleCreate = async () => {
    if (!user) return;
    const name = window.prompt("Workspace name");
    if (!name?.trim()) return;

    setCreating(true);
    try {
      // Resolve current user id from API (/users/me returns the user model directly)
      const me = await apiClient.get<{ id: string }>("/users/me");
      const slug = name
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "");

      const created = await createWorkspace({
        owner_id: me.id,
        name: name.trim(),
        slug: slug || `ws-${Date.now()}`,
      });
      setActiveWorkspaceId(created.id);
      await load();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create workspace");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-4xl select-none">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Workspaces</h1>
          <p className="text-sm text-muted-foreground">
            Manage your development spaces and team collaboration groups.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            className="p-2 rounded-lg bg-surface border border-border hover:bg-muted text-muted-foreground"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <Button size="sm" onClick={handleCreate} disabled={creating} className="h-9 gap-1.5">
            <Plus className="w-3.5 h-3.5" />
            New Workspace
          </Button>
        </div>
      </div>

      <LoadingErrorWrapper
        state={state}
        onRetry={load}
        loadingSkeleton={
          <div className="grid grid-cols-1 gap-4">
            {Array.from({ length: 2 }).map((_, i) => (
              <div key={i} className="p-5 rounded-lg border border-border bg-surface space-y-3">
                <Skeleton className="h-10 w-10 rounded-md" />
                <Skeleton className="h-4 w-1/3" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            ))}
          </div>
        }
        emptyTitle="No workspaces yet"
        emptyDescription="Create a workspace to start organizing projects and repositories."
        emptyIcon={Building}
        errorTitle="Failed to load workspaces"
        errorDescription="Could not reach the Forge API. Confirm the backend is running."
      >
        <div className="grid grid-cols-1 gap-4">
          {workspaces.map((ws) => (
            <div
              key={ws.id}
              className="p-5 rounded-lg border border-border bg-surface flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:border-muted-foreground/30 transition-all shadow-3xs"
            >
              <div className="flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-md bg-muted border border-border flex items-center justify-center text-primary">
                  <Building className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-sm text-foreground">{ws.name}</h3>
                    {activeWorkspaceId === ws.id && (
                      <span className="bg-primary/10 border border-primary/20 text-primary text-[10px] font-semibold px-2 py-0.5 rounded">
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Role:{" "}
                    <span className="font-medium text-foreground capitalize">{ws.role || "member"}</span>
                    {ws.slug ? ` • ${ws.slug}` : null}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 self-end sm:self-center">
                <button
                  disabled
                  className="h-9 px-3 border border-border bg-surface text-xs font-semibold rounded-md flex items-center gap-1.5 cursor-not-allowed opacity-60"
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  <span>Invite</span>
                </button>
                <button
                  onClick={() => setActiveWorkspaceId(ws.id)}
                  className="h-9 px-3 border border-border bg-surface hover:bg-muted text-xs font-semibold rounded-md"
                >
                  Set Active
                </button>
                <Link
                  href="/dashboard"
                  onClick={() => setActiveWorkspaceId(ws.id)}
                  className="h-9 px-4 bg-primary text-primary-foreground text-xs font-semibold rounded-md flex items-center gap-1.5 hover:opacity-90 transition-all shadow-3xs"
                >
                  <span>Enter</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </LoadingErrorWrapper>
    </div>
  );
}
