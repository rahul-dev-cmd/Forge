"use client";

import * as React from "react";
import { TopNavbar } from "@/components/navigation/TopNavbar";
import { Sidebar } from "@/components/navigation/Sidebar";
import { AIPanel } from "@/components/ai/AIPanel";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { cn } from "@/lib/utils";

export default function WorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { sidebarCollapsed, aiPanelOpen } = useWorkspaceStore();

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col antialiased">
      {/* Top Navigation Bar */}
      <TopNavbar />

      <div className="flex flex-grow">
        {/* Left-hand Navigation Sidebar */}
        <Sidebar />

        {/* Center Workspace Content Area */}
        <main
          className={cn(
            "flex-grow mt-24 px-6 pb-6 overflow-y-auto transition-all duration-300 ease-in-out min-h-[calc(100vh-96px)]",
            sidebarCollapsed ? "ml-[96px]" : "ml-[304px]",
            aiPanelOpen ? "mr-[384px]" : "mr-0",
            // Responsive mobile adjustments overrides
            "max-md:ml-0 max-md:mr-0 max-md:px-4"
          )}
        >
          {children}
        </main>

        {/* Right-hand AI Chat Copilot Drawer */}
        <AIPanel />
      </div>
    </div>
  );
}
