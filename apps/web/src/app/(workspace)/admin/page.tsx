"use client";

import * as React from "react";
import { AdminDashboard } from "@/components/admin/AdminDashboard";
import { WorkspaceActivityFeed } from "@/components/collaboration/WorkspaceActivityFeed";

export default function AdminPage() {
  const workspaceId = "00000000-0000-0000-0000-000000000001";

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-foreground">Production Administration & Team Control</h1>
        <p className="text-xs text-muted-foreground mt-0.5">
          Monitor system diagnostics, database resource connection pools, vector metrics, and workspace activity feeds.
        </p>
      </div>

      <AdminDashboard />
      <WorkspaceActivityFeed workspaceId={workspaceId} />
    </div>
  );
}
