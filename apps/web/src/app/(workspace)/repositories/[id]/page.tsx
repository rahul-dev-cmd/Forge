"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  RefreshCw,
  Unplug,
  GitBranch,
  GitCommit,
  GitPullRequest,
  CircleDot,
  Users,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { LoadingErrorWrapper } from "@/components/shared/LoadingErrorWrapper";
import {
  getRepository,
  getRepositoryStatus,
  syncRepository,
  disconnectRepository,
  listBranches,
  listCommits,
  listPullRequests,
  listIssues,
  listContributors,
} from "@/lib/api/repositories";
import { RepositoryIntelligence } from "@/components/repositories/RepositoryIntelligence";
import { AIKnowledgeDashboard } from "@/components/repositories/AIKnowledgeDashboard";



export default function RepositoryDetailsPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const queryClient = useQueryClient();

  const repoQuery = useQuery({
    queryKey: ["repository", id],
    queryFn: () => getRepository(id),
    enabled: !!id,
  });

  const statusQuery = useQuery({
    queryKey: ["repository-status", id],
    queryFn: () => getRepositoryStatus(id),
    enabled: !!id,
    refetchInterval: (q) => {
      const status = q.state.data?.sync_status;
      return status === "syncing" || status === "queued" ? 2500 : false;
    },
  });

  const branchesQuery = useQuery({
    queryKey: ["repository-branches", id],
    queryFn: () => listBranches(id),
    enabled: !!id,
  });
  const commitsQuery = useQuery({
    queryKey: ["repository-commits", id],
    queryFn: () => listCommits(id),
    enabled: !!id,
  });
  const prsQuery = useQuery({
    queryKey: ["repository-prs", id],
    queryFn: () => listPullRequests(id),
    enabled: !!id,
  });
  const issuesQuery = useQuery({
    queryKey: ["repository-issues", id],
    queryFn: () => listIssues(id),
    enabled: !!id,
  });
  const contributorsQuery = useQuery({
    queryKey: ["repository-contributors", id],
    queryFn: () => listContributors(id),
    enabled: !!id,
  });

  const syncMutation = useMutation({
    mutationFn: () => syncRepository(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repository", id] });
      queryClient.invalidateQueries({ queryKey: ["repository-status", id] });
    },
  });

  const disconnectMutation = useMutation({
    mutationFn: () => disconnectRepository(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repository", id] });
    },
  });

  const repo = repoQuery.data;
  const state = repoQuery.isLoading
    ? "loading"
    : repoQuery.isError
      ? "error"
      : !repo
        ? "empty"
        : "loaded";

  return (
    <div className="flex flex-col gap-6 max-w-5xl select-none pb-12">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Link href="/repositories" className="inline-flex items-center gap-1 hover:text-foreground">
          <ArrowLeft className="w-3.5 h-3.5" />
          Repositories
        </Link>
      </div>

      <LoadingErrorWrapper
        state={state}
        onRetry={() => repoQuery.refetch()}
        loadingSkeleton={
          <div className="space-y-3">
            <Skeleton className="h-8 w-1/2" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-40 w-full" />
          </div>
        }
      >
        {repo ? (
          <>
            <div className="flex flex-col sm:flex-row justify-between gap-4 border-b border-border pb-4">
              <div className="flex flex-col gap-2 min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-xl font-bold tracking-tight text-foreground truncate">
                    {repo.full_name || repo.name}
                  </h1>
                  <Badge variant="outline" className="text-[10px] capitalize">
                    {repo.visibility}
                  </Badge>
                  <Badge className="text-[10px] capitalize">{repo.sync_status}</Badge>
                  <Badge variant="secondary" className="text-[10px] capitalize">
                    {repo.connection_status}
                  </Badge>
                </div>
                {repo.description ? (
                  <p className="text-xs text-muted-foreground">{repo.description}</p>
                ) : null}
                <div className="flex flex-wrap gap-3 text-[11px] text-muted-foreground">
                  <span className="inline-flex items-center gap-1">
                    <GitBranch className="w-3 h-3" />
                    {repo.default_branch}
                  </span>
                  {repo.primary_language ? <span>{repo.primary_language}</span> : null}
                  {repo.license ? <span>{repo.license}</span> : null}
                  <span>★ {repo.stars_count ?? 0}</span>
                  <span>⑂ {repo.forks_count ?? 0}</span>
                  <span>👁 {repo.watchers_count ?? 0}</span>
                  {repo.indexing_ready ? (
                    <span className="text-success">Indexing ready</span>
                  ) : (
                    <span>Not ready for indexing</span>
                  )}
                </div>
                {(repo.topics?.length ?? 0) > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {repo.topics!.map((topic) => (
                      <Badge key={topic} variant="secondary" className="text-[10px]">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                ) : null}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {repo.html_url ? (
                  <Button size="sm" variant="outline" asChild>
                    <a href={repo.html_url} target="_blank" rel="noreferrer" className="gap-1.5">
                      <ExternalLink className="w-3.5 h-3.5" />
                      GitHub
                    </a>
                  </Button>
                ) : null}
                <Button
                  size="sm"
                  variant="outline"
                  className="gap-1.5"
                  disabled={syncMutation.isPending}
                  onClick={() => syncMutation.mutate()}
                >
                  <RefreshCw
                    className={`w-3.5 h-3.5 ${syncMutation.isPending ? "animate-spin" : ""}`}
                  />
                  Sync
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className="gap-1.5 text-destructive"
                  disabled={disconnectMutation.isPending}
                  onClick={() => {
                    if (confirm("Disconnect this repository from Forge?")) {
                      disconnectMutation.mutate();
                    }
                  }}
                >
                  <Unplug className="w-3.5 h-3.5" />
                  Disconnect
                </Button>
              </div>
            </div>

            {/* Milestone 7 Code Intelligence Dashboard */}
            <RepositoryIntelligence repositoryId={id} />

            {/* Milestone 8 AI Knowledge Dashboard */}
            <AIKnowledgeDashboard repositoryId={id} />


              <section className="flex flex-col gap-2">
                <h2 className="text-sm font-semibold text-foreground">Languages</h2>
                <div className="flex flex-col gap-1.5">
                  {repo.languages!.map((lang) => (
                    <div key={lang.language} className="flex items-center gap-3 text-[11px]">
                      <span className="w-24 text-muted-foreground truncate">{lang.language}</span>
                      <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full bg-primary/70"
                          style={{ width: `${Math.min(100, lang.percentage)}%` }}
                        />
                      </div>
                      <span className="w-12 text-right text-muted-foreground">
                        {lang.percentage}%
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            ) : null}

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <MetaList
                title="Branches"
                icon={GitBranch}
                loading={branchesQuery.isLoading}
                empty="No branches synced yet"
                items={(branchesQuery.data ?? []).map((b) => ({
                  key: b.id,
                  primary: b.name,
                  secondary: b.latest_commit_sha?.slice(0, 7) ?? "",
                  badge: b.is_default ? "default" : undefined,
                }))}
              />
              <MetaList
                title="Contributors"
                icon={Users}
                loading={contributorsQuery.isLoading}
                empty="No contributors synced yet"
                items={(contributorsQuery.data ?? []).map((c) => ({
                  key: c.id,
                  primary: c.login,
                  secondary: `${c.contributions} contributions`,
                }))}
              />
              <MetaList
                title="Recent commits"
                icon={GitCommit}
                loading={commitsQuery.isLoading}
                empty="No commits synced yet"
                items={(commitsQuery.data ?? []).map((c) => ({
                  key: c.id,
                  primary: c.commit_message?.split("\n")[0] || c.commit_sha.slice(0, 7),
                  secondary: `${c.author_login || c.author_name || "unknown"} · ${
                    c.committed_at ? new Date(c.committed_at).toLocaleString() : ""
                  }`,
                  href: c.html_url ?? undefined,
                }))}
              />
              <MetaList
                title="Pull requests"
                icon={GitPullRequest}
                loading={prsQuery.isLoading}
                empty="No pull requests synced yet"
                items={(prsQuery.data ?? []).map((pr) => ({
                  key: pr.id,
                  primary: `#${pr.number} ${pr.title}`,
                  secondary: `${pr.status} · ${pr.author_login ?? ""}`,
                  href: pr.html_url ?? undefined,
                }))}
              />
              <MetaList
                title="Issues"
                icon={CircleDot}
                loading={issuesQuery.isLoading}
                empty="No issues synced yet"
                items={(issuesQuery.data ?? []).map((issue) => ({
                  key: issue.id,
                  primary: `#${issue.number} ${issue.title}`,
                  secondary: `${issue.status} · ${issue.author_login ?? ""}`,
                  href: issue.html_url ?? undefined,
                }))}
              />
              <section className="border border-border rounded-lg bg-surface p-3 flex flex-col gap-2">
                <h3 className="text-xs font-semibold text-foreground">Sync history</h3>
                {statusQuery.isLoading ? (
                  <Skeleton className="h-16 w-full" />
                ) : (statusQuery.data?.sync_history.length ?? 0) === 0 ? (
                  <p className="text-[11px] text-muted-foreground">No sync jobs yet.</p>
                ) : (
                  <ul className="flex flex-col divide-y divide-border">
                    {statusQuery.data!.sync_history.map((job) => (
                      <li key={job.id} className="py-2 text-[11px]">
                        <div className="flex justify-between gap-2">
                          <span className="font-medium text-foreground capitalize">
                            {job.job_type.replaceAll("_", " ")}
                          </span>
                          <Badge variant="outline" className="text-[10px] capitalize">
                            {job.status}
                          </Badge>
                        </div>
                        <div className="text-muted-foreground mt-0.5">
                          Progress {job.progress}%
                          {job.finished_at
                            ? ` · ${new Date(job.finished_at).toLocaleString()}`
                            : ""}
                        </div>
                        {job.error_message ? (
                          <p className="text-destructive mt-0.5 line-clamp-2">{job.error_message}</p>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                )}
                {statusQuery.data?.sync_error ? (
                  <p className="text-[11px] text-destructive">{statusQuery.data.sync_error}</p>
                ) : null}
              </section>
            </section>

            <p className="text-[11px] text-muted-foreground border border-dashed border-border rounded-lg p-3">
              Source code is not displayed or stored. Forge syncs repository metadata only to prepare for future AI indexing.
            </p>
          </>
        ) : null}
      </LoadingErrorWrapper>
    </div>
  );
}

function MetaList({
  title,
  icon: Icon,
  loading,
  empty,
  items,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  loading: boolean;
  empty: string;
  items: {
    key: string;
    primary: string;
    secondary?: string;
    badge?: string;
    href?: string;
  }[];
}) {
  return (
    <section className="border border-border rounded-lg bg-surface p-3 flex flex-col gap-2 min-h-[140px]">
      <h3 className="text-xs font-semibold text-foreground flex items-center gap-1.5">
        <Icon className="w-3.5 h-3.5" />
        {title}
      </h3>
      {loading ? (
        <Skeleton className="h-16 w-full" />
      ) : items.length === 0 ? (
        <p className="text-[11px] text-muted-foreground">{empty}</p>
      ) : (
        <ul className="flex flex-col divide-y divide-border max-h-56 overflow-y-auto">
          {items.map((item) => (
            <li key={item.key} className="py-2">
              <div className="flex items-start justify-between gap-2">
                {item.href ? (
                  <a
                    href={item.href}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] font-medium text-foreground hover:text-primary line-clamp-2"
                  >
                    {item.primary}
                  </a>
                ) : (
                  <span className="text-[11px] font-medium text-foreground line-clamp-2">
                    {item.primary}
                  </span>
                )}
                {item.badge ? (
                  <Badge variant="info" className="text-[10px] shrink-0">
                    {item.badge}
                  </Badge>
                ) : null}
              </div>
              {item.secondary ? (
                <p className="text-[10px] text-muted-foreground mt-0.5 line-clamp-1">
                  {item.secondary}
                </p>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
