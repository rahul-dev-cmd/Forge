"use client";

import * as React from "react";
import { useUser, UserProfile } from "@/providers/AuthProvider";
import { User, Calendar, ShieldCheck, Mail, Link as LinkIcon, Building2 } from "lucide-react";
import { Skeleton } from "@/components/ui/Skeleton";
import { DashboardCard } from "@/components/shared/DashboardCard";

export default function ProfilePage() {
  const { user, isLoaded } = useUser();

  if (!isLoaded) {
    return (
      <div className="flex flex-col gap-6 max-w-4xl mx-auto p-4 space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="w-16 h-16 rounded-full" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-6 w-1/4" />
            <Skeleton className="h-4 w-1/3" />
          </div>
        </div>
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-border bg-surface rounded-xl max-w-md mx-auto gap-3">
        <User className="w-10 h-10 text-muted-foreground" />
        <h2 className="text-sm font-bold text-foreground">Not Signed In</h2>
        <p className="text-xs text-muted-foreground leading-normal">
          Please authenticate to view profile details.
        </p>
      </div>
    );
  }

  const createdAtDate = user.createdAt ? new Date(user.createdAt).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric"
  }) : "Unknown";

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto select-none pb-12 text-left">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <User className="w-5 h-5 text-blue-500" />
          <span>User Profile</span>
        </h1>
        <p className="text-xs text-muted-foreground">
          Manage your personal identity credentials, account settings, and workspace integrations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Clerk Profile Manager (8 columns) */}
        <div className="lg:col-span-8 border border-border rounded-xl bg-surface shadow-3xs p-1.5 overflow-hidden">
          <UserProfile
            routing="hash"
            appearance={{
              elements: {
                card: "shadow-none border-none p-0 m-0 w-full bg-transparent",
                navbar: "hidden", // Hide navigation menu inside our custom page container
                pageScrollable: "p-4 w-full max-w-full",
                headerTitle: "text-xs font-bold text-foreground uppercase tracking-widest leading-none mb-1",
                headerSubtitle: "text-[11px] text-muted-foreground",
                profileSectionTitleText: "text-xs font-bold text-foreground",
                formButtonPrimary: "bg-blue-600 hover:bg-blue-600/90 text-white font-semibold text-xs shadow-3xs",
                formFieldLabel: "text-xs font-semibold text-foreground",
                formFieldInput: "border border-border bg-muted/15 text-foreground text-xs rounded-lg",
              }
            }}
          />
        </div>

        {/* Right Column: Platform Metadata & Connected Accounts (4 columns) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          {/* Metadata Card */}
          <DashboardCard title="Account Overview" description="METRICS & SYSTEM AUDITS">
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <img
                  src={user.imageUrl}
                  alt={user.fullName || "User Avatar"}
                  className="w-12 h-12 rounded-full border border-border/40 shadow-3xs"
                />
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-bold text-foreground leading-tight truncate">
                    {user.fullName || "No Name"}
                  </span>
                  <span className="text-[10px] text-muted-foreground mt-0.5 truncate leading-none">
                    @{user.username || "no_username"}
                  </span>
                </div>
              </div>

              <div className="h-px bg-border/60" />

              <div className="flex flex-col gap-2.5 text-xs">
                <div className="flex items-center justify-between text-muted-foreground">
                  <span className="flex items-center gap-1.5 font-semibold text-[11px]">
                    <Mail className="w-3.5 h-3.5" /> Email
                  </span>
                  <span className="font-mono text-[10px] text-foreground truncate max-w-[150px]">
                    {user.primaryEmailAddress?.emailAddress}
                  </span>
                </div>

                <div className="flex items-center justify-between text-muted-foreground">
                  <span className="flex items-center gap-1.5 font-semibold text-[11px]">
                    <Calendar className="w-3.5 h-3.5" /> Created On
                  </span>
                  <span className="text-foreground font-semibold">
                    {createdAtDate}
                  </span>
                </div>

                <div className="flex items-center justify-between text-muted-foreground">
                  <span className="flex items-center gap-1.5 font-semibold text-[11px]">
                    <ShieldCheck className="w-3.5 h-3.5" /> Status
                  </span>
                  <span className="bg-success/15 text-success border border-success/20 px-2 py-0.2 rounded text-[10px] font-bold">
                    Active Session
                  </span>
                </div>
              </div>
            </div>
          </DashboardCard>

          {/* Organization & OAuth Integrations placeholders */}
          <DashboardCard title="Workspace Links" description="ORGANIZATIONS & AUTHENTICATORS">
            <div className="flex flex-col gap-3 text-xs">
              <div className="flex items-start gap-3 p-2.5 rounded-lg border border-border bg-muted/10">
                <Building2 className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                <div className="flex flex-col gap-0.5 text-left">
                  <span className="font-bold text-foreground">Organization Membership</span>
                  <p className="text-[10px] text-muted-foreground leading-normal">
                    Organization controls are disabled. Clerk Multi-tenant org routing will map to this panel in next milestones.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-2.5 rounded-lg border border-border bg-muted/10">
                <LinkIcon className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                <div className="flex flex-col gap-0.5 text-left">
                  <span className="font-bold text-foreground">Connected Integrations</span>
                  <p className="text-[10px] text-muted-foreground leading-normal">
                    GitHub connection and index credentials placeholders.
                  </p>
                </div>
              </div>
            </div>
          </DashboardCard>
        </div>
      </div>
    </div>
  );
}
