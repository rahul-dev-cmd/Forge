"use client";

import * as React from "react";
import { Bell, Check, CheckCheck, Inbox, CircleAlert, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { MOCK_NOTIFICATIONS, Notification } from "@/lib/mockData";

export function NotificationMenu() {
  const { notificationOpen, setNotificationOpen } = useWorkspaceStore();
  const [notifications, setNotifications] = React.useState<Notification[]>(MOCK_NOTIFICATIONS);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  // Close dropdown on click outside
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setNotificationOpen(false);
      }
    }
    if (notificationOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [notificationOpen, setNotificationOpen]);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleMarkAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const handleMarkAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Trigger Button */}
      <button
        onClick={() => setNotificationOpen(!notificationOpen)}
        className={cn(
          "relative p-2 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-all cursor-pointer border border-transparent hover:border-border",
          notificationOpen && "bg-muted text-foreground border-border"
        )}
        title="Notifications"
      >
        <Bell className="w-4.5 h-4.5" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-destructive animate-pulse" />
        )}
      </button>

      {/* Dropdown Card */}
      {notificationOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-popover border border-border rounded-xl shadow-md z-50 flex flex-col overflow-hidden animate-in fade-in-0 slide-in-from-top-2 duration-150">
          {/* Header */}
          <div className="p-4 border-b border-border/60 flex items-center justify-between bg-muted/20">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-foreground">Notifications</span>
              {unreadCount > 0 && (
                <span className="text-[10px] font-black bg-blue-500/10 text-blue-500 border border-blue-500/20 px-1.5 py-0.5 rounded-md leading-none">
                  {unreadCount} new
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="text-[10px] font-bold text-blue-500 hover:text-blue-600 flex items-center gap-1 cursor-pointer transition-colors"
              >
                <CheckCheck className="w-3 h-3" />
                <span>Mark all read</span>
              </button>
            )}
          </div>

          {/* List content */}
          <div className="max-h-80 overflow-y-auto divide-y divide-border/40">
            {notifications.length === 0 ? (
              <div className="p-8 text-center flex flex-col items-center justify-center gap-2">
                <Inbox className="w-8 h-8 text-muted-foreground/60" />
                <span className="text-xs font-bold text-foreground">No Notifications</span>
                <p className="text-[10px] text-muted-foreground leading-normal max-w-[200px]">
                  You are all caught up. No new alerts at this time.
                </p>
              </div>
            ) : (
              notifications.map((n) => {
                return (
                  <div
                    key={n.id}
                    className={cn(
                      "p-3 flex gap-2.5 transition-all text-left relative group",
                      !n.read ? "bg-blue-500/2" : "hover:bg-muted/30"
                    )}
                  >
                    {/* Unread indicator */}
                    {!n.read && (
                      <span className="absolute left-1.5 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-blue-500" />
                    )}

                    {/* Icon mapping */}
                    <div className="pl-1.5 mt-0.5">
                      {n.type === "warning" && (
                        <CircleAlert className="w-4 h-4 text-warning shrink-0" />
                      )}
                      {n.type === "success" && (
                        <Check className="w-4 h-4 text-success shrink-0" />
                      )}
                      {n.type === "info" && (
                        <Sparkles className="w-4 h-4 text-blue-500 shrink-0" />
                      )}
                    </div>

                    <div className="flex-1 flex flex-col gap-0.5">
                      <div className="flex items-center justify-between gap-1">
                        <span className="text-[11px] font-bold text-foreground leading-none">
                          {n.title}
                        </span>
                        <span className="text-[8px] text-muted-foreground whitespace-nowrap">
                          {n.time}
                        </span>
                      </div>
                      <p className="text-[10px] text-muted-foreground leading-normal">
                        {n.message}
                      </p>
                    </div>

                    {/* Action Mark as Read */}
                    {!n.read && (
                      <button
                        onClick={() => handleMarkAsRead(n.id)}
                        className="opacity-0 group-hover:opacity-100 absolute right-2 top-2 p-1 rounded bg-muted border border-border text-muted-foreground hover:text-foreground cursor-pointer transition-all shadow-3xs"
                        title="Mark as read"
                      >
                        <Check className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
export default NotificationMenu;
