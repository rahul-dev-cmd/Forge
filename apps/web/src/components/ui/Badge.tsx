import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "info" | "warning";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 select-none",
        variant === "default" && "border-transparent bg-primary text-primary-foreground shadow-2xs hover:opacity-90",
        variant === "secondary" && "border-transparent bg-secondary text-secondary-foreground hover:bg-muted",
        variant === "destructive" && "border-transparent bg-destructive text-destructive-foreground shadow-2xs hover:opacity-90",
        variant === "outline" && "text-foreground border-border bg-transparent",
        variant === "success" && "border-success/20 bg-success/10 text-success hover:bg-success/15",
        variant === "info" && "border-info/20 bg-info/10 text-info hover:bg-info/15",
        variant === "warning" && "border-warning/20 bg-warning/10 text-warning hover:bg-warning/15",
        className
      )}
      {...props}
    />
  );
}

export { Badge };
