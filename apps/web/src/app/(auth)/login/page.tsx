import Link from "next/link";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
      <div className="max-w-md w-full border border-border bg-surface rounded-lg p-8 shadow-xs flex flex-col gap-6">
        <div className="flex flex-col gap-2 text-center">
          <Link href="/" className="self-center">
            <div className="w-10 h-10 rounded-md bg-primary flex items-center justify-center text-primary-foreground font-bold text-xl">
              F
            </div>
          </Link>
          <h2 className="text-xl font-bold tracking-tight">Sign in to Forge</h2>
          <p className="text-xs text-muted-foreground">
            Enter your credentials or choose your provider to continue
          </p>
        </div>

        {/* Form placeholder */}
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-muted-foreground">Email Address</label>
            <input
              disabled
              type="email"
              placeholder="name@example.com"
              className="w-full h-10 px-3 rounded-md bg-muted border border-border text-sm placeholder:text-muted-foreground focus:outline-none cursor-not-allowed"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-muted-foreground">Password</label>
            <input
              disabled
              type="password"
              placeholder="••••••••"
              className="w-full h-10 px-3 rounded-md bg-muted border border-border text-sm placeholder:text-muted-foreground focus:outline-none cursor-not-allowed"
            />
          </div>

          <button
            disabled
            className="w-full h-10 bg-primary text-primary-foreground rounded-md font-medium text-sm hover:opacity-90 transition-all cursor-not-allowed mt-2"
          >
            Sign In with Email (Demo Only)
          </button>
        </div>

        <div className="relative flex py-2 items-center">
          <div className="flex-grow border-t border-border"></div>
          <span className="flex-shrink mx-4 text-muted-foreground text-[10px] uppercase font-bold tracking-wider">or continue with</span>
          <div className="flex-grow border-t border-border"></div>
        </div>

        {/* Auth providers placeholder */}
        <div className="grid grid-cols-2 gap-4">
          <Link
            href="/dashboard"
            className="h-10 border border-border bg-surface hover:bg-muted/50 rounded-md flex items-center justify-center text-xs font-semibold transition-all shadow-3xs"
          >
            <span>GitHub</span>
          </Link>
          <Link
            href="/dashboard"
            className="h-10 border border-border bg-surface hover:bg-muted/50 rounded-md flex items-center justify-center text-xs font-semibold transition-all shadow-3xs"
          >
            <span>Google</span>
          </Link>
        </div>

        <div className="text-center text-xs text-muted-foreground">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-primary font-medium hover:underline">
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
}
