"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Github, Loader2, CheckCircle2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  connectGitHub,
  installGitHubApp,
  listGitHubInstallations,
  listGitHubRepositories,
  type GitHubRemoteRepoDto,
} from "@/lib/api/github";
import { importRepository } from "@/lib/api/repositories";
import { listProjects } from "@/lib/api/projects";
import { cn } from "@/lib/utils";

interface ImportWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  workspaceId: string;
}

type Step = "connect" | "select" | "confirm" | "done";

export function ImportWizard({ open, onOpenChange, workspaceId }: ImportWizardProps) {
  const queryClient = useQueryClient();
  const [step, setStep] = React.useState<Step>("connect");
  const [selectedInstallId, setSelectedInstallId] = React.useState<string | null>(null);
  const [selectedRepo, setSelectedRepo] = React.useState<GitHubRemoteRepoDto | null>(null);
  const [projectId, setProjectId] = React.useState<string>("");
  const [error, setError] = React.useState<string | null>(null);

  const installationsQuery = useQuery({
    queryKey: ["github-installations"],
    queryFn: listGitHubInstallations,
    enabled: open,
  });

  const projectsQuery = useQuery({
    queryKey: ["projects", workspaceId],
    queryFn: () => listProjects({ workspaceId, limit: 50 }),
    enabled: open && !!workspaceId,
  });

  const reposQuery = useQuery({
    queryKey: ["github-remote-repos", selectedInstallId],
    queryFn: () =>
      listGitHubRepositories({
        installationId: selectedInstallId ?? undefined,
        perPage: 50,
      }),
    enabled: open && step === "select" && !!selectedInstallId,
  });

  React.useEffect(() => {
    if (!open) {
      setStep("connect");
      setSelectedRepo(null);
      setError(null);
      return;
    }
    if ((installationsQuery.data?.length ?? 0) > 0) {
      setStep("select");
      if (!selectedInstallId) {
        setSelectedInstallId(installationsQuery.data![0].installation_id);
      }
    }
  }, [open, installationsQuery.data, selectedInstallId]);

  React.useEffect(() => {
    const first = projectsQuery.data?.items?.[0];
    if (first && !projectId) setProjectId(first.id);
  }, [projectsQuery.data, projectId]);

  const connectMutation = useMutation({
    mutationFn: async () => {
      const data = await connectGitHub(workspaceId);
      window.location.href = data.authorize_url || data.install_url;
    },
  });

  const installMutation = useMutation({
    mutationFn: async () => {
      const data = await installGitHubApp(workspaceId);
      if (data.install_url) window.location.href = data.install_url;
    },
  });

  const importMutation = useMutation({
    mutationFn: async () => {
      if (!selectedRepo || !projectId) throw new Error("Select a repository and project");
      return importRepository({
        workspace_id: workspaceId,
        project_id: projectId,
        installation_id: selectedRepo.installation_id,
        provider_repository_id: selectedRepo.provider_repository_id,
        full_name: selectedRepo.full_name,
        name: selectedRepo.name,
        owner: selectedRepo.owner,
        default_branch: selectedRepo.default_branch,
        clone_url: selectedRepo.clone_url,
        html_url: selectedRepo.html_url,
        private: selectedRepo.private,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repositories"] });
      setStep("done");
    },
    onError: (err: Error) => setError(err.message),
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Import from GitHub</DialogTitle>
          <DialogDescription>
            Connect the Forge GitHub App, pick a repository, and sync metadata — no source code is cloned.
          </DialogDescription>
        </DialogHeader>

        {step === "connect" && (
          <div className="flex flex-col gap-4 py-2">
            <p className="text-xs text-muted-foreground">
              Install the Forge GitHub App on your account or organization, then return here to import repositories.
            </p>
            <div className="flex flex-col sm:flex-row gap-2">
              <Button
                onClick={() => connectMutation.mutate()}
                disabled={connectMutation.isPending}
                className="gap-2"
              >
                <Github className="w-4 h-4" />
                Connect GitHub
              </Button>
              <Button
                variant="outline"
                onClick={() => installMutation.mutate()}
                disabled={installMutation.isPending}
              >
                Install GitHub App
              </Button>
            </div>
            {installationsQuery.isLoading ? <Skeleton className="h-10 w-full" /> : null}
          </div>
        )}

        {step === "select" && (
          <div className="flex flex-col gap-3 py-1 max-h-[420px]">
            <div className="flex flex-wrap gap-2">
              {(installationsQuery.data ?? []).map((inst) => (
                <button
                  key={inst.id}
                  type="button"
                  onClick={() => setSelectedInstallId(inst.installation_id)}
                  className={cn(
                    "px-2.5 py-1 rounded-md border text-[11px] font-semibold cursor-pointer",
                    selectedInstallId === inst.installation_id
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-muted-foreground"
                  )}
                >
                  {inst.account_login}
                </button>
              ))}
              <Button size="sm" variant="ghost" className="h-7 text-[11px]" onClick={() => installMutation.mutate()}>
                + Add installation
              </Button>
            </div>

            <div className="overflow-y-auto border border-border rounded-md divide-y divide-border max-h-64">
              {reposQuery.isLoading ? (
                <div className="p-3 space-y-2">
                  <Skeleton className="h-8 w-full" />
                  <Skeleton className="h-8 w-full" />
                </div>
              ) : (reposQuery.data?.items.length ?? 0) === 0 ? (
                <div className="p-4 text-xs text-muted-foreground">
                  No remote repositories returned. Configure the GitHub App, or enter details after selecting an installation.
                  You can still import if you know the provider repository ID via the API.
                </div>
              ) : (
                reposQuery.data!.items.map((repo) => (
                  <button
                    key={repo.provider_repository_id}
                    type="button"
                    disabled={repo.already_imported}
                    onClick={() => {
                      setSelectedRepo(repo);
                      setStep("confirm");
                    }}
                    className={cn(
                      "w-full text-left px-3 py-2.5 hover:bg-muted/40 transition-colors cursor-pointer",
                      repo.already_imported && "opacity-50 cursor-not-allowed"
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-semibold text-foreground">{repo.full_name}</span>
                      {repo.already_imported ? (
                        <Badge variant="secondary" className="text-[10px]">Imported</Badge>
                      ) : repo.private ? (
                        <Badge variant="outline" className="text-[10px]">Private</Badge>
                      ) : (
                        <Badge variant="success" className="text-[10px]">Public</Badge>
                      )}
                    </div>
                    {repo.description ? (
                      <p className="text-[11px] text-muted-foreground mt-0.5 line-clamp-1">
                        {repo.description}
                      </p>
                    ) : null}
                  </button>
                ))
              )}
            </div>
          </div>
        )}

        {step === "confirm" && selectedRepo && (
          <div className="flex flex-col gap-3 py-2">
            <div className="rounded-md border border-border bg-muted/20 p-3 text-xs">
              <div className="font-semibold text-foreground">{selectedRepo.full_name}</div>
              <div className="text-muted-foreground mt-1">
                Branch: {selectedRepo.default_branch} · Installation: {selectedRepo.installation_id}
              </div>
            </div>
            <label className="flex flex-col gap-1.5 text-[11px] font-semibold text-muted-foreground">
              Target project
              <select
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                className="h-9 rounded-md border border-border bg-surface px-2 text-xs text-foreground font-normal"
              >
                {(projectsQuery.data?.items ?? []).map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </label>
            {error ? <p className="text-[11px] text-destructive">{error}</p> : null}
          </div>
        )}

        {step === "done" && (
          <div className="flex flex-col items-center gap-2 py-6 text-center">
            <CheckCircle2 className="w-8 h-8 text-success" />
            <p className="text-sm font-semibold text-foreground">Import started</p>
            <p className="text-xs text-muted-foreground">
              Metadata sync is running in the background. Status updates on the repository card.
            </p>
          </div>
        )}

        <DialogFooter>
          {step === "confirm" ? (
            <>
              <Button variant="outline" onClick={() => setStep("select")}>
                Back
              </Button>
              <Button
                onClick={() => importMutation.mutate()}
                disabled={importMutation.isPending || !projectId}
                className="gap-2"
              >
                {importMutation.isPending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
                Import & Sync
              </Button>
            </>
          ) : step === "done" ? (
            <Button onClick={() => onOpenChange(false)}>Close</Button>
          ) : step === "select" ? (
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
          ) : null}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
