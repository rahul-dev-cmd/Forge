"use client";

import * as React from "react";
import {
  FolderKanban,
  AlertCircle,
  HeartPulse,
  Sparkles,
  TrendingUp,
  GitPullRequest,
  Plus,
  RefreshCw,
  Inbox,
  AlertOctagon
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { StatisticCard } from "@/components/shared/StatisticCard";
import { DashboardCard } from "@/components/shared/DashboardCard";
import { LoadingErrorWrapper } from "@/components/shared/LoadingErrorWrapper";
import { ActivityItem } from "@/components/dashboard/ActivityItem";
import { ProjectCard } from "@/components/projects/ProjectCard";
import { AIInsights } from "@/components/ai/AIInsights";
import { MOCK_INSIGHTS } from "@/lib/mockData";
import { listProjects } from "@/lib/api/projects";
import { listWorkspaces } from "@/lib/api/workspaces";
import { listWorkspaceActivities } from "@/lib/api/activities";
import { toActivityItemModel, toProjectCardModel } from "@/lib/api/mappers";
import { useWorkspaceStore } from "@/store/workspaceStore";
import type { Activity, Project } from "@/lib/mockData";
import { cn } from "@/lib/utils";

export default function DashboardPage() {
  const { activeWorkspaceId, setActiveWorkspaceId } = useWorkspaceStore();
  const [componentState, setComponentState] = React.useState<"loading" | "loaded" | "error" | "empty">("loading");
  const [errorCount, setErrorCount] = React.useState(0);
  const [recentProjects, setRecentProjects] = React.useState<Project[]>([]);
  const [activities, setActivities] = React.useState<Activity[]>([]);
  const [activeCount, setActiveCount] = React.useState(0);

  const loadDashboard = React.useCallback(async () => {
    setComponentState("loading");
    try {
      let workspaceId = useWorkspaceStore.getState().activeWorkspaceId;
      if (!workspaceId) {
        const workspaces = await listWorkspaces();
        if (workspaces.length === 0) {
          setRecentProjects([]);
          setActivities([]);
          setActiveCount(0);
          setComponentState("empty");
          return;
        }
        workspaceId = workspaces[0].id;
        setActiveWorkspaceId(workspaceId);
      }

      const [{ items, total }, activityRows] = await Promise.all([
        listProjects({ workspaceId, page: 1, limit: 6, sortBy: "created_at", order: "desc" }),
        listWorkspaceActivities(workspaceId, 12),
      ]);

      setRecentProjects(items.slice(0, 3).map(toProjectCardModel));
      setActivities(activityRows.map(toActivityItemModel));
      setActiveCount(items.filter((p) => p.status === "active").length || total);
      setComponentState(items.length === 0 && activityRows.length === 0 ? "empty" : "loaded");
    } catch {
      setComponentState("error");
    }
  }, [setActiveWorkspaceId]);

  React.useEffect(() => {
    loadDashboard();
  }, [loadDashboard, activeWorkspaceId]);

  const handleRetry = () => {
    setErrorCount((prev) => prev + 1);
    loadDashboard();
  };

  const handleQuickAction = (label: string) => {
    if (label === "New Workspace") {
      window.location.href = "/workspaces";
      return;
    }
    alert(`Action: "${label}" — form wiring comes next.`);
  };

  const statsSkeleton = (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="p-5 bg-surface border border-border rounded-xl space-y-3">
          <div className="flex justify-between">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-8 w-8 rounded-lg" />
          </div>
          <Skeleton className="h-7 w-12" />
          <Skeleton className="h-3.5 w-24" />
        </div>
      ))}
    </div>
  );

  return (
    <div className="flex flex-col gap-6 max-w-[1250px] mx-auto select-none pb-12">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground">Dashboard</h1>
          <p className="text-xs text-muted-foreground">Live workspace metrics from the Forge API.</p>
        </div>
        <button
          onClick={loadDashboard}
          className="p-2 rounded-lg bg-surface border border-border hover:bg-muted cursor-pointer"
          title="Refresh dashboard"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <LoadingErrorWrapper
        state={componentState}
        onRetry={handleRetry}
        loadingSkeleton={statsSkeleton}
        errorTitle="Failed to load dashboard statistics"
        errorDescription={`Could not reach the Forge API. Attempts: ${errorCount + 1}`}
        emptyTitle="No statistics recorded"
        emptyDescription="Workspace is fresh. Create a project or connect a repository to begin."
        emptyIcon={AlertOctagon}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <StatisticCard
            title="Active Projects"
            value={String(activeCount)}
            icon={FolderKanban}
            trend="from API"
            trendType="neutral"
            description="in current workspace"
          />
          <StatisticCard
            title="Open Issues"
            value="—"
            icon={AlertCircle}
            trend="coming soon"
            trendType="neutral"
            description="requires repo sync"
          />
          <StatisticCard
            title="Repository Health"
            value="—"
            icon={HeartPulse}
            trend="coming soon"
            trendType="neutral"
            description="average test pass score"
          />
          <StatisticCard
            title="AI Copilot Tasks"
            value="—"
            icon={Sparkles}
            trend="coming soon"
            trendType="neutral"
            description="automatic code updates"
          />
          <StatisticCard
            title="Team Productivity"
            value="—"
            icon={TrendingUp}
            trend="coming soon"
            trendType="neutral"
            description="weighted velocity score"
          />
          <StatisticCard
            title="Activity Events"
            value={String(activities.length)}
            icon={GitPullRequest}
            trend="workspace feed"
            trendType="neutral"
            description="recent audit + repo events"
          />
        </div>
      </LoadingErrorWrapper>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-8 flex flex-col gap-6">
          <DashboardCard
            title="Recent Projects"
            description="ACTIVE WORKSPACE PROJECTS"
            headerActions={
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleQuickAction("New Project")}
                className="h-7 text-[10px] font-semibold gap-1 hover:bg-muted cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Project</span>
              </Button>
            }
          >
            <LoadingErrorWrapper
              state={componentState}
              onRetry={handleRetry}
              loadingSkeleton={
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-5 bg-surface border border-border rounded-xl space-y-4">
                    <Skeleton className="h-4 w-1/3" />
                    <Skeleton className="h-6 w-2/3" />
                    <Skeleton className="h-2 w-full" />
                  </div>
                  <div className="p-5 bg-surface border border-border rounded-xl space-y-4">
                    <Skeleton className="h-4 w-1/3" />
                    <Skeleton className="h-6 w-2/3" />
                    <Skeleton className="h-2 w-full" />
                  </div>
                </div>
              }
              emptyTitle="No Projects connected"
              emptyDescription="No active repositories connected to this workspace."
              emptyIcon={Inbox}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {recentProjects.map((project) => (
                  <ProjectCard key={project.id} project={project} />
                ))}
              </div>
            </LoadingErrorWrapper>
          </DashboardCard>

          <DashboardCard title="Activity Feed" description="WORKSPACE AUDIT TIMELINE">
            <LoadingErrorWrapper
              state={componentState}
              onRetry={handleRetry}
              loadingSkeleton={
                <div className="space-y-4">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="flex gap-4">
                      <Skeleton className="w-8 h-8 rounded-lg shrink-0" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-3.5 w-1/3" />
                      </div>
                    </div>
                  ))}
                </div>
              }
              emptyTitle="No activities logged"
              emptyDescription="Commit logs, AI audits, and repository updates will show up here."
              emptyIcon={Inbox}
            >
              <div className="flex flex-col pl-1.5 mt-2">
                {activities.map((activity, idx) => (
                  <ActivityItem
                    key={activity.id}
                    activity={activity}
                    isLast={idx === activities.length - 1}
                  />
                ))}
              </div>
            </LoadingErrorWrapper>
          </DashboardCard>
        </div>

        <div className="lg:col-span-4 flex flex-col gap-6">
          <DashboardCard title="Quick Actions" description="EXECUTE LOGICAL WORKFLOW CHECKS">
            <div className="grid grid-cols-2 gap-2.5">
              {[
                { label: "New Project", color: "hover:bg-blue-500/5 hover:text-blue-500 hover:border-blue-500/20" },
                { label: "New Workspace", color: "hover:bg-purple-500/5 hover:text-purple-500 hover:border-purple-500/20" },
                { label: "Connect Repo", color: "hover:bg-success/5 hover:text-success hover:border-success/20" },
                { label: "Invite Team", color: "hover:bg-warning/5 hover:text-warning hover:border-warning/20" },
              ].map((btn) => (
                <button
                  key={btn.label}
                  onClick={() => handleQuickAction(btn.label)}
                  className={cn(
                    "p-3 rounded-lg border border-border bg-surface text-xs font-semibold text-foreground text-center select-none shadow-3xs cursor-pointer transition-all duration-200 hover:-translate-y-0.5",
                    btn.color
                  )}
                >
                  {btn.label}
                </button>
              ))}
            </div>
          </DashboardCard>

          <DashboardCard title="AI Copilot Insights" description="ACTIONABLE AI RECOMMENDATIONS" gradient>
            <AIInsights insights={MOCK_INSIGHTS.slice(0, 3)} />
          </DashboardCard>
        </div>
      </div>
    </div>
  );
}
