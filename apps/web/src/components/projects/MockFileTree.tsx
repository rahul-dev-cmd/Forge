"use client";

import * as React from "react";
import { Folder, FolderOpen, FileCode, ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { FileNode } from "@/lib/mockData";

interface MockFileTreeProps {
  files: FileNode[];
}

export function MockFileTree({ files }: MockFileTreeProps) {
  return (
    <div className="border border-border rounded-xl bg-surface flex flex-col shadow-3xs overflow-hidden select-none font-mono">
      {/* File Tree Header */}
      <div className="bg-muted/20 px-4 py-3 border-b border-border/60 grid grid-cols-12 text-[9px] font-black uppercase tracking-wider text-muted-foreground">
        <div className="col-span-6">Name</div>
        <div className="col-span-3 text-right">Size</div>
        <div className="col-span-3 text-right">Last Updated</div>
      </div>

      {/* Scrollable File List */}
      <div className="flex flex-col py-1.5 divide-y divide-border/20 max-h-96 overflow-y-auto">
        {files.length === 0 ? (
          <div className="p-6 text-center text-xs text-muted-foreground">
            No files available for this repository.
          </div>
        ) : (
          files.map((node) => <FileTreeNode key={node.name} node={node} level={0} />)
        )}
      </div>
    </div>
  );
}

interface FileTreeNodeProps {
  node: FileNode;
  level: number;
}

function FileTreeNode({ node, level }: FileTreeNodeProps) {
  const [isOpen, setIsOpen] = React.useState(level < 1); // Expand top-level by default
  const isDirectory = node.type === "directory";

  return (
    <div className="flex flex-col">
      {/* Node Entry Row */}
      <div
        onClick={() => isDirectory && setIsOpen(!isOpen)}
        style={{ paddingLeft: `${(level * 16) + 16}px` }}
        className={cn(
          "pr-4 py-2.5 grid grid-cols-12 text-xs items-center hover:bg-muted/35 transition-all",
          isDirectory ? "cursor-pointer font-bold text-foreground" : "cursor-default text-muted-foreground"
        )}
      >
        <div className="col-span-6 flex items-center gap-2 overflow-hidden truncate">
          {isDirectory ? (
            <>
              <span className="text-muted-foreground/60 shrink-0">
                {isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              </span>
              {isOpen ? (
                <FolderOpen className="w-4 h-4 text-blue-500 shrink-0" />
              ) : (
                <Folder className="w-4 h-4 text-blue-500 shrink-0" />
              )}
            </>
          ) : (
            <>
              <span className="w-3.5 h-3.5 shrink-0" /> {/* Spacer spacer */}
              <FileCode className="w-4 h-4 text-muted-foreground/80 shrink-0" />
            </>
          )}
          <span className="truncate">{node.name}</span>
        </div>
        <div className="col-span-3 text-right font-mono text-[10px] text-muted-foreground/75 whitespace-nowrap">
          {node.size || "-"}
        </div>
        <div className="col-span-3 text-right text-[10px] text-muted-foreground/75 whitespace-nowrap">
          {node.lastUpdated || "2 hours ago"}
        </div>
      </div>

      {/* Children expansion */}
      {isDirectory && isOpen && node.children && (
        <div className="flex flex-col">
          {node.children.map((child) => (
            <FileTreeNode key={child.name} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}
export default MockFileTree;
