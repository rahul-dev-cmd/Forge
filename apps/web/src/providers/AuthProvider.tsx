"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { ClerkProvider, useUser as useClerkUser, useClerk as useClerkContext, UserButton as ClerkUserButton, SignIn as ClerkSignIn, SignUp as ClerkSignUp, UserProfile as ClerkUserProfile } from "@clerk/nextjs";
import { LogOut, User, Settings } from "lucide-react";
import { useWorkspaceStore } from "@/store/workspaceStore";

// Check if Clerk publishable and secret keys are active (not placeholder)
export const isClerkConfigured =
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
  !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes("placeholder");

interface AuthContextType {
  isAuthenticated: boolean;
  user: {
    fullName: string | null;
    username: string | null;
    imageUrl: string;
    primaryEmailAddress: {
      emailAddress: string;
    } | null;
    createdAt: string;
  } | null;
  signOut: () => void;
  signIn: (username: string) => void;
  updateUser: (fields: { fullName?: string; username?: string }) => void;
}

const AuthContext = React.createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  signOut: () => {},
  signIn: () => {},
  updateUser: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, setIsAuthenticated } = useWorkspaceStore();
  const [userState, setUserState] = React.useState<{
    fullName: string;
    username: string;
    imageUrl: string;
    primaryEmailAddress: { emailAddress: string };
    createdAt: string;
  } | null>(null);

  // Initialize mock user session from localStorage
  React.useEffect(() => {
    if (!isClerkConfigured) {
      const storedUser = localStorage.getItem("forge_mock_user");
      const storedAuth = localStorage.getItem("forge_mock_auth");

      if (storedUser) {
        setUserState(JSON.parse(storedUser));
      } else {
        const defaultUser = {
          fullName: "Rahul Dev",
          username: "rahuldev",
          imageUrl: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&fit=crop",
          primaryEmailAddress: { emailAddress: "rahul.dev@forge.com" },
          createdAt: new Date().toISOString(),
        };
        setUserState(defaultUser);
        localStorage.setItem("forge_mock_user", JSON.stringify(defaultUser));
      }

      if (storedAuth) {
        setIsAuthenticated(storedAuth === "true");
      } else {
        setIsAuthenticated(true);
        localStorage.setItem("forge_mock_auth", "true");
      }
    }
  }, [setIsAuthenticated]);

  const signIn = (username: string) => {
    const defaultUser = {
      fullName: username || "Rahul Dev",
      username: username.toLowerCase().replace(/\s+/g, "") || "rahuldev",
      imageUrl: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&fit=crop",
      primaryEmailAddress: { emailAddress: `${username.toLowerCase().replace(/\s+/g, "") || "rahul.dev"}@forge.com` },
      createdAt: new Date().toISOString(),
    };
    setUserState(defaultUser);
    setIsAuthenticated(true);
    localStorage.setItem("forge_mock_user", JSON.stringify(defaultUser));
    localStorage.setItem("forge_mock_auth", "true");
    router.push("/dashboard");
  };

  const signOut = () => {
    setIsAuthenticated(false);
    localStorage.setItem("forge_mock_auth", "false");
    router.push("/sign-in");
  };

  const updateUser = (fields: { fullName?: string; username?: string }) => {
    if (userState) {
      const updated = {
        ...userState,
        fullName: fields.fullName ?? userState.fullName,
        username: fields.username ?? userState.username,
      };
      setUserState(updated);
      localStorage.setItem("forge_mock_user", JSON.stringify(updated));
    }
  };

  if (isClerkConfigured) {
    return <ClerkProvider>{children}</ClerkProvider>;
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user: userState,
        signOut,
        signIn,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Custom wrapper hooks
export function useUser() {
  if (isClerkConfigured) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { user, isLoaded } = useClerkUser();
    return { user, isLoaded };
  }

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const context = React.useContext(AuthContext);
  return { user: context.user, isLoaded: true };
}

export function useClerk() {
  if (isClerkConfigured) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const clerk = useClerkContext();
    return clerk;
  }

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const context = React.useContext(AuthContext);
  return {
    signOut: context.signOut,
    signIn: context.signIn,
    updateUser: context.updateUser,
  };
}

export function UserButton({ appearance }: { appearance?: Record<string, unknown> }) {
  if (isClerkConfigured) {
    return <ClerkUserButton appearance={appearance} />;
  }

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const context = React.useContext(AuthContext);
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const [dropdownOpen, setDropdownOpen] = React.useState(false);
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const menuRef = React.useRef<HTMLDivElement>(null);
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const router = useRouter();

  // eslint-disable-next-line react-hooks/rules-of-hooks
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    if (dropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownOpen]);

  if (!context.user) return null;

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className="w-8 h-8 rounded-full border border-blue-500/20 text-blue-600 flex items-center justify-center font-bold text-xs shadow-3xs overflow-hidden cursor-pointer hover:scale-105 transition-transform"
      >
        <img src={context.user.imageUrl} className="w-full h-full object-cover" alt="User avatar" />
      </button>

      {dropdownOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-popover border border-border rounded-lg shadow-md z-50 flex flex-col p-1 animate-in fade-in-0 slide-in-from-top-2 duration-150 text-left">
          <div className="px-3 py-2 border-b border-border/40 mb-1 select-none">
            <span className="text-[11px] font-bold text-foreground block leading-none truncate">
              {context.user.fullName}
            </span>
            <span className="text-[9px] text-muted-foreground mt-1 truncate block leading-none">
              {context.user.primaryEmailAddress?.emailAddress}
            </span>
          </div>

          <button
            onClick={() => {
              router.push("/profile");
              setDropdownOpen(false);
            }}
            className="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-md text-foreground hover:bg-muted/65 transition-colors cursor-pointer"
          >
            <User className="w-3.5 h-3.5" />
            <span>Manage Account</span>
          </button>

          <button
            onClick={() => {
              router.push("/settings");
              setDropdownOpen(false);
            }}
            className="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-md text-foreground hover:bg-muted/65 transition-colors cursor-pointer"
          >
            <Settings className="w-3.5 h-3.5" />
            <span>Settings</span>
          </button>

          <div className="h-px bg-border/40 my-1" />

          <button
            onClick={() => {
              context.signOut();
              setDropdownOpen(false);
            }}
            className="w-full flex items-center gap-2 px-3 py-2 text-xs font-bold rounded-md text-destructive hover:bg-destructive/5 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      )}
    </div>
  );
}

export function SignIn({ appearance }: { appearance?: Record<string, unknown> }) {
  if (isClerkConfigured) {
    return <ClerkSignIn appearance={appearance} />;
  }

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const context = React.useContext(AuthContext);
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const [val, setVal] = React.useState("");

  return (
    <div className="w-full border border-border bg-surface shadow-xs rounded-xl p-6 flex flex-col gap-4 text-left">
      <div className="flex flex-col gap-1 select-none">
        <h3 className="font-bold text-sm text-foreground">Sign In (Mock Flow)</h3>
        <p className="text-[10px] text-muted-foreground">Type a mock user name below to bypass server keys checks.</p>
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-semibold text-foreground">User Profile Name</label>
        <input
          type="text"
          value={val}
          onChange={(e) => setVal(e.target.value)}
          placeholder="e.g. Rahul Dev"
          className="w-full h-9 px-3 rounded-lg border border-border bg-muted/10 text-foreground text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <button
        onClick={() => context.signIn(val)}
        className="w-full h-9 bg-blue-600 hover:bg-blue-600/90 text-white rounded-lg text-xs font-semibold shadow-3xs cursor-pointer select-none transition-colors"
      >
        Sign In as Mock User
      </button>
    </div>
  );
}

export function SignUp({ appearance }: { appearance?: Record<string, unknown> }) {
  if (isClerkConfigured) {
    return <ClerkSignUp appearance={appearance} />;
  }

  return <SignIn appearance={appearance} />;
}

export function UserProfile(props: Record<string, unknown>) {
  if (isClerkConfigured) {
    return <ClerkUserProfile {...props} />;
  }

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const context = React.useContext(AuthContext);
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const [fullName, setFullName] = React.useState(context.user?.fullName || "");
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const [username, setUsername] = React.useState(context.user?.username || "");

  // eslint-disable-next-line react-hooks/rules-of-hooks
  React.useEffect(() => {
    if (context.user) {
      setFullName(context.user.fullName || "");
      setUsername(context.user.username || "");
    }
  }, [context.user]);

  if (!context.user) return null;

  return (
    <div className="p-6 flex flex-col gap-6 text-left">
      <div className="flex flex-col gap-1 select-none">
        <h3 className="font-bold text-sm text-foreground">Profile Details (Mock Settings)</h3>
        <p className="text-[10px] text-muted-foreground">Manage your mock user attributes stored in Local Storage.</p>
      </div>

      <div className="h-px bg-border/40" />

      <div className="flex flex-col gap-4 text-xs">
        <div className="flex flex-col gap-1.5">
          <label className="font-semibold text-foreground">Full Name</label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full h-9 px-3 rounded-lg border border-border bg-surface text-foreground focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="font-semibold text-foreground">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full h-9 px-3 rounded-lg border border-border bg-surface text-foreground focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="font-semibold text-muted-foreground">Email Address (Read-only)</label>
          <input
            type="email"
            value={context.user.primaryEmailAddress?.emailAddress}
            disabled
            className="w-full h-9 px-3 rounded-lg border border-border bg-muted/20 text-muted-foreground cursor-not-allowed"
          />
        </div>
      </div>

      <button
        onClick={() => {
          context.updateUser({ fullName, username });
          alert("Mock profile updated successfully!");
        }}
        className="w-full h-9 bg-blue-600 hover:bg-blue-600/90 text-white rounded-lg text-xs font-semibold shadow-3xs cursor-pointer select-none transition-colors"
      >
        Save Changes
      </button>
    </div>
  );
}
