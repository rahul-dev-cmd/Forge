"use client";

import * as React from "react";
import Link from "next/link";
import { FolderKanban, GitFork, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { Project } from "@/lib/mockData";

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const getStatusColor = (status: Project["status"]) => {
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

  const getPriorityColor = (priority: Project["priority"]) => {
    switch (priority) {
      case "high":
        return "bg-destructive/10 text-destructive border-destructive/20 font-bold";
      case "medium":
        return "bg-warning/10 text-warning border-warning/20";
      case "low":
        return "bg-muted text-muted-foreground border-border";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  return (
    <Link href={`/projects/${project.id}`} className="block group select-none">
      <div className="p-5 rounded-xl border border-border bg-surface flex flex-col gap-4 justify-between transition-all duration-300 group-hover:border-border/80 group-hover:shadow-xs group-hover:-translate-y-0.5 relative overflow-hidden">
        {/* Glow effect on hover */}
        <div className="absolute inset-0 bg-linear-to-tr from-blue-500/0 via-indigo-500/0 to-cyan-500/0 group-hover:from-blue-500/2 pointer-events-none transition-all duration-300" />

        <div className="flex flex-col gap-2.5 relative z-10">
          {/* Top Line: Badges */}
          <div className="flex justify-between items-center">
            <span className={cn("text-[9px] font-black uppercase tracking-widest border px-2 py-0.5 rounded-md", getStatusColor(project.status))}>
              {project.status.replace("_", " ")}
            </span>
            <span className={cn("text-[9px] font-black uppercase tracking-widest border px-2 py-0.5 rounded-md", getPriorityColor(project.priority))}>
              {project.priority} priority
            </span>
          </div>

          {/* Heading and details */}
          <div className="flex items-start gap-3 mt-1">
            <div className="w-9 h-9 rounded-lg bg-blue-500/5 border border-blue-500/10 text-blue-500 flex items-center justify-center shadow-3xs group-hover:bg-blue-600 group-hover:text-white transition-all duration-300 shrink-0">
              <FolderKanban className="w-4.5 h-4.5" />
            </div>
            <div className="flex flex-col overflow-hidden">
              <h3 className="font-bold text-sm text-foreground group-hover:text-blue-500 transition-colors truncate">
                {project.name}
              </h3>
              <p className="text-[11px] text-muted-foreground mt-0.5 line-clamp-1">
                {project.description}
              </p>
            </div>
          </div>

          {/* Connected Git Details */}
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground/80 mt-1 font-mono">
            <GitFork className="w-3 h-3 shrink-0" />
            <span className="truncate">{project.repository}</span>
            <span className="text-[9px] bg-muted px-1.5 py-0.2 rounded-md border border-border shrink-0">{project.branch}</span>
          </div>
        </div>

        {/* Progress Bar (Linear Only) */}
        <div className="flex flex-col gap-1.5 mt-1 relative z-10">
          <div className="flex justify-between items-baseline text-[10px]">
            <span className="text-muted-foreground font-semibold">Workspace Progress</span>
            <span className="font-bold text-foreground">{project.progress}%</span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-muted overflow-hidden relative border border-border/40">
            <div
              style={{ width: `${project.progress}%` }}
              className="h-full rounded-full bg-blue-600 dark:bg-blue-500 transition-all duration-500 ease-out"
            />
          </div>
        </div>

        {/* Bottom Line: Team & Meta */}
        <div className="flex items-center justify-between pt-3 border-t border-border/40 mt-1.5 relative z-10">
          {/* Avatar stack */}
          <div className="flex -space-x-1.5 overflow-hidden">
            {project.teamMembers.map((member) => (
              <div
                key={member}
                className="w-5.5 h-5.5 rounded-full bg-blue-500/10 border border-surface text-[9px] font-black text-blue-600 dark:text-blue-400 flex items-center justify-center shadow-3xs shrink-0 select-none"
              >
                {member}
              </div>
            ))}
          </div>

          {/* Updated time */}
          <div className="flex items-center gap-1 text-[9px] text-muted-foreground font-semibold">
            <Clock className="w-3.5 h-3.5 shrink-0" />
            <span>Updated {project.lastUpdated}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}
export default ProjectCard;
