import * as React from "react";
import { cn } from "@/lib/utils";

interface ProgressCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  progress: number; // 0 to 100
  subtitle?: string;
  color?: "blue" | "green" | "orange" | "purple";
}

export function ProgressCard({
  className,
  title,
  progress,
  subtitle,
  color = "blue",
  ...props
}: ProgressCardProps) {
  const percent = Math.min(100, Math.max(0, progress));

  return (
    <div
      className={cn(
        "p-5 bg-surface border border-border rounded-xl flex flex-col gap-3 shadow-2xs hover:border-border/80 transition-all select-none",
        className
      )}
      {...props}
    >
      <div className="flex justify-between items-baseline">
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
          {title}
        </span>
        <span className="text-sm font-black text-foreground">{percent}%</span>
      </div>

      <div className="w-full h-2 rounded-full bg-muted overflow-hidden relative border border-border/40">
        <div
          style={{ width: `${percent}%` }}
          className={cn(
            "h-full rounded-full transition-all duration-500 ease-out",
            color === "blue" && "bg-blue-600 dark:bg-blue-500",
            color === "green" && "bg-success",
            color === "orange" && "bg-warning",
            color === "purple" && "bg-purple-600 dark:bg-purple-500"
          )}
        />
      </div>

      {subtitle && (
        <span className="text-[9px] text-muted-foreground mt-0.5 leading-none">
          {subtitle}
        </span>
      )}
    </div>
  );
}
export default ProgressCard;
