import * as React from "react";
import { Folder, FileCode, GitFork, RefreshCw, AlertCircle } from "lucide-react";

export default function RepositoriesPage() {
  const mockFiles = [
    { name: "apps", type: "dir", size: "-", date: "2 hours ago" },
    { name: "packages", type: "dir", size: "-", date: "2 hours ago" },
    { name: "docs", type: "dir", size: "-", date: "1 day ago" },
    { name: "package.json", type: "file", size: "583 B", date: "2 hours ago" },
    { name: "turbo.json", type: "file", size: "336 B", date: "1 week ago" },
    { name: "pnpm-workspace.yaml", type: "file", size: "90 B", date: "2 hours ago" },
  ];

  return (
    <div className="flex flex-col gap-6 max-w-4xl select-none">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-border pb-4">
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-foreground">forge-monorepo</h1>
            <span className="bg-primary/10 border border-primary/20 text-primary text-[10px] font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1">
              <GitFork className="w-3 h-3" /> main
            </span>
          </div>
          <p className="text-xs text-muted-foreground">
            Connected to github.com/active-workspace/forge-monorepo
          </p>
        </div>
        <button
          disabled
          className="h-9 px-3 border border-border bg-surface text-xs font-semibold rounded-md flex items-center gap-1.5 cursor-not-allowed text-muted-foreground"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Sync Repo</span>
        </button>
      </div>

      {/* Directory Browser mockup */}
      <div className="border border-border rounded-lg bg-surface flex flex-col shadow-3xs overflow-hidden">
        {/* Header bar */}
        <div className="bg-muted/20 px-4 py-2.5 border-b border-border grid grid-cols-12 text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
          <div className="col-span-6">Name</div>
          <div className="col-span-3 text-right">Size</div>
          <div className="col-span-3 text-right">Last Modified</div>
        </div>

        {/* File items list */}
        <div className="flex flex-col divide-y divide-border">
          {mockFiles.map((file, idx) => (
            <div
              key={idx}
              className="px-4 py-3 grid grid-cols-12 text-xs items-center hover:bg-muted/30 transition-all cursor-pointer"
            >
              <div className="col-span-6 flex items-center gap-2.5 font-medium text-foreground">
                {file.type === "dir" ? (
                  <Folder className="w-4.5 h-4.5 text-primary/70" />
                ) : (
                  <FileCode className="w-4.5 h-4.5 text-muted-foreground/75" />
                )}
                <span>{file.name}</span>
              </div>
              <div className="col-span-3 text-right text-muted-foreground font-mono">{file.size}</div>
              <div className="col-span-3 text-right text-muted-foreground">{file.date}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Info notice about monaco editor and logic placeholders */}
      <div className="p-4 rounded-lg bg-primary/5 border border-primary/10 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
        <div className="flex flex-col gap-0.5">
          <span className="text-xs font-semibold text-foreground">Monaco Editor Out of Scope</span>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            Code editing and workspace file sync capabilities will be configured in subsequent milestones.
          </p>
        </div>
      </div>
    </div>
  );
}
