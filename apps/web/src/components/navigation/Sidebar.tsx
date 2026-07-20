"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Bot,
  MessageSquare,
  Milestone,
  FolderKanban,
  FolderGit2,
  Settings,
  LogOut,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Menu,
  X
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { useUser, useClerk } from "@/providers/AuthProvider";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider
} from "@/components/ui/Tooltip";

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useWorkspaceStore();
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const { user, isLoaded } = useUser();
  const { signOut } = useClerk();

  const mainNavItems = [
    { label: "Home", href: "/dashboard", icon: Home },
    { label: "AI Assistant", href: "/projects/forge-core", icon: Bot }, // link to mock detail
    { label: "Discussions", href: "/dashboard?tab=discussions", icon: MessageSquare },
    { label: "Timeline", href: "/dashboard?tab=timeline", icon: Milestone },
  ];

  const workspaceNavItems = [
    { label: "Projects", href: "/projects", icon: FolderKanban },
    { label: "Repositories", href: "/repositories", icon: FolderGit2 },
  ];

  const renderLink = (item: { label: string; href: string; icon: React.ComponentType<{ className?: string }> }) => {
    const Icon = item.icon;
    const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

    const content = (
      <Link
        href={item.href}
        onClick={() => setMobileOpen(false)}
        className={cn(
          "flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-all duration-200 border border-transparent select-none",
          isActive
            ? "bg-blue-600 text-white shadow-2xs hover:bg-blue-600/90"
            : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
        )}
      >
        <Icon className={cn("w-4 h-4 shrink-0", isActive ? "text-white" : "text-muted-foreground")} />
        {!sidebarCollapsed && <span className="transition-opacity duration-200">{item.label}</span>}
      </Link>
    );

    if (sidebarCollapsed) {
      return (
        <Tooltip key={item.href} delayDuration={50}>
          <TooltipTrigger asChild>{content}</TooltipTrigger>
          <TooltipContent side="right" align="center" className="font-semibold text-[10px]">
            {item.label}
          </TooltipContent>
        </Tooltip>
      );
    }

    return <React.Fragment key={item.href}>{content}</React.Fragment>;
  };

  return (
    <TooltipProvider>
      {/* Mobile Menu Button - Fixed at top-left on small screens */}
      <div className="md:hidden fixed top-5 left-4 z-50">
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 rounded-lg bg-surface border border-border text-foreground hover:bg-muted cursor-pointer shadow-3xs"
        >
          {mobileOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
        </button>
      </div>

      {/* Sidebar Container */}
      <aside
        className={cn(
          "h-[calc(100vh-32px)] fixed top-4 bottom-4 bg-surface border border-border rounded-xl flex flex-col justify-between py-5 px-3.5 select-none z-40 shadow-xs transition-all duration-300 ease-in-out",
          sidebarCollapsed ? "w-[76px] left-4" : "w-[280px] left-4",
          // Mobile responsive overlay
          "max-md:w-[260px] max-md:left-4 max-md:top-4 max-md:bottom-4 max-md:h-[calc(100vh-32px)] max-md:shadow-xl max-md:z-50",
          mobileOpen ? "max-md:translate-x-0" : "max-md:-translate-x-[290px]"
        )}
      >
        <div className="flex flex-col gap-6">
          {/* Brand Header */}
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2.5">
              <div className="w-8.5 h-8.5 rounded-lg bg-linear-to-tr from-blue-600 to-cyan-400 flex items-center justify-center text-white shadow-2xs shrink-0">
                <Sparkles className="w-4.5 h-4.5" />
              </div>
              {!sidebarCollapsed && (
                <span className="font-black text-base tracking-tight text-foreground animate-in fade-in duration-200">
                  Forge
                </span>
              )}
            </div>

            {/* Collapse Toggle Button (Desktop only) */}
            {!sidebarCollapsed && (
              <button
                onClick={toggleSidebar}
                className="hidden md:flex p-1 rounded-md hover:bg-muted border border-transparent hover:border-border text-muted-foreground hover:text-foreground cursor-pointer transition-colors"
                title="Collapse Sidebar"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
            )}
            {sidebarCollapsed && (
              <button
                onClick={toggleSidebar}
                className="hidden md:flex p-1 mx-auto rounded-md hover:bg-muted border border-transparent hover:border-border text-muted-foreground hover:text-foreground cursor-pointer transition-colors"
                title="Expand Sidebar"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Primary Menu */}
          <nav className="flex flex-col gap-1">
            {mainNavItems.map(renderLink)}
          </nav>

          <div className="h-px bg-border/60 my-1 mx-1.5" />

          {/* Category section */}
          <div className="flex flex-col gap-1.5">
            {!sidebarCollapsed ? (
              <div className="px-3.5 text-[9px] font-black text-muted-foreground uppercase tracking-widest select-none leading-none mb-1 animate-in fade-in duration-200">
                Workspace
              </div>
            ) : (
              <div className="h-2" />
            )}
            <nav className="flex flex-col gap-0.5">
              {workspaceNavItems.map(renderLink)}
            </nav>
          </div>
        </div>

        {/* Bottom Menu */}
        <div className="flex flex-col gap-2.5 border-t border-border/60 pt-4">
          {/* Authenticated User Profile Details */}
          {isLoaded && user && (
            <div className={cn(
              "flex items-center gap-3 rounded-lg bg-muted/20 border border-border/30 overflow-hidden mb-1 select-none transition-all duration-200",
              sidebarCollapsed ? "justify-center p-1.5" : "p-2.5"
            )}>
              <img
                src={user.imageUrl}
                alt={user.fullName || "User Avatar"}
                className="w-7 h-7 rounded-full shrink-0 border border-border/30 shadow-3xs"
              />
              {!sidebarCollapsed && (
                <div className="flex flex-col text-left overflow-hidden min-w-0 flex-1">
                  <span className="text-[11px] font-bold text-foreground leading-none truncate">
                    {user.fullName || user.username || "User"}
                  </span>
                  <span className="text-[9px] text-muted-foreground mt-1.5 truncate leading-none">
                    {user.primaryEmailAddress?.emailAddress || ""}
                  </span>
                </div>
              )}
            </div>
          )}

          {renderLink({ label: "Settings", href: "/settings", icon: Settings })}
          <button
            onClick={() => signOut()}
            className={cn(
              "flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold text-destructive hover:bg-destructive/5 transition-all text-left cursor-pointer border border-transparent select-none",
              sidebarCollapsed && "justify-center"
            )}
          >
            <LogOut className="w-4 h-4 text-destructive shrink-0" />
            {!sidebarCollapsed && <span>Log out</span>}
          </button>
        </div>
      </aside>

      {/* Mobile Drawer Backdrop overlay */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="md:hidden fixed inset-0 bg-background/60 backdrop-blur-xs z-35 animate-in fade-in duration-200"
        />
      )}
    </TooltipProvider>
  );
}
export default Sidebar;
