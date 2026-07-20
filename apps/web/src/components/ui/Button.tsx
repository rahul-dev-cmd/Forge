import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(
          "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 cursor-pointer select-none",
          // Variant classes
          variant === "default" && "bg-primary text-primary-foreground shadow-xs hover:opacity-90",
          variant === "destructive" && "bg-destructive text-destructive-foreground shadow-xs hover:opacity-90",
          variant === "outline" && "border border-border bg-background shadow-2xs hover:bg-muted hover:text-foreground",
          variant === "secondary" && "bg-secondary text-secondary-foreground shadow-2xs hover:bg-muted",
          variant === "ghost" && "hover:bg-muted hover:text-foreground",
          variant === "link" && "text-primary underline-offset-4 hover:underline",
          // Size classes
          size === "default" && "h-9 px-4 py-2",
          size === "sm" && "h-8 rounded-md px-3 text-xs",
          size === "lg" && "h-10 rounded-md px-8",
          size === "icon" && "h-9 w-9",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };
