import * as React from "react";
import { cn } from "@/lib/utils";

interface DashboardCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  headerActions?: React.ReactNode;
  gradient?: boolean;
}

export const DashboardCard = React.forwardRef<HTMLDivElement, DashboardCardProps>(
  ({ className, title, description, headerActions, gradient = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "relative overflow-hidden rounded-xl border border-border bg-surface shadow-xs transition-all duration-300 hover:shadow-sm hover:border-border/80 flex flex-col",
          className
        )}
        {...props}
      >
        {/* Abstract Glowing Accent Gradient background */}
        {gradient && (
          <div className="absolute inset-0 bg-linear-to-tr from-blue-500/5 to-cyan-500/0 dark:from-blue-500/10 pointer-events-none" />
        )}

        {(title || description || headerActions) && (
          <div className="flex items-start justify-between p-5 border-b border-border/40 relative z-10">
            <div className="flex flex-col gap-1">
              {title && (
                <h3 className="text-xs font-bold text-foreground uppercase tracking-wider select-none">
                  {title}
                </h3>
              )}
              {description && (
                <p className="text-[11px] text-muted-foreground select-none">
                  {description}
                </p>
              )}
            </div>
            {headerActions && <div className="flex items-center gap-1.5">{headerActions}</div>}
          </div>
        )}

        <div className="p-5 flex-grow relative z-10">{children}</div>
      </div>
    );
  }
);

DashboardCard.displayName = "DashboardCard";
