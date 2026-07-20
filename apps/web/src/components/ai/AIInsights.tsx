import * as React from "react";
import { ShieldAlert, CircleAlert, Info, ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { AIInsight } from "@/lib/mockData";

interface AIInsightsProps {
  insights: AIInsight[];
}

export function AIInsights({ insights }: AIInsightsProps) {
  const getSeverityStyles = (severity: AIInsight["severity"]) => {
    switch (severity) {
      case "critical":
        return {
          bg: "bg-destructive/5 border-destructive/10",
          badge: "bg-destructive/10 text-destructive border-destructive/20",
          icon: ShieldAlert,
          iconColor: "text-destructive",
        };
      case "warning":
        return {
          bg: "bg-warning/5 border-warning/10",
          badge: "bg-warning/10 text-warning border-warning/20",
          icon: CircleAlert,
          iconColor: "text-warning",
        };
      case "info":
        return {
          bg: "bg-blue-500/5 border-blue-500/10",
          badge: "bg-blue-500/10 text-blue-500 border-blue-500/20",
          icon: Info,
          iconColor: "text-blue-500",
        };
      default:
        return {
          bg: "bg-muted/30 border-border",
          badge: "bg-muted text-muted-foreground border-border",
          icon: Info,
          iconColor: "text-muted-foreground",
        };
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {insights.map((insight) => {
        const styles = getSeverityStyles(insight.severity);
        const Icon = styles.icon;

        return (
          <div
            key={insight.id}
            className={cn(
              "p-4 rounded-xl border flex flex-col justify-between gap-3 shadow-3xs transition-all hover:shadow-2xs",
              styles.bg
            )}
          >
            {/* Header info */}
            <div className="flex items-start gap-3">
              <div className={cn("p-1.5 rounded-lg bg-surface border border-border/40 shadow-3xs", styles.iconColor)}>
                <Icon className="w-4 h-4 shrink-0" />
              </div>
              <div className="flex flex-col gap-1 flex-1">
                <div className="flex items-center gap-2">
                  <span className={cn("text-[9px] font-black uppercase tracking-wider border px-1.5 py-0.2 rounded-md", styles.badge)}>
                    {insight.severity}
                  </span>
                </div>
                <h4 className="text-xs font-bold text-foreground mt-0.5 leading-tight">
                  {insight.suggestion}
                </h4>
                <p className="text-[11px] text-muted-foreground leading-relaxed">
                  {insight.description}
                </p>
              </div>
            </div>

            {/* Recommended Action Row */}
            <div className="flex items-center justify-between pl-10 pt-2.5 border-t border-border/10">
              <div className="flex items-center gap-1 text-[9px] text-muted-foreground">
                <span className="font-semibold">Recommended Action:</span>
                <span className="font-mono text-[9px]">{insight.recommendedAction}</span>
              </div>
              <button className="flex items-center gap-0.5 text-[9px] font-black text-blue-500 hover:text-blue-600 transition-colors cursor-pointer select-none">
                <span>Apply</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
export default AIInsights;
