"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  GitFork,
  GitBranch,
  Code2,
  AlertTriangle,
  RefreshCw,
  Inbox
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { DashboardCard } from "@/components/shared/DashboardCard";
import { LoadingErrorWrapper } from "@/components/shared/LoadingErrorWrapper";
import { MockFileTree } from "@/components/projects/MockFileTree";
import { ActivityItem } from "@/components/dashboard/ActivityItem";
import { AIInsights } from "@/components/ai/AIInsights";
import { MOCK_PROJECTS, MOCK_ACTIVITIES, MOCK_INSIGHTS, MOCK_FILE_TREES } from "@/lib/mockData";

export default function ProjectDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [componentState, setComponentState] = React.useState<"loading" | "loaded" | "error" | "empty">("loading");

  const triggerLoading = () => {
    setComponentState("loading");
    const timer = setTimeout(() => {
      setComponentState("loaded");
    }, 700);
    return () => clearTimeout(timer);
  };

  React.useEffect(() => {
    triggerLoading();
  }, [id]);

  const handleRetry = () => {
    triggerLoading();
  };

  // Find project
  const project = MOCK_PROJECTS.find((p) => p.id === id);

  // If project not found and we are not in loading/error state, fallback to first project or show error
  if (!project && componentState === "loaded") {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-border bg-surface rounded-xl max-w-md mx-auto gap-4">
        <AlertTriangle className="w-10 h-10 text-destructive" />
        <h2 className="text-sm font-bold text-foreground">Project Not Found</h2>
        <p className="text-xs text-muted-foreground leading-normal">
          The requested project ID &quot;{id}&quot; does not exist or has been deleted.
        </p>
        <Button size="sm" onClick={() => router.push("/projects")} className="h-9 px-4 bg-blue-600 text-white font-semibold">
          Back to Projects List
        </Button>
      </div>
    );
  }

  // Get project data fallbacks if not found yet during loading
  const currentProject = project || MOCK_PROJECTS[0];

  // Filter activities matching this project (some commits contain repository path)
  const projectActivities = MOCK_ACTIVITIES.filter(
    (act) => act.message.toLowerCase().includes(currentProject.id) ||
             act.message.toLowerCase().includes(currentProject.name.toLowerCase()) ||
             act.type === "ai" || act.type === "sprint"
  );

  // AI insights matching this project
  const projectInsights = MOCK_INSIGHTS.slice(0, currentProject.priority === "high" ? 3 : 2);

  // File tree matching this project
  const fileTree = MOCK_FILE_TREES[currentProject.id] || [];

  const getStatusColor = (status: typeof currentProject.status) => {
    switch (status) {
      case "active":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "completed":
        return "bg-success/10 text-success border-success/20";
      case "on_hold":
        return "bg-warning/10 text-warning border-warning/20";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-[1200px] mx-auto select-none pb-12">
      {/* Top Banner Control Panel for testing mock UI states */}
      <div className="p-3 bg-muted/20 border border-border rounded-xl flex items-center justify-between gap-3 text-[10px] max-sm:flex-col max-sm:items-start">
        <div className="flex items-center gap-2">
          <button
            onClick={() => router.push("/projects")}
            className="h-8 px-2.5 bg-surface border border-border text-[10px] font-bold text-foreground rounded-lg flex items-center gap-1 hover:bg-muted cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>All Projects</span>
          </button>
          <span className="font-bold text-muted-foreground uppercase tracking-widest pl-2 border-l border-border/80">Sandbox controls:</span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setComponentState("loading")}
            className={`px-2 py-0.5 rounded font-semibold ${componentState === "loading" ? "bg-blue-600 text-white" : "bg-surface border border-border"}`}
          >
            Loading
          </button>
          <button
            onClick={() => setComponentState("loaded")}
            className={`px-2 py-0.5 rounded font-semibold ${componentState === "loaded" ? "bg-blue-600 text-white" : "bg-surface border border-border"}`}
          >
            Loaded
          </button>
          <button
            onClick={() => setComponentState("empty")}
            className={`px-2 py-0.5 rounded font-semibold ${componentState === "empty" ? "bg-blue-600 text-white" : "bg-surface border border-border"}`}
          >
            Empty File Tree
          </button>
          <button
            onClick={() => setComponentState("error")}
            className={`px-2 py-0.5 rounded font-semibold ${componentState === "error" ? "bg-destructive text-white" : "bg-surface border border-border"}`}
          >
            Error State
          </button>
        </div>
      </div>

      <LoadingErrorWrapper
        state={componentState === "loading" ? "loading" : "loaded"}
        onRetry={handleRetry}
        loadingSkeleton={
          <div className="space-y-6">
            <div className="flex justify-between items-start">
              <div className="space-y-2 flex-1">
                <Skeleton className="h-7 w-1/3" />
                <Skeleton className="h-4 w-1/2" />
              </div>
              <Skeleton className="h-9 w-24" />
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
            </div>
            <Skeleton className="h-60 w-full" />
          </div>
        }
      >
        {/* Project Summary Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border/60 pb-5">
          <div className="flex flex-col gap-1.5 text-left">
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="text-xl font-bold tracking-tight text-foreground">
                {currentProject.name}
              </h1>
              <span className={`text-[9px] font-black uppercase tracking-widest border px-2 py-0.5 rounded-md ${getStatusColor(currentProject.status)}`}>
                {currentProject.status.replace("_", " ")}
              </span>
            </div>
            <p className="text-xs text-muted-foreground max-w-xl leading-relaxed">
              {currentProject.description}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={triggerLoading}
              className="p-2 rounded-lg bg-surface border border-border hover:bg-muted text-muted-foreground hover:text-foreground cursor-pointer transition-all"
              title="Refresh project indices"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <Button
              size="sm"
              onClick={() => alert(`Mock: Syncing repository ${currentProject.repository}`)}
              className="h-9 px-3.5 border border-border bg-surface text-xs font-semibold rounded-lg text-foreground hover:bg-muted cursor-pointer"
            >
              <GitFork className="w-3.5 h-3.5" />
              <span>Sync Files</span>
            </Button>
          </div>
        </div>

        {/* Project Statistics Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <div className="p-4 bg-surface border border-border rounded-xl flex flex-col gap-1 text-left shadow-3xs">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">Lines Of Code</span>
            <span className="text-lg font-black text-foreground">{currentProject.linesOfCode}</span>
          </div>
          <div className="p-4 bg-surface border border-border rounded-xl flex flex-col gap-1 text-left shadow-3xs">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">Test Coverage</span>
            <span className="text-lg font-black text-foreground">{currentProject.testCoverage}</span>
          </div>
          <div className="p-4 bg-surface border border-border rounded-xl flex flex-col gap-1 text-left shadow-3xs">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">Open Issues</span>
            <span className="text-lg font-black text-foreground">{currentProject.openIssues}</span>
          </div>
          <div className="p-4 bg-surface border border-border rounded-xl flex flex-col gap-1 text-left shadow-3xs">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">Pull Requests</span>
            <span className="text-lg font-black text-foreground">{currentProject.pullRequests}</span>
          </div>
          <div className="p-4 bg-surface border border-border rounded-xl flex flex-col gap-1 text-left shadow-3xs">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">AI Copilot Tasks</span>
            <span className="text-lg font-black text-foreground">{currentProject.aiTasks}</span>
          </div>
          <div className="p-4 bg-surface border border-border rounded-xl flex flex-col gap-1 text-left shadow-3xs">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">Productivity Score</span>
            <span className="text-lg font-black text-blue-500">{currentProject.productivityScore}</span>
          </div>
        </div>

        {/* Repository details row */}
        <div className="p-4 bg-muted/20 border border-border rounded-xl flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 text-muted-foreground font-semibold">
              <Code2 className="w-4 h-4 text-blue-500" />
              <span>Git Repository:</span>
            </div>
            <a
              href={`https://${currentProject.repository}`}
              target="_blank"
              rel="noreferrer"
              className="font-mono text-xs text-blue-600 hover:text-blue-500 hover:underline"
            >
              {currentProject.repository}
            </a>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 text-muted-foreground font-semibold">
              <GitBranch className="w-4 h-4 text-blue-500" />
              <span>Index Branch:</span>
            </div>
            <span className="bg-muted px-2 py-0.5 rounded-md border border-border font-mono text-[11px] font-bold text-foreground">
              {currentProject.branch}
            </span>
          </div>
        </div>

        {/* Linear Progress Card */}
        <div className="p-5 bg-surface border border-border rounded-xl flex flex-col gap-3 shadow-3xs">
          <div className="flex justify-between items-baseline text-xs">
            <span className="text-muted-foreground font-semibold">Development Target Completion Milestone</span>
            <span className="font-bold text-foreground">{currentProject.progress}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-muted overflow-hidden relative border border-border/40">
            <div
              style={{ width: `${currentProject.progress}%` }}
              className="h-full rounded-full bg-blue-600 dark:bg-blue-500 transition-all duration-500 ease-out"
            />
          </div>
        </div>

        {/* Grid: File tree layout & AI summary */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* File Tree Explorer (8 columns) */}
          <div className="lg:col-span-8 flex flex-col gap-4">
            <div className="text-left">
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground select-none">
                File System Directory Tree
              </h3>
            </div>
            <LoadingErrorWrapper
              state={componentState === "empty" ? "empty" : componentState === "error" ? "error" : "loaded"}
              onRetry={handleRetry}
              emptyTitle="No Repository Files Connected"
              emptyDescription="No indexed directories were discovered. Click Sync Files to scan repository branch contents."
              emptyIcon={Inbox}
              errorTitle="Failed to index repository directory"
              errorDescription="Connection handshake with repository server timed out."
            >
              <MockFileTree files={fileTree} />
            </LoadingErrorWrapper>
          </div>

          {/* AI summaries and activity (4 columns) */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            {/* AI Summary Card */}
            <DashboardCard title="AI Copilot Summary" description="COMPILER AUDIT INSIGHTS" gradient>
              <LoadingErrorWrapper
                state={componentState === "error" ? "error" : "loaded"}
                onRetry={handleRetry}
                errorTitle="Failed to fetch AI insights"
                errorDescription="Index database timed out during summaries mapping lookup."
              >
                {projectInsights.length === 0 ? (
                  <div className="p-4 text-center text-xs text-muted-foreground">
                    No active suggestions for this repository.
                  </div>
                ) : (
                  <AIInsights insights={projectInsights} />
                )}
              </LoadingErrorWrapper>
            </DashboardCard>

            {/* Project activity */}
            <DashboardCard title="Project Activity" description="RECENT COMMITS AND AUDITS">
              <LoadingErrorWrapper
                state={componentState === "error" ? "error" : "loaded"}
                onRetry={handleRetry}
                errorTitle="Failed to index activity logs"
                errorDescription="Connection socket failure."
              >
                {projectActivities.length === 0 ? (
                  <div className="p-6 text-center text-xs text-muted-foreground">
                    No activities logged for this project.
                  </div>
                ) : (
                  <div className="flex flex-col pl-1 mt-1">
                    {projectActivities.map((act, idx) => (
                      <ActivityItem
                        key={act.id}
                        activity={act}
                        isLast={idx === projectActivities.length - 1}
                      />
                    ))}
                  </div>
                )}
              </LoadingErrorWrapper>
            </DashboardCard>
          </div>
        </div>
      </LoadingErrorWrapper>
    </div>
  );
}
