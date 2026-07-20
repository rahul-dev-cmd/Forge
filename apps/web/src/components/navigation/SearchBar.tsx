"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Search, FolderKanban, FolderGit2, CornerDownLeft, Command, HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { MOCK_PROJECTS } from "@/lib/mockData";

export function SearchBar() {
  const router = useRouter();
  const { searchOpen, setSearchOpen } = useWorkspaceStore();
  const [query, setQuery] = React.useState("");
  const [selectedIndex, setSelectedIndex] = React.useState(0);
  const inputRef = React.useRef<HTMLInputElement>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);

  // Monitor keys for Ctrl+K, Cmd+K, Esc, and Arrow Navigation
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Toggle search on Ctrl+K or Cmd+K
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(!searchOpen);
        setQuery("");
      }

      // Close on Esc
      if (e.key === "Escape" && searchOpen) {
        e.preventDefault();
        setSearchOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [searchOpen, setSearchOpen]);

  // Autofocus input when modal opens
  React.useEffect(() => {
    if (searchOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
      setSelectedIndex(0);
    }
  }, [searchOpen]);

  // Listen to mouse click outside to close
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setSearchOpen(false);
      }
    }
    if (searchOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [searchOpen, setSearchOpen]);

  // Flatten results for keyboard navigation index matching
  const filteredProjects = query.trim() === ""
    ? MOCK_PROJECTS
    : MOCK_PROJECTS.filter((p) =>
        p.name.toLowerCase().includes(query.toLowerCase()) ||
        p.repository.toLowerCase().includes(query.toLowerCase())
      );

  // Filtered repositories (using connected projects as repositories)
  const filteredRepos = query.trim() === ""
    ? MOCK_PROJECTS.map(p => ({ id: p.id, name: p.name, repository: p.repository }))
    : MOCK_PROJECTS.map(p => ({ id: p.id, name: p.name, repository: p.repository }))
        .filter(r => r.repository.toLowerCase().includes(query.toLowerCase()));

  const totalItems = filteredProjects.length + filteredRepos.length;

  const triggerSelection = React.useCallback((index: number) => {
    if (index < 0 || index >= totalItems) return;

    setSearchOpen(false);
    setQuery("");

    // Identify if project or repo was selected
    if (index < filteredProjects.length) {
      const proj = filteredProjects[index];
      router.push(`/projects/${proj.id}`);
    } else {
      const repoIdx = index - filteredProjects.length;
      const repo = filteredRepos[repoIdx];
      router.push(`/projects/${repo.id}`);
    }
  }, [totalItems, setSearchOpen, filteredProjects, router, filteredRepos]);

  // Handle keyboard list navigation
  React.useEffect(() => {
    const handleNav = (e: KeyboardEvent) => {
      if (!searchOpen) return;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % totalItems);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + totalItems) % totalItems);
      } else if (e.key === "Enter") {
        e.preventDefault();
        triggerSelection(selectedIndex);
      }
    };

    window.addEventListener("keydown", handleNav);
    return () => window.removeEventListener("keydown", handleNav);
  }, [searchOpen, selectedIndex, totalItems, triggerSelection]);

  return (
    <>
      {/* Navbar trigger mockup input box */}
      <div className="flex-1 max-w-sm">
        <div
          onClick={() => setSearchOpen(true)}
          className="relative group cursor-pointer"
        >
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-muted-foreground transition-colors group-hover:text-foreground" />
          <div className="w-full h-9 pl-9 pr-14 rounded-lg bg-muted border border-border text-xs text-muted-foreground flex items-center select-none hover:border-border/80 transition-colors">
            Search projects, repositories...
          </div>
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 h-5 px-1.5 rounded bg-surface border border-border text-[9px] font-bold text-muted-foreground flex items-center shadow-3xs">
            Ctrl+K
          </kbd>
        </div>
      </div>

      {/* Backdrop Spotlight Modal */}
      {searchOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-xs z-50 flex items-start justify-center pt-[15vh] px-4 animate-in fade-in duration-200">
          <div
            ref={containerRef}
            className="w-full max-w-xl bg-surface border border-border rounded-xl shadow-lg overflow-hidden flex flex-col animate-in zoom-in-95 duration-150"
          >
            {/* Input Row */}
            <div className="flex items-center px-4 border-b border-border/60">
              <Search className="w-4.5 h-4.5 text-muted-foreground shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setSelectedIndex(0);
                }}
                placeholder="Type a command or search..."
                className="w-full h-12 px-3 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none border-none focus:ring-0 focus:outline-none"
              />
              <kbd className="h-5 px-1.5 rounded bg-muted border border-border text-[9px] font-black text-muted-foreground flex items-center shadow-3xs select-none">
                ESC
              </kbd>
            </div>

            {/* Results Scroll Container */}
            <div className="max-h-80 overflow-y-auto p-2">
              {totalItems === 0 ? (
                <div className="p-8 text-center flex flex-col items-center justify-center gap-2 select-none">
                  <HelpCircle className="w-8 h-8 text-muted-foreground/60" />
                  <span className="text-xs font-bold text-foreground">No matches found</span>
                  <p className="text-[10px] text-muted-foreground leading-normal max-w-xs">
                    We couldn&apos;t find any project or repository matching &quot;{query}&quot;.
                  </p>
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  {/* Projects Section */}
                  {filteredProjects.length > 0 && (
                    <div className="flex flex-col gap-0.5">
                      <span className="px-3 py-1 text-[9px] font-bold text-muted-foreground uppercase tracking-widest select-none">
                        Projects
                      </span>
                      {filteredProjects.map((proj, idx) => {
                        const globalIdx = idx;
                        const isSelected = selectedIndex === globalIdx;

                        return (
                          <div
                            key={proj.id}
                            onClick={() => triggerSelection(globalIdx)}
                            onMouseEnter={() => setSelectedIndex(globalIdx)}
                            className={cn(
                              "px-3 py-2 rounded-lg flex items-center justify-between text-xs cursor-pointer select-none transition-all duration-100",
                              isSelected ? "bg-blue-600 text-white font-medium" : "hover:bg-muted/40 text-foreground"
                            )}
                          >
                            <div className="flex items-center gap-2.5">
                              <FolderKanban className={cn("w-4.5 h-4.5 shrink-0", isSelected ? "text-white" : "text-blue-500")} />
                              <div className="flex flex-col">
                                <span className="font-bold">{proj.name}</span>
                                <span className={cn("text-[9px] mt-0.5 font-mono", isSelected ? "text-white/70" : "text-muted-foreground")}>
                                  {proj.repository}
                                </span>
                              </div>
                            </div>
                            {isSelected && (
                              <div className="flex items-center gap-1 text-[9px] opacity-80">
                                <span>Go to</span>
                                <CornerDownLeft className="w-3 h-3" />
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Repositories Section */}
                  {filteredRepos.length > 0 && (
                    <div className="flex flex-col gap-0.5">
                      <span className="px-3 py-1 text-[9px] font-bold text-muted-foreground uppercase tracking-widest select-none">
                        Repositories
                      </span>
                      {filteredRepos.map((repo, idx) => {
                        const globalIdx = filteredProjects.length + idx;
                        const isSelected = selectedIndex === globalIdx;

                        return (
                          <div
                            key={`repo-${repo.id}`}
                            onClick={() => triggerSelection(globalIdx)}
                            onMouseEnter={() => setSelectedIndex(globalIdx)}
                            className={cn(
                              "px-3 py-2 rounded-lg flex items-center justify-between text-xs cursor-pointer select-none transition-all duration-100",
                              isSelected ? "bg-blue-600 text-white font-medium" : "hover:bg-muted/40 text-foreground"
                            )}
                          >
                            <div className="flex items-center gap-2.5">
                              <FolderGit2 className={cn("w-4.5 h-4.5 shrink-0", isSelected ? "text-white" : "text-muted-foreground")} />
                              <div className="flex flex-col">
                                <span className="font-bold">{repo.repository.split("/").pop()}</span>
                                <span className={cn("text-[9px] mt-0.5 font-mono", isSelected ? "text-white/75" : "text-muted-foreground")}>
                                  {repo.repository}
                                </span>
                              </div>
                            </div>
                            {isSelected && (
                              <div className="flex items-center gap-1 text-[9px] opacity-80">
                                <span>Explore</span>
                                <CornerDownLeft className="w-3 h-3" />
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Bottom Help Bar */}
            <div className="px-4 py-2 border-t border-border/60 bg-muted/20 flex justify-between items-center text-[10px] text-muted-foreground select-none">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1">
                  <Command className="w-3 h-3" /> + K to search
                </span>
                <span>↑↓ to navigate</span>
                <span>↵ to select</span>
              </div>
              <span>Forge spotlight</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
export default SearchBar;
