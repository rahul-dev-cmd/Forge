"use client";

import * as React from "react";
import Link from "next/link";
import { GitBranch, Star, GitFork, RefreshCw, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import type { RepositoryDto } from "@/lib/api/repositories";
import { cn } from "@/lib/utils";

function syncVariant(status: string): React.ComponentProps<typeof Badge>["variant"] {
  switch (status) {
    case "synced":
      return "success";
    case "syncing":
    case "queued":
      return "info";
    case "failed":
      return "destructive";
    case "disconnected":
      return "warning";
    default:
      return "secondary";
  }
}

interface RepositoryCardProps {
  repository: RepositoryDto;
  onSync?: (id: string) => void;
  syncing?: boolean;
}

export function RepositoryCard({ repository, onSync, syncing }: RepositoryCardProps) {
  const title = repository.full_name || repository.name;

  return (
    <div className="border border-border rounded-lg bg-surface p-4 flex flex-col gap-3 hover:border-primary/30 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1 min-w-0">
          <Link
            href={`/repositories/${repository.id}`}
            className="text-sm font-semibold text-foreground hover:text-primary truncate"
          >
            {title}
          </Link>
          {repository.description ? (
            <p className="text-[11px] text-muted-foreground line-clamp-2">
              {repository.description}
            </p>
          ) : null}
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <Badge variant={syncVariant(repository.sync_status)} className="text-[10px] capitalize">
            {repository.sync_status}
          </Badge>
          <Badge variant="outline" className="text-[10px] capitalize">
            {repository.connection_status}
          </Badge>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 text-[11px] text-muted-foreground">
        {repository.primary_language ? (
          <span className="font-medium text-foreground/80">{repository.primary_language}</span>
        ) : null}
        <span className="inline-flex items-center gap-1">
          <GitBranch className="w-3 h-3" />
          {repository.default_branch}
        </span>
        <span className="inline-flex items-center gap-1">
          <Star className="w-3 h-3" />
          {repository.stars_count ?? 0}
        </span>
        <span className="inline-flex items-center gap-1">
          <GitFork className="w-3 h-3" />
          {repository.forks_count ?? 0}
        </span>
        {repository.last_synced_at ? (
          <span>Synced {new Date(repository.last_synced_at).toLocaleString()}</span>
        ) : (
          <span>Never synced</span>
        )}
      </div>

      {repository.sync_error ? (
        <p className="text-[11px] text-destructive/90 line-clamp-2">{repository.sync_error}</p>
      ) : null}

      <div className="flex items-center gap-2 pt-1">
        <Button
          size="sm"
          variant="outline"
          className="h-8 text-[11px] gap-1.5"
          disabled={syncing || repository.connection_status === "disconnected"}
          onClick={() => onSync?.(repository.id)}
        >
          <RefreshCw className={cn("w-3 h-3", syncing && "animate-spin")} />
          Sync
        </Button>
        <Button size="sm" variant="ghost" className="h-8 text-[11px]" asChild>
          <Link href={`/repositories/${repository.id}`}>Details</Link>
        </Button>
        {repository.html_url ? (
          <a
            href={repository.html_url}
            target="_blank"
            rel="noreferrer"
            className="ml-auto inline-flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground"
          >
            GitHub <ExternalLink className="w-3 h-3" />
          </a>
        ) : null}
      </div>
    </div>
  );
}
