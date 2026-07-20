import * as React from "react";
import { AlertTriangle, RefreshCw, FolderOpen } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";

interface LoadingErrorWrapperProps {
  state: "loading" | "loaded" | "error" | "empty";
  onRetry?: () => void;
  loadingSkeleton?: React.ReactNode;
  emptyIcon?: React.ComponentType<{ className?: string }>;
  emptyTitle?: string;
  emptyDescription?: string;
  errorTitle?: string;
  errorDescription?: string;
  children: React.ReactNode;
}

export function LoadingErrorWrapper({
  state,
  onRetry,
  loadingSkeleton,
  emptyIcon: EmptyIcon = FolderOpen,
  emptyTitle = "No Items Found",
  emptyDescription = "There are no elements to display right now.",
  errorTitle = "Failed to load details",
  errorDescription = "An unexpected error occurred while loading this section.",
  children,
}: LoadingErrorWrapperProps) {
  if (state === "loading") {
    return (
      loadingSkeleton || (
        <div className="space-y-3 p-4">
          <Skeleton className="h-5 w-2/5" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
          <div className="pt-2 flex gap-2">
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-8 w-20" />
          </div>
        </div>
      )
    );
  }

  if (state === "error") {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center border border-dashed border-destructive/20 rounded-xl bg-destructive/5 gap-3 animate-in fade-in-50 duration-300">
        <div className="w-10 h-10 rounded-full bg-destructive/15 flex items-center justify-center text-destructive">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div className="flex flex-col gap-1 max-w-sm">
          <h4 className="text-sm font-bold text-foreground">{errorTitle}</h4>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            {errorDescription}
          </p>
        </div>
        {onRetry && (
          <Button
            size="sm"
            variant="outline"
            onClick={onRetry}
            className="mt-1 h-8 text-[11px] font-semibold gap-1.5 cursor-pointer shadow-3xs"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Retry Connection</span>
          </Button>
        )}
      </div>
    );
  }

  if (state === "empty") {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center border border-dashed border-border rounded-xl bg-muted/10 gap-3 animate-in fade-in-50 duration-300">
        <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center text-muted-foreground">
          <EmptyIcon className="w-5 h-5" />
        </div>
        <div className="flex flex-col gap-1 max-w-sm">
          <h4 className="text-sm font-bold text-foreground">{emptyTitle}</h4>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            {emptyDescription}
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
