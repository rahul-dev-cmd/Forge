"use client";

import * as React from "react";
import { Search, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ProjectFiltersProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  statusFilter: string;
  setStatusFilter: (status: string) => void;
  priorityFilter: string;
  setPriorityFilter: (priority: string) => void;
  sortBy: string;
  setSortBy: (sort: string) => void;
  onClearFilters: () => void;
  hasFiltersActive: boolean;
}

export function ProjectFilters({
  searchQuery,
  setSearchQuery,
  statusFilter,
  setStatusFilter,
  priorityFilter,
  setPriorityFilter,
  sortBy,
  setSortBy,
  onClearFilters,
  hasFiltersActive,
}: ProjectFiltersProps) {
  return (
    <div className="flex flex-col gap-3 p-4 bg-muted/20 border border-border rounded-xl">
      {/* Top row: search + sort */}
      <div className="flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search projects by name, description, repository..."
            className="w-full h-9 pl-9 pr-4 rounded-lg bg-surface border border-border text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-black uppercase text-muted-foreground tracking-wider shrink-0">
            Sort By:
          </span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="h-9 px-3 rounded-lg bg-surface border border-border text-xs text-foreground focus:outline-none cursor-pointer"
          >
            <option value="last_updated">Recently Updated</option>
            <option value="progress_desc">Highest Progress</option>
            <option value="progress_asc">Lowest Progress</option>
            <option value="name">Alphabetical</option>
          </select>
        </div>
      </div>

      {/* Bottom row: status + priority badges */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2.5 border-t border-border/40">
        <div className="flex flex-wrap items-center gap-4">
          {/* Status Segment */}
          <div className="flex items-center gap-2">
            <span className="text-[9px] font-black uppercase tracking-wider text-muted-foreground">Status:</span>
            <div className="flex rounded-md border border-border bg-surface p-0.5 overflow-hidden">
              {["all", "active", "completed", "on_hold"].map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={cn(
                    "px-2.5 py-1 text-[10px] font-bold rounded-sm transition-all cursor-pointer capitalize select-none",
                    statusFilter === status
                      ? "bg-blue-600 text-white shadow-3xs"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {status.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          {/* Priority Segment */}
          <div className="flex items-center gap-2">
            <span className="text-[9px] font-black uppercase tracking-wider text-muted-foreground">Priority:</span>
            <div className="flex rounded-md border border-border bg-surface p-0.5 overflow-hidden">
              {["all", "high", "medium", "low"].map((priority) => (
                <button
                  key={priority}
                  onClick={() => setPriorityFilter(priority)}
                  className={cn(
                    "px-2.5 py-1 text-[10px] font-bold rounded-sm transition-all cursor-pointer capitalize select-none",
                    priorityFilter === priority
                      ? "bg-blue-600 text-white shadow-3xs"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {priority}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Clear Filters Button */}
        {hasFiltersActive && (
          <button
            onClick={onClearFilters}
            className="flex items-center gap-1 text-[10px] font-black text-destructive hover:text-destructive/80 transition-colors cursor-pointer"
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>Reset Filters</span>
          </button>
        )}
      </div>
    </div>
  );
}
export default ProjectFilters;
