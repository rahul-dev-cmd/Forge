import { create } from "zustand";
import { persist } from "zustand/middleware";

interface WorkspaceState {
  sidebarCollapsed: boolean;
  aiPanelOpen: boolean;
  searchOpen: boolean;
  notificationOpen: boolean;
  isAuthenticated: boolean;
  activeWorkspaceId: string | null;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleAiPanel: () => void;
  setAiPanelOpen: (open: boolean) => void;
  setSearchOpen: (open: boolean) => void;
  setNotificationOpen: (open: boolean) => void;
  setIsAuthenticated: (auth: boolean) => void;
  setActiveWorkspaceId: (id: string | null) => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      aiPanelOpen: true,
      searchOpen: false,
      notificationOpen: false,
      isAuthenticated: true,
      activeWorkspaceId: null,
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      toggleAiPanel: () => set((state) => ({ aiPanelOpen: !state.aiPanelOpen })),
      setAiPanelOpen: (open) => set({ aiPanelOpen: open }),
      setSearchOpen: (open) => set({ searchOpen: open }),
      setNotificationOpen: (open) => set({ notificationOpen: open }),
      setIsAuthenticated: (auth) => set({ isAuthenticated: auth }),
      setActiveWorkspaceId: (id) => set({ activeWorkspaceId: id }),
    }),
    {
      name: "forge-workspace-store",
      partialize: (state) => ({
        activeWorkspaceId: state.activeWorkspaceId,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
