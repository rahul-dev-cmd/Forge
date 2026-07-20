import * as React from "react";
import { LucideIcon, HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "./Button";

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description: string;
  icon?: LucideIcon;
  actionText?: string;
  onActionClick?: () => void;
}

export function EmptyState({
  title,
  description,
  icon: Icon = HelpCircle,
  actionText,
  onActionClick,
  className,
  ...props
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center p-8 border border-dashed border-border rounded-lg bg-surface/50 select-none min-h-[300px] gap-5",
        className
      )}
      {...props}
    >
      <div className="w-12 h-12 rounded-full bg-muted border border-border flex items-center justify-center text-muted-foreground shadow-3xs">
        <Icon className="w-6 h-6 text-muted-foreground/80" />
      </div>

      <div className="flex flex-col gap-1.5 max-w-sm">
        <h3 className="font-semibold text-sm text-foreground">{title}</h3>
        <p className="text-xs text-muted-foreground leading-relaxed">{description}</p>
      </div>

      {actionText && (
        <Button size="sm" onClick={onActionClick}>
          {actionText}
        </Button>
      )}
    </div>
  );
}
