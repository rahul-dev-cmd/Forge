"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, MessageSquare, Code2, User } from "lucide-react";
import { adminApi, WorkspaceActivityItem } from "@/lib/api/admin";

interface WorkspaceActivityFeedProps {
  workspaceId: string;
}

export function WorkspaceActivityFeed({ workspaceId }: WorkspaceActivityFeedProps) {
  const activityQuery = useQuery({
    queryKey: ["workspace-activity", workspaceId],
    queryFn: () => adminApi.listWorkspaceActivity(workspaceId),
  });

  const activities = activityQuery.data || [];

  return (
    <div className="border border-border rounded-lg p-4 bg-card space-y-3">
      <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5 border-b border-border pb-2">
        <Activity className="w-4 h-4 text-primary" /> Workspace Activity Feed
      </h4>

      <div className="space-y-2">
        {activities.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-4">No activity logged in workspace.</p>
        ) : (
          activities.map((act) => (
            <div key={act.id} className="flex items-center justify-between text-xs py-1.5 border-b border-border/40">
              <div className="flex items-center gap-2">
                <User className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="font-semibold text-foreground capitalize">{act.action.replace("_", " ")}</span>
                <span className="text-muted-foreground font-mono">({act.target_type})</span>
              </div>
              <span className="text-[10px] text-muted-foreground">
                {new Date(act.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
