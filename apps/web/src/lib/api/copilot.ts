import { api } from "./client";

export interface ConversationItem {
  id: string;
  title: string;
  workspace_id: string;
  repository_id?: string | null;
  active_agent: string;
  is_pinned?: boolean;
  is_archived?: boolean;
  created_at: string;
}

export interface ConversationMessageItem {
  id: string;
  conversation_id: string;
  sender: "user" | "agent" | "system";
  agent_type?: string | null;
  content: string;
  structured_json?: {
    agent?: string;
    answer?: string;
    citations?: { file_path: string; start_line: number; end_line: number; confidence: number }[];
    confidence?: number;
    followups?: string[];
  } | null;
  citations?: { file_path: string; start_line: number; end_line: number; confidence: number }[] | null;
  tokens_used?: number;
  created_at: string;
}

export interface ConversationDetailResponse {
  id: string;
  title: string;
  workspace_id: string;
  repository_id?: string | null;
  active_agent: string;
  messages: ConversationMessageItem[];
}

export const copilotApi = {
  async listConversations(workspaceId: string): Promise<ConversationItem[]> {
    const res = await api.get<{ data: ConversationItem[] }>(`/ai/conversations?workspace_id=${workspaceId}`);
    return res.data || [];
  },

  async createConversation(
    workspaceId: string,
    repositoryId?: string,
    title = "New Conversation",
    agent = "coordinator"
  ): Promise<ConversationItem> {
    const res = await api.post<{ data: ConversationItem }>("/ai/conversations", {
      workspace_id: workspaceId,
      repository_id: repositoryId,
      title,
      active_agent: agent,
    });
    return res.data;
  },

  async getConversation(id: string): Promise<ConversationDetailResponse> {
    const res = await api.get<{ data: ConversationDetailResponse }>(`/ai/conversations/${id}`);
    return res.data;
  },

  async deleteConversation(id: string): Promise<void> {
    await api.delete(`/ai/conversations/${id}`);
  },

  async executeSpecializedAgent(
    endpoint: "explain" | "review" | "debug" | "plan" | "summarize",
    workspaceId: string,
    prompt: string,
    repositoryId?: string
  ) {
    const res = await api.post<{ data: any }>(`/ai/${endpoint}`, {
      prompt,
      workspace_id: workspaceId,
      repository_id: repositoryId,
    });
    return res.data;
  },
};
