import type { ProjectDto } from "@/lib/api/projects";
import type { ActivityDto } from "@/lib/api/activities";
import type { Activity, Project } from "@/lib/mockData";

function formatRelativeTime(iso?: string | null): string {
  if (!iso) return "just now";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "just now";
  const delta = Date.now() - date.getTime();
  const mins = Math.floor(delta / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} mins ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} hours ago`;
  const days = Math.floor(hours / 24);
  return `${days} days ago`;
}

function mapStatus(status: ProjectDto["status"]): Project["status"] {
  if (status === "archived") return "on_hold";
  if (status === "draft") return "on_hold";
  if (status === "completed") return "completed";
  return "active";
}

function mapPriority(priority: ProjectDto["priority"]): Project["priority"] {
  if (priority === "critical") return "high";
  if (priority === "low" || priority === "medium" || priority === "high") return priority;
  return "medium";
}

/** Adapt API project payloads to the existing ProjectCard UI shape. */
export function toProjectCardModel(project: ProjectDto): Project {
  return {
    id: project.id,
    name: project.name,
    description: project.description || "No description provided.",
    progress: project.status === "completed" ? 100 : project.status === "archived" ? 0 : 50,
    status: mapStatus(project.status),
    priority: mapPriority(project.priority),
    lastUpdated: formatRelativeTime(project.created_at),
    repository: project.slug,
    branch: "main",
    teamMembers: [],
    openIssues: 0,
    pullRequests: 0,
    aiTasks: 0,
    linesOfCode: "—",
    testCoverage: "—",
    productivityScore: 0,
  };
}

export function toActivityItemModel(activity: ActivityDto): Activity {
  const name = (activity.details?.name as string | undefined) || activity.action;
  return {
    id: activity.id,
    message: name.replace(/_/g, " "),
    time: formatRelativeTime(activity.created_at),
    author: activity.actor_id ? activity.actor_id.slice(0, 8) : "system",
    type: activity.type === "repository" ? "commit" : "sync",
  };
}
