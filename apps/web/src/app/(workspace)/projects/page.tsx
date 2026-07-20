"use client";

import * as React from "react";
import { Plus, RefreshCw, FolderKanban, Inbox } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { ProjectCard } from "@/components/projects/ProjectCard";
import { ProjectFilters } from "@/components/projects/ProjectFilters";
import { LoadingErrorWrapper } from "@/components/shared/LoadingErrorWrapper";
import { listProjects, ProjectDto } from "@/lib/api/projects";
import { listWorkspaces } from "@/lib/api/workspaces";
import { toProjectCardModel } from "@/lib/api/mappers";
import { useWorkspaceStore } from "@/store/workspaceStore";
import type { Project } from "@/lib/mockData";

export default function ProjectsPage() {
  const { activeWorkspaceId, setActiveWorkspaceId } = useWorkspaceStore();
  const [componentState, setComponentState] = React.useState<"loading" | "loaded" | "error" | "empty">("loading");
  const [projects, setProjects] = React.useState<Project[]>([]);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("all");
  const [priorityFilter, setPriorityFilter] = React.useState("all");
  const [sortBy, setSortBy] = React.useState("last_updated");
  const [errorCount, setErrorCount] = React.useState(0);

  const loadProjects = React.useCallback(async () => {
    setComponentState("loading");
    try {
      let workspaceId = useWorkspaceStore.getState().activeWorkspaceId;
      if (!workspaceId) {
        const workspaces = await listWorkspaces();
        if (workspaces.length === 0) {
          setProjects([]);
          setComponentState("empty");
          return;
        }
        workspaceId = workspaces[0].id;
        setActiveWorkspaceId(workspaceId);
      }

      const sortMap: Record<string, string> = {
        last_updated: "created_at",
        name: "name",
        progress_desc: "created_at",
        progress_asc: "created_at",
        created_at: "created_at",
      };

      const { items } = await listProjects({
        workspaceId,
        query: searchQuery || undefined,
        status: statusFilter,
        priority: priorityFilter,
        sortBy: sortMap[sortBy] || "created_at",
        order: sortBy === "name" || sortBy === "progress_asc" ? "asc" : "desc",
        page: 1,
        limit: 50,
      });

      setProjects(items.map((p: ProjectDto) => toProjectCardModel(p)));
      setComponentState(items.length === 0 ? "empty" : "loaded");
    } catch {
      setComponentState("error");
    }
  }, [searchQuery, statusFilter, priorityFilter, sortBy, setActiveWorkspaceId]);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      loadProjects();
    }, 200);
    return () => clearTimeout(timer);
  }, [loadProjects, activeWorkspaceId]);

  const handleRetry = () => {
    setErrorCount((prev) => prev + 1);
    loadProjects();
  };

  const handleClearFilters = () => {
    setSearchQuery("");
    setStatusFilter("all");
    setPriorityFilter("all");
    setSortBy("last_updated");
  };

  const hasFiltersActive =
    searchQuery.trim() !== "" ||
    statusFilter !== "all" ||
    priorityFilter !== "all" ||
    sortBy !== "last_updated";

  return (
    <div className="flex flex-col gap-6 max-w-[1200px] mx-auto select-none pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex flex-col gap-1 text-left">
          <h1 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <FolderKanban className="w-5 h-5 text-blue-500" />
            <span>Workspace Projects</span>
          </h1>
          <p className="text-xs text-muted-foreground">
            Explore and filter development repositories connected to the Forge AI core index.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadProjects}
            className="p-2 rounded-lg bg-surface border border-border hover:bg-muted text-muted-foreground hover:text-foreground cursor-pointer transition-all"
            title="Refresh list"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <Button
            size="sm"
            onClick={() => alert("Open Create Project drawer (wire form in next milestone)")}
            className="h-9 px-3.5 bg-blue-600 hover:bg-blue-600/90 text-white font-semibold flex items-center gap-1.5 shadow-2xs rounded-lg cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Project</span>
          </Button>
        </div>
      </div>

      <ProjectFilters
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        priorityFilter={priorityFilter}
        setPriorityFilter={setPriorityFilter}
        sortBy={sortBy}
        setSortBy={setSortBy}
        onClearFilters={handleClearFilters}
        hasFiltersActive={hasFiltersActive}
      />

      <LoadingErrorWrapper
        state={componentState}
        onRetry={handleRetry}
        loadingSkeleton={
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="p-5 bg-surface border border-border rounded-xl space-y-4">
                <div className="flex justify-between">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-3 w-16" />
                </div>
                <Skeleton className="h-5 w-2/3" />
                <Skeleton className="h-3.5 w-full" />
                <Skeleton className="h-1.5 w-full" />
                <div className="flex justify-between pt-2">
                  <Skeleton className="h-5 w-16 rounded-full" />
                  <Skeleton className="h-3.5 w-16" />
                </div>
              </div>
            ))}
          </div>
        }
        emptyTitle={hasFiltersActive ? "No matching projects" : "No Projects indexing"}
        emptyDescription={
          hasFiltersActive
            ? "Try resetting filters or adjusting search queries to locate files."
            : "Create a project in this workspace or connect a repository to begin indexing."
        }
        emptyIcon={Inbox}
        errorTitle="Failed to sync project list"
        errorDescription={`Could not load projects from the API. Attempt index: ${errorCount + 1}`}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      </LoadingErrorWrapper>
    </div>
  );
}
