"use client";

import * as React from "react";
import { SignUp } from "@/providers/AuthProvider";
import { Sparkles } from "lucide-react";

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground px-4 relative select-none">
      {/* Background radial gradient accent */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[380px] h-[380px] bg-blue-500/5 blur-[80px] rounded-full pointer-events-none" />

      <div className="flex flex-col items-center gap-6 z-10 max-w-sm w-full text-center">
        {/* Brand Header */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-linear-to-tr from-blue-600 to-cyan-400 flex items-center justify-center text-white shadow-2xs">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <span className="font-black text-xl tracking-tight text-foreground">Forge</span>
        </div>
        <div className="flex flex-col gap-1.5 mb-2">
          <h2 className="text-sm font-bold text-foreground uppercase tracking-widest">
            Create Account
          </h2>
          <p className="text-xs text-muted-foreground">
            Sign up to create your workspaces and invite team members.
          </p>
        </div>

        {/* Clerk Sign Up component */}
        <SignUp
          appearance={{
            elements: {
              card: "border border-border bg-surface shadow-xs rounded-xl",
              headerTitle: "text-foreground font-bold",
              headerSubtitle: "text-muted-foreground",
              socialButtonsBlockButton: "border border-border bg-muted/20 text-foreground hover:bg-muted/40",
              formFieldLabel: "text-foreground font-semibold",
              formFieldInput: "border border-border bg-muted/10 text-foreground",
              formButtonPrimary: "bg-blue-600 hover:bg-blue-600/90 text-white shadow-3xs font-semibold",
              footerActionLink: "text-blue-500 hover:text-blue-600",
            },
          }}
        />
      </div>
    </div>
  );
}
