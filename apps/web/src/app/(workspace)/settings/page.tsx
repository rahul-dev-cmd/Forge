"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { useUser } from "@/providers/AuthProvider";
import {
  Sun,
  Moon,
  Laptop,
  User,
  SlidersHorizontal,
  Bell,
  Lock,
  Building2,
  CreditCard,
  AlertOctagon,
  Check,
  ShieldCheck,
  ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import { DashboardCard } from "@/components/shared/DashboardCard";
import { Button } from "@/components/ui/Button";

type TabID = "account" | "appearance" | "notifications" | "security" | "workspace" | "billing" | "danger";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { user, isLoaded } = useUser();
  const [mounted, setMounted] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState<TabID>("account");

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const tabs = [
    { id: "account" as TabID, name: "Account Details", icon: User },
    { id: "appearance" as TabID, name: "Appearance & Theme", icon: SlidersHorizontal },
    { id: "notifications" as TabID, name: "Notification Rules", icon: Bell },
    { id: "security" as TabID, name: "Security & Access", icon: Lock },
    { id: "workspace" as TabID, name: "Workspace Config", icon: Building2 },
    { id: "billing" as TabID, name: "Billing & Plans", icon: CreditCard },
    { id: "danger" as TabID, name: "Danger Zone", icon: AlertOctagon },
  ];

  // Theme option list
  const themeOptions = [
    { name: "Light Mode", value: "light", icon: Sun },
    { name: "Dark Mode", value: "dark", icon: Moon },
    { name: "System Sync", value: "system", icon: Laptop },
  ];

  // Notification checkbox states
  const [notifEmails, setNotifEmails] = React.useState(true);
  const [notifAI, setNotifAI] = React.useState(true);
  const [notifBuild, setNotifBuild] = React.useState(false);

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto select-none pb-12 text-left">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <SlidersHorizontal className="w-5 h-5 text-blue-500" />
          <span>Application Settings</span>
        </h1>
        <p className="text-xs text-muted-foreground">
          Update your account parameters, notification filters, billing tiers, and dark/light color themes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        {/* Left Hand Section: Tabs Navigation Selector (4 columns) */}
        <div className="md:col-span-4 flex flex-col gap-1 bg-surface border border-border rounded-xl p-2.5 shadow-3xs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isSelected = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold transition-all border border-transparent cursor-pointer",
                  isSelected
                    ? "bg-blue-600 text-white shadow-2xs hover:bg-blue-600/95"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{tab.name}</span>
                </div>
                {!isSelected && <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/60" />}
              </button>
            );
          })}
        </div>

        {/* Right Hand Section: Form Card (8 columns) */}
        <div className="md:col-span-8 flex flex-col gap-6">
          {/* Account Details Tab */}
          {activeTab === "account" && (
            <DashboardCard title="Account Details" description="USER IDENTITY & DETAILS">
              {isLoaded && user ? (
                <div className="flex flex-col gap-5 text-xs text-left">
                  <div className="flex items-center gap-4">
                    <img
                      src={user.imageUrl}
                      alt={user.fullName || "User Avatar"}
                      className="w-12 h-12 rounded-full border border-border/40 shadow-3xs"
                    />
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-foreground">
                        {user.fullName || "User name placeholder"}
                      </span>
                      <span className="text-[10px] text-muted-foreground mt-0.5">
                        @{user.username || "username_unset"}
                      </span>
                    </div>
                  </div>

                  <div className="h-px bg-border/60" />

                  <div className="flex flex-col gap-2">
                    <div className="flex flex-col gap-1">
                      <span className="font-bold text-muted-foreground text-[9px] uppercase tracking-wider">Primary Email Address</span>
                      <span className="text-foreground font-mono font-bold">{user.primaryEmailAddress?.emailAddress}</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-1">
                      Profile attributes (name, username, avatar) are hosted on Clerk. Click edit to open the account management panel.
                    </p>
                  </div>

                  <div className="pt-2">
                    <Button
                      size="sm"
                      onClick={() => window.location.href = "/profile"}
                      className="h-8 px-3 text-xs bg-blue-600 hover:bg-blue-600/90 text-white font-semibold cursor-pointer shadow-3xs"
                    >
                      Edit User Profile
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-muted animate-pulse" />
                    <div className="space-y-1.5 flex-1">
                      <div className="h-3.5 bg-muted rounded w-1/4 animate-pulse" />
                      <div className="h-3 bg-muted rounded w-1/3 animate-pulse" />
                    </div>
                  </div>
                  <div className="h-px bg-border/60" />
                  <div className="h-10 bg-muted rounded w-full animate-pulse" />
                </div>
              )}
            </DashboardCard>
          )}

          {/* Appearance & Themes Tab */}
          {activeTab === "appearance" && (
            <DashboardCard title="Interface Theme" description="CUSTOM COLOR MODE PREFERENCES">
              <div className="flex flex-col gap-4 text-left">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {themeOptions.map((opt) => {
                    const Icon = opt.icon;
                    const isActive = mounted && theme === opt.value;
                    return (
                      <button
                        key={opt.value}
                        onClick={() => setTheme(opt.value)}
                        className={cn(
                          "flex flex-col items-center gap-2.5 p-4 rounded-xl border text-xs font-bold hover:bg-muted/40 transition-all cursor-pointer relative",
                          isActive
                            ? "bg-muted text-foreground border-muted-foreground/30 shadow-3xs"
                            : "bg-surface text-muted-foreground border-border"
                        )}
                      >
                        {isActive && (
                          <span className="absolute top-2 right-2 w-4 h-4 rounded-full bg-blue-500 text-white flex items-center justify-center shadow-3xs">
                            <Check className="w-2.5 h-2.5" />
                          </span>
                        )}
                        <Icon className="w-5 h-5 shrink-0" />
                        <span>{opt.name}</span>
                      </button>
                    );
                  })}
                </div>
                <p className="text-[10px] text-muted-foreground mt-1">
                  System sync automatically coordinates with your operating system dark/light variables settings.
                </p>
              </div>
            </DashboardCard>
          )}

          {/* Notifications Tab */}
          {activeTab === "notifications" && (
            <DashboardCard title="Notification Rules" description="EMAIL ALERTS & DISPATCH CODES">
              <div className="flex flex-col gap-4 text-xs text-left">
                <label className="flex items-start gap-3 p-3 rounded-lg border border-border bg-surface cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={notifEmails}
                    onChange={(e) => setNotifEmails(e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded border-border focus:ring-blue-500 mt-0.5 cursor-pointer"
                  />
                  <div className="flex flex-col text-left">
                    <span className="font-bold text-foreground">Critical security alerts</span>
                    <span className="text-[10px] text-muted-foreground mt-0.5 leading-normal">
                      Receive notices if credentials change, MFA is disabled, or OAuth keys expire.
                    </span>
                  </div>
                </label>

                <label className="flex items-start gap-3 p-3 rounded-lg border border-border bg-surface cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={notifAI}
                    onChange={(e) => setNotifAI(e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded border-border focus:ring-blue-500 mt-0.5 cursor-pointer"
                  />
                  <div className="flex flex-col text-left">
                    <span className="font-bold text-foreground">AI Copilot digest digests</span>
                    <span className="text-[10px] text-muted-foreground mt-0.5 leading-normal">
                      Get a weekly compile summary of database index warnings, test metrics, and code audits.
                    </span>
                  </div>
                </label>

                <label className="flex items-start gap-3 p-3 rounded-lg border border-border bg-surface cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={notifBuild}
                    onChange={(e) => setNotifBuild(e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded border-border focus:ring-blue-500 mt-0.5 cursor-pointer"
                  />
                  <div className="flex flex-col text-left">
                    <span className="font-bold text-foreground">Build failure notifications</span>
                    <span className="text-[10px] text-muted-foreground mt-0.5 leading-normal">
                      Trigger immediate emails if push pipelines fail to compile on main repository branch.
                    </span>
                  </div>
                </label>

                <div className="pt-2">
                  <Button
                    size="sm"
                    onClick={() => alert("Notification rules saved.")}
                    className="h-8 px-3.5 bg-blue-600 hover:bg-blue-600/90 text-white font-semibold cursor-pointer shadow-3xs"
                  >
                    Save Preferences
                  </Button>
                </div>
              </div>
            </DashboardCard>
          )}

          {/* Security Tab */}
          {activeTab === "security" && (
            <DashboardCard title="Security & Authentication" description="PASSWORD ROTATION & MULTI-FACTOR KEY">
              <div className="flex flex-col gap-4 text-xs text-left">
                <div className="flex items-start gap-3 p-3 bg-muted/20 border border-border rounded-lg">
                  <ShieldCheck className="w-4 h-4 text-success shrink-0 mt-0.5" />
                  <div className="flex flex-col text-left">
                    <span className="font-bold text-foreground">Password Cryptography</span>
                    <span className="text-[10px] text-muted-foreground mt-0.5 leading-normal">
                      Password updates and security variables are hosted by Clerk authentication infrastructure.
                    </span>
                  </div>
                </div>

                <div className="h-px bg-border/60" />

                <div className="flex items-center justify-between p-3 rounded-lg border border-dashed border-border bg-surface">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-bold text-foreground">Multi-Factor Authentication (MFA)</span>
                    <span className="text-[10px] text-muted-foreground">Add auth code verification for logins.</span>
                  </div>
                  <Button size="sm" variant="outline" className="h-7 text-[10px] font-semibold cursor-pointer shadow-3xs">
                    Enable
                  </Button>
                </div>
              </div>
            </DashboardCard>
          )}

          {/* Workspace Tab */}
          {activeTab === "workspace" && (
            <DashboardCard title="Workspace Settings" description="ORGANIZATION & MEMBERSHIP CLASSIFICATION">
              <div className="flex flex-col gap-4 text-xs text-left">
                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-foreground">Active Workspace Name</label>
                  <input
                    type="text"
                    defaultValue="Personal Dev Sandbox"
                    className="w-full h-9 px-3 rounded-lg border border-border bg-surface placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-blue-500 mt-1"
                  />
                </div>

                <div className="h-px bg-border/60" />

                <div className="flex flex-col gap-1.5">
                  <span className="font-bold text-foreground text-[11px]">Organization context</span>
                  <p className="text-[10px] text-muted-foreground leading-normal max-w-md">
                    Manage multi-tenant roles, group memberships, and resource tags. Organizations setup is locked during local mock staging.
                  </p>
                </div>
              </div>
            </DashboardCard>
          )}

          {/* Billing Tab */}
          {activeTab === "billing" && (
            <DashboardCard title="Billing & Upgrade Plans" description="STAGING BILLING METADATA LAYOUT">
              <div className="flex flex-col gap-4 text-center items-center py-6 border border-dashed border-border rounded-xl bg-muted/10">
                <CreditCard className="w-10 h-10 text-muted-foreground/60" />
                <div className="flex flex-col gap-1 max-w-sm mt-1">
                  <h4 className="text-xs font-bold text-foreground uppercase tracking-widest">Free Tier Plan</h4>
                  <p className="text-[10px] text-muted-foreground leading-relaxed">
                    You are currently using the Free Developer tier. Upgrading options for enterprise AI agents billing will map to Stripe in milestone roadmap.
                  </p>
                </div>
              </div>
            </DashboardCard>
          )}

          {/* Danger Zone Tab */}
          {activeTab === "danger" && (
            <DashboardCard title="Danger Zone" description="HIGH RISK CRITICAL ACTIONS">
              <div className="flex flex-col gap-4 text-xs text-left">
                <div className="p-4 border border-destructive/20 rounded-xl bg-destructive/5 flex items-center justify-between gap-4">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-bold text-foreground">Archive Workspace</span>
                    <span className="text-[10px] text-muted-foreground">Logically freeze and read-only connect this sandbox.</span>
                  </div>
                  <Button size="sm" variant="outline" className="h-7 text-[10px] font-bold text-destructive hover:bg-destructive/5 border-destructive/20 cursor-pointer shadow-3xs">
                    Archive
                  </Button>
                </div>

                <div className="p-4 border border-destructive/20 rounded-xl bg-destructive/5 flex items-center justify-between gap-4">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-bold text-destructive font-black">Delete Workspace</span>
                    <span className="text-[10px] text-muted-foreground">Permanently wipe files indexing data cache. Cannot be undone.</span>
                  </div>
                  <Button size="sm" className="h-7 text-[10px] font-bold bg-destructive hover:bg-destructive/90 text-white cursor-pointer shadow-3xs">
                    Delete
                  </Button>
                </div>
              </div>
            </DashboardCard>
          )}
        </div>
      </div>
    </div>
  );
}
