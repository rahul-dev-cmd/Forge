"use client";

import * as React from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/Input";
import { cn } from "@/lib/utils";

const SYNC_FILTERS = [
  { value: "all", label: "All" },
  { value: "synced", label: "Synced" },
  { value: "syncing", label: "Syncing" },
  { value: "failed", label: "Failed" },
  { value: "queued", label: "Queued" },
  { value: "disconnected", label: "Disconnected" },
] as const;

const SORT_OPTIONS = [
  { value: "updated_at", label: "Updated" },
  { value: "name", label: "Name" },
  { value: "stars_count", label: "Stars" },
  { value: "last_synced_at", label: "Last synced" },
] as const;

interface RepositoryFiltersProps {
  query: string;
  syncStatus: string;
  sortBy: string;
  order: "asc" | "desc";
  onQueryChange: (value: string) => void;
  onSyncStatusChange: (value: string) => void;
  onSortByChange: (value: string) => void;
  onOrderChange: (value: "asc" | "desc") => void;
}

export function RepositoryFilters({
  query,
  syncStatus,
  sortBy,
  order,
  onQueryChange,
  onSyncStatusChange,
  onSortByChange,
  onOrderChange,
}: RepositoryFiltersProps) {
  return (
    <div className="flex flex-col gap-3">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Search repositories…"
          className="pl-9 h-9 text-xs"
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {SYNC_FILTERS.map((filter) => (
          <button
            key={filter.value}
            type="button"
            onClick={() => onSyncStatusChange(filter.value)}
            className={cn(
              "px-2.5 py-1 rounded-md text-[11px] font-semibold border transition-colors cursor-pointer",
              syncStatus === filter.value
                ? "bg-primary text-primary-foreground border-primary"
                : "bg-surface border-border text-muted-foreground hover:text-foreground"
            )}
          >
            {filter.label}
          </button>
        ))}

        <div className="ml-auto flex items-center gap-2">
          <select
            value={sortBy}
            onChange={(e) => onSortByChange(e.target.value)}
            className="h-8 rounded-md border border-border bg-surface px-2 text-[11px] text-foreground"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                Sort: {opt.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => onOrderChange(order === "asc" ? "desc" : "asc")}
            className="h-8 px-2 rounded-md border border-border bg-surface text-[11px] font-semibold text-muted-foreground hover:text-foreground cursor-pointer"
          >
            {order === "asc" ? "Asc" : "Desc"}
          </button>
        </div>
      </div>
    </div>
  );
}
