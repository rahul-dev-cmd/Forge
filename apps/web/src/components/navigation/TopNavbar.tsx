"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { Sun, Moon, Plus, ChevronDown, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { SearchBar } from "./SearchBar";
import { NotificationMenu } from "./NotificationMenu";
import { cn } from "@/lib/utils";
import { UserButton, useUser } from "@/providers/AuthProvider";

export function TopNavbar() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);
  const { sidebarCollapsed, aiPanelOpen, toggleAiPanel } = useWorkspaceStore();
  const { user } = useUser();
  const [quickActionsOpen, setQuickActionsOpen] = React.useState(false);
  const quickActionsRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  // Listen to click outside quick actions
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (quickActionsRef.current && !quickActionsRef.current.contains(event.target as Node)) {
        setQuickActionsOpen(false);
      }
    }
    if (quickActionsOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [quickActionsOpen]);

  const quickActions = [
    { label: "New Project", action: () => alert("Mock: Open Create Project dialog") },
    { label: "New Workspace", action: () => alert("Mock: Open Create Workspace dialog") },
    { label: "Connect Repository", action: () => alert("Mock: Open GitHub import panel") },
    { label: "Invite Team", action: () => alert("Mock: Open Invite members email form") },
  ];

  return (
    <header
      className={cn(
        "fixed top-4 h-16 bg-surface border border-border rounded-xl z-30 flex items-center justify-between px-5 select-none shadow-xs transition-all duration-300 ease-in-out",
        sidebarCollapsed ? "left-[96px]" : "left-[304px]",
        aiPanelOpen ? "right-[384px]" : "right-4",
        // Responsive Coordinates overrides
        "max-md:left-4 max-md:right-4 max-md:pl-14"
      )}
    >
      {/* Left: Search input */}
      <SearchBar />

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {/* Quick Actions Dropdown */}
        <div className="relative" ref={quickActionsRef}>
          <Button
            size="sm"
            onClick={() => setQuickActionsOpen(!quickActionsOpen)}
            className="h-9 px-3 text-xs bg-blue-600 hover:bg-blue-600/90 text-white font-semibold flex items-center gap-1.5 shadow-2xs rounded-lg cursor-pointer max-sm:hidden"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Quick Actions</span>
            <ChevronDown className={cn("w-3 h-3 transition-transform duration-200", quickActionsOpen && "rotate-180")} />
          </Button>

          {/* Quick Actions dropdown panel */}
          {quickActionsOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-popover border border-border rounded-lg shadow-md z-50 flex flex-col p-1 animate-in fade-in-0 slide-in-from-top-2 duration-150">
              {quickActions.map((act) => (
                <button
                  key={act.label}
                  onClick={() => {
                    act.action();
                    setQuickActionsOpen(false);
                  }}
                  className="w-full text-left px-3 py-2 text-xs font-semibold rounded-md text-foreground hover:bg-muted/65 transition-colors cursor-pointer"
                >
                  {act.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
          className="p-2 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-all cursor-pointer border border-transparent hover:border-border"
          title="Toggle Theme"
        >
          {mounted && resolvedTheme === "dark" ? (
            <Sun className="w-4.5 h-4.5" />
          ) : (
            <Moon className="w-4.5 h-4.5" />
          )}
        </button>

        {/* Notification Icon Component */}
        <NotificationMenu />

        {/* AI Copilot Toggle Icon */}
        <button
          onClick={toggleAiPanel}
          className={cn(
            "p-2 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-all cursor-pointer border border-transparent hover:border-border max-lg:hidden",
            aiPanelOpen && "bg-muted text-foreground border-border"
          )}
          title="Toggle AI Panel"
        >
          <Sparkles className="w-4.5 h-4.5 text-blue-500" />
        </button>

        <div className="h-6 w-px bg-border max-sm:hidden" />

        {/* Clerk Authenticated User Button */}
        {mounted && (
          <div className="flex items-center gap-2 max-sm:hidden select-none">
            <UserButton
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8 rounded-full border border-blue-500/20 shadow-3xs hover:scale-105 transition-transform"
                }
              }}
            />
            {user && (
              <div className="hidden lg:flex flex-col text-left overflow-hidden min-w-0">
                <span className="text-[11px] font-bold text-foreground leading-none truncate max-w-[100px]">
                  {user.fullName || user.username || "User"}
                </span>
                <span className="text-[9px] text-muted-foreground mt-1 truncate max-w-[120px] leading-none">
                  {user.primaryEmailAddress?.emailAddress}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
export default TopNavbar;
