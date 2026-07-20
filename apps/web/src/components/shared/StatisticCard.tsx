import * as React from "react";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatisticCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  trendType?: "up" | "down" | "neutral";
  description?: string;
}

export function StatisticCard({
  className,
  title,
  value,
  icon: Icon,
  trend,
  trendType = "neutral",
  description,
  ...props
}: StatisticCardProps) {
  return (
    <div
      className={cn(
        "p-5 bg-surface border border-border rounded-xl flex flex-col gap-3.5 shadow-2xs hover:border-border/80 transition-all select-none relative overflow-hidden group",
        className
      )}
      {...props}
    >
      <div className="absolute inset-0 bg-linear-to-tr from-blue-500/0 via-indigo-500/0 to-cyan-500/0 group-hover:from-blue-500/2 pointer-events-none transition-all duration-300" />
      
      <div className="flex justify-between items-center relative z-10">
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
          {title}
        </span>
        <div className="w-8 h-8 rounded-lg bg-blue-500/5 border border-blue-500/10 text-blue-500 group-hover:text-blue-600 dark:group-hover:text-blue-400 group-hover:bg-blue-500/10 group-hover:border-blue-500/20 flex items-center justify-center shadow-3xs transition-all duration-300">
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="flex flex-col gap-1 relative z-10">
        <span className="text-2xl font-extrabold tracking-tight text-foreground">
          {value}
        </span>
        
        {trend && (
          <div className="flex items-center gap-1.5 mt-0.5">
            <span
              className={cn(
                "text-[10px] font-bold px-1.5 py-0.5 rounded-md",
                trendType === "up" && "bg-success/10 text-success border border-success/10",
                trendType === "down" && "bg-destructive/10 text-destructive border border-destructive/10",
                trendType === "neutral" && "bg-muted text-muted-foreground border border-border"
              )}
            >
              {trend}
            </span>
            {description && (
              <span className="text-[9px] text-muted-foreground">{description}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
