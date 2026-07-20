"use client";

import * as React from "react";
import { CopilotWorkspace } from "@/components/copilot/CopilotWorkspace";

export default function CopilotPage() {
  // Demo workspace ID fallback for standalone view
  const workspaceId = "00000000-0000-0000-0000-000000000001";

  return (
    <div className="p-6 space-y-4 max-w-7xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-foreground">AI Copilot & Multi-Agent Workspace</h1>
        <p className="text-xs text-muted-foreground mt-0.5">
          Conversational software engineering powered by 7 specialized agents and ContextPackage retrieval.
        </p>
      </div>

      <CopilotWorkspace workspaceId={workspaceId} />
    </div>
  );
}
