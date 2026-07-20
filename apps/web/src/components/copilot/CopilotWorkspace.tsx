"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Bot,
  User as UserIcon,
  Send,
  Plus,
  Trash2,
  Sparkles,
  Code2,
  Bug,
  CheckSquare,
  FileText,
  Compass,
  Cpu,
  Layers,
  FileCode,
  Zap,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  copilotApi,
  ConversationItem,
  ConversationMessageItem,
} from "@/lib/api/copilot";

interface CopilotWorkspaceProps {
  workspaceId: string;
  repositoryId?: string;
}

const AGENTS = [
  { id: "coordinator", name: "Coordinator (Auto)", icon: Compass, desc: "Auto-routes query to optimal specialized agent" },
  { id: "repository_analyst", name: "Repository Analyst", icon: Layers, desc: "Architecture explanations & codebase summaries" },
  { id: "code_explainer", name: "Code Explainer", icon: Code2, desc: "Deep explanation of functions & modules" },
  { id: "debug_assistant", name: "Debug Assistant", icon: Bug, desc: "Stack trace diagnosis & root cause analysis" },
  { id: "code_reviewer", name: "Code Reviewer", icon: CheckSquare, desc: "Code smells & maintainability review" },
  { id: "documentation_assistant", name: "Documentation Assistant", icon: FileText, desc: "API documentation generation" },
  { id: "planner", name: "Planner Agent", icon: Cpu, desc: "Task decomposition & implementation ordering" },
];

export function CopilotWorkspace({ workspaceId, repositoryId }: CopilotWorkspaceProps) {
  const queryClient = useQueryClient();

  const [activeConvId, setActiveConvId] = React.useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = React.useState("coordinator");
  const [inputPrompt, setInputPrompt] = React.useState("");
  const [isStreaming, setIsStreaming] = React.useState(false);
  const [thinkingStatus, setThinkingStatus] = React.useState<string | null>(null);

  // Local message state for immediate UI updates & SSE streaming
  const [localMessages, setLocalMessages] = React.useState<ConversationMessageItem[]>([]);

  const convListQuery = useQuery({
    queryKey: ["copilot-conversations", workspaceId],
    queryFn: () => copilotApi.listConversations(workspaceId),
  });

  const detailQuery = useQuery({
    queryKey: ["copilot-conversation-detail", activeConvId],
    queryFn: () => (activeConvId ? copilotApi.getConversation(activeConvId) : null),
    enabled: !!activeConvId,
  });

  React.useEffect(() => {
    if (detailQuery.data?.messages) {
      setLocalMessages(detailQuery.data.messages);
    }
  }, [detailQuery.data]);

  const createConvMutation = useMutation({
    mutationFn: (title: string) => copilotApi.createConversation(workspaceId, repositoryId, title, selectedAgent),
    onSuccess: (newConv) => {
      queryClient.invalidateQueries({ queryKey: ["copilot-conversations", workspaceId] });
      setActiveConvId(newConv.id);
      setLocalMessages([]);
    },
  });

  const deleteConvMutation = useMutation({
    mutationFn: (id: string) => copilotApi.deleteConversation(id),
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: ["copilot-conversations", workspaceId] });
      if (activeConvId === deletedId) {
        setActiveConvId(null);
        setLocalMessages([]);
      }
    },
  });

  const handleSendMessage = async (promptText: string) => {
    if (!promptText.trim() || isStreaming) return;

    let targetConvId = activeConvId;
    if (!targetConvId) {
      const created = await createConvMutation.mutateAsync(promptText.slice(0, 30) + "...");
      targetConvId = created.id;
    }

    const userMsg: ConversationMessageItem = {
      id: `usr-${Date.now()}`,
      conversation_id: targetConvId,
      sender: "user",
      content: promptText,
      created_at: new Date().toISOString(),
    };

    setLocalMessages((prev) => [...prev, userMsg]);
    setInputPrompt("");
    setIsStreaming(true);
    setThinkingStatus("Routing query via AgentOrchestrator...");

    try {
      const agentEndpoint = selectedAgent === "coordinator" ? "explain" : (
        selectedAgent === "repository_analyst" ? "summarize" :
        selectedAgent === "code_explainer" ? "explain" :
        selectedAgent === "debug_assistant" ? "debug" :
        selectedAgent === "code_reviewer" ? "review" :
        selectedAgent === "planner" ? "plan" : "explain"
      );

      const res = await copilotApi.executeSpecializedAgent(
        agentEndpoint as any,
        workspaceId,
        promptText,
        repositoryId
      );

      const botMsg: ConversationMessageItem = {
        id: `bot-${Date.now()}`,
        conversation_id: targetConvId,
        sender: "agent",
        agent_type: selectedAgent,
        content: res.answer || "Execution complete.",
        structured_json: res,
        citations: res.citations || [],
        created_at: new Date().toISOString(),
      };

      setLocalMessages((prev) => [...prev, botMsg]);
    } catch (e: any) {
      const errMsg: ConversationMessageItem = {
        id: `err-${Date.now()}`,
        conversation_id: targetConvId,
        sender: "system",
        content: `Agent Execution Error: ${e.message || "Failed to execute agent"}`,
        created_at: new Date().toISOString(),
      };
      setLocalMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsStreaming(false);
      setThinkingStatus(null);
    }
  };

  const conversations = convListQuery.data || [];

  return (
    <div className="flex h-[750px] w-full border border-border rounded-xl bg-card overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-border flex flex-col bg-muted/20">
        <div className="p-3 border-b border-border flex items-center justify-between">
          <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-primary" /> Copilot Sessions
          </span>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => createConvMutation.mutate("New Conversation")}
            className="h-7 px-2 text-xs gap-1"
          >
            <Plus className="w-3.5 h-3.5" /> New
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 ? (
            <p className="text-[11px] text-muted-foreground p-3 text-center">No conversations yet.</p>
          ) : (
            conversations.map((c) => (
              <div
                key={c.id}
                onClick={() => setActiveConvId(c.id)}
                className={`group flex items-center justify-between px-2.5 py-2 rounded-md cursor-pointer text-xs transition-colors ${
                  activeConvId === c.id
                    ? "bg-primary/10 text-primary font-semibold"
                    : "hover:bg-muted text-muted-foreground"
                }`}
              >
                <span className="truncate flex-1">{c.title}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteConvMutation.mutate(c.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 hover:text-destructive p-1"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-card">
        {/* Top Header Bar with Agent Selector */}
        <div className="p-3 border-b border-border flex items-center justify-between bg-card/80">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-primary" />
            <span className="text-xs font-semibold text-foreground">Specialized Agent:</span>
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              className="text-xs border border-border rounded px-2 py-1 bg-background text-foreground focus:outline-none"
            >
              {AGENTS.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>

          <Badge variant="outline" className="text-[10px] uppercase font-mono">
            Provider: Local / OpenAI Failover
          </Badge>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {localMessages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground p-8">
              <Sparkles className="w-8 h-8 text-primary mb-2 opacity-80" />
              <h4 className="text-sm font-semibold text-foreground">Forge AI Software Engineering Copilot</h4>
              <p className="text-xs max-w-sm mt-1">
                Ask architectural questions, request code reviews, debug errors, or generate task plans.
              </p>
            </div>
          ) : (
            localMessages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-3 text-xs ${m.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {m.sender !== "user" && (
                  <div className="w-7 h-7 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-lg p-3 space-y-2 ${
                    m.sender === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted/40 border border-border text-foreground"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 border-b border-border/40 pb-1 text-[10px] text-muted-foreground">
                    <span className="font-semibold capitalize">{m.agent_type || m.sender}</span>
                    <span>{new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                  </div>

                  <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>

                  {/* Citations Viewer */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-border/40 space-y-1">
                      <span className="text-[10px] font-semibold text-muted-foreground">Citations & References:</span>
                      <div className="flex flex-wrap gap-1">
                        {m.citations.map((c, idx) => (
                          <Badge key={idx} variant="outline" className="text-[9px] font-mono gap-1">
                            <FileCode className="w-3 h-3 text-primary" />
                            {c.file_path}:{c.start_line}-{c.end_line}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Follow-up suggestions */}
                  {m.structured_json?.followups && m.structured_json.followups.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-border/40 space-y-1">
                      <span className="text-[10px] font-semibold text-muted-foreground">Suggested Follow-ups:</span>
                      <div className="flex flex-wrap gap-1">
                        {m.structured_json.followups.map((f, i) => (
                          <button
                            key={i}
                            onClick={() => handleSendMessage(f)}
                            className="text-[10px] px-2 py-0.5 rounded bg-background/60 hover:bg-background border border-border text-foreground text-left"
                          >
                            {f}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {m.sender === "user" && (
                  <div className="w-7 h-7 rounded-full bg-secondary text-secondary-foreground flex items-center justify-center shrink-0">
                    <UserIcon className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {isStreaming && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground p-2 bg-muted/20 rounded-md animate-pulse">
              <Zap className="w-4 h-4 text-primary animate-spin" />
              <span>{thinkingStatus || "Agent processing..."}</span>
            </div>
          )}
        </div>

        {/* Input Box */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage(inputPrompt);
          }}
          className="p-3 border-t border-border flex gap-2"
        >
          <input
            type="text"
            placeholder="Ask AI Copilot (e.g. 'Explain authentication architecture', 'Review error handling')..."
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            disabled={isStreaming}
            className="flex-1 text-xs px-3 py-2 rounded-md border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
          <Button size="sm" type="submit" disabled={isStreaming || !inputPrompt.trim()}>
            <Send className="w-3.5 h-3.5" />
          </Button>
        </form>
      </div>
    </div>
  );
}
