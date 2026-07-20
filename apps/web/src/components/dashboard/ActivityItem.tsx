import * as React from "react";
import { Sparkles, GitFork, RefreshCw, FileCode, Milestone, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { Activity } from "@/lib/mockData";

interface ActivityItemProps {
  activity: Activity;
  isLast?: boolean;
}

export function ActivityItem({ activity, isLast = false }: ActivityItemProps) {
  const getIcon = (type: Activity["type"]) => {
    switch (type) {
      case "ai":
        return { icon: Sparkles, color: "text-blue-500 bg-blue-500/10 border-blue-500/20" };
      case "commit":
        return { icon: GitFork, color: "text-purple-500 bg-purple-500/10 border-purple-500/20" };
      case "sync":
        return { icon: RefreshCw, color: "text-success bg-success/10 border-success/20" };
      case "documentation":
        return { icon: FileCode, color: "text-warning bg-warning/10 border-warning/20" };
      case "sprint":
        return { icon: Milestone, color: "text-pink-500 bg-pink-500/10 border-pink-500/20" };
      default:
        return { icon: User, color: "text-muted-foreground bg-muted border-border" };
    }
  };

  const { icon: Icon, color: iconStyle } = getIcon(activity.type);

  return (
    <div className="flex gap-4 group select-none">
      {/* Visual Line connector */}
      <div className="flex flex-col items-center shrink-0">
        <div className={cn("w-7.5 h-7.5 rounded-lg border flex items-center justify-center shadow-3xs transition-transform duration-200 group-hover:scale-105", iconStyle)}>
          <Icon className="w-3.5 h-3.5" />
        </div>
        {!isLast && <div className="w-px flex-1 bg-border/60 my-2" />}
      </div>

      {/* Text Details */}
      <div className="flex flex-col gap-1 pb-4 flex-1">
        <div className="flex items-center justify-between gap-2 mt-0.5">
          <span className="text-xs font-semibold text-foreground leading-tight group-hover:text-blue-500 transition-colors">
            {activity.message}
          </span>
          <span className="text-[9px] text-muted-foreground whitespace-nowrap">
            {activity.time}
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-[9px] text-muted-foreground">
          <span className="font-bold uppercase tracking-widest text-[8px] bg-muted px-1.5 py-0.2 rounded border border-border">
            {activity.type}
          </span>
          <span>•</span>
          <span>By {activity.author}</span>
        </div>
      </div>
    </div>
  );
}
export default ActivityItem;
